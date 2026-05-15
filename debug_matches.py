
import json
import re
from seed_checkpoint import clean_for_match
from munk_pipeline_v3 import extract_and_flatten

PREV_FILE = "/Users/rayhabbaz/Downloads/munk_translations-3.json"
SOURCE_FILE = "French_Arabic_Enriched.json"

with open(PREV_FILE, 'r', encoding='utf-8') as f:
    prev_data = json.load(f)
with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
    source_data = json.load(f)

flat_main, _ = extract_and_flatten(source_data)
source_cleaned = {clean_for_match(d["text"]): path for path, d in flat_main.items()}

print("--- UNMATCHED SEGMENTS FROM PREVIOUS FILE ---")
count = 0
for seg_id, seg_data in prev_data.get("segments", {}).items():
    fr = seg_data.get("french", "")
    fr_clean = clean_for_match(fr)
    if fr_clean not in source_cleaned:
        print(f"ID: {seg_id}")
        print(f"Cleaned French (first 100): {fr_clean[:100]}")
        # Try to find a partial match
        for s_fr in source_cleaned:
            if fr_clean[:50] in s_fr:
                print(f"  POTENTIAL MATCH IN SOURCE: {s_fr[:100]}")
        print("-" * 20)
        count += 1
        if count > 5: break
