#!/usr/bin/env python3
"""
scripts/export_packet.py - Shard Packet Exporter.
Bundles text segments, co-referenced footnotes, and Faur lexical context
into a single isolated packet JSON for translator and verifier subagents.
"""

import os
import re
import json
import argparse
from typing import List, Dict, Any, Optional
from scripts.munk_aligner import MunkCorpusAligner

# Shard Distribution Matrix mapping shard_id -> list of chapter strings
def _ch_range(part: int, start: int, end: int) -> List[str]:
    return [f"Part {part}, Chapter {i}" for i in range(start, end + 1)]

SHARD_MATRIX: Dict[str, List[str]] = {
    # Wave 0 (Pilot)
    "p1_w0_s1": _ch_range(1, 22, 26),
    "p1_w0_s2": _ch_range(1, 27, 30),
    # Wave 1
    "p1_w1_s1": _ch_range(1, 31, 35),
    "p1_w1_s2": _ch_range(1, 36, 41),
    "p1_w1_s3": _ch_range(1, 42, 45),
    "p1_w1_s4": _ch_range(1, 46, 49),
    "p1_w1_s5": _ch_range(1, 50, 54),
    # Wave 2
    "p1_w2_s1": _ch_range(1, 55, 60),
    "p1_w2_s2": _ch_range(1, 61, 67),
    "p1_w2_s3": _ch_range(1, 68, 70),
    "p1_w2_s4": _ch_range(1, 71, 72),
    "p1_w2_s5": ["Part 1, Chapter 73"],
    "p1_w2_s6": _ch_range(1, 74, 76),
    # Wave 3
    "p2_w3_s1": ["Part 2, Introduction"] + _ch_range(2, 1, 2),
    "p2_w3_s2": _ch_range(2, 3, 7),
    "p2_w3_s3": _ch_range(2, 8, 12),
    "p2_w3_s4": _ch_range(2, 13, 18),
    "p2_w3_s5": _ch_range(2, 19, 24),
    # Wave 4
    "p2_w4_s1": _ch_range(2, 25, 31),
    "p2_w4_s2": _ch_range(2, 32, 35),
    "p2_w4_s3": _ch_range(2, 36, 39),
    "p2_w4_s4": _ch_range(2, 40, 44),
    "p2_w4_s5": _ch_range(2, 45, 48),
    # Wave 5
    "p3_w5_s1": _ch_range(3, 1, 7),
    "p3_w5_s2": _ch_range(3, 8, 12),
    "p3_w5_s3": _ch_range(3, 13, 16),
    "p3_w5_s4": _ch_range(3, 17, 21),
    "p3_w5_s5": _ch_range(3, 22, 24),
    # Wave 6
    "p3_w6_s1": _ch_range(3, 25, 31),
    "p3_w6_s2": _ch_range(3, 32, 35),
    "p3_w6_s3": _ch_range(3, 36, 42),
    "p3_w6_s4": _ch_range(3, 43, 49),
    "p3_w6_s5": _ch_range(3, 50, 54),
    "p3_w6_s6": ["Munk's Introduction"]
}

def export_shard_packet(
    shard_id: str,
    chapters: Optional[List[str]] = None,
    output_dir: str = "data/packets",
    base_dir: Optional[str] = None
) -> str:
    """Exports a single self-contained shard packet JSON."""
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if chapters is None:
        if shard_id in SHARD_MATRIX:
            chapters = SHARD_MATRIX[shard_id]
        else:
            raise ValueError(f"Unknown shard_id '{shard_id}' and no chapters provided.")

    aligner = MunkCorpusAligner(base_dir=base_dir)

    # Load munk raw to get master footnotes
    munk_path = os.path.join(base_dir, "munk_production_v1.json")
    with open(munk_path, "r", encoding="utf-8") as f:
        munk_raw = json.load(f)
    all_footnotes = munk_raw.get("footnotes", {})

    # Load Faur guide index if available
    faur_path = os.path.join(base_dir, "data", "faur_guide_index.json")
    faur_data = {}
    if os.path.exists(faur_path):
        with open(faur_path, "r", encoding="utf-8") as f:
            faur_data = json.load(f)

    faur_lexicon = faur_data.get("global_lexicon", {})
    all_faur_citations = faur_data.get("chapter_citations", {})

    # Extract segments
    segments: List[Dict[str, Any]] = []
    referenced_fn_ids = set()
    matched_faur_citations = {}

    for ch_name in chapters:
        ch_segs = aligner.get_chapter_segments(ch_name)
        for seg in ch_segs:
            segments.append({
                "segment_id": seg["segment_id"],
                "chapter_id": seg["chapter_id"],
                "english_v1": seg["english_v1"],
                "french": seg["french"],
                "judeo_arabic": seg["judeo_arabic"]
            })
            # Scan footnote callouts
            fn_matches = re.findall(r'\[\[fn:(\d+)\]\]', seg["english_v1"])
            for fn_id in fn_matches:
                referenced_fn_ids.add(fn_id)

        # Match Faur citations
        if ch_name in all_faur_citations:
            matched_faur_citations[ch_name] = all_faur_citations[ch_name]

    # Bundle co-referenced footnotes
    footnotes: Dict[str, str] = {}
    for fn_id in sorted(referenced_fn_ids, key=lambda x: int(x)):
        key_standard = f"fn.{fn_id}"
        if key_standard in all_footnotes:
            footnotes[key_standard] = all_footnotes[key_standard]
        elif fn_id in all_footnotes:
            footnotes[key_standard] = all_footnotes[fn_id]
        else:
            footnotes[key_standard] = ""

    packet_data = {
        "shard_id": shard_id,
        "chapters": chapters,
        "total_segments": len(segments),
        "total_footnotes": len(footnotes),
        "segments": segments,
        "footnotes": footnotes,
        "faur_context": {
            "global_lexicon": faur_lexicon,
            "chapter_citations": matched_faur_citations
        }
    }

    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, f"{shard_id}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(packet_data, f, ensure_ascii=False, indent=2)

    return out_file

def main():
    parser = argparse.ArgumentParser(description="Export Shard Packet for Review Waves")
    parser.add_argument("--shards", type=str, required=True, help="Comma-separated shard IDs")
    parser.add_argument("--out-dir", type=str, default="data/packets", help="Output directory")
    args = parser.parse_args()

    shard_list = [s.strip() for s in args.shards.split(",") if s.strip()]
    for sid in shard_list:
        path = export_shard_packet(sid, output_dir=args.out_dir)
        print(f"Exported shard packet: {path}")

if __name__ == "__main__":
    main()
