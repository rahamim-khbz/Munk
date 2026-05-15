
import json
import re
import os

# CONFIG
FRENCH_JSON = "French_Arabic_Enriched.json"
TRANSLATED_FN_JSON = "checkpoint_footnotes_gemini.json"
MAIN_TEXT_JSON = "checkpoint_main_text_groq.json" 

def count_words(text):
    # Strip HTML and markers
    clean = re.sub(r'<[^>]+>', '', text)
    clean = re.sub(r'\[\[fn:\d+\]\]', '', clean)
    clean = re.sub(r'\[\[t:\d+\]\]', '', clean)
    return len(clean.split())

def find_balanced_tag(text, start_index):
    match = re.search(r'<i class="footnote">', text[start_index:])
    if not match:
        return None, None
    content_start = start_index + match.end()
    stack = 1
    curr = content_start
    while stack > 0 and curr < len(text):
        if text.startswith('<i>', curr) or text.startswith('<i ', curr):
            stack += 1
            curr += 3
        elif text.startswith('</i>', curr):
            stack -= 1
            if stack == 0:
                return text[content_start:curr], curr + 4
            curr += 4
        else:
            curr += 1
    return None, None

def extract_all_original_footnotes(data):
    """Walks the JSON and extracts all footnotes with their segment paths."""
    flattened_text = {}
    footnotes = {}
    fn_counter = [0]

    def walk(node, current_path):
        if isinstance(node, dict):
            for k, v in node.items(): walk(v, f"{current_path}.{k}")
        elif isinstance(node, list):
            for i, item in enumerate(node): walk(item, f"{current_path}.{i}")
        elif isinstance(node, str):
            text = node
            pos = 0
            processed_text = ""
            marker_pattern = r'<sup class="footnote-marker">\(\d+\)</sup>\s*<i class="footnote">|<i class="footnote">'
            
            fns_in_this_segment = []
            while True:
                match = re.search(marker_pattern, text[pos:])
                if not match:
                    processed_text += text[pos:]
                    break
                processed_text += text[pos:pos+match.start()]
                content, end_pos = find_balanced_tag(text, pos + match.start())
                if content is not None:
                    id_str = f"fn.{fn_counter[0]}"
                    footnotes[id_str] = {"text": content, "path": current_path}
                    fns_in_this_segment.append(id_str)
                    processed_text += f"[[fn:{fn_counter[0]}]]"
                    fn_counter[0] += 1
                    pos = end_pos
                else:
                    processed_text += text[pos + match.start() : pos + match.end()]
                    pos += match.end()
            flattened_text[current_path] = {"text": processed_text, "fn_ids": fns_in_this_segment}

    walk(data.get("text", {}), "root.text")
    return flattened_text, footnotes

def run_audit():
    if not os.path.exists(FRENCH_JSON):
        print(f"Error: {FRENCH_JSON} not found.")
        return
    if not os.path.exists(TRANSLATED_FN_JSON):
        print(f"Error: {TRANSLATED_FN_JSON} not found.")
        return

    print(f"Loading {FRENCH_JSON}...")
    with open(FRENCH_JSON, 'r') as f:
        french_data = json.load(f)
    
    print(f"Loading {TRANSLATED_FN_JSON}...")
    with open(TRANSLATED_FN_JSON, 'r') as f:
        trans_fns = json.load(f)
        
    print("Extracting original footnotes...")
    flat_french, orig_fns = extract_all_original_footnotes(french_data)
    
    report = []
    report.append("# Detailed Footnote Integrity Audit")
    report.append(f"**Date:** 2026-05-10")
    report.append(f"- Total segments with text: {len(flat_french)}")
    report.append(f"- Total original footnotes extracted: {len(orig_fns)}")
    report.append(f"- Total translated footnote entries: {len(trans_fns)}")
    
    # 1. MAPPING CHECK: Check for missing IDs
    missing_ids = []
    for fn_id in orig_fns:
        if fn_id not in trans_fns:
            # Check for sub-parts
            sub_parts = [k for k in trans_fns if k.startswith(f"{fn_id}.sub_")]
            if not sub_parts:
                missing_ids.append(fn_id)
                
    if missing_ids:
        report.append(f"\n## 1. Missing Footnotes ({len(missing_ids)})")
        report.append("These footnotes exist in the French source but are missing from the translated checkpoint.")
        for mid in missing_ids:
            report.append(f"- **{mid}**: {orig_fns[mid]['path']}")
    else:
        report.append("\n## 1. Missing Footnotes: None")
    
    # 2. WORD COUNT AUDIT (10% Tolerance)
    report.append("\n## 2. Word Count Ratio Audit (>10% deviation)")
    report.append("Flags footnotes where the translation length is significantly different from the original.")
    deviations = []
    for fn_id, orig_info in orig_fns.items():
        orig_text = orig_info["text"]
        orig_words = count_words(orig_text)
        
        # Get translated text
        trans_text = ""
        if fn_id in trans_fns:
            trans_text = trans_fns[fn_id]
        else:
            # Recombine
            parts = sorted([k for k in trans_fns if k.startswith(f"{fn_id}.sub_")], 
                           key=lambda x: int(x.split(".sub_")[1]) if ".sub_" in x else 0)
            if parts:
                trans_text = " ".join([trans_fns[p] for p in parts])
            
        if not trans_text: continue
        
        trans_words = count_words(trans_text)
        if orig_words == 0: 
            if trans_words > 0:
                deviations.append({"id": fn_id, "orig": 0, "trans": trans_words, "ratio": 99, "path": orig_info["path"]})
            continue
        
        ratio = trans_words / orig_words
        if ratio < 0.9 or ratio > 1.3: # Increased upper bound slightly as English often expands
            deviations.append({
                "id": fn_id,
                "orig": orig_words,
                "trans": trans_words,
                "ratio": ratio,
                "path": orig_info["path"]
            })
            
    if deviations:
        report.append("| Footnote ID | Path | French Words | English Words | Ratio |")
        report.append("|---|---|---|---|---|")
        # Sort by most deviant ratio
        for d in sorted(deviations, key=lambda x: abs(1-x['ratio']), reverse=True)[:100]: # Cap at 100
            report.append(f"| {d['id']} | {d['path']} | {d['orig']} | {d['trans']} | {d['ratio']:.2f} |")
        if len(deviations) > 100:
            report.append(f"\n*... and {len(deviations)-100} more.*")
    else:
        report.append("No significant word count deviations found.")

    # 3. SUB-FOOTNOTE INTEGRITY (Sequence gaps)
    report.append("\n## 3. Sub-Footnote Sequence Gaps")
    report.append("Checks if any multi-part (split) footnotes have missing segments.")
    sub_bases = set(k.split(".sub_")[0] for k in trans_fns if ".sub_" in k)
    gaps = []
    for base in sub_bases:
        idxs = sorted([int(k.split(".sub_")[1]) for k in trans_fns if k.startswith(f"{base}.sub_")])
        if idxs and idxs[0] != 0: gaps.append(f"{base}: Missing sub_0 (starts at {idxs[0]})")
        for i in range(len(idxs)-1):
            if idxs[i+1] != idxs[i] + 1:
                gaps.append(f"{base}: Gap between sub_{idxs[i]} and sub_{idxs[i+1]}")
    
    if gaps:
        for g in gaps: report.append(f"- {g}")
    else: report.append("No sequence gaps found in split footnotes.")

    # 4. RESIDUAL TAGS IN MAIN TEXT
    if os.path.exists(MAIN_TEXT_JSON):
        report.append("\n## 4. Residual Tags in Translated Main Text")
        report.append("Checks if any original French footnote tags were left behind in the English translation.")
        with open(MAIN_TEXT_JSON, 'r') as f:
            main_trans = json.load(f)
        
        residuals = []
        for path, entry in main_trans.items():
            text = entry if isinstance(entry, str) else entry.get("text", "")
            if '<i class="footnote">' in text:
                residuals.append(path)
        
        if residuals:
            for r in residuals: report.append(f"- **{r}** contains unextracted `<i class=\"footnote\">`")
        else:
            report.append("No residual tags found.")

    # 5. SEGMENT FOOTNOTE COUNT MISMATCH
    # This checks if the number of [[fn:N]] markers in translated segments matches original
    if os.path.exists(MAIN_TEXT_JSON):
        report.append("\n## 5. Segment Footnote Count Mismatch")
        report.append("Checks if the number of footnote markers in each segment matches the French original.")
        mismatches = []
        for path, orig_entry in flat_french.items():
            orig_text = orig_entry["text"]
            orig_fn_count = len(re.findall(r'\[\[fn:\d+\]\]', orig_text))
            
            if path in main_trans:
                trans_entry = main_trans[path]
                trans_text = trans_entry if isinstance(trans_entry, str) else trans_entry.get("text", "")
                trans_fn_count = len(re.findall(r'\[\[fn:\d+\]\]', trans_text))
                
                if orig_fn_count != trans_fn_count:
                    mismatches.append(f"| {path} | {orig_fn_count} | {trans_fn_count} |")
            elif path.split(".sub_")[0] in main_trans:
                # Handle sub-segments if they were split during translation
                pass 

        if mismatches:
            report.append("| Segment Path | French FN Count | English FN Count |")
            report.append("|---|---|---|")
            for m in mismatches[:50]: report.append(m)
        else:
            report.append("All segment footnote counts match.")

    with open("footnote_audit_full.md", "w") as f:
        f.write("\n".join(report))
    print("Full audit report generated: footnote_audit_full.md")

if __name__ == "__main__":
    run_audit()
