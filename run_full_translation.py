
import json
import os
from munk_pipeline_groq import extract_and_flatten, run_track, inject_translation

def main():
    print("--- Starting FULL Munk Translation Pipeline (Groq/Llama 3.3) ---")
    
    # 1. Load Source
    with open('French_Arabic_Enriched.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 2. Flatten Full Text
    print("Flattening entire corpus...")
    flat_main, flat_fns = extract_and_flatten(data)
    print(f"Total Segments: {len(flat_main)}")
    print(f"Total Footnotes: {len(flat_fns)}")
    
    # 3. Run Main Text Track
    translated_main = run_track(flat_main, "Main Text")
    
    # 4. Run Footnotes Track
    translated_fns = run_track(flat_fns, "Footnotes")
    
    # 5. Final Reconstruction
    print("\nReconstructing final English JSON...")
    english_data = json.loads(json.dumps(data)) # Deep copy structure
    
    # Inject main text
    for path, text in translated_main.items():
        inject_translation(english_data, path, text, flat_main[path])
        
    # Inject footnotes into a separate dedicated object
    english_data["footnotes_translated"] = {}
    for path, text in translated_fns.items():
        # Re-inject tags for footnotes
        final_fn_text = text
        original_fn = flat_fns[path]
        if "tags" in original_fn:
            for i, tag in enumerate(original_fn["tags"]):
                final_fn_text = final_fn_text.replace(f"[[t:{i}]]", tag)
        
        # Handle sub-segments in footnotes
        if ".sub_" in path:
            parent_id = path.rsplit(".sub_", 1)[0]
            if parent_id not in english_data["footnotes_translated"]:
                english_data["footnotes_translated"][parent_id] = final_fn_text
            else:
                english_data["footnotes_translated"][parent_id] += " " + final_fn_text
        else:
            english_data["footnotes_translated"][path] = final_fn_text
        
    # 6. Save Result
    with open('munk_translation_english_full.json', 'w', encoding='utf-8') as f:
        json.dump(english_data, f, indent=2, ensure_ascii=False)
        
    print("\nSUCCESS! Full translation saved to munk_translation_english_full.json")

if __name__ == "__main__":
    main()
