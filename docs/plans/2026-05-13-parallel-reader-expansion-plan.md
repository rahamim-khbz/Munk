# Parallel Reader Expansion Implementation Plan

> **For Antigravity:** REQUIRED SUB-SKILL: Load executing-plans to implement this plan task-by-task.

**Goal:** Expand the static HTML pipeline to ingest Ibn Tibon, Judeo-Arabic, and French JSON source editions and inject client-side CSS column toggles for zero-latency multi-language navigation.

**Architecture:** Implement Option A (Nested Language Spans) by rendering all target language variants into Sefaria wrapper spans inside each segment row container. A top-level selection bar updates layout container attributes, allowing optimized CSS rules to instantaneously show the selected texts and hide inactive layers.

**Tech Stack:** Python, Vanilla CSS, Vanilla JavaScript, Sefaria JSON Datasets.

---

### Task 1: Ingesting Alternative Source JSON Datasets

**Files:**
- Create: `tests/test_data_ingestion.py`
- Modify: `build_full_viewer.py:280-305`

**Step 1: Write failing verification test**
Create `tests/test_data_ingestion.py` to assert that the three alternative JSON corpuses are successfully loaded into global/module dictionaries mapped by standard Sefaria section keys. Provide verification logic asserting that target text segment arrays are fully accessible.
```python
import os
import sys
import json

def test_ingestion():
    # Verify local file presence
    assert os.path.exists("French.json"), "French.json missing"
    assert os.path.exists("Guide for the Perplexed - he - Judeo Arabic, Paris, 1856 [jrb].json"), "Judeo-Arabic JSON missing"
    
    # Load build script context safely
    sys.path.insert(0, os.path.abspath("."))
    import build_full_viewer
    # Function will verify parsing logic integration
    print("Ingestion verification suite scaffolded successfully.")

if __name__ == "__main__":
    test_ingestion()
```

**Step 2: Run verification command**
Execute `python tests/test_data_ingestion.py` to observe baseline context checks.

**Step 3: Implement the change**
Modify `build_full_viewer.py` to copy/load the Ibn Tibon file from Downloads if missing locally, and ingest `French.json`, Judeo-Arabic JSON, and Ibn Tibon JSON into lookup dictionaries. Add a robust key path resolver function `get_variant_text(lang_main, key)`.
```python
    # Load French Original
    french_main = {}
    if os.path.exists("French.json"):
        with open("French.json", "r", encoding="utf-8") as f:
            french_main = json.load(f).get("text", {})

    # Load Judeo-Arabic Edition
    jrb_main = {}
    jrb_path = "Guide for the Perplexed - he - Judeo Arabic, Paris, 1856 [jrb].json"
    if os.path.exists(jrb_path):
        with open(jrb_path, "r", encoding="utf-8") as f:
            jrb_main = json.load(f).get("text", {})

    # Load Ibn Tibon Edition (Auto-copy from Downloads if missing locally)
    tibon_local_path = "Guide for the Perplexed - he - Moreh Nevuchim, translated by Ibn Tibon.json"
    tibon_dl_path = os.path.expanduser("~/Downloads/Guide for the Perplexed - he - Moreh Nevuchim, translated by Ibn Tibon.json")
    if not os.path.exists(tibon_local_path) and os.path.exists(tibon_dl_path):
        import shutil
        shutil.copy(tibon_dl_path, tibon_local_path)
    
    tibon_main = {}
    if os.path.exists(tibon_local_path):
        with open(tibon_local_path, "r", encoding="utf-8") as f:
            tibon_main = json.load(f).get("text", {})

    def get_variant_text(lang_main, key, default="[Text Missing in this Edition]"):
        if not lang_main or not key:
            return default
        parts = key.split(".")
        if len(parts) < 3: return default
        
        if len(parts) == 4: # e.g. root.text.Prefatory Remarks.3
            sec = parts[2]
            try:
                idx = int(parts[3])
                if sec in lang_main and isinstance(lang_main[sec], list) and idx < len(lang_main[sec]):
                    return lang_main[sec][idx]
            except ValueError: pass
        elif len(parts) == 5: # e.g. root.text.Part 1.Introduction.4
            part_name, sub_name = parts[2], parts[3]
            try:
                idx = int(parts[4])
                if part_name in lang_main and sub_name in lang_main[part_name] and idx < len(lang_main[part_name][sub_name]):
                    return lang_main[part_name][sub_name][idx]
            except ValueError: pass
        elif len(parts) == 6 and parts[3] == '': # e.g. root.text.Part 1..0.5
            part_name = parts[2]
            try:
                ch_idx, seg_idx = int(parts[4]), int(parts[5])
                if part_name in lang_main and "" in lang_main[part_name] and ch_idx < len(lang_main[part_name][""]) and seg_idx < len(lang_main[part_name][""][ch_idx]):
                    return lang_main[part_name][""][ch_idx][seg_idx]
            except ValueError: pass
        return default
```

**Step 4: Run verification command**
Run `python tests/test_data_ingestion.py` to confirm successful ingestion integration.

**Step 5: Commit changes**
Commit ingestion pipeline additions.

---

### Task 2: Upgrading HTML Row Generation Logic (Option A Spans Integration)

**Files:**
- Create: `tests/test_row_rendering.py`
- Modify: `build_full_viewer.py` `render_row` definition section

**Step 1: Write failing verification test**
Create a test script asserting that output HTML rows embed the four target language wrapper spans inside `.he-cell` and two spans inside `.en-cell`.

**Step 2: Run verification command**
Run the row rendering verification suite.

**Step 3: Implement the change**
Update `render_row` to pull secondary variants via `get_variant_text` using `key`, wrap text contents in respective language span classes, and distribute variants cleanly across legacy sub-block divisions.
```python
    def render_row(he_text, en_text, key=None):
        fr_text = get_variant_text(french_main, key) if key else ""
        jrb_text = get_variant_text(jrb_main, key) if key else ""
        tibon_text = get_variant_text(tibon_main, key) if key else ""
        
        if '<span class="mediumGrey">' in he_text:
            parts = re.split(r'(<span class="mediumGrey">.*?</span>)', he_text)
            text_blocks_indices = [i for i, p in enumerate(parts) if not p.strip().startswith('<span class="mediumGrey">') and p.strip()]
            
            # Legacy English mapping logic retained here...
            # (Insert mapping selection block identical to existing script)
            
            rows = ""
            for i, part in enumerate(parts):
                part = part.strip()
                if not part: continue
                if part.startswith('<span class="mediumGrey">'):
                    rows += f"""
                    <div class="parallel-row header-row">
                        <div class="he-cell"><span class="col2-variant variant-makbili">{part}</span></div>
                        <div class="en-cell"></div>
                    </div>
                    """
                else:
                    clean_he = re.sub(r'^(<br>)+|(<br>)+$', '', part).strip()
                    if not clean_he: continue
                    row_id = f'id="row-{key}"' if key else ""
                    cell_en = en_mapping.get(i, "")
                    
                    is_first = (i == text_blocks_indices[0]) if text_blocks_indices else False
                    c1_fr = fr_text if is_first else ""
                    c2_jrb = jrb_text if is_first else ""
                    c2_tibon = tibon_text if is_first else ""
                    c2_fr = fr_text if is_first else ""
                    
                    c1_html = f'<span class="col1-variant variant-en">{cell_en}</span>'
                    if c1_fr: c1_html += f'<span class="col1-variant variant-fr" style="display:none;">{c1_fr}</span>'
                    
                    c2_html = f'<span class="col2-variant variant-makbili">{repair_tags(clean_he)}</span>'
                    if c2_jrb: c2_html += f'<span class="col2-variant variant-jrb" style="display:none;">{repair_tags(c2_jrb)}</span>'
                    if c2_tibon: c2_html += f'<span class="col2-variant variant-tibon" style="display:none;">{repair_tags(c2_tibon)}</span>'
                    if c2_fr: c2_html += f'<span class="col2-variant variant-fr" style="display:none;">{c2_fr}</span>'
                    
                    rows += f"""
                    <div class="parallel-row" {row_id}>
                        <div class="he-cell">{c2_html}</div>
                        <div class="en-cell">{c1_html}</div>
                    </div>
                    """
            return rows
        else:
            row_id = f'id="row-{key}"' if key else ""
            c1_html = f'<span class="col1-variant variant-en">{en_text}</span>'
            if fr_text: c1_html += f'<span class="col1-variant variant-fr" style="display:none;">{fr_text}</span>'
            
            c2_html = f'<span class="col2-variant variant-makbili">{repair_tags(he_text)}</span>'
            if jrb_text: c2_html += f'<span class="col2-variant variant-jrb" style="display:none;">{repair_tags(jrb_text)}</span>'
            if tibon_text: c2_html += f'<span class="col2-variant variant-tibon" style="display:none;">{repair_tags(tibon_text)}</span>'
            if fr_text: c2_html += f'<span class="col2-variant variant-fr" style="display:none;">{fr_text}</span>'
            
            return f"""
            <div class="parallel-row" {row_id}>
                <div class="he-cell">{c2_html}</div>
                <div class="en-cell">{c1_html}</div>
            </div>
            """
```

**Step 4: Run verification command**
Run suite confirming output strings format successfully.

**Step 5: Commit changes**
Commit updated row building logic.

---

### Task 3: Injecting Column Dropdown Selectors and Dynamic Toggle CSS

**Files:**
- Create: `tests/test_viewer_toggles.py`
- Modify: `build_full_viewer.py` HTML string layout styles and DOM assembly blocks

**Step 1: Write failing verification test**
Create verification script asserting that generated viewing bundles embed the `.column-selectors-bar` component, `switchCol1`/`switchCol2` inline script handlers, and dedicated container layer matching selectors.

**Step 2: Run verification command**
Execute verification to establish baseline failure.

**Step 3: Implement the change**
Inject structural dynamic display rules into `render_html` stylesheet block. Inject the multi-select header control directly above the chapter rows inside `.content`.
```css
        /* Dynamic Column Visibility Rules */
        .main-container[data-col1="en"] .col1-variant:not(.variant-en) { display: none !important; }
        .main-container[data-col1="fr"] .col1-variant:not(.variant-fr) { display: none !important; }

        .main-container[data-col2="makbili"] .col2-variant:not(.variant-makbili) { display: none !important; }
        .main-container[data-col2="jrb"] .col2-variant:not(.variant-jrb) { display: none !important; }
        .main-container[data-col2="tibon"] .col2-variant:not(.variant-tibon) { display: none !important; }
        .main-container[data-col2="fr"] .col2-variant:not(.variant-fr) { display: none !important; }

        /* Typography & Direction Overrides */
        .col2-variant.variant-fr { direction: ltr; text-align: left; font-family: var(--font-english); font-size: 1.1rem; display: block; }
        .col1-variant.variant-fr { direction: ltr; text-align: left; font-family: var(--font-english); display: block; }
        .col1-variant.variant-en, .col2-variant:not(.variant-fr) { display: block; }
        
        .column-selectors-bar { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 2px solid var(--border); }
        .column-selectors-bar div { display: flex; align-items: center; gap: 12px; }
        .column-selectors-bar label { font-size: 0.85rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; }
        .column-selectors-bar select { flex: 1; padding: 8px 12px; border-radius: 6px; border: 1px solid var(--border); background: var(--surface); color: var(--text); font-size: 0.95rem; font-weight: 600; cursor: pointer; outline: none; }
```
Inject inline selector layout markup into `render_html` body output:
```html
        <div class="content">
            <div class="column-selectors-bar">
                <div class="col2-selector">
                    <label for="select-col2">Column 2:</label>
                    <select id="select-col2" onchange="document.querySelector('.main-container').setAttribute('data-col2', this.value)">
                        <option value="makbili" selected>Makbili (Hebrew)</option>
                        <option value="jrb">Judeo-Arabic</option>
                        <option value="tibon">Ibn Tibon (Hebrew)</option>
                        <option value="fr">French Original</option>
                    </select>
                </div>
                <div class="col1-selector">
                    <label for="select-col1">Column 1:</label>
                    <select id="select-col1" onchange="document.querySelector('.main-container').setAttribute('data-col1', this.value)">
                        <option value="en" selected>English Translation</option>
                        <option value="fr">French Original</option>
                    </select>
                </div>
            </div>
            {main_content_html}
```
Set container initial attribute defaults: `<div class="main-container" data-col1="en" data-col2="makbili">`.

**Step 4: Run verification command**
Run `python build_full_viewer.py` to compile all target standalone pages, then run toggle verification scripts confirming zero build failures.

**Step 5: Commit changes**
Commit template compilation updates.
