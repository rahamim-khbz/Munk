
import json
import random
import re
import os

def audit_coherence():
    print("=== Munk Translation Coherence Audit (Sampling) ===")
    
    prod_file = "munk_production_v1.json"
    french_file = "French_Arabic_Enriched.json" # Using the enriched one as it matches the structure
    
    if not os.path.exists(prod_file) or not os.path.exists(french_file):
        print(f"  [Error] Missing files for audit: {prod_file} or {french_file}")
        return

    # 1. Load Data
    with open(prod_file, "r") as f:
        prod_data = json.load(f)["text"]
    with open(french_file, "r") as f:
        french_data_raw = json.load(f)

    # 2. Flatten French Source (we need a way to match IDs)
    # Re-using the flattener logic
    def get_structure_ids(data, path="root.text"):
        items = {}
        if isinstance(data, dict):
            for k, v in data.items():
                items.update(get_structure_ids(v, f"{path}.{k}"))
        elif isinstance(data, list):
            for i, v in enumerate(data):
                if isinstance(v, list):
                    items.update(get_structure_ids(v, f"{path}.{i}"))
                else:
                    items[f"{path}.{i}"] = v
        return items

    french_flat = get_structure_ids(french_data_raw["text"])
    
    # 3. Sample 10 Main Text Segments
    common_ids = list(set(prod_data.keys()) & set(french_flat.keys()))
    main_sample_ids = random.sample(common_ids, min(10, len(common_ids)))
    
    # 4. Sample 10 Footnotes
    with open(prod_file, "r") as f:
        prod_all = json.load(f)
        prod_fns = prod_all.get("footnotes", {})
    
    # Extract French Footnotes for comparison
    def get_all_french_fns(data):
        fns = {}
        pattern = r'<sup class="footnote-marker">\(\d+\)</sup><i class="footnote">(.*?)</i>|<i class="footnote">(.*?)</i>'
        
        def extract_from_text(text, ref_base):
            matches = re.findall(pattern, text, flags=re.DOTALL)
            for i, match in enumerate(matches):
                fn_text = match[0] or match[1]
                fn_id = f"fn.{ref_base}_fn{i+1}" # This logic might differ from checkpoint, need to be careful
                # Wait, the checkpoint IDs are often just "fn.N"
                # Let's check a few IDs from prod_fns
                pass

        # Actually, let's use a simpler way to find the French footnote
        # The pipeline likely uses a specific mapping.
        # Since I am the LLM, I can search for the French text in French_Arabic_Enriched.json 
        # that matches the 'scholarly essence' of the English one if IDs don't match.
        return fns

    # Re-evaluating ID mapping: 
    # The checkpoint uses "fn.N" where N is a sequential number.
    # The original French.json has them embedded.
    
    fn_sample_ids = random.sample(list(prod_fns.keys()), min(10, len(prod_fns)))
        
    print(f"  [Action] Sampling 10 segments and 10 footnotes for audit...")

    report_lines = []
    report_lines.append("# Scholarly Coherence Audit: French Original vs. English Translation\n")
    report_lines.append("This report presents a qualitative alignment check of the Munk Translation.\n")

    # Audit Main Text
    report_lines.append("## PART 1: MAIN TEXT SEGMENTS (10 SAMPLES)\n")
    for i, seg_id in enumerate(main_sample_ids, 1):
        fr_text = french_flat[seg_id]
        en_text = prod_data[seg_id]
        
        fr_clean = re.sub(r"<[^>]+>", "", fr_text)
        en_clean = re.sub(r"\[\[.*?\]\]", "", en_text)
        en_clean = re.sub(r"<[^>]+>", "", en_clean)
        
        fr_words = fr_clean.split()
        en_words = en_clean.split()
        
        use_start = random.choice([True, False])
        if use_start:
            fr_snippet = " ".join(fr_words[:10])
            en_snippet = " ".join(en_words[:10])
            type_label = "STARTING 10 WORDS"
        else:
            fr_snippet = " ".join(fr_words[-10:])
            en_snippet = " ".join(en_words[-10:])
            type_label = "ENDING 10 WORDS"

        report_lines.append(f"### M.{i} Segment: `{seg_id}` ({type_label})")
        report_lines.append(f"**French Source:** {fr_snippet}")
        report_lines.append(f"**English Translation:** {en_snippet}")
        report_lines.append("\n> **AI SCHOLARLY ANALYSIS:** [To be completed in chat]\n")
        report_lines.append("\n---\n")

    # Audit Footnotes
    report_lines.append("\n## PART 2: FOOTNOTES (10 SAMPLES - FULL TEXT)\n")
    
    # For footnotes, I'll provide the Full English and the ID. 
    # I will look up the French in the chat during the audit step.
    for i, fn_id in enumerate(fn_sample_ids, 1):
        en_fn = prod_fns[fn_id]
        report_lines.append(f"### FN.{i} Footnote: `{fn_id}`")
        report_lines.append(f"**English Translation (Full):** {en_fn}")
        report_lines.append("\n> **AI SCHOLARLY ANALYSIS:** [To be completed in chat]\n")
        report_lines.append("\n---\n")

    output_file = "translation_coherence_audit.md"
    with open(output_file, "w") as f:
        f.writelines([line + "\n" for line in report_lines])
        
    print(f"  [Success] Audit report generated at: {output_file}")

if __name__ == "__main__":
    audit_coherence()
