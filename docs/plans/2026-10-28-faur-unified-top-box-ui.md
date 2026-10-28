# José Faur (*Homo Mysticus*) Unified Top Collapsible Box UI Implementation Plan

> **For Antigravity:** REQUIRED SUB-SKILL: Load executing-plans to implement this plan task-by-task.

**Goal:** Refactor the *Homo Mysticus* integration in `reader.html` and `Homo_Mysticus_Sample_Chapters.html` to replace floating margin popovers and bottom postscripts with an inline `❦ HM` button inside the chapter heading that expands a full-width, push-down collapsible commentary box opening with exact `Homo Mysticus, Chapter ## - [[Subtitle/Section]]` citations (without page ranges), verified across Desktop, iPad Mini, and iPhone iOS Safari viewports.

**Architecture:** Unify Tier 1 and Tier 2 commentary in `scripts/build_faur_commentary_map.py` so every annotated chapter has a single non-overlapping list of *Homo Mysticus* subsections (with embedded `citation` strings and `key_terms` badges). In `js/reader.js` and `css/reader.css`, render the `❦ HM` toggle button inline with `<h2>${data.title}</h2>` inside `.chapter-header` and place `#faur-top-box` as a normal-flow full-width block (`grid-column: span 2; width: 100%`) immediately below `.chapter-header` so expanding it naturally pushes down `.parallel-row` chapter text. Verify via automated multi-viewport CDP browser interaction (`scripts/capture_faur_multiviewport_audit.cjs`) and a visual critique subagent inspection loop.

**Tech Stack:** Vanilla HTML5, CSS3 (CSS Grid, Flexbox, Custom Properties, Responsive Media Queries, Safe-Area Insets), ES6+ JavaScript, Python 3.10+ (`pytest`), Node.js WebSocket Chrome DevTools Protocol (CDP).

---

### Task 1: Unify Commentary Map Data & Citation Labels (`scripts/build_faur_commentary_map.py`)

**Files:**
- Modify: `scripts/build_faur_commentary_map.py:90-130,860-1005`
- Modify: `data/faur_commentary_map.json`
- Modify: `dist/data/faur_commentary_map.json`

**Step 1: Update `scripts/build_faur_commentary_map.py` to add `citation`, `faur_chapter`, `key_terms`, and unify `maimonides-prefatory-remarks`**

In `scripts/build_faur_commentary_map.py`:
1. Add `PART_TO_CHAPTER_NUM` mapping `Part One: Apophasis` → `1`, `Part Two: Imagination` → `2`, `Part Three: Cosmology` → `3`, `Part Four: Anthropology` → `4`, and helper `format_faur_citation(part_title: str, section_title: str) -> Tuple[Optional[int], str]`:
   ```python
   PART_TO_CHAPTER_NUM: Dict[str, Optional[int]] = {
       "Part One: Apophasis": 1,
       "Part Two: Imagination": 2,
       "Part Three: Cosmology": 3,
       "Part Four: Anthropology": 4,
       "Introduction": None,
       "Front Matter": None,
   }

   def format_faur_citation(part_title: str, section_title: str) -> Tuple[Optional[int], str]:
       ch_num = PART_TO_CHAPTER_NUM.get(part_title)
       if ch_num is not None:
           return ch_num, f"Homo Mysticus, Chapter {ch_num} - {section_title}"
       if part_title == "Introduction":
           return None, "Homo Mysticus, Introduction"
       return None, f"Homo Mysticus, {section_title}"
   ```
2. In `CHUNK_TIER1_TARGETS`, update `"chunk_08_the_resolution_of_unconcluded_subscripts"` so `maimonides-prefatory-remarks` (the 24th Tier 2 gloss on `al-burūq`) also has its full subsection in `tier1`:
   ```python
       "chunk_08_the_resolution_of_unconcluded_subscripts": [
           "maimonides-introduction-to-part-1",
           "maimonides-prefatory-remarks"
       ],
   ```
3. In `build_commentary_map()`, attach `faur_chapter`, `citation`, and `key_terms` (matched from `tier2_entries` for that chapter) onto each `tier1_entry`, and sort each chapter's `tier1` list so numbered chapters (`faur_chapter` 1–4) always precede `Introduction` (`faur_chapter is None`), ensuring every chapter opens with `Homo Mysticus, Chapter ## - [[Subtitle/Section]]`:
   ```python
       faur_ch_num, citation_str = format_faur_citation(chunk["part_title"], chunk["title"])
       tier1_entry = {
           "id": f"tier1_{chunk_id}_{slug}",
           "chunk_id": chunk_id,
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
   ```
   After populating `tier2_entries`, for each chapter `ch_obj`, sort `ch_obj["tier1"]` by `(0 if e["faur_chapter"] is not None else 1, e["chunk_id"])`, and populate `key_terms` on the matching chunk (or first chunk in `ch_obj["tier1"]`) with `{"term": entry["term"], "original_script": entry["original_script"], "anchor_label": entry["anchor_label"]}`.

**Step 2: Run `scripts/build_faur_commentary_map.py` and verify output**

Run: `python3 scripts/build_faur_commentary_map.py`
Expected:
- `✓ Parsed 46 chunks`
- `✓ Compiled 100 Tier 1 extended exegeses`
- `✓ Verified byte identity between root and dist datasets.`

---

### Task 2: Refactor `reader.html`, `js/reader.js`, and `css/reader.css` for Inline Header Button & Full-Width Push-Down Box

**Files:**
- Modify: `reader.html:21-28` and `dist/reader.html:21-28`
- Modify: `js/reader.js:50-220,460-515,615-630` and `dist/js/reader.js`
- Modify: `css/reader.css:84-105,184-470` and `dist/css/reader.css`

**Step 1: Fix duplicate `#btn-faur-toggle` in `reader.html`**

In `reader.html` lines 21–28, remove the duplicate `<button class="theme-btn active" id="btn-faur-toggle" ...>` inside `.mobile-theme-panel` so `.mobile-theme-panel` only has `#btn-mobile-faur-toggle` and `.theme-controls` in `.header` uniquely owns `#btn-faur-toggle`:
```html
        <div class="mobile-theme-panel">
            <a href="scripture.html" class="theme-btn" style="text-decoration:none; display:inline-flex; align-items:center; justify-content:center; gap:6px; font-weight:600;">📜 Scriptural Index</a>
            <button id="btn-mobile-faur-toggle" onclick="toggleFaurAnnotations()" class="theme-btn active" title="Toggle Homo Mysticus annotations" aria-pressed="true">❦ HM</button>
            <button onclick="setTheme('light')" class="theme-btn">&#9728;&#65039; Light</button>
            <button onclick="setTheme('sepia')" class="theme-btn">&#128220; Sepia</button>
            <button onclick="setTheme('dark')" class="theme-btn">&#127769; Dark</button>
        </div>
```

**Step 2: Replace hover popover & bottom postscript rendering in `js/reader.js` with inline header button and top collapsible box**

In `js/reader.js`:
1. Replace `formatFaurPages`, `toggleFaurPostscriptDrawer`, `renderFaurPostscripts`, `toggleFaurPopover`, `closeFaurPopover`, and `renderFaurMarginAnchor` with:
```javascript
const FAUR_PART_CHAPTER_MAP = {
    'Part One: Apophasis': 1,
    'Part Two: Imagination': 2,
    'Part Three: Cosmology': 3,
    'Part Four: Anthropology': 4
};

function formatFaurCitation(entry) {
    if (!entry) return 'Homo Mysticus';
    if (entry.citation) return entry.citation;
    const chNum = entry.faur_chapter || FAUR_PART_CHAPTER_MAP[entry.part_title];
    if (chNum && entry.section_title) {
        return `Homo Mysticus, Chapter ${chNum} - ${entry.section_title}`;
    }
    if (entry.part_title === 'Introduction' || entry.section_title === 'Introduction') {
        return 'Homo Mysticus, Introduction';
    }
    return entry.section_title ? `Homo Mysticus - ${entry.section_title}` : 'Homo Mysticus';
}

function formatFaurContent(htmlStr, slug) {
    if (!htmlStr) return '';
    return htmlStr.replace(/<sup class="fn-callout"><a [^>]*href="#(fn_[^"]+)"[^>]*>(\d+)<\/a><\/sup>/g, (m, fnId, num) => {
        return `<sup class="fn-ref faur-fn-ref" onclick="showFn('fn.faur.${slug}.${fnId}')" title="View Faur's Footnote">${num}</sup>`;
    });
}

function toggleFaurTopBox(forceState) {
    const topBox = document.getElementById('faur-top-box');
    const inlineBtn = document.getElementById('btn-chapter-faur');
    if (!topBox) return;
    const currentlyOpen = topBox.classList.contains('open');
    const nextOpen = typeof forceState === 'boolean' ? forceState : !currentlyOpen;
    topBox.classList.toggle('open', nextOpen);
    topBox.setAttribute('aria-hidden', nextOpen ? 'false' : 'true');
    if (inlineBtn) {
        inlineBtn.classList.toggle('active', nextOpen);
        inlineBtn.setAttribute('aria-expanded', nextOpen ? 'true' : 'false');
        const chev = inlineBtn.querySelector('.faur-inline-chevron');
        if (chev) chev.textContent = nextOpen ? '▲' : '▼';
    }
}

function switchFaurSubsection(index) {
    const topBox = document.getElementById('faur-top-box');
    if (!topBox) return;
    const cards = topBox.querySelectorAll('.faur-subsection-card');
    const tabs = topBox.querySelectorAll('.faur-subsection-tab');
    cards.forEach((card, idx) => {
        const isTarget = idx === index;
        const body = card.querySelector('.faur-subsection-body');
        const headerBtn = card.querySelector('.faur-subsection-header');
        const icon = card.querySelector('.faur-subsection-toggle-icon');
        card.classList.toggle('open', isTarget);
        if (body) body.classList.toggle('open', isTarget);
        if (headerBtn) headerBtn.setAttribute('aria-expanded', isTarget ? 'true' : 'false');
        if (icon) icon.textContent = isTarget ? '▲' : '▼';
    });
    tabs.forEach((tab, idx) => {
        const isTarget = idx === index;
        tab.classList.toggle('active', isTarget);
        tab.setAttribute('aria-selected', isTarget ? 'true' : 'false');
    });
}

function toggleFaurSubsection(btn) {
    const card = btn.closest('.faur-subsection-card');
    if (!card) return;
    const body = card.querySelector('.faur-subsection-body');
    const icon = btn.querySelector('.faur-subsection-toggle-icon');
    const isExpanded = btn.getAttribute('aria-expanded') === 'true';
    const nextExpanded = !isExpanded;
    btn.setAttribute('aria-expanded', nextExpanded ? 'true' : 'false');
    card.classList.toggle('open', nextExpanded);
    if (body) body.classList.toggle('open', nextExpanded);
    if (icon) icon.textContent = nextExpanded ? '▲' : '▼';
}

function renderFaurTopBox(sections, slug) {
    if (!sections || !sections.length) return '';
    const hasMultiple = sections.length > 1;
    const tabsHtml = hasMultiple ? `
        <div class="faur-subsection-tabs" role="tablist" aria-label="Homo Mysticus Subsections">
            ${sections.map((entry, idx) => {
                const cit = formatFaurCitation(entry);
                return `<button type="button" role="tab" class="faur-subsection-tab ${idx === 0 ? 'active' : ''}" aria-selected="${idx === 0 ? 'true' : 'false'}" onclick="switchFaurSubsection(${idx})">${cit}</button>`;
            }).join('')}
        </div>
    ` : '';

    const cardsHtml = sections.map((entry, idx) => {
        const citation = formatFaurCitation(entry);
        const processedContent = formatFaurContent(entry.content_html, entry.slug || slug);
        const isOpenInitially = (idx === 0);
        const keyTerms = entry.key_terms || [];
        const keyTermsHtml = keyTerms.length > 0 ? `
            <div class="faur-key-terms-bar">
                ${keyTerms.map(kt => `
                    <div class="faur-key-term-chip">
                        <span class="faur-key-term-label">Key Term:</span>
                        ${kt.term ? `<strong class="faur-key-term-name">${kt.term}</strong>` : ''}
                        ${kt.original_script ? `<span class="faur-key-term-orig" dir="rtl" lang="he">${kt.original_script}</span>` : ''}
                        ${kt.anchor_label ? `<span class="faur-key-term-desc">— ${kt.anchor_label}</span>` : ''}
                    </div>
                `).join('')}
            </div>
        ` : '';

        return `
            <div class="faur-subsection-card ${isOpenInitially ? 'open' : ''}" data-subsection-index="${idx}">
                <button type="button" class="faur-subsection-header" onclick="toggleFaurSubsection(this)" aria-expanded="${isOpenInitially ? 'true' : 'false'}">
                    <div class="faur-subsection-header-main">
                        <div class="faur-subsection-citation">${citation}</div>
                        <div class="faur-subsection-author">José Faur · <em>Homo Mysticus</em></div>
                    </div>
                    <span class="faur-subsection-toggle-icon" aria-hidden="true">${isOpenInitially ? '▲' : '▼'}</span>
                </button>
                <div class="faur-subsection-body ${isOpenInitially ? 'open' : ''}">
                    ${keyTermsHtml}
                    <div class="faur-subsection-content">
                        ${processedContent}
                    </div>
                    <div class="faur-subsection-footer">
                        José Faur, <em>Homo Mysticus: A Guide to Maimonides's Guide for the Perplexed</em> (Syracuse University Press, 1998)
                    </div>
                </div>
            </div>
        `;
    }).join('');

    return `
        <section id="faur-top-box" class="faur-top-box" aria-hidden="true" aria-label="Homo Mysticus Commentary">
            ${tabsHtml}
            <div class="faur-subsections-list">
                ${cardsHtml}
            </div>
        </section>
    `;
}
```
2. In `loadChapter(slug)` (lines 474–500):
   - Determine `const faurSections = (commentary && commentary.chapters && commentary.chapters[slug] && commentary.chapters[slug].tier1) || [];`
   - Render `.chapter-header` with inline `#btn-chapter-faur` when `faurSections.length > 0`, followed immediately by `renderFaurTopBox(faurSections, slug)`:
   ```javascript
        const faurSections = (commentary && commentary.chapters && commentary.chapters[slug] && commentary.chapters[slug].tier1) || [];
        const hasFaur = faurSections.length > 0;
        const inlineFaurBtnHtml = hasFaur ? `
            <button type="button"
                    id="btn-chapter-faur"
                    class="faur-inline-btn"
                    onclick="toggleFaurTopBox()"
                    aria-expanded="false"
                    aria-controls="faur-top-box"
                    title="Open Homo Mysticus Commentary (${faurSections.length} ${faurSections.length === 1 ? 'subsection' : 'subsections'})">
                <span class="faur-inline-glyph">❦ HM</span>
                <span class="faur-inline-chevron" aria-hidden="true">▼</span>
            </button>
        ` : '';
        let html = `<div class="chapter-header"><div class="chapter-header-row"><h2>${data.title}</h2>${inlineFaurBtnHtml}</div></div>`;
        if (hasFaur) {
            html += renderFaurTopBox(faurSections, slug);
        }
        data.rows.forEach(row => {
            html += `<div class="parallel-row" ${row.key ? `id="row-${row.key}"` : ''}>
                <div class="left-cell">
                    ${Object.entries(row.variants).map(([v, t]) => {
                        let processed = t.replace(/\[\[fn:([^|\]]+)(?:\|([^\]]+))?\]\]/g, formatFootnoteToken);
                        return `<span class="variant-span variant-${v}">${processed}</span>`;
                    }).join('')}
                </div>
                <div class="right-cell">
                    ${Object.entries(row.variants).map(([v, t]) => {
                        let processed = t.replace(/\[\[fn:([^|\]]+)(?:\|([^\]]+))?\]\]/g, formatFootnoteToken);
                        return `<span class="variant-span variant-${v}">${processed}</span>`;
                    }).join('')}
                </div>
            </div>`;
        });
   ```
   - Remove the old `document.addEventListener('keydown', ...)` and `document.addEventListener('click', ...)` listeners that targeted `.faur-margin-anchor.pinned`.

**Step 3: Update `css/reader.css` for `.chapter-header-row`, `.faur-inline-btn`, and `#faur-top-box`**

In `css/reader.css`:
1. Update `.chapter-header` and add `.chapter-header-row` and `.faur-inline-btn`:
```css
.chapter-header {
    grid-column: span 2;
    padding: 36px 0 18px;
    border-bottom: 2px solid var(--accent);
    margin-bottom: 20px;
}
.chapter-header-row {
    display: flex;
    align-items: center;
    gap: 14px;
    flex-wrap: wrap;
}
.chapter-header h2 {
    margin: 0;
    color: var(--accent);
    font-weight: 700;
}
.faur-inline-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    min-height: 44px;
    min-width: 44px;
    padding: 6px 14px;
    border: 1.5px solid var(--accent);
    border-radius: 6px;
    background: var(--surface);
    color: var(--accent);
    font-family: var(--font-english);
    font-size: 0.9rem;
    font-weight: 700;
    cursor: pointer;
    transition: background 0.18s ease, color 0.18s ease, box-shadow 0.18s ease;
    box-sizing: border-box;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}
.faur-inline-btn:hover,
.faur-inline-btn.active {
    background: var(--accent);
    color: #ffffff;
}
.faur-inline-chevron {
    font-size: 0.75rem;
    line-height: 1;
}
```
2. Replace the old margin anchor / popover / bottom postscript styles in `css/reader.css` with the full-width top collapsible box styles:
```css
/* Zero-thrash global toggle hiding */
.main-container[data-faur="off"] .faur-inline-btn,
.main-container[data-faur="off"] .faur-top-box {
    display: none !important;
}

/* Full-Width Push-Down Collapsible Box */
.faur-top-box {
    display: none;
    grid-column: span 2;
    width: 100%;
    margin: 0 0 28px 0;
    box-sizing: border-box;
}
.faur-top-box.open {
    display: block;
}

.faur-subsection-tabs {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 12px;
}
.faur-subsection-tab {
    min-height: 44px;
    padding: 8px 14px;
    border-radius: 6px;
    border: 1px solid var(--border);
    background: var(--surface);
    color: var(--text);
    font-family: var(--font-english);
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    text-align: left;
    transition: all 0.18s ease;
    box-sizing: border-box;
}
.faur-subsection-tab:hover {
    border-color: var(--accent);
    color: var(--accent);
}
.faur-subsection-tab.active {
    background: var(--accent);
    color: #ffffff;
    border-color: var(--accent);
}

.faur-subsection-card {
    border: 1px solid var(--border);
    border-top: 3px solid var(--accent);
    border-radius: 8px;
    margin-bottom: 16px;
    background: var(--surface);
    overflow: hidden;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.05);
}

.faur-subsection-header {
    width: 100%;
    min-height: 52px;
    padding: 14px 20px;
    background: var(--surface);
    border: none;
    text-align: left;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    cursor: pointer;
    box-sizing: border-box;
    transition: background 0.18s ease;
}
.faur-subsection-header:hover {
    background: var(--row-hover);
}
.faur-subsection-header-main {
    display: flex;
    flex-direction: column;
    gap: 4px;
    min-width: 0;
}
.faur-subsection-citation {
    font-family: var(--font-english);
    font-size: 1.08rem;
    font-weight: 700;
    color: var(--accent);
    line-height: 1.35;
}
.faur-subsection-author {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-muted);
    letter-spacing: 0.03em;
}
.faur-subsection-toggle-icon {
    font-size: 0.9rem;
    color: var(--accent);
    flex-shrink: 0;
}

.faur-subsection-body {
    display: none;
    padding: 18px 24px 24px;
    border-top: 1px solid var(--border);
    background: var(--surface);
    font-size: 0.98rem;
    line-height: 1.72;
    color: var(--text);
}
.faur-subsection-body.open {
    display: block;
}

.faur-key-terms-bar {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 18px;
    padding: 12px 16px;
    background: var(--bg);
    border-left: 3px solid var(--accent);
    border-radius: 0 6px 6px 0;
}
.faur-key-term-chip {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    gap: 8px;
    font-size: 0.9rem;
}
.faur-key-term-label {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--accent);
}
.faur-key-term-name {
    color: var(--text);
}
.faur-key-term-orig {
    font-family: var(--font-hebrew);
    font-size: 1.15rem;
    color: var(--accent);
}
.faur-key-term-desc {
    color: var(--text-muted);
    font-style: italic;
}

.faur-subsection-content p {
    margin: 0 0 14px 0;
    text-align: justify;
    hyphens: auto;
}
.faur-subsection-content blockquote {
    margin: 14px 20px;
    padding: 10px 16px;
    border-left: 3px solid var(--border);
    color: var(--text-muted);
    font-style: italic;
}
.faur-fn-ref {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 20px;
    min-height: 20px;
    padding: 1px 5px;
    margin: 0 1px;
    border-radius: 4px;
    font-size: 0.78rem;
    background: color-mix(in srgb, var(--accent) 12%, transparent);
}
.faur-subsection-footer {
    margin-top: 20px;
    padding-top: 10px;
    border-top: 1px dashed var(--border);
    font-size: 0.8rem;
    color: var(--text-muted);
}

@media (max-width: 768px) {
    .faur-subsection-header {
        padding: 12px 16px;
    }
    .faur-subsection-citation {
        font-size: 0.98rem;
    }
    .faur-subsection-body {
        padding: 14px 16px 18px;
    }
    .faur-subsection-content p {
        text-align: left;
    }
    .faur-subsection-content blockquote {
        margin: 12px 8px;
        padding: 8px 12px;
    }
}
```
3. Synchronize `reader.html`, `js/reader.js`, and `css/reader.css` to `dist/reader.html`, `dist/js/reader.js`, and `dist/css/reader.css`.

---

### Task 3: Update & Regenerate Standalone Showcase (`scripts/generate_sample_showcase.py` & `Homo_Mysticus_Sample_Chapters.html`)

**Files:**
- Modify: `scripts/generate_sample_showcase.py:110-156`
- Modify: `Homo_Mysticus_Sample_Chapters.html`

**Step 1: Ensure `.sample-pill-btn` meets 44px touch target height and mobile responsiveness in `scripts/generate_sample_showcase.py`**

Update `showcase_css` in `scripts/generate_sample_showcase.py` so `.sample-pill-btn` has `min-height: 44px; display: inline-flex; align-items: center; justify-content: center; box-sizing: border-box;` and on `@media (max-width: 768px)` `.sample-showcase-pills` scrolls horizontally (`flex-wrap: nowrap; overflow-x: auto; max-width: 100%; -webkit-overflow-scrolling: touch; padding-bottom: 4px;`) so the sticky top bar remains compact on iPhone (`390x844`) without vertical bloat or horizontal page overflow.

**Step 2: Run `scripts/generate_sample_showcase.py`**

Run: `python3 scripts/generate_sample_showcase.py`
Expected: `Generated standalone showcase: .../Homo_Mysticus_Sample_Chapters.html`

---

### Task 4: Update Automated Test Suite & Quality Gate (`tests/test_faur_reader_ui.py` & `scripts/verify_faur_integration.py`)

**Files:**
- Modify: `tests/test_faur_reader_ui.py`
- Modify: `scripts/verify_faur_integration.py`

**Step 1: Update `tests/test_faur_reader_ui.py` and `scripts/verify_faur_integration.py` to test the Unified Top Collapsible Box UI**

Update assertions in both files to verify:
1. `.chapter-header` contains `.chapter-header-row` and `#btn-chapter-faur` (`.faur-inline-btn`) inline with `<h2>Part 1 - Chapter 5</h2>`.
2. `#faur-top-box` (`.faur-top-box`) is rendered immediately after `.chapter-header` and **before** the first `.parallel-row`.
3. Zero `.faur-margin-anchor`, zero `.faur-popover`, zero `.faur-postscript-container`, and zero `Homo Mysticus, pp.` strings exist in the rendered chapter HTML.
4. Every subsection opens with the exact citation `Homo Mysticus, Chapter ## - [[Subtitle/Section]]` (e.g., `Homo Mysticus, Chapter 2 - Anthropocentric Theology`, `Homo Mysticus, Chapter 3 - The Fault with Aristotle` in Ch 5; `Homo Mysticus, Chapter 3 - In Search of the Ultimate Reality` in Ch 71).
5. Calling `toggleFaurTopBox()` toggles `.open` on `#faur-top-box` and `aria-expanded="true"|"false"` on `#btn-chapter-faur`.
6. Calling `showFn('fn.faur.part-1---chapter-5.fn_part-two_183')` opens `#fn-panel` with `"Faur's Note:"`.

**Step 2: Run `pytest` and `scripts/verify_faur_integration.py`**

Run: `pytest tests/test_faur_reader_ui.py -v && python3 scripts/verify_faur_integration.py`
Expected: PASS on all pytest tests and all 5 quality gates in `verify_faur_integration.py`.

---

### Task 5: Multi-Viewport CDP Browser Click-Around Audit Script (`scripts/capture_faur_multiviewport_audit.cjs`)

**Files:**
- Create: `scripts/capture_faur_multiviewport_audit.cjs`

**Step 1: Write `scripts/capture_faur_multiviewport_audit.cjs` to drive headless Chrome across Desktop, iPad Mini, and iPhone iOS Safari**

Create `scripts/capture_faur_multiviewport_audit.cjs` using `Emulation.setDeviceMetricsOverride`, `Emulation.setTouchEmulationEnabled`, and `Emulation.setUserAgentOverride` across three explicit viewports:
1. `desktop` (`1440x900`, `deviceScaleFactor: 2`, `mobile: false`)
2. `ipad_mini` (`768x1024`, `deviceScaleFactor: 2`, `mobile: true`, iPadOS Safari UA)
3. `iphone_ios_safari` (`390x844`, `deviceScaleFactor: 3`, `mobile: true`, iPhone iOS Safari UA)

At each viewport, the script must execute the following interactive click-around sequence and save PNG screenshots to `scratch/faur_multiviewport_audit/`:
1. **Load `Homo_Mysticus_Sample_Chapters.html` (Part 1 - Chapter 5 initial collapsed state)**:
   - Assert `#btn-chapter-faur` is visible inline with `<h2>Part 1 - Chapter 5</h2>` (check vertical center alignment delta `< 12px` on same line and touch target height `>= 44px`).
   - Assert `#faur-top-box` has `getComputedStyle(el).display === 'none'`.
   - Measure `row0TopBefore = document.querySelector('.parallel-row').getBoundingClientRect().top`.
   - Capture `01_<viewport>_ch5_collapsed.png`.
2. **Click inline `❦ HM` button (`#btn-chapter-faur`) to expand full-width box**:
   - Assert `#faur-top-box` has `getComputedStyle(el).display === 'block'`.
   - Measure `row0TopAfter = document.querySelector('.parallel-row').getBoundingClientRect().top` and assert `row0TopAfter - row0TopBefore > 200` (proving `.parallel-row` was pushed down by the full-width box).
   - Assert first `.faur-subsection-citation` text is `"Homo Mysticus, Chapter 2 - Anthropocentric Theology"` and `#faur-top-box` contains zero `"pp."` page ranges.
   - Capture `02_<viewport>_ch5_expanded_sub1.png`.
3. **Click 3rd subsection tab (`Homo Mysticus, Chapter 3 - The Fault with Aristotle`)**:
   - Click `.faur-subsection-tab` index 2.
   - Assert active subsection displays `"Homo Mysticus, Chapter 3 - The Fault with Aristotle"` and key terms `rayyis` (`רייס אלפלאספה`) and `aṣīle` (`אצילי בני ישראל`).
   - Capture `03_<viewport>_ch5_sub3_rayyis.png`.
4. **Click a footnote callout inside `#faur-top-box`**:
   - Click first visible `.faur-fn-ref` inside the open subsection.
   - Assert `#fn-panel` has class `open` and displays `"Faur's Note:"`.
   - Capture `04_<viewport>_ch5_footnote_open.png`, then close `#fn-panel`.
5. **Switch to Sepia and Dark themes while `#faur-top-box` is open**:
   - Call `setTheme('sepia')`, capture `05_<viewport>_ch5_sepia.png`.
   - Call `setTheme('dark')`, capture `06_<viewport>_ch5_dark.png`.
   - Restore `setTheme('light')`.
6. **Switch sample chapter pill to Guide I:71 (`part-1---chapter-71`) and expand `#btn-chapter-faur`**:
   - Click `.sample-pill-btn[data-slug="part-1---chapter-71"]`, then click `#btn-chapter-faur`.
   - Assert citation reads `"Homo Mysticus, Chapter 3 - In Search of the Ultimate Reality"`.
   - Capture `07_<viewport>_ch71_expanded.png`.
7. **Navigate to `reader.html?ch=part-1---chapter-5` and expand `#btn-chapter-faur`**:
   - Measure `row0TopBefore` vs `row0TopAfter`, assert push-down delta `> 200`, assert zero horizontal overflow (`document.documentElement.scrollWidth <= window.innerWidth`).
   - Capture `08_<viewport>_reader_ch5_expanded.png`.

**Step 2: Run `node scripts/capture_faur_multiviewport_audit.cjs`**

Run: `node scripts/capture_faur_multiviewport_audit.cjs`
Expected: 24 screenshots generated in `scratch/faur_multiviewport_audit/` and `ALL MULTI-VIEWPORT AUDIT CHECKS PASSED` printed to stdout.

---

### Task 6: Visual UI Critique Subagent Inspection & Polish Loop

**Files:**
- Inspect: `scratch/faur_multiviewport_audit/*.png` (24 screenshots across Desktop `1440x900`, iPad Mini `768x1024`, and iPhone iOS Safari `390x844`)

**Step 1: Dispatch Visual Critic Subagent (`frontend-architect` / `auditor-agent`) to inspect all captured screenshots**

The visual critic subagent must call `view_file` / `read_file` on the captured PNG screenshots across all 3 viewports and evaluate against a strict 6-point rubric:
1. **Inline Header Button Placement**: Is `❦ HM` (`#btn-chapter-faur`) cleanly aligned inline with `"Part 1 - Chapter 5"` without awkward wrapping or baseline misalignment?
2. **Full-Width Push-Down Box Geometry**: Does `#faur-top-box` span the full content width matching `.parallel-row` below it, pushing down the chapter text cleanly without overlapping or floating over any text?
3. **Citation & Subsection Hierarchy**: Does every subsection visibly open with `Homo Mysticus, Chapter ## - [[Subtitle/Section]]` with zero `pp.` page ranges and zero duplicated opening paragraphs?
4. **Touch Targets & Mobile Ergonomics (iPad Mini `768x1024` & iPhone `390x844`)**: Are `.faur-inline-btn`, `.faur-subsection-tab`, `.faur-subsection-header`, and `.sample-pill-btn` at least `44px` tall, legible, and free of horizontal overflow or cramped borders?
5. **Footnote Drawer Harmony**: When `#fn-panel` opens for `"Faur's Note:"`, is it cleanly readable above the bottom safe area without clipping?
6. **Theme Contrast (Light, Sepia, Dark)**: Do borders, key-term badges, and citations maintain crisp contrast across all 3 themes?

**Step 2: Remediate any visual critiques found and re-run verification**

If the visual critic subagent flags any spacing, typography, alignment, or responsive layout defects:
1. Dispatch `editor-agent` to fix the CSS/JS in `css/reader.css`, `js/reader.js`, and `Homo_Mysticus_Sample_Chapters.html` (and sync `dist/`).
2. Re-run `node scripts/capture_faur_multiviewport_audit.cjs`, `pytest tests/test_faur_reader_ui.py -v`, and `python3 scripts/verify_faur_integration.py` until all automated checks and visual inspections pass with zero defects.
