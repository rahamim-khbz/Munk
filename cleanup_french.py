import json
import re

ENRICHED_FILE = 'French_Arabic_Enriched.json'

def clean_text(text):
    if isinstance(text, str):
        # Remove stray </img> and </img > tags
        text = re.sub(r'</img\s*>', '', text)
        # Normalize zero-width spaces or weird quotes if any
        text = text.replace('\u200b', '')
        return text
    elif isinstance(text, list):
        return [clean_text(item) for item in text]
    elif isinstance(text, dict):
        return {k: clean_text(v) for k, v in text.items()}
    return text

def main():
    print(f"Loading {ENRICHED_FILE}...")
    with open(ENRICHED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print("Cleaning stray HTML tags...")
    cleaned_data = clean_text(data)
    
    with open(ENRICHED_FILE, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
        
    print("Cleanup complete.")

if __name__ == '__main__':
    main()
