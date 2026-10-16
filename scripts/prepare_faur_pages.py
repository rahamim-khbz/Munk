#!/usr/bin/env python3
"""
Renders 300 DPI single-page PNG crops from the 144-spread PDF and
initializes data/faur_queue_state.json for slow page-by-page processing.
"""

import json
import os
import fitz  # PyMuPDF

PDF_PATH = "Faur J. - Homo Mysticus_ A Guide to Maimonides's Guide for the Perplexed.pdf"
SCANS_DIR = "data/faur_scans"
PAGES_DIR = "data/faur_pages"
QUEUE_PATH = "data/faur_queue_state.json"


def get_note_pages_for_book_page(page_id: str) -> list[str]:
    """Maps a main text page ID to the back-of-book Note page(s) (pp. 183-248)."""
    if page_id in ("ix", "x", "xi"):
        return ["183", "184"]
    if page_id in ("xii", "xiii"):
        return ["184"]
    if not page_id.isdigit():
        return []
    p = int(page_id)
    # Approximate mapping across pp. 183-248 with +-1 page buffer so the notes subagent
    # always sees the exact page header "NOTES TO PAGES X-Y"
    if 1 <= p <= 19:
        return [str(n) for n in range(184, 193)]
    if 20 <= p <= 52:
        return [str(n) for n in range(192, 208)]
    if 53 <= p <= 88:
        return [str(n) for n in range(208, 221)]
    if 89 <= p <= 126:
        return [str(n) for n in range(221, 232)]
    if 127 <= p <= 180:
        return [str(n) for n in range(232, 249)]
    return []


def build_book_page_manifest() -> list[dict]:
    manifest = []
    preface = [
        ("ix", 4, "right", ["183", "184"]),
        ("x", 5, "left", ["183", "184"]),
        ("xi", 5, "right", ["183", "184"]),
        ("xii", 6, "left", ["184"]),
        ("xiii", 6, "right", []),
    ]
    for pid, sp, side, npages in preface:
        manifest.append({
            "page_id": pid,
            "section_file": "00_front_matter.md",
            "spread_index": sp,
            "spread_side": side,
            "scan_image": f"data/faur_scans/page_{pid}.png",
            "note_pages": npages,
        })

    def section_for_page(p: int) -> str:
        if 1 <= p <= 19:
            return "01_introduction.md"
        if 20 <= p <= 52:
            return "02_part_one_apophasis.md"
        if 53 <= p <= 88:
            return "03_part_two_imagination.md"
        if 89 <= p <= 126:
            return "04_part_three_cosmology.md"
        if 127 <= p <= 180:
            return "05_part_four_anthropology.md"
        if 183 <= p <= 248:
            return "06_notes.md"
        if 249 <= p <= 261:
            return "07_bibliography.md"
        return "08_indexes.md"

    # Page 1 is Spread 8 Right; pp. 2-180 are Spreads 9..98 Left
    manifest.append({
        "page_id": "1",
        "section_file": "01_introduction.md",
        "spread_index": 8,
        "spread_side": "right",
        "scan_image": "data/faur_scans/page_001.png",
        "note_pages": ["184", "185"],
    })
    for sp in range(9, 99):
        left_p = (sp - 8) * 2
        right_p = left_p + 1
        for p, side in [(left_p, "left"), (right_p, "right")]:
            if p <= 180:
                manifest.append({
                    "page_id": str(p),
                    "section_file": section_for_page(p),
                    "spread_index": sp,
                    "spread_side": side,
                    "scan_image": f"data/faur_scans/page_{p:03d}.png",
                    "note_pages": get_note_pages_for_book_page(str(p)),
                })

    # Notes pp. 183-248 (Spread 99 Right = 183; Spreads 100-132 Left = 184-248)
    manifest.append({
        "page_id": "183",
        "section_file": "06_notes.md",
        "spread_index": 99,
        "spread_side": "right",
        "scan_image": "data/faur_scans/page_183.png",
        "note_pages": [],
    })
    for sp in range(100, 133):
        left_p = 184 + (sp - 100) * 2
        right_p = left_p + 1
        for p, side in [(left_p, "left"), (right_p, "right")]:
            if p <= 248:
                manifest.append({
                    "page_id": str(p),
                    "section_file": "06_notes.md",
                    "spread_index": sp,
                    "spread_side": side,
                    "scan_image": f"data/faur_scans/page_{p:03d}.png",
                    "note_pages": [],
                })
    return manifest


def render_page_crop(doc: fitz.Document, spread_index: int, side: str, out_path: str, dpi: int = 300):
    if os.path.exists(out_path):
        return
    page = doc[spread_index - 1]
    rect = page.rect
    mid_x = rect.width / 2.0
    clip = fitz.Rect(0, 0, mid_x, rect.height) if side == "left" else fitz.Rect(mid_x, 0, rect.width, rect.height)
    pix = page.get_pixmap(clip=clip, dpi=dpi)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pix.save(out_path)


if __name__ == "__main__":
    os.makedirs(SCANS_DIR, exist_ok=True)
    os.makedirs(PAGES_DIR, exist_ok=True)
    manifest = build_book_page_manifest()
    if os.path.exists(PDF_PATH):
        doc = fitz.open(PDF_PATH)
        for item in manifest:
            render_page_crop(doc, item["spread_index"], item["spread_side"], item["scan_image"])
        doc.close()
    if not os.path.exists(QUEUE_PATH):
        queue_state = {
            "active_batch_name": "pilot_preface_ix_to_xiii",
            "active_batch_pages": ["ix", "x", "xi", "xii", "xiii"],
            "pause_at_batch_end": True,
            "status": "ready",
            "pages": {
                item["page_id"]: {
                    "status": "pending",
                    "section_file": item["section_file"],
                    "spread_index": item["spread_index"],
                    "spread_side": item["spread_side"],
                    "scan_image": item["scan_image"],
                    "note_pages": item["note_pages"],
                }
                for item in manifest if item["section_file"] != "06_notes.md"
            }
        }
        with open(QUEUE_PATH, "w", encoding="utf-8") as f:
            json.dump(queue_state, f, indent=2)
