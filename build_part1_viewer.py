import json
import os
import re

def build_viewer():
    # 1. Load Data
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

    # 2. Extract Part I Sections
    sections_to_include = [
        "Letter to R Joseph son of Judah",
        "Prefatory Remarks",
        "Part 1"
    ]
    
    unified_chapters = []

    # Handle Letter
    unified_chapters.append({
        "title": "Letter to R Joseph son of Judah",
        "segments": hebrew_data["text"]["Letter to R Joseph son of Judah"]
    })
    
    # Handle Prefatory Remarks
    unified_chapters.append({
        "title": "Prefatory Remarks",
        "segments": hebrew_data["text"]["Prefatory Remarks"]
    })
    
    # Handle Part 1 Chapters
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

    # 3. Build HTML Content
    rows_html = ""
    
    for ch in unified_chapters:
        chapter_id = ch['title'].replace(' ', '-').replace('/', '-')
        rows_html += f"""<section class="chapter-section" id="chapter-{chapter_id}" data-title="{ch['title']}">
            <div class='chapter-header'><h2>{ch['title']}</h2></div>"""
        
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

            rows_html += f"""
            <div class="parallel-row" id="row-{key}">
                <div class="en-cell">{en_processed}</div>
                <div class="he-cell">{he_text}</div>
            </div>
            """
        rows_html += "</section>"

    # 4. Prepare Footnotes JSON & Chapter Index
    footnotes_json = json.dumps(english_footnotes)
    chapter_index_js = json.dumps([
        {"id": f"chapter-{ch['title'].replace(' ', '-').replace('/', '-')}", "title": ch['title']}
        for ch in unified_chapters
    ])

    # 5. Generate Final HTML
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Munk's Guide - Parallel Reader (Part I)</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=Frank+Ruhl+Libre:wght@400;700&family=Amiri&display=swap" rel="stylesheet">
    <style>
        /* Default (Light) */
        :root {{
            --bg: #fdfcfb;
            --surface: #ffffff;
            --text: #1a1a1a;
            --text-muted: #6b7280;
            --accent: #8b5cf6;
            --border: #e5e7eb;
            --row-hover: #f9fafb;
            --fn-ref-hover: #f3e8ff;
            --panel-bg: #ffffff;
            --header-bg: #ffffff;
            --font-hebrew: 'Frank Ruhl Libre', serif;
            --font-english: 'Inter', sans-serif;
        }}

        /* Sepia */
        html.sepia {{
            --bg: #f4ecd8;
            --surface: #ede3c8;
            --text: #3c2f1e;
            --text-muted: #7a6040;
            --accent: #a0522d;
            --border: #c9b89a;
            --row-hover: #ecdfc8;
            --fn-ref-hover: #d4b896;
            --panel-bg: #ede3c8;
            --header-bg: #e8dcc5;
        }}

        /* Dark */
        html.dark {{
            --bg: #12121e;
            --surface: #1e1e30;
            --text: #e2e2e2;
            --text-muted: #9ca3af;
            --accent: #a78bfa;
            --border: #2e2e46;
            --row-hover: #1e1e38;
            --fn-ref-hover: #2e2040;
            --panel-bg: #1a1a2e;
            --header-bg: #16162a;
        }}

        body {{
            background: var(--bg);
            color: var(--text);
            font-family: var(--font-english);
            margin: 0;
            display: flex;
            height: 100vh;
            overflow: hidden;
            transition: background 0.3s, color 0.3s;
        }}

        /* TOC Drawer */
        .toc-drawer {{
            position: fixed;
            top: 0; left: 0;
            width: 280px;
            height: 100vh;
            background: var(--panel-bg);
            border-right: 1px solid var(--border);
            z-index: 500;
            transform: translateX(-100%);
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            flex-direction: column;
            box-shadow: 4px 0 20px rgba(0,0,0,0.15);
        }}
        .toc-drawer.open {{ transform: translateX(0); }}

        .toc-header-bar {{
            display: flex; justify-content: space-between; align-items: center;
            padding: 16px 20px; border-bottom: 1px solid var(--border);
            font-weight: bold; color: var(--text);
        }}
        .toc-header-bar button {{
            background: none; border: none; font-size: 1.2rem;
            cursor: pointer; color: var(--text-muted);
        }}

        .toc-body {{ flex: 1; overflow-y: auto; padding-bottom: 20px; }}

        .toc-backdrop {{
            display: none; position: fixed; inset: 0;
            background: rgba(0,0,0,0.4); z-index: 499;
        }}
        .toc-backdrop.visible {{ display: block; }}

        .toc-tile-grid {{
            display: grid; grid-template-columns: repeat(5, 1fr);
            gap: 6px; padding: 8px 12px 16px;
        }}
        .toc-tile {{
            aspect-ratio: 1; display: flex; align-items: center; justify-content: center;
            border-radius: 6px; border: 1px solid var(--border);
            cursor: pointer; font-size: 0.8rem; font-weight: 600;
            transition: background 0.15s, color 0.15s;
            color: var(--text); background: var(--surface);
        }}
        .toc-tile:hover, .toc-tile.active {{
            background: var(--accent); color: white; border-color: var(--accent);
        }}

        .toc-section-btn {{
            width: 100%; text-align: left; padding: 12px 16px;
            border: none; background: none; color: var(--text);
            font-weight: 600; font-size: 0.9rem; cursor: pointer;
            display: flex; justify-content: space-between;
            border-bottom: 1px solid var(--border);
        }}
        .toc-section-btn:hover {{ background: var(--row-hover); }}
        .toc-section-btn .arrow {{ transition: transform 0.2s; }}
        .toc-section-btn.open .arrow {{ transform: rotate(90deg); }}

        /* Main Layout */
        .main-container {{
            flex: 1; display: flex; flex-direction: column; overflow-y: auto;
            transition: padding-bottom 0.3s;
        }}
        .main-container.fn-open {{ padding-bottom: 25vh; }}

        .header {{
            padding: 15px 40px; background: var(--header-bg);
            border-bottom: 1px solid var(--border);
            position: sticky; top: 0; z-index: 100;
            display: flex; justify-content: space-between; align-items: center;
            transition: background 0.3s, border-color 0.3s;
        }}
        .header-left {{ display: flex; align-items: center; gap: 20px; }}
        #hamburger-btn {{
            background: none; border: none; font-size: 1.5rem;
            cursor: pointer; color: var(--text); padding: 5px;
        }}
        .header h1 {{ margin: 0; font-size: 1.5rem; color: var(--text); }}
        .header p {{ margin: 5px 0 0 0; color: var(--text-muted); font-size: 0.9rem; }}

        .theme-controls {{ display: flex; gap: 5px; }}
        .theme-btn {{
            background: var(--surface); border: 1px solid var(--border);
            border-radius: 4px; padding: 6px 10px; cursor: pointer;
            font-size: 1rem;
        }}
        .theme-btn.active {{ border-color: var(--accent); background: var(--row-hover); }}

        .content {{ padding: 20px 40px; max-width: 1200px; margin: 0 auto; width: 100%; box-sizing: border-box; }}
        .chapter-section {{ display: none; }}

        /* Parallel View */
        .parallel-row {{
            display: grid; grid-template-columns: 1fr 1fr; gap: 40px;
            padding: 24px 0; border-bottom: 1px solid var(--border);
            transition: background 0.2s;
        }}
        .parallel-row:hover {{ background: var(--row-hover); }}
        .en-cell {{ 
            font-family: var(--font-english), var(--font-hebrew);
            font-size: 1.1rem; 
            line-height: 1.7; 
            text-align: justify; 
        }}
        .he-cell {{
            font-family: var(--font-hebrew); font-size: 1.3rem; line-height: 1.6;
            direction: rtl; text-align: right; color: var(--text);
        }}
        .chapter-header {{
            grid-column: span 2; padding: 40px 0 20px;
            border-bottom: 2px solid var(--accent); margin-bottom: 20px;
        }}
        .chapter-header h2 {{ margin: 0; color: var(--accent); font-weight: 700; }}

        .fn-ref {{
            color: var(--accent); font-weight: bold; cursor: pointer;
            padding: 0 2px; border-radius: 4px;
        }}
        .fn-ref:hover {{ background: var(--fn-ref-hover); }}

        .full-text-bar {{
            text-align: center; padding: 40px 0; margin-top: 20px;
            border-top: 1px solid var(--border);
        }}
        #full-text-toggle-btn {{
            background: var(--surface); border: 1px solid var(--accent); color: var(--accent);
            padding: 10px 24px; border-radius: 20px; font-weight: bold; cursor: pointer;
            transition: all 0.2s;
        }}
        #full-text-toggle-btn:hover {{ background: var(--accent); color: white; }}

        /* Footnote Bottom Panel */
        .fn-panel {{
            position: fixed; bottom: 0; left: 0; right: 0; height: 0;
            background: var(--panel-bg); border-top: 2px solid var(--accent);
            z-index: 300; transition: height 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex; flex-direction: column; overflow: hidden;
            box-shadow: 0 -5px 20px rgba(0,0,0,0.05);
        }}
        .fn-panel.open {{ height: 25vh; min-height: 160px; }}

        .fn-panel-header {{
            display: flex; justify-content: space-between; align-items: center;
            padding: 10px 24px; border-bottom: 1px solid var(--border);
            flex-shrink: 0; background: var(--header-bg);
        }}
        .fn-panel-label {{
            font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em;
            color: var(--text-muted); font-weight: 600;
        }}
        .fn-panel-close {{
            font-size: 0.8rem; color: var(--text-muted);
            background: none; border: none; cursor: pointer;
            padding: 4px 8px; border-radius: 4px;
        }}
        .fn-panel-close:hover {{ background: var(--row-hover); }}

        .fn-panel-body {{
            font-family: var(--font-english), var(--font-hebrew);
            flex: 1; overflow-y: auto; padding: 16px 24px;
            font-size: 0.95rem; line-height: 1.7; color: var(--text);
        }}
        .mediumGrey {{ color: var(--accent); font-size: 0.95em; display: block; margin-top: 1.5em; margin-bottom: 0.5em; font-weight: 700; text-transform: uppercase; letter-spacing: 0.02em; }}
    </style>
</head>
<body>

    <!-- TOC Elements -->
    <div id="toc-backdrop" class="toc-backdrop" onclick="toggleTOC()"></div>
    <nav id="toc-drawer" class="toc-drawer">
        <div class="toc-header-bar">
            <span>Contents</span>
            <button onclick="toggleTOC()">✕</button>
        </div>
        <div id="toc-body" class="toc-body"></div>
    </nav>

    <!-- Main Reader -->
    <div class="main-container">
        <div class="header">
            <div class="header-left">
                <button id="hamburger-btn" onclick="toggleTOC()" aria-label="Table of Contents">☰</button>
                <div>
                    <h1>Salomon Munk - Guide for the Perplexed</h1>
                    <p id="current-chapter-label">Parallel Reader: Modern English & Makbili Hebrew</p>
                </div>
            </div>
            <div class="theme-controls">
                <button onclick="setTheme('light')" title="Light" class="theme-btn" id="btn-light">☀️</button>
                <button onclick="setTheme('sepia')" title="Sepia" class="theme-btn" id="btn-sepia">📜</button>
                <button onclick="setTheme('dark')"  title="Dark"  class="theme-btn" id="btn-dark">🌙</button>
            </div>
        </div>
        <div class="content">
            {rows_html}
            <div class="full-text-bar">
                <button id="full-text-toggle-btn" onclick="fullTextMode ? exitFullText() : enterFullText()">
                    Show Full Text
                </button>
            </div>
        </div>
    </div>

    <!-- Footnote Panel -->
    <div id="fn-panel" class="fn-panel">
        <div class="fn-panel-header">
            <span id="fn-panel-label" class="fn-panel-label">Scholarly Note</span>
            <button class="fn-panel-close" onclick="closeFnPanel()">✕ Hide</button>
        </div>
        <div id="fn-panel-body" class="fn-panel-body">
            <!-- Content injected by showFn() -->
        </div>
    </div>

    <!-- Data -->
    <script type="application/json" id="footnote-data">{footnotes_json}</script>
    <script>
        const footnotes = JSON.parse(document.getElementById('footnote-data').textContent);
        const chapterIndex = {chapter_index_js};
        
        // Theme Management
        function setTheme(mode) {{
            document.documentElement.className = mode === 'light' ? '' : mode;
            localStorage.setItem('munk-theme', mode);
            document.querySelectorAll('.theme-btn').forEach(b => b.classList.remove('active'));
            const activeBtn = document.getElementById('btn-' + mode);
            if(activeBtn) activeBtn.classList.add('active');
        }}
        const savedTheme = localStorage.getItem('munk-theme') || 'light';
        setTheme(savedTheme);

        // TOC Building
        function buildTOC() {{
            const body = document.getElementById('toc-body');
            const groups = {{
                'Introductions': ['Letter to R Joseph son of Judah', 'Prefatory Remarks', 'Part 1 - Introduction'],
                'Part 1': [],
                'Part 2': [],
                'Part 3': [],
            }};

            chapterIndex.forEach(ch => {{
                const m = ch.title.match(/^Part (\\d) - Chapter (\\d+)$/);
                if (m) groups[`Part ${{m[1]}}`].push({{ title: ch.title, num: parseInt(m[2]), id: ch.id }});
            }});

            for (const [groupName, chapters] of Object.entries(groups)) {{
                if (groupName !== 'Introductions' && chapters.length === 0) continue;

                const btn = document.createElement('button');
                btn.className = 'toc-section-btn';
                btn.innerHTML = `${{groupName}} <span class="arrow">›</span>`;
                body.appendChild(btn);

                const panel = document.createElement('div');
                panel.style.display = 'none';

                if (groupName === 'Introductions') {{
                    groups['Introductions'].forEach(title => {{
                        const tile = document.createElement('div');
                        tile.className = 'toc-tile';
                        tile.style.gridColumn = 'span 5';
                        tile.style.padding = '8px';
                        tile.textContent = title.replace('Part 1 - ', '').replace('Letter to R Joseph son of Judah', 'Epistle');
                        tile.onclick = () => navigateToChapter(title);
                        panel.appendChild(tile);
                    }});
                    panel.style.padding = '0 12px 16px';
                    panel.style.display = 'grid';
                    panel.style.gap = '6px';
                }} else {{
                    const grid = document.createElement('div');
                    grid.className = 'toc-tile-grid';
                    chapters.forEach(ch => {{
                        const tile = document.createElement('div');
                        tile.className = 'toc-tile';
                        tile.dataset.chapterId = ch.id;
                        tile.textContent = ch.num;
                        tile.onclick = () => navigateToChapter(ch.title);
                        grid.appendChild(tile);
                    }});
                    panel.appendChild(grid);
                }}

                btn.onclick = () => {{
                    const isIntro = groupName === 'Introductions';
                    const isHidden = panel.style.display === 'none';
                    panel.style.display = isHidden ? (isIntro ? 'grid' : 'block') : 'none';
                    btn.classList.toggle('open', isHidden);
                }};

                body.appendChild(panel);
            }}
        }}

        function toggleTOC() {{
            document.getElementById('toc-drawer').classList.toggle('open');
            document.getElementById('toc-backdrop').classList.toggle('visible');
        }}

        // Navigation
        let fullTextMode = false;
        let activeChapterId = null;

        function navigateToChapter(title) {{
            if (fullTextMode) exitFullText();

            const id = 'chapter-' + title.replace(/ /g, '-').replace(/\\//g, '-');
            document.querySelectorAll('.chapter-section').forEach(s => {{
                s.style.display = s.id === id ? 'block' : 'none';
            }});

            activeChapterId = id;
            document.getElementById('current-chapter-label').textContent = title;

            document.querySelectorAll('.toc-tile').forEach(t => {{
                t.classList.toggle('active', t.dataset.chapterId === id || t.textContent === title.replace('Part 1 - ', '').replace('Letter to R Joseph son of Judah', 'Epistle'));
            }});

            const drawer = document.getElementById('toc-drawer');
            if(drawer.classList.contains('open')) toggleTOC();
            document.querySelector('.main-container').scrollTop = 0;
        }}

        function enterFullText() {{
            fullTextMode = true;
            document.querySelectorAll('.chapter-section').forEach(s => s.style.display = 'block');
            document.getElementById('current-chapter-label').textContent = 'Full Text Mode';
            document.getElementById('full-text-toggle-btn').textContent = 'Exit Full Text';
            document.querySelectorAll('.toc-tile').forEach(t => t.classList.remove('active'));
        }}

        function exitFullText() {{
            fullTextMode = false;
            if (activeChapterId) {{
                const title = document.getElementById(activeChapterId).dataset.title;
                navigateToChapter(title);
            }} else {{
                navigateToChapter(chapterIndex[0].title);
            }}
            document.getElementById('full-text-toggle-btn').textContent = 'Show Full Text';
        }}

        // Footnotes
        function showFn(id) {{
            const raw = footnotes[id];
            const num = id.replace('fn.', '');
            // Strip [[t:N]] structural placeholder tags that are not needed for display
            const text = raw ? raw.replace(/\[\[t:\d+\]\]/g, '') : null;
            
            document.getElementById('fn-panel-label').textContent = `Note ${{num}}`;
            document.getElementById('fn-panel-body').innerHTML = text 
                ? text 
                : '<em>Footnote translation still in progress...</em>';
                
            document.getElementById('fn-panel').classList.add('open');
            document.querySelector('.main-container').classList.add('fn-open');
        }}

        function closeFnPanel() {{
            document.getElementById('fn-panel').classList.remove('open');
            document.querySelector('.main-container').classList.remove('fn-open');
        }}

        // Init
        window.addEventListener('DOMContentLoaded', () => {{
            buildTOC();
            if (chapterIndex.length > 0) {{
                navigateToChapter(chapterIndex[0].title);
            }}
        }});
    </script>
</body>
</html>
    """
    
    with open("Part1_Munk_Viewer.html", "w") as f:
        f.write(html_template)
    
    print(f"Success! Viewer generated at: Part1_Munk_Viewer.html")

if __name__ == "__main__":
    build_viewer()
