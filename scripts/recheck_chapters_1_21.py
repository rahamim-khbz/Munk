#!/usr/bin/env python3
"""
scripts/recheck_chapters_1_21.py - Retroactive Style & Footnote Normalization.
Inspects all 144 reviewed segments and early footnotes (fn.0-fn.172) in munk_production_v2.json,
aligns them with v2_style_sheet.md, fixes tag inversions, purges archaisms,
and verifies 100% compliance with StrictApparatusValidator.
"""

import os
import sys
import re
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scripts.validate_review import StrictApparatusValidator

def normalize_text_lexicon(text: str) -> str:
    """Normalizes philosophical terms, archaisms, and transliterations in text."""
    # 1. Homonym -> equivocal term
    # Avoid replacing if already 'an equivocal term'
    text = re.sub(r'\bhomonyms\b', 'equivocal terms', text, flags=re.IGNORECASE)
    text = re.sub(r'\bhomonymy\b', 'equivocation', text, flags=re.IGNORECASE)
    text = re.sub(r'\ba homonym\b', 'an equivocal term', text, flags=re.IGNORECASE)
    text = re.sub(r'\bthe homonym\b', 'the equivocal term', text, flags=re.IGNORECASE)
    text = re.sub(r'\bhomonym\b', 'equivocal term', text, flags=re.IGNORECASE)
    
    # 2. Doctors -> Sages (rabbinic)
    text = re.sub(r'\bthe doctors of the Law\b', 'the Sages of the Law', text, flags=re.IGNORECASE)
    text = re.sub(r'\bthe doctors\b', 'the Sages', text, flags=re.IGNORECASE)
    text = re.sub(r'\bour doctors\b', 'our Sages', text, flags=re.IGNORECASE)

    # 3. Purge archaisms
    text = re.sub(r'\bunto\b', 'to', text)
    text = re.sub(r'\bUnto\b', 'To', text)
    text = re.sub(r'\bwhilst\b', 'while', text, flags=re.IGNORECASE)
    text = re.sub(r'\bhath\b', 'has', text, flags=re.IGNORECASE)
    text = re.sub(r'\bdoth\b', 'does', text, flags=re.IGNORECASE)
    text = re.sub(r'\bthou\b', 'you', text, flags=re.IGNORECASE)
    text = re.sub(r'\bthee\b', 'you', text, flags=re.IGNORECASE)
    text = re.sub(r'\bthine\b', 'your', text, flags=re.IGNORECASE)

    # 4. Transliteration unification
    text = text.replace("’Āmad", "’Amad")
    text = text.replace("’āmad", "’amad")

    return text

def fix_known_segment_corruptions(sid: str, text: str) -> str:
    """Applies precise fixes for tag inversions and drafting collisions in specific segments."""
    if sid == "root.text.Part 1..1.4.sub_0":
        text = text.replace('<span dir="rtl">ugly</span>', '<i>ugly</i>')
        text = text.replace('<span dir="rtl">false</span>', '<i>false</i>')
        text = text.replace('<i>אמת</i>', '<span dir="rtl">אמת</span>')
        text = text.replace('<i>טוב</i>', '<span dir="rtl">טוב</span>')
        text = text.replace('<i>רע</i>', '<span dir="rtl">רע</span>')

    elif sid == "root.text.Part 1..3.3":
        # Repair Hebrew/English tag inversion and OCR typo
        text = text.replace("theintuition", "the intuition")
        text = text.replace("<i>לא הביט</i> <span dir=\"rtl\">in Jacob</span>", "<span dir=\"rtl\">לא הביט</span> <i>in Jacob</i>")
        text = text.replace("<i>והביטו</i> <span dir=\"rtl\">after Moses</span>", "<span dir=\"rtl\">והביטו</span> <i>after Moses</i>")
        text = text.replace("<i>הבט</i> <span dir=\"rtl\">toward the heaven</span>", "<span dir=\"rtl\">הבט</span> <i>toward the heaven</i>")
        text = text.replace("… <span dir=\"rtl\">to look</span> <i>מהביט</i> <span dir=\"rtl\">toward God</span>", "… <span dir=\"rtl\">מהביט</span> <i>to look toward God</i>")
        text = text.replace("<i>יביט</i> <span dir=\"rtl\">the figure of God</span>", "<span dir=\"rtl\">יביט</span> <i>the figure of God</i>")
        text = text.replace("<i>והביט</i> <span dir=\"rtl\">at iniquity</span>", "<span dir=\"rtl\">והביט</span> <i>at iniquity</i>")
        text = text.replace("Genesis, 19, 17", "Gen. 19:17")
        text = text.replace("Isaiah, 5, 30", "Isa. 5:30")
        text = text.replace("Numbers, 23, 21", "Num. 23:21")
        text = text.replace("Exodus, 33, 8", "Exod. 33:8")
        text = text.replace("Genesis, 15, 5", "Gen. 15:5")
        text = text.replace("Exodus, 3, 6", "Exod. 3:6")
        text = text.replace("Numbers, 12, 8", "Num. 12:8")
        text = text.replace("Habakkuk, 1, 13", "Hab. 1:13")

    elif sid == "root.text.Part 1..3.4":
        text = text.replace("<i>ותחז</i> <span dir=\"rtl\">the fall of Zion</span>", "<span dir=\"rtl\">ותחז</span> <i>the fall of Zion</i>")
        text = text.replace("<i>חזה</i> <span dir=\"rtl\">upon Judah and Jerusalem</span>", "<span dir=\"rtl\">חזה</span> <i>upon Judah and Jerusalem</i>")
        text = text.replace("<i>במחזה</i> <span dir=\"rtl\">in a vision</span>", "<span dir=\"rtl\">במחזה</span> <i>in a vision</i>")
        text = text.replace("<i>ויחזו</i> <span dir=\"rtl\">God</span>", "<span dir=\"rtl\">ויחזו</span> <i>God</i>")
        text = text.replace("Micah, 4, 11", "Mic. 4:11")
        text = text.replace("Isaiah, 1, 1", "Isa. 1:1")
        text = text.replace("Genesis, 15, 1", "Gen. 15:1")
        text = text.replace("Exodus, 24, 11", "Exod. 24:11")

    elif sid == "root.text.Part 1..6.0":
        text = text.replace("(<i>וילדו</i>) <span dir=\"rtl\">sons</span>", "(<span dir=\"rtl\">וילדו</span>) <i>sons</i>")
        text = text.replace("<span dir=\"rtl\">that she has made it germinate</span> (<i>והולידה</i>)", "<i>that it has made it germinate</i> (<span dir=\"rtl\">והולידה</span>)")
        text = text.replace("<span dir=\"rtl\">For you know not what the day shall bring forth</span> (<i>ילד</i>)", "<i>For you do not know what a day will bring forth</i> (<span dir=\"rtl\">ילד</span>)")
        text = text.replace("<span dir=\"rtl\">And he shall bring forth</span> (<i>וילד</i>)", "<i>And he brought forth</i> (<span dir=\"rtl\">וילד</span>)")
        text = text.replace("<span dir=\"rtl\">And they are content with the children</span> (<i>בילדי</i>)", "<i>And they are content with the children</i> (<span dir=\"rtl\">בילדי</span>)")
        text = text.replace("<span dir=\"rtl\">And they follow the laws of the nations.</span>", "<i>And they walk in the laws of the nations.</i>")

    elif sid == "root.text.Part 1..9.1":
        text = text.replace("sense ofdescendere andascendere", "sense of descending and ascending")
        text = text.replace("<i>ירד</i> (descendere)", "<span dir=\"rtl\">ירד</span> (descending)")
        text = text.replace("<i>עלה</i> (ascendere)", "<span dir=\"rtl\">עלה</span> (ascending)")
        text = text.replace("<span dir=\"rtl\">ירד</span> (descendere)", "<span dir=\"rtl\">ירד</span> (descending)")
        text = text.replace("<span dir=\"rtl\">עלה</span> (ascendere)", "<span dir=\"rtl\">עלה</span> (ascending)")
        text = text.replace("<span dir=\"rtl\">The stranger who is in your midst willascendere</span> (<span dir=\"rtl\">יעלה</span>) <i>higher and higher above you, and you willdescendere</i> (<span dir=\"rtl\">תרד</span>) <i>lower and lower</i>", "<i>The stranger who is in your midst shall ascend</i> (<span dir=\"rtl\">יעלה</span>) <i>higher and higher above you, and you shall descend</i> (<span dir=\"rtl\">תרד</span>) <i>lower and lower</i>")
        text = text.replace("<span dir=\"rtl\">Ibid.</span>", "<i>Ibid.</i>")
        text = text.replace("<small>למעלה</small>", "<span dir=\"rtl\">למעלה</span>")
        text = text.replace("«One must makeascendere the sacred things, but not make themdescendere»", "“One must elevate sacred things, but not demote them”")
        text = text.replace("Deuteronomy, 28, 43", "Deut. 28:43")
        text = text.replace("I Chronicles, 29, 25", "I Chron. 29:25")

    elif sid == "root.text.Part 1..10.1":
        text = text.replace("residest", "reside")
        text = text.replace("resids", "resides")
        text = text.replace("Lament., 5, 19", "Lam. 5:19")
        text = text.replace("Ps. 123, 1", "Ps. 123:1")
        text = text.replace("Ps. 2, 4", "Ps. 2:4")
        text = text.replace("Malach., 3, 6", "Mal. 3:6")

    return text

def fix_known_footnote_corruptions(fid: str, text: str) -> str:
    """Applies precise fixes for footnotes fn.0 through fn.172."""
    if fid == "fn.6":
        text = text.replace("Dictionnaire des sciences philosophiques", "Dictionary of the Philosophical Sciences")
        text = text.replace("article <i>Arabes</i>", "article “Arabes”")

    elif fid == "fn.23":
        text = text.replace("<span dir=\"rtl\">with a slight difference between them</span>", "<span dir=\"rtl\">במעט הפרש ביניהם</span>")

    elif fid == "fn.36":
        text = text.replace("2nd<sup> part, tractate </sup>Shebu'oth<i> or of </i>Oaths<i>, ch. VIII);", "2nd part, tractate <i>Shevu‘ot</i> (or <i>Oaths</i>), ch. VIII);")

    elif fid == "fn.71":
        text = text.replace("Abrégé de l’Organon", "Epitome of the Organon")
        text = text.replace("Topiques", "Topics")
        text = text.replace("Morale à Nicemaque", "Nicomachean Ethics")

    # Purge archaisms in footnotes
    text = re.sub(r'\bunto\b', 'to', text)
    text = re.sub(r'\bwhilst\b', 'while', text, flags=re.IGNORECASE)
    text = re.sub(r'\bhath\b', 'has', text, flags=re.IGNORECASE)
    text = re.sub(r'\bdoth\b', 'does', text, flags=re.IGNORECASE)

    return text

def main():
    v2_path = os.path.join(BASE_DIR, "munk_production_v2.json")
    v1_path = os.path.join(BASE_DIR, "munk_production_v1.json")
    audit_dir = os.path.join(BASE_DIR, "docs", "audits")
    os.makedirs(audit_dir, exist_ok=True)

    with open(v2_path, "r", encoding="utf-8") as f:
        v2 = json.load(f)
    with open(v1_path, "r", encoding="utf-8") as f:
        v1 = json.load(f)

    validator = StrictApparatusValidator()
    reviewed_segs = v2["metadata"].get("reviewed_segments", [])
    print(f"Total reviewed segments: {len(reviewed_segs)}")

    # 1. Normalize segments
    modified_segs = []
    for sid in reviewed_segs:
        orig = v2["text"].get(sid, "")
        norm = normalize_text_lexicon(orig)
        norm = fix_known_segment_corruptions(sid, norm)
        
        ok, errs = validator.validate_segment(sid, orig, norm)
        if not ok:
            print(f"ERROR on segment {sid}: {errs}")
            exit(1)
        if norm != orig:
            v2["text"][sid] = norm
            modified_segs.append(sid)

    print(f"Normalized {len(modified_segs)} segments.")

    # 2. Collect referenced footnotes
    ref_fns = set()
    for sid in reviewed_segs:
        ref_fns.update(re.findall(r'\[\[fn:(\d+)\]\]', v2["text"][sid]))

    print(f"Total footnotes referenced in reviewed segments: {len(ref_fns)}")

    # 3. Normalize referenced footnotes
    modified_fns = []
    v2_footnotes = v2.setdefault("footnotes", {})
    v1_footnotes = v1.get("footnotes", {})
    v2_reviewed_fns = v2["metadata"].setdefault("reviewed_footnotes", [])

    for fn_num in sorted(ref_fns, key=lambda x: int(x)):
        fid = f"fn.{fn_num}"
        orig_fn = v2_footnotes.get(fid) or v1_footnotes.get(fid, "")
        norm_fn = normalize_text_lexicon(orig_fn)
        norm_fn = fix_known_footnote_corruptions(fid, norm_fn)

        ok, errs = validator.validate_footnote(fid, orig_fn, norm_fn)
        if not ok:
            print(f"ERROR on footnote {fid}: {errs}")
            exit(1)

        v2_footnotes[fid] = norm_fn
        if norm_fn != orig_fn:
            modified_fns.append(fid)

        if fid not in v2["metadata"]["reviewed_footnotes"]:
            v2["metadata"]["reviewed_footnotes"].append(fid)

    print(f"Normalized {len(modified_fns)} footnotes. Total reviewed footnotes in metadata: {len(v2['metadata']['reviewed_footnotes'])}")

    # 4. Save atomically
    tmp_path = v2_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(v2, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, v2_path)

    # 5. Write audit report
    audit_file = os.path.join(audit_dir, "review_audit_retroactive_chapters_1_21.md")
    with open(audit_file, "w", encoding="utf-8") as f:
        f.write("# Retroactive Normalization Audit: Chapters 1–21 & Early Footnotes\n\n")
        f.write(f"- **Total Segments Inspected:** {len(reviewed_segs)}\n")
        f.write(f"- **Segments Normalized:** {len(modified_segs)}\n")
        f.write(f"- **Footnotes Reviewed:** {len(v2['metadata']['reviewed_footnotes'])}\n")
        f.write(f"- **Footnotes Normalized:** {len(modified_fns)}\n")
        f.write("- **Strict Apparatus Validation:** 100% Passed (0 errors)\n\n")
        f.write("## Normalized Segments Sample\n")
        for sid in modified_segs[:10]:
            f.write(f"- `{sid}`\n")
        f.write("\n## Normalized Footnotes Sample\n")
        for fid in modified_fns[:10]:
            f.write(f"- `{fid}`\n")

    print(f"Saved audit log to: {audit_file}")
    print("Retroactive normalization completed successfully!")

if __name__ == "__main__":
    main()
