import json
import re

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
        # Using a simple find for the target string
        target = 'Sur le mot <span dir="rtl">פקה'
        if target in obj:
            # Found the segment
            print(f"FOUND SEGMENT: {obj[:100]}...")
            # Now find the footnote index in the full list
            # We need to extract all fns in order
            pass
    return res

# Better way:
def get_all_fns(obj):
    res = []
    if isinstance(obj, dict):
        for v in obj.values():
            res.extend(get_all_fns(v))
    elif isinstance(obj, list):
        for i in obj:
            res.extend(get_all_fns(i))
    elif isinstance(obj, str):
        # find_balanced_tag simulation
        curr = 0
        while True:
            match = re.search(r'<i class="footnote">', obj[curr:])
            if not match: break
            # Balanced search...
            stack = 1
            start = curr + match.end()
            p = start
            while stack > 0 and p < len(obj):
                if obj.startswith('<i>', p) or obj.startswith('<i ', p): stack += 1; p += 3
                elif obj.startswith('</i>', p): stack -= 1; p += 4
                else: p += 1
            res.append(obj[start:p-4])
            curr = p
    return res

all_fns = get_all_fns(data['text'])
target = 'Sur le mot <span dir="rtl">פקה'
for i, fn in enumerate(all_fns):
    if target in fn:
        print(f"Footnote Index: {i} (ID: fn.{i+1})")
        print(f"Content: {fn[:200]}...")
