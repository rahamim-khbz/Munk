
import json
import os
import copy
from munk_pipeline_groq import extract_and_flatten, run_track, inject_translation

def main():
    INPUT_FILE = "French_Arabic_Enriched.json"
    print(f"Loading {INPUT_FILE} for Pilot Run...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    # Target: Part 1, Chapter 2
    # In French_Arabic_Enriched.json, Part 1 Chapters are in text["Part 1"][""]
    # Chapter 2 is index 1
    chapter_data = original_data["text"]["Part 1"][""][1]
    
    # We wrap it in a dummy structure so extract_and_flatten can process it correctly
    dummy_data = {
        "text": {
            "Part 1": {
                "Chapter 2": chapter_data
            }
        }
    }
    
    print("Flattening Chapter 2...")
    flat_main, flat_fns = extract_and_flatten(dummy_data)
    
    print(f"Items to translate: {len(flat_main)} segments, {len(flat_fns)} footnotes.")
    
    # 2. Translate Main
    translated_main = run_track(flat_main, "Pilot Main Text")
    
    # 3. Translate Footnotes
    translated_fns = run_track(flat_fns, "Pilot Footnotes")
    
    # 4. Reconstruction
    print("Reconstructing pilot results...")
    reconstructed_chapter = copy.deepcopy(chapter_data)
    
    # Map paths correctly
    # extract_and_flatten produced paths like root.text.Part 1.Chapter 2.0
    for path, text in translated_main.items():
        original_entry = flat_main.get(path)
        # We need to adapt inject_translation or just do it manually for this flat list
        # Since it's a simple list, we can extract the index
        idx = int(path.split('.')[-1])
        final_text = text
        for i, tag in enumerate(original_entry["tags"]):
            final_text = final_text.replace(f"[[t:{i}]]", tag)
        reconstructed_chapter[idx] = final_text
    
    # Save translated footnotes separately for reference
    final_fns = {}
    for fn_id, trans_text in translated_fns.items():
        original_fn = flat_fns.get(fn_id)
        if isinstance(original_fn, dict) and "tags" in original_fn:
            for i, tag in enumerate(original_fn["tags"]):
                trans_text = trans_text.replace(f"[[t:{i}]]", tag)
        final_fns[fn_id] = trans_text

    pilot_results = {
        "chapter_2_translated": reconstructed_chapter,
        "footnotes_translated": final_fns
    }
    
    with open('pilot_chapter2_groq.json', 'w', encoding='utf-8') as f:
        json.dump(pilot_results, f, ensure_ascii=False, indent=2)
        
    print("\nPILOT COMPLETE. Results saved to pilot_chapter2_groq.json")

if __name__ == "__main__":
    main()
