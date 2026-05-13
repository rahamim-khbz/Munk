# Sefaria Full Corpus Native Layout Generator Architectural Design

## Goal
Implement a complete production-grade standalone generator fork (`build_sefaria_full_viewer.py`) that strictly applies native 1:1 macro-segment alignment mapping across the entire multi-volume scholarly corpus of Maimonides' *Guide for the Perplexed* (Munk/Makbili editions), outputting parallel layouts to `viewer_sefaria_full/` with embedded block-level subheadings.

## Scope & Datasets
Ingest the newly rehabilitated JSON datasets alongside the primary dictionary:
- Munk's Scholarly Prefaces (`preface_resegmented.json`/`preface_english_final.json`, `preface_vol2.json`, `preface_vol3.json`, `munk_title_note.json`)
- Munk's Endnotes (`endnotes_vol1.json`, `endnotes_vol2.json`, `endnotes_vol3.json`)
- Makbili Hebrew Source (`Guide for the Perplexed - he - Makbili*.json`)
- Primary Corpus English Translations & Footnotes (`munk_production_v1.json`)

## Architecture & Data Flow
1. **Generator Engine:** `build_sefaria_full_viewer.py` unifies all modular sections into a seamless array.
2. **Mapping Protocol:** Iterate through section blocks mapping `hebrew_segments[i]` directly to translation keys (`root.text.Part N..{ch}.{i}`). Sub-segments (`.sub_0`, `.sub_1`) are concatenated to maintain continuous block prose matching Sefaria's native data model.
3. **Styling Layer:** Apply block display formatting directly to `.mediumGrey` markers (`display: block; margin-top: 18px; margin-bottom: 8px; font-weight: bold; color: #8b0000;`) to render inline section dividers as clear visual headings inside standard text blocks.
4. **Footnotes System:** Superscript toggle references slide open continuous bottom-sheet footnote viewers populated by embedded chapter-level JSON object maps.

## Testing & Quality Assurance
- Automated alignment audit suite (`inspect_sefaria_full_alignment.py`) verifies exact 1:1 macro-segment pairing and absence of missing translation gaps across all 190+ target sections.
- Structural regression testing checks stable DOM generation patterns.
