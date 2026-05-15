# Munk's Endnotes Implementation Plan

> **For Antigravity:** REQUIRED SUB-SKILL: Load executing-plans to implement this plan task-by-task.

**Goal:** Create three distinct JSON endnote data files from the source text and integrate them into the static parallel viewer grouped under a dedicated category header in the Table of Contents.

**Architecture:** Housed alongside the introductory JSON prefaces, three dedicated storage files (`endnotes_vol1.json`, `endnotes_vol2.json`, `endnotes_vol3.json`) will maintain side-by-side scrolling parity by merging multi-paragraph internal note strings into cohesive single array items. The generation pipeline script (`build_full_viewer.py`) will ingest these files and inject dynamic TOC separator logic to produce beautifully structured HTML output pages.

**Tech Stack:** Python, JSON, Vanilla HTML/CSS.

---

### Task 1: Endnotes Structure Verification Setup

**Files:**
- Create: `test_endnotes_structure.py`

**Step 1: Write the failing verification test**
```python
import json
import os

def test_endnotes_files():
    files = ["endnotes_vol1.json", "endnotes_vol2.json", "endnotes_vol3.json"]
    for fn in files:
        assert os.path.exists(fn), f"{fn} does not exist"
        with open(fn, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "fr" in data, f"Missing 'fr' key in {fn}"
        assert "en" in data, f"Missing 'en' key in {fn}"
        assert len(data["fr"]) == len(data["en"]), f"Array mismatch in {fn}"
        assert len(data["fr"]) > 0, f"Empty array in {fn}"
    print("test_endnotes_structure passed successfully!")

if __name__ == "__main__":
    test_endnotes_files()
```

**Step 2: Run test to verify it fails**
Run: `./venv/bin/python test_endnotes_structure.py`  
Expected: `AssertionError: endnotes_vol1.json does not exist`

**Step 3: Commit verification script**
```bash
git add test_endnotes_structure.py
git commit -m "test: add structural verification suite for Endnotes integration"
```

---

### Task 2: Implement Endnotes Volume I Data File

**Files:**
- Create: `endnotes_vol1.json`

**Step 1: Create Volume I data set**
Transcribe all 16 distinct paired segments from Part I source text, wrapping italic sequences in `<em>` tags and combining internal multi-paragraph notes into single string slots.

**Step 2: Run verification test**
Run: `./venv/bin/python test_endnotes_structure.py`  
Expected: `AssertionError: endnotes_vol2.json does not exist` (verifying Vol 1 passes successfully)

**Step 3: Commit Volume I data file**
```bash
git add endnotes_vol1.json
git commit -m "feat: implement Volume I Endnotes parallel data set"
```

---

### Task 3: Implement Endnotes Volume II Data File

**Files:**
- Create: `endnotes_vol2.json`

**Step 1: Create Volume II data set**
Transcribe all aligned segment blocks from Part II source text, taking special care to combine multi-block items (e.g., Page 352 note 3) into single array slots.

**Step 2: Run verification test**
Run: `./venv/bin/python test_endnotes_structure.py`  
Expected: `AssertionError: endnotes_vol3.json does not exist`

**Step 3: Commit Volume II data file**
```bash
git add endnotes_vol2.json
git commit -m "feat: implement Volume II Endnotes parallel data set"
```

---

### Task 4: Implement Endnotes Volume III Data File

**Files:**
- Create: `endnotes_vol3.json`

**Step 1: Create Volume III data set**
Transcribe all aligned segments from Part III source text.

**Step 2: Run verification test**
Run: `./venv/bin/python test_endnotes_structure.py`  
Expected: `test_endnotes_structure passed successfully!`

**Step 3: Commit Volume III data file**
```bash
git add endnotes_vol3.json
git commit -m "feat: implement Volume III Endnotes parallel data set"
```

---

### Task 5: Pipeline Integration & Table of Contents Rendering

**Files:**
- Modify: `build_full_viewer.py`

**Step 1: Modify generation pipeline**
Inject loading sequences for all three endnote files right after the Preface Volume III block. Add logic inside the TOC building loops to output a category separator titled **"Munk's Endnotes"** immediately preceding the endnote sub-items.

**Step 2: Execute compilation script**
Run: `./venv/bin/python build_full_viewer.py`  
Expected: `Success! Multi-page viewer generated in "viewer/" directory.`

**Step 3: Commit pipeline changes**
```bash
git add build_full_viewer.py
git commit -m "feat: integrate Munk's Endnotes into static viewer TOC and build engine"
```
