import json
import re

def count_words(text):
    if isinstance(text, str):
        # Remove HTML tags before counting words
        clean_text = re.sub(r'<[^>]+>', ' ', text)
        return len(clean_text.split())
    elif isinstance(text, list):
        return sum(count_words(item) for item in text)
    elif isinstance(text, dict):
        return sum(count_words(v) for v in text.values())
    return 0

files = ['French.json', 'French_Light.json', 'French_Arabic_Enriched.json']
results = {}

for filename in files:
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            results[filename] = count_words(data.get('text', {}))
    except Exception as e:
        results[filename] = f"Error: {e}"

print(json.dumps(results, indent=4))
