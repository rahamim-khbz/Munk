import json
import re

with open('French_Healed_Enriched.json', 'r') as f:
    data = json.load(f)

def extract_footnotes(obj):
    res = []
    if isinstance(obj, dict):
        for v in obj.values():
            res.extend(extract_footnotes(v))
    elif isinstance(obj, list):
        for i in obj:
            res.extend(extract_footnotes(i))
    elif isinstance(obj, str):
        matches = re.findall(r'<i class="footnote">(.*?)</i>', obj, re.DOTALL)
        res.extend(matches)
    return res

fns = extract_footnotes(data['text'])
print(f"Total footnotes: {len(fns)}")
if len(fns) >= 2186:
    print(f"fn.2186 content:\n{fns[2185]}")
else:
    print("fn.2186 not found")
