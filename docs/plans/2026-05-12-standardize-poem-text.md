# Standardizing Poem Text Implementation Plan

> **For Antigravity:** REQUIRED SUB-SKILL: Load executing-plans to implement this plan task-by-task.

**Goal:** Standardize the English translation of the opening poem in the *Letter to R Joseph* to render as standard body text formatting without italics or CSS overrides across all output views.

**Architecture:** Modify `build_full_viewer.py` to remove inline `<i>` tags from the poem translation string and render the cell without the `.poem-segment` supplementary CSS class.

**Tech Stack:** Python 3, HTML5/CSS3.

---

### [COMPLETED] Task 1: Update Poem Fallback String & Cell Rendering Logic

**Files:**
- Modify: `build_full_viewer.py`

**Step 1: Implement the string and style updates**

Modify `build_full_viewer.py` around line 362 to remove inline `<i>` tags:
```python
    # Segment 1: Poem
    letter_segments.append({
        "he": poem_he,
        "en": get_en_text("root.text.Letter to R Joseph son of Judah.Poem", 'My thought will guide you on the path of truth, and smooth the way.<br>Come, walk along its path, O all you who wander in the field of religion!<br>The impure and the ignorant shall not pass over it; it shall be called the sacred way.'),
        "is_poem": True
    })
```

Modify `build_full_viewer.py` around line 573 to render the cell without the `poem-segment` supplementary class:
```python
                if seg.get("is_poem"):
                    chapter_rows_html += f"""
                    <div class="parallel-row poem-row">
                        <div class="en-cell">{en_processed}</div>
                        <div class="he-cell">{seg['he']}</div>
                    </div>
                    """
```

**Step 2: Execute build script to verify successful regeneration**

Run: `./venv/bin/python build_full_viewer.py`
Expected: `Success! Multi-page viewer generated in "viewer/" directory.`

**Step 3: Verify visual output in generated files**

Run: `grep -A 5 "My thought will guide you" viewer/Letter-to-R-Joseph-son-of-Judah.html`
Expected: Output showing `<div class="en-cell">` with plain text strings (no `<i>` tags).

**Step 4: Commit**

```bash
git add build_full_viewer.py
git commit -m "style: standardize Letter to R Joseph opening poem formatting to body text defaults"
```
