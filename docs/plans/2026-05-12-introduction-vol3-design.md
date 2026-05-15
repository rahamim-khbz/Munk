# Introduction to Volume III Integration Design

**Date:** 2026-05-12
**Topic:** Introduction to Volume III

## Overview
Integrate Salomon Munk's Introduction to Volume III into the Munk's Guide multi-page scholarly parallel viewer. The layout and architecture follow the identical pattern established by Introduction to Volume II.

## Architecture & Schema
- **Dedicated Storage:** `preface_vol3.json` containing `"footnotes_en"`, `"fr"` array (14 segments), and `"en"` array (14 segments).
- **Rich Text Conversion:** Map markdown italics (`*text*`) to HTML `<em>text</em>` tags.
- **Footnotes Mapping:** Map inline footnote citations `[^1]` and `[^2]` in Segment 9 to `[[fn:3007]]` and `[[fn:3008]]`.
- **Signature Block:** Align signature block layout to `"S. MUNK.<br>Paris, July 1866."` matching Volume II.

## Pipeline Integration
- Update `build_full_viewer.py` to check for and load `preface_vol3.json`.
- Inject `fn.3007` and `fn.3008` into the runtime `english_footnotes` dictionary.
- Append `"Introduction to Volume III"` chapter config to `unified_chapters`.
- Rely on automated UI tag rendering to convert preface footnotes to standard asterisks (`*`).
