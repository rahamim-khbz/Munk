# Homo Mysticus Pericope Pruning & Verbatim Excerpt Plan

> **For Antigravity:** REQUIRED SUB-SKILL: Load `executing-plans` and `subagent-driven-development` to implement this plan task-by-task using specialized subagents.

**Goal:** Prune the Homo Mysticus commentary integration from 100 bloated full-chapter dumps down to ~28 curated, high-impact Tier 1 close-readings, extracting strictly 100% verbatim direct quotes (2–4 paragraph pericopes) audited by a skeptical verification subagent, demoting all secondary mentions to Tier 3 footnote citations, and updating the reader link to "Read full section in Homo Mysticus (Chapter ##) ↗".

**Architecture:** 
1. Redefine `CHUNK_TIER1_TARGETS` in `scripts/build_faur_commentary_map.py` to map only the approved ~28 primary close-readings, adding explicit `[start_block, end_block]` ranges for contiguous verbatim paragraph extraction.
2. Demote all 72 secondary/thematic mentions into Tier 3 (incidental footnote citations).
3. Implement an automated skeptical auditor test (`tests/test_faur_pericope_verbatim.py`) to verify character-by-character that extracted text matches `data/hm_chunks/` and `docs/faur_homo_mysticus_verified/` with zero alterations, zero missing words, and properly routed footnote callouts (`fn.faur.*`).
4. Update `js/reader.js` and `dist/js/reader.js` to render the clean pericope card with link text `"Read full section in Homo Mysticus (Chapter ##) ↗"`.
5. Maintain 100% byte parity between root and `dist/`, pass all quality gates, commit, push, and verify live on GitHub Pages.

**Tech Stack:** Python 3, Vanilla JS / ES6, CSS Grid / Custom Properties, Node.js Chrome DevTools Protocol (CDP), Git / GitHub Pages.

---

## Task Breakdown

### Task 1: Curate Approved Tier 1 Targets & Block Ranges
- **Files to touch:** `scripts/build_faur_commentary_map.py`
- **Actions:**
  1. Define `CURATED_TIER1_PERICOPES: Dict[str, Dict[str, Any]]` mapping the ~28 approved *Guide* chapters to:
     - `chunk_id`: The source chunk.
     - `start_block`: First paragraph index (inclusive).
     - `end_block`: Last paragraph index (inclusive).
     - `key_terms`: Specific Tier 2 technical terms verified for that chapter.
  2. Demote all other prior Tier 1 targets to Tier 3 citations.
  3. Update `build_chunk_content_html` to slice `blocks[start_block : end_block + 1]` instead of dumping all blocks.
  4. Ensure each Tier 1 entry includes `faur_chapter_num`, `part_title`, `section_title`, `start_block`, `end_block`, and `page_range`.

### Task 2: Build Skeptical Auditor Verification Suite
- **Files to touch:** `tests/test_faur_pericope_verbatim.py`
- **Actions:**
  1. Write an automated audit harness callable via standard Python:
     - Load `data/faur_commentary_map.json`.
     - For every Tier 1 entry, load the underlying `data/hm_chunks/{chunk_id}.json`.
     - Verify that every paragraph in `content_html` matches verbatim against the slice of blocks in the source chunk.
     - Verify footnote callouts `<sup class="fn-callout">` resolve to genuine notes in `data/footnotes.json` with zero missing definitions.
     - Assert that no Tier 1 entry exceeds 800 words or 5 paragraphs (hard anti-bloat boundary).
     - Assert that every *Guide* chapter has at most 1 (or max 2) Tier 1 entries.

### Task 3: Build & Mirror Commentary Map Assets
- **Files to touch:** `data/faur_commentary_map.json`, `dist/data/faur_commentary_map.json`
- **Actions:**
  1. Run `python3 scripts/build_faur_commentary_map.py`.
  2. Copy to `dist/data/faur_commentary_map.json`.
  3. Verify byte-identical parity with `cmp`.

### Task 4: UI & Link Refinements in Reader
- **Files to touch:** `js/reader.js`, `dist/js/reader.js`, `css/reader.css`, `dist/css/reader.css`
- **Actions:**
  1. Update footer link in `renderFaurTopBox` to read:
     `"Read full section in Homo Mysticus (Chapter ##) ↗"` (skipping "analytical").
  2. Verify that clicking the link navigates to the standalone reader at `Homo_Mysticus_Sample_Chapters.html` or modal with the correct section anchor.
  3. Ensure Tier 2 key term chips and Firestore feedback card render seamlessly beneath the focused excerpt.
  4. Mirror changes byte-identically to `dist/`.

### Task 5: Comprehensive Quality Gate & Headless Multi-Viewport Audit
- **Files to touch:** `scripts/verify_faur_integration.py`
- **Actions:**
  1. Update invariants in `scripts/verify_faur_integration.py` for new counts:
     - Tier 1 count: ~28–30 (down from 100).
     - Tier 2 count: 24.
     - Tier 3 count: ~531+.
  2. Run `python3 scripts/verify_faur_integration.py` and ensure all 5 gates pass.
  3. Run headless CDP visual audit across Desktop, iPad, and iPhone to verify zero overflow.

### Task 6: Commit, Push, and Live Web Verification
- **Files to touch:** Git branches `feat/scripture-index-web` and `gh-pages`
- **Actions:**
  1. Commit on `feat/scripture-index-web` and push to `origin`.
  2. Checkout web release assets onto `gh-pages`, commit, and push to `origin`.
  3. Run `scratch/verify_live_web_deployment.cjs` against live GitHub Pages to verify the pruned, focused pericopes live in production.

---

## Skeptical Auditor Subagent Protocol

When executing in the new session, dispatch a dedicated subagent (`code-reviewer` or `auditor-agent`) with the following explicit instructions:

```markdown
Role: Skeptical Textual Fidelity Auditor
Task: Conduct an adversarial audit of all Tier 1 commentary pericopes against the original source files in data/hm_chunks/ and docs/faur_homo_mysticus_verified/.
Checklist:
1. Verbatim Text Check: Ensure 0 paraphrasing, 0 hallucinated words, 0 dropped words.
2. Boundary Check: Ensure quotes start and end on complete, clean sentence boundaries.
3. Footnote Check: Ensure all <sup> footnotes match genuine Faur notes.
4. Bloat Check: Reject any pericope that exceeds 4 paragraphs or 600 words.
Output: Report PASS only if 100% of the ~28 pericopes pass all checks with zero discrepancies.
```
