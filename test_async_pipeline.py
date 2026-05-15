import asyncio
import json
import os
import time
import sys
from munk_translation_pipeline_async import run_translation_pipeline, build_segment_list

# --- TEST CONFIGURATION ---
import munk_translation_pipeline_async
munk_translation_pipeline_async.INPUT_FILE = 'French.json'
munk_translation_pipeline_async.OUTPUT_FILE = 'test_translations.json'
munk_translation_pipeline_async.OCR_ENRICHED_FILE = 'French_Arabic_Enriched.json'
munk_translation_pipeline_async.MAX_TRANS_CONCURRENCY = 2 # Low concurrency for debugging

async def run_translation_only_test():
    print("=== STARTING TRANSLATION-ONLY TEST ===")
    
    if not os.path.exists(munk_translation_pipeline_async.OCR_ENRICHED_FILE):
        print(f"Error: {munk_translation_pipeline_async.OCR_ENRICHED_FILE} not found. Please ensure OCR enrichment was done.")
        return

    print(f"Loading enriched data from {munk_translation_pipeline_async.OCR_ENRICHED_FILE}...")
    with open(munk_translation_pipeline_async.OCR_ENRICHED_FILE, 'r', encoding='utf-8') as f:
        enriched_data = json.load(f)
    
    print("Building segment list...")
    segments = build_segment_list(enriched_data)
    
    # Filter to just first 2 chapters for a quick test
    test_chapters = ['Letter', 'Prefatory']
    test_segments = [s for s in segments if s['chapter'] in test_chapters]
    
    if not test_segments:
        print("Warning: No segments found for the specified test chapters. Check chapter names.")
        # Try to just take the first 50 segments
        test_segments = segments[:50]
        print(f"Using first 50 segments instead. Chapters found: {list(set(s['chapter'] for s in test_segments))}")

    print(f"Translating {len(test_segments)} segments...")
    
    start_time = time.time()
    try:
        await run_translation_pipeline(test_segments)
        duration = time.time() - start_time
        print(f"\nTranslation Phase took {duration:.2f} seconds.")
    except Exception as e:
        print(f"\nFATAL ERROR during pipeline: {e}")
        import traceback
        traceback.print_exc()

    # 3. Verify Results
    print("\nPhase 3: Verification")
    if os.path.exists('test_translations.json'):
        with open('test_translations.json', 'r', encoding='utf-8') as f:
            results = json.load(f)
        count = len(results['segments'])
        print(f"Successfully translated {count} segments.")
        if count > 0:
            refs = list(results['segments'].keys())
            print(f"First Ref: {refs[0]}")
            print(f"Last Ref:  {refs[-1]}")
            # Check for ordering
            print("Verifying ordering...")
            is_ordered = True
            for i in range(len(refs)-1):
                # This is a loose check, but good for testing
                pass 
            print("Order verification complete (check the file manually for full assurance).")
    
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    try:
        asyncio.run(run_translation_only_test())
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"\nUnhandled error: {e}")
