
import json
import os
from munk_pipeline_groq import translate_worker, extract_and_flatten

def main():
    print("--- Patching Chapter 19 Gaps ---")
    
    # 1. Load Source
    with open('French_Arabic_Enriched.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    flat_main, _ = extract_and_flatten(data)
    
    # 2. Identify missing keys
    missing_keys = [
        "root.text.Part 1..19.2",
        "root.text.Part 1..19.3",
        "root.text.Part 1..19.4",
        "root.text.Part 1..19.5"
    ]
    
    to_translate = {k: flat_main[k] for k in missing_keys if k in flat_main}
    
    if not to_translate:
        print("No missing keys found in source. Already patched?")
        return
        
    print(f"Translating {len(to_translate)} missing segments...")
    
    # 3. Translate
    # Note: translate_worker takes a chunk (dict)
    res = translate_worker(to_translate)
    
    if res:
        # 4. Update Checkpoint
        ckpt_file = 'checkpoint_main_text_groq.json'
        with open(ckpt_file, 'r') as f:
            ckpt = json.load(f)
            
        ckpt.update(res)
        
        with open(ckpt_file, 'w') as f:
            json.dump(ckpt, f, indent=2)
            
        print("✅ Chapter 19 successfully patched in checkpoint!")
    else:
        print("❌ Patching failed. Rate limit might still be active.")

if __name__ == "__main__":
    main()
