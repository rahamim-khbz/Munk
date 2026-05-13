# Parallel Reader Expansion Design Document

**Date:** 2026-05-13  
**Status:** Approved  

## 1. Overview
Expanding the static HTML generation pipeline for Salomon Munk's *Guide for the Perplexed* parallel reader to ingest multiple alternative JSON source editions and provide an instantaneous, zero-latency column-toggling interface in the client browser.

## 2. Architecture & UI Components
- **Column 1 Options:** Toggle between the **English** translation and the **French** edition (`French.json`).
- **Column 2 Options:** Toggle among **Judeo-Arabic** (`Guide for the Perplexed - he - Judeo Arabic, Paris, 1856 [jrb].json`), **Makbili** (`Guide for the Perplexed - he - Makbili Edition, Mif'al Mishneh Torah, 2024.json`), **Ibn Tibon** (`Guide for the Perplexed - he - Moreh Nevuchim, translated by Ibn Tibon.json`), and **French** (`French.json`).
- **Core Mechanism (Option A - Nested Spans):** Render a single parallel row per text segment. Inside each column cell, embed all target language versions within dedicated wrapper spans mapped by specific language classes (e.g., `<span class="lang-text lang-jrb" style="display:none;">...</span>`).
- **Instantaneous Client Toggling:** Embed intuitive select dropdowns in the column headers. Toggling updates a container attribute (e.g., `data-col2="jrb"`), allowing highly optimized CSS rules to instantly show the selected layer and hide inactive ones.

## 3. Data Flow
1. **Ingestion Registry:** Update `build_full_viewer.py` to ingest the new JSON datasets into memory, structured by canonical segment identifiers.
2. **Weaving Pipeline:** Loop through the primary structural segments, retrieve corresponding segment contents from all target language variants, process inline footnote markers, and construct unified HTML row cells.
3. **Static Output:** Compile standalone, high-fidelity HTML pages saved to the output `viewer/` bundle.

## 4. Error Handling & Resilience
- **Missing Segment Fallbacks:** If a specific secondary edition lacks an aligned segment key, automatically inject a standard descriptive wrapper span (`[Translation/Text Missing in this Edition]`) to ensure continuous vertical grid height alignment.
- **Tag Hygiene:** Pass all text strings through the automated tag repair stack to prevent unclosed HTML elements inside specific JSON editions from breaking the broader DOM layout structure.

## 5. Testing & Verification Strategy
- **Data Parity Audits:** Verify that segment IDs across the incoming Ibn Tibon and Judeo-Arabic files map cleanly to the standard corpus hierarchy.
- **Client Rendering Test:** Open generated HTML files locally via the `file://` protocol to ensure instant CSS toggling and perfect 100% offline functionality.
