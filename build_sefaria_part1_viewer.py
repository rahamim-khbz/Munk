import json
import os
import re
import glob

def build_viewer():
    os.makedirs("viewer_sefaria_part1", exist_ok=True)
    
    # Safely locate the Makbili file ignoring unicode normalization differences
    he_files = glob.glob("Guide for the Perplexed - he - Makbili*.json")
    if not he_files:
        print("Error: Makbili Hebrew JSON file not found.")
        return
    hebrew_filename = he_files[0]
    
    with open(hebrew_filename, "r", encoding="utf-8") as f:
        hebrew_data = json.load(f)
    
    with open("checkpoint_main_text_groq.json", "r", encoding="utf-8") as f:
        english_main = json.load(f)
        
    with open("checkpoint_footnotes_rehab_groq.json", "r", encoding="utf-8") as f:
        english_footnotes = json.load(f)

    def get_en_text(key, default="[Translation Missing]"):
        if key in english_main:
            return english_main[key]
        # Check for sub-segments if any exist
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

    unified_chapters = []
    
    if "Letter to R Joseph son of Judah" in hebrew_data.get("text", {}):
        unified_chapters.append({
            "title": "Letter to R Joseph son of Judah",
            "segments": hebrew_data["text"]["Letter to R Joseph son of Judah"]
        })
        
    if "Prefatory Remarks" in hebrew_data.get("text", {}):
        unified_chapters.append({
            "title": "Prefatory Remarks",
            "segments": hebrew_data["text"]["Prefatory Remarks"]
        })
    
    part1_data = hebrew_data.get("text", {}).get("Part 1", {})
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

    chapter_index = []
    for ch in unified_chapters:
        safe_id = ch['title'].replace(' ', '-').replace('/', '-')
        chapter_index.append({"id": f"chapter-{safe_id}", "title": ch['title'], "filename": f"{safe_id}.html"})

    # Pre-render Footnotes Section JS/HTML drawer templates if needed, or link simple toggles
    # Let us embed simple JS toggle logic for smooth viewing
    for ch in unified_chapters:
        safe_id = ch['title'].replace(' ', '-').replace('/', '-')
        rows_html = ""
        footnotes_collected = {}
        
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
                fn_text = english_footnotes.get(full_id, f"[Footnote {fn_id_num} content missing]")
                footnotes_collected[full_id] = (fn_id_num, fn_text)
                return f'<sup class="fn-ref" onclick="showFn(\'{full_id}\')">{fn_id_num}</sup>'
            
            en_processed = re.sub(r"\[\[fn:(\d+)\]\]", replace_fn, en_text)
            en_processed = re.sub(r"\[\[t:\d+\]\]", "", en_processed)
            
            clean_he = re.sub(r'^(<br>)+|(<br>)+$', '', he_text).strip()
            
            rows_html += f"""
            <div class="parallel-row" id="row-{key}">
                <div class="he-cell">{repair_tags(clean_he)}</div>
                <div class="en-cell">{en_processed}</div>
            </div>
            """
            
        fn_drawer_html = ""
        for fn_full_id, (fn_num, fn_content) in footnotes_collected.items():
            fn_drawer_html += f"""
            <div class="footnote-item" id="item-{fn_full_id}" style="display: none;">
                <strong>Note {fn_num}:</strong> {fn_content}
            </div>
            """
            
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{ch['title']} - Sefaria Native Layout Reader</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=Frank+Ruhl+Libre:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #fdfcfb;
            --surface: #ffffff;
            --text: #1a1a1a;
            --text-muted: #6b7280;
            --accent: #8b0000;
            --border: #e5e7eb;
            --row-hover: #f9fafb;
            --header-bg: #f3eee8;
            --font-hebrew: 'Frank Ruhl Libre', serif;
            --font-english: 'Inter', sans-serif;
        }}
        body {{
            background: var(--bg); color: var(--text);
            font-family: var(--font-english); margin: 0;
            display: flex; flex-direction: column; height: 100vh;
            overflow: hidden;
        }}
        .header {{
            padding: 12px 30px; background: var(--header-bg);
            border-bottom: 1px solid var(--border);
            display: flex; justify-content: space-between; align-items: center;
        }}
        .header h1 {{ margin: 0; font-size: 1.2rem; color: var(--accent); }}
        .nav-links a {{ margin-left: 15px; text-decoration: none; color: var(--text); font-weight: 500; font-size: 0.95rem; }}
        .nav-links a:hover {{ text-decoration: underline; }}
        .main-container {{
            display: flex; flex-direction: column; flex: 1; overflow: hidden;
        }}
        .content {{
            flex: 1; overflow-y: auto; padding: 20px 60px;
            max-width: 1400px; margin: 0 auto; width: 100%; box-sizing: border-box;
        }}
        .parallel-row {{
            display: grid; grid-template-columns: 1fr 1fr; gap: 50px;
            padding: 28px 0; border-bottom: 1px solid var(--border);
            align-items: start;
        }}
        .parallel-row:hover {{ background: var(--row-hover); }}
        .en-cell {{ font-size: 1.1rem; line-height: 1.7; text-align: justify; white-space: pre-line; }}
        .he-cell {{ font-family: var(--font-hebrew); font-size: 1.35rem; line-height: 1.6; direction: rtl; text-align: right; }}
        .mediumGrey {{ display: block; margin-top: 18px; margin-bottom: 8px; font-weight: bold; color: var(--accent); font-size: 1.1rem; }}
        .fn-ref {{ color: var(--accent); font-weight: bold; cursor: pointer; padding: 0 3px; text-decoration: underline; }}
        .footnote-drawer {{
            height: 180px; background: #fff; border-top: 2px solid var(--accent);
            padding: 20px 40px; overflow-y: auto; box-shadow: 0 -4px 12px rgba(0,0,0,0.05);
            display: none; box-sizing: border-box;
        }}
        .footnote-drawer.active {{ display: block; }}
        .footnote-item {{ font-size: 1rem; line-height: 1.6; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{ch['title']}</h1>
        <div class="nav-links">
            <a href="index.html">Index / Contents</a>
        </div>
    </div>
    <div class="main-container">
        <div class="content">
            {rows_html}
        </div>
        <div class="footnote-drawer" id="fn-drawer">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 8px; margin-bottom: 12px;">
                <span style="font-weight: bold; font-size: 0.85rem; text-transform: uppercase; color: var(--text-muted);">Footnotes Viewer</span>
                <button onclick="closeFn()" style="background: none; border: none; font-size: 1.2rem; cursor: pointer;">&times;</button>
            </div>
            <div id="fn-content-area">
                {fn_drawer_html}
            </div>
        </div>
    </div>
    <script>
        let currentActiveFn = null;
        function showFn(id) {{
            const drawer = document.getElementById('fn-drawer');
            const items = document.querySelectorAll('.footnote-item');
            items.forEach(item => item.style.display = 'none');
            
            if (currentActiveFn === id && drawer.classList.contains('active')) {{
                drawer.classList.remove('active');
                currentActiveFn = null;
                return;
            }}
            
            const target = document.getElementById('item-' + id);
            if (target) {{
                target.style.display = 'block';
                drawer.classList.add('active');
                currentActiveFn = id;
            }}
        }}
        function closeFn() {{
            document.getElementById('fn-drawer').classList.remove('active');
            currentActiveFn = null;
        }}
    </script>
</body>
</html>"""

        out_filename = f"{safe_id}.html"
        with open(os.path.join("viewer_sefaria_part1", out_filename), "w", encoding="utf-8") as f:
            f.write(html_template)
            
    # Index Landing Page
    index_links = ""
    for ch in chapter_index:
        index_links += f'<div class="index-item"><a href="{ch["filename"]}">{ch["title"]}</a></div>'
        
    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sefaria Native Layout Index (Part I)</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; background: #fdfcfb; color: #1a1a1a; margin: 0; padding: 40px 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #8b0000; margin-bottom: 10px; }}
        p {{ color: #555; line-height: 1.6; margin-bottom: 30px; }}
        .grid {{ border: 1px solid #e5e7eb; border-radius: 8px; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.05); overflow: hidden; }}
        .index-item {{ border-bottom: 1px solid #e5e7eb; }}
        .index-item:last-child {{ border-bottom: none; }}
        .index-item a {{ display: block; padding: 16px 24px; text-decoration: none; color: #1a1a1a; font-weight: 500; transition: background 0.15s; }}
        .index-item a:hover {{ background: #f9fafb; color: #8b0000; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Sefaria Native Layout Reader (Part I Fork)</h1>
        <p>This layout enforces pure 1:1 alignment with Sefaria's canonical database macro-segments. Source paragraphs containing inline sections are displayed as unified side-by-side rows, with internal markers visually formatted as subheadings.</p>
        <div class="grid">
            {index_links}
        </div>
    </div>
</body>
</html>"""
    with open(os.path.join("viewer_sefaria_part1", "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)
        
    print("Success! Sefaria native layout generated in viewer_sefaria_part1/")

if __name__ == "__main__":
    build_viewer()
