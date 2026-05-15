import json
import re
from munk_pipeline_groq import extract_and_flatten

with open('French_Arabic_Enriched.json', 'r') as f:
    data = json.load(f)

_, flat_footnotes = extract_and_flatten(data)
key = "fn.2186.sub_1"
if key in flat_footnotes:
    text = flat_footnotes[key]['text']
    print(f"Key: {key}")
    print(f"Length: {len(text)}")
    print(f"Sample: {text[:200]}...")
else:
    print(f"Key {key} not found")
