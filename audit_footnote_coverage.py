import json
import os
import re
from munk_pipeline_groq import extract_and_flatten

def audit_footnote_coverage():
    print("=== Footnote Coverage Audit ===")
    
    source_path = 'French_Healed_Enriched.json'
    if not os.path.exists(source_path): source_path = 'French_Arabic_Enriched.json'
    
    ckpt_path = 'checkpoint_footnotes_gemini.json'
    
    if not os.path.exists(source_path):
        print(f"[Error] Source file {source_path} not found.")
        return

    # 1. Load Source and Extract
    print(f"Loading {source_path}...")
    with open(source_path, 'r') as f:
        data = json.load(f)
    
    print("Running extraction logic...")
    flat_main, flat_footnotes = extract_and_flatten(data)
    
    # 2. Basic Count Check
    total_extracted_keys = len(flat_footnotes)
    
    # Count occurrences of [[fn:N]] in the main text to ensure they were all extracted
    all_markers = []
    for val in flat_main.values():
        text = val.get('text', '')
        all_markers.extend(re.findall(r'\[\[fn:(\d+)\]\]', text))
    
    unique_markers = set(all_markers)
    max_marker = max([int(m) for m in unique_markers]) if unique_markers else -1
    
    print(f"\n[Extraction Stats]")
    print(f"  Total distinct footnote markers in text: {len(unique_markers)}")
    print(f"  Max marker index found: {max_marker}")
    print(f"  Total flattened footnote chunks: {total_extracted_keys}")
    
    # 3. Check for Residual Footnote Tags in Main Text
    # If extraction missed something, we might still see <i class="footnote"> in flat_main
    print("\n[Scanning for Unextracted Footnotes]")
    unextracted_found = False
    for ref, val in flat_main.items():
        text = val.get('text', '')
        if '<i class="footnote">' in text:
            print(f"  ⚠️ ALERT: Unextracted footnote tag found in: {ref}")
            snippet = text[text.find('<i class="footnote">'):text.find('<i class="footnote">')+100]
            print(f"    Snippet: {snippet}...")
            unextracted_found = True
    
    if not unextracted_found:
        print("  ✅ No unextracted <i class=\"footnote\"> tags found in main text.")

    # 4. Check Checkpoint Coverage
    if os.path.exists(ckpt_path):
        with open(ckpt_path, 'r') as f:
            translated_map = json.load(f)
        
        translated_count = len(translated_map)
        missing_keys = [k for k in flat_footnotes.keys() if k not in translated_map]
        
        print(f"\n[Translation Status]")
        print(f"  Total translated in checkpoint: {translated_count}")
        print(f"  Remaining to translate: {len(missing_keys)}")
        
        if missing_keys:
            print(f"  First 5 missing: {missing_keys[:5]}")
            # Group missing by part/chapter for easier troubleshooting
            missing_by_ch = {}
            for k in missing_keys:
                ch = flat_footnotes[k].get('parent_path', 'unknown')
                missing_by_ch[ch] = missing_by_ch.get(ch, 0) + 1
            
            print(f"  Missing grouped by location (top 5):")
            for ch, count in sorted(missing_by_ch.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"    - {ch}: {count}")
    else:
        print("\n[Checkpoint Status]")
        print(f"  ⚠️ Warning: Checkpoint {ckpt_path} not found.")

    # 5. Check for Structural Mismatches in Sub-footnotes
    print("\n[Sub-footnote Integrity Check]")
    # Ensure if we have fn.N.sub_0, we also have sub_1, etc.
    sub_groups = {}
    for k in flat_footnotes.keys():
        if ".sub_" in k:
            base_id = k.split(".sub_")[0]
            idx = int(k.split(".sub_")[1])
            if base_id not in sub_groups: sub_groups[base_id] = []
            sub_groups[base_id].append(idx)
    
    missing_sub_parts = []
    for base_id, indices in sub_groups.items():
        indices.sort()
        expected = list(range(len(indices)))
        if indices != expected:
            missing_sub_parts.append((base_id, indices))
    
    if missing_sub_parts:
        for b, i in missing_sub_parts:
            print(f"  ⚠️ ALERT: Gaps found in sub-footnotes for {b}: {i}")
    else:
        print("  ✅ All multi-part footnotes have continuous segments.")

if __name__ == "__main__":
    audit_footnote_coverage()
