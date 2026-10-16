#!/usr/bin/env python3
"""
Deterministic quality gate for single-page Faur JSON records.
Rejects any page with mismatched footnotes, Cyrillic characters,
optical digit/letter swaps (I982, x7b, I3b, 1o), unhealed hyphens,
or mangled superscript symbols (."º, ."s, .').
"""

import json
import re
import sys
from typing import Dict, Any, List

REQUIRED_FIELDS = [
    "page_id", "section_file", "spread_index", "spread_side",
    "scan_image", "note_pages", "note_scan_images", "status",
    "continues_from_prev_page", "ends_with_hyphen", "blocks", "footnotes"
]

# Cyrillic Unicode block U+0400..U+04FF
CYRILLIC_RE = re.compile(r'[\u0400-\u04FF]')

# Unhealed mid-line hyphenation like "applica- tion"
MIDLINE_HYPHEN_RE = re.compile(r'\b[a-zA-Z]+-\s+[a-z]+\b')

# Mangled OCR superscript callouts at end of clauses/quotes
MANGLED_SUPERSCRIPT_RE = re.compile(r'(\."[sº°*?!\']|\.\'[0-9a-zA-Z]|\.[º°*])')

# Optical digit/letter confusions in years, folios, or citations
OPTICAL_DIGIT_SWAP_RE = re.compile(
    r'\b(I9\d\d|19[89]I|[Ix]\d{1,2}[ab]|\d+[Io]\b|z:[I1]|\bI[0-9]{1,2}\b|\[[xrz]\])'
)

FOOTNOTE_CALLOUT_RE = re.compile(r'\[\^(\d+)\]')


def validate_text_segment(text: str, location: str) -> List[str]:
    errors = []
    if CYRILLIC_RE.search(text):
        match = CYRILLIC_RE.search(text).group(0)
        errors.append(f"{location}: Cyrillic character detected ({repr(match)})")
    if MIDLINE_HYPHEN_RE.search(text):
        match = MIDLINE_HYPHEN_RE.search(text).group(0)
        errors.append(f"{location}: Unhealed mid-line hyphenation ({repr(match)})")
    if MANGLED_SUPERSCRIPT_RE.search(text):
        match = MANGLED_SUPERSCRIPT_RE.search(text).group(0)
        errors.append(f"{location}: Mangled OCR footnote symbol ({repr(match)})")
    if OPTICAL_DIGIT_SWAP_RE.search(text):
        match = OPTICAL_DIGIT_SWAP_RE.search(text).group(0)
        errors.append(f"{location}: Optical digit/letter confusion ({repr(match)})")
    return errors


def validate_page_record(record: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    for field in REQUIRED_FIELDS:
        if field not in record:
            errors.append(f"Missing required field: {field}")
    if errors:
        return errors

    blocks = record.get("blocks", [])
    footnotes = record.get("footnotes", {})
    if not blocks and record.get("page_id") not in ("i", "iii", "iv", "v"):
        errors.append("Page has zero content blocks")

    called_notes: List[str] = []
    for idx, block in enumerate(blocks):
        b_id = block.get("block_id", f"block_{idx}")
        md = block.get("markdown", "")
        errors.extend(validate_text_segment(md, f"Block {b_id}"))
        for m in FOOTNOTE_CALLOUT_RE.finditer(md):
            called_notes.append(m.group(1))

    for fn_num, fn_text in footnotes.items():
        if not fn_text or not fn_text.strip():
            errors.append(f"Footnote [^{fn_num}] is empty")
        errors.extend(validate_text_segment(fn_text, f"Footnote [^{fn_num}]"))

    called_set = set(called_notes)
    defined_set = set(footnotes.keys())

    for c in called_notes:
        if c not in defined_set:
            errors.append(f"Missing footnote definition for [^{c}]")
    for d in defined_set:
        if d not in called_set:
            errors.append(f"Orphan footnote definition [^{d}] not called in page blocks")

    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_faur_page.py <path/to/page.json>")
        sys.exit(2)
    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        record = json.load(f)
    errs = validate_page_record(record)
    if errs:
        print(f"FAIL ({len(errs)} errors in {path}):")
        for e in errs:
            print(f"  - {e}")
        sys.exit(1)
    print(f"PASS: {path} (0 errors, {len(record['blocks'])} blocks, {len(record['footnotes'])} footnotes)")


if __name__ == "__main__":
    main()
