
import json
import os
import re
from munk_pipeline_gemini import translate_worker_gemini, MAIN_SYSTEM_PROMPT

def fix_gaps():
    print("=== Fixing Part I Gaps (Targeted Translation) ===")
    
    # 1. Load Sources
    with open("French_Arabic_Enriched.json", "r") as f:
        structure = json.load(f)
    with open("checkpoint_main_text_groq.json", "r") as f:
        english = json.load(f)
    
    # Missing IDs from the audit
    missing_ids = [
        "root.text.Part 1..1.4",
        "root.text.Part 1..45.7",
        "root.text.Part 1..45.10",
        "root.text.Part 1..47.2",
        "root.text.Part 1..51.13",
        "root.text.Part 1..53.5",
        "root.text.Part 1..60.0",
        "root.text.Part 1..63.1",
        "root.text.Part 1..69.3",
        "root.text.Part 1..71.15",
        "root.text.Part 1..73.9",
        "root.text.Part 1..75.5"
    ]
    
    # Flatten source text for these IDs
    # This is a bit complex due to the nested structure
    from munk_pipeline_groq import extract_and_flatten
    flat_main, _ = extract_and_flatten(structure)
    
    chunk_to_translate = {}
    for seg_id in missing_ids:
        if seg_id in flat_main:
            chunk_to_translate[seg_id] = flat_main[seg_id]
        else:
            print(f"  [Warning] {seg_id} not found in flattened source!")

    if not chunk_to_translate:
        print("  [Done] No items to translate.")
        return

    print(f"  [Action] Translating {len(chunk_to_translate)} missing segments...")
    
    # Use Gemini to fix these gaps
    # We use translate_worker_gemini which handles tag re-weaving
    translated = translate_worker_gemini(chunk_to_translate, MAIN_SYSTEM_PROMPT)
    
    if translated:
        english.update(translated)
        with open("checkpoint_main_text_groq.json", "w") as f:
            json.dump(english, f, indent=2)
        print(f"  [Success] Fixed {len(translated)} gaps in Part I.")
    else:
        print("  [Error] Translation worker failed.")

if __name__ == "__main__":
    # We need to make sure requests and google-genai are available
    # Actually, I'll just use a try-except for the imports
    try:
        fix_gaps()
    except Exception as e:
        print(f"Failed to run fix_gaps: {e}")
