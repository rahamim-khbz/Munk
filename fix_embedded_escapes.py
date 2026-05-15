
import json
import re

def decode_embedded_escapes(text):
    """Replace literal \\uXXXX sequences embedded in string values."""
    return re.sub(
        r'\\u([0-9a-fA-F]{4})',
        lambda m: chr(int(m.group(1), 16)),
        text
    )

def walk_and_fix(obj):
    """Recursively walk JSON structure and fix all string values."""
    if isinstance(obj, dict):
        return {k: walk_and_fix(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [walk_and_fix(item) for item in obj]
    elif isinstance(obj, str):
        return decode_embedded_escapes(obj)
    return obj

FILES = [
    "checkpoint_main_text_groq.json",
    "checkpoint_footnotes_gemini.json",
    "checkpoint_footnotes_rehab_groq.json",
]

for fname in FILES:
    try:
        with open(fname, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Count before
        raw_before = json.dumps(data)
        before = len(re.findall(r'\\u[0-9a-fA-F]{4}', raw_before))

        fixed = walk_and_fix(data)

        raw_after = json.dumps(fixed)
        after = len(re.findall(r'\\u[0-9a-fA-F]{4}', raw_after))

        with open(fname, "w", encoding="utf-8") as f:
            json.dump(fixed, f, indent=2, ensure_ascii=False)

        print(f"{fname}: {before} → {after} escape sequences")
    except FileNotFoundError:
        print(f"Skipping {fname} (not found)")
