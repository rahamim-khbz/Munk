
import json
import os

files_to_fix = [
    "checkpoint_footnotes_gemini.json",
    "French_Arabic_Enriched.json",
    "checkpoint_main_text_groq.json"
]

for filename in files_to_fix:
    if os.path.exists(filename):
        print(f"Normalizing {filename}...")
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"  Successfully normalized {filename}")
        except Exception as e:
            print(f"  Error fixing {filename}: {e}")
    else:
        print(f"Skipping {filename} (not found)")
