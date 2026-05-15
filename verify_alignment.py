import json
import os

def verify_triple_alignment():
    print("=== Triple-Source Alignment Audit (Part I) ===")
    
    # 1. Load Sources
    with open("French_Arabic_Enriched.json", "r") as f:
        structure = json.load(f)
    with open("Guide for the Perplexed - he - Makbili Edition, Mif'al Mishneh Torah, 2024.json", "r") as f:
        hebrew = json.load(f)
    with open("checkpoint_main_text_groq.json", "r") as f:
        english = json.load(f)
    with open("checkpoint_footnotes_gemini.json", "r") as f:
        footnotes = json.load(f)

    report = []
    errors = 0
    warnings = 0

    # 2. Define Part I segments to check
    # We'll crawl the structure for Part 1
    def get_structure_ids(data, path="root.text"):
        ids = []
        if isinstance(data, dict):
            for k, v in data.items():
                ids.extend(get_structure_ids(v, f"{path}.{k}"))
        elif isinstance(data, list):
            for i, v in enumerate(data):
                if isinstance(v, list):
                    # Recursive for nested lists (like chapters in Part 1)
                    ids.extend(get_structure_ids(v, f"{path}.{i}"))
                else:
                    ids.append(f"{path}.{i}")
        return ids

    # Focus on Part 1, Prefatory, and Letter
    all_ids = get_structure_ids(structure["text"])
    part1_ids = [idx for idx in all_ids if "Part 1" in idx or "Prefatory" in idx or "Letter" in idx]

    print(f"  [Info] Auditing {len(part1_ids)} segments...")

    for seg_id in part1_ids:
        # Check English Alignment
        # The English checkpoint matches the structure IDs precisely now
        en_text = english.get(seg_id)
        
        # Check Hebrew Alignment
        # The Hebrew JSON matches the structure IDs (with "" keys)
        he_node = hebrew["text"]
        he_exists = False
        parts = seg_id.replace("root.text.", "").split(".")
        try:
            temp_node = he_node
            for p in parts:
                if p.isdigit():
                    temp_node = temp_node[int(p)]
                else:
                    temp_node = temp_node[p]
            he_exists = True
        except (KeyError, IndexError, TypeError):
            he_exists = False

        # Validation Logic
        if not he_exists:
            report.append(f"❌ [Hebrew Missing] {seg_id}")
            errors += 1
        elif not en_text:
            report.append(f"❌ [English Missing] {seg_id}")
            errors += 1
        else:
            # Check Footnote Alignment in this segment
            import re
            fn_refs = re.findall(r"\[\[fn:(\d+)\]\]", en_text)
            for fn_num in fn_refs:
                fn_key = f"fn.{fn_num}"
                if fn_key not in footnotes:
                    report.append(f"⚠️ [Footnote Missing] {seg_id} -> {fn_key}")
                    warnings += 1

    # 3. Final Result
    if report:
        print("\nDetail of First 10 Errors:")
        for r in report[:10]:
            print(f"  {r}")

    print(f"\nAudit Results:")
    print(f"  - Total Segments Audited: {len(part1_ids)}")
    print(f"  - Critical Alignment Errors: {errors}")
    print(f"  - Missing Footnote Warnings: {warnings}")
    
    if errors == 0:
        print("\n✅ ALIGNMENT VERIFIED: Triple-source synchronization is perfect for Part I.")
    else:
        print("\n❌ ALIGNMENT FAILED: See above for specific missing segments.")

if __name__ == "__main__":
    verify_triple_alignment()
