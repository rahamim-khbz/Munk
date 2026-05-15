import os
import json
import time
import re
import subprocess
import argparse
from sys import executable
from dotenv import load_dotenv
from groq import Groq

# Reuse extraction logic from the original pipeline
from munk_pipeline_groq import extract_and_flatten, GroqRateLimiter

load_dotenv()

# Configuration
GROQ_API_KEY = os.getenv("VITE_GROQ_API_KEY")
MODEL_TRANSLATOR = "llama-3.3-70b-versatile" 
MODEL_ALIGNER = "llama-3.1-8b-instant"

# Groq limits for 70B model are very tight (12k TPM)
# We use a conservative 8k TPM limit to avoid any 413/429
RATE_LIMITER = GroqRateLimiter(tpm_limit=8000, rpm_limit=10)

client = Groq(api_key=GROQ_API_KEY)

# --- PROMPTS ---

TRANSLATOR_PROMPT = """You are a master scholarly translator specializing in French academic prose and medieval philosophical texts.
Your task is to translate Salomon Munk's 'Le Guide des Égarés' FOOTNOTES into precise Academic English.

Tone: Modern Academic Scholarly (precise, formal, clear).
Rules:
1. Use formal academic vocabulary. Avoid archaic or "old-sounding" English.
2. NO EXTERNAL KNOWLEDGE: Translate ONLY what is in the provided French text.
3. If the French text contains Latin citations or phrases, translate them into English. You may preserve the original Latin in brackets [Lat.: ...] following the English translation, but the segment must be primarily English.
4. Do NOT translate Hebrew/Arabic scripts if present; preserve them exactly.
5. Use standard modern scholarly conventions for citations (e.g., 'See', 'Cf.', 'Note').
6. DO NOT ADD ANY PREAMBLE. Return only the translated text."""

ALIGNER_PROMPT_TEMPLATE = """I have a French sentence with [[t:N]] markers and its English translation.
Your task is to re-insert the [[t:N]] markers into the English translation in the exact same semantic positions.

IMPORTANT:
1. Preserve all [[t:N]] markers.
2. If a marker wraps Hebrew or Arabic text, ensure it remains in the same relative position.
3. Be extremely careful with Right-to-Left (RTL) text; the markers should stay outside the RTL text if that's how they were in the original.
4. Do NOT add any preamble or explanation.

French (Original): {french}
English (Translated): {english}

Return ONLY the English text with markers."""

# --- UTILS ---

def trigger_status_report():
    """Runs the report generator script to update the MD status checker."""
    try:
        subprocess.run([executable, "generate_footnote_report.py"], check=False)
    except Exception as e:
        print(f"  [Status] Failed to update MD report: {e}")

def estimate_tokens(text):
    # Rough estimate: 1 token = 4 chars
    return len(text) // 4 + 100

def translate_worker_groq_rehab(fn_id, fn_data):
    """Translates a footnote using the Two-Pass Rehab logic with Model Splitting."""
    
    french_text = fn_data['text']
    # The extraction logic already replaced HTML with [[t:N]] tags
    # french_text is already "tag-woven" with [[t:N]]
    
    # Naked version for translation
    naked_french = re.sub(r'\[\[t:\d+\]\]', '', french_text)
    
    # Wait for rate limits before Pass 1
    est_tokens = estimate_tokens(naked_french) + 500 # + prompt
    RATE_LIMITER.wait_for_limit(est_tokens)
    
    for attempt in range(5):
        try:
            # PASS 1: The Brain (70B)
            chat_1 = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": TRANSLATOR_PROMPT},
                    {"role": "user", "content": naked_french}
                ],
                model=MODEL_TRANSLATOR,
                max_tokens=2048,
                temperature=0.1
            )
            english_naked = chat_1.choices[0].message.content.strip()
            
            # Record usage
            RATE_LIMITER.history.append((time.time(), chat_1.usage.total_tokens))
            
            # PASS 2: The Clerk (8B) - re-insert tags
            # 8B is much faster and has higher limits
            chat_2 = client.chat.completions.create(
                messages=[
                    {"role": "user", "content": ALIGNER_PROMPT_TEMPLATE.format(french=french_text, english=english_naked)}
                ],
                model=MODEL_ALIGNER,
                max_tokens=2048,
                temperature=0.1
            )
            final_text = chat_2.choices[0].message.content.strip()
            
            # Clean up potential LLM preamble
            final_text = re.sub(r'^Here is the.*:\s*', '', final_text, flags=re.IGNORECASE)
            
            # Basic validation: ensure tag count matches
            original_tags = re.findall(r'\[\[t:\d+\]\]', french_text)
            new_tags = re.findall(r'\[\[t:\d+\]\]', final_text)
            
            if len(original_tags) != len(new_tags):
                 print(f"  [Warning] {fn_id} Tag mismatch. Retrying...")
                 continue
            
            return final_text
            
        except Exception as e:
            err_msg = str(e)
            print(f"  [Error] {fn_id} Attempt {attempt+1}: {err_msg}")
            
            if "429" in err_msg or "rate limit" in err_msg.lower():
                # Groq 429 usually contains retry-after info
                wait_sec = 60
                wait_match = re.search(r'try again in ([\d\.ms]+)', err_msg)
                if wait_match:
                    wait_str = wait_match.group(1)
                    if 'm' in wait_str and 's' in wait_str:
                        m, s = re.findall(r'(\d+)', wait_str)[:2]
                        wait_sec = int(m)*60 + int(s) + 2
                    elif 's' in wait_str:
                        wait_sec = int(re.search(r'(\d+)', wait_str).group(1)) + 2
                print(f"  [Rate Limit] Sleeping {wait_sec}s...")
                time.sleep(wait_sec)
            elif "413" in err_msg:
                print(f"  [Fatal] {fn_id} Request too large. Skipping.")
                return None
            else:
                time.sleep(5 * (attempt + 1))
                
    return None

def run_rehab_track_groq(flat_footnotes, checkpoint_file, limit=None):
    """Main loop for Two-Pass Llama Rehab."""
    print(f"\n=== Starting Llama Rehab Track V3 (Groq: Hybrid 70B/8B) ===")
    
    translated_map = {}
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            translated_map = json.load(f)
        print(f"  [Resuming] Found {len(translated_map)} items already translated.")
    
    remaining_keys = [k for k in flat_footnotes.keys() if k not in translated_map]
    if limit:
        remaining_keys = remaining_keys[:limit]
        
    if not remaining_keys:
        print(f"  [Skip] No remaining items to translate.")
        return translated_map

    def natural_sort_key(s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]
    
    sorted_keys = sorted(remaining_keys, key=natural_sort_key)
    
    count = 0
    for i, k in enumerate(sorted_keys):
        print(f"  [Processing] {k} ({i+1}/{len(sorted_keys)})")
        result = translate_worker_groq_rehab(k, flat_footnotes[k])
        
        if result:
            translated_map[k] = result
            # Save every step for safety
            with open(checkpoint_file, 'w') as f:
                json.dump(translated_map, f, indent=2, ensure_ascii=False)
            
            count += 1
            if count % 10 == 0:
                print(f"  [Heartbeat] {k}: {count} completed in this session.")
                trigger_status_report()
        else:
            print(f"  [Warning] {k} failed after retries.")
            
    trigger_status_report()
    return translated_map

def main():
    parser = argparse.ArgumentParser(description="Llama Tag Rehab Pipeline V3")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of footnotes")
    parser.add_argument("--source", type=str, default="French_Healed_Enriched.json", help="Source JSON file")
    args = parser.parse_args()

    print(f"Loading {args.source}...")
    with open(args.source, 'r') as f:
        data = json.load(f)
    
    print("Extracting footnotes...")
    _, flat_footnotes = extract_and_flatten(data)
    
    # Note: checkpoint_footnotes_gemini.json is the file used for footnotes
    run_rehab_track_groq(flat_footnotes, "checkpoint_footnotes_gemini.json", limit=args.limit)

if __name__ == "__main__":
    main()
