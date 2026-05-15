
import json
import os
from munk_pipeline_v3 import extract_and_flatten, chunk_dictionary

with open("French_Arabic_Enriched.json", "r", encoding="utf-8") as f:
    data = json.load(f)

flat_main, _ = extract_and_flatten(data)

# Load checkpoint to see what's already done
checkpoint_file = "checkpoint_main_text.json"
translated_map = {}
if os.path.exists(checkpoint_file):
    with open(checkpoint_file, "r", encoding="utf-8") as f:
        translated_map = json.load(f)

# Get the "todo" keys in order
todo_keys = [k for k in flat_main.keys() if k not in translated_map]
todo_items = {k: flat_main[k] for k in todo_keys}

chunks = chunk_dictionary(todo_items)
first_batch = chunks[0]

print(f"--- FIRST BATCH (BATCH 1) ---")
for path, text in first_batch.items():
    print(f"Path: {path}")
    print(f"Text Preview: {text[:100]}...")
    print(f"Length: {len(text)} chars")
    print("-" * 20)
