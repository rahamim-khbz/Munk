# Parallel Reader Expansion Design Document

**Date:** 2026-05-13 (Updated: 2026-05-14)  
**Status:** Approved  

## 1. Overview
Expanding the static HTML generation pipeline for Salomon Munk's *Guide for the Perplexed* parallel reader to ingest multiple alternative JSON source editions and provide an instantaneous, zero-latency column-toggling interface in the client browser, fully integrated with persistent multi-theme presentation modes and seamless responsive mobile view optimization.

## 2. Architecture & UI Components
- **Column 1 Options:** Toggle between the **English** translation and the **French** edition (`French.json`).
- **Column 2 Options:** Toggle among **Judeo-Arabic** (`Guide for the Perplexed - he - Judeo Arabic, Paris, 1856 [jrb].json`), **Makbili** (`Guide for the Perplexed - he - Makbili Edition, Mif'al Mishneh Torah, 2024.json`), **Ibn Tibon** (`Guide for the Perplexed - he - Moreh Nevuchim, translated by Ibn Tibon.json`), and **French** (`French.json`).
- **Core Mechanism (Option A - Nested Spans):** Render exactly one unified parallel row container per source text segment. Inside each column cell, embed all target language versions within dedicated wrapper spans mapped by specific language classes.
- **Makbili Subheadings Styling:** Retain the segment as a single unified Sefaria row. The inline `.mediumGrey` subheadings are styled using block layouts with a full-width bottom border (`border-bottom: 2px solid var(--accent); width: 100%; display: block;`) to achieve a distinct underline across the column directly below the heading text.
- **Responsive Mobile Layout Stacking:** Mirror the existing viewer's mobile layout mechanics under `@media (max-width: 768px)`. The side-by-side `.parallel-row` grid containers natively transition to vertical flex column stacks (`display: flex; flex-direction: column;`), placing Column 2 on top (`order: -1`) and Column 1 below it separated by a dashed divider. The multi-select `.column-selectors-bar` component dynamically transitions to a full-width vertically stacked arrangement to prevent UI squeezing on smaller mobile viewports.
- **Instantaneous Client Toggling:** Embed intuitive select dropdowns at the top of the viewing layout. Toggling updates container data-attributes, allowing optimized CSS rules to instantly show the selected layer.
- **Theme Mode Integration:** Natively adapt all UI selector elements and layouts to global custom semantic properties (`var(--surface)`, `var(--border)`, `var(--accent)`) to blend seamlessly across Light, Sepia, and Dark viewing themes.

## 3. Data Flow
1. **Ingestion Registry:** Update `build_full_viewer.py` to ingest the new JSON datasets into memory dictionaries, mapped cleanly by segment keys.
2. **Unified Weaving Pipeline:** Loop through Sefaria structural segments 1:1, retrieve variant strings via dynamic key matching, process inline footnotes, and assemble single consolidated row cells. Legacy row fragmentation logic is completely purged.
3. **Static Output:** Compile standalone HTML files supporting complete offline operation.

## 4. Error Handling & Resilience
- **Missing Segment Fallbacks:** Inject a standardized text fallback wrapper if an edition lacks a matching segment key.
- **Tag Hygiene:** Pass all extracted content strings through tag healing algorithms to prevent malformed structures.

## 5. Testing & Verification Strategy
- **Data Parity Audits:** Validate that segment structures map accurately across all source corpa.
- **Responsive Navigation:** Resize browser windows below 768px width to verify that parallel rows and dropdown controllers transition cleanly to single-column vertically stacked viewports.
