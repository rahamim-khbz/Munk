import os
import json
import time
import re
import subprocess
import argparse
from sys import executable
from dotenv import load_dotenv
from groq import Groq
from munk_pipeline_groq import extract_and_flatten

load_dotenv()

# Configuration
GROQ_API_KEY = os.getenv("VITE_GROQ_API_KEY")
MODEL_TRANSLATOR = "llama-3.3-70b-versatile" 
MODEL_ALIGNER = "llama-3.1-8b-instant"

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

French (Original): {french}
English (Translated): {english}

Return ONLY the English text with markers. No preamble."""

# --- UTILS ---

def trigger_status_report():
    """Runs the report generator script to update the MD status checker."""
    try:
        subprocess.run([executable, "generate_footnote_report.py"], check=False)
    except Exception as e:
        print(f"  [Status] Failed to update MD report: {e}")

def translate_worker_groq_rehab(fn_id, french_text):
    """Translates a footnote using the Two-Pass Rehab logic with Model Splitting."""
    
    naked_french = re.sub(r'\[\[t:\d+\]\]', '', french_text)
    
    for attempt in range(5):
        try:
            # PASS 1: The Brain (70B)
            # We set max_tokens to prevent hitting low TPM limits (12k)
            chat_1 = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": TRANSLATOR_PROMPT},
                    {"role": "user", "content": naked_french}
                ],
                model=MODEL_TRANSLATOR,
                max_tokens=4096,
                temperature=0.1
            )
            english_naked = chat_1.choices[0].message.content.strip()
            
            # PASS 2: The Clerk (8B)
            chat_2 = client.chat.completions.create(
                messages=[
                    {"role": "user", "content": ALIGNER_PROMPT_TEMPLATE.format(french=french_text, english=english_naked)}
                ],
                model=MODEL_ALIGNER,
                max_tokens=4096,
                temperature=0.1
            )
            final_text = chat_2.choices[0].message.content.strip()
            
            # Clean up potential LLM preamble
            final_text = re.sub(r'^Here is the.*:\s*', '', final_text, flags=re.IGNORECASE)
            
            # Basic validation: ensure tag count matches
            original_tags = re.findall(r'\[\[t:\d+\]\]', french_text)
            new_tags = re.findall(r'\[\[t:\d+\]\]', final_text)
            
            if len(original_tags) != len(new_tags):
                 continue
            
            return final_text
            
        except Exception as e:
            err_msg = str(e)
            print(f"  [Error] {fn_id} Attempt {attempt+1}: {err_msg}")
            
            if "429" in err_msg:
                wait_match = re.search(r'try again in ([\d\.ms]+)', err_msg)
                if wait_match:
                    wait_str = wait_match.group(1)
                    wait_sec = 60
                    if 'm' in wait_str and 's' in wait_str:
                        m, s = re.findall(r'(\d+)', wait_str)[:2]
                        wait_sec = int(m)*60 + int(s) + 2
                    elif 's' in wait_str:
                        wait_sec = int(re.search(r'(\d+)', wait_str).group(1)) + 2
                    print(f"  [Rate Limit] TPD Reached. Sleeping {wait_sec}s...")
                    time.sleep(wait_sec)
                else:
                    time.sleep(20)
            else:
                time.sleep(10)
                
    return None

def run_rehab_track_groq(flat_footnotes, checkpoint_file, limit=None):
    """Main loop for Two-Pass Llama Rehab."""
    print(f"\n=== Starting Llama Rehab Track (Groq: Hybrid 70B/8B) ===")
    
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
    
    total = len(sorted_keys)
    for i, k in enumerate(sorted_keys):
        print(f"  [Heartbeat] {k}: {i+1}/{total} complete (Track: Groq Rehab)")
        
        res = translate_worker_groq_rehab(k, flat_footnotes[k]['text'])
        if res:
            translated_map[k] = res
            with open(checkpoint_file, 'w') as f:
                json.dump(translated_map, f, indent=2)
            if (i+1) % 5 == 0:
                trigger_status_report()
        else:
            print(f"  [Warning] {k} failed. Skipping.")
            
    trigger_status_report()
    return translated_map

def main():
    parser = argparse.ArgumentParser(description="Llama Tag Rehab Pipeline")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of footnotes")
    args = parser.parse_args()

    with open('French_Arabic_Enriched.json', 'r') as f:
        data = json.load(f)
    
    _, flat_footnotes = extract_and_flatten(data)
    run_rehab_track_groq(flat_footnotes, "checkpoint_footnotes_gemini.json", limit=args.limit)

if __name__ == "__main__":
    main()
