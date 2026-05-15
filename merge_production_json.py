
import json
import os
import re
import datetime

# --- SOURCE FILES ---
FR_SOURCE      = "French_Arabic_Enriched.json"
MAIN_TEXT_FILE = "checkpoint_main_text_groq.json"
FN_REHAB_FILE  = "checkpoint_footnotes_rehab_groq.json"
FN_OLD_FILE    = "checkpoint_footnotes_gemini.json"   # fallback for IDs not yet in rehab
OUTPUT_FILE    = "munk_production_v1.json"


# ── Helpers ──────────────────────────────────────────────────────────────────

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def clean_text(text):
    """
    Light sanitisation only — does NOT strip [[t:N]] or [[fn:N]] tags
    because the viewer depends on them for formatting and navigation.
    """
    if not text:
        return text

    # 1. Normalise footnote-marker HTML to canonical [[fn:N]]
    text = re.sub(r'<sup class="footnote-marker">\[fn:(\d+)\]</sup>', r'[[fn:\1]]', text)
    text = re.sub(r'\[fn:(\d+)\](?!\])', r'[[fn:\1]]', text)  # single-bracket variant

    # 2. Normalise [Lat.: X] — strip the prefix, keep the content
    text = re.sub(r'\[Lat\.\:\s*(.*?)\]', r'\1', text)

    # 3. Common word-concatenation artifacts from the LLM
    concat_fixes = [
        (r'\bthevision\b',   'the vision'),
        (r'\btheword\b',     'the word'),
        (r'\bthesoul\b',     'the soul'),
        (r'\btheintellect\b','the intellect'),
        (r'\bthebody\b',     'the body'),
    ]
    for pattern, repl in concat_fixes:
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)

    return text


def inject_tags(translated_text, tags):
    """Re-weave original HTML tags back into translated text using [[t:N]] markers."""
    for i, tag in enumerate(tags):
        translated_text = translated_text.replace(f"[[t:{i}]]", tag)
    return translated_text


# ── Sub-footnote consolidation ────────────────────────────────────────────────

def consolidate_sub_footnotes(raw_fns):
    """
    Merge fn.X.sub_0 + fn.X.sub_1 ... → fn.X.
    The rehab file should not have sub-parts (1-at-a-time pipeline),
    but the old Gemini fallback might.
    """
    merged = {}
    sub_groups = {}

    for k, v in raw_fns.items():
        if ".sub_" in k:
            base, idx = k.rsplit(".sub_", 1)
            sub_groups.setdefault(base, []).append((int(idx), v))
        else:
            merged[k] = v

    for base_id, parts in sub_groups.items():
        parts.sort(key=lambda x: x[0])
        merged[base_id] = " ".join(p[1] for p in parts)

    return merged


# ── Main merge ────────────────────────────────────────────────────────────────

def merge_production():
    print("=== Munk Production Merger (v2 — UTF-8 Clean) ===\n")

    # 1. Load French source (for tag arrays)
    print("[1/6] Loading French source for tag metadata...")
    from munk_pipeline_groq import extract_and_flatten
    fr_data = load_json(FR_SOURCE)
    fr_segments, fr_fns = extract_and_flatten(fr_data)
    print(f"      {len(fr_segments)} segments, {len(fr_fns)} footnotes in source.\n")

    # 2. Load main text (raw translated, [[t:N]] markers still in place)
    print("[2/6] Loading main text checkpoint...")
    main_raw = load_json(MAIN_TEXT_FILE)
    print(f"      {len(main_raw)} segments loaded.\n")

    # 3. Re-weave HTML tags back into main text
    print("[3/6] Re-weaving formatting tags into main text...")
    main_clean = {}
    unresolved_tags = 0
    for seg_id, translated in main_raw.items():
        source_entry = fr_segments.get(seg_id)
        if source_entry and source_entry.get("tags"):
            woven = inject_tags(translated, source_entry["tags"])
        else:
            woven = translated
            if "[[t:" in translated:
                unresolved_tags += 1
        main_clean[seg_id] = clean_text(woven)
    print(f"      Done. {unresolved_tags} segments had unresolvable [[t:N]] tags.\n")

    # 4. Load footnotes — rehab file takes priority, old file as fallback
    print("[4/6] Loading and merging footnote checkpoints...")
    rehab_fns   = load_json(FN_REHAB_FILE) if os.path.exists(FN_REHAB_FILE) else {}
    old_fns_raw = load_json(FN_OLD_FILE)   if os.path.exists(FN_OLD_FILE)   else {}
    old_fns = consolidate_sub_footnotes(old_fns_raw)

    # Priority merge: rehab wins; old fills gaps
    merged_fns = {**old_fns, **rehab_fns}   # rehab overwrites old for same IDs
    print(f"      Rehab: {len(rehab_fns)} | Old (consolidated): {len(old_fns)} | "
          f"Final unique: {len(merged_fns)}\n")

    # 5. Re-weave tags into footnotes
    print("[5/6] Re-weaving formatting tags into footnotes...")
    final_fns = {}
    fn_tag_errors = 0
    for fn_id, fn_text in merged_fns.items():
        source_entry = fr_fns.get(fn_id) or fr_fns.get(f"{fn_id}.sub_0")
        if source_entry and source_entry.get("tags"):
            woven = inject_tags(fn_text, source_entry["tags"])
        else:
            woven = fn_text
            if "[[t:" in fn_text:
                fn_tag_errors += 1
        final_fns[fn_id] = clean_text(woven)
    print(f"      Done. {fn_tag_errors} footnotes had unresolvable [[t:N]] tags.\n")

    # 6. Assemble and write production JSON
    print("[6/6] Writing production JSON...")
    production = {
        "metadata": {
            "version": "2.0",
            "description": "Salomon Munk — Guide for the Perplexed (English, Production)",
            "generated_at": datetime.datetime.now().isoformat(),
            "source": FR_SOURCE,
            "main_text_segments": len(main_clean),
            "footnotes": len(final_fns),
            "rehab_footnotes": len(rehab_fns),
            "fallback_footnotes": len(old_fns),
        },
        "text": main_clean,
        "footnotes": final_fns,
    }

    save_json(OUTPUT_FILE, production)

    print(f"\n✅ Done. Production JSON written to: {OUTPUT_FILE}")
    print(f"   Main text segments : {len(main_clean)}")
    print(f"   Footnotes          : {len(final_fns)}")
    print(f"   (Rehab coverage    : {len(rehab_fns)/max(len(final_fns),1)*100:.1f}%)")


if __name__ == "__main__":
    merge_production()
