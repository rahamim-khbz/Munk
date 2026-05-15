import os
import json
import time
import re
import sys
import datetime
import subprocess
from dotenv import load_dotenv
from google import genai
from google.genai import types
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from tqdm import tqdm

# Load Extraction logic from the most robust source
from munk_pipeline_groq import extract_and_flatten

load_dotenv()

# --- CONFIGURATION ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-3-flash-preview" 

client = genai.Client(api_key=GOOGLE_API_KEY)

# --- SCHOLARLY PROMPT ---
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
"""

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

def trigger_status_report():
    """Updates the markdown status report."""
    try:
        subprocess.run([sys.executable, "generate_footnote_report.py"], check=False)
    except:
        pass

def translate_worker_gemini(chunk, attempt_limit=3):
    """Pure worker that translates a chunk. NO RECURSION. Outer loop handles splitting."""
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
            
            # 1. Fix invalid \u escapes
            raw_text = re.sub(r'\\u(?![0-9a-fA-F]{4})', r'\\\\u', raw_text)
            
            # 2. Handle Truncation (Minimal repair before parsing)
            if not raw_text.endswith('}'):
                raw_text = raw_text.rstrip().rstrip(',')
                if raw_text.count('"') % 2 != 0: raw_text += '"'
                while raw_text.count('{') > raw_text.count('}'): raw_text += '}'
            
            # 3. Extract JSON block
            json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if json_match: raw_text = json_match.group(0)
            
            parsed = json.loads(raw_text)
            
            # 4. Alignment check
            if len(parsed) < len(chunk):
                if len(chunk) > 1: return None 
                continue # Retry single items
            
            # 5. Re-weave Tags
            final_res = {}
            for k, translated_text in parsed.items():
                if k in chunk and isinstance(chunk[k], dict) and 'tags' in chunk[k]:
                    original_tags = chunk[k]['tags']
                    def tag_sub(m):
                        tid = int(m.group(1))
                        return original_tags[tid] if tid < len(original_tags) else m.group(0)
                    final_res[k] = re.sub(r'\[\[t:(\d+)\]\]', tag_sub, str(translated_text))
                else:
                    final_res[k] = translated_text
            
            return final_res
            
        except Exception as e:
            err_msg = str(e)
            if "RESOURCE_EXHAUSTED" in err_msg:
                time.sleep(30 * (attempt + 1))
            else:
                time.sleep(2 * (attempt + 1))
                
    return None

def run_footnote_rehab():
    print(f"\n--- Parallel Gemini Footnote Pipeline (Model: {MODEL_NAME}) ---")
    
    source_path = 'French_Healed_Enriched.json'
    if not os.path.exists(source_path): source_path = 'French_Arabic_Enriched.json'
    
    print(f"Loading {source_path}...")
    with open(source_path, 'r') as f: data = json.load(f)
    
    print("Extracting footnotes...")
    _, flat_footnotes = extract_and_flatten(data)
    
    checkpoint_file = "checkpoint_footnotes_gemini.json"
    translated_map = {}
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f: translated_map = json.load(f)
        print(f"  [Resume] Found {len(translated_map)} items in checkpoint.")

    remaining_items = {k: v for k, v in flat_footnotes.items() if k not in translated_map}
    if not remaining_items:
        print("  [Done] All footnotes already translated.")
        return

    # Chunking: 3000 chars is optimal for Gemini Flash output stability
    chunks = []
    current_chunk = {}
    current_chars = 0
    for k, v in remaining_items.items():
        text_len = len(v['text'])
        if current_chars + text_len > 3000 and current_chunk:
            chunks.append(current_chunk)
            current_chunk = {}; current_chars = 0
        current_chunk[k] = v
        current_chars += text_len
    if current_chunk: chunks.append(current_chunk)

    print(f"  [Todo] {len(remaining_items)} footnotes in {len(chunks)} batches.")
    
    MAX_WORKERS = 10
    pipeline_start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Dictionary mapping future -> (chunk, start_time)
        futures = {executor.submit(translate_worker_gemini, c): (c, time.time()) for c in chunks}
        pbar = tqdm(total=len(chunks), desc="Translating")
        
        while futures:
            done, not_done = wait(futures.keys(), timeout=5, return_when=FIRST_COMPLETED)
            current_time = time.time()
            
            if done:
                for f in done:
                    if f not in futures: continue
                    chunk, start_time = futures.pop(f)
                    try:
                        res = f.result()
                        if res:
                            translated_map.update(res)
                            # Save checkpoint
                            with open(checkpoint_file, 'w') as out_f:
                                json.dump(translated_map, out_f, indent=2, ensure_ascii=False)
                        else:
                            # If it returned None, it's a candidate for splitting if > 1
                            if len(chunk) > 1:
                                items = list(chunk.items())
                                mid = len(items) // 2
                                c1, c2 = dict(items[:mid]), dict(items[mid:])
                                futures[executor.submit(translate_worker_gemini, c1)] = (c1, current_time)
                                futures[executor.submit(translate_worker_gemini, c2)] = (c2, current_time)
                                pbar.total += 1
                            else:
                                print(f"\n  [Fail] Footnote {list(chunk.keys())[0]} failed permanently.")
                    except Exception as e:
                        print(f"\n  [Fatal] Future exception: {e}")
                    
                    pbar.update(1)
            
            # Surgical fallback for stalled tasks
            stalled = []
            for f, (c, start) in futures.items():
                if current_time - start > 180 and len(c) > 1:
                    stalled.append(f)
            
            if stalled:
                print(f"\n  [Timeout] {len(stalled)} batches stalled. Splitting...")
                for f in stalled:
                    c, _ = futures.pop(f)
                    f.cancel()
                    items = list(c.items())
                    mid = len(items) // 2
                    c1, c2 = dict(items[:mid]), dict(items[mid:])
                    futures[executor.submit(translate_worker_gemini, c1)] = (c1, current_time)
                    futures[executor.submit(translate_worker_gemini, c2)] = (c2, current_time)
                    pbar.total += 1
                pbar.refresh()
            
            if len(done) > 0:
                trigger_status_report()

    print(f"\nDONE. Processed {len(remaining_items)} items.")

if __name__ == "__main__":
    try:
        run_footnote_rehab()
    except KeyboardInterrupt:
        print("\n[Stop] Interrupted by user.")
        sys.exit(0)
