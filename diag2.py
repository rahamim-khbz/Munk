import json

def flatten_text(t):
    if isinstance(t, list): return ' '.join(flatten_text(x) for x in t)
    return t or ''

with open('French_Arabic_Enriched.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Part 1 Ch 21 Paragraph 4 is at text -> Part 1 -> '' -> index 20 -> index 3
try:
    p4 = data['text']['Part 1'][''][20][3]
    text = flatten_text(p4)
    print("--- Part 1 Ch 21 Segment 4 in ENRICHED ---")
    print(f"Word count via split: {len(text.split())}")
    print(f"Full text:\n{text}")
except Exception as e:
    print(f"Error finding segment: {e}")
