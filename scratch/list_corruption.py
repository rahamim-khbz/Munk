import json
import re

def find_corruption(obj, path="root"):
    corrupted = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            corrupted.extend(find_corruption(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            corrupted.extend(find_corruption(item, f"{path}[{i}]"))
    elif isinstance(obj, str):
        # Look for typical LLM/Code markers
        markers = ["Pascal's Provincial", "To(String name", "Confirm or deny", "Grammatical breakdown"]
        if any(m in obj for m in markers):
            corrupted.append(path)
    return corrupted

with open('French_Arabic_Enriched.json', 'r') as f:
    data = json.load(f)

corrupted_paths = find_corruption(data)
print(f"Total corrupted segments: {len(corrupted_paths)}")
for p in corrupted_paths:
    print(f"  - {p}")
