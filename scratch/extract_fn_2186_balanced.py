import json
import re

def find_balanced_tag(text, start_index):
    match = re.search(r'<i class="footnote">', text[start_index:])
    if not match:
        return None, None
    content_start = start_index + match.end()
    stack = 1
    curr = content_start
    while stack > 0 and curr < len(text):
        if text.startswith('<i>', curr) or text.startswith('<i ', curr):
            stack += 1
            curr += 3
        elif text.startswith('</i>', curr):
            stack -= 1
            if stack == 0:
                return text[content_start:curr], curr + 4
            curr += 4
        else:
            curr += 1
    return None, None

with open('French_Healed_Enriched.json', 'r') as f:
    data = json.load(f)

def extract_all(obj):
    res = []
    if isinstance(obj, dict):
        for v in obj.values():
            res.extend(extract_all(v))
    elif isinstance(obj, list):
        for i in obj:
            res.extend(extract_all(i))
    elif isinstance(obj, str):
        curr = 0
        while True:
            content, next_idx = find_balanced_tag(obj, curr)
            if content is None:
                break
            res.append(content)
            curr = next_idx
    return res

fns = extract_all(data['text'])
print(f"Total footnotes: {len(fns)}")
if len(fns) >= 2186:
    print(f"fn.2186 content (Balanced):\n{fns[2185]}")
