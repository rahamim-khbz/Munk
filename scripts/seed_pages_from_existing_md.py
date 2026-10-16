#!/usr/bin/env python3
"""
Seeds data/faur_pages/page_<id>.json from the existing consolidated Markdown
files in docs/faur_homo_mysticus/*.md (including pre-splitting 06_notes.md)
so subagents start from the existing first draft rather than a blank slate.
"""

import glob
import json
import os
import re
from typing import Dict, Any, List

SUPERSCRIPT_MAP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")
UNICODE_SUP_RE = re.compile(r'([⁰¹²³⁴⁵⁶⁷⁸⁹]+)')
PAGE_ANCHOR_RE = re.compile(r'<!--\s*\[p\.\s*([^\]]+)\]\s*-->')


def convert_unicode_superscripts_to_fn(text: str) -> str:
    def repl(m):
        digits = m.group(1).translate(SUPERSCRIPT_MAP)
        return f"[^{digits}]"
    return UNICODE_SUP_RE.sub(repl, text)


def slice_md_by_page_anchors(md_text: str) -> Dict[str, Dict[str, Any]]:
    parts = PAGE_ANCHOR_RE.split(md_text)
    pages: Dict[str, Dict[str, Any]] = {}
    # parts[0] is header before first <!-- [p. X] -->
    for i in range(1, len(parts), 2):
        page_id = parts[i].strip()
        raw_body = parts[i + 1] if i + 1 < len(parts) else ""
        # Check if raw_body starts immediately on the next line without blank line (continuation)
        stripped_leading = raw_body.lstrip(" \t")
        continues = stripped_leading.startswith("\n") and not stripped_leading.startswith("\n\n")

        raw_paras = [p.strip() for p in re.split(r'\n\s*\n', raw_body.strip()) if p.strip()]
        blocks: List[Dict[str, Any]] = []
        for idx, p in enumerate(raw_paras):
            p_clean = convert_unicode_superscripts_to_fn(p)
            if p_clean.startswith("#"):
                m = re.match(r'^(#+)\s+(.*)$', p_clean)
                level = len(m.group(1)) if m else 3
                title = m.group(2) if m else p_clean
                blocks.append({
                    "block_id": f"p{page_id}_b{idx+1}",
                    "type": "heading",
                    "level": level,
                    "markdown": title.strip()
                })
            elif p_clean.startswith(">"):
                unquoted = "\n".join(re.sub(r'^>\s?', '', line) for line in p_clean.splitlines())
                blocks.append({
                    "block_id": f"p{page_id}_b{idx+1}",
                    "type": "blockquote",
                    "markdown": unquoted.strip()
                })
            else:
                blocks.append({
                    "block_id": f"p{page_id}_b{idx+1}",
                    "type": "paragraph",
                    "indent": "continuation" if (idx == 0 and continues) else "indented",
                    "markdown": p_clean
                })

        ends_with_hyphen = bool(blocks and blocks[-1]["markdown"].endswith("-"))
        pages[page_id] = {
            "page_id": page_id,
            "continues_from_prev_page": continues,
            "ends_with_hyphen": ends_with_hyphen,
            "blocks": blocks,
        }
    return pages


def seed_canonical_pages(md_dir: str = "docs/faur_homo_mysticus", out_dir: str = "data/faur_pages"):
    os.makedirs(out_dir, exist_ok=True)
    from scripts.prepare_faur_pages import build_book_page_manifest
    manifest = build_book_page_manifest()
    manifest_by_id = {m["page_id"]: m for m in manifest}

    for md_file in sorted(glob.glob(os.path.join(md_dir, "*.md"))):
        with open(md_file, "r", encoding="utf-8") as f:
            text = f.read()
        sliced = slice_md_by_page_anchors(text)
        for pid, data in sliced.items():
            out_file = os.path.join(out_dir, f"page_{pid}.json")
            meta = manifest_by_id.get(pid, {})
            record = {
                "page_id": pid,
                "section_file": meta.get("section_file", os.path.basename(md_file)),
                "spread_index": meta.get("spread_index", 0),
                "spread_side": meta.get("spread_side", "unknown"),
                "scan_image": meta.get("scan_image", f"data/faur_scans/page_{pid}.png"),
                "note_pages": meta.get("note_pages", []),
                "note_scan_images": [f"data/faur_scans/page_{n}.png" for n in meta.get("note_pages", [])],
                "status": "draft",
                "continues_from_prev_page": data["continues_from_prev_page"],
                "ends_with_hyphen": data["ends_with_hyphen"],
                "blocks": data["blocks"],
                "footnotes": {},
                "audit_log": ["Seeded from " + os.path.basename(md_file)]
            }
            with open(out_file, "w", encoding="utf-8") as out_f:
                json.dump(record, out_f, indent=2)


if __name__ == "__main__":
    seed_canonical_pages()
    print("Successfully seeded pages into data/faur_pages")
