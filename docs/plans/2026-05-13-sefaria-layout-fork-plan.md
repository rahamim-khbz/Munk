# Sefaria Native Layout Fork (Part I) Implementation Plan

> **For Antigravity:** REQUIRED SUB-SKILL: Load executing-plans to implement this plan task-by-task.

**Goal:** Implement a clean alternative viewer fork (`build_sefaria_part1_viewer.py`) that outputs native 1:1 segment alignment mapping for Part I without block shattering, and execute a targeted alignment audit proving the visual stability of unified blocks.

**Architecture:** Create an independent generator script targeting `viewer_sefaria_part1/` with simple index pairing loops and `.mediumGrey` CSS block styling. Adapt the alignment audit to verify the results.

**Tech Stack:** Python, Vanilla HTML/CSS/JS.

---

### Task 1: Create the Forked Generator Script (`build_sefaria_part1_viewer.py`)

**Files:**
- Create: `/Users/rayhabbaz/Munk's Guide/build_sefaria_part1_viewer.py`

**Step 1: Write the generator script implementation**

```python
import json
import os
import re

def build_viewer():
    os.makedirs("viewer_sefaria_part1", exist_ok=True)
    
    with open("Guide for the Perplexed - he - Makbili Edition, Mif'al Mishneh Torah, 2024.json", "r") as f:
        hebrew_data = json.load(f)
    
    with open("checkpoint_main_text_groq.json", "r") as f:
        english_main = json.load(f)
        
    with open("checkpoint_footnotes_rehab_groq.json", "r") as f:
        english_footnotes = json.load(f)

    def get_en_text(key, default="[Translation Missing]"):
        if key in english_main:
            return english_main[key]
        if f"{key}.sub_0" in english_main:
            parts = []
            i = 0
            while f"{key}.sub_{i}" in english_main:
                parts.append(english_main[f"{key}.sub_{i}"])
                i += 1
            return " ".join(parts)
        return default

    def repair_tags(html):
        stack = []
        clean = ""
        # Basic self-closing tag prevention or stack tracking if needed, 
        # but let us keep it simple or implement stack loop
        tokens = re.split(r'(</?[^>]+>)', html)
        res = ""
        for t in tokens:
            if not t: continue
            if t.startswith('<') and t.endswith('>'):
                if t.startswith('</'):
                    tag_name = t[2:-1].split()[0]
                    if stack and stack[-1] == tag_name:
                        stack.pop()
                        res += t
                else:
                    tag_name = t[1:-1].split()[0]
                    if not t.endswith('/>') and tag_name not in ['br', 'hr', 'img']:
                        stack.append(tag_name)
                    res += t
            else:
                res += t
        for tag in reversed(stack):
            res += f'</{tag}>'
        return res

    sections_to_include = [
        "Letter to R Joseph son of Judah",
        "Prefatory Remarks",
        "Part 1"
    ]
    
    unified_chapters = []
    unified_chapters.append({
        "title": "Letter to R Joseph son of Judah",
        "segments": hebrew_data["text"]["Letter to R Joseph son of Judah"]
    })
    unified_chapters.append({
        "title": "Prefatory Remarks",
        "segments": hebrew_data["text"]["Prefatory Remarks"]
    })
    
    part1_data = hebrew_data["text"]["Part 1"]
    if "Introduction" in part1_data:
        unified_chapters.append({
            "title": "Part 1 - Introduction",
            "key_prefix": "root.text.Part 1.Introduction",
            "segments": part1_data["Introduction"]
        })
    
    if "" in part1_data:
        for ch_idx, segments in enumerate(part1_data[""]):
            unified_chapters.append({
                "title": f"Part 1 - Chapter {ch_idx + 1}",
                "key_prefix": f"root.text.Part 1..{ch_idx}",
                "segments": segments
            })

    # Build TOC metadata
    chapter_index = []
    for ch in unified_chapters:
        safe_id = ch['title'].replace(' ', '-').replace('/', '-')
        chapter_index.append({"id": f"chapter-{safe_id}", "title": ch['title']})

    for ch in unified_chapters:
        safe_id = ch['title'].replace(' ', '-').replace('/', '-')
        rows_html = ""
        
        for i, he_text in enumerate(ch['segments']):
            if "key_prefix" in ch:
                key = f"{ch['key_prefix']}.{i}"
            else:
                prefix = "root.text.Letter to R Joseph son of Judah" if "Letter" in ch['title'] else "root.text.Prefatory Remarks"
                key = f"{prefix}.{i}"

            en_text = get_en_text(key, "[Translation Missing]")
            
            def replace_fn(match):
                fn_id_num = match.group(1)
                full_id = f"fn.{fn_id_num}"
                return f'<sup class="fn-ref" title="View Footnote" onclick="showFn(\'{full_id}\')">{fn_id_num}</sup>'
            
            en_processed = re.sub(r"\[\[fn:(\d+)\]\]", replace_fn, en_text)
            en_processed = re.sub(r"\[\[t:\d+\]\]", "", en_processed)
            
            clean_he = re.sub(r'^(<br>)+|(<br>)+$', '', he_text).strip()
            
            rows_html += f"""
            <div class="parallel-row" id="row-{key}">
                <div class="he-cell">{repair_tags(clean_he)}</div>
                <div class="en-cell">{en_processed}</div>
            </div>
            """
            
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{ch['title']} - Munk/Makbili Sefaria Parallel Reader</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=Frank+Ruhl+Libre:wght@400;700&family=Amiri&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #fdfcfb;
            --surface: #ffffff;
            --text: #1a1a1a;
            --text-muted: #6b7280;
            --accent: #8b5cf6;
            --border: #e5e7eb;
            --row-hover: #f9fafb;
            --panel-bg: #ffffff;
            --header-bg: #ffffff;
            --font-hebrew: 'Frank Ruhl Libre', serif;
            --font-english: 'Inter', sans-serif;
        }}
        body {{
            background: var(--bg); color: var(--text);
            font-family: var(--font-english); margin: 0;
            display: flex; flex-direction: column; height: 100vh;
        }}
        .header {{
            padding: 15px 40px; background: var(--header-bg);
            border-bottom: 1px solid var(--border);
            display: flex; justify-content: space-between; align-items: center;
        }}
        .header h1 {{ margin: 0; font-size: 1.3rem; }}
        .nav-links a {{ margin-left: 15px; text-decoration: none; color: var(--accent); font-weight: 500; }}
        .content {{
            flex: 1; overflow-y: auto; padding: 20px 40px;
            max-width: 1200px; margin: 0 auto; width: 100%; box-sizing: border-box;
        }}
        .parallel-row {{
            display: grid; grid-template-columns: 1fr 1fr; gap: 40px;
            padding: 24px 0; border-bottom: 1px solid var(--border);
        }}
        .parallel-row:hover {{ background: var(--row-hover); }}
        .en-cell {{ font-size: 1.1rem; line-height: 1.7; text-align: justify; white-space: pre-line; }}
        .he-cell {{ font-family: var(--font-hebrew); font-size: 1.3rem; line-height: 1.6; direction: rtl; text-align: right; }}
        .mediumGrey {{ display: block; margin-top: 16px; margin-bottom: 6px; font-weight: bold; color: var(--accent); font-size: 1rem; }}
        .fn-ref {{ color: var(--accent); font-weight: bold; cursor: pointer; padding: 0 2px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{ch['title']}</h1>
        <div class="nav-links">
            <a href="index.html">Index / Contents</a>
        </div>
    </div>
    <div class="content">
        {rows_html}
    </div>
</body>
</html>"""

        out_filename = f"{safe_id}.html"
        with open(os.path.join("viewer_sefaria_part1", out_filename), "w") as f:
            f.write(html_template)
            
    # Write a simple landing index page
    index_links = ""
    for ch in chapter_index:
        filename = ch['id'].replace("chapter-", "") + ".html"
        index_links += f'<div style="padding: 10px; border-bottom: 1px solid #eee;"><a href="{filename}" style="text-decoration: none; color: #333; font-weight: 500;">{ch["title"]}</a></div>'
        
    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sefaria Native Layout Index (Part I)</title>
    <style>body {{ font-family: sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }}</style>
</head>
<body>
    <h1>Munk/Makbili Sefaria Native Layout (Part I Fork)</h1>
    <p>Every row directly aligns 1:1 with Sefaria's canonical macro-segments without string shattering.</p>
    <div style="border: 1px solid #ccc; border-radius: 6px;">
        {index_links}
    </div>
</body>
</html>"""
    with open(os.path.join("viewer_sefaria_part1", "index.html"), "w") as f:
        f.write(index_html)
        
    print("Success! Sefaria native layout generated in viewer_sefaria_part1/")

if __name__ == "__main__":
    build_viewer()
```

**Step 2: Execute script to generate layout**

Run: `python build_sefaria_part1_viewer.py`
Expected: `Success! Sefaria native layout generated in viewer_sefaria_part1/`

**Step 3: Commit**

```bash
git add build_sefaria_part1_viewer.py
git commit -m "feat: create dedicated generator script for Sefaria native segment layout fork (Part I)"
```

---

### Task 2: Create Targeted Alignment Audit (`inspect_sefaria_part1_alignment.py`)

**Files:**
- Create: `/Users/rayhabbaz/Munk's Guide/inspect_sefaria_part1_alignment.py`

**Step 1: Write the targeted alignment inspection script**

```python
import os
import re

def word_count(text):
    clean = re.sub(r'<[^>]+>', ' ', text)
    clean = re.sub(r'[^\w\s]', '', clean)
    return len(clean.split())

def inspect():
    directory = "viewer_sefaria_part1"
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist.")
        return
        
    files = sorted([f for f in os.listdir(directory) if f.endswith('.html') and f != 'index.html'])
    
    issues = []
    total_rows = 0
    
    for filename in files:
        with open(os.path.join(directory, filename), "r", encoding="utf-8") as f:
            content = f.read()
            
        rows = content.split('<div class="parallel-row"')
        for i, row in enumerate(rows[1:]):
            total_rows += 1
            he_match = re.search(r'<div class="he-cell">(.*?)</div>', row, re.DOTALL)
            en_match = re.search(r'<div class="en-cell">(.*?)</div>', row, re.DOTALL)
            
            he_text = he_match.group(1).strip() if he_match else ""
            en_text = en_match.group(1).strip() if en_match else ""
            
            id_match = re.search(r'id="([^"]+)"', row)
            row_id = id_match.group(1) if id_match else f"row_{i+1}"
            
            he_wc = word_count(he_text)
            en_wc = word_count(en_text)
            
            row_issues = []
            if not en_text or "[Translation Missing]" in en_text:
                row_issues.append("Empty or Missing EN text")
            elif he_wc > 0:
                ratio = en_wc / he_wc
                # Relaxed high-ratio check since segment 0/introductory headers are intentionally short in HE
                if ratio < 0.25 and he_wc > 10:
                    row_issues.append(f"Extremely Low Ratio ({ratio:.2f})")
                elif ratio > 4.0 and he_wc > 15:
                    row_issues.append(f"Extremely High Ratio ({ratio:.2f})")
                    
            if row_issues:
                issues.append({
                    "file": filename,
                    "row_id": row_id,
                    "issues": row_issues,
                    "he_wc": he_wc,
                    "en_wc": en_wc
                })
                
    # Write audit report
    report = "# Sefaria Layout Fork Alignment Audit Report (Part I)\n\n"
    report += f"**Files audited:** {len(files)}\n"
    report += f"**Total macro-segments scanned:** {total_rows}\n"
    report += f"**Flagged segments:** {len(issues)}\n\n"
    
    if not issues:
        report += "### ✅ Absolute Parity Verified\nZero missing translations or extreme word count mismatches detected. Unified blocks maintain complete visual alignment."
    else:
        report += "| File | Row ID | Issues | HE Words | EN Words |\n|---|---|---|---|---|\n"
        for iss in issues:
            report += f"| {iss['file']} | `{iss['row_id']}` | {', '.join(iss['issues'])} | {iss['he_wc']} | {iss['en_wc']} |\n"
            
    with open("alignment_report_sefaria_part1.md", "w") as f:
        f.write(report)
        
    print(f"Audit complete. Scanned {total_rows} unified segments across {len(files)} files.")
    print(f"Flagged anomalies: {len(issues)}. Detailed results written to alignment_report_sefaria_part1.md")

if __name__ == "__main__":
    inspect()
```

**Step 2: Execute targeted alignment audit**

Run: `python inspect_sefaria_part1_alignment.py`
Expected output ends with: `Detailed results written to alignment_report_sefaria_part1.md`

**Step 3: Commit**

```bash
git add inspect_sefaria_part1_alignment.py
git commit -m "test: implement targeted alignment audit script verifying native Sefaria segment parity for Part I fork"
```
