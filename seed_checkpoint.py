
import json
import re
import os
from munk_pipeline_v3 import extract_and_flatten

def clean_for_match(text):
    """Strips all HTML, footnote content, markers, and whitespace for robust matching."""
    if not isinstance(text, str): return ""
    # Strip footnote tags AND their content
    text = re.sub(r'<i class="footnote">.*?</i>', '', text, flags=re.DOTALL)
    # Strip sup tags (markers)
    text = re.sub(r'<sup[^>]*>.*?</sup>', '', text)
    # Strip numeric markers in parentheses like (1) or (2)
    text = re.sub(r'\(\d+\)', '', text)
    # Strip remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Strip v3 markers like [[fn:0]] or [[t:0]]
    text = re.sub(r'\[\[(?:fn|t):\d+\]\]', '', text)
    # Strip whitespace and normalize
    return re.sub(r'\s+', '', text).strip()

def seed_checkpoint():
    PREV_FILE = "/Users/rayhabbaz/Downloads/munk_translations-3.json"
    SOURCE_FILE = "French_Arabic_Enriched.json"
    CHECKPOINT_FILE = "checkpoint_main_text.json"
    
    print(f"Loading previous translations from {PREV_FILE}...")
    with open(PREV_FILE, 'r', encoding='utf-8') as f:
        prev_data = json.load(f)
        
    prev_segments = prev_data.get("segments", {})
    # Create a lookup map of {cleaned_french: english}
    lookup = {}
    for seg_id, seg_data in prev_segments.items():
        fr_clean = clean_for_match(seg_data.get("french", ""))
        en = seg_data.get("english", "")
        if fr_clean and en:
            lookup[fr_clean] = en
            
    print(f"Loaded {len(lookup)} unique prior segments.")
    
    print(f"Loading source and flattening...")
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        source_data = json.load(f)
        
    flat_main, _ = extract_and_flatten(source_data)
    
    checkpoint_map = {}
    match_count = 0
    
    for path, data in flat_main.items():
        fr_text = data["text"] # This is the stripped text from v3 flattener
        fr_clean = clean_for_match(fr_text)
        
        if fr_clean in lookup:
            # We found a match! 
            # Note: The English from prev_data might contain HTML/Markdown.
            # That's fine, the Reconstructor will handle it.
            checkpoint_map[path] = lookup[fr_clean]
            match_count += 1
            
    print(f"Successfully matched and seeded {match_count} segments into checkpoint.")
    
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(checkpoint_map, f, ensure_ascii=False, indent=2)
        
    print(f"DONE. {CHECKPOINT_FILE} is ready.")

if __name__ == "__main__":
    seed_checkpoint()
