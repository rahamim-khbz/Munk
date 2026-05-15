import json
import re

def extract_footnotes(data):
    flat_footnotes = {}
    
    def process_text(text, prefix=""):
        if isinstance(text, str):
            # Extract footnotes
            # Pattern: <i class="footnote">...</i>
            # Note: Footnotes can contain <i> tags inside them, so we need a non-greedy but balanced match or just assume no nested footnotes
            # The current pipeline uses: r'<sup class="footnote-marker">\(\d+\)</sup>\s*<i class="footnote">|<i class="footnote">'
            matches = re.finditer(r'<i class="footnote">(.*?)</i>', text, re.DOTALL)
            for i, match in enumerate(matches):
                fn_id = f"{prefix}.sub_{i+1}"
                flat_footnotes[fn_id] = match.group(1).strip()
        elif isinstance(text, list):
            for i, item in enumerate(text):
                process_text(item, f"{prefix}.{i}")
        elif isinstance(text, dict):
            for k, v in text.items():
                process_text(v, f"{prefix}_{k}")

    process_text(data['text'], "fn")
    return flat_footnotes

with open('French_Light.json', 'r') as f:
    data = json.load(f)

flat_fns = extract_footnotes(data)
lengths = {k: len(v) for k, v in flat_fns.items()}
sorted_lengths = sorted(lengths.items(), key=lambda x: x[1], reverse=True)

print("Top 10 longest footnotes:")
for k, v in sorted_lengths[:10]:
    print(f"{k}: {v} chars")

# Check fn.2186 specifically
for k in flat_fns:
    if "2186" in k:
        print(f"Found {k}: {len(flat_fns[k])} chars")
