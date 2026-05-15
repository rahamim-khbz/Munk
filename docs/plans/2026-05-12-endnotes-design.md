# Munk's Endnotes Architectural Design

**Date:** 2026-05-12  
**Status:** Approved  

## Goal
Integrate Salomon Munk's Endnotes (Parts I, II, and III) into the scholarly parallel reader as three distinct web pages grouped under a dedicated category header in the Table of Contents.

## Data Storage Architecture
Three dedicated JSON files will be created in the project root:
- `endnotes_vol1.json`
- `endnotes_vol2.json`
- `endnotes_vol3.json`

Schema follows standard mapping parity:
```json
{
  "fr": ["..."],
  "en": ["..."]
}
```

## UI Presentation & Alignment Strategy
- **Parallel Segment Integrity (Option A):** Multi-paragraph textual sequences within a single Endnote reference item will be merged into a single continuous block per language array. Inline paragraph tags (`<p>...</p>`) or line break pairs (`<br><br>`) will be utilized to maintain internal paragraph rendering while keeping parallel side-by-side array alignment synchronized.
- **Emphasis Preservation:** All source markdown italic sequences (`*`) will be cleanly converted to semantic `<em>...</em>` tags.

## Pipeline Integration
- Update `build_full_viewer.py` to ingest the new files and inject them into `unified_chapters`.
- Set page titles to `"Endnotes to Volume I"`, `"Endnotes to Volume II"`, and `"Endnotes to Volume III"`.
- Introduce grouping flags/logic in the Table of Contents rendering loop to generate a category separator titled **"Munk's Endnotes"** before appending the sub-item navigation links.
