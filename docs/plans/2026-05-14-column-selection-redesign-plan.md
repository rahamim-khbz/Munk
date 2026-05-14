# Universal Column Selection Redesign Implementation Plan

> **For Antigravity:** REQUIRED SUB-SKILL: Load executing-plans to implement this plan task-by-task.

**Goal:** Refactor the Munk Parallel Reader to support symmetrical multi-variant translation column assignment via a pure CSS display engine controlled from the TOC drawer.

**Architecture:** We update `build_full_viewer.py` to output identical `.left-cell` and `.right-cell` DOM nodes embedding all five translation variants. CSS attributes govern view state and responsive mobile soft line insertion, while a central JS module enforces mutual dropdown exclusion and dynamic auto-switch section navigation.

**Tech Stack:** Python, HTML, Vanilla CSS, Vanilla JS

---

## Path Convention
All source and viewer build files map directly to the root project working directory. Test files reside within the `tests/` directory and are executed via `pytest`.

---

### Task 1: Update Test Suite to Expect Symmetrical Layout Attributes

**Files:**
- Modify: `tests/test_viewer_toggles.py`

**Step 1: Write the failing test assertions**
Update `test_spa_output()` to assert new symmetrical container data attributes, updated left/right cell classes, drawer control integration, and JS logic presence.

```python
import os

def test_spa_output():
    output_path = "Munk Viewer.html"
    assert os.path.exists(output_path), f"Master output file {output_path} not found"
    
    with open(output_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Check for container data attributes
    assert 'data-left-col="en"' in content, "data-left-col attribute missing"
    assert 'data-right-col="makbili"' in content, "data-right-col attribute missing"
    
    # Check for TOC drawer column layout panel integration
    assert 'id="select-left-col"' in content and 'id="select-right-col"' in content, "Left/Right column dropdowns missing"
    
    # Check for new symmetrical cell wrapper classes
    assert 'class="left-cell"' in content and 'class="right-cell"' in content, "Symmetrical cell containers missing"
    
    # Check for pure CSS visibility rules targeting left/right cell spans
    assert '.left-cell .variant-en' in content, "Pure CSS visibility rules for variant-en missing"
    assert '.right-cell .variant-makbili' in content, "Pure CSS visibility rules for variant-makbili missing"
    
    # Check for JS mutual exclusion coordination function
    assert 'function updateColumnSelectors()' in content, "updateColumnSelectors JS logic missing"
    
    # Check for responsive mobile vertical stacking viewport override with soft divider
    assert '@media (max-width: 768px)' in content, "Mobile stacking viewport overrides missing"
    assert '.right-cell {' in content and 'border-top:' in content, "Mobile view right-cell soft line divider rule missing"

if __name__ == "__main__":
    test_spa_output()
```

**Step 2: Run test to verify it fails**
Run: `pytest tests/test_viewer_toggles.py -v`  
Expected: FAIL with assertion errors indicating missing `data-left-col` attributes or layout class structures.

**Step 3: Commit**
```bash
git add tests/test_viewer_toggles.py
git commit -m "test: update spa output assertions for universal column redesign"
```

---

### Task 2: Implement TOC Drawer Selection Layout Controls

**Files:**
- Modify: `build_full_viewer.py`

**Step 1: Relocate controls to TOC drawer**
Modify `build_full_viewer.py` HTML template string:
1. Update `.main-container` initial attributes to `data-left-col="en" data-right-col="makbili"`.
2. Remove the legacy `.column-selectors-bar` section entirely from `.content`.
3. Insert the **Column Layout Panel** directly inside `#toc-drawer` below the mobile theme panel, featuring standardized options with approved simplified display labels.

```html
        <div class="toc-column-panel" style="padding: 16px 20px; border-bottom: 1px solid var(--border); background: var(--header-bg);">
            <div style="display: flex; flex-direction: column; gap: 12px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <label for="select-left-col" style="font-size: 0.8rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Left Column</label>
                    <select id="select-left-col" onchange="updateColumnSelectors()" style="padding: 6px 10px; border-radius: 6px; border: 1px solid var(--border); background: var(--surface); color: var(--text); font-size: 0.9rem; font-weight: 600; cursor: pointer; outline: none; width: 160px;">
                        <option value="en" selected>Munk (AI-English)</option>
                        <option value="fr">Munk (French)</option>
                        <option value="makbili">מקבילי</option>
                        <option value="tibon">אבן תיבון</option>
                        <option value="jrb">Judeo-Arabic</option>
                    </select>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <label for="select-right-col" style="font-size: 0.8rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Right Column</label>
                    <select id="select-right-col" onchange="updateColumnSelectors()" style="padding: 6px 10px; border-radius: 6px; border: 1px solid var(--border); background: var(--surface); color: var(--text); font-size: 0.9rem; font-weight: 600; cursor: pointer; outline: none; width: 160px;">
                        <option value="en">Munk (AI-English)</option>
                        <option value="fr">Munk (French)</option>
                        <option value="makbili" selected>מקבילי</option>
                        <option value="tibon">אבן תי-בון</option>
                        <option value="jrb">Judeo-Arabic</option>
                    </select>
                </div>
            </div>
        </div>
```

**Step 2: Commit**
```bash
git add build_full_viewer.py
git commit -m "feat: embed universal column selection controls into TOC drawer"
```

---

### Task 3: Refactor Pure CSS Engine & Symmetrical DOM Row Output

**Files:**
- Modify: `build_full_viewer.py`

**Step 1: Update CSS visibility, decoupled typography, and mobile soft divider**
Replace old dynamic visibility rules inside the `<style>` block with decoupled `.variant-*` styling classes and unified cell display rules:

```css
        /* Dynamic Symmetrical Column Visibility Rules */
        .left-cell .variant-span, .right-cell .variant-span { display: none; }
        
        .main-container[data-left-col="en"] .left-cell .variant-en { display: block; }
        .main-container[data-left-col="fr"] .left-cell .variant-fr { display: block; }
        .main-container[data-left-col="makbili"] .left-cell .variant-makbili { display: block; }
        .main-container[data-left-col="tibon"] .left-cell .variant-tibon { display: block; }
        .main-container[data-left-col="jrb"] .left-cell .variant-jrb { display: block; }

        .main-container[data-right-col="en"] .right-cell .variant-en { display: block; }
        .main-container[data-right-col="fr"] .right-cell .variant-fr { display: block; }
        .main-container[data-right-col="makbili"] .right-cell .variant-makbili { display: block; }
        .main-container[data-right-col="tibon"] .right-cell .variant-tibon { display: block; }
        .main-container[data-right-col="jrb"] .right-cell .variant-jrb { display: block; }

        /* Decoupled Variant Typography & Direction Rules */
        .variant-en { font-family: var(--font-english), var(--font-hebrew); font-size: 1.1rem; line-height: 1.7; text-align: left; direction: ltr; }
        .variant-fr { font-family: var(--font-english); font-size: 1.1rem; line-height: 1.7; text-align: left; direction: ltr; }
        .variant-makbili { font-family: var(--font-hebrew); font-size: 1.3rem; line-height: 1.6; text-align: right; direction: rtl; color: var(--text); }
        .variant-tibon { font-family: var(--font-hebrew); font-size: 1.3rem; line-height: 1.6; text-align: right; direction: rtl; color: var(--text); }
        .variant-jrb { font-family: var(--font-hebrew); font-size: 1.3rem; line-height: 1.6; text-align: right; direction: rtl; color: var(--text); }

        .left-cell, .right-cell { width: 100%; box-sizing: border-box; }

        /* Responsive Mobile Vertical Stacking with Soft Divider */
        @media (max-width: 768px) {
            .parallel-row { display: flex; flex-direction: column; gap: 16px; padding: 20px 0; }
            .right-cell { border-top: 1px solid var(--border); padding-top: 12px; }
            .chapter-header { padding: 24px 0 12px; order: -2; }
            .chapter-header h2 { font-size: 1.4rem; }
            .content { padding: 10px 16px; }
        }
```

**Step 2: Update `render_row()` generation output**
Update `render_row()` logic to wrap all extracted variant spans symmetrically inside both `.left-cell` and `.right-cell`.

```python
        return f"""
        <div class="parallel-row" {row_id}>
            <div class="left-cell">
                <span class="variant-span variant-en">{en_text}</span>
                <span class="variant-span variant-fr">{fr_processed}</span>
                <span class="variant-span variant-makbili">{repair_tags(clean_he)}</span>
                <span class="variant-span variant-jrb">{repair_tags(jrb_text)}</span>
                <span class="variant-span variant-tibon">{repair_tags(tibon_text)}</span>
            </div>
            <div class="right-cell">
                <span class="variant-span variant-en">{en_text}</span>
                <span class="variant-span variant-fr">{fr_processed}</span>
                <span class="variant-span variant-makbili">{repair_tags(clean_he)}</span>
                <span class="variant-span variant-jrb">{repair_tags(jrb_text)}</span>
                <span class="variant-span variant-tibon">{repair_tags(tibon_text)}</span>
            </div>
        </div>
        """
```

**Step 3: Commit**
```bash
git add build_full_viewer.py
git commit -m "feat: implement pure CSS layout switching engine and symmetrical cell rendering"
```

---

### Task 4: Implement JS Control Logic for Mutual Exclusion & Auto-Switch Navigation

**Files:**
- Modify: `build_full_viewer.py`

**Step 1: Inject JS modules**
Inside the primary `<script>` block of `build_full_viewer.py`, define `updateColumnSelectors()` and update `navigateToChapter()` logic.

```javascript
        function updateColumnSelectors() {
            const leftSel = document.getElementById('select-left-col');
            const rightSel = document.getElementById('select-right-col');
            if (!leftSel || !rightSel) return;
            
            const leftVal = leftSel.value;
            const rightVal = rightSel.value;
            
            // Update pure CSS engine layout data attributes
            const mainCont = document.querySelector('.main-container');
            if (mainCont) {
                mainCont.setAttribute('data-left-col', leftVal);
                mainCont.setAttribute('data-right-col', rightVal);
            }
            
            // Apply mutual exclusion: disable selected choices in opposite dropdowns
            Array.from(leftSel.options).forEach(opt => {
                opt.disabled = (opt.value === rightVal);
            });
            Array.from(rightSel.options).forEach(opt => {
                opt.disabled = (opt.value === leftVal);
            });
        }

        function navigateToChapter(title) {
            const id = title === 'Contents' ? 'chapter-Contents' : 'chapter-' + title.replace(/ /g, '-').replace(/\//g, '-').replace(/\./g, '');
            document.querySelectorAll('.chapter-section').forEach(s => {
                s.style.display = s.id === id ? 'block' : 'none';
            });
            activeChapterId = id;
            const titleElem = document.getElementById('main-title');
            if (titleElem) titleElem.textContent = title;
            
            document.querySelectorAll('.toc-tile').forEach(t => {
                t.classList.toggle('active', t.dataset.chapterId === id);
            });
            
            // Dynamic variant navigation validation & fallback auto-switching
            const isRestrictedSection = title.startsWith('Introduction to Volume') || title === 'Note On The Title' || title.startsWith('Endnotes to Volume');
            const restrictedVariants = ['makbili', 'tibon', 'jrb'];
            
            const leftSel = document.getElementById('select-left-col');
            const rightSel = document.getElementById('select-right-col');
            
            if (leftSel && rightSel) {
                // Dynamically disable/enable specific variant options based on loaded chapter availability
                [leftSel, rightSel].forEach(sel => {
                    Array.from(sel.options).forEach(opt => {
                        if (restrictedVariants.includes(opt.value)) {
                            // If restricted section, option is unavailable entirely
                            if (isRestrictedSection) {
                                opt.disabled = true;
                            }
                        }
                    });
                });
                
                // Fallback auto-switching validation (Option A)
                if (isRestrictedSection) {
                    if (restrictedVariants.includes(leftSel.value)) {
                        // Reassign left column to an available active language
                        leftSel.value = (rightSel.value === 'en') ? 'fr' : 'en';
                    }
                    if (restrictedVariants.includes(rightSel.value)) {
                        // Reassign right column to an available active language
                        rightSel.value = (leftSel.value === 'fr') ? 'en' : 'fr';
                    }
                }
                
                // Trigger mutual exclusion coordination synchronization
                updateColumnSelectors();
            }
            
            const drawer = document.getElementById('toc-drawer');
            if (drawer && drawer.classList.contains('open')) toggleTOC();
            const mainCont = document.querySelector('.main-container');
            if (mainCont) mainCont.scrollTop = 0;
        }

        window.addEventListener('DOMContentLoaded', () => { 
            buildTOC(); 
            navigateToChapter('Contents'); 
            updateColumnSelectors(); 
        });
```

**Step 2: Commit**
```bash
git add build_full_viewer.py
git commit -m "feat: add JS mutual exclusion checks and dynamic section fallback auto-switching"
```

---

### Task 5: Execute Compilation Pipeline & Validate Success

**Step 1: Execute production build generation**
Run: `python build_full_viewer.py`  
Expected: Output status indicating successful SPA output bundle compilation.

**Step 2: Verify passing test suite**
Run: `pytest tests/test_viewer_toggles.py -v`  
Expected: PASS output for all layout checks, selectors integration, and CSS assertion targets.

**Step 3: Commit final bundle**
```bash
git add "Munk Viewer.html"
git commit -m "build: compile updated premium single-page parallel viewer bundle"
```
