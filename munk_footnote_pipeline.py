import json
import os
import re
import datetime
import base64
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, FIRST_COMPLETED
from google import genai
from google.genai import types
from tqdm import tqdm
from dotenv import load_dotenv
from pydantic import BaseModel

# --- CONFIGURATION ---
load_dotenv()
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
client = genai.Client(api_key=GOOGLE_API_KEY)

MODEL_TRANS = 'gemini-2.5-flash' # Switching to Gemini 2.5 Flash as requested

BASE_DIR = '/Users/rayhabbaz/Library/CloudStorage/GoogleDrive-rhabbaz@gmail.com/My Drive/Munks Guide'
INPUT_FILE = os.path.join(BASE_DIR, 'French_Arabic_Enriched.json')
OUTPUT_FILE = os.path.join(BASE_DIR, 'munk_translated_footnotes.json')

MAX_TRANS_WORKERS = 5 
BATCH_SIZE = 25

# --- DATA MODELS ---
class TranslatedFootnote(BaseModel):
    id: str
    english_footnote: str

# --- PROMPTS ---
SYSTEM_PROMPT = '''ROLE AND TASK
You are translating the scholarly footnotes of Salomon Munk's French philosophical translation of Maimonides' Guide for the Perplexed.
Your sole task is to render Munk's French footnotes into English faithfully and completely.

MULTILINGUAL CONTENT — CRITICAL RULES
Munk frequently embeds Hebrew, Arabic, Greek, and Latin within his French prose. Handle each as follows:
  - Hebrew/Arabic text in HTML tags (e.g. `<span dir="rtl">...</span>`): PRESERVE EXACTLY. Do not translate the Hebrew/Arabic characters.
  - Munk's transliterations: preserve exactly, including diacritics.
  - Latin: translate into English inline in square brackets [Lat.: ...].
  - Greek: preserve in Greek script.
  - Citations: use English book names, preserve chapter/verse numbering.

STRICT OUTPUT FORMAT
You will receive a JSON array of footnotes. Each object has an `id` and a `french_footnote`.
Return a JSON array of objects with keys: `id` and `english_footnote`.
Do not output Markdown code blocks, just raw JSON.
'''

def flatten_text(t):
    if isinstance(t, list): return ' '.join(flatten_text(x) for x in t)
    return t or ''

def extract_all_footnotes(data):
    footnotes_list = []
    
    def extract_from_text(text, ref_base):
        pattern = r'<sup class="footnote-marker">\(\d+\)</sup><i class="footnote">(.*?)</i>|<i class="footnote">(.*?)</i>'
        matches = re.findall(pattern, text, flags=re.DOTALL)
        for i, match in enumerate(matches):
            fn_text = match[0] or match[1]
            fn_id = f"{ref_base}_fn{i+1}"
            footnotes_list.append({
                'id': fn_id,
                'french_footnote': fn_text,
                'ref_base': ref_base # keep track of origin
            })

    # 1. Letter to R Joseph
    letter = data['text'].get('Letter to R Joseph son of Judah', [])
    for i, t in enumerate(letter):
        txt = flatten_text(t).strip()
        if txt: extract_from_text(txt, f'Guide_for_the_Perplexed_Letter_to_R_Joseph_son_of_Judah.{i+1}')

    # 2. Prefatory Remarks
    prefatory = data['text'].get('Prefatory Remarks', [])
    for i, t in enumerate(prefatory):
        txt = flatten_text(t).strip()
        if txt: extract_from_text(txt, f'Guide_for_the_Perplexed_Prefatory_Remarks.{i+1}')

    # 3. Parts 1, 2, 3
    for part in ['Part 1', 'Part 2', 'Part 3']:
        part_data = data['text'].get(part, {})
        if not part_data: continue

        # Introduction for the Part
        for i, t in enumerate(part_data.get('Introduction', [])):
            txt = flatten_text(t).strip()
            if txt: extract_from_text(txt, f'Guide_for_the_Perplexed_{part.replace(" ", "_")}_Introduction.{i+1}')

        # Chapters for the Part
        chapters = part_data.get('', [])
        for ch_idx, chapter_paras in enumerate(chapters):
            ch = ch_idx + 1
            for i, t in enumerate(chapter_paras):
                txt = flatten_text(t).strip()
                if txt: extract_from_text(txt, f'Guide_for_the_Perplexed_{part.replace(" ", "_")}.{ch}.{i+1}')

    return footnotes_list

def translate_worker(chunk):
    payload = [{'id': f['id'], 'french_footnote': f['french_footnote']} for f in chunk]
    user_msg = f"TRANSLATE THESE FOOTNOTES:\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
    
    first_id = chunk[0]['id']
    for attempt in range(5):
        try:
            res = client.models.generate_content(
                model=MODEL_TRANS,
                contents=user_msg,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.1 + (attempt * 0.1),
                    response_mime_type='application/json',
                    response_schema=list[TranslatedFootnote]
                )
            )
            
            raw_text = res.text.strip()
            parsed = json.loads(raw_text)
            
            if len(parsed) != len(chunk):
                print(f"  [Batch {first_id}] Alignment mismatch: got {len(parsed)}, expected {len(chunk)}. Retrying.")
                continue
                
            return parsed
        except Exception as e:
            time.sleep(2 * (attempt + 1))
            
    return None

def pre_flight_check():
    print(f"--- Pre-flight Check: Testing connection to {MODEL_TRANS} ---")
    try:
        res = client.models.generate_content(
            model=MODEL_TRANS,
            contents="hi",
            config=types.GenerateContentConfig(max_output_tokens=5)
        )
        if res.text:
            print("  [OK] Connection successful.")
            return True
    except Exception as e:
        print(f"  [CRITICAL] Pre-flight failed: {e}")
        return False
    return False

def run_pipeline():
    print("=== Munk Footnote Pipeline ===")
    
    if not pre_flight_check():
        print("Pipeline aborted due to connectivity issues. Please check your internet/API key.")
        return
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    all_fns = extract_all_footnotes(data)
    print(f"Extracted {len(all_fns)} total footnotes from source.")
    
    results = {}
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            results = json.load(f)
            
    done_ids = set(results.keys())
    todo_fns = [f for f in all_fns if f['id'] not in done_ids]
    
    if not todo_fns:
        print("All footnotes translated!")
        return
        
    print(f"Translation: {len(todo_fns)} footnotes pending.")
    
    batches = [todo_fns[i:i+BATCH_SIZE] for i in range(0, len(todo_fns), BATCH_SIZE)]
    print(f"Grouped into {len(batches)} batches of ~{BATCH_SIZE}.")
    
    completed_batches = 0
    failed_batches = 0
    pipeline_start_time = time.time()
    
    # Increase max_workers to avoid thread starvation from lingering tasks
    with ThreadPoolExecutor(max_workers=MAX_TRANS_WORKERS * 20) as executor:
        # Dictionary mapping future -> (chunk, start_time)
        futures = {executor.submit(translate_worker, b): (b, time.time()) for b in batches}
        pbar = tqdm(total=len(batches), desc="Translating")
        
        while futures:
            # Short wait to keep the loop responsive to timeouts
            done, not_done = wait(futures.keys(), timeout=10, return_when=FIRST_COMPLETED)
            
            current_time = time.time()
            
            if done:
                for future in done:
                    if future not in futures:
                        continue # Already handled (e.g. by the timeout splitter)
                        
                    chunk, start_time = futures.pop(future)
                    try:
                        res_list = future.result()
                        if res_list:
                            for item in res_list:
                                results[item['id']] = item['english_footnote']
                            completed_batches += 1
                        else:
                            failed_batches += 1
                    except Exception as e:
                        print(f"\n  [Error] Batch failed at {chunk[0]['id'] if chunk else 'unknown'}: {e}")
                        failed_batches += 1
                    
                    pbar.update(1)
            
            # SURGICAL FALLBACK: Check for specific stalled tasks
            stalled_futures = []
            for f, (chunk, start_time) in futures.items():
                if current_time - start_time > 120 and len(chunk) > 1:
                    stalled_futures.append(f)
            
            if stalled_futures:
                print(f"\n[Timeout] {len(stalled_futures)} tasks stalled for 120s. Splitting them...")
                for f in stalled_futures:
                    chunk, _ = futures.pop(f)
                    f.cancel() # Future is already running, so this mostly marks it
                    
                    mid = len(chunk) // 2
                    b1, b2 = chunk[:mid], chunk[mid:]
                    
                    # Submit two smaller tasks to replace the big slow one
                    futures[executor.submit(translate_worker, b1)] = (b1, current_time)
                    futures[executor.submit(translate_worker, b2)] = (b2, current_time)
                    
                    pbar.total += 1 # One task became two
                pbar.refresh()

            # Periodic save & Heartbeat
            total_proc = completed_batches + failed_batches
            if total_proc > 0 and total_proc % 5 == 0:
                elapsed = time.time() - pipeline_start_time
                rate = elapsed / total_proc
                rem_count = len(all_fns) - len(results)
                
                # Dynamic ETA based on current average chunk size
                avg_sz = sum(len(c) for c, _ in futures.values()) / max(1, len(futures)) if futures else BATCH_SIZE
                rem_batches = rem_count / max(1, avg_sz)
                rem_time = rem_batches * rate
                
                mins = int(rem_time // 60)
                hrs = int(mins // 60)
                mins = mins % 60
                
                print(f"\n[Heartbeat] Success: {completed_batches} | Failures: {failed_batches} | Active: {len(futures)}")
                print(f"  -> ETA: ~{hrs}h {mins}m")
                with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                    
        pbar.close()
                    
    # Final Save
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"DONE. Total translated footnotes: {len(results)}")

if __name__ == '__main__':
    run_pipeline()
