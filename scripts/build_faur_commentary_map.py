#!/usr/bin/env python3
"""
scripts/build_faur_commentary_map.py

Compiles the scholarly commentary map from José Faur's Homo Mysticus (1998)
into a production-grade 3-tier taxonomy mapped to Salomon Munk's Guide for the Perplexed.

3-Tier Taxonomy:
  - Tier 1 (Extended Exegesis): Multi-paragraph deep philosophical, structural, or political
    critiques of entire chapters, preserving Faur's verbatim text, HTML markup, and resolved footnotes.
  - Tier 2 (Philological & Conceptual Anchors): Targeted analyses of specific Hebrew / Judeo-Arabic
    terminology (e.g. rayyis, burhan, derekh, manthūra, Kalam) anchored to exact paragraph row keys.
  - Tier 3 (Incidental Proof-Texts): Footnote-only passing citations collated into chapter indices.

Output Artifacts:
  - data/faur_commentary_map.json
  - dist/data/faur_commentary_map.json
"""

import json
import os
import re
import shutil
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_DATA = os.path.join(WORKSPACE, "data")
DIST_DATA = os.path.join(WORKSPACE, "dist", "data")
CHUNKS_DIR = os.path.join(ROOT_DATA, "hm_chunks")
MANIFEST_PATH = os.path.join(CHUNKS_DIR, "manifest.json")
CHAPTERS_PATH = os.path.join(ROOT_DATA, "chapters.json")

ROMAN_PART_MAP: Dict[str, int] = {
    "I": 1, "II": 2, "III": 3,
    "1": 1, "2": 2, "3": 3,
    "ONE": 1, "TWO": 2, "THREE": 3
}

PART_TO_CHAPTER_NUM: Dict[str, Optional[int]] = {
    "Part One: Apophasis": 1,
    "Part Two: Imagination": 2,
    "Part Three: Cosmology": 3,
    "Part Four: Anthropology": 4,
    "Introduction": None,
    "Front Matter": None,
}


def format_faur_citation(part_title: str, section_title: str) -> Tuple[Optional[int], str]:
    """
    Formats the citation label and chapter number for José Faur's Homo Mysticus.
    If ch_num is not None: returns (ch_num, f"Homo Mysticus, Chapter {ch_num} - {section_title}")
    If part_title == "Introduction": returns (None, "Homo Mysticus, Introduction")
    Else: returns (None, f"Homo Mysticus, {section_title}")
    """
    ch_num = PART_TO_CHAPTER_NUM.get(part_title)
    if ch_num is not None:
        return (ch_num, f"Homo Mysticus, Chapter {ch_num} - {section_title}")
    if part_title == "Introduction":
        return (None, "Homo Mysticus, Introduction")
    return (None, f"Homo Mysticus, {section_title}")


# Verified page mappings for all 46 analytical sections in Homo Mysticus (text pages + note pages)
SECTION_PAGE_RANGES: Dict[str, List[int]] = {
    "chunk_00_preface": [9, 10, 11, 12, 183, 184],
    "chunk_01_introduction": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 184, 185, 186, 187, 188, 189, 190, 191, 192],
    "chunk_02_the_dialectics_of_apophatic_knowledge": [20, 21, 22, 192, 193],
    "chunk_03_apophasis_and_paradox": [22, 23, 24, 193],
    "chunk_04_the_acquisition_of_esoteric_instruction": [24, 25, 26, 27, 193, 194],
    "chunk_05_dissemination_of_esoteric_knowledge": [27, 28, 29, 194, 195],
    "chunk_06_hekhalot_literature_and_rabbinic_esoterics": [29, 30, 31, 32, 33, 195, 196],
    "chunk_07_subjectivity_and_the_esoteric_insight": [33, 34, 196],
    "chunk_08_the_resolution_of_unconcluded_subscripts": [34, 35, 196, 197],
    "chunk_09_descending_toward_the_inner_sanctuary": [35, 36, 37, 38, 197, 198],
    "chunk_10_the_realm_of_subjectivity": [38, 39, 40, 41, 42, 198, 199, 200],
    "chunk_11_at_the_crossroads": [42, 43, 44, 45, 46, 200, 201, 202, 203, 204, 205, 206, 209],
    "chunk_12_the_epistle_to_the_student_reader": [47, 48, 193, 194, 207],
    "chunk_13_the_guide_in_function_of_metatron": [48, 49, 50, 51, 52, 207, 208, 209],
    "chunk_14_deus_absconditus_homo_absconditus": [53, 54, 55, 56, 209, 210],
    "chunk_15_apophasis_and_imagination": [56, 57, 58, 206, 209, 210, 211],
    "chunk_16_transference_of_meaning": [58, 59, 60, 61, 62, 211, 212],
    "chunk_17_imagination_and_the_loss_of_individual_freedom": [62, 63, 64, 65, 196, 197, 198, 212, 213],
    "chunk_18_the_epistemology_of_reason_and_imagination": [65, 66, 67, 68, 69, 213, 214, 215],
    "chunk_19_prophecy_and_the_epistemology_of_the_creative_mind": [69, 70, 71, 72, 73, 74, 215, 216],
    "chunk_20_the_prophets_reflective_consciousness": [74, 75, 76, 77, 78, 79, 216, 217, 218],
    "chunk_21_anthropocentric_theology": [79, 80, 81, 82, 218, 219],
    "chunk_22_joining_the_angelical_beings_in_chorus_and_dance": [82, 83, 84, 85, 86, 87, 88, 219, 220],
    "chunk_23_creation_ex_nihilo": [89, 90, 91, 92, 93, 94, 220, 221],
    "chunk_24_in_search_of_the_ultimate_reality": [94, 95, 96, 97, 98, 196, 197, 221, 222, 223],
    "chunk_25_the_god_of_reason": [98, 99, 100, 101, 102, 223, 224, 225],
    "chunk_26_the_perimeters_of_aristotelian_rationality": [102, 103, 104, 105, 225, 226],
    "chunk_27_the_fault_with_aristotle": [105, 106, 107, 108, 109, 217, 218, 219, 226],
    "chunk_28_at_the_cutting_edge_of_reason": [109, 110, 111, 226, 227],
    "chunk_29_the_realm_of_the_probable": [111, 112, 113, 114, 115, 227, 228],
    "chunk_30_maase_bereshit": [115, 116, 117, 118, 119, 228, 229],
    "chunk_31_a_kind_of_madness": [119, 120, 121, 122, 123, 229, 230],
    "chunk_32_tilting_on_the_side_of_creation_ex_nihilo": [123, 124, 125, 126, 230, 231],
    "chunk_33_man_before_seth": [127, 128, 129, 130, 131, 231, 232],
    "chunk_34_traces_in_the_soul": [131, 132, 133, 134, 135, 136, 137, 232, 233, 234],
    "chunk_35_palingenesis_at_sinai": [137, 138, 139, 140, 141, 142, 234, 235, 236],
    "chunk_36_annulling_the_poison_of_the_primeval_snake": [142, 143, 144, 145, 146, 147, 236, 237],
    "chunk_37_witnessing_prophecy": [147, 148, 149, 150, 237, 238],
    "chunk_38_overcoming_the_pagan_past": [150, 151, 152, 153, 154, 155, 238, 239, 240],
    "chunk_39_the_archetypes_of_israel": [155, 156, 157, 158, 159, 160, 240, 241],
    "chunk_40_the_moment_of_mystical_illumination": [160, 161, 162, 163, 241, 242],
    "chunk_41_the_demarcation_of_cultures": [163, 164, 165, 166, 167, 168, 242, 243, 244],
    "chunk_42_knowing_by_virtue_of_perfection": [168, 169, 170, 171, 244, 245, 246],
    "chunk_43_training_for_intellectual_worship": [171, 172, 173, 246, 247],
    "chunk_44_up_and_down_jacobs_ladder": [173, 174, 175, 176, 177, 178, 247, 248],
    "chunk_45_at_gods_service": [178, 179, 180, 248],
}

# Mapping of chunks to primary Guide chapter exegesis targets (Tier 1)
CHUNK_TIER1_TARGETS: Dict[str, List[str]] = {
    "chunk_01_introduction": [
        "part-1---chapter-2",
        "part-1---chapter-51",
        "part-1---chapter-58",
        "part-3---chapter-54"
    ],
    "chunk_02_the_dialectics_of_apophatic_knowledge": [
        "part-1---chapter-58",
        "part-1---chapter-59",
        "part-1---chapter-31",
        "part-1---chapter-32"
    ],
    "chunk_03_apophasis_and_paradox": [
        "part-1---chapter-59",
        "maimonides-introduction-to-part-1"
    ],
    "chunk_04_the_acquisition_of_esoteric_instruction": [
        "maimonides-introduction-to-part-1",
        "part-1---chapter-33"
    ],
    "chunk_05_dissemination_of_esoteric_knowledge": [
        "maimonides-introduction-to-part-3",
        "maimonides-introduction-to-part-1"
    ],
    "chunk_06_hekhalot_literature_and_rabbinic_esoterics": [
        "part-3---chapter-51"
    ],
    "chunk_07_subjectivity_and_the_esoteric_insight": [
        "maimonides-introduction-to-part-3"
    ],
    "chunk_08_the_resolution_of_unconcluded_subscripts": [
        "maimonides-introduction-to-part-1",
        "maimonides-prefatory-remarks"
    ],
    "chunk_09_descending_toward_the_inner_sanctuary": [
        "maimonides-introduction-to-part-1",
        "part-3---chapter-51"
    ],
    "chunk_10_the_realm_of_subjectivity": [
        "part-1---chapter-32",
        "part-2---chapter-30"
    ],
    "chunk_11_at_the_crossroads": [
        "part-1---chapter-51",
        "part-1---chapter-59",
        "part-3---chapter-8",
        "part-1---chapter-70"
    ],
    "chunk_12_the_epistle_to_the_student_reader": [
        "maimonides-letter-to-r-joseph-son-of-judah",
        "part-1---chapter-35"
    ],
    "chunk_13_the_guide_in_function_of_metatron": [
        "part-2---chapter-29"
    ],
    "chunk_14_deus_absconditus_homo_absconditus": [
        "part-3---chapter-9",
        "part-1---chapter-21"
    ],
    "chunk_15_apophasis_and_imagination": [
        "part-1---chapter-51",
        "part-1---chapter-60",
        "part-1---chapter-26"
    ],
    "chunk_16_transference_of_meaning": [
        "part-1---chapter-2",
        "part-2---chapter-23"
    ],
    "chunk_17_imagination_and_the_loss_of_individual_freedom": [
        "part-1---chapter-73",
        "part-1---chapter-2"
    ],
    "chunk_18_the_epistemology_of_reason_and_imagination": [
        "part-1---chapter-73",
        "part-2---chapter-36"
    ],
    "chunk_19_prophecy_and_the_epistemology_of_the_creative_mind": [
        "part-2---chapter-36",
        "part-2---chapter-32"
    ],
    "chunk_20_the_prophets_reflective_consciousness": [
        "part-2---chapter-45",
        "part-2---chapter-43",
        "part-1---chapter-3"
    ],
    "chunk_21_anthropocentric_theology": [
        "part-1---chapter-32",
        "part-1---chapter-5"
    ],
    "chunk_22_joining_the_angelical_beings_in_chorus_and_dance": [
        "part-1---chapter-5",
        "part-2---chapter-38"
    ],
    "chunk_23_creation_ex_nihilo": [
        "part-2---chapter-13",
        "part-1---chapter-55",
        "part-1---chapter-56",
        "part-1---chapter-57",
        "part-1---chapter-58"
    ],
    "chunk_24_in_search_of_the_ultimate_reality": [
        "part-1---chapter-71"
    ],
    "chunk_25_the_god_of_reason": [
        "part-1---chapter-71",
        "part-2---chapter-1"
    ],
    "chunk_26_the_perimeters_of_aristotelian_rationality": [
        "part-1---chapter-31",
        "part-1---chapter-32",
        "part-2---chapter-19"
    ],
    "chunk_27_the_fault_with_aristotle": [
        "part-1---chapter-5",
        "maimonides-introduction-to-part-2"
    ],
    "chunk_28_at_the_cutting_edge_of_reason": [
        "part-2---chapter-23",
        "part-2---chapter-24"
    ],
    "chunk_29_the_realm_of_the_probable": [
        "part-2---chapter-18",
        "part-2---chapter-19",
        "part-2---chapter-20"
    ],
    "chunk_30_maase_bereshit": [
        "part-2---chapter-30",
        "part-2---chapter-17"
    ],
    "chunk_31_a_kind_of_madness": [
        "part-2---chapter-23",
        "part-1---chapter-32"
    ],
    "chunk_32_tilting_on_the_side_of_creation_ex_nihilo": [
        "part-2---chapter-13",
        "part-2---chapter-30"
    ],
    "chunk_33_man_before_seth": [
        "part-1---chapter-1",
        "part-1---chapter-7",
        "part-1---chapter-2"
    ],
    "chunk_34_traces_in_the_soul": [
        "part-3---chapter-32"
    ],
    "chunk_35_palingenesis_at_sinai": [
        "part-2---chapter-30",
        "part-2---chapter-33"
    ],
    "chunk_36_annulling_the_poison_of_the_primeval_snake": [
        "part-2---chapter-33",
        "part-2---chapter-34"
    ],
    "chunk_37_witnessing_prophecy": [
        "part-2---chapter-32",
        "part-2---chapter-33"
    ],
    "chunk_38_overcoming_the_pagan_past": [
        "part-3---chapter-32",
        "part-3---chapter-46"
    ],
    "chunk_39_the_archetypes_of_israel": [
        "part-3---chapter-24",
        "part-3---chapter-32"
    ],
    "chunk_40_the_moment_of_mystical_illumination": [
        "part-3---chapter-23",
        "part-3---chapter-7"
    ],
    "chunk_41_the_demarcation_of_cultures": [
        "part-3---chapter-27",
        "part-2---chapter-37",
        "part-2---chapter-38"
    ],
    "chunk_42_knowing_by_virtue_of_perfection": [
        "part-3---chapter-51",
        "part-3---chapter-54"
    ],
    "chunk_43_training_for_intellectual_worship": [
        "part-3---chapter-51"
    ],
    "chunk_44_up_and_down_jacobs_ladder": [
        "part-1---chapter-15",
        "part-3---chapter-54",
        "part-2---chapter-37"
    ],
    "chunk_45_at_gods_service": [
        "part-3---chapter-51",
        "part-3---chapter-30"
    ]
}


def load_valid_chapters() -> Dict[str, str]:
    """Loads all valid chapters from data/chapters.json and returns {slug: title}."""
    with open(CHAPTERS_PATH, "r", encoding="utf-8") as f:
        chapters = json.load(f)
    return {c["slug"]: c.get("title", c["slug"]) for c in chapters}


def load_all_chunks() -> Dict[str, Dict[str, Any]]:
    """Loads manifest and all 46 chunks from data/hm_chunks/."""
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    chunks: Dict[str, Dict[str, Any]] = {}
    for item in manifest["chunks"]:
        fname = item["file"]
        cpath = os.path.join(CHUNKS_DIR, fname)
        with open(cpath, "r", encoding="utf-8") as f:
            chunk_data = json.load(f)
            chunks[item["chunk_id"]] = chunk_data

    if len(chunks) != 46:
        raise AssertionError(f"Expected 46 chunks, loaded {len(chunks)}.")
    return chunks


def build_chunk_content_html(blocks: List[Dict[str, Any]]) -> str:
    """Concatenates chunk blocks into verbatim HTML preserving classes and callouts."""
    html_parts: List[str] = []
    for b in blocks:
        b_type = b.get("type", "paragraph")
        b_class = b.get("class", "book-paragraph" if b_type == "paragraph" else "book-blockquote")
        inner_html = b.get("html", "")
        if b_type == "blockquote":
            html_parts.append(f'<blockquote class="{b_class}">{inner_html}</blockquote>')
        else:
            html_parts.append(f'<p class="{b_class}">{inner_html}</p>')
    return "\n".join(html_parts)


def parse_footnote_citations(fn_text: str, valid_slugs: Set[str], last_part: Optional[int]) -> Tuple[List[Tuple[str, str]], Optional[int]]:
    """
    Parses a footnote text to identify authentic citations to Maimonides's Guide.
    Returns ([(slug, citation_str), ...], updated_last_part).
    """
    results: List[Tuple[str, str]] = []
    t_lower = fn_text.lower()

    # Ignore citations clearly to other texts with sections/chapters
    non_guide_prefixes = ["leone ebreo", "dialoghi", "golden doves", "wittgenstein", "descartes"]

    has_guide_indicator = any(w in t_lower for w in ["guide", "moreh", "dalālat"])
    has_ibid = "ibid" in t_lower

    # 1. sec/sect/part X, chap(s). Y[-Z]
    p1 = re.finditer(
        r"\b(?:sec\.|sect\.|part)\s*([1-3]|I{1,3}|one|two|three)\s*,\s*(?:chaps?\.|chapters?)\s*(\d+)(?:\s*[-–]\s*(\d+))?",
        fn_text, re.I
    )
    for m in p1:
        pre = fn_text[:m.start()].lower()
        if any(a in pre for a in non_guide_prefixes):
            continue
        p_num = ROMAN_PART_MAP.get(m.group(1).upper())
        c_start = int(m.group(2))
        c_end = int(m.group(3)) if m.group(3) else c_start
        if p_num and (1 <= p_num <= 3):
            last_part = p_num
            for c in range(c_start, c_end + 1):
                s = f"part-{p_num}---chapter-{c}"
                if s in valid_slugs:
                    results.append((s, m.group(0)))

    # 2. sec/sect/part X, Y[-Z] (e.g. sec. 1, 31-32)
    p2 = re.finditer(
        r"\b(?:sec\.|sect\.|part)\s*([1-3]|I{1,3}|one|two|three)\s*,\s*(\d+)(?:\s*[-–]\s*(\d+))?",
        fn_text, re.I
    )
    for m in p2:
        pre = fn_text[:m.start()].lower()
        if "chap" in pre[-10:] or any(a in pre for a in non_guide_prefixes):
            continue
        p_num = ROMAN_PART_MAP.get(m.group(1).upper())
        c_start = int(m.group(2))
        c_end = int(m.group(3)) if m.group(3) else c_start
        if p_num and (1 <= p_num <= 3):
            max_c = {1: 76, 2: 48, 3: 54}.get(p_num, 0)
            if c_start <= max_c:
                last_part = p_num
                for c in range(c_start, c_end + 1):
                    s = f"part-{p_num}---chapter-{c}"
                    if s in valid_slugs:
                        results.append((s, m.group(0)))

    # 3. Guide/Moreh ... (I|II|III|1|2|3):(\d+)
    p3 = re.finditer(
        r"\b(?:Guide|Moreh)[^.;\n]*?\b([1-3]|I{1,3})\s*[,:]\s*(\d+)(?:\s*[-–]\s*(\d+))?",
        fn_text, re.I
    )
    for m in p3:
        p_num = ROMAN_PART_MAP.get(m.group(1).upper())
        c_start = int(m.group(2))
        c_end = int(m.group(3)) if m.group(3) else c_start
        if p_num:
            last_part = p_num
            for c in range(c_start, c_end + 1):
                s = f"part-{p_num}---chapter-{c}"
                if s in valid_slugs:
                    results.append((s, m.group(0)))

    # 4. Ibid., chap. Y[-Z]
    if (has_ibid or has_guide_indicator) and last_part:
        p4 = re.finditer(r"\b(?:ibid\.?|guide)\s*,?\s*(?:chaps?\.|chapters?)\s*(\d+)(?:\s*[-–]\s*(\d+))?", fn_text, re.I)
        for m in p4:
            c_start = int(m.group(1))
            c_end = int(m.group(2)) if m.group(2) else c_start
            max_c = {1: 76, 2: 48, 3: 54}.get(last_part, 0)
            if c_start <= max_c:
                for c in range(c_start, c_end + 1):
                    s = f"part-{last_part}---chapter-{c}"
                    if s in valid_slugs:
                        results.append((s, m.group(0)))

    # 5. Introductory Epistle / Epistle
    if re.search(r"\b(?:Introductory Epistle|Epistle to R\. Joseph|Epistle to the student)\b", fn_text, re.I):
        m = re.search(r"\b(?:Introductory Epistle|Epistle to R\. Joseph|Epistle to the student)\b", fn_text, re.I)
        if m:
            results.append(("maimonides-letter-to-r-joseph-son-of-judah", m.group(0)))

    # 6. Prefatory Remarks
    if re.search(r"\bPrefatory Remarks\b", fn_text, re.I):
        m = re.search(r"\bPrefatory Remarks\b", fn_text, re.I)
        if m:
            results.append(("maimonides-prefatory-remarks", m.group(0)))

    # 7. Introductions
    if re.search(r"\b(?:Introduction to Part 1|Introduction to Part One|Guide\s*,\s*Introduction|(?:sec\.|sect\.|part)\s*(?:1|I|one)\s*,?\s*Introduction)\b", fn_text, re.I):
        m = re.search(r"\b(?:Introduction to Part 1|Introduction to Part One|Guide\s*,\s*Introduction|(?:sec\.|sect\.|part)\s*(?:1|I|one)\s*,?\s*Introduction)\b", fn_text, re.I)
        if m:
            results.append(("maimonides-introduction-to-part-1", m.group(0)))
    if re.search(r"\b(?:Introduction to Part 2|Introduction to Part Two|(?:sec\.|sect\.|part)\s*(?:2|II|two)\s*,?\s*Introduction)\b", fn_text, re.I):
        m = re.search(r"\b(?:Introduction to Part 2|Introduction to Part Two|(?:sec\.|sect\.|part)\s*(?:2|II|two)\s*,?\s*Introduction)\b", fn_text, re.I)
        if m:
            results.append(("maimonides-introduction-to-part-2", m.group(0)))
    if re.search(r"\b(?:Introduction to Part 3|Introduction to Part Three|(?:sec\.|sect\.|part)\s*(?:3|III|three)\s*,?\s*Introduction)\b", fn_text, re.I):
        m = re.search(r"\b(?:Introduction to Part 3|Introduction to Part Three|(?:sec\.|sect\.|part)\s*(?:3|III|three)\s*,?\s*Introduction)\b", fn_text, re.I)
        if m:
            results.append(("maimonides-introduction-to-part-3", m.group(0)))

    # Deduplicate preserving order
    dedup: List[Tuple[str, str]] = []
    seen: Set[str] = set()
    for s, cit in results:
        if s not in seen:
            seen.add(s)
            dedup.append((s, cit))
    return dedup, last_part


def build_tier2_glosses(chunks: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Constructs the definitive, authentic Tier 2 philological and conceptual anchors,
    strictly verified against row keys in data/*.json with Faur's authentic exegesis.
    """
    c27 = chunks["chunk_27_the_fault_with_aristotle"]
    c24 = chunks["chunk_24_in_search_of_the_ultimate_reality"]
    c12 = chunks["chunk_12_the_epistle_to_the_student_reader"]
    c11 = chunks["chunk_11_at_the_crossroads"]
    c33 = chunks["chunk_33_man_before_seth"]
    c02 = chunks["chunk_02_the_dialectics_of_apophatic_knowledge"]
    c03 = chunks["chunk_03_apophasis_and_paradox"]
    c26 = chunks["chunk_26_the_perimeters_of_aristotelian_rationality"]
    c23 = chunks["chunk_23_creation_ex_nihilo"]
    c30 = chunks["chunk_30_maase_bereshit"]
    c19 = chunks["chunk_19_prophecy_and_the_epistemology_of_the_creative_mind"]
    c37 = chunks["chunk_37_witnessing_prophecy"]
    c38 = chunks["chunk_38_overcoming_the_pagan_past"]
    c43 = chunks["chunk_43_training_for_intellectual_worship"]
    c42 = chunks["chunk_42_knowing_by_virtue_of_perfection"]
    c44 = chunks["chunk_44_up_and_down_jacobs_ladder"]
    c08 = chunks["chunk_08_the_resolution_of_unconcluded_subscripts"]

    fn_map = {}
    for c in chunks.values():
        for fn in c["footnotes"]:
            fn_map[fn["id"]] = fn["html"]

    def extract_fn_dict(fn_ids: List[str]) -> Dict[str, str]:
        return {fid: fn_map[fid] for fid in fn_ids if fid in fn_map}

    tier2_list: List[Dict[str, Any]] = [
        # 1. Mandatory Anchor: Aristotle as Rayyis
        {
            "id": "tier2_part-1---chapter-5_rayyis",
            "slug": "part-1---chapter-5",
            "row_key": "root.text.Part 1..4.0",
            "term": "rayyis",
            "original_script": "רייס אלפלאספה",
            "target_variant": "jrb",
            "anchor_label": "Aristotle as Rayyis (Political Prince of the Philosophers)",
            "faur_pages": [107, 108, 217, 218],
            "analysis_html": f"<p class='first-paragraph'>{c27['blocks'][6]['html']}</p>\n<blockquote class='book-blockquote'>{c27['blocks'][7]['html']}</blockquote>\n<p class='book-paragraph'>{c27['blocks'][8]['html']}</p>\n<p class='book-paragraph'>{c27['blocks'][9]['html']}</p>\n<p class='book-paragraph'>{c27['blocks'][10]['html']}</p>",
            "footnotes": extract_fn_dict(
                c27["blocks"][6]["footnote_ids"] +
                c27["blocks"][7]["footnote_ids"] +
                c27["blocks"][8]["footnote_ids"] +
                c27["blocks"][9]["footnote_ids"] +
                c27["blocks"][10]["footnote_ids"]
            )
        },
        # 2. Aristotle as the Aṣīle of Israel (Remediated: Row 4.3 with authentic verbatim script)
        {
            "id": "tier2_part-1---chapter-5_asile",
            "slug": "part-1---chapter-5",
            "row_key": "root.text.Part 1..4.3",
            "term": "aṣīle",
            "original_script": "אצילי בני ישראל",
            "target_variant": "jrb",
            "anchor_label": "Aristotle as the Aṣīle (Nobles of Israel)",
            "faur_pages": [108, 109, 218],
            "analysis_html": f"<p class='book-paragraph'>{c27['blocks'][10]['html']}</p>",
            "footnotes": extract_fn_dict(c27["blocks"][10]["footnote_ids"])
        },
        # 3. Mandatory Anchor: Kalam & Christian Church Fathers (Remediated: authentic Greek/Syrian scholars)
        {
            "id": "tier2_part-1---chapter-71_kalam_church_fathers",
            "slug": "part-1---chapter-71",
            "row_key": "root.text.Part 1..70.3",
            "term": "Kalam & Christian Church Fathers",
            "original_script": "ראוא עלמא תלך אלאעצאר מן אליונאן ואלסריאן",
            "target_variant": "jrb",
            "anchor_label": "Christian Patristic Origins of Kalam Apologetics",
            "faur_pages": [94, 95, 196, 197, 221, 222],
            "analysis_html": f"<p class='book-paragraph'>{c24['blocks'][2]['html']}</p>\n<p class='book-paragraph'>{c24['blocks'][3]['html']}</p>\n<blockquote class='book-blockquote'>{c24['blocks'][6]['html']}</blockquote>",
            "footnotes": extract_fn_dict(
                c24["blocks"][2]["footnote_ids"] +
                c24["blocks"][3]["footnote_ids"] +
                c24["blocks"][6]["footnote_ids"]
            )
        },
        # 4. Mandatory Anchor: Mutakallimūn Methodology (Remediated: authentic method phrase)
        {
            "id": "tier2_part-1---chapter-71_mutakallimun_methodology",
            "slug": "part-1---chapter-71",
            "row_key": "root.text.Part 1..70.7",
            "term": "Mutakallimūn Methodology",
            "original_script": "טריק אלמתכלמין כלהם טריקא ואחדא באלנוע",
            "target_variant": "jrb",
            "anchor_label": "Mutakallimūn Methodology: Imagination Subjugating Reality",
            "faur_pages": [95, 96, 197, 222],
            "analysis_html": f"<p class='book-paragraph'>{c24['blocks'][5]['html']}</p>\n<p class='book-paragraph'>{c24['blocks'][7]['html']}</p>",
            "footnotes": extract_fn_dict(
                c24["blocks"][5]["footnote_ids"] +
                c24["blocks"][7]["footnote_ids"]
            )
        },
        # 5. Kalam Repugnance to Maimonides's Soul (Remediated: authentic soul revulsion phrase)
        {
            "id": "tier2_part-1---chapter-71_kalam_repugnance",
            "slug": "part-1---chapter-71",
            "row_key": "root.text.Part 1..70.8",
            "term": "burhān vs Kalam Dialectic",
            "original_script": "נפרת נפסי מנהא נפורא עט'ימא ג'דא",
            "target_variant": "jrb",
            "anchor_label": "Maimonides's Epistemic Repugnance to Dialectical Apologetics",
            "faur_pages": [96, 97, 222, 223],
            "analysis_html": f"<p class='book-paragraph'>{c24['blocks'][8]['html']}</p>\n<p class='book-paragraph'>{c24['blocks'][9]['html']}</p>\n<p class='book-paragraph'>{c24['blocks'][10]['html']}</p>",
            "footnotes": extract_fn_dict(
                c24["blocks"][8]["footnote_ids"] +
                c24["blocks"][9]["footnote_ids"] +
                c24["blocks"][10]["footnote_ids"]
            )
        },
        # 6. Mandatory Anchor: Manthūra (Scattered Chapters)
        {
            "id": "tier2_maimonides-letter-to-r-joseph-son-of-judah_manthura",
            "slug": "maimonides-letter-to-r-joseph-son-of-judah",
            "row_key": "root.text.Letter to R Joseph son of Judah.3",
            "term": "detached chapters (manthūra)",
            "original_script": "פרקים פרקים",
            "target_variant": "makbili",
            "anchor_label": "Manthūra (Scattered Chapters / Esoteric Pedagogy)",
            "faur_pages": [47, 48, 193, 194, 207],
            "analysis_html": f"<p class='first-paragraph'>{c12['blocks'][0]['html']}</p>\n<p class='book-paragraph'>{c12['blocks'][1]['html']}</p>\n<p class='book-paragraph'>{c12['blocks'][3]['html']}</p>",
            "footnotes": extract_fn_dict(
                c12["blocks"][0]["footnote_ids"] +
                c12["blocks"][1]["footnote_ids"] +
                c12["blocks"][3]["footnote_ids"]
            )
        },
        # 7. Mandatory Anchor: al-Derekh as Divine Attribute
        {
            "id": "tier2_part-1---chapter-51_al_derekh",
            "slug": "part-1---chapter-51",
            "row_key": "root.text.Part 1..50.5",
            "term": "al-derekh",
            "original_script": "וקום תרפעוא ען הד'א אלדרך ונפוא אלג'סם ואבקוא אלצפאת",
            "target_variant": "jrb",
            "anchor_label": "al-Derekh (Rabbinic Code-Term for Divine Attributes)",
            "faur_pages": [45, 46, 206, 209],
            "analysis_html": f"<p class='first-paragraph'>{c11['blocks'][8]['html']}</p>",
            "footnotes": extract_fn_dict(c11["blocks"][8]["footnote_ids"])
        },
        # 8. lil-Derekh as Antinomian Path in Part 3 Chapter 8
        {
            "id": "tier2_part-3---chapter-8_lil_derekh",
            "slug": "part-3---chapter-8",
            "row_key": "root.text.Part 3..7.5",
            "term": "lil-derekh",
            "original_script": "לא ללאנחטאט ללדרך אלאספל",
            "target_variant": "jrb",
            "anchor_label": "lil-Derekh (Rabbinic Code-Term for the Antinomian Path)",
            "faur_pages": [45, 46, 206],
            "analysis_html": f"<p class='book-paragraph'>{c11['blocks'][12]['html']}</p>\n<blockquote class='book-blockquote'>{c11['blocks'][13]['html']}</blockquote>",
            "footnotes": extract_fn_dict(
                c11["blocks"][12]["footnote_ids"] +
                c11["blocks"][13]["footnote_ids"]
            )
        },
        # 9. Tzelem vs To'ar in Part 1 Chapter 1
        {
            "id": "tier2_part-1---chapter-1_tzelem",
            "slug": "part-1---chapter-1",
            "row_key": "root.text.Part 1..0.1",
            "term": "tzelem",
            "original_script": "צלם ודמות",
            "target_variant": "jrb",
            "anchor_label": "Tzelem Elohim: Intellectual Appurtenance vs Physical Form",
            "faur_pages": [127, 128, 231],
            "analysis_html": f"<p class='first-paragraph'>{c33['blocks'][0]['html']}</p>\n<p class='book-paragraph'>{c33['blocks'][1]['html']}</p>\n<p class='book-paragraph'>{c33['blocks'][2]['html']}</p>",
            "footnotes": extract_fn_dict(
                c33["blocks"][0]["footnote_ids"] +
                c33["blocks"][1]["footnote_ids"] +
                c33["blocks"][2]["footnote_ids"]
            )
        },
        # 10. Sons of Adam Before Seth (Sub-Human Progeny)
        {
            "id": "tier2_part-1---chapter-7_sons_before_seth",
            "slug": "part-1---chapter-7",
            "row_key": "root.text.Part 1..6.2",
            "term": "bi-dmutho ke-tzalmo",
            "original_script": "בדמותו כצלמו",
            "target_variant": "jrb",
            "anchor_label": "Sub-Human Humanity Before Seth: Loss of Tzelem",
            "faur_pages": [128, 129, 231, 232],
            "analysis_html": f"<p class='first-paragraph'>{c33['blocks'][4]['html']}</p>\n<p class='book-paragraph'>{c33['blocks'][5]['html']}</p>",
            "footnotes": extract_fn_dict(
                c33["blocks"][4]["footnote_ids"] +
                c33["blocks"][5]["footnote_ids"]
            )
        },
        # 11. Burhān (Demonstration vs Faith in Negative Attributes)
        {
            "id": "tier2_part-1---chapter-58_burhan",
            "slug": "part-1---chapter-58",
            "row_key": "root.text.Part 1..57.4",
            "term": "burhān",
            "original_script": "תברהן",
            "target_variant": "jrb",
            "anchor_label": "Burhān: Two-Stage Demonstration in Negative Theology",
            "faur_pages": [20, 21, 192, 193],
            "analysis_html": f"<p class='first-paragraph'>{c02['blocks'][5]['html']}</p>\n<p class='book-paragraph'>{c02['blocks'][6]['html']}</p>",
            "footnotes": extract_fn_dict(
                c02["blocks"][5]["footnote_ids"] +
                c02["blocks"][6]["footnote_ids"]
            )
        },
        # 12. Dumya Tehilla (Remediated: Row 58.4 containing authentic Psalm 65:2 verse)
        {
            "id": "tier2_part-1---chapter-59_dumya_tehilla",
            "slug": "part-1---chapter-59",
            "row_key": "root.text.Part 1..58.4",
            "term": "dumya tehilla",
            "original_script": "לך דמיה תהלה",
            "target_variant": "jrb",
            "anchor_label": "Dumya Tehilla: Silence as the Ultimate Form of Worship",
            "faur_pages": [22, 23, 193],
            "analysis_html": f"<p class='book-paragraph'>{c03['blocks'][1]['html']}</p>\n<p class='first-paragraph'>{c03['blocks'][3]['html']}</p>",
            "footnotes": extract_fn_dict(
                c03["blocks"][1]["footnote_ids"] +
                c03["blocks"][3]["footnote_ids"]
            )
        },
        # 13. Limits of Human Reason (Remediated: authentic intellect capacity phrase)
        {
            "id": "tier2_part-1---chapter-31_limits_of_reason",
            "slug": "part-1---chapter-31",
            "row_key": "root.text.Part 1..30.0",
            "term": "ḥadd al-'aql",
            "original_script": "ללעקל אלאנסאני מדארך פי קותה וטביעתה אן ידרכהא",
            "target_variant": "jrb",
            "anchor_label": "Limits of Reason: The Demarcation of Human Understanding",
            "faur_pages": [102, 103, 225],
            "analysis_html": f"<p class='first-paragraph'>{c26['blocks'][0]['html']}</p>\n<p class='book-paragraph'>{c26['blocks'][1]['html']}</p>",
            "footnotes": extract_fn_dict(
                c26["blocks"][0]["footnote_ids"] +
                c26["blocks"][1]["footnote_ids"]
            )
        },
        # 14. Intellectual Vertigo (taḥayyur)
        {
            "id": "tier2_part-1---chapter-32_tahayyur",
            "slug": "part-1---chapter-32",
            "row_key": "root.text.Part 1..31.0",
            "term": "taḥayyur",
            "original_script": "יעתרי פי אלאדראכאת אלעקליה",
            "target_variant": "jrb",
            "anchor_label": "Intellectual Vertigo: Epistemic Hazard of Transgressing Limits",
            "faur_pages": [104, 105, 225, 226],
            "analysis_html": f"<p class='book-paragraph'>{c26['blocks'][3]['html']}</p>\n<p class='book-paragraph'>{c26['blocks'][4]['html']}</p>",
            "footnotes": extract_fn_dict(
                c26["blocks"][3]["footnote_ids"] +
                c26["blocks"][4]["footnote_ids"]
            )
        },
        # 15. Three Views on Creation
        {
            "id": "tier2_part-2---chapter-13_creation_theses",
            "slug": "part-2---chapter-13",
            "row_key": "root.text.Part 2..12.1",
            "term": "khalq min lā shay'",
            "original_script": "אלראי אלאול",
            "target_variant": "jrb",
            "anchor_label": "Creation ex Nihilo: Rabbinic vs Platonic vs Aristotelian Theses",
            "faur_pages": [89, 90, 220],
            "analysis_html": f"<p class='first-paragraph'>{c23['blocks'][0]['html']}</p>\n<p class='book-paragraph'>{c23['blocks'][1]['html']}</p>",
            "footnotes": extract_fn_dict(
                c23["blocks"][0]["footnote_ids"] +
                c23["blocks"][1]["footnote_ids"]
            )
        },
        # 16. Ma‘aśe Bereshit as Natural Science (Remediated: Row 29.16 with authentic Rabbinic dictum)
        {
            "id": "tier2_part-2---chapter-30_maase_bereshit",
            "slug": "part-2---chapter-30",
            "row_key": "root.text.Part 2..29.16",
            "term": "ma'ase bereshit",
            "original_script": "כל מעשה בראשית לקומתן נבראו",
            "target_variant": "jrb",
            "anchor_label": "Ma‘aśe Bereshit: Maimonides's Esoteric Cosmological Synthesis",
            "faur_pages": [115, 116, 228],
            "analysis_html": f"<p class='first-paragraph'>{c30['blocks'][0]['html']}</p>\n<p class='book-paragraph'>{c30['blocks'][1]['html']}</p>",
            "footnotes": extract_fn_dict(
                c30["blocks"][0]["footnote_ids"] +
                c30["blocks"][1]["footnote_ids"]
            )
        },
        # 17. Prophecy as Overflow via Active Intellect (Remediated: authentic overflow phrase)
        {
            "id": "tier2_part-2---chapter-36_fayd",
            "slug": "part-2---chapter-36",
            "row_key": "root.text.Part 2..35.0",
            "term": "fayḍ",
            "original_script": "פיץ' יפיץ' מן אללה",
            "target_variant": "jrb",
            "anchor_label": "Prophetic Overflow (Fayḍ): Creative Imagination Subordinate to Intellect",
            "faur_pages": [69, 70, 215],
            "analysis_html": f"<p class='first-paragraph'>{c19['blocks'][0]['html']}</p>\n<p class='book-paragraph'>{c19['blocks'][1]['html']}</p>",
            "footnotes": extract_fn_dict(
                c19["blocks"][0]["footnote_ids"] +
                c19["blocks"][1]["footnote_ids"]
            )
        },
        # 18. Sinai Theophany (Collective Historical Verification)
        {
            "id": "tier2_part-2---chapter-33_sinai_verification",
            "slug": "part-2---chapter-33",
            "row_key": "root.text.Part 2..32.0",
            "term": "ma'amad har sinai",
            "original_script": "מעמד הר סיני",
            "target_variant": "jrb",
            "anchor_label": "Theophany at Sinai: Collective Historical Verification",
            "faur_pages": [147, 148, 237],
            "analysis_html": f"<p class='first-paragraph'>{c37['blocks'][0]['html']}</p>\n<p class='book-paragraph'>{c37['blocks'][1]['html']}</p>",
            "footnotes": extract_fn_dict(
                c37["blocks"][0]["footnote_ids"] +
                c37["blocks"][1]["footnote_ids"]
            )
        },
        # 19. Luṭf (Divine Subtlety in Legislation) (Remediated: authentic subtlety/providence phrase)
        {
            "id": "tier2_part-3---chapter-32_lutf",
            "slug": "part-3---chapter-32",
            "row_key": "root.text.Part 3..31.0",
            "term": "luṭf",
            "original_script": "תלטף אלאלאה וחכמתה",
            "target_variant": "jrb",
            "anchor_label": "Luṭf (Divine Subtlety): Historical Accommodation in Sacrificial Cult",
            "faur_pages": [150, 151, 238],
            "analysis_html": f"<p class='first-paragraph'>{c38['blocks'][0]['html']}</p>\n<p class='book-paragraph'>{c38['blocks'][1]['html']}</p>",
            "footnotes": extract_fn_dict(
                c38["blocks"][0]["footnote_ids"] +
                c38["blocks"][1]["footnote_ids"]
            )
        },
        # 20. The Palace Parable (Remediated: Row 50.1 with authentic opening of the parable)
        {
            "id": "tier2_part-3---chapter-51_palace_parable",
            "slug": "part-3---chapter-51",
            "row_key": "root.text.Part 3..50.1",
            "term": "al-sultān fi darihi",
            "original_script": "אן אלסלטאן פי קצרה",
            "target_variant": "jrb",
            "anchor_label": "The Palace Parable: Concentric Degrees of Proximity to the Ruler",
            "faur_pages": [171, 172, 246],
            "analysis_html": f"<p class='first-paragraph'>{c43['blocks'][0]['html']}</p>\n<p class='book-paragraph'>{c43['blocks'][1]['html']}</p>",
            "footnotes": extract_fn_dict(
                c43["blocks"][0]["footnote_ids"] +
                c43["blocks"][1]["footnote_ids"]
            )
        },
        # 21. The First Idea (Intellectual Worship)
        {
            "id": "tier2_part-3---chapter-51_first_idea",
            "slug": "part-3---chapter-51",
            "row_key": "root.text.Part 3..50.9",
            "term": "First Idea",
            "original_script": "אלפכרה",
            "target_variant": "jrb",
            "anchor_label": "The First Idea: Intellectual Worship in the Inner Sanctuary",
            "faur_pages": [170, 171, 246],
            "analysis_html": f"<p class='book-paragraph'>{c42['blocks'][4]['html']}</p>\n<p class='book-paragraph'>{c42['blocks'][5]['html']}</p>",
            "footnotes": extract_fn_dict(
                c42["blocks"][4]["footnote_ids"] +
                c42["blocks"][5]["footnote_ids"]
            )
        },
        # 22. The Four Human Perfections (Remediated: Row 53.3 with authentic 4 perfections introduction)
        {
            "id": "tier2_part-3---chapter-54_four_perfections",
            "slug": "part-3---chapter-54",
            "row_key": "root.text.Part 3..53.3",
            "term": "al-kamālāt al-arba'",
            "original_script": "אלכמאלאת אלמוג'ודה ללאנסאן ארבעה אנואע",
            "target_variant": "jrb",
            "anchor_label": "The Four Human Perfections: From Possessions to Hesed and Mishpat",
            "faur_pages": [168, 169, 244],
            "analysis_html": f"<p class='first-paragraph'>{c42['blocks'][0]['html']}</p>\n<p class='book-paragraph'>{c42['blocks'][1]['html']}</p>",
            "footnotes": extract_fn_dict(
                c42["blocks"][0]["footnote_ids"] +
                c42["blocks"][1]["footnote_ids"]
            )
        },
        # 23. Jacob's Ladder (Ascent and Descent)
        {
            "id": "tier2_part-1---chapter-15_jacobs_ladder",
            "slug": "part-1---chapter-15",
            "row_key": "root.text.Part 1..14.2",
            "term": "sullam ya'aqov",
            "original_script": "סלם",
            "target_variant": "jrb",
            "anchor_label": "Jacob's Ladder: Epistemic Ascent and Civic Political Descent",
            "faur_pages": [173, 174, 247],
            "analysis_html": f"<p class='first-paragraph'>{c44['blocks'][0]['html']}</p>\n<p class='book-paragraph'>{c44['blocks'][1]['html']}</p>",
            "footnotes": extract_fn_dict(
                c44["blocks"][0]["footnote_ids"] +
                c44["blocks"][1]["footnote_ids"]
            )
        },
        # 24. Lightning Flashes & Seven Causes of Contradiction
        {
            "id": "tier2_maimonides-prefatory-remarks_lightning",
            "slug": "maimonides-prefatory-remarks",
            "row_key": "root.text.Prefatory Remarks.10",
            "term": "al-burūq",
            "original_script": "ברק",
            "target_variant": "jrb",
            "anchor_label": "The Lightning Flashes: Intermittent Intuition and Esoteric Concealment",
            "faur_pages": [34, 35, 196, 197],
            "analysis_html": f"<p class='first-paragraph'>{c08['blocks'][0]['html']}</p>",
            "footnotes": extract_fn_dict(c08["blocks"][0]["footnote_ids"])
        }
    ]

    return tier2_list


def build_commentary_map() -> Dict[str, Any]:
    """Compiles the master commentary map adhering to the survey_explorer_2 §3 schema."""
    valid_chapters = load_valid_chapters()
    valid_slugs_set = set(valid_chapters.keys())
    chunks = load_all_chunks()

    # Pre-load chapter rows to verify row keys
    chapter_row_keys: Dict[str, Set[str]] = {}
    for slug in valid_slugs_set:
        cpath = os.path.join(ROOT_DATA, f"{slug}.json")
        if os.path.exists(cpath):
            with open(cpath, "r", encoding="utf-8") as f:
                cdata = json.load(f)
                chapter_row_keys[slug] = set(r["key"] for r in cdata.get("rows", []))
        else:
            chapter_row_keys[slug] = set()

    chapters_dict: Dict[str, Dict[str, Any]] = {}
    tier2_by_row_key: Dict[str, List[Dict[str, Any]]] = {}

    def get_or_create_chapter(slug: str) -> Dict[str, Any]:
        if slug not in chapters_dict:
            chapters_dict[slug] = {
                "slug": slug,
                "title": valid_chapters.get(slug, slug),
                "tier1": [],
                "tier2": [],
                "tier3": []
            }
        return chapters_dict[slug]

    # --- Phase 1: Compile Tier 1 (Extended Exegesis) ---
    total_tier1 = 0
    for chunk_id, target_slugs in CHUNK_TIER1_TARGETS.items():
        chunk = chunks[chunk_id]
        content_html = build_chunk_content_html(chunk["blocks"])
        footnotes_dict = {fn["id"]: fn["html"] for fn in chunk["footnotes"]}
        pages = SECTION_PAGE_RANGES.get(chunk_id, [chunk["chunk_index"] + 1])
        first_text = chunk["blocks"][0]["text"] if chunk["blocks"] else ""
        faur_ch_num, citation_str = format_faur_citation(chunk["part_title"], chunk["title"])

        for slug in target_slugs:
            if slug not in valid_slugs_set:
                print(f"Warning: Skipping invalid slug {slug} in Tier 1")
                continue
            ch_obj = get_or_create_chapter(slug)
            tier1_entry = {
                "id": f"tier1_{chunk_id}_{slug}",
                "chunk_id": chunk_id,
                "slug": slug,
                "section_title": chunk["title"],
                "part_title": chunk["part_title"],
                "faur_chapter": faur_ch_num,
                "citation": citation_str,
                "faur_pages": pages,
                "thesis_summary": first_text,
                "content_html": content_html,
                "footnotes": footnotes_dict,
                "key_terms": []
            }
            ch_obj["tier1"].append(tier1_entry)
            total_tier1 += 1

    # --- Phase 2: Compile Tier 2 (Philological & Conceptual Anchors) ---
    tier2_entries = build_tier2_glosses(chunks)
    total_tier2 = len(tier2_entries)

    for entry in tier2_entries:
        slug = entry["slug"]
        row_key = entry["row_key"]

        # Invariant: verify row key exists in target chapter
        if slug not in chapter_row_keys or row_key not in chapter_row_keys[slug]:
            raise AssertionError(f"Tier 2 row_key '{row_key}' not found in data/{slug}.json!")

        ch_obj = get_or_create_chapter(slug)

        # Chapter-level Tier 2 entry
        ch_tier2_item = {
            "id": entry["id"],
            "row_key": row_key,
            "term": entry["term"],
            "original_script": entry["original_script"],
            "target_variant": entry["target_variant"],
            "anchor_label": entry["anchor_label"],
            "faur_pages": entry["faur_pages"],
            "analysis_html": entry["analysis_html"],
            "footnotes": entry["footnotes"]
        }
        ch_obj["tier2"].append(ch_tier2_item)

        # Reverse lookup by row key for O(1) reader.js rendering
        if row_key not in tier2_by_row_key:
            tier2_by_row_key[row_key] = []

        rev_item = {
            "id": entry["id"],
            "slug": slug,
            "term": entry["term"],
            "original_script": entry["original_script"],
            "target_variant": entry["target_variant"],
            "anchor_label": entry["anchor_label"],
            "faur_pages": entry["faur_pages"],
            "analysis_html": entry["analysis_html"],
            "footnotes": entry["footnotes"]
        }
        tier2_by_row_key[row_key].append(rev_item)

    # Sort Tier 1 chunks first so numbered chapters precede Introduction deterministically
    for ch_obj in chapters_dict.values():
        ch_obj["tier1"].sort(key=lambda e: (0 if e["faur_chapter"] is not None else 1, e["chunk_id"]))

    # Populate key_terms on matching Tier 1 chunk from Tier 2 entries (using maximum page overlap)
    for ch_obj in chapters_dict.values():
        for entry in ch_obj["tier2"]:
            entry_pages = set(entry.get("faur_pages", []))
            matching_t1 = None
            if ch_obj["tier1"]:
                best_t1 = None
                best_overlap = 0
                for t1 in ch_obj["tier1"]:
                    overlap = len(entry_pages.intersection(set(t1.get("faur_pages", []))))
                    if overlap > best_overlap:
                        best_overlap = overlap
                        best_t1 = t1
                matching_t1 = best_t1 if best_overlap > 0 else ch_obj["tier1"][0]

            if matching_t1 is not None:
                term_obj = {
                    "term": entry["term"],
                    "original_script": entry["original_script"],
                    "anchor_label": entry["anchor_label"]
                }
                if term_obj not in matching_t1["key_terms"]:
                    matching_t1["key_terms"].append(term_obj)

    # --- Phase 3: Compile Tier 3 (Incidental Proof-Texts) ---
    total_tier3 = 0
    last_p: Optional[int] = None
    for chunk in chunks.values():
        chunk_id = chunk["chunk_id"]
        sec_title = chunk["title"]
        pages = SECTION_PAGE_RANGES.get(chunk_id, [1])
        base_page = pages[0]

        for fn in chunk["footnotes"]:
            fn_id = fn["id"]
            fn_text = fn["text"]
            citations, last_p = parse_footnote_citations(fn_text, valid_slugs_set, last_p)

            for target_slug, cit_str in citations:
                ch_obj = get_or_create_chapter(target_slug)
                tier3_entry = {
                    "id": f"tier3_{fn_id}_{target_slug}",
                    "source_footnote_id": fn_id,
                    "faur_section": sec_title,
                    "faur_page": base_page,
                    "citation_text": fn_text
                }
                ch_obj["tier3"].append(tier3_entry)
                total_tier3 += 1

    # --- Phase 4: Construct Master Commentary Map ---
    commentary_map = {
        "metadata": {
            "version": "1.0",
            "source": "José Faur, Homo Mysticus: A Guide to Maimonides's Guide for the Perplexed (Syracuse University Press, 1998)",
            "total_chunks_parsed": len(chunks),
            "total_tier1": total_tier1,
            "total_tier2": total_tier2,
            "total_tier3": total_tier3,
            "chapters_mapped": len(chapters_dict)
        },
        "chapters": chapters_dict,
        "tier2_by_row_key": tier2_by_row_key
    }

    return commentary_map


def main() -> None:
    print("=" * 70)
    print("Homo Mysticus Commentary Map Compiler (Milestone 2)")
    print("=" * 70)

    commentary_map = build_commentary_map()
    meta = commentary_map["metadata"]
    print(f"✓ Parsed {meta['total_chunks_parsed']} chunks from {CHUNKS_DIR}")
    print(f"✓ Compiled {meta['total_tier1']} Tier 1 extended exegeses")
    print(f"✓ Compiled {meta['total_tier2']} Tier 2 philological anchors across {len(commentary_map['tier2_by_row_key'])} unique row keys")
    print(f"✓ Compiled {meta['total_tier3']} Tier 3 incidental proof-texts")
    print(f"✓ Successfully mapped {meta['chapters_mapped']} Guide chapters")

    # Serialize to data/faur_commentary_map.json
    root_out = os.path.join(ROOT_DATA, "faur_commentary_map.json")
    dist_out = os.path.join(DIST_DATA, "faur_commentary_map.json")

    os.makedirs(ROOT_DATA, exist_ok=True)
    os.makedirs(DIST_DATA, exist_ok=True)

    with open(root_out, "w", encoding="utf-8") as f:
        json.dump(commentary_map, f, ensure_ascii=False, indent=2)
    print(f"✓ Serialized root dataset to: {root_out}")

    shutil.copy2(root_out, dist_out)
    print(f"✓ Mirror-synchronized dist dataset to: {dist_out}")

    # Byte identity verification
    with open(root_out, "rb") as f1, open(dist_out, "rb") as f2:
        assert f1.read() == f2.read(), "FATAL: Root and dist datasets are not byte-identical!"
    print("✓ Verified byte identity between root and dist datasets.")

    print("\n" + "=" * 70)
    print("Commentary Map Compilation Completed Successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
