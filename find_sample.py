
import json
from munk_pipeline_groq import extract_and_flatten

with open("French_Arabic_Enriched.json", "r") as f:
    data = json.load(f)

_, flat_fns = extract_and_flatten(data)

with open("checkpoint_footnotes_gemini.json", "r") as f:
    english_fns = json.load(f)

# Find first few footnotes for Part 3 Chapter 41 (root.text.Part 3..40)
samples = []
for fid, info in flat_fns.items():
    if "Part 3..40" in info['parent_path']:
        samples.append({
            "id": fid,
            "fr": info['text'],
            "en": english_fns.get(fid, "MISSING")
        })
        if len(samples) > 3: break

for s in samples:
    print(f"ID: {s['id']}")
    print(f"FR: {s['fr'][:500]}...")
    print(f"EN: {s['en'][:500]}...")
    print("-" * 40)
