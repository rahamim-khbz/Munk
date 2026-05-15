import json
import re

with open('French_Healed_Enriched.json', 'r') as f:
    data = json.load(f)

def check_tags(text, path):
    # Very simple check for unclosed span/i tags
    # This is not perfect but will catch the obvious ones
    spans = len(re.findall(r'<span', text))
    span_ends = len(re.findall(r'</span>', text))
    if spans != span_ends:
        print(f"UNCLOSED SPAN at {path}: {spans} open, {span_ends} close")
        print(f"Snippet: {text[max(0, text.find('<span')-20):text.find('<span')+100]}...")
    
    is_tags = len(re.findall(r'<i ', text)) + len(re.findall(r'<i>', text))
    i_ends = len(re.findall(r'</i>', text))
    if is_tags != i_ends:
        # Note: some <i> might be footnote containers themselves
        pass

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
