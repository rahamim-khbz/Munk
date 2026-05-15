import os
import json
import time
import re
import subprocess
import argparse
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from munk_pipeline_groq import extract_and_flatten

load_dotenv()

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-3-flash-preview" 

client = genai.Client(api_key=GOOGLE_API_KEY)

# --- PROMPTS ---

MAIN_SYSTEM_PROMPT = """You are a master scholarly translator specializing in French academic prose and medieval philosophical texts.
Your task is to translate Salomon Munk's 'Le Guide des Égarés' into precise Academic English.

Tone: Modern Academic Scholarly (precise, formal, clear).
Rules:
1. Preserve all HTML tags exactly: <i>, <b>, <sup class="footnote-marker">.
2. Maintain Hebrew and Arabic scripts exactly as they appear.
3. Use formal academic vocabulary. Avoid archaic or "old-sounding" English (do NOT use words like 'hath', 'verily', 'thenceforth', 'whilst', or 'doth').
4. NO EXTERNAL KNOWLEDGE: Do NOT use any stored information you may have about 'The Guide for the Perplexed' or consult other English translations (like Friedländer or Pines). Translate ONLY what is in the provided French text, maintaining Munk's specific 19th-century perspective.
5. Return ONLY a valid JSON object mapping the input keys to translated strings.
6. Do NOT add any preamble or markdown formatting. Just the JSON.
"""

FOOTNOTE_SYSTEM_PROMPT = """You are a master scholarly translator specializing in French academic prose and medieval philosophical texts.
Your task is to translate Salomon Munk's 'Le Guide des Égarés' FOOTNOTES into precise Academic English.

Tone: Modern Academic Scholarly (precise, formal, clear).
Rules:
1. Use formal academic vocabulary. Avoid archaic or "old-sounding" English (do NOT use words like 'hath', 'verily', 'thenceforth', 'whilst', or 'doth').
2. NO EXTERNAL KNOWLEDGE: Do NOT use any stored information you may have about 'The Guide for the Perplexed' or consult other English translations (like Friedländer or Pines). Translate ONLY what is in the provided French text.
3. Do NOT translate Hebrew/Arabic scripts if present; preserve them exactly.
4. Use standard modern scholarly conventions for citations (e.g., 'See', 'Cf.', 'Note').
5. Preserve markers like [[t:N]] or [[fn:ID]] exactly in their correct relative positions.
6. Return ONLY a valid JSON object mapping the input keys (e.g. "fn.123") to translated strings.
7. Do NOT add any preamble or markdown formatting. Just the JSON.

Input JSON format:
{ "fn.123": "French footnote text..." }

Output JSON format:
{ "fn.123": "English footnote translation..." }"""

# --- GLOBAL CACHE STATE ---
ACTIVE_CACHE_NAME = None

def get_or_create_cache(system_prompt):
    global ACTIVE_CACHE_NAME
    if ACTIVE_CACHE_NAME:
        return ACTIVE_CACHE_NAME
    
    # Check if prompt is large enough for explicit caching (>1024 tokens)
    # Rough estimate: 1 word = 1.3 tokens
    token_est = len(system_prompt.split()) * 1.3
    if token_est < 1024:
        # Implicit caching will handle this small prompt automatically
        return None
    
    print(f"  [Cache] Initializing explicit context cache for {MODEL_NAME}...")
    try:
        cache = client.caches.create(
            model=MODEL_NAME,
            config=types.CreateCachedContentConfig(
                system_instruction=system_prompt,
                ttl="7200s", # 2 hours
                display_name="Munk Scholarly Persona"
            )
        )
        ACTIVE_CACHE_NAME = cache.name
        print(f"  [Cache] Created: {cache.name} (TTL: 2h)")
        return ACTIVE_CACHE_NAME
    except Exception as e:
        print(f"  [Cache Info] Explicit caching not requested or not supported. Falling back to implicit/stateless.")
        return None

# --- UTILS ---

def trigger_status_report():
    """Runs the report generator script to update the MD status checker."""
    try:
        subprocess.run([sys.executable, "generate_footnote_report.py"], check=False)
    except Exception as e:
        print(f"  [Status] Failed to update MD report: {e}")

def translate_worker_gemini(chunk, system_prompt):
    """Translates a batch of segments using Gemini 3 Flash."""
    
    # 1. Prepare lean prompt
    lean_chunk = {k: v['text'] if isinstance(v, dict) else v for k, v in chunk.items()}
    prompt = json.dumps(lean_chunk, indent=2)
    
    # 2. Handle Caching
    cache_name = get_or_create_cache(system_prompt)
    
    for attempt in range(5):
        try:
            if cache_name:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        cached_content=cache_name,
                        response_mime_type="application/json",
                    )
                )
            else:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        response_mime_type="application/json",
                    )
                )
            
            raw_text = response.text.strip()
            json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if json_match: raw_text = json_match.group(0)
            
            parsed = json.loads(raw_text)
            
            # 3. Re-weave Tags
            final_res = {}
            for k, translated_text in parsed.items():
                if k in chunk and isinstance(chunk[k], dict) and 'tags' in chunk[k]:
                    original_tags = chunk[k]['tags']
                    def tag_sub(m):
                        tid = int(m.group(1))
                        return original_tags[tid] if tid < len(original_tags) else m.group(0)
                    
                    final_res[k] = re.sub(r'\[\[t:(\d+)\]\]', tag_sub, translated_text)
                else:
                    final_res[k] = translated_text
            
            return final_res
            
        except Exception as e:
            err_msg = str(e)
            print(f"  [Error] Batch Attempt {attempt+1} failed: {err_msg}")
            
            if "RESOURCE_EXHAUSTED" in err_msg:
                print("  [Limit] Spending cap or rate limit reached. Pause 60s...")
                time.sleep(60)
            elif "expired" in err_msg.lower():
                global ACTIVE_CACHE_NAME
                ACTIVE_CACHE_NAME = None
                cache_name = get_or_create_cache(system_prompt)
            else:
                time.sleep(10)
                
    return None

def dynamic_chunk_dictionary(data, target_chars=8000):
    """Splits a dictionary into variable-sized chunks based on character count."""
    chunks = []
    current_chunk = {}
    current_char_count = 0
    
    for k, v in data.items():
        # Estimate text length (including metadata)
        text_len = len(v['text']) if isinstance(v, dict) else len(str(v))
        
        # If adding this item exceeds target and we already have items, start new chunk
        if current_char_count + text_len > target_chars and current_chunk:
            chunks.append(current_chunk)
            current_chunk = {}
            current_char_count = 0
        
        current_chunk[k] = v
        current_char_count += text_len
        
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def run_track_gemini(data_map, track_name, checkpoint_file, system_prompt, target_chars=8000):
    """Main loop for a specific translation track using dynamic chunking."""
    print(f"\n=== Starting {track_name} Track (Gemini 3 Dynamic) ===")
    
    translated_map = {}
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            translated_map = json.load(f)
        print(f"  [Resuming] Found {len(translated_map)} items already translated.")
    
    remaining_items = {k: v for k, v in data_map.items() if k not in translated_map}
    if not remaining_items:
        print(f"  [Skip] No remaining items to translate.")
        return translated_map

    chunks = dynamic_chunk_dictionary(remaining_items, target_chars)
    total_chunks = len(chunks)
    
    for i, chunk in enumerate(chunks):
        first_key = list(chunk.keys())[0]
        batch_size = len(chunk)
        print(f"  [Heartbeat] {track_name} ({first_key}): {i+1}/{total_chunks} batches (Size: {batch_size})")
        
        res = translate_worker_gemini(chunk, system_prompt)
        if res:
            translated_map.update(res)
            with open(checkpoint_file, 'w') as f:
                json.dump(translated_map, f, indent=2)
            trigger_status_report()
        else:
            print(f"  [Warning] Batch {i} failed after retries. Skipping.")
            
    return translated_map

def main():
    parser = argparse.ArgumentParser(description="Munk Translation Pipeline (Gemini 3)")
    parser.add_argument("--track", choices=["main", "footnotes"], default="main", help="Which track to run")
    args = parser.parse_args()

    print("--- Starting Modern Gemini 3 Optimized Pipeline ---")
    
    source_path = 'French_Arabic_Enriched.json'
    with open(source_path, 'r') as f:
        data = json.load(f)
    
    flat_main, flat_footnotes = extract_and_flatten(data)
    
    if args.track == "main":
        run_track_gemini(flat_main, "Main Text", "checkpoint_main_text_groq.json", MAIN_SYSTEM_PROMPT, target_chars=12000)
    else:
        run_track_gemini(flat_footnotes, "Footnotes", "checkpoint_footnotes_gemini.json", FOOTNOTE_SYSTEM_PROMPT, target_chars=8000)

if __name__ == "__main__":
    main()
