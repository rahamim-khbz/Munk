import json
import re

def strip_images(text):
    if isinstance(text, str):
        # Remove <img src="data:image/jpg;base64,..."> tags
        return re.sub(r'<img src="data:image/[^"]+"[^>]*>', '', text)
    elif isinstance(text, list):
        return [strip_images(item) for item in text]
    elif isinstance(text, dict):
        return {k: strip_images(v) for k, v in text.items()}
    return text

print("Loading French.json...")
with open('French.json', 'r') as f:
    data = json.load(f)

print("Stripping images...")
data['text'] = strip_images(data['text'])

print("Saving French_Light.json...")
with open('French_Light.json', 'w') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("Done.")
