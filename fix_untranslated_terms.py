#!/usr/bin/env python3
"""
fix_untranslated_terms.py — Scans and fixes untranslated Arabic/Hebrew anomalies in Munk translation.

ROOT CAUSE ANALYSIS
===================
The translation prompt instructs: "Preserve ALL Hebrew, Arabic, and Greek script exactly."
This instruction was intended for script that appears in the French SOURCE (e.g., Munk's inline
Hebrew/Arabic citations). However, the LLM sometimes REPLACED Munk's Latin-alphabet
transliterations (like "Makâmât", "Motécallemîn") with the original Arabic script forms
(مَقَامَات, مُتَكَلِمُون), violating the other instruction: "Translate ONLY what is in the
provided French text."

ANOMALY CATEGORIES
==================
1. MAIN TEXT — LLM-introduced Arabic (2 cases in Letter to R' Joseph):
   - "Makâmât" → مَقَامَات  (should be "Makâmât" or "maqāmāt [assemblies/sessions]")
   - "Motécallemîn" → مُتَكَلِمُون (should be "Mutakallimūn" or "Motécallemîn")
   These are REAL BUGS to fix.

2. MAIN TEXT — Part 1, Ch 42: Arabic in parenthetical context with transliteration — CORRECT.

3. FOOTNOTES — Arabic words in scholarly linguistic discussion (75 occurrences across 26 footnotes):
   These are CORRECT: Munk's footnotes discuss Arabic etymology and grammar, so Arabic script
   is intentionally preserved from the French source.

FIX STRATEGY
============
- Fix the 2 main text anomalies in checkpoint_main_text_groq.json
- Fix the footnote superscript position issue (fn marker before Arabic word instead of after)
- Rebuild the viewer
"""

import json
import re
import os
import shutil
from datetime import datetime


def backup_file(filepath):
    """Create a timestamped backup before modifying."""
    if os.path.exists(filepath):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = f"{filepath}.bak_{ts}"
        shutil.copy2(filepath, backup)
        print(f"  [Backup] {os.path.basename(filepath)} → {os.path.basename(backup)}")
        return backup
    return None


def scan_main_text(main_text):
    """Scan main text for standalone Arabic words not in proper scholarly context."""
    arabic_word = re.compile(
        r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\u064B-\u065F]+'
    )
    
    anomalies = []
    for seg_id, text in sorted(main_text.items()):
        for m in arabic_word.finditer(text):
            word = m.group()
            idx = m.start()
            before = text[max(0, idx - 60):idx]
            after = text[idx + len(word):min(len(text), idx + len(word) + 60)]
            
            # Skip if inside <span dir="rtl"> or parentheses (legitimate scholarly context)
            in_span = 'dir="rtl"' in before[-50:] or '<span' in before[-50:]
            in_parens = ('(' in before[-5:]) and (')' in after[:5])
            
            if not in_span and not in_parens:
                context = text[max(0, idx - 60):min(len(text), idx + len(word) + 60)]
                anomalies.append({
                    'seg_id': seg_id,
                    'word': word,
                    'position': idx,
                    'context': context
                })
    
    return anomalies


def scan_footnotes(footnotes):
    """Scan footnotes for standalone Arabic words (informational — most are legitimate)."""
    arabic_word = re.compile(
        r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\u064B-\u065F]+'
    )
    
    anomalies = []
    for fn_id, text in sorted(footnotes.items()):
        for m in arabic_word.finditer(text):
            word = m.group()
            idx = m.start()
            before = text[max(0, idx - 60):idx]
            
            in_span = 'dir="rtl"' in before[-50:] or '<span' in before[-50:]
            if not in_span:
                anomalies.append({
                    'fn_id': fn_id,
                    'word': word,
                    'position': idx,
                })
    
    return anomalies


def fix_main_text_anomalies(main_text):
    """Fix known anomalies in the main translated text."""
    fixes_applied = 0
    
    seg_key = "root.text.Letter to R Joseph son of Judah.2"
    if seg_key in main_text:
        text = main_text[seg_key]
        
        # Fix 1: مَقَامَات → Makâmât (maqāmāt, literary assemblies/sessions)
        # The French source has: tes <i>Makâmât</i>
        # The tag markers [[t:0]] and [[t:1]] wrap the <i> tags, so the word
        # between them should be the transliteration, not Arabic script
        old_1 = "[[t:0]]مَقَامَات[[t:1]]"
        new_1 = "[[t:0]]Makâmât[[t:1]]"
        if old_1 in text:
            text = text.replace(old_1, new_1)
            fixes_applied += 1
            print(f"  [Fix] مَقَامَات → Makâmât (Letter to R' Joseph)")
        
        # Fix 2: مُتَكَلِمُون → Motécallemîn (the Mutakallimūn)
        # The French source has: les <i>Motécallemîn</i>
        old_2 = "[[t:2]]مُتَكَلِمُون[[t:3]]"
        new_2 = "[[t:2]]Motécallemîn[[t:3]]"
        if old_2 in text:
            text = text.replace(old_2, new_2)
            fixes_applied += 1
            print(f"  [Fix] مُتَكَلِمُون → Motécallemîn (Letter to R' Joseph)")
        
        main_text[seg_key] = text
    
    # Fix 3: Check for archaic "thou" forms that slipped through in the Letter
    seg_key_3 = "root.text.Letter to R Joseph son of Judah.3"
    if seg_key_3 in main_text:
        text = main_text[seg_key_3]
        # "thou didst depart" etc. — these should use modern academic register
        archaic_fixes = {
            "thou didst depart": "you departed",
            "thou didst": "you did",
            "thou hast": "you have",
            "thou wert": "you were",
            "thou art": "you are",
            "thee ": "you ",
            "thy ": "your ",
            "thine ": "your ",
        }
        for old, new in archaic_fixes.items():
            if old in text:
                text = text.replace(old, new)
                fixes_applied += 1
                print(f"  [Fix] Archaic form: '{old}' → '{new}'")
        main_text[seg_key_3] = text
    
    return main_text, fixes_applied


def scan_all_segments(main_text, footnotes):
    """Full scan report."""
    print("=" * 70)
    print("  MUNK TRANSLATION — UNTRANSLATED TERM SCANNER")
    print("=" * 70)
    
    print("\n--- MAIN TEXT SCAN ---")
    main_anomalies = scan_main_text(main_text)
    if main_anomalies:
        print(f"  Found {len(main_anomalies)} standalone Arabic words:")
        for a in main_anomalies:
            print(f"    ❌ {a['seg_id']}: \"{a['word']}\"")
            print(f"       ...{a['context']}...")
    else:
        print("  ✅ No standalone Arabic anomalies found.")
    
    print("\n--- FOOTNOTE SCAN (informational) ---")
    fn_anomalies = scan_footnotes(footnotes)
    from collections import Counter
    fn_counts = Counter(a['fn_id'] for a in fn_anomalies)
    print(f"  {len(fn_anomalies)} Arabic words across {len(fn_counts)} footnotes")
    print("  (Most are legitimate scholarly citations — Munk discusses Arabic etymology)")
    
    # Check for truly problematic footnote cases
    # A footnote is problematic if it has Arabic WITHOUT any nearby English gloss
    problematic_fns = []
    for fn_id, text in footnotes.items():
        arabic_pattern = re.compile(r'[\u0600-\u06FF\u064B-\u065F]+')
        matches = list(arabic_pattern.finditer(text))
        if not matches:
            continue
        
        # Check if the Arabic words have NO English translation/gloss nearby
        has_gloss = bool(re.search(
            r'(meaning|signif|i\.e\.|that is|namely|in the sense of|which means|translat)',
            text, re.I
        ))
        has_span = 'dir="rtl"' in text
        
        if not has_gloss and not has_span and len(matches) > 2:
            problematic_fns.append(fn_id)
    
    if problematic_fns:
        print(f"\n  ⚠️ Potentially under-contextualized footnotes: {problematic_fns}")
    
    return main_anomalies, fn_anomalies


def main():
    print("=" * 70)
    print("  MUNK TRANSLATION — FIX UNTRANSLATED TERMS")
    print("=" * 70)
    
    # Load data
    with open("checkpoint_main_text_groq.json", "r", encoding="utf-8") as f:
        main_text = json.load(f)
    
    with open("checkpoint_footnotes_gemini.json", "r", encoding="utf-8") as f:
        footnotes = json.load(f)
    
    # Also load the rehab footnotes checkpoint (used by the viewer)
    rehab_fn_path = "checkpoint_footnotes_rehab_groq.json"
    if os.path.exists(rehab_fn_path):
        with open(rehab_fn_path, "r", encoding="utf-8") as f:
            footnotes_rehab = json.load(f)
    else:
        footnotes_rehab = None
    
    # Phase 1: Scan
    print("\n[Phase 1] Scanning all segments...\n")
    scan_all_segments(main_text, footnotes)
    
    # Phase 2: Fix
    print("\n" + "=" * 70)
    print("[Phase 2] Applying fixes to main text...\n")
    
    backup_file("checkpoint_main_text_groq.json")
    main_text, fix_count = fix_main_text_anomalies(main_text)
    
    if fix_count > 0:
        with open("checkpoint_main_text_groq.json", "w", encoding="utf-8") as f:
            json.dump(main_text, f, indent=2, ensure_ascii=False)
        print(f"\n  ✅ {fix_count} fixes applied to checkpoint_main_text_groq.json")
    else:
        print("  ℹ️ No fixes needed (already clean).")
    
    # Phase 3: Verify
    print("\n" + "=" * 70)
    print("[Phase 3] Post-fix verification...\n")
    remaining = scan_main_text(main_text)
    # Filter out the Part 1 Ch 42 case which is legitimate (Arabic in parenthetical context)
    true_anomalies = [a for a in remaining 
                      if 'kanaftu' not in main_text.get(a['seg_id'], '').lower()
                      and '(' not in main_text.get(a['seg_id'], '')[max(0, a['position']-5):a['position']]]
    
    if not true_anomalies:
        print("  ✅ All main text anomalies resolved!")
    else:
        print(f"  ⚠️ {len(true_anomalies)} remaining anomalies (may need manual review):")
        for a in true_anomalies:
            print(f"    {a['seg_id']}: \"{a['word']}\"")
    
    print("\n" + "=" * 70)
    print("  PROMPT ANALYSIS — WHY THESE ANOMALIES OCCURRED")
    print("=" * 70)
    print("""
  The translation prompts contain a tension between two instructions:

  1. "Preserve ALL Hebrew, Arabic, and Greek script exactly."
     → This was intended for script ALREADY present in the French source.

  2. "NO EXTERNAL KNOWLEDGE... Translate ONLY what is in the provided French text."
     → This should prevent the LLM from introducing new content.

  What happened: The French source had Latin-alphabet transliterations like
  "Makâmât" and "Motécallemîn" (standard Munk scholarly convention). The LLM
  recognized these as Arabic terms and REPLACED them with Arabic script forms,
  violating instruction #2 while trying to honour instruction #1.

  RECOMMENDED PROMPT FIX for future runs:
  Change: "Preserve ALL Hebrew, Arabic, and Greek script exactly."
  To:     "Preserve ALL Hebrew, Arabic, and Greek script exactly AS IT APPEARS
           IN THE SOURCE. Do NOT convert Latin-alphabet transliterations
           (e.g., Makâmât, Motécallemîn) into their original scripts."
""")
    
    print("\nDone. Run `python3 build_full_viewer.py` to rebuild the viewer.\n")


if __name__ == "__main__":
    main()
