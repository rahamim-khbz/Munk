import json
import os
import time
from munk_translation_pipeline_threaded import run_translation_pipeline
from munk_translation_pipeline_async import build_segment_list

# --- TEST CONFIGURATION ---
import munk_translation_pipeline_threaded
BASE_DIR = '/Users/rayhabbaz/Library/CloudStorage/GoogleDrive-rhabbaz@gmail.com/My Drive/Munks Guide'
munk_translation_pipeline_threaded.INPUT_FILE = os.path.join(BASE_DIR, 'French.json')
munk_translation_pipeline_threaded.OUTPUT_FILE = os.path.join(BASE_DIR, 'test_translations_threaded.json')
munk_translation_pipeline_threaded.OCR_ENRICHED_FILE = os.path.join(BASE_DIR, 'French_Arabic_Enriched.json')
munk_translation_pipeline_threaded.MAX_TRANS_WORKERS = 3

def run_threaded_test():
    print("=== STARTING THREADED PIPELINE TEST ===")
    
    if not os.path.exists(munk_translation_pipeline_threaded.OCR_ENRICHED_FILE):
        print(f"Error: {munk_translation_pipeline_threaded.OCR_ENRICHED_FILE} not found.")
        return

    with open(munk_translation_pipeline_threaded.OCR_ENRICHED_FILE, 'r', encoding='utf-8') as f:
        enriched_data = json.load(f)
    
    segments = build_segment_list(enriched_data)
    
    # Filter to first 2 chapters
    test_chapters = ['Letter', 'Prefatory']
    test_segments = [s for s in segments if s['chapter'] in test_chapters]
    
    if not test_segments:
        test_segments = segments[:30]
        print(f"Using first 30 segments. Chapters: {list(set(s['chapter'] for s in test_segments))}")

    print(f"Translating {len(test_segments)} segments using Threads...")
    
    start_time = time.time()
    run_translation_pipeline(test_segments)
    duration = time.time() - start_time
    print(f"\nThreaded Phase took {duration:.2f} seconds.")

    # Verification
    if os.path.exists('test_translations_threaded.json'):
        with open('test_translations_threaded.json', 'r', encoding='utf-8') as f:
            results = json.load(f)
        count = len(results['segments'])
        print(f"Successfully translated {count} segments.")
        if count > 0:
            refs = list(results['segments'].keys())
            print(f"First Ref: {refs[0]}")
            print(f"Last Ref:  {refs[-1]}")
    
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    run_threaded_test()
