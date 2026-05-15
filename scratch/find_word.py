import json
import re

with open('French_Arabic_Enriched.json', 'r') as f:
    data = json.load(f)

def find_target(obj, target):
    if isinstance(obj, str):
        if target in obj:
            # Find the position
            idx = obj.find(target)
            print(f"FOUND: {obj[max(0, idx-100):min(len(obj), idx+500)]}")
    elif isinstance(obj, dict):
        for v in obj.values():
            find_target(v, target)
    elif isinstance(obj, list):
        for i in obj:
            find_target(i, target)

find_target(data, '\u05e4\u05e7\u05d4')
