
import json
import os
import sys

# Add path to import extract_and_flatten
sys.path.append(os.getcwd())
from munk_pipeline_groq import extract_and_flatten

def dump_problematic_fn(target_id="fn.2186"):
    with open("French_Arabic_Enriched.json", "r") as f:
        data = json.load(f)
    
    _, footnotes = extract_and_flatten(data)
    
    found = False
    for k, v in footnotes.items():
        if target_id in k:
            print(f"=== {k} ===")
            print(f"Length: {len(v['text'])} characters")
            print(f"Sample: {v['text'][:500]}...")
            found = True
    
    if not found:
        print(f"ID {target_id} not found in flattened footnotes.")

if __name__ == "__main__":
    dump_problematic_fn()
