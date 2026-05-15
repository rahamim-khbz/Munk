import json
import re

with open('French_Arabic_Enriched.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def flatten_text(t):
    if isinstance(t, list): return ' '.join(flatten_text(x) for x in t)
    return t or ''

def count_footnotes(data):
    total = 0
    
    def extract_fn(text):
        nonlocal total
        pattern = r'<sup class="footnote-marker">\(\d+\)</sup><i class="footnote">(.*?)</i>|<i class="footnote">(.*?)</i>'
        matches = re.findall(pattern, text, flags=re.DOTALL)
        total += len(matches)

    for part in ['Part 1', 'Part 2', 'Part 3']:
        part_data = data['text'].get(part, {})
        for ch in part_data.get('', []):
            for p in ch:
                extract_fn(flatten_text(p))
    print(f"Total footnotes: {total}")

count_footnotes(data)
