#!/usr/bin/env python3# Munk Translation Pipeline - Batch API# Converted from Jupyter Notebookprint('Done.')

from google.genai import types
from google import genai
import requests
import json, os, re, time, datetime
from getpass import getpass
from tqdm import tqdm
print('Imports OK.')

import os
from dotenv import load_dotenv

# This will load the API key from a .env file in the same directory
load_dotenv()
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

if not GOOGLE_API_KEY:
    print('WARNING: GOOGLE_API_KEY not found in .env file')

from google import genai
client = genai.Client(api_key=GOOGLE_API_KEY)
print('Client initialized.')


# ── Model ──────────────────────────────────────────────────────────────
# gemini-2.5-flash  →  fast, high quality, ~$4-8 for all of Part 1
# claude-opus-4-6    →  highest quality,    ~$20-30 for all of Part 1
MODEL = 'gemini-3-flash-preview'

# ── Output file ─────────────────────────────────────────────────────────
OUTPUT_FILE = 'munk_translations.json'

# ── Rate limiting ────────────────────────────────────────────────────────
# Seconds to wait between API calls. Increase to 2.0 if you hit errors.
DELAY = 3.0

# ── Sefaria version string for Munk's French ────────────────────────────
MUNK_VER = 'french|Guide_des_\u00e9gar\u00e9s,_trans._by_Salomon_Munk,_Paris,_1856_[fr]'
TEXT_BASE = 'Guide_for_the_Perplexed,_Part_1'

print(f'Model: {MODEL}')
print(f'Output: {OUTPUT_FILE}')

SYSTEM_PROMPT = '''ROLE AND TASK
You are translating Salomon Munk's French philosophical translation of Maimonides' Guide for the Perplexed into English.

You are translating Munk — not Maimonides. Do not harmonize with other English translations.
Adopt the register of serious Victorian scholarly prose: formal, precise, somewhat elevated, but not artificially archaic.
Preserve Munk's long periodic sentences.

MULTILINGUAL CONTENT
Hebrew/Arabic: preserve exactly. Munk's transliterations: preserve exactly.
Latin: translate inline in square brackets [Lat.: ...].

MUNK'S FOOTNOTES
Preserve Munk's footnotes as standard Markdown footnotes: [^1] in the text, and append the footnote bodies to the end of your translation.

STRICT OUTPUT FORMAT
You will be given a JSON array of segments to translate. You MUST return a JSON array containing the exact same number of items.
For each item, provide:
- `ref`: the exact Sefaria reference provided in the input.
- `english`: your full English translation of the segment, including any inline footnotes and footnote bodies appended at the end.
- `tr_notes`: A list of strings. If a French word is ambiguous or a technical term needs clarification, provide a translator's note here (e.g. "faculty: Munk distinguishes..."). Otherwise leave empty.
'''

GLOSSARY = ''' TERMINOLOGY GLOSSARY
  intellect          -> intellect
  entendement        -> understanding
  forme              -> form
  matière            -> matter
  faculté            -> faculty
'''


import json

LOCAL_JSON_PATH = "French.json"

def flatten_text(t):
    '''Sefaria sometimes returns nested lists; flatten to plain string.'''
    if isinstance(t, list):
        return ' '.join(flatten_text(x) for x in t)
    return t or ''

def build_segment_list():
    '''
    Loads the ENTIRE book structure from local Sefaria JSON export.
    Returns a list of dicts: {ref, chapter, paragraph, french}.
    '''
    print('Loading text from local Sefaria JSON export...')
    with open(LOCAL_JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    segments = []

    # 1. Letter to R Joseph
    letter = data['text'].get('Letter to R Joseph son of Judah', [])
    for i, t in enumerate(letter):
        french = flatten_text(t).strip()
        if french:
            segments.append({
                'ref': f'Guide_for_the_Perplexed,_Letter_to_R_Joseph_son_of_Judah.{i+1}',
                'chapter': 'Letter',
                'paragraph': i + 1,
                'french': french
            })

    # 2. Prefatory Remarks
    prefatory = data['text'].get('Prefatory Remarks', [])
    for i, t in enumerate(prefatory):
        french = flatten_text(t).strip()
        if french:
            segments.append({
                'ref': f'Guide_for_the_Perplexed,_Prefatory_Remarks.{i+1}',
                'chapter': 'Prefatory',
                'paragraph': i + 1,
                'french': french
            })

    # 3. Parts 1, 2, 3
    for part in ['Part 1', 'Part 2', 'Part 3']:
        part_data = data['text'].get(part, {})

        # Introduction for the Part
        for i, t in enumerate(part_data.get('Introduction', [])):
            french = flatten_text(t).strip()
            if french:
                segments.append({
                    'ref': f'Guide_for_the_Perplexed,_{part.replace(" ", "_")},_Introduction.{i+1}',
                    'chapter': f'{part} Intro',
                    'paragraph': i + 1,
                    'french': french
                })

        # Chapters for the Part
        chapters = part_data.get('', [])
        for ch_idx, chapter_paras in enumerate(chapters):
            ch = ch_idx + 1
            for i, t in enumerate(chapter_paras):
                french = flatten_text(t).strip()
                if french:
                    segments.append({
                        'ref': f'Guide_for_the_Perplexed,_{part.replace(" ", "_")}.{ch}.{i+1}',
                        'chapter': f'{part} Ch {ch}',
                        'paragraph': i + 1,
                        'french': french
                    })

    print(f'\nTotal: {len(segments)} segments extracted.')
    return segments
# Run it
ALL_SEGMENTS = build_segment_list()
# Build a quick-lookup dict: ref → french text
FRENCH_BY_REF = {s['ref']: s['french'] for s in ALL_SEGMENTS}
SEG_REFS = [s['ref'] for s in ALL_SEGMENTS]  # ordered list of all refs


def load_results():
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, encoding='utf-8') as f:
            existing = json.load(f)
        done = len(existing.get('segments', {}))
        print(f'Resuming: {done} segments already translated.')
        return existing
    print('No existing file found — starting fresh.')
    return {
        'metadata': {
            'title': 'Guide des égarés — Part 1',
            'munk_edition': 'Paris, 1856',
            'model': MODEL,
            'part': 1,
            'created': datetime.datetime.now().isoformat(),
            'completed': False
        },
        'segments': {},
        'stats': {
            'total_segments': len(ALL_SEGMENTS),
            'completed': 0,
            'total_tokens': 0
        }
    }

def save_results(results):
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

RESULTS = load_results()

from pydantic import BaseModel

class TranslatedSegment(BaseModel):
    ref: str
    english: str
    tr_notes: list[str]

def group_segments(segments):
    chunks = []
    # Batch 0: Letter & Prefatory
    batch_0 = [s for s in segments if s['chapter'] in ['Letter', 'Prefatory']]
    if batch_0: chunks.append(batch_0)
    
    # Batch 1: Part 1 Intro + Chapters 1-4
    batch_1 = [s for s in segments if s['chapter'] in ['Part 1 Intro', 'Part 1 Ch 1', 'Part 1 Ch 2', 'Part 1 Ch 3', 'Part 1 Ch 4']]
    if batch_1: chunks.append(batch_1)
    
    # Get the rest of the segments (Chapters 5 to 76)
    handled = ['Letter', 'Prefatory', 'Part 1 Intro', 'Part 1 Ch 1', 'Part 1 Ch 2', 'Part 1 Ch 3', 'Part 1 Ch 4']
    rest = [s for s in segments if s['chapter'] not in handled]
    
    chapters = []
    for s in rest:
        if s['chapter'] not in chapters:
            chapters.append(s['chapter'])
            
    # Chunk remaining by 1
    for i in range(0, len(chapters), 1):
        chunk_chaps = chapters[i:i+1]
        chunk_segs = [s for s in rest if s['chapter'] in chunk_chaps]
        chunks.append(chunk_segs)
        
    return chunks

CHUNKS = group_segments(ALL_SEGMENTS)
print(f'Total segments: {len(ALL_SEGMENTS)}')
print(f'Grouped into {len(CHUNKS)} batches.')
for i, c in enumerate(CHUNKS[:3]):
    print(f'Batch {i}: {len(c)} segments, chapters: {list(dict.fromkeys(s["chapter"] for s in c))}')

from google.genai import types

def create_batch_request(chunk, chunk_id):
    payload = [{'ref': s['ref'], 'french': s['french']} for s in chunk]
    full_system_instruction = f"{SYSTEM_PROMPT}\n\n{GLOSSARY}"
    user_msg = f"TRANSLATE THE FOLLOWING SEGMENTS:\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
    
    # Building the request dictionary manually to ensure JSONL compatibility
    request = {
        'contents': [{'role': 'user', 'parts': [{'text': user_msg}]}],
        'systemInstruction': {'parts': [{'text': full_system_instruction}]},
        'generationConfig': {
            'temperature': 0.2,
            'responseMimeType': 'application/json',
            'responseSchema': {
                'type': 'ARRAY',
                'items': {
                    'type': 'OBJECT',
                    'properties': {
                        'ref': {'type': 'STRING'},
                        'english': {'type': 'STRING'},
                        'tr_notes': {
                            'type': 'ARRAY',
                            'items': {'type': 'STRING'}
                        }
                    },
                    'required': ['ref', 'english', 'tr_notes']
                }
            }
        }
    }
    return {
        'id': chunk_id,
        'request': request
    }


def run_test():
    print('=== TEST MODE: First 2 Batches ===\n')
    chunks_to_test = CHUNKS[:2]
    
    for i, chunk in enumerate(chunks_to_test):
        chunk_id = f'test_batch_{i}'
        print(f'--- BATCH {i} ---')
        print(f'Chapters: {list(dict.fromkeys(s["chapter"] for s in chunk))}')
        print(f'Segments: {len(chunk)}')
        
        batch_req = create_batch_request(chunk, chunk_id)
        jsonl_str = json.dumps(batch_req, ensure_ascii=False)
        print(f'JSONL Payload size: {len(jsonl_str)} characters\n')
        
        print('Executing synchronously for test...')
        payload = [{'ref': s['ref'], 'french': s['french']} for s in chunk]
        user_msg = f'TRANSLATE THE FOLLOWING SEGMENTS:\n{json.dumps(payload, ensure_ascii=False, indent=2)}'
        full_system_instruction = f"{SYSTEM_PROMPT}\n\n{GLOSSARY}"
        
        response = client.models.generate_content(
            model=MODEL,
            contents=user_msg,
            config=types.GenerateContentConfig(
                system_instruction=full_system_instruction,
                temperature=0.2,
                response_mime_type='application/json',
                response_schema=list[TranslatedSegment]
            )
        )
        
        print('\nParsing response...')
        try:
            parsed_array = json.loads(response.text)
            print(f'Successfully parsed array of {len(parsed_array)} segments.')
            print(f'Sample English: {parsed_array[0]["english"][:100]}...')
            
            # Convert output jsonl/array back to original dictionary structure to verify
            print('\nVerifying structure conversion...')
            simulated_output = {}
            import datetime
            for item in parsed_array:
                ref = item['ref']
                # find original segment
                orig_seg = next(s for s in chunk if s['ref'] == ref)
                simulated_output[ref] = {
                    'ref': ref,
                    'chapter': orig_seg['chapter'],
                    'paragraph': orig_seg['paragraph'],
                    'french': orig_seg['french'],
                    'english': item['english'],
                    'tr_notes': item['tr_notes'],
                    'timestamp': datetime.datetime.now().isoformat()
                }
            print(f'Successfully mapped {len(simulated_output)} items to output structure!')
            print(f'Mapped ref: {list(simulated_output.keys())[0]}')
        except Exception as e:
            print(f'Error parsing JSON: {e}')
            print(response.text)
        print('=' * 50 + '\n')

# run_test()


import json
import os

if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    completed_refs = sorted(data.get('segments', {}).keys())
    if completed_refs:
        print(f"First translated segment in file: {completed_refs[0]}")
        print(f"Total segments translated so far: {len(completed_refs)}")
    else:
        print("The file exists but contains no translated segments yet.")
else:
    print(f"The file '{OUTPUT_FILE}' has not been created yet. Run the pipeline to start translating.")

def submit_batch_job():
    import datetime
    print('Preparing JSONL file for batch job...')
    jsonl_filename = 'requests.jsonl'
    
    with open(jsonl_filename, 'w', encoding='utf-8') as f:
        for i, chunk in enumerate(CHUNKS):
            chunk_id = f'batch_{i}'
            batch_req = create_batch_request(chunk, chunk_id)
            f.write(json.dumps(batch_req, ensure_ascii=False) + '\n')
            
    print(f'Uploading {jsonl_filename} to Gemini Files API...')
    uploaded_file = client.files.upload(file=jsonl_filename, config={'mime_type': 'text/plain'})
    print(f'File uploaded successfully. URI: {uploaded_file.uri}')
    
    print('Creating Batch Job...')
    batch_job = client.batches.create(
        model=MODEL,
        src=uploaded_file.name
    )
    print(f'Batch Job Created! Name: {batch_job.name}')
    print(f'State: {batch_job.state.name}')
    
    BATCH_JOB_FILE = 'batch_job_status.json'
    with open(BATCH_JOB_FILE, 'w') as f:
        json.dump({'job_name': batch_job.name, 'created_at': datetime.datetime.now().isoformat()}, f)
    print(f'Job tracking saved to {BATCH_JOB_FILE}. You can safely close the notebook while it runs.')

# submit_batch_job()


# Ensure the directory exists before running
dir_name = os.path.dirname(OUTPUT_FILE)
if dir_name:
    os.makedirs(dir_name, exist_ok=True)

# run_pipeline()

def check_and_download_batch():
    import datetime
    BATCH_JOB_FILE = 'batch_job_status.json'
    if not os.path.exists(BATCH_JOB_FILE):
        print('No active batch job tracking file found.')
        return
        
    with open(BATCH_JOB_FILE, 'r') as f:
        job_info = json.load(f)
        
    job_name = job_info['job_name']
    print(f'Checking status for job: {job_name}')
    
    job = client.batches.get(name=job_name)
    print(f'Current State: {job.state.name}')
    
    if job.state.name == 'JOB_STATE_SUCCEEDED':
        print('Job succeeded! Retrieving output...')
        output_uri = job.job_result.output_uri if (hasattr(job, 'job_result') and hasattr(job.job_result, 'output_uri')) else None
        print(f'Output URI: {output_uri}')
        
        try:
            if hasattr(job, 'dest') and job.dest:
                remote_file = job.dest
            else:
                remote_file = output_uri
                
            if output_uri and output_uri.startswith('gs://'):
                 print('Output is in GCS. Please use gsutil or google-cloud-storage to download it.')
                 return
            print('Attempting to download using Files API...')
            try:
                content_bytes = client.files.download(file=remote_file)
            except Exception as e:
                print(f"Could not download using Files API with remote_file: {remote_file}. Error: {e}")
                print("Attempting to read directly with requests if it's a URL...")
                import requests
                if str(remote_file).startswith('http'):
                    r = requests.get(str(remote_file))
                    content_bytes = r.content
                else:
                    raise
                    
            with open('batch_output.jsonl', 'wb') as f:
                f.write(content_bytes)
            print('Saved to batch_output.jsonl')
            
            RESULTS = load_results()
            with open('batch_output.jsonl', 'r') as f:
                for line in f:
                    data = json.loads(line)
                    chunk_id = data.get('id') or data.get('key')
                    text = data['response']['candidates'][0]['content']['parts'][0]['text']
                    parsed_array = json.loads(text)
                    for item in parsed_array:
                        ref = item['ref']
                        orig_seg = next((s for s in ALL_SEGMENTS if s['ref'] == ref), None)
                        if orig_seg:
                            RESULTS['segments'][ref] = {
                                'ref': ref,
                                'chapter': orig_seg['chapter'],
                                'paragraph': orig_seg['paragraph'],
                                'french': orig_seg['french'],
                                'english': item['english'],
                                'tr_notes': item['tr_notes'],
                                'timestamp': datetime.datetime.now().isoformat()
                            }
            RESULTS['stats']['completed'] = len(RESULTS['segments'])
            save_results(RESULTS)
            print('Master output file updated successfully!')
            os.remove(BATCH_JOB_FILE)
        except Exception as e:
            print(f'Error downloading/parsing: {e}')
            print(job)
            
# check_and_download_batch()

def cancel_batch_job():
    BATCH_JOB_FILE = 'batch_job_status.json'
    if not os.path.exists(BATCH_JOB_FILE):
        print('No active batch job tracking file found.')
        return
        
    with open(BATCH_JOB_FILE, 'r') as f:
        job_info = json.load(f)
        
    job_name = job_info['job_name']
    print(f'Cancelling job: {job_name}')
    
    try:
        client.batches.cancel(name=job_name)
        print('Cancel request submitted successfully.')
        # We keep the file if they want to check status one last time, 
        # or remove it if they are sure. Let's ask.
        choice = input('Remove local tracking file? (y/n): ').lower()
        if choice == 'y':
            os.remove(BATCH_JOB_FILE)
            print('Tracking file removed.')
    except Exception as e:
        print(f'Error cancelling job: {e}')


import random

def show_stats():
    if not os.path.exists(OUTPUT_FILE):
        print('No output file yet — run the pipeline first.')
        return
    with open(OUTPUT_FILE, encoding='utf-8') as f:
        data = json.load(f)
    stats = data['stats']
    segs = data['segments']
    meta = data['metadata']
    print(f'Progress   : {stats["completed"]}/{stats["total_segments"]} segments')
    pct = 100 * stats['completed'] / max(stats['total_segments'], 1)
    bar = '█' * int(pct // 5) + '░' * (20 - int(pct // 5))
    print(f'           : [{bar}] {pct:.1f}%')
    print(f'Tokens     : {stats["total_tokens"]:,}')
    est = stats['total_tokens'] * 0.075 / 1_000_000
    print(f'Est. cost  : ~${est:.2f} (Flash pricing)')
    print(f'Model      : {meta["model"]}')
    print(f'Completed  : {meta.get("completed", False)}')
    if segs:
        notes_count = sum(len(s.get('tr_notes', [])) for s in segs.values())
        print(f'Tr. notes  : {notes_count} logged')
        print()
        sample_ref = random.choice(list(segs.keys()))
        sample = segs[sample_ref]
        print(f'─── Random sample: {sample_ref} ───')
        print(f'FRENCH  : {sample["french"][:250]}...')
        print(f'ENGLISH : {sample["english"][:250]}...')
        if sample.get('tr_notes'):
            print(f'TR.NOTES: {sample["tr_notes"]}')

# show_stats()

def export_notes():
    if not os.path.exists(OUTPUT_FILE):
        print('No output file yet.')
        return
    with open(OUTPUT_FILE, encoding='utf-8') as f:
        data = json.load(f)
    notes_file = OUTPUT_FILE.replace('.json', '_translator_notes.json')
    notes = {}
    for ref, seg in data['segments'].items():
        if seg.get('tr_notes'):
            notes[ref] = {
                'chapter': seg['chapter'],
                'paragraph': seg['paragraph'],
                'notes': seg['tr_notes'],
                'french_context': seg['french'][:200],
                'english_context': seg['english'][:200]
            }
    with open(notes_file, 'w', encoding='utf-8') as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)
    print(f'Exported {len(notes)} notes to {notes_file}')
    return notes_file

# export_notes()

import os

notes_file = OUTPUT_FILE.replace('.json', '_translator_notes.json')

if os.path.exists(OUTPUT_FILE):
    print(f'Done! Translation saved locally to: {os.path.abspath(OUTPUT_FILE)}')
else:
    print(f'Main output file not found: {OUTPUT_FILE}')

if os.path.exists(notes_file):
    print(f'Translator notes saved locally to: {os.path.abspath(notes_file)}')
else:
    print('No translator notes file yet — run Step 12 first.')




if __name__ == '__main__':
    print('Munk Translation Pipeline - Batch API')
    print('1. Run Test (First 2 Batches)')
    print('2. Submit Full Batch Job')
    print('3. Check Status & Download Results')
    print('4. Show Stats')
    print('5. Export Translator Notes')
    print('6. Cancel Active Batch Job')
    
    choice = input('Select an option (1-6): ').strip()
    
    if choice == '1':
        run_test()
    elif choice == '2':
        submit_batch_job()
    elif choice == '3':
        check_and_download_batch()
    elif choice == '4':
        show_stats()
    elif choice == '5':
        export_notes()
    elif choice == '6':
        cancel_batch_job()
    else:
        print('Invalid option.')
