
import json
import re
import os

def check_integrity():
    print("=== Munk Final Integrity & Alignment Check ===")
    
    prod_file = "munk_production_v1.json"
    french_file = "French_Arabic_Enriched.json"
    
    if not os.path.exists(prod_file) or not os.path.exists(french_file):
        print(f"  [Error] Missing files for integrity check.")
        return

    # 1. Load Data
    with open(prod_file, "r") as f:
        prod_all = json.load(f)
        prod_text = prod_all["text"]
    with open(french_file, "r") as f:
        french_data_raw = json.load(f)

    # 2. Extract French Source and Footnotes
    from munk_pipeline_groq import extract_and_flatten
    french_main, french_fns = extract_and_flatten(french_data_raw)
    
    # 3. Group Footnotes by Parent Path
    # For English
    en_fn_text_by_parent = {}
    prod_fns = prod_all.get("footnotes", {})
    # Note: production footnotes are merged, so we need to find which segments they belong to.
    # Actually, French footnotes have 'parent_path'. We can use that.
    
    fr_fn_text_by_parent = {}
    for fn_id, fn_data in french_fns.items():
        parent = fn_data['parent_path']
        if parent not in fr_fn_text_by_parent: fr_fn_text_by_parent[parent] = ""
        fr_fn_text_by_parent[parent] += " " + re.sub(r"<[^>]+>", "", fn_data['text'])

    report_lines = []
    report_lines.append("# Final Integrity & Word Count Report\n")
    
    mismatched_fns = []
    word_outliers = []
    
    print("  [Action] Analyzing segments (Inclusive of footnotes)...")
    
    for seg_id, fr_data in french_main.items():
        if seg_id not in prod_text:
            continue
            
        en_raw = prod_text[seg_id]
        fr_raw = fr_data['text']
        
        # A. Footnote Count Check
        # Original: count tags in raw French
        fr_fn_count = len(re.findall(r'\[\[fn:\d+\]\]', fr_raw))
        # English: count [[fn:N]]
        en_fn_count = len(re.findall(r'\[\[fn:\d+\]\]', en_raw))
        
        if fr_fn_count != en_fn_count:
            mismatched_fns.append({"id": seg_id, "fr": fr_fn_count, "en": en_fn_count})
            
        # B. Word Count Check (Inclusive)
        # 1. Body
        fr_body_words = re.sub(r"\[\[.*?\]\]", "", fr_raw).split()
        en_body_words = re.sub(r"\[\[.*?\]\]", "", en_raw).split()
        
        # 2. Add Footnotes (This is an approximation since IDs might shift, 
        # but we can sum all footnote text associated with this segment)
        fr_fn_total_words = fr_fn_text_by_parent.get(seg_id, "").split()
        
        # For English, we need to find which footnotes were invoked in this segment [[fn:N]]
        # and look them up in prod_fns
        en_fn_invoked = re.findall(r'\[\[fn:(\d+)\]\]', en_raw)
        en_fn_total_words = []
        for fn_num in en_fn_invoked:
            fn_id = f"fn.{fn_num}"
            if fn_id in prod_fns:
                en_fn_total_words += re.sub(r"<[^>]+>", "", prod_fns[fn_id]).split()

        total_fr = len(fr_body_words) + len(fr_fn_total_words)
        total_en = len(en_body_words) + len(en_fn_total_words)
        
        if total_fr > 0:
            ratio = total_en / total_fr
            if ratio < 0.7 or ratio > 1.6: 
                word_outliers.append({
                    "id": seg_id,
                    "ratio": round(ratio, 2),
                    "fr_words": total_fr,
                    "en_words": total_en
                })

    # 3. Write Report
    report_lines.append(f"## Summary\n")
    report_lines.append(f"- **Total Segments Checked:** {len(french_flat)}\n")
    report_lines.append(f"- **Footnote Mismatches:** {len(mismatched_fns)}\n")
    report_lines.append(f"- **Word Count Outliers:** {len(word_outliers)}\n\n")
    
    if mismatched_fns:
        report_lines.append("## ❌ Footnote Mismatches\n")
        report_lines.append("| Segment ID | French FNs | English FNs |\n| --- | --- | --- |\n")
        for m in mismatched_fns:
            report_lines.append(f"| {m['id']} | {m['fr']} | {m['en']} |\n")
        report_lines.append("\n")

    if word_outliers:
        report_lines.append("## ⚠️ Word Count Outliers (Extreme Ratios)\n")
        report_lines.append("| Segment ID | Ratio | FR Words | EN Words |\n| --- | --- | --- | --- |\n")
        for o in word_outliers:
            report_lines.append(f"| {o['id']} | {o['ratio']} | {o['fr_words']} | {o['en_words']} |\n")

    with open("final_integrity_report.md", "w") as f:
        f.writelines([l + "\n" for l in report_lines])
        
    print(f"  [Success] Integrity report generated: final_integrity_report.md")

if __name__ == "__main__":
    check_integrity()
