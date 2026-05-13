import json
import os
import re
import glob

def build_viewer():
    os.makedirs("viewer_sefaria_full", exist_ok=True)
    
    # Locate the Makbili Hebrew JSON file safely
    he_files = glob.glob("Guide for the Perplexed - he - Makbili*.json")
    if not he_files:
        print("Error: Makbili Hebrew JSON file not found.")
        return
    hebrew_filename = he_files[0]
    
    with open(hebrew_filename, "r", encoding="utf-8") as f:
        hebrew_data = json.load(f)
        
    with open("munk_production_v1.json", "r", encoding="utf-8") as f:
        prod_data = json.load(f)
        english_main = prod_data["text"]
        english_footnotes = prod_data["footnotes"]

    def get_en_text(key, default="[Translation Missing]"):
        if key in english_main:
            return english_main[key]
        # Check if sub-segments exist and merge them
        sub_idx = 0
        merged_parts = []
        while f"{key}.sub_{sub_idx}" in english_main:
            merged_parts.append(english_main[f"{key}.sub_{sub_idx}"])
            sub_idx += 1
        if merged_parts:
            return " ".join(merged_parts)
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
    
    # 1. Munk's Scholarly Prefaces
    munk_intro_segments = []
    try:
        with open("preface_resegmented.json", "r", encoding="utf-8") as f:
            fr_paras = json.load(f)
        with open("preface_english_final.json", "r", encoding="utf-8") as f:
            en_paras = json.load(f)
        for i in range(len(fr_paras)):
            munk_intro_segments.append({
                "he": fr_paras[i],
                "en": en_paras[i] if i < len(en_paras) else "[Translation Missing]"
            })
        unified_chapters.append({
            "title": "Introduction to Volume I",
            "group": "Munk's Prefaces",
            "custom_segments": munk_intro_segments
        })
        # Inject standard scholarly preface notes
        english_footnotes["fn.3001"] = "In some manuscripts, the غ is rendered by ג̇ or ג̄, and the ج by ג."
        english_footnotes["fn.3002"] = "See the translation, p. 50, n. 3, and p. 351, n. 4."
        english_footnotes["fn.3003"] = "See the translation, p. 19, n. 2."
        english_footnotes["fn.3004"] = "Sometimes, to render the sentence clearer, I have added explanatory words in ( ) that are not found in the text; the parentheses of the original text have been indicated by [ ]."
        english_footnotes["fn.3005"] = "The importance that I believed I should attach to these indications did not permit me to shrink from the difficulties that my current situation opposes to such a task, and I have not hesitated in all my research, often taking a few vague memories as my starting point, to listen to long readings in order to achieve the desired goal. There are, I believe, in this first volume, only three citations whose location I have been unable to indicate: page 14, a passage from the Midrash or Haggadah (To expound the power, etc.), which is also cited by R. Moses ben Nahman in his Commentary on Genesis, but which perhaps no longer exists in our Midrashim; page 107, a passage from Alexander of Aphrodisias, which I did not have at my disposal; page 381, words attributed by the author to Galen regarding time."
    except FileNotFoundError:
        pass

    try:
        with open("preface_vol2.json", "r", encoding="utf-8") as f:
            v2_data = json.load(f)
        if "footnote_en" in v2_data:
            english_footnotes["fn.3006"] = v2_data["footnote_en"]
        v2_segs = [{"he": v2_data["fr"][i], "en": v2_data["en"][i]} for i in range(len(v2_data["fr"]))]
        unified_chapters.append({
            "title": "Introduction to Volume II",
            "group": "Munk's Prefaces",
            "custom_segments": v2_segs
        })
    except FileNotFoundError:
        pass

    try:
        with open("preface_vol3.json", "r", encoding="utf-8") as f:
            v3_data = json.load(f)
        if "footnotes_en" in v3_data:
            for k, v in v3_data["footnotes_en"].items():
                english_footnotes[f"fn.{k}"] = v
        v3_segs = [{"he": v3_data["fr"][i], "en": v3_data["en"][i]} for i in range(len(v3_data["fr"]))]
        unified_chapters.append({
            "title": "Introduction to Volume III",
            "group": "Munk's Prefaces",
            "custom_segments": v3_segs
        })
    except FileNotFoundError:
        pass

    try:
        with open("munk_title_note.json", "r", encoding="utf-8") as f:
            tn_data = json.load(f)
        if "footnote_en" in tn_data:
            english_footnotes["fn.3000"] = tn_data["footnote_en"]
        tn_segs = [{"he": tn_data["fr"][i], "en": tn_data["en"][i]} for i in range(len(tn_data["fr"]))]
        unified_chapters.append({
            "title": "Note On The Title",
            "group": "Munk's Prefaces",
            "custom_segments": tn_segs
        })
    except FileNotFoundError:
        pass

    # 2. Classical Introductions
    if "Letter to R Joseph son of Judah" in hebrew_data.get("text", {}):
        letter_he = hebrew_data["text"]["Letter to R Joseph son of Judah"]
        parts = letter_he[0].split("<br>")
        poem_he = "<br>".join(parts[:-1])
        invoc_he = parts[-1]
        addr_he = letter_he[2:]
        
        l_segs = []
        l_segs.append({
            "he": poem_he,
            "en": get_en_text("root.text.Letter to R Joseph son of Judah.Poem", 'My thought will guide you on the path of truth, and smooth the way.<br>Come, walk along its path, O all you who wander in the field of religion!<br>The impure and the ignorant shall not pass over it; it shall be called the sacred way.'),
            "is_poem": True
        })
        l_segs.append({
            "he": invoc_he,
            "en": get_en_text("root.text.Letter to R Joseph son of Judah.0", "In the name of the Eternal God of the Universe")
        })
        en_sal = get_en_text("root.text.Letter to R Joseph son of Judah.1", "")
        en_bod = get_en_text("root.text.Letter to R Joseph son of Judah.2", "")
        en_addr_merged = (en_sal + " " + en_bod).strip() if en_sal else en_bod
        l_segs.append({
            "he": addr_he[0],
            "en": en_addr_merged
        })
        if len(addr_he) > 1:
            l_segs.append({
                "he": addr_he[1],
                "en": get_en_text("root.text.Letter to R Joseph son of Judah.3", "[Translation Missing]")
            })
        unified_chapters.append({
            "title": "Letter to R Joseph son of Judah",
            "group": "Introductions",
            "custom_segments": l_segs
        })

    if "Prefatory Remarks" in hebrew_data.get("text", {}):
        unified_chapters.append({
            "title": "Prefatory Remarks",
            "group": "Introductions",
            "key_prefix": "root.text.Prefatory Remarks",
            "segments": hebrew_data["text"]["Prefatory Remarks"]
        })

    # 3. Philosophical Parts
    for part_num in [1, 2, 3]:
        p_data = hebrew_data.get("text", {}).get(f"Part {part_num}", {})
        if "Introduction" in p_data:
            unified_chapters.append({
                "title": f"Part {part_num} - Introduction",
                "group": f"Part {part_num}",
                "key_prefix": f"root.text.Part {part_num}.Introduction",
                "segments": p_data["Introduction"]
            })
        if "" in p_data:
            for ch_idx, segs in enumerate(p_data[""]):
                unified_chapters.append({
                    "title": f"Part {part_num} - Chapter {ch_idx + 1}",
                    "group": f"Part {part_num}",
                    "key_prefix": f"root.text.Part {part_num}..{ch_idx}",
                    "segments": segs
                })

    # 4. Salomon Munk's Endnotes
    endnote_files = [
        ("endnotes_vol1.json", "Endnotes to Volume I"),
        ("endnotes_vol2.json", "Endnotes to Volume II"),
        ("endnotes_vol3.json", "Endnotes to Volume III")
    ]
    for fn, en_title in endnote_files:
        try:
            with open(fn, "r", encoding="utf-8") as f:
                en_data = json.load(f)
            en_segs = [{"he": en_data["fr"][i], "en": en_data["en"][i]} for i in range(len(en_data["fr"]))]
            unified_chapters.append({
                "title": en_title,
                "group": "Munk's Endnotes",
                "custom_segments": en_segs
            })
        except FileNotFoundError:
            pass

    # Precompute chapter mapping list for dynamic sidebar TOC drawers
    chapter_index = []
    for ch in unified_chapters:
        safe_id = ch['title'].replace(' ', '-').replace('/', '-').replace('.', '')
        chapter_index.append({
            "id": f"chapter-{safe_id}",
            "title": ch['title'],
            "filename": f"{safe_id}.html",
            "group": ch.get("group", "Other")
        })

    chapter_index_json = json.dumps(chapter_index)
    
    # Render individual HTML files
    for idx, ch in enumerate(unified_chapters):
        safe_id = ch['title'].replace(' ', '-').replace('/', '-').replace('.', '')
        prev_ch = unified_chapters[idx - 1] if idx > 0 else None
        next_ch = unified_chapters[idx + 1] if idx < len(unified_chapters) - 1 else None
        
        rows_html = ""
        footnotes_collected = {}
        
        is_preface_or_endnote = ch.get("group") in ["Munk's Prefaces", "Munk's Endnotes"]
        
        segments_source = ch.get("custom_segments", [])
        if not segments_source and "segments" in ch:
            segments_source = []
            for i, he_text in enumerate(ch["segments"]):
                key = f"{ch['key_prefix']}.{i}"
                segments_source.append({
                    "he": he_text,
                    "en": get_en_text(key, "[Translation Missing]")
                })

        fn_counter = [0]
        
        for i, seg in enumerate(segments_source):
            he_text = seg["he"]
            en_text = seg["en"]
            
            def replace_fn(match):
                fn_id_num = match.group(1)
                full_id = f"fn.{fn_id_num}"
                if is_preface_or_endnote:
                    marker = "*"
                else:
                    fn_counter[0] += 1
                    marker = str(fn_counter[0])
                    
                fn_text = english_footnotes.get(full_id, f"[Footnote content missing]")
                footnotes_collected[full_id] = (marker, fn_text)
                return f'<sup class="fn-ref" onclick="showFn(\'{full_id}\')">{marker}</sup>'
            
            en_processed = re.sub(r"\[\[fn:(\d+)(?:\|([^\]]+))?\]\]", replace_fn, en_text)
            en_processed = re.sub(r"\[\[t:\d+\]\]", "", en_processed)
            
            clean_he = re.sub(r'^(<br>)+|(<br>)+$', '', he_text).strip()
            row_class = "parallel-row poem-row" if seg.get("is_poem") else "parallel-row"
            
            rows_html += f"""
            <div class="{row_class}" id="row-{i+1}">
                <div class="he-cell">{repair_tags(clean_he)}</div>
                <div class="en-cell">{repair_tags(en_processed)}</div>
            </div>
            """
            
        nav_buttons_html = f"""
        <div class="bottom-nav" style="display: flex; justify-content: space-between; margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
            <div>{f'<a href="{prev_ch["title"].replace(" ", "-").replace("/", "-").replace(".", "")}.html" style="color: #8b0000; font-weight: bold; text-decoration: none;">← Previous: {prev_ch["title"]}</a>' if prev_ch else ''}</div>
            <div>{f'<a href="{next_ch["title"].replace(" ", "-").replace("/", "-").replace(".", "")}.html" style="color: #8b0000; font-weight: bold; text-decoration: none;">Next: {next_ch["title"]} →</a>' if next_ch else ''}</div>
        </div>
        """
        
        footnotes_map_json = json.dumps({k: v[1] for k, v in footnotes_collected.items()})
        
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{ch['title']} - Sefaria Full Corpus Native Reader</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=Frank+Ruhl+Libre:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #fdfcfb; --surface: #ffffff; --text: #1a1a1a; --text-muted: #6b7280;
            --accent: #8b0000; --border: #e5e7eb; --row-hover: #f9fafb; --header-bg: #f3eee8;
            --font-hebrew: 'Frank Ruhl Libre', serif; --font-english: 'Inter', sans-serif;
        }}
        body {{ background: var(--bg); color: var(--text); font-family: var(--font-english); margin: 0; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }}
        .header {{ padding: 12px 30px; background: var(--header-bg); border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; z-index: 100; }}
        .header-left {{ display: flex; align-items: center; gap: 15px; }}
        #hamburger-btn {{ background: none; border: none; font-size: 1.4rem; cursor: pointer; color: var(--accent); }}
        .header h1 {{ margin: 0; font-size: 1.25rem; color: var(--accent); }}
        .main-container {{ display: flex; flex-direction: column; flex: 1; overflow: hidden; position: relative; }}
        .content {{ flex: 1; overflow-y: auto; padding: 20px 60px; max-width: 1400px; margin: 0 auto; width: 100%; box-sizing: border-box; }}
        .parallel-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 50px; padding: 28px 0; border-bottom: 1px solid var(--border); align-items: start; }}
        .parallel-row:hover {{ background: var(--row-hover); }}
        .poem-row .en-cell {{ font-style: italic; color: var(--text-muted); }}
        .en-cell {{ font-size: 1.1rem; line-height: 1.7; text-align: justify; white-space: pre-line; }}
        .he-cell {{ font-family: var(--font-hebrew); font-size: 1.35rem; line-height: 1.6; direction: rtl; text-align: right; }}
        .mediumGrey {{ display: block; margin-top: 18px; margin-bottom: 8px; font-weight: bold; color: var(--accent); font-size: 1.1rem; }}
        .fn-ref {{ color: var(--accent); font-weight: bold; cursor: pointer; padding: 0 3px; text-decoration: underline; }}
        
        /* Drawer TOC Sidebar */
        .toc-drawer {{ position: fixed; top: 0; left: 0; width: 320px; height: 100vh; background: #fff; border-right: 1px solid var(--border); z-index: 500; transform: translateX(-100%); transition: transform 0.3s ease; display: flex; flex-direction: column; box-shadow: 4px 0 15px rgba(0,0,0,0.1); }}
        .toc-drawer.open {{ transform: translateX(0); }}
        .toc-header {{ padding: 16px 20px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; font-weight: bold; }}
        .toc-header button {{ background: none; border: none; font-size: 1.2rem; cursor: pointer; }}
        .toc-body {{ flex: 1; overflow-y: auto; padding: 10px 0; }}
        .toc-group-title {{ padding: 10px 20px; font-size: 0.85rem; font-weight: bold; color: var(--text-muted); text-transform: uppercase; background: #f9fafb; border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); margin-top: 10px; }}
        .toc-group-title:first-child {{ margin-top: 0; border-top: none; }}
        .toc-item {{ padding: 10px 20px; border-bottom: 1px solid #f3f4f6; font-size: 0.95rem; }}
        .toc-item a {{ color: var(--text); text-decoration: none; display: block; }}
        .toc-item a:hover {{ color: var(--accent); font-weight: 500; }}
        .toc-backdrop {{ position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 499; display: none; }}
        .toc-backdrop.visible {{ display: block; }}
        
        /* Footnote Bottom Sheet Drawer */
        .fn-panel {{ position: fixed; bottom: 0; left: 0; right: 0; height: 220px; background: #fff; border-top: 2px solid var(--accent); z-index: 400; transform: translateY(100%); transition: transform 0.3s ease; box-shadow: 0 -4px 15px rgba(0,0,0,0.05); display: flex; flex-direction: column; }}
        .fn-panel.open {{ transform: translateY(0); }}
        .fn-header {{ padding: 12px 30px; border-bottom: 1px solid var(--border); background: var(--header-bg); display: flex; justify-content: space-between; align-items: center; font-weight: bold; color: var(--accent); }}
        .fn-body {{ padding: 20px 30px; overflow-y: auto; flex: 1; font-size: 1.05rem; line-height: 1.6; }}
    </style>
</head>
<body>
    <div class="toc-backdrop" id="toc-backdrop" onclick="toggleTOC()"></div>
    <div class="toc-drawer" id="toc-drawer">
        <div class="toc-header">
            <span>Table of Contents</span>
            <button onclick="toggleTOC()">&times;</button>
        </div>
        <div class="toc-body" id="toc-links-container"></div>
    </div>
    
    <div class="header">
        <div class="header-left">
            <button id="hamburger-btn" onclick="toggleTOC()">☰</button>
            <h1>{ch['title']}</h1>
        </div>
        <div><a href="index.html" style="color: var(--accent); text-decoration: none; font-weight: 500;">Index View</a></div>
    </div>
    
    <div class="main-container">
        <div class="content">
            {rows_html}
            {nav_buttons_html}
        </div>
        
        <div class="fn-panel" id="fn-panel">
            <div class="fn-header">
                <span id="fn-title">Scholarly Note</span>
                <button onclick="closeFn()" style="background: none; border: none; font-size: 1.2rem; cursor: pointer; color: var(--accent);">&times;</button>
            </div>
            <div class="fn-body" id="fn-body-content"></div>
        </div>
    </div>
    
    <script>
        const chapterIndex = {chapter_index_json};
        const footnotesMap = {footnotes_map_json};
        let activeFnId = null;
        
        function toggleTOC() {{
            document.getElementById('toc-drawer').classList.toggle('open');
            document.getElementById('toc-backdrop').classList.toggle('visible');
        }}
        
        function showFn(id) {{
            const panel = document.getElementById('fn-panel');
            if (panel.classList.contains('open') && activeFnId === id) {{
                closeFn();
                return;
            }}
            activeFnId = id;
            document.getElementById('fn-title').textContent = 'Note';
            document.getElementById('fn-body-content').innerHTML = footnotesMap[id] || '<em>Content missing</em>';
            panel.classList.add('open');
        }}
        
        function closeFn() {{
            activeFnId = null;
            document.getElementById('fn-panel').classList.remove('open');
        }}
        
        // Populate Sidebar TOC dynamically Group by Group
        window.addEventListener('DOMContentLoaded', () => {{
            const container = document.getElementById('toc-links-container');
            const groups = {{}};
            chapterIndex.forEach(c => {{
                if (!groups[c.group]) groups[c.group] = [];
                groups[c.group].push(c);
            }});
            
            for (const [gName, items] of Object.entries(groups)) {{
                const gTitle = document.createElement('div');
                gTitle.className = 'toc-group-title';
                gTitle.textContent = gName;
                container.appendChild(gTitle);
                
                items.forEach(item => {{
                    const div = document.createElement('div');
                    div.className = 'toc-item';
                    div.innerHTML = `<a href="${{item.filename}}">${{item.title.replace('Part 1 - ', '').replace('Part 2 - ', '').replace('Part 3 - ', '')}}</a>`;
                    container.appendChild(div);
                }});
            }}
        }});
    </script>
</body>
</html>"""

        out_filename = f"{safe_id}.html"
        with open(os.path.join("viewer_sefaria_full", out_filename), "w", encoding="utf-8") as f:
            f.write(html_template)
            
    # Output Master Index View Page
    groups_html = ""
    groups_dict = {}
    for ch in chapter_index:
        g = ch.get("group", "Other")
        if g not in groups_dict: groups_dict[g] = []
        groups_dict[g].append(ch)
        
    for gName, items in groups_dict.items():
        links_str = ""
        for item in items:
            disp = item["title"].replace('Part 1 - ', '').replace('Part 2 - ', '').replace('Part 3 - ', '')
            links_str += f'<div class="grid-item"><a href="{item["filename"]}">{disp}</a></div>'
        groups_html += f"""
        <div class="group-section">
            <h2>{gName}</h2>
            <div class="grid-container">{links_str}</div>
        </div>
        """
        
    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sefaria Full Corpus Native Index</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; background: #fdfcfb; color: #1a1a1a; margin: 0; padding: 40px 40px 80px; }}
        .container {{ max-width: 1100px; margin: 0 auto; }}
        h1 {{ color: #8b0000; margin-bottom: 5px; }}
        p.subtitle {{ color: #555; font-size: 1.05rem; margin-bottom: 40px; }}
        .group-section {{ margin-bottom: 40px; }}
        .group-section h2 {{ font-size: 1.2rem; color: #6b7280; border-bottom: 2px solid #8b0000; padding-bottom: 8px; margin-bottom: 16px; text-transform: uppercase; letter-spacing: 0.05em; }}
        .grid-container {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }}
        .grid-item a {{ display: block; padding: 14px 20px; background: #fff; border: 1px solid #e5e7eb; border-radius: 6px; text-decoration: none; color: #1a1a1a; font-weight: 500; transition: all 0.15s; box-shadow: 0 1px 2px rgba(0,0,0,0.02); }}
        .grid-item a:hover {{ background: #8b0000; color: #fff; border-color: #8b0000; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Maimonides' Guide for the Perplexed</h1>
        <p class="subtitle">Complete Sefaria Native Alignment Parallel Edition (Munk / Makbili Framework)</p>
        {groups_html}
    </div>
</body>
</html>"""
    with open(os.path.join("viewer_sefaria_full", "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)
        
    print(f"Success! Full corpus generated natively: {len(unified_chapters)} total sections populated in viewer_sefaria_full/")

if __name__ == "__main__":
    build_viewer()
