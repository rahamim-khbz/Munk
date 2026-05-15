
import json
import os
import re

def identify_latin_only(text):
    """Detects if a segment is purely or mostly Latin/markers."""
    if not text: return False
    # Remove markers and Latin brackets
    clean = re.sub(r'\[Lat\.:.*?\]', '', text)
    clean = re.sub(r'\[\[fn:\d+\]\]', '', clean)
    clean = re.sub(r'\[\[t:\d+\]\]', '', clean)
    clean = re.sub(r'\(.*?\)', '', clean) # Remove citations in parens
    clean = clean.strip()
    
    # If after removing everything, there's very little English left, it's a "Latin Heavy" segment
    return len(clean) < 5 and "[Lat.:" in text

def audit_latin_detailed():
    print("=== Detailed Latin Usage & Gap Audit ===")
    
    with open("French_Arabic_Enriched.json", "r") as f:
        french_data = json.load(f)
    with open("Guide for the Perplexed - he - Makbili Edition, Mif'al Mishneh Torah, 2024.json", "r") as f:
        hebrew_data = json.load(f)
    with open("checkpoint_main_text_groq.json", "r") as f:
        english_main = json.load(f)
    with open("checkpoint_footnotes_gemini.json", "r") as f:
        english_fns = json.load(f)

    from munk_pipeline_groq import extract_and_flatten
    flat_french_main, flat_french_fns = extract_and_flatten(french_data)

    latin_only = []
    latin_mixed = []
    
    # Combine all English
    all_en = {**english_main, **english_fns}
    
    for seg_id, en_text in all_en.items():
        if "[Lat.:" in en_text:
            # Get Context
            fr_text = ""
            he_text = "N/A"
            if "fn." in seg_id:
                fr_text = flat_french_fns.get(seg_id, {}).get('text', '')
            else:
                fr_text = flat_french_main.get(seg_id, {}).get('text', '')
                parts = seg_id.replace("root.text.", "").split(".")
                try:
                    temp = hebrew_data["text"]
                    for p in parts:
                        if p.isdigit(): temp = temp[int(p)]
                        else: temp = temp[p]
                    he_text = temp
                except: pass

            entry = {
                "id": seg_id,
                "english": en_text,
                "french": fr_text,
                "hebrew": he_text
            }
            
            if identify_latin_only(en_text):
                latin_only.append(entry)
            else:
                latin_mixed.append(entry)

    # Output CSV-like Markdown for the user
    output_path = "latin_gaps_report.md"
    with open(output_path, "w") as f:
        f.write("# Latin Gaps & Usage Report\n\n")
        f.write(f"**Total Segments with Latin:** {len(latin_only) + len(latin_mixed)}\n")
        f.write(f"**Critical Gaps (Latin-only, No English):** {len(latin_only)}\n\n")
        
        f.write("## 🚨 Critical Gaps (Latin-only)\n")
        f.write("These segments have NO English translation, only a Latin verse or term. These need re-translation.\n\n")
        for res in latin_only:
            f.write(f"### {res['id']}\n")
            f.write(f"| Source | Text |\n| --- | --- |\n")
            f.write(f"| **English (Error)** | {res['english']} |\n")
            f.write(f"| **French (Source)** | {res['french']} |\n")
            f.write(f"| **Hebrew** | {res['hebrew']} |\n\n")
            
        f.write("## 📝 Mixed Usage (Latin Terminology/Citations)\n")
        f.write("These are likely correct scholarly references preserved in the translation.\n\n")
        for res in latin_mixed[:50]: # Limit for brevity in report
            f.write(f"- **{res['id']}**: {res['english'][:100]}...\n")

    print(f"  [Success] Found {len(latin_only)} critical Latin-only gaps. See {output_path}")

if __name__ == "__main__":
    audit_latin_detailed()
