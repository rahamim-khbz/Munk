# Section-Specific Selection Refinement Implementation Plan

> **For Antigravity:** REQUIRED SUB-SKILL: Load executing-plans to implement this plan task-by-task.

**Goal:** Implement specialized default forcing (French/English) and variant grayouts for Munk reader sections while persistently caching and restoring prior custom selections across standard chapters.

**Architecture:** We introduce global tracking variables `previousStandardLeft` and `previousStandardRight` to cache layout preferences. Navigation scripts evaluate target section titles to dynamically toggle column configuration panel visibility on landing pages, apply grayscale disables to unpopulated variants, force defaults for specialized segments, and automatically restore custom multi-variant configurations.

**Tech Stack:** Python, HTML, Vanilla JS

---

## Path Convention
All generation files reside directly in the workspace project directory. Test validation scripts live inside `tests/` and are executed directly using Python interpreters.

---

### Task 1: Update Test Suite to Expect Specialized Forcing Logic

**Files:**
- Modify: `tests/test_viewer_toggles.py`

**Step 1: Write the failing test assertions**
Extend `test_spa_output()` to verify layout cache variables, Munk section predicate matching, grayscale disables, default forcing statements, and contextual masking logic.

```python
import os

def test_spa_output():
    output_path = "Munk Viewer.html"
    assert os.path.exists(output_path), f"Master output file {output_path} not found"
    
    with open(output_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Check for container data attributes
    assert 'data-left-col=' in content, "data-left-col attribute missing"
    assert 'data-right-col=' in content, "data-right-col attribute missing"
    
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
    
    # Check for layout state cache persistence strings
    assert 'let previousStandardLeft =' in content and 'let previousStandardRight =' in content, "Layout persistence tracking variables missing"
    
    # Check for contextual TOC column panel masking on landing page
    assert 'columnPanel.style.display =' in content, "Contextual TOC column panel masking logic missing"
    
    # Check for Munk section identification predicates and specialized default forcing
    assert 'const isMunkSection =' in content, "Munk section identification checks missing"
    assert 'previousStandardLeft = leftSel.value;' in content, "Caching of active dropdown values prior to Munk section activation missing"
    assert 'leftSel.value = previousStandardLeft;' in content, "Restoration of cached values when returning to standard sections missing"

if __name__ == "__main__":
    test_spa_output()
```

**Step 2: Run test to verify it fails**
Run: `venv/bin/python tests/test_viewer_toggles.py`  
Expected: FAIL with assertion errors indicating missing tracking variables or predicate checks.

**Step 3: Commit**
```bash
git add tests/test_viewer_toggles.py
git commit -m "test: add layout persistence and specialized section default assertions"
```

---

### Task 2: Inject Persistence Variables and Contextual Panel Masking

**Files:**
- Modify: `build_full_viewer.py`

**Step 1: Declare global memory variables and toggle panel display**
Modify `build_full_viewer.py` to inject `previousStandardLeft` and `previousStandardRight` variables into the master script scope, and add logic to dynamically set `columnPanel.style.display` based on whether the activated section title is `'Contents'`.

```javascript
        let previousStandardLeft = 'en';
        let previousStandardRight = 'makbili';
        
        function updateColumnSelectors() {
```

Inside `navigateToChapter(title)`:
```javascript
            // Dynamically hide column configuration panel on landing page
            const columnPanel = document.querySelector('.toc-column-panel');
            if (columnPanel) {
                columnPanel.style.display = (title === 'Contents') ? 'none' : 'block';
            }
```

**Step 2: Commit**
```bash
git add build_full_viewer.py
git commit -m "feat: declare persistent tracking variables and add dynamic panel masking"
```

---

### Task 3: Refactor Section-Specific Variant Filtering and Forcing Routing

**Files:**
- Modify: `build_full_viewer.py`

**Step 1: Implement dynamic default forcing and grayscale filtering**
Inside `navigateToChapter(title)`, replace old static sub-variant validation with comprehensive Munk section routing checks.

```javascript
            // Dynamic variant navigation validation, grayscale filtering & persistent default forcing
            const isMunkSection = title.startsWith('Introduction to Volume') || 
                                  title === 'Note On The Title' || 
                                  title.startsWith('Endnotes to Volume');
            const restrictedVariants = ['makbili', 'tibon', 'jrb'];
            
            const leftSel = document.getElementById('select-left-col');
            const rightSel = document.getElementById('select-right-col');
            
            if (leftSel && rightSel) {
                // Determine if we are currently inside a standard multi-variant view prior to this navigation
                const wasInStandardSection = !activeChapterId || (!activeChapterId.includes('Introduction-to-Volume') && 
                                                                  !activeChapterId.includes('Note-On-The-Title') && 
                                                                  !activeChapterId.includes('Endnotes-to-Volume'));
                
                // Process grayscale filtering: gray out restricted original choices in Munk segments
                [leftSel, rightSel].forEach(sel => {
                    Array.from(sel.options).forEach(opt => {
                        if (restrictedVariants.includes(opt.value)) {
                            opt.disabled = isMunkSection;
                        } else {
                            opt.disabled = false;
                        }
                    });
                });
                
                // Enforce section-specific default mapping alignment
                if (isMunkSection) {
                    // Cache prior custom multi-variant configurations only if leaving a standard section
                    if (wasInStandardSection && title !== 'Contents') {
                        previousStandardLeft = leftSel.value;
                        previousStandardRight = rightSel.value;
                    }
                    // Force specific defaults for Munk prefaces and endnotes
                    leftSel.value = 'fr';
                    rightSel.value = 'en';
                } else if (title !== 'Contents') {
                    // Restore custom multi-variant configurations directly from internal cache variables
                    leftSel.value = previousStandardLeft;
                    rightSel.value = previousStandardRight;
                }
                
                // Synchronize main container CSS reveal tokens and opposite column grayouts
                updateColumnSelectors();
            }
```

**Step 2: Commit**
```bash
git add build_full_viewer.py
git commit -m "feat: apply specialized section default forcing and grayscale option masks"
```

---

### Task 4: Execute SPA Compilation Pipeline & Verify Success

**Step 1: Compile application artifact**
Run: `venv/bin/python build_full_viewer.py`  
Expected: Clean compilation summary reporting complete HTML SPA file production.

**Step 2: Execute assertions check suite**
Run: `venv/bin/python tests/test_viewer_toggles.py`  
Expected: PASS output for all data attributes, tracking flags, forcing logic, and dynamic masking checks.

**Step 3: Commit master bundle**
```bash
git add "Munk Viewer.html"
git commit -m "build: compile updated bundle featuring specialized defaults and layout persistence"
```
