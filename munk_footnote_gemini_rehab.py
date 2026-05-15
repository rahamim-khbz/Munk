import os
import json
import time
import re
import argparse
import sys
import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load Extraction logic
from munk_pipeline_groq import extract_and_flatten

load_dotenv()

# --- CONFIGURATION ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-3-flash-preview" 

client = genai.Client(api_key=GOOGLE_API_KEY)

# --- PROMPT ---
FOOTNOTE_SYSTEM_PROMPT = """You are a master scholarly translator specializing in French academic prose and medieval philosophical texts.
Your task is to translate Salomon Munk's 'Le Guide des Égarés' FOOTNOTES into precise Academic English.

REGISTER
Adopt the register of serious Victorian scholarly prose: formal, precise, somewhat elevated, but not artificially archaic. 
Prefer Latinate vocabulary where Munk makes Latinate choices in French (e.g., "faculty" not "ability"; "intellect" not "mind"; "substance" not "stuff"; "apprehension" not "grasp").
Munk's sentences are often long and periodic; preserve their syntactic structure where English permits.
Do not modernize. Do not colloquialize.

MULTILINGUAL CONTENT — CRITICAL RULES
1. Hebrew/Arabic script: DO NOT TRANSLATE. Preserve these exactly as they appear in the source.
2. Latin: translate into English inline in square brackets [Lat.: ...].
3. Greek: preserve in Greek script exactly.
4. Munk's transliterations: preserve exactly, including diacritics.

COMPLETENESS
Translate every word. Do not summarize or omit any portion. Do not add explanatory glosses inside the translation.

STRICT OUTPUT FORMAT
Return ONLY a valid JSON object mapping the input keys (e.g. "fn.123") to translated strings.
Do NOT add any preamble or markdown formatting. Just the JSON.

Input JSON format:
{ "fn.123": "French footnote text..." }

Output JSON format:
{ "fn.123": "English footnote translation..." }"""

GLOSSARY = """ TERMINOLOGY GLOSSARY — apply strictly
  intellect          → intellect          (not "mind")
  entendement        → understanding      (distinct from intellect; preserve distinction)
  forme              → form               (not "shape")
  matière            → matter             (not "material")
  faculté            → faculty            (not "ability")
  imagination        → imagination
  perfection         → perfection         (Aristotelian sense)
  agent              → agent
  cause efficiente   → efficient cause
  hypostase          → hypostasis         (not "substance")
  attributs          → attributes         (theological sense)
  essence            → essence
  accident           → accident
  substance          → substance
  mouvement          → motion             (not "movement")
  repos              → rest
  âme                → soul
  puissance          → potentiality
  acte               → actuality
  matière première   → prime matter
  intelligence séparée → separate intellect
"""

FAILED_FILE = "failed_footnotes.json"

def log_failure(fn_id, error_msg):
    failures = {}
    if os.path.exists(FAILED_FILE):
        with open(FAILED_FILE, 'r') as f:
            try: failures = json.load(f)
            except: pass
    failures[fn_id] = {
        "error": error_msg,
        "timestamp": datetime.datetime.now().isoformat()
    }
    with open(FAILED_FILE, 'w') as f:
        json.dump(failures, f, indent=2)

def translate_worker_gemini(chunk, attempt_limit=5):
    """Translates a batch of footnotes with recursive splitting and extreme resilience."""
    
    # Prepare lean prompt
    lean_chunk = {k: v['text'] if isinstance(v, dict) else v for k, v in chunk.items()}
    prompt = json.dumps(lean_chunk, indent=2)
    
    for attempt in range(attempt_limit):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=FOOTNOTE_SYSTEM_PROMPT + "\n\n" + GLOSSARY,
                    temperature=0.1 + (attempt * 0.1),
                    response_mime_type="application/json",
                    max_output_tokens=8192
                )
            )
            
            raw_text = response.text.strip()
            # Fix invalid \u escapes (where \u is not followed by 4 hex digits)
            raw_text = re.sub(r'\\u(?![0-9a-fA-F]{4})', r'\\\\u', raw_text)
            
            # Robust JSON cleanup
            is_truncated = not raw_text.endswith('}')
            if is_truncated:
                print(f"  [Repair] JSON truncated for {list(chunk.keys())[0]}. Attempting fix...")
                # Remove trailing comma or partial key/value
                raw_text = raw_text.rstrip().rstrip(',')
                if raw_text.count('"') % 2 != 0: 
                    # If odd quotes, we are in the middle of a string. Close it.
                    raw_text += '"'
                
                # After closing the string, if it still doesn't end with a value, it might be a partial key.
                # Try to find the last '" : "' or similar? 
                # Simpler: just close the object and let json.loads tell us if it's valid.
                while raw_text.count('{') > raw_text.count('}'): raw_text += '}'
            
            json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if json_match: raw_text = json_match.group(0)
            
            parsed = json.loads(raw_text)
            
            # If we were truncated and didn't get everything, we MUST split
            if (is_truncated or len(parsed) < len(chunk)) and len(chunk) > 1:
                print(f"  [Fallback] Batch incomplete ({len(parsed)}/{len(chunk)}). Splitting...")
                items = list(chunk.items())
                mid = len(items) // 2
                r1 = translate_worker_gemini(dict(items[:mid]))
                r2 = translate_worker_gemini(dict(items[mid:]))
                if r1 and r2: return {**r1, **r2}
                return None

            # Re-weave Tags
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
            
            # PERMANENT RETRY for network or rate limits
            if "RESOURCE_EXHAUSTED" in err_msg or "ConnectError" in err_msg or "timeout" in err_msg.lower():
                wait_time = 30 * (attempt + 1)
                print(f"  [Network/Limit] Pause {wait_time}s and retry... ({err_msg[:50]})")
                time.sleep(wait_time)
                return translate_worker_gemini(chunk, attempt_limit) # Infinite recursion for network issues

            # Split on JSON/Parsing errors
            if len(chunk) > 1:
                print(f"  [Immediate Split] Error in batch ({err_msg[:50]}). Splitting...")
                items = list(chunk.items())
                mid = len(items) // 2
                r1 = translate_worker_gemini(dict(items[:mid]))
                r2 = translate_worker_gemini(dict(items[mid:]))
                if r1 and r2: return {**r1, **r2}

            print(f"  [Error] {list(chunk.keys())[0]} Attempt {attempt+1} failed: {err_msg[:100]}")
            time.sleep(5 * (attempt + 1))
                
    # If we got here and chunk size is 1, it's a hard failure for that footnote
    if len(chunk) == 1:
        fn_id = list(chunk.keys())[0]
        print(f"  [Critical] Footnote {fn_id} failed repeatedly. Skipping and logging.")
        log_failure(fn_id, "Max attempts reached or unrecoverable error.")
    
    return None

def dynamic_chunk_dictionary(data, target_chars=3000):
    chunks = []
    current_chunk = {}
    current_char_count = 0
    
    for k, v in data.items():
        text_len = len(v['text']) if isinstance(v, dict) else len(str(v))
        if current_char_count + text_len > target_chars and current_chunk:
            chunks.append(current_chunk)
            current_chunk = {}
            current_char_count = 0
        current_chunk[k] = v
        current_char_count += text_len
        
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def run_footnote_track_gemini(flat_footnotes, checkpoint_file, target_chars=3000):
    print(f"\n=== Starting Bulletproof Gemini Footnote Rehab (Model: {MODEL_NAME}) ===")
    
    translated_map = {}
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            translated_map = json.load(f)
        print(f"  [Resuming] Found {len(translated_map)} items already translated.")
    
    # Load failures to avoid retrying doomed ones in the same run
    doomed_ids = set()
    if os.path.exists(FAILED_FILE):
        with open(FAILED_FILE, 'r') as f:
            try: doomed_ids = set(json.load(f).keys())
            except: pass

    remaining_items = {k: v for k, v in flat_footnotes.items() if k not in translated_map and k not in doomed_ids}
    if not remaining_items:
        print(f"  [Skip] No remaining items to translate (all done or all failed).")
        return translated_map

    chunks = dynamic_chunk_dictionary(remaining_items, target_chars)
    total_chunks = len(chunks)
    
    for i, chunk in enumerate(chunks):
        first_key = list(chunk.keys())[0]
        batch_size = len(chunk)
        print(f"  [Processing] Batch {i+1}/{total_chunks} (Starts at {first_key}, Items: {batch_size})")
        
        res = translate_worker_gemini(chunk)
        if res:
            translated_map.update(res)
            with open(checkpoint_file, 'w') as f:
                json.dump(translated_map, f, indent=2, ensure_ascii=False)
            
            # Heartbeat info
            pct = (len(translated_map) / len(flat_footnotes)) * 100
            print(f"  [Heartbeat] Progress: {len(translated_map)}/{len(flat_footnotes)} ({pct:.1f}%)")
        else:
            print(f"  [Warning] Batch starting with {first_key} could not be recovered. Moving to next.")
            
    return translated_map

def main():
    print("--- Bulletproof Gemini Footnote Pipeline ---")
    
    source_path = 'French_Healed_Enriched.json'
    if not os.path.exists(source_path):
        source_path = 'French_Arabic_Enriched.json'
        
    print(f"Loading {source_path}...")
    with open(source_path, 'r') as f:
        data = json.load(f)
    
    print("Extracting footnotes...")
    _, flat_footnotes = extract_and_flatten(data)
    
    checkpoint_file = "checkpoint_footnotes_gemini.json"
    
    try:
        run_footnote_track_gemini(flat_footnotes, checkpoint_file)
    except KeyboardInterrupt:
        print("\n[User Interrupted] Saving progress and exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n[Unexpected Global Error] {e}")
        # Final attempt to save
        sys.exit(1)

if __name__ == "__main__":
    main()
