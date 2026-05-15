import json
import re

with open('French_Healed_Enriched.json', 'r') as f:
    data = json.load(f)

def check_tags(text, path):
    spans = len(re.findall(r'<span', text))
    span_ends = len(re.findall(r'</span>', text))
    if spans != span_ends:
        print(f"UNCLOSED SPAN at {path}: {spans} open, {span_ends} close")
    
    # Note: <i> tags can be <i class="footnote"> or just <i>
    i_opens = len(re.findall(r'<i[ >]', text))
    i_closes = len(re.findall(r'</i>', text))
    if i_opens != i_closes:
        # For footnotes, the container itself is an <i>.
        # But if it's inside a string segment, it might be nested.
        print(f"UNCLOSED I at {path}: {i_opens} open, {i_closes} close")

def traverse(obj, path="root"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            traverse(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            traverse(item, f"{path}[{i}]")
    elif isinstance(obj, str):
        check_tags(obj, path)

traverse(data)
