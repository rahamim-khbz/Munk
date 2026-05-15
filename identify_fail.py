
import json
import re
from munk_pipeline_v3 import extract_and_flatten, chunk_dictionary

with open("French_Arabic_Enriched.json", "r", encoding="utf-8") as f:
    data = json.load(f)

flat_main, _ = extract_and_flatten(data)
chunks = chunk_dictionary(flat_main, max_chars_per_chunk=12000) # Use the old limit to find the failing batch

# The error happened after Heartbeat 5 (batches 0-4 finished).
# So Batch 5 (the 6th batch) is the one that hit the limit.
failing_batch = chunks[5]

print(f"--- FAILING BATCH CONTENTS (Batch Index 5) ---")
for path, text in failing_batch.items():
    print(f"Path: {path}")
    print(f"Length: {len(text)}")
    print(f"Text Preview: {text[:200]}...")
    print("-" * 20)
