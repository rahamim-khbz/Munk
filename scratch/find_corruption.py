import json

def find_fn(data, target_id):
    if isinstance(data, dict):
        for k, v in data.items():
            if target_id in str(v):
                print(f"Found in key: {k}")
                find_fn(v, target_id)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if target_id in str(item):
                print(f"Found in index: {i}")
                find_fn(item, target_id)

with open('French_Arabic_Enriched.json', 'r') as f:
    data = json.load(f)
    # Search for the Pascal string
    target = "Pascal's Provincial Letters"
    find_fn(data, target)
