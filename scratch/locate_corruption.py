import json

def find_corruption(data, target, path="root"):
    found = []
    if isinstance(data, dict):
        for k, v in data.items():
            found.extend(find_corruption(v, target, f"{path}.{k}"))
    elif isinstance(obj := data, list):
        for i, item in enumerate(obj):
            found.extend(find_corruption(item, target, f"{path}[{i}]"))
    elif isinstance(data, str):
        if target in data:
            found.append(path)
    return found

with open('French_Arabic_Enriched.json', 'r') as f:
    data = json.load(f)

target = "Pascal's Provincial Letters"
results = find_corruption(data, target)
print(f"Found corruption in: {results}")

if results:
    # Print a snippet of the first one
    path = results[0]
    # Simple way to get the nested value
    val = data
    for part in path.split('.')[1:]:
        if '[' in part:
            key = part.split('[')[0]
            idx = int(part.split('[')[1][:-1])
            val = val[key][idx]
        else:
            val = val[part]
    print(f"Content length: {len(val)}")
    print(f"Snippet: {val[:200]}...")
