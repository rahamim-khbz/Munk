import json
import os
import re
import datetime
import base64
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from google import genai
from google.genai import types
from tqdm import tqdm
from dotenv import load_dotenv
from pydantic import BaseModel

# --- CONFIGURATION ---
load_dotenv()
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
# Clean client initialization
client = genai.Client(api_key=GOOGLE_API_KEY)

MODEL_OCR = 'gemini-3-flash-preview'
MODEL_TRANS = 'gemini-3-flash-preview' 

BASE_DIR = '/Users/rayhabbaz/Library/CloudStorage/GoogleDrive-rhabbaz@gmail.com/My Drive/Munks Guide'
INPUT_FILE = os.path.join(BASE_DIR, 'French.json')
OUTPUT_FILE = os.path.join(BASE_DIR, 'munk_translations.json')
OCR_CHECKPOINT = os.path.join(BASE_DIR, 'ocr_checkpoint.json')
OCR_ENRICHED_FILE = os.path.join(BASE_DIR, 'French_Arabic_Enriched.json')

MAX_OCR_WORKERS = 10
MAX_TRANS_WORKERS = 5 # Keep it lower to avoid rate limits with sync calls

# --- DATA MODELS ---
class TranslatedSegment(BaseModel):
    ref: str
    english: str
    tr_notes: list[str]

# --- PROMPTS ---
SYSTEM_PROMPT = '''ROLE AND TASK
You are translating the main body of Salomon Munk's French philosophical
translation of Maimonides' Guide for the Perplexed, published as Guide des
egarés, Paris, 1856. Munk's French is itself a translation from the original
Judeo-Arabic (Dalalat al-Ha'irin). Your sole task is to render Munk's French
into English faithfully and completely.
... [Rest of prompt same as before] ...
'''
# I'll shorten the prompt for the script but in practice it should be full.
# For the sake of the user's script, I'll include the full logic.

# [Importing same prompts as async version...]
from munk_translation_pipeline_async import SYSTEM_PROMPT, GLOSSARY, flatten_text, build_segment_list

# --- OCR UTILITIES ---

def ocr_image_worker(b64):
    for attempt in range(5):
        try:
            img = types.Part.from_bytes(data=base64.b64decode(b64), mime_type='image/jpeg')
            res = client.models.generate_content(
                model=MODEL_OCR,
                contents=['Provide ONLY the Arabic or Hebrew script of the word in this image. No other text.', img]
            )
            return b64, res.text.strip()
        except Exception as e:
            if "429" in str(e):
                time.sleep(5 * (attempt + 1))
            elif attempt == 4:
                return b64, "[OCR_ERROR]"
            time.sleep(1)

def run_ocr_enrichment(limit=None):
    if not os.path.exists(INPUT_FILE): return None
    with open(INPUT_FILE, 'r', encoding='utf-8') as f: data = json.load(f)
    
    unique_b64s = set()
    def find_all_images(node):
        if isinstance(node, dict): 
            for v in node.values(): find_all_images(v)
        elif isinstance(node, list): 
            for x in node: find_all_images(x)
        elif isinstance(node, str):
            for b64 in re.findall(r'data:image/[^;]+;base64,([a-zA-Z0-9+/=]+)', node):
                unique_b64s.add(b64)
    find_all_images(data)
    
    ocr_map = {}
    if os.path.exists(OCR_CHECKPOINT):
        with open(OCR_CHECKPOINT, 'r', encoding='utf-8') as f: ocr_map = json.load(f)
    
    todo = [b64 for b64 in unique_b64s if b64 not in ocr_map]
    if limit: todo = todo[:limit]
    
    if todo:
        print(f"OCR: {len(todo)} images to process...")
        with ThreadPoolExecutor(max_workers=MAX_OCR_WORKERS) as executor:
            futures = {executor.submit(ocr_image_worker, b): b for b in todo}
            for future in tqdm(as_completed(futures), total=len(todo), desc="OCRing"):
                b64, text = future.result()
                ocr_map[b64] = text
                # Partial save
                if len(ocr_map) % 50 == 0:
                    with open(OCR_CHECKPOINT, 'w', encoding='utf-8') as f: json.dump(ocr_map, f)

    def replace_images(node):
        if isinstance(node, dict): return {k: replace_images(v) for k, v in node.items()}
        if isinstance(node, list): return [replace_images(x) for x in node]
        if isinstance(node, str):
            matches = re.findall(r'data:image/[^;]+;base64,([a-zA-Z0-9+/=]+)', node)
            for b64 in matches:
                word = ocr_map.get(b64, "[IMAGE]")
                tag_pattern = r'<img [^>]*data:image/[^;]+;base64,' + re.escape(b64) + r'[^>]*>' 
                node = re.sub(tag_pattern, f'<span dir="rtl">{word}</span>', node)
            return node
        return node

    enriched_data = replace_images(data)
    with open(OCR_ENRICHED_FILE, 'w', encoding='utf-8') as f: json.dump(enriched_data, f, indent=2)
    return enriched_data

# --- TRANSLATION UTILITIES ---

def clean_json_response(text):
    # Remove potential markdown code blocks
    text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE)
    return text.strip()

def translate_worker(chunk, prev_french):
    payload = [{'ref': s['ref'], 'french': s['french'], 'french_footnotes': s.get('french_footnotes', [])} for s in chunk]
    user_msg = f"CONTEXT — preceding segment (do not translate):\n\n{prev_french}\n\nTRANSLATE THESE SEGMENTS:\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
    
    first_ref = chunk[0]['ref']
    for attempt in range(5):
        try:
            print(f"  [Chunk {first_ref}] Attempt {attempt+1}...")
            res = client.models.generate_content(
                model=MODEL_TRANS,
                contents=user_msg,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT + "\n\n" + GLOSSARY,
                    temperature=0.1 + (attempt * 0.1),
                    response_mime_type='application/json',
                    response_schema=list[TranslatedSegment]
                )
            )
            raw_text = clean_json_response(res.text)
            try:
                parsed = json.loads(raw_text)
                if len(parsed) != len(chunk):
                    print(f"  [Chunk {first_ref}] Alignment mismatch: got {len(parsed)}, expected {len(chunk)}. Retrying.")
                    continue
                
                # --- Word Count Validation ---
                for trans in parsed:
                    ref = trans['ref']
                    orig = next((s for s in chunk if s['ref'] == ref), None)
                    if orig:
                        fr_words = len(orig['french'].split())
                        en_words = len(trans['english'].split())
                        diff_pct = ((en_words - fr_words) / fr_words) * 100 if fr_words > 0 else 0.0
                        trans['word_count_diff_pct'] = round(diff_pct, 1)
                        trans['word_count_flag'] = abs(diff_pct) > 20.0
                        if trans['word_count_flag']:
                            print(f"    \033[91m⚠️ [Flag]\033[0m {ref} word count diff: {diff_pct:+.1f}% (Fr:{fr_words} -> En:{en_words})")
                
                return parsed
            except json.JSONDecodeError as je:
                print(f"  [Chunk {first_ref}] JSON Error on attempt {attempt+1}")
                if attempt == 4:
                    err_log = f"error_{first_ref}.json"
                    with open(err_log, 'w', encoding='utf-8') as f: f.write(raw_text)
                    return None
        except Exception as e:
            print(f"  [Chunk {first_ref}] API Error: {str(e)[:100]}")
            if "429" in str(e):
                time.sleep(15 * (attempt + 1))
            elif attempt == 4:
                return None
            time.sleep(5)
    return None

def run_translation_pipeline(segments):
    results = {'segments': {}, 'stats': {'completed': 0}}
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f: results = json.load(f)
    
    done_refs = set(results['segments'].keys())
    chapters = {}
    for s in segments: chapters.setdefault(s['chapter'], []).append(s)
    
    todo_fragments = []
    for chap_name, segs in chapters.items():
        if any(s['ref'] not in done_refs for s in segs):
            # Split into chunks of 8 to prevent token overflow and massive hangs
            for i in range(0, len(segs), 8):
                fragment = segs[i:i+8]
                if any(f['ref'] not in done_refs for f in fragment):
                    # Find context for this specific fragment
                    first_ref = fragment[0]['ref']
                    idx = [s['ref'] for s in segments].index(first_ref)
                    prev_f = segments[idx-1]['french'] if idx > 0 else "[First segment]"
                    todo_fragments.append((fragment, prev_f))

    if todo_fragments:
        print(f"Translation: {len(todo_fragments)} fragments to process...")
        completed_fragments = 0
        failed_fragments = 0
        pipeline_start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=MAX_TRANS_WORKERS) as executor:
            future_to_frag = {executor.submit(translate_worker, c, pf): c for c, pf in todo_fragments}
            for future in tqdm(as_completed(future_to_frag), total=len(todo_fragments), desc="Translating"):
                res_list = future.result()
                frag_data = future_to_frag[future]
                current_chapter = frag_data[0]['chapter'] if frag_data else "Unknown"
                
                if res_list:
                    for item in res_list:
                        ref = item['ref']
                        # Find original segment
                        orig = next((s for s in segments if s['ref'] == ref), None)
                        if orig:
                            results['segments'][ref] = {
                                **orig,
                                'english': item['english'],
                                'tr_notes': item.get('tr_notes', []),
                                'word_count_diff_pct': item.get('word_count_diff_pct', 0.0),
                                'word_count_flag': item.get('word_count_flag', False),
                                'timestamp': datetime.datetime.now().isoformat()
                            }
                    completed_fragments += 1
                else:
                    failed_fragments += 1
                
                # Periodic save and heartbeat
                if (completed_fragments + failed_fragments) % 5 == 0:
                    elapsed = time.time() - pipeline_start_time
                    rate_per_frag = elapsed / (completed_fragments + failed_fragments)
                    rate_per_seg = rate_per_frag / 8.0 # roughly 8 segments per fragment

                    parts_remaining = {'Prefatory/Letter': 0, 'Part 1': 0, 'Part 2': 0, 'Part 3': 0}
                    done_refs = set(results['segments'].keys())
                    for s in segments:
                        if s['ref'] not in done_refs:
                            if 'Part 1' in s['chapter']: parts_remaining['Part 1'] += 1
                            elif 'Part 2' in s['chapter']: parts_remaining['Part 2'] += 1
                            elif 'Part 3' in s['chapter']: parts_remaining['Part 3'] += 1
                            else: parts_remaining['Prefatory/Letter'] += 1
                            
                    print(f"\n[Heartbeat] Success: {completed_fragments} | Failures: {failed_fragments}")
                    print(f"  -> Currently processing: {current_chapter}")
                    print("  -> Estimated Time Remaining:")
                    
                    for part, rem in parts_remaining.items():
                        if rem > 0:
                            rem_secs = rem * rate_per_seg
                            hrs = int(rem_secs // 3600)
                            mins = int((rem_secs % 3600) // 60)
                            print(f"     - {part}: {rem} segments left (~{hrs}h {mins}m)")
                            
                    total_rem = sum(parts_remaining.values())
                    if total_rem > 0:
                        total_secs = total_rem * rate_per_seg
                        total_hrs = int(total_secs // 3600)
                        total_mins = int((total_secs % 3600) // 60)
                        print(f"     - TOTAL BOOK: {total_rem} segments left (~{total_hrs}h {total_mins}m)")

                    # Sort and Save
                    ordered_refs = [s['ref'] for s in segments]
                    results['segments'] = {r: results['segments'][r] for r in ordered_refs if r in results['segments']}
                    results['stats']['completed'] = len(results['segments'])
                    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                        json.dump(results, f, indent=2, ensure_ascii=False)
                    print(f"  -> {OUTPUT_FILE} updated. Total translated segments: {len(results['segments'])}")
                    update_status_tracker(segments, results['segments'])

        # Final Save
        ordered_refs = [s['ref'] for s in segments]
        results['segments'] = {r: results['segments'][r] for r in ordered_refs if r in results['segments']}
        results['stats']['completed'] = len(results['segments'])
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"DONE. Final count: {len(results['segments'])}")
        update_status_tracker(segments, results['segments'])

def update_status_tracker(expected_segments, results_segments):
    translated_refs = set(results_segments.keys())
    chapters = {}
    for s in expected_segments:
        ch = s['chapter']
        if ch not in chapters:
            chapters[ch] = {'total': 0, 'translated': 0, 'missing_refs': [], 'segments': []}
        
        chapters[ch]['total'] += 1
        
        status = 'Missing'
        diff_str = ""
        if s['ref'] in translated_refs:
            chapters[ch]['translated'] += 1
            status = 'Translated'
            seg_data = results_segments[s['ref']]
            if 'word_count_diff_pct' in seg_data:
                pct = seg_data['word_count_diff_pct']
                is_flagged = seg_data.get('word_count_flag', False)
                if is_flagged:
                    diff_str = f"🔴 {pct:+.1f}%"
                else:
                    diff_str = f"🟢 {pct:+.1f}%"
        else:
            chapters[ch]['missing_refs'].append(s['ref'])
            
        chapters[ch]['segments'].append({
            'ref': s['ref'],
            'status': status,
            'diff_str': diff_str
        })
            
    report_path = '/Users/rayhabbaz/.gemini/antigravity/brain/3d1d1fdf-f0d1-412e-8f26-5d58860631ff/translation_status_report.md'
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Translation Status Report\n\n")
            
            total_segs = len(expected_segments)
            total_trans = len(translated_refs)
            f.write(f"**Total Segments (Source):** {total_segs}  \n")
            f.write(f"**Total Translated:** {total_trans}  \n")
            f.write(f"**Progress:** {(total_trans/total_segs)*100:.1f}%  \n\n")
            
            f.write("## Chapter Summary\n\n")
            f.write("| Chapter | Total Segments | Translated | Status |\n")
            f.write("|---|---|---|---|\n")
            
            for ch, stats in chapters.items():
                total = stats['total']
                trans = stats['translated']
                status_str = "✅ Complete" if trans == total else f"❌ Missing {total - trans}"
                if trans == 0:
                    status_str = "⏳ Pending"
                f.write(f"| {ch} | {total} | {trans} | {status_str} |\n")
                
            f.write("\n## Detailed Segment Status\n\n")
            f.write("Only showing chapters with incomplete translations.\n\n")
            
            for ch, stats in chapters.items():
                total = stats['total']
                trans = stats['translated']
                
                if trans > 0 and trans < total:
                    f.write(f"### {ch}\n")
                    f.write("| Segment Ref | Status | Word Count Diff |\n")
                    f.write("|---|---|---|\n")
                    for s in stats['segments']:
                        icon = "✅" if s['status'] == 'Translated' else "❌"
                        f.write(f"| `{s['ref']}` | {icon} {s['status']} | {s.get('diff_str', '')} |\n")
                    f.write("\n")
    except Exception as e:
        print(f"Warning: Could not update status report: {e}")

def main():
    print("=== Munk Threaded Pipeline ===")
    if os.path.exists(OCR_ENRICHED_FILE):
        print(f"Loading existing {OCR_ENRICHED_FILE}")
        with open(OCR_ENRICHED_FILE, 'r', encoding='utf-8') as f: enriched_data = json.load(f)
    else:
        enriched_data = run_ocr_enrichment()
    
    if enriched_data:
        segments = build_segment_list(enriched_data)
        run_translation_pipeline(segments)
    print("=== Complete ===")

if __name__ == "__main__":
    main()
