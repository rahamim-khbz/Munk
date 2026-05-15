import asyncio
import json
import os
import re
import datetime
import base64
from google import genai
from google.genai import types
from tqdm.asyncio import tqdm
from dotenv import load_dotenv
from pydantic import BaseModel

# --- CONFIGURATION ---
load_dotenv()
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
client = genai.Client(api_key=GOOGLE_API_KEY)

# Using models confirmed to work in the user's environment
MODEL_OCR = 'gemini-3-flash-preview'
MODEL_TRANS = 'gemini-3-flash-preview' 

INPUT_FILE = 'French.json'
OUTPUT_FILE = 'munk_translations.json'
OCR_CHECKPOINT = 'ocr_checkpoint.json'
OCR_ENRICHED_FILE = 'French_Arabic_Enriched.json'

MAX_OCR_CONCURRENCY = 20
MAX_TRANS_CONCURRENCY = 10

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

You are translating Munk — not Maimonides. Do not consult, harmonize with,
or import phrasing from other English translations of the Guide (Friedländer
1881, Pines 1963, or any other). If you are aware of how another translator
renders a given passage, set that knowledge aside entirely.

REGISTER
Adopt the register of serious Victorian scholarly prose: formal, precise,
somewhat elevated, but not artificially archaic. Prefer Latinate vocabulary
where Munk makes Latinate choices in French (e.g., "faculty" not "ability";
"intellect" not "mind"; "substance" not "stuff"; "apprehension" not "grasp").
Munk's sentences are often long and periodic; preserve their syntactic
structure where English permits, rather than breaking them into shorter units.
Do not modernize. Do not colloquialize.

COMPLETENESS
Translate every word Munk wrote. Do not summarize, compress, or omit any
portion of the input. Do not add explanatory glosses, parenthetical
clarifications, or interpretive expansions of your own.

MULTILINGUAL CONTENT — CRITICAL RULES
Munk frequently embeds Hebrew, Arabic, Greek, and Latin within his French
prose. Handle each as follows:
  - Hebrew in Hebrew script: preserve exactly.
  - Munk's transliterations: preserve exactly, including diacritics.
  - Latin: translate into English inline in square brackets [Lat.: ...].
  - Greek: preserve in Greek script.
  - Citations: use English book names, preserve chapter/verse numbering.

MUNK'S FOOTNOTES
The original HTML footnotes have been extracted into the `french_footnotes` array in your JSON payload. 
The main text (`french`) now contains markdown markers (e.g. `[^1]`).
You MUST translate the `french` text keeping the `[^1]` markers exactly where they are.
You MUST translate the items in `french_footnotes` and output them into the `tr_notes` JSON array in the exact same order.

STRICT OUTPUT FORMAT
Return a JSON array of objects with keys: ref, english, tr_notes.
'''

GLOSSARY = ''' TERMINOLOGY GLOSSARY
  intellect          → intellect
  entendement        → understanding
  forme              → form
  matière            → matter
  faculté            → faculty
  imagination        → imagination
  perfection         → perfection
  substance          → substance
  mouvement          → motion
  repos              → rest
  âme                → soul
  puissance          → potentiality
  acte               → actuality
'''

# --- OCR UTILITIES ---

async def ocr_image_worker(b64, semaphore, pbar):
    async with semaphore:
        for attempt in range(5):
            try:
                img = types.Part.from_bytes(data=base64.b64decode(b64), mime_type='image/jpeg')
                res = await client.aio.models.generate_content(
                    model=MODEL_OCR,
                    contents=['Provide ONLY the Arabic or Hebrew script of the word in this image. No other text.', img]
                )
                pbar.update(1)
                return b64, res.text.strip()
            except Exception as e:
                if "429" in str(e):
                    await asyncio.sleep(5 * (attempt + 1))
                elif attempt == 4:
                    pbar.update(1)
                    return b64, "[OCR_ERROR]"
                await asyncio.sleep(1)

async def run_ocr_enrichment(limit=None):
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return None
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
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
        with open(OCR_CHECKPOINT, 'r', encoding='utf-8') as f:
            ocr_map = json.load(f)
        print(f"Loaded {len(ocr_map)} results from checkpoint.")
    
    todo = [b64 for b64 in unique_b64s if b64 not in ocr_map]
    if limit:
        todo = todo[:limit]
    print(f"OCR: {len(todo)} new images to process.")
    
    if todo:
        semaphore = asyncio.Semaphore(MAX_OCR_CONCURRENCY)
        pbar = tqdm(total=len(todo), desc="OCRing images")
        
        batch_size = 50
        for i in range(0, len(todo), batch_size):
            batch = todo[i:i+batch_size]
            tasks = [ocr_image_worker(b, semaphore, pbar) for b in batch]
            results = await asyncio.gather(*tasks)
            for b64, text in results: ocr_map[b64] = text
            with open(OCR_CHECKPOINT, 'w', encoding='utf-8') as f:
                json.dump(ocr_map, f, ensure_ascii=False)
        pbar.close()

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

    print("Reconstructing enriched JSON...")
    enriched_data = replace_images(data)
    with open(OCR_ENRICHED_FILE, 'w', encoding='utf-8') as f:
        json.dump(enriched_data, f, ensure_ascii=False, indent=2)
    print(f"OCR Enrichment Complete -> {OCR_ENRICHED_FILE}")
    return enriched_data

# --- TRANSLATION UTILITIES ---

def flatten_text(t):
    if isinstance(t, list): return ' '.join(flatten_text(x) for x in t)
    return t or ''

def build_segment_list(data):
    segments = []
    
    def extract_footnotes(text):
        footnotes = []
        pattern = r'<sup class="footnote-marker">\(\d+\)</sup><i class="footnote">(.*?)</i>|<i class="footnote">(.*?)</i>'
        def replacer(match):
            fn_text = match.group(1) or match.group(2)
            idx = len(footnotes) + 1
            footnotes.append(fn_text)
            return f"[^{idx}]"
        new_text = re.sub(pattern, replacer, text, flags=re.DOTALL)
        return new_text, footnotes

    # 1. Letter to R Joseph
    letter = data['text'].get('Letter to R Joseph son of Judah', [])
    for i, t in enumerate(letter):
        txt = flatten_text(t).strip()
        if txt:
            txt, fns = extract_footnotes(txt)
            segments.append({
                'ref': f'Guide_for_the_Perplexed_Letter_to_R_Joseph_son_of_Judah.{i+1}',
                'chapter': 'Letter',
                'paragraph': i + 1,
                'french': txt,
                'french_footnotes': fns
            })

    # 2. Prefatory Remarks
    prefatory = data['text'].get('Prefatory Remarks', [])
    for i, t in enumerate(prefatory):
        txt = flatten_text(t).strip()
        if txt:
            txt, fns = extract_footnotes(txt)
            segments.append({
                'ref': f'Guide_for_the_Perplexed_Prefatory_Remarks.{i+1}',
                'chapter': 'Prefatory',
                'paragraph': i + 1,
                'french': txt,
                'french_footnotes': fns
            })

    # 3. Parts 1, 2, 3
    for part in ['Part 1', 'Part 2', 'Part 3']:
        part_data = data['text'].get(part, {})
        if not part_data: continue

        # Introduction for the Part
        for i, t in enumerate(part_data.get('Introduction', [])):
            txt = flatten_text(t).strip()
            if txt:
                txt, fns = extract_footnotes(txt)
                segments.append({
                    'ref': f'Guide_for_the_Perplexed_{part.replace(" ", "_")}_Introduction.{i+1}',
                    'chapter': f'{part} Intro',
                    'paragraph': i + 1,
                    'french': txt,
                    'french_footnotes': fns
                })

        # Chapters for the Part
        chapters = part_data.get('', [])
        for ch_idx, chapter_paras in enumerate(chapters):
            ch = ch_idx + 1
            for i, t in enumerate(chapter_paras):
                txt = flatten_text(t).strip()
                if txt:
                    txt, fns = extract_footnotes(txt)
                    segments.append({
                        'ref': f'Guide_for_the_Perplexed_{part.replace(" ", "_")}.{ch}.{i+1}',
                        'chapter': f'{part} Ch {ch}',
                        'paragraph': i + 1,
                        'french': txt,
                        'french_footnotes': fns
                    })
    return segments

async def translate_worker(chunk, prev_french, semaphore, pbar):
    async with semaphore:
        payload = [{'ref': s['ref'], 'french': s['french']} for s in chunk]
        user_msg = f"CONTEXT — preceding segment (do not translate):\\n\\n{prev_french}\\n\\nTRANSLATE THESE SEGMENTS:\\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
        
        for attempt in range(5):
            try:
                res = await client.aio.models.generate_content(
                    model=MODEL_TRANS,
                    contents=user_msg,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT + "\n\n" + GLOSSARY,
                        temperature=0.1 + (attempt * 0.1),
                        response_mime_type='application/json',
                        response_schema=list[TranslatedSegment]
                    )
                )
                parsed = json.loads(res.text)
                if len(parsed) != len(chunk):
                    raise ValueError("Segment count mismatch")
                pbar.update(1)
                return parsed
            except Exception as e:
                if "429" in str(e):
                    await asyncio.sleep(10 * (attempt + 1))
                elif attempt == 4:
                    print(f"Fatal error in chunk starting {chunk[0]['ref']}: {e}")
                    return None
                await asyncio.sleep(1)

async def run_translation_pipeline(segments):
    results = {'segments': {}, 'stats': {'completed': 0}}
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            results = json.load(f)
    
    done_refs = set(results['segments'].keys())
    
    # Group by chapter for contextual processing
    chapters = {}
    for s in segments:
        chapters.setdefault(s['chapter'], []).append(s)
    
    todo_chapters = []
    for chap_name, segs in chapters.items():
        if any(s['ref'] not in done_refs for s in segs):
            # Find context from the full ordered list
            first_todo_ref = segs[0]['ref']
            idx = [s['ref'] for s in segments].index(first_todo_ref)
            prev_f = segments[idx-1]['french'] if idx > 0 else "[First segment]"
            todo_chapters.append((segs, prev_f))

    print(f"Translation: {len(todo_chapters)} chapters remaining.")
    
    if todo_chapters:
        semaphore = asyncio.Semaphore(MAX_TRANS_CONCURRENCY)
        pbar = tqdm(total=len(todo_chapters), desc="Translating chapters")
        
        for i in range(0, len(todo_chapters), 5):
            batch = todo_chapters[i:i+5]
            tasks = [translate_worker(c, pf, semaphore, pbar) for c, pf in batch]
            batch_results = await asyncio.gather(*tasks)
            
            for res_list in batch_results:
                if res_list:
                    for item in res_list:
                        ref = item['ref']
                        orig = next(s for s in segments if s['ref'] == ref)
                        results['segments'][ref] = {
                            **orig,
                            'english': item['english'],
                            'tr_notes': item.get('tr_notes', []),
                            'timestamp': datetime.datetime.now().isoformat()
                        }
            
            # Sort the dictionary based on the original chronological segment order
            ordered_refs = [s['ref'] for s in segments]
            results['segments'] = {
                ref: results['segments'][ref] 
                for ref in ordered_refs if ref in results['segments']
            }
            
            results['stats']['completed'] = len(results['segments'])
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
        pbar.close()

async def main():
    print("--- Starting Async Munk Pipeline ---")
    
    # Check if we already have the enriched file
    if os.path.exists(OCR_ENRICHED_FILE):
        print(f"Found existing enriched file: {OCR_ENRICHED_FILE}")
        print("Skipping OCR step and loading data directly.")
        with open(OCR_ENRICHED_FILE, 'r', encoding='utf-8') as f:
            enriched_data = json.load(f)
    else:
        enriched_data = await run_ocr_enrichment()
    
    if enriched_data:
        segments = build_segment_list(enriched_data)
        await run_translation_pipeline(segments)
    else:
        print("Error: Could not obtain enriched data.")
    print("--- All Tasks Complete ---")

if __name__ == "__main__":
    asyncio.run(main())
