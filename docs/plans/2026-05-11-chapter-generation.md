# Chapter-by-Chapter HTML Generation Implementation Plan

> **For Antigravity:** REQUIRED SUB-SKILL: Load executing-plans to implement this plan task-by-task.

**Goal:** Refactor the build pipeline to generate individual HTML pages for each chapter of the Munk Viewer, improving performance and enabling direct URL sharing.

**Architecture:** We will modify the Python build script (`build_full_viewer.py`) to output files into a `viewer/` directory. The monolithic HTML template will be refactored so that each chapter gets its own `[chapter-name].html` file, with `index.html` serving as the Table of Contents. We will also inject Next/Previous navigation links into each page and update the JavaScript routing to use actual URLs instead of DOM hiding/showing.

**Tech Stack:** Python (build script), HTML/CSS/Vanilla JS (viewer interface).

---

### Task 1: Create the Output Directory

**Files:**
- Modify: `build_full_viewer.py`

**Step 1: Add directory creation logic**
Add code near the start of `build_full_viewer.py` to ensure a `viewer/` directory exists where the generated HTML files will be saved.

```python
import os

# Create output directory
os.makedirs("viewer", exist_ok=True)
```

**Step 2: Run script to verify directory creation**
Run: `python3 build_full_viewer.py`
Expected: A `viewer/` directory is created.

**Step 3: Commit**
```bash
git add build_full_viewer.py
git commit -m "chore: setup viewer output directory"
```

### Task 2: Refactor Filename Generation

**Files:**
- Modify: `build_full_viewer.py`

**Step 1: Add a filename helper**
Create a function to safely convert chapter titles into URL-friendly filenames.

```python
def get_filename(title):
    if title == "Contents":
        return "index.html"
    return title.replace(' ', '-').replace('/', '-').replace('.', '') + ".html"
```

**Step 2: Run script to verify no syntax errors**
Run: `python3 build_full_viewer.py`
Expected: Script completes successfully.

**Step 3: Commit**
```bash
git add build_full_viewer.py
git commit -m "feat: add filename generation helper"
```

### Task 3: Refactor the HTML Template into a Function

**Files:**
- Modify: `build_full_viewer.py`

**Step 1: Create the render_html function**
Extract the massive `html_template` string at the bottom of the script into a reusable function: `def render_html(page_title, main_content_html, chapter_index_js, footnotes_json):`. 
Replace the hardcoded `{rows_html}` and `{toc_landing_html}` with the passed `main_content_html`.

**Step 2: Update JavaScript Navigation**
Inside the extracted `render_html` function's `<script>` tag, modify the `navigateToChapter` function to navigate via URLs instead of manipulating `display: none`:
```javascript
function navigateToChapter(title) {
    const filename = title === "Contents" ? "index.html" : title.replace(/ /g, '-').replace(/\\//g, '-').replace(/\\./g, '') + ".html";
    window.location.href = filename;
}
```

**Step 3: Run script to verify syntax**
Run: `python3 build_full_viewer.py`
Expected: Script completes successfully.

**Step 4: Commit**
```bash
git add build_full_viewer.py
git commit -m "refactor: extract html template to function and update JS routing"
```

### Task 4: Add Next/Previous Navigation UI

**Files:**
- Modify: `build_full_viewer.py`

**Step 1: Create a Navigation Component**
Write a helper function `generate_nav_links(prev_ch, next_ch)` that returns HTML for Next/Previous buttons to be appended at the bottom of a chapter.

```python
def generate_nav_links(prev_ch, next_ch):
    html = '<div class="chapter-nav" style="display:flex; justify-content:space-between; margin-top:40px; padding-top:20px; border-top:1px solid var(--border);">'
    if prev_ch:
        html += f'<a href="{get_filename(prev_ch["title"])}" class="nav-btn">← Previous: {prev_ch["title"]}</a>'
    else:
        html += '<div></div>'
        
    if next_ch:
        html += f'<a href="{get_filename(next_ch["title"])}" class="nav-btn">Next: {next_ch["title"]} →</a>'
    else:
        html += '<div></div>'
    html += '</div>'
    return html
```

**Step 2: Commit**
```bash
git add build_full_viewer.py
git commit -m "feat: add next/previous navigation generation"
```

### Task 5: Generate Individual Chapter Files

**Files:**
- Modify: `build_full_viewer.py`

**Step 1: Write the loop to output chapter files**
Instead of concatenating `rows_html` for all chapters, loop through `unified_chapters`. For each chapter, determine `prev_ch` and `next_ch`, generate its specific `rows_html`, append the `generate_nav_links` output, and call `render_html()`.
Write the output to `viewer/{get_filename(ch['title'])}`.

**Step 2: Write the index.html**
Generate the TOC landing page HTML (as it currently exists) and wrap it using `render_html("Contents", toc_landing_html, ...)`.
Write it to `viewer/index.html`.

**Step 3: Run the build script**
Run: `python3 build_full_viewer.py`
Expected: The `viewer/` directory is populated with `index.html` and a `.html` file for every chapter. Open `viewer/index.html` in a browser to verify.

**Step 4: Commit**
```bash
git add build_full_viewer.py
git commit -m "feat: generate individual chapter html files"
```
