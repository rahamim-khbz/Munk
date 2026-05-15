
import json
import os
import re

def identify_latin(text):
    """Detects likely Latin content in text."""
    if not text: return False
    # Look for the specific [Lat.: ...] marker or common Latin function words
    if "[Lat.:" in text: return True
    
    # Common Latin words that are unlikely to be in English/French/Hebrew in this context
    latin_words = {r'\best\b', r'\bnon\b', r'\bquia\b', r'\bet\b', r'\bcum\b', r'\bquod\b', r'\bsum\b', r'\besse\b'}
    for word in latin_words:
        if re.search(word, text, re.IGNORECASE):
            return True
    return False

def audit_latin():
    print("=== Latin Usage Audit ===")
    
    # 1. Load Sources
    with open("French_Arabic_Enriched.json", "r") as f:
        french_data = json.load(f)
    with open("Guide for the Perplexed - he - Makbili Edition, Mif'al Mishneh Torah, 2024.json", "r") as f:
        hebrew_data = json.load(f)
    with open("checkpoint_main_text_groq.json", "r") as f:
        english_main = json.load(f)
    with open("checkpoint_footnotes_gemini.json", "r") as f:
        english_fns = json.load(f)

    # Flatten French and Footnotes for easy lookup
    from munk_pipeline_groq import extract_and_flatten
    flat_french_main, flat_french_fns = extract_and_flatten(french_data)

    results = []
    
    # Audit Main Text
    main_count = 0
    for seg_id, en_text in english_main.items():
        if identify_latin(en_text):
            main_count += 1
            # Get French
            fr_entry = flat_french_main.get(seg_id, {})
            fr_text = fr_entry.get('text', '[Missing]')
            
            # Get Hebrew
            he_text = "[Not Found]"
            parts = seg_id.replace("root.text.", "").split(".")
            try:
                temp = hebrew_data["text"]
                for p in parts:
                    if p.isdigit(): temp = temp[int(p)]
                    else: temp = temp[p]
                he_text = temp
            except: pass
            
            results.append({
                "id": seg_id,
                "type": "Main Text",
                "english": en_text,
                "french": fr_text,
                "hebrew": he_text
            })

    # Audit Footnotes
    fn_count = 0
    for fn_id, en_text in english_fns.items():
        if identify_latin(en_text):
            fn_count += 1
            fr_entry = flat_french_fns.get(fn_id, {})
            fr_text = fr_entry.get('text', '[Missing]')
            
            results.append({
                "id": fn_id,
                "type": "Footnote",
                "english": en_text,
                "french": fr_text,
                "hebrew": "N/A"
            })

    # 2. Output File
    output_path = "latin_usage_audit.md"
    with open(output_path, "w") as f:
        f.write("# Latin Usage Audit\n\n")
        f.write(f"**Total Main Text Segments with Latin:** {main_count}  \n")
        f.write(f"**Total Footnotes with Latin:** {fn_count}  \n\n")
        
        f.write("## Detailed Audit Log\n\n")
        for res in results:
            f.write(f"### {res['id']} ({res['type']})\n")
            f.write(f"**English:** {res['english']}\n\n")
            f.write(f"**French (Source):** {res['french']}\n\n")
            if res['hebrew'] != "N/A":
                f.write(f"**Hebrew (Makbili):** {res['hebrew']}\n\n")
            f.write("---\n\n")

    print(f"  [Success] Audit complete. Found {len(results)} occurrences. See {output_path}")

if __name__ == "__main__":
    # Use venv for dependencies if needed, but we just need json/re here
    audit_latin()
