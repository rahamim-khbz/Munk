# Sefaria Native Layout Fork (Part I) Architectural Design

## Goal
Implement a robust, standalone viewer generation fork (`build_sefaria_part1_viewer.py`) that strictly honors Sefaria's native 1:1 segment alignment mapping for Maimonides' *Guide for the Perplexed* (Part I) without shattering source text blocks, demonstrating absolute alignment stability side-by-side.

## Constraints
- **Scope:** Execute generation exclusively for Part I chapters, isolating outputs to `viewer_sefaria_part1/`.
- **Fidelity:** Ingest existing, unaltered JSON translation datasets. Maintain complete structural matching with Sefaria's macro-segment references.
- **Safety:** Fork the generation pipeline to protect existing visual formatting code.

## Architecture & Components
- **Generator Script:** `build_sefaria_part1_viewer.py` handles the file ingestion, simplified text pairing loop, and static HTML output writing.
- **Styling Layer:** Inline CSS target rules style `.mediumGrey` dynamically as visual subheadings inside unified cells (`display: block; margin-top: 16px; margin-bottom: 6px; font-weight: bold; color: var(--accent-color);`).

## Data Flow
1. Load Makbili source JSON and Munk translation JSON.
2. Iterate through Part I chapter arrays. Pair segment `hebrew_data["text"]["Part 1"][""][ch_idx][i]` directly with `get_en_text(f"root.text.Part 1..{ch_idx}.{i}")` using simple array index alignment.
3. Output exactly one parallel row (`<div class="parallel-row">`) per canonical segment block.

## Testing Strategy
- Execute `build_sefaria_part1_viewer.py` to produce pristine multi-page HTML outputs.
- Adapt/run the automated `inspect_html_alignment.py` audit targeting `viewer_sefaria_part1/` to prove that segment unification fully eliminates "Empty EN text" flags and normalizes word count ratios.
