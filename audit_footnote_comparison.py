import json
import re
import os

def clean_path(path):
    """Converts a raw data path into a human-readable chapter name."""
    # root.Part 1..0 -> Part 1 Ch 1
    parts = path.split('.')
    if len(parts) < 2: return "Unknown"
    
    section = parts[1]
    if "Letter" in section: return "Letter to R Joseph"
    if "Prefatory" in section: return "Prefatory Remarks"
    if "Introduction of Ibn Tibon" in section: return "Intro Ibn Tibon"
    
    if len(parts) >= 4:
        if parts[2] == "Introduction":
            return f"{section} Intro"
        if parts[2] == "": # Chapter index is in parts[3]
            try:
                ch_num = int(parts[3]) + 1
                return f"{section} Ch {ch_num}"
            except:
                return f"{section} Ch {parts[3]}"
    
    return section

def audit_footnotes():
    # 1. Count in Original French.json
    french_path = 'French.json'
    with open(french_path, 'r') as f:
        french_data = json.load(f)
    
    french_counts = {}
    def walk(obj, path):
        if isinstance(obj, str):
            # Find both <i class="footnote"> and MD style [^...] just in case
            count = len(re.findall(r'<i class="footnote">', obj))
            if count > 0:
                ch = clean_path(path)
                french_counts[ch] = french_counts.get(ch, 0) + count
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                walk(v, f"{path}.{i}")
        elif isinstance(obj, dict):
            for k, v in obj.items():
                walk(v, f"{path}.{k}")
    
    walk(french_data['text'], 'root')

    # 2. Count in Translated Checkpoint
    # We need to know which footnote belongs to which chapter.
    # The checkpoint itself doesn't have chapter info, but French_Arabic_Enriched.json
    # was used to generate it. Let's use the logic from generate_footnote_report.py
    
    source_path = 'French_Arabic_Enriched.json'
    ckpt_path = 'checkpoint_footnotes_gemini.json'
    
    from munk_pipeline_groq import extract_and_flatten
    with open(source_path, 'r') as f:
        source_data = json.load(f)
    
    _, flat_footnotes = extract_and_flatten(source_data)
    
    translated_map = {}
    if os.path.exists(ckpt_path):
        with open(ckpt_path, 'r') as f:
            translated_map = json.load(f)
            
    translated_counts = {}
    for k, v in flat_footnotes.items():
        if k in translated_map:
            ch = clean_path(v.get('parent_path', 'root').replace('root.text.', 'root.'))
            translated_counts[ch] = translated_counts.get(ch, 0) + 1

    # 3. Generate Report
    all_chapters = sorted(set(list(french_counts.keys()) + list(translated_counts.keys())))
    
    print(f"{'Chapter':<30} | {'French':<10} | {'Translated':<10} | {'Delta':<10}")
    print("-" * 70)
    
    total_fr = 0
    total_tr = 0
    
    for ch in all_chapters:
        fr = french_counts.get(ch, 0)
        tr = translated_counts.get(ch, 0)
        delta = tr - fr
        total_fr += fr
        total_tr += tr
        
        status = ""
        if delta != 0:
            status = f" ({delta:+})"
            
        print(f"{ch:<30} | {fr:<10} | {tr:<10} | {delta:<10}")

    print("-" * 70)
    print(f"{'TOTAL':<30} | {total_fr:<10} | {total_tr:<10} | {total_tr - total_fr:<10}")

if __name__ == "__main__":
    audit_footnotes()
