
import json
from munk_pipeline_groq import extract_and_flatten

def main():
    print("--- Munk Translation Gap Analysis ---")
    
    # 1. Load Checkpoint
    try:
        with open('checkpoint_main_text_groq.json', 'r', encoding='utf-8') as f:
            translated = json.load(f)
    except FileNotFoundError:
        print("Checkpoint not found.")
        return

    # 2. Load Source
    with open('French_Arabic_Enriched.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    flat_main, _ = extract_and_flatten(data)
    
    # 3. Find missing items
    # Note: We only check items that SHOULD have been processed by now.
    # The user said batch 43 failed, and the run is now on batch 54+.
    
    all_keys = list(flat_main.keys())
    missing = []
    
    # We'll check every key. If it's not in translated but lower keys are, it's a gap.
    found_any = False
    last_found_idx = 0
    for i, key in enumerate(all_keys):
        if key in translated:
            found_any = True
            last_found_idx = i
        else:
            if found_any: # We've started, so if it's missing it might be a gap
                missing.append(key)
                
    # Filter missing to only those BEFORE the last found index
    true_gaps = [m for m in missing if all_keys.index(m) < last_found_idx]
    
    if true_gaps:
        print(f"\n🚩 FOUND {len(true_gaps)} MISSING SEGMENTS:")
        for key in true_gaps:
            print(f"- {key}: {flat_main[key]['text'][:100]}...")
    else:
        print("\n✅ No gaps detected in the processed sequence.")

if __name__ == "__main__":
    main()
