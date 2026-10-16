#!/usr/bin/env python3
"""
Deterministically compiles verified per-page JSON records into continuous,
page-break-free chapter Markdown files with self-contained [^N] footnotes.
"""

import json
import os
import re
from typing import List, Dict, Any


def stitch_pages_to_markdown(chapter_title: str, pages: List[Dict[str, Any]]) -> str:
    compiled_blocks: List[Dict[str, Any]] = []
    all_footnotes: Dict[str, str] = {}
    prev_ended_with_hyphen = False

    for page in pages:
        for k, v in page.get("footnotes", {}).items():
            all_footnotes[k] = v.strip()

        blocks = page.get("blocks", [])
        continues = page.get("continues_from_prev_page", False)

        for idx, block in enumerate(blocks):
            b_type = block["type"]
            b_md = block["markdown"].strip()

            if idx == 0 and continues and compiled_blocks and compiled_blocks[-1]["type"] == b_type:
                prev_md = compiled_blocks[-1]["markdown"]
                if prev_ended_with_hyphen and prev_md.endswith("-"):
                    compiled_blocks[-1]["markdown"] = prev_md[:-1] + b_md
                else:
                    compiled_blocks[-1]["markdown"] = prev_md + " " + b_md
            else:
                compiled_blocks.append({"type": b_type, "level": block.get("level", 3), "markdown": b_md})

        prev_ended_with_hyphen = page.get("ends_with_hyphen", False)

    out_lines = [f"# {chapter_title}\n"]
    for b in compiled_blocks:
        if b["type"] == "heading":
            hashes = "#" * b.get("level", 3)
            out_lines.append(f"{hashes} {b['markdown']}\n")
        elif b["type"] == "blockquote":
            quoted = "\n".join(f"> {line}" for line in b["markdown"].splitlines())
            out_lines.append(f"{quoted}\n")
        else:
            out_lines.append(f"{b['markdown']}\n")

    if all_footnotes:
        out_lines.append("---\n\n## Notes\n")
        sorted_keys = sorted(all_footnotes.keys(), key=lambda x: int(re.sub(r'\D', '', x) or 0))
        for k in sorted_keys:
            out_lines.append(f"[^{k}]: {all_footnotes[k]}\n")

    return "\n".join(out_lines)


def compile_chapter_from_pages(section_file: str, pages_dir: str = "data/faur_pages", out_dir: str = "docs/faur_homo_mysticus_verified"):
    os.makedirs(out_dir, exist_ok=True)
    from scripts.prepare_faur_pages import build_book_page_manifest
    manifest = build_book_page_manifest()
    
    # Filter manifest for this section file
    section_pages = [m for m in manifest if m["section_file"] == section_file]
    page_records = []
    for item in section_pages:
        p_path = os.path.join(pages_dir, f"page_{item['page_id']}.json")
        if os.path.exists(p_path):
            with open(p_path, "r", encoding="utf-8") as f:
                page_records.append(json.load(f))
    
    if not page_records:
        return None
    
    chapter_title = section_file.replace(".md", "").replace("_", " ").title()
    compiled_md = stitch_pages_to_markdown(chapter_title, page_records)
    out_file = os.path.join(out_dir, section_file)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(compiled_md)
    return out_file


if __name__ == "__main__":
    from scripts.prepare_faur_pages import build_book_page_manifest
    manifest = build_book_page_manifest()
    sections = sorted(list(set(m["section_file"] for m in manifest)))
    for s in sections:
        res = compile_chapter_from_pages(s)
        if res:
            print(f"Compiled {s} -> {res}")
