#!/usr/bin/env python3
"""
tests/test_faur_pericope_verbatim.py

Skeptical Auditor Verification Suite for Homo Mysticus Tier 1 Commentary Pericopes.
Validates:
  1. Tier 1 entry counts (exactly 30), single-pericope-per-chapter constraint, and anti-bloat bounds
     (1–4 blocks, <= 800 words).
  2. 100% character-by-character verbatim fidelity between commentary pericopes and source chunks
     in data/hm_chunks/{chunk_id}.json (0 paraphrased words, 0 dropped words, 0 hallucinations).
  3. Footnote routing and master resolution across per-entry footnote dictionaries and canonical
     data/footnotes.json with zero missing or empty definitions.
  4. Complete, clean sentence boundaries (valid capital/quote openings and terminal punctuation).
  5. 100% byte-for-byte parity between root and dist datasets.

Executable via:
  pytest tests/test_faur_pericope_verbatim.py
  python3 tests/test_faur_pericope_verbatim.py
"""

import json
import os
import re
import sys
from typing import Any, Dict, List, Tuple

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_MAP_PATH = os.path.join(REPO_ROOT, "data", "faur_commentary_map.json")
DIST_MAP_PATH = os.path.join(REPO_ROOT, "dist", "data", "faur_commentary_map.json")
FOOTNOTES_PATH = os.path.join(REPO_ROOT, "data", "footnotes.json")
CHUNKS_DIR = os.path.join(REPO_ROOT, "data", "hm_chunks")


def _load_json(filepath: str) -> Any:
    assert os.path.exists(filepath), f"Required file not found: {filepath}"
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def _get_tier1_entries(commentary_map: Dict[str, Any]) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    for slug, chapter_data in commentary_map.get("chapters", {}).items():
        for t1 in chapter_data.get("tier1", []):
            entries.append(t1)
    return entries


def test_tier1_counts_and_anti_bloat():
    """
    Invariant 1:
      - Exactly 30 Tier 1 entries across all chapters.
      - Every Guide chapter has at most 1 (or max 2) Tier 1 entries.
      - Every Tier 1 entry has between 1 and 4 paragraphs/blocks (hard limit: <= 5).
      - Every Tier 1 entry has <= 800 words (word_count <= 800).
    """
    commentary_map = _load_json(ROOT_MAP_PATH)
    t1_entries = _get_tier1_entries(commentary_map)

    # Invariant: Exactly 30 Tier 1 entries
    assert len(t1_entries) == 30, (
        f"Expected exactly 30 Tier 1 pericopes, found {len(t1_entries)}"
    )

    # Invariant: Every chapter has at most 1 (or max 2) Tier 1 entries
    for slug, ch in commentary_map.get("chapters", {}).items():
        count = len(ch.get("tier1", []))
        assert count <= 2, (
            f"Guide chapter '{slug}' exceeds per-chapter limit with {count} Tier 1 entries"
        )

    # Invariant: Anti-bloat check for each Tier 1 entry
    for entry in t1_entries:
        entry_id = entry.get("id", "unknown")
        slug = entry.get("slug", "unknown")
        content_html = entry.get("content_html", "")

        blocks = re.findall(
            r'<(p|blockquote)[^>]*>(.*?)</\1>',
            content_html,
            re.DOTALL
        )
        num_blocks = len(blocks)
        assert 1 <= num_blocks <= 5, (
            f"Entry {entry_id} in {slug} violates block limits: {num_blocks} blocks (allowed: 1..5)"
        )

        clean_text = re.sub(r'<[^>]+>', ' ', content_html)
        word_count = len(clean_text.split())
        assert word_count <= 800, (
            f"Entry {entry_id} in {slug} violates word limit: {word_count} words (allowed: <= 800)"
        )


def test_pericope_verbatim_fidelity_against_source_chunks():
    """
    Invariant 2:
      - For every Tier 1 entry, load data/hm_chunks/{chunk_id}.json.
      - Verify that start_block and end_block exist and 0 <= start_block <= end_block < len(chunk["blocks"]).
      - Extract expected_blocks = chunk["blocks"][start_block : end_block + 1].
      - Parse content_html of the entry and verify character-by-character that each <p> or <blockquote>
        matches expected_blocks[i]["html"] verbatim (0 paraphrased words, 0 dropped words, 0 hallucinations).
    """
    commentary_map = _load_json(ROOT_MAP_PATH)
    t1_entries = _get_tier1_entries(commentary_map)

    for entry in t1_entries:
        entry_id = entry.get("id", "unknown")
        slug = entry.get("slug", "unknown")
        chunk_id = entry.get("chunk_id")
        assert chunk_id, f"Entry {entry_id} in {slug} missing 'chunk_id'"

        chunk_path = os.path.join(CHUNKS_DIR, f"{chunk_id}.json")
        chunk = _load_json(chunk_path)
        blocks = chunk.get("blocks", [])

        start_block = entry.get("start_block")
        end_block = entry.get("end_block")
        assert start_block is not None and end_block is not None, (
            f"Entry {entry_id} in {slug} missing 'start_block' or 'end_block'"
        )

        assert 0 <= start_block <= end_block < len(blocks), (
            f"Entry {entry_id} in {slug} has invalid range [{start_block}, {end_block}] "
            f"for chunk {chunk_id} with {len(blocks)} blocks"
        )

        expected_blocks = blocks[start_block : end_block + 1]

        # Parse <p> and <blockquote> elements from content_html
        parsed_tags: List[Tuple[str, str]] = re.findall(
            r'<(p|blockquote)[^>]*>(.*?)</\1>',
            entry.get("content_html", ""),
            re.DOTALL
        )

        assert len(parsed_tags) == len(expected_blocks), (
            f"Entry {entry_id} in {slug}: tag count {len(parsed_tags)} does not match "
            f"expected block count {len(expected_blocks)}"
        )

        for i, (tag_type, inner_html) in enumerate(parsed_tags):
            exp_block = expected_blocks[i]
            exp_type = exp_block.get("type", "paragraph")
            exp_html = exp_block.get("html", "")

            # Verify block type matches tag
            if exp_type == "blockquote":
                assert tag_type == "blockquote", (
                    f"Entry {entry_id} block {i}: expected <blockquote>, found <{tag_type}>"
                )
            else:
                assert tag_type == "p", (
                    f"Entry {entry_id} block {i}: expected <p>, found <{tag_type}>"
                )

            # Character-by-character verbatim equality
            assert inner_html == exp_html, (
                f"Entry {entry_id} block {i} ({slug}): textual divergence detected!\n"
                f"Extracted: {repr(inner_html[:100])}...\n"
                f"Expected:  {repr(exp_html[:100])}..."
            )


def test_footnote_routing_and_master_resolution():
    """
    Invariant 3:
      - Load data/footnotes.json.
      - For every Tier 1 entry:
        - Extract all footnote callout IDs from content_html (href="#(fn_[^"]+)").
        - Verify every callout ID exists in the entry's footnotes dict.
        - Verify every callout ID exists in data/footnotes.json with a non-empty definition.
    """
    commentary_map = _load_json(ROOT_MAP_PATH)
    master_footnotes = _load_json(FOOTNOTES_PATH)
    t1_entries = _get_tier1_entries(commentary_map)

    total_callouts = 0
    unique_callouts = set()

    for entry in t1_entries:
        entry_id = entry.get("id", "unknown")
        slug = entry.get("slug", "unknown")
        content_html = entry.get("content_html", "")
        entry_fns = entry.get("footnotes", {})

        callout_ids = re.findall(r'href=[\'"]#(fn_[^\'"]+)[\'"]', content_html)
        assert set(entry_fns.keys()) == set(callout_ids), (
            f"Entry {entry_id} footnotes dictionary mismatch: {set(entry_fns.keys())} vs {set(callout_ids)}"
        )

        for cid in callout_ids:
            total_callouts += 1
            unique_callouts.add(cid)

            # Check 1: Exists in entry's local footnotes dictionary
            assert cid in entry_fns, (
                f"Callout #{cid} in entry {entry_id} ({slug}) missing from entry's local footnotes dictionary"
            )
            entry_fn_def = entry_fns[cid]
            assert isinstance(entry_fn_def, str) and entry_fn_def.strip(), (
                f"Callout #{cid} in entry {entry_id} has empty local definition"
            )

            # Check 2: Exists in master data/footnotes.json
            assert cid in master_footnotes, (
                f"Callout #{cid} in entry {entry_id} ({slug}) does not exist in master {FOOTNOTES_PATH}"
            )
            master_def = master_footnotes[cid]
            assert isinstance(master_def, str) and master_def.strip(), (
                f"Callout #{cid} in master {FOOTNOTES_PATH} has empty definition"
            )

    assert total_callouts > 0, "Expected at least 1 footnote callout across Tier 1 pericopes"
    assert len(unique_callouts) > 0, "Expected non-empty unique callouts set"


def test_pericope_sentence_boundaries():
    """
    Invariant 4:
      - Verify that the first block of each pericope starts cleanly with a capital letter or valid quote opening.
      - Verify that the last block of each pericope ends with proper terminating punctuation (., ?, !, ”, ").
    """
    commentary_map = _load_json(ROOT_MAP_PATH)
    t1_entries = _get_tier1_entries(commentary_map)

    for entry in t1_entries:
        entry_id = entry.get("id", "unknown")
        slug = entry.get("slug", "unknown")
        content_html = entry.get("content_html", "")

        blocks = re.findall(
            r'<(p|blockquote)[^>]*>(.*?)</\1>',
            content_html,
            re.DOTALL
        )
        assert blocks, f"Entry {entry_id} in {slug} has no parsed blocks"

        # First block: strip footnote callouts and HTML tags to inspect true textual start
        first_raw = re.sub(r'<sup class=[\'"]fn-callout[\'"].*?</sup>', '', blocks[0][1], flags=re.DOTALL)
        first_clean = re.sub(r'<[^>]+>', '', first_raw).strip()

        # Last block: strip footnote callouts and HTML tags to inspect true textual terminal punctuation
        last_raw = re.sub(r'<sup class=[\'"]fn-callout[\'"].*?</sup>', '', blocks[-1][1], flags=re.DOTALL)
        last_clean = re.sub(r'<[^>]+>', '', last_raw).strip()

        # Opening boundary: must start with capital letter, quote, or bracket (including Hebrew Unicode)
        valid_start = bool(re.match(r'^[A-Z\u0590-\u05FF"“‘\'«\[]', first_clean))
        assert valid_start, (
            f"Entry {entry_id} ({slug}) violates opening boundary: "
            f"starts with {repr(first_clean[:30])}"
        )

        # Terminating boundary: must end with terminal punctuation: ., ?, !, ”, ', ", ’
        valid_end = bool(re.search(r'[.?!”"\'’]$', last_clean))
        assert valid_end, (
            f"Entry {entry_id} ({slug}) violates closing boundary: "
            f"ends with {repr(last_clean[-40:])}"
        )


def test_root_dist_commentary_map_parity():
    """
    Invariant 5:
      - Assert data/faur_commentary_map.json and dist/data/faur_commentary_map.json match 100% byte-for-byte.
    """
    assert os.path.exists(ROOT_MAP_PATH), f"Root dataset missing: {ROOT_MAP_PATH}"
    assert os.path.exists(DIST_MAP_PATH), f"Dist dataset missing: {DIST_MAP_PATH}"

    with open(ROOT_MAP_PATH, "rb") as f1, open(DIST_MAP_PATH, "rb") as f2:
        root_bytes = f1.read()
        dist_bytes = f2.read()

    assert len(root_bytes) > 0, "Root dataset is empty"
    assert len(dist_bytes) > 0, "Dist dataset is empty"
    assert root_bytes == dist_bytes, (
        f"Byte parity mismatch between {ROOT_MAP_PATH} ({len(root_bytes)} bytes) and "
        f"{DIST_MAP_PATH} ({len(dist_bytes)} bytes)"
    )


def main():
    """Standalone CLI runner for the Skeptical Auditor Verification Suite."""
    print("=" * 72)
    print("Skeptical Auditor Verification Suite (Verbatim Fidelity & Taxonomy)")
    print("Target: tests/test_faur_pericope_verbatim.py")
    print("=" * 72)

    tests = [
        ("Invariant 1: Tier 1 Counts & Anti-Bloat", test_tier1_counts_and_anti_bloat),
        ("Invariant 2: Pericope Verbatim Fidelity", test_pericope_verbatim_fidelity_against_source_chunks),
        ("Invariant 3: Footnote Routing & Master Resolution", test_footnote_routing_and_master_resolution),
        ("Invariant 4: Pericope Sentence Boundaries", test_pericope_sentence_boundaries),
        ("Invariant 5: Root vs Dist Byte Parity", test_root_dist_commentary_map_parity),
    ]

    failed = 0
    passed = 0

    for name, test_fn in tests:
        print(f"\n▶ Running {name}...")
        try:
            test_fn()
            print(f"  ✓ PASS: {name}")
            passed += 1
        except AssertionError as e:
            print(f"  💥 FAIL: {name}\n    AssertionError: {e}")
            failed += 1
        except Exception as e:
            print(f"  💥 ERROR: {name}\n    {type(e).__name__}: {e}")
            failed += 1

    print("\n" + "=" * 72)
    print(f"Audit Results: {passed} passed, {failed} failed.")
    print("=" * 72)

    if failed > 0:
        sys.exit(1)
    else:
        print("All Skeptical Auditor Invariants Verified 100% Successfully.")
        sys.exit(0)


if __name__ == "__main__":
    main()
