import json
import os
import re

# Create output directory
os.makedirs("viewer", exist_ok=True)

def get_filename(title):
    if title == "Contents":
        return "index.html"
    return title.replace(' ', '-').replace('/', '-').replace('.', '') + ".html"

def generate_nav_links(prev_ch, next_ch):
    html = '<div class="chapter-nav" style="display:flex; justify-content:space-between; margin-top:40px; padding-top:20px; border-top:1px solid var(--border);">'
    if prev_ch:
        html += f'<a href="javascript:void(0)" onclick="navigateToChapter(\'{prev_ch["title"]}\')" class="nav-btn" style="text-decoration:none; color:var(--accent); font-weight:bold;">← Previous: {prev_ch["title"]}</a>'
    else:
        html += '<div></div>'
        
    if next_ch:
        html += f'<a href="javascript:void(0)" onclick="navigateToChapter(\'{next_ch["title"]}\')" class="nav-btn" style="text-decoration:none; color:var(--accent); font-weight:bold;">Next: {next_ch["title"]} →</a>'
    else:
        html += '<div></div>'
    html += '</div>'
    return html

def render_html(page_title, main_content_html, chapter_index_js, footnotes_json, display_title=None):
    if display_title is None:
        display_title = page_title
    # This template uses double curly braces for CSS/JS that aren't f-string variables
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title} - Munk Parallel Reader</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=Frank+Ruhl+Libre:wght@400;700&family=Amiri&display=swap" rel="stylesheet">
    <link rel="manifest" href="../manifest.json">
    <style>
        :root {{
            --bg: #fdfcfb; --surface: #ffffff; --text: #1a1a1a; --text-muted: #6b7280;
            --accent: #8b5cf6; --border: #e5e7eb; --row-hover: #f9fafb; --fn-ref-hover: #f3e8ff;
            --panel-bg: #ffffff; --header-bg: #ffffff; --font-hebrew: 'Frank Ruhl Libre', serif;
            --font-english: 'Inter', sans-serif;
        }}
        html.sepia {{
            --bg: #f4ecd8; --surface: #ede3c8; --text: #3c2f1e; --text-muted: #7a6040;
            --accent: #a0522d; --border: #c9b89a; --row-hover: #ecdfc8; --fn-ref-hover: #d4b896;
            --panel-bg: #ede3c8; --header-bg: #e8dcc5;
        }}
        html.dark {{
            --bg: #12121e; --surface: #1e1e30; --text: #e2e2e2; --text-muted: #9ca3af;
            --accent: #a78bfa; --border: #2e2e46; --row-hover: #1e1e38; --fn-ref-hover: #2e2040;
            --panel-bg: #1a1a2e; --header-bg: #16162a;
        }}
        body {{ background: var(--bg); color: var(--text); font-family: var(--font-english); margin: 0; display: flex; height: 100vh; overflow: hidden; transition: background 0.3s, color 0.3s; }}
        
        /* Dynamic Column Visibility Rules */
        .main-container[data-col1="en"] .col1-variant:not(.variant-en) {{ display: none !important; }}
        .main-container[data-col1="fr"] .col1-variant:not(.variant-fr) {{ display: none !important; }}

        .main-container[data-col2="makbili"] .col2-variant:not(.variant-makbili) {{ display: none !important; }}
        .main-container[data-col2="jrb"] .col2-variant:not(.variant-jrb) {{ display: none !important; }}
        .main-container[data-col2="tibon"] .col2-variant:not(.variant-tibon) {{ display: none !important; }}
        .main-container[data-col2="fr"] .col2-variant:not(.variant-fr) {{ display: none !important; }}

        /* Typography & Direction Overrides */
        .col2-variant.variant-fr {{ direction: ltr; text-align: left; font-family: var(--font-english); font-size: 1.1rem; display: block; }}
        .col1-variant.variant-fr {{ direction: ltr; text-align: left; font-family: var(--font-english); display: block; }}
        .col1-variant.variant-en, .col2-variant:not(.variant-fr) {{ display: block; }}

        .toc-drawer {{ position: fixed; top: 0; left: 0; width: 320px; height: 100vh; background: var(--panel-bg); border-right: 1px solid var(--border); z-index: 500; transform: translateX(-100%); transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1); display: flex; flex-direction: column; box-shadow: 4px 0 20px rgba(0,0,0,0.15); }}
        .toc-drawer.open {{ transform: translateX(0); }}
        .toc-header-bar {{ display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid var(--border); font-weight: bold; color: var(--text); }}
        .toc-header-bar button {{ background: none; border: none; font-size: 1.2rem; cursor: pointer; color: var(--text-muted); }}
        .mobile-theme-panel {{ display: none; }}
        @media (max-width: 768px) {{ .mobile-theme-panel {{ display: flex; justify-content: space-around; padding: 16px; background: var(--header-bg); border-bottom: 1px solid var(--border); }} }}
        .toc-body {{ flex: 1; overflow-y: auto; padding-bottom: 20px; }}
        .toc-backdrop {{ display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 499; }}
        .toc-backdrop.visible {{ display: block; }}
        .toc-tile-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; padding: 8px 12px 16px; }}
        .toc-tile {{ aspect-ratio: 1; display: flex; align-items: center; justify-content: center; border-radius: 6px; border: 1px solid var(--border); cursor: pointer; font-size: 0.8rem; font-weight: 600; transition: background 0.15s, color 0.15s; color: var(--text); background: var(--surface); }}
        .toc-tile:hover, .toc-tile.active {{ background: var(--accent); color: white; border-color: var(--accent); }}
        .toc-section-btn {{ width: 100%; text-align: left; padding: 12px 16px; border: none; background: none; color: var(--text); font-weight: 600; font-size: 0.9rem; cursor: pointer; display: flex; justify-content: space-between; border-bottom: 1px solid var(--border); }}
        .toc-section-btn .arrow {{ transition: transform 0.2s; }}
        .toc-section-btn.open .arrow {{ transform: rotate(90deg); }}
        .main-container {{ flex: 1; display: flex; flex-direction: column; overflow-y: auto; transition: padding-bottom 0.3s; }}
        .main-container.fn-open {{ padding-bottom: 25vh; }}
        .header {{ padding: 15px 40px; background: var(--header-bg); border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 100; display: flex; justify-content: space-between; align-items: center; transition: background 0.3s, border-color 0.3s; }}
        .header-left {{ display: flex; align-items: center; gap: 20px; flex: 1; }}
        #hamburger-btn {{ background: none; border: none; font-size: 1.5rem; cursor: pointer; color: var(--text); padding: 5px; }}
        .header h1 {{ margin: 0; font-size: 1.4rem; color: var(--text); font-weight: 700; flex: 1; }}
        .header .munk-label {{ color: var(--text-muted); font-size: 0.8rem; margin-right: 20px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }}
        .theme-controls {{ display: flex; gap: 5px; }}
        .theme-btn {{ background: var(--surface); border: 1px solid var(--border); border-radius: 4px; padding: 6px 10px; cursor: pointer; font-size: 1rem; color:var(--text); }}
        .theme-btn.active {{ border-color: var(--accent); background: var(--row-hover); }}
        .content {{ padding: 20px 40px; max-width: 1200px; margin: 0 auto; width: 100%; box-sizing: border-box; }}
        
        /* Responsive UI Header Components */
        .column-selectors-bar {{ display: grid; grid-template-columns: 1fr 1fr; gap: 40px; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 2px solid var(--border); }}
        .column-selectors-bar div {{ display: flex; align-items: center; gap: 12px; }}
        .column-selectors-bar label {{ font-size: 0.85rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; }}
        .column-selectors-bar select {{ flex: 1; padding: 8px 12px; border-radius: 6px; border: 1px solid var(--border); background: var(--surface); color: var(--text); font-size: 0.95rem; font-weight: 600; cursor: pointer; outline: none; transition: border-color 0.2s, background 0.2s, color 0.2s; }}
        .column-selectors-bar select:hover, .column-selectors-bar select:focus {{ border-color: var(--accent); }}

        .parallel-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 40px; padding: 24px 0; border-bottom: 1px solid var(--border); transition: background 0.2s; }}
        .parallel-row:hover {{ background: var(--row-hover); }}
        .en-cell {{ font-family: var(--font-english), var(--font-hebrew); font-size: 1.1rem; line-height: 1.7; text-align: left; }}
        .he-cell {{ font-family: var(--font-hebrew); font-size: 1.3rem; line-height: 1.6; direction: rtl; text-align: right; color: var(--text); }}
        .fr-cell {{ font-family: var(--font-english); font-size: 1.1rem; line-height: 1.7; text-align: left; }}
        .chapter-header {{ grid-column: span 2; padding: 40px 0 20px; border-bottom: 2px solid var(--accent); margin-bottom: 20px; }}
        .chapter-header h2 {{ margin: 0; color: var(--accent); font-weight: 700; }}
        .poem-segment {{ color: var(--text-muted); font-size: 0.95rem; font-style: italic; }}
        
        /* Mobile Layout Optimizations */
        @media (max-width: 768px) {{
            .column-selectors-bar {{ display: flex; flex-direction: column; gap: 16px; }}
            .column-selectors-bar div {{ width: 100%; justify-content: space-between; }}
            .column-selectors-bar select {{ width: auto; flex: 1; margin-left: 12px; }}
            
            .header {{ padding: 10px 16px; }}
            .header .munk-label {{ display: none; }}
            .header h1 {{ font-size: 1.1rem; }}
            .theme-controls {{ display: none; }}
            .parallel-row {{ display: flex; flex-direction: column; gap: 12px; padding: 16px 0; }}
            .en-cell {{ font-size: 1rem; padding-top: 8px; border-top: 1px dashed var(--border); }}
            .fr-cell {{ font-size: 1rem; }}
            .he-cell {{ font-size: 1.2rem; order: -1; }}
            .chapter-header {{ padding: 24px 0 12px; order: -2; }}
            .chapter-header h2 {{ font-size: 1.4rem; }}
            .content {{ padding: 10px 16px; }}
        }}
        .header-row {{ border-bottom: none; padding-bottom: 0; padding-top: 32px; }}
        .header-row .he-cell {{ border-bottom: 2px solid var(--accent); display: inline-block; width: auto; padding-bottom: 4px; }}
        
        /* Unified Subheading Line-Underneath Styles */
        .mediumGrey {{
            display: block;
            color: var(--accent);
            font-size: 1.15rem;
            font-weight: 700;
            border-bottom: 2px solid var(--accent);
            padding-bottom: 6px;
            margin-bottom: 16px;
            margin-top: 12px;
            width: 100%;
        }}
        
        .toc-landing-page {{ padding: 40px 0; max-width: 900px; margin: 0 auto; }}
        .landing-title {{ font-family: var(--font-hebrew); font-size: 3rem; margin-bottom: 8px; color: var(--text); text-align: center; }}
        .landing-subtitle {{ text-align: center; color: var(--text-muted); margin-bottom: 60px; font-size: 1.1rem; letter-spacing: 0.1em; text-transform: uppercase; }}
        .landing-section {{ margin-bottom: 40px; }}
        .landing-section h3 {{ border-bottom: 2px solid var(--accent); padding-bottom: 8px; margin-bottom: 20px; font-size: 1.2rem; color: var(--accent); }}
        .landing-links {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; }}
        .landing-links a {{ color: var(--text); text-decoration: none; padding: 8px 12px; border-radius: 4px; background: var(--surface); border: 1px solid var(--border); font-size: 0.9rem; transition: all 0.2s; display: block; text-align: center; }}
        .landing-links a:hover {{ background: var(--accent); color: white; border-color: var(--accent); }}
        .fn-panel {{ position: fixed; bottom: 0; left: 0; right: 0; height: 0; max-height: 35vh; background: var(--panel-bg); border-top: 2px solid var(--accent); z-index: 400; overflow: hidden; transition: height 0.3s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 -4px 20px rgba(0,0,0,0.12); display: flex; flex-direction: column; }}
        .fn-panel.open {{ height: 25vh; }}
        .fn-panel-header {{ display: flex; justify-content: space-between; align-items: center; padding: 10px 24px; border-bottom: 1px solid var(--border); background: var(--header-bg); flex-shrink: 0; }}
        .fn-panel-label {{ font-weight: 700; color: var(--accent); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em; }}
        .fn-panel-close {{ background: none; border: 1px solid var(--border); border-radius: 6px; padding: 4px 12px; cursor: pointer; color: var(--text-muted); font-size: 0.8rem; transition: all 0.2s; }}
        .fn-panel-close:hover {{ background: var(--accent); color: white; border-color: var(--accent); }}
        .fn-panel-body {{ font-family: var(--font-english), var(--font-hebrew); padding: 16px 24px; overflow-y: auto; flex: 1; font-size: 1rem; line-height: 1.7; color: var(--text); }}
        .fn-ref {{ color: var(--accent); cursor: pointer; font-weight: 600; transition: background 0.15s; padding: 0 2px; border-radius: 2px; }}
        .fn-ref:hover {{ background: var(--fn-ref-hover); }}
        .feedback-footer {{ margin-top: 60px; padding-top: 24px; border-top: 1px solid var(--border); text-align: center; }}
        .feedback-footer a {{ display: inline-block; padding: 10px 20px; font-size: 0.95rem; font-weight: 600; color: var(--text-muted); background: var(--surface); border: 1px solid var(--border); border-radius: 6px; text-decoration: none; transition: all 0.2s; }}
        .feedback-footer a:hover {{ background: var(--accent); color: white; border-color: var(--accent); }}
        .update-toast {{ position: fixed; bottom: 20px; right: 20px; background: var(--text); color: var(--surface); padding: 12px 20px; border-radius: 8px; font-size: 0.95rem; font-weight: 600; box-shadow: 0 10px 25px rgba(0,0,0,0.2); z-index: 1000; cursor: pointer; display: none; align-items: center; gap: 10px; }}
        .update-toast:hover {{ opacity: 0.9; }}
    </style>
</head>
<body>
    <div id="toc-backdrop" class="toc-backdrop" onclick="toggleTOC()"></div>
    <nav id="toc-drawer" class="toc-drawer">
        <div class="toc-header-bar">
            <span onclick="navigateToChapter('Contents')" style="cursor:pointer">Contents</span>
            <span onclick="showAllChapters()" style="color:var(--text-muted); cursor:pointer; font-size:0.8rem; margin-left:10px; border:1px solid var(--border); padding:2px 6px; border-radius:4px;">Full Text</span>
            <button onclick="toggleTOC()">✕</button>
        </div>
        <div class="mobile-theme-panel">
            <button onclick="setTheme('light')" class="theme-btn">☀️ Light</button>
            <button onclick="setTheme('sepia')" class="theme-btn">📜 Sepia</button>
            <button onclick="setTheme('dark')"  class="theme-btn">🌙 Dark</button>
        </div>
        <div id="toc-body" class="toc-body"></div>
    </nav>
    <div class="main-container" data-col1="en" data-col2="makbili">
        <div class="header">
            <div class="header-left">
                <button id="hamburger-btn" onclick="toggleTOC()" aria-label="Table of Contents">☰</button>
                <h1 id="main-title">{display_title}</h1>
                <span class="munk-label">Dalalat al-Ha'irin</span>
            </div>
            <div class="theme-controls">
                <button onclick="setTheme('light')" title="Light" class="theme-btn" id="btn-light">☀️</button>
                <button onclick="setTheme('sepia')" title="Sepia" class="theme-btn" id="btn-sepia">📜</button>
                <button onclick="setTheme('dark')"  title="Dark"  class="theme-btn" id="btn-dark">🌙</button>
            </div>
        </div>
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
            <div class="feedback-footer">
                <a href="https://github.com/rayhabbaz/Munk-Guide/issues/new?title=Correction:%20{display_title}" target="_blank" rel="noopener noreferrer">Propose an Edit on GitHub</a>
            </div>
        </div>
    </div>
    <div id="fn-panel" class="fn-panel">
        <div class="fn-panel-header">
            <span id="fn-panel-label" class="fn-panel-label">Scholarly Note</span>
            <button class="fn-panel-close" onclick="closeFnPanel()">✕ Hide</button>
        </div>
        <div id="fn-panel-body" class="fn-panel-body"></div>
    </div>
    <script type="application/json" id="footnote-data">{footnotes_json}</script>
    <script>
        const footnotes = JSON.parse(document.getElementById('footnote-data').textContent);
        const chapterIndex = {chapter_index_js};
        function setTheme(mode) {{
            document.documentElement.className = mode === 'light' ? '' : mode;
            localStorage.setItem('munk-theme', mode);
            document.querySelectorAll('.theme-btn').forEach(b => b.classList.remove('active'));
            const activeBtn = document.getElementById('btn-' + mode);
            if(activeBtn) activeBtn.classList.add('active');
        }}
        setTheme(localStorage.getItem('munk-theme') || 'light');
        function buildTOC() {{
            const body = document.getElementById('toc-body');
            const groups = {{ "Munk's Prefaces": ["Introduction to Volume I", "Introduction to Volume II", "Introduction to Volume III", "Note On The Title"], "Munk's Endnotes": ["Endnotes to Volume I", "Endnotes to Volume II", "Endnotes to Volume III"], 'Introductions': ['Letter to R Joseph son of Judah', 'Prefatory Remarks'], 'Part 1': [], 'Part 2': [], 'Part 3': [] }};
            chapterIndex.forEach(ch => {{
                const m = ch.title.match(/^Part (\\d) - (Chapter \\d+|Introduction)$/);
                if (m) {{
                    const isIntro = m[2] === 'Introduction';
                    let num = isIntro ? 'Intro' : parseInt(m[2].replace('Chapter ', ''));
                    groups[`Part ${{m[1]}}`].push({{ title: ch.title, num: num, id: ch.id, isIntro: isIntro }});
                }}
            }});
            for (const [groupName, chapters] of Object.entries(groups)) {{
                if (groupName !== 'Introductions' && groupName !== "Munk's Prefaces" && groupName !== "Munk's Endnotes" && chapters.length === 0) continue;
                const btn = document.createElement('button');
                btn.className = 'toc-section-btn';
                btn.innerHTML = `${{groupName}} <span class="arrow">›</span>`;
                body.appendChild(btn);
                const panel = document.createElement('div');
                panel.style.display = 'none';
                if (groupName === 'Introductions' || groupName === "Munk's Prefaces" || groupName === "Munk's Endnotes") {{
                    groups[groupName].forEach(title => {{
                        if (!chapterIndex.some(c => c.title === title)) return;
                        const tile = document.createElement('div');
                        tile.className = 'toc-tile'; tile.style.gridColumn = 'span 5'; tile.style.padding = '8px'; tile.style.aspectRatio = 'auto';
                        let displayTitle = title.replace('Part 1 - ', '').replace('Part 2 - ', '').replace('Part 3 - ', '').replace('Letter to R Joseph son of Judah', 'Letter to R. Joseph');
                        tile.textContent = displayTitle;
                        const chId = 'chapter-' + title.replace(/ /g, '-').replace(/\\//g, '-').replace(/\\./g, '');
                        tile.dataset.chapterId = chId;
                        tile.onclick = () => navigateToChapter(title);
                        panel.appendChild(tile);
                    }});
                    panel.style.padding = '0 12px 16px'; panel.style.display = 'grid'; panel.style.gap = '6px';
                }} else {{
                    const grid = document.createElement('div');
                    grid.className = 'toc-tile-grid';
                    chapters.forEach(ch => {{
                        const tile = document.createElement('div');
                        tile.className = 'toc-tile'; tile.dataset.chapterId = ch.id; tile.textContent = ch.num;
                        if (ch.isIntro) {{ tile.style.gridColumn = 'span 5'; tile.style.aspectRatio = 'auto'; tile.style.padding = '8px'; }}
                        tile.onclick = () => navigateToChapter(ch.title);
                        grid.appendChild(tile);
                    }});
                    panel.appendChild(grid);
                }}
                btn.onclick = () => {{
                    const isHidden = panel.style.display === 'none';
                    const isListGroup = groupName === 'Introductions' || groupName === "Munk's Prefaces" || groupName === "Munk's Endnotes";
                    panel.style.display = isHidden ? (isListGroup ? 'grid' : 'block') : 'none';
                    btn.classList.toggle('open', isHidden);
                }};
                body.appendChild(panel);
            }}
        }}
        function toggleTOC() {{ document.getElementById('toc-drawer').classList.toggle('open'); document.getElementById('toc-backdrop').classList.toggle('visible'); }}
        
        let activeChapterId = null;
        function navigateToChapter(title) {{
            const id = title === 'Contents' ? 'chapter-Contents' : 'chapter-' + title.replace(/ /g, '-').replace(/\\//g, '-').replace(/\\./g, '');
            document.querySelectorAll('.chapter-section').forEach(s => {{
                s.style.display = s.id === id ? 'block' : 'none';
            }});
            activeChapterId = id;
            const titleElem = document.getElementById('main-title');
            if (titleElem) titleElem.textContent = title;
            
            document.querySelectorAll('.toc-tile').forEach(t => {{
                t.classList.toggle('active', t.dataset.chapterId === id);
            }});
            const drawer = document.getElementById('toc-drawer');
            if (drawer && drawer.classList.contains('open')) toggleTOC();
            const mainCont = document.querySelector('.main-container');
            if (mainCont) mainCont.scrollTop = 0;
        }}
        
        function showAllChapters() {{
            document.querySelectorAll('.chapter-section').forEach(s => {{
                s.style.display = 'block';
            }});
            const titleElem = document.getElementById('main-title');
            if (titleElem) titleElem.textContent = 'Full Text Reader';
            if (document.getElementById('toc-drawer').classList.contains('open')) toggleTOC();
            const mainCont = document.querySelector('.main-container');
            if (mainCont) mainCont.scrollTop = 0;
        }}

        let activeFnId = null;
        function showFn(id) {{
            const panel = document.getElementById('fn-panel');
            if (panel.classList.contains('open') && activeFnId === id) {{
                closeFnPanel();
                return;
            }}
            activeFnId = id;
            const raw = footnotes[id];
            const text = raw ? raw.replace(/\\[\\[t:\\d+\\]\\]/g, '').replace(/\\[\\[fn:\\d+\\]\\]/g, '') : null;
            document.getElementById('fn-panel-label').textContent = 'Note';
            document.getElementById('fn-panel-body').innerHTML = text || '<em>Footnote translation still in progress...</em>';
            panel.classList.add('open');
            document.querySelector('.main-container').classList.add('fn-open');
        }}
        function closeFnPanel() {{ activeFnId = null; document.getElementById('fn-panel').classList.remove('open'); document.querySelector('.main-container').classList.remove('fn-open'); }}
        window.addEventListener('DOMContentLoaded', () => {{ buildTOC(); navigateToChapter('Contents'); }});
        if ('serviceWorker' in navigator) {{
            window.addEventListener('load', () => {{
                navigator.serviceWorker.register('../sw.js').then(reg => {{
                    reg.addEventListener('updatefound', () => {{
                        const newWorker = reg.installing;
                        newWorker.addEventListener('statechange', () => {{
                            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {{
                                const toast = document.getElementById('update-toast');
                                if (toast) toast.style.display = 'flex';
                            }}
                        }});
                    }});
                }}).catch(() => {{}});
            }});
        }}
    </script>
    <div id="update-toast" class="update-toast" onclick="window.location.reload()">
        <span>🔄 Update available. Click to refresh.</span>
    </div>
</body>
</html>
"""

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

# Load Ibn Tibon Edition
tibon_local_path = "Guide for the Perplexed - he - Moreh Nevuchim, translated by Ibn Tibon.json"
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

def build_viewer():
    # 1. Load Data
    with open("Guide for the Perplexed - he - Makbili Edition, Mif'al Mishneh Torah, 2024.json", "r") as f:
        hebrew_data = json.load(f)
    
    with open("munk_production_v1.json", "r", encoding="utf-8") as f:
        prod_data = json.load(f)
        english_main = prod_data["text"]
        english_footnotes = prod_data["footnotes"]

    def get_en_text(key, default="[Translation Missing]"):
        if key in english_main:
            return english_main[key]
        sub_idx = 0
        merged_parts = []
        while f"{key}.sub_{sub_idx}" in english_main:
            merged_parts.append(english_main[f"{key}.sub_{sub_idx}"])
            sub_idx += 1
        if merged_parts:
            return " ".join(merged_parts)
        return default

    unified_chapters = []

    # --- Part 1 Section ---
    
    # Handle Munk's Introduction
    munk_intro_segments = []
    try:
        with open("preface_resegmented.json", "r", encoding="utf-8") as f:
            french_paras = json.load(f)
        with open("preface_english_final.json", "r", encoding="utf-8") as f:
            english_paras = json.load(f)
            
        for i in range(len(french_paras)):
            munk_intro_segments.append({
                "he": french_paras[i],
                "en": english_paras[i] if i < len(english_paras) else "[Translation Missing]"
            })
        unified_chapters.append({
            "title": "Introduction to Volume I",
            "is_french_intro": True,
            "custom_segments": munk_intro_segments
        })
        
        # Inject Munk's Introduction Footnotes
        english_footnotes["fn.3001"] = "In some manuscripts, the غ is rendered by ג̇ or ג̄, and the ج by ג."
        english_footnotes["fn.3002"] = "See the translation, p. 50, n. 3, and p. 351, n. 4."
        english_footnotes["fn.3003"] = "See the translation, p. 19, n. 2."
        english_footnotes["fn.3004"] = "Sometimes, to render the sentence clearer, I have added explanatory words in ( ) that are not found in the text; the parentheses of the original text have been indicated by [ ]."
        english_footnotes["fn.3005"] = "The importance that I believed I should attach to these indications did not permit me to shrink from the difficulties that my current situation opposes to such a task, and I have not hesitated in all my research, often taking a few vague memories as my starting point, to listen to long readings in order to achieve the desired goal. There are, I believe, in this first volume, only three citations whose location I have been unable to indicate: page 14, a passage from the Midrash or Haggadah (To expound the power, etc.), which is also cited by R. Moses ben Nahman in his Commentary on Genesis, but which perhaps no longer exists in our Midrashim; page 107, a passage from Alexander of Aphrodisias, which I did not have at my disposal; page 381, words attributed by the author to Galen regarding time."
    except FileNotFoundError:
        pass

    # Handle Introduction to Volume II
    try:
        with open("preface_vol2.json", "r", encoding="utf-8") as f:
            vol2_data = json.load(f)
            
        if "footnote_en" in vol2_data:
            english_footnotes["fn.3006"] = vol2_data["footnote_en"]
            
        vol2_segments = []
        for i in range(len(vol2_data["fr"])):
            vol2_segments.append({
                "he": vol2_data["fr"][i],
                "en": vol2_data["en"][i]
            })
        unified_chapters.append({
            "title": "Introduction to Volume II",
            "is_french_intro": True,
            "custom_segments": vol2_segments
        })
    except FileNotFoundError:
        pass

    # Handle Introduction to Volume III
    try:
        with open("preface_vol3.json", "r", encoding="utf-8") as f:
            vol3_data = json.load(f)
            
        if "footnotes_en" in vol3_data:
            for fn_id, fn_text in vol3_data["footnotes_en"].items():
                english_footnotes[f"fn.{fn_id}"] = fn_text
            
        vol3_segments = []
        for i in range(len(vol3_data["fr"])):
            vol3_segments.append({
                "he": vol3_data["fr"][i],
                "en": vol3_data["en"][i]
            })
        unified_chapters.append({
            "title": "Introduction to Volume III",
            "is_french_intro": True,
            "custom_segments": vol3_segments
        })
    except FileNotFoundError:
        pass

    # Handle Note On The Title
    try:
        with open("munk_title_note.json", "r", encoding="utf-8") as f:
            title_note_data = json.load(f)
            
        if "footnote_en" in title_note_data:
            english_footnotes["fn.3000"] = title_note_data["footnote_en"]
            
        title_note_segments = []
        for i in range(len(title_note_data["fr"])):
            title_note_segments.append({
                "he": title_note_data["fr"][i],
                "en": title_note_data["en"][i]
            })
        unified_chapters.append({
            "title": "Note On The Title",
            "display_title": title_note_data.get("title_en", "Note On The Title"),
            "is_french_intro": True,
            "custom_segments": title_note_segments
        })
    except FileNotFoundError:
        pass

    # Handle Munk's Endnotes Volumes I, II, and III
    endnote_files = [
        ("endnotes_vol1.json", "Endnotes to Volume I"),
        ("endnotes_vol2.json", "Endnotes to Volume II"),
        ("endnotes_vol3.json", "Endnotes to Volume III")
    ]
    for fn, en_title in endnote_files:
        try:
            with open(fn, "r", encoding="utf-8") as f:
                en_data = json.load(f)
            en_segments = []
            for i in range(len(en_data["fr"])):
                en_segments.append({
                    "he": en_data["fr"][i],
                    "en": en_data["en"][i]
                })
            unified_chapters.append({
                "title": en_title,
                "is_french_intro": True,
                "custom_segments": en_segments
            })
        except FileNotFoundError:
            pass
    
    # Handle Letter to R Joseph (Special Split)
    letter_he = hebrew_data["text"]["Letter to R Joseph son of Judah"]
    # The first element contains both the poem and the invocation.
    # Split them at the last <br>
    poem_plus_invocation = letter_he[0]
    parts = poem_plus_invocation.split("<br>")
    poem_he = "<br>".join(parts[:-1])
    invocation_he = parts[-1]
    
    # The address is in letter_he[2] (letter_he[1] is "--")
    address_he = letter_he[2:]
    
    # Construct manually aligned segments
    letter_segments = []
    
    # Segment 1: Poem
    letter_segments.append({
        "he": poem_he,
        "en": get_en_text("root.text.Letter to R Joseph son of Judah.Poem", 'My thought will guide you on the path of truth, and smooth the way.<br>Come, walk along its path, O all you who wander in the field of religion!<br>The impure and the ignorant shall not pass over it; it shall be called the sacred way.'),
        "is_poem": True
    })
    
    # Segment 2: Invocation
    letter_segments.append({
        "he": invocation_he,
        "en": get_en_text("root.text.Letter to R Joseph son of Judah.0", "In the name of the Eternal God of the Universe")
    })
    
    # Segment 3: Address body — Hebrew [2] is one segment, but English has .1 (salutation) + .2 (body)
    # Merge English .1 and .2 to align with Hebrew [2]
    en_salutation = get_en_text("root.text.Letter to R Joseph son of Judah.1", "")
    en_body = get_en_text("root.text.Letter to R Joseph son of Judah.2", "")
    en_address_merged = (en_salutation + " " + en_body).strip() if en_salutation else en_body
    letter_segments.append({
        "he": address_he[0],  # Hebrew [2] — full address
        "en": en_address_merged
    })
    
    # Segment 4: Closing — Hebrew [3] maps to English .3
    if len(address_he) > 1:
        en_closing = get_en_text("root.text.Letter to R Joseph son of Judah.3", "[Translation Missing]")
        letter_segments.append({"he": address_he[1], "en": en_closing})

    unified_chapters.append({
        "title": "Letter to R Joseph son of Judah",
        "custom_segments": letter_segments
    })
    
    # Handle Prefatory Remarks
    unified_chapters.append({
        "title": "Prefatory Remarks",
        "key_prefix": "root.text.Prefatory Remarks",
        "segments": hebrew_data["text"]["Prefatory Remarks"]
    })
    
    # Handle Part 1 Introduction
    part1_data = hebrew_data["text"]["Part 1"]
    if "Introduction" in part1_data:
        unified_chapters.append({
            "title": "Part 1 - Introduction",
            "key_prefix": "root.text.Part 1.Introduction",
            "segments": part1_data["Introduction"]
        })
    
    # Handle Part 1 Chapters
    if "" in part1_data:
        for ch_idx, segments in enumerate(part1_data[""]):
            unified_chapters.append({
                "title": f"Part 1 - Chapter {ch_idx + 1}",
                "key_prefix": f"root.text.Part 1..{ch_idx}",
                "segments": segments
            })

    # --- Part 2 Section ---
    part2_data = hebrew_data["text"]["Part 2"]
    if "Introduction" in part2_data:
        unified_chapters.append({
            "title": "Part 2 - Introduction",
            "key_prefix": "root.text.Part 2.Introduction",
            "segments": part2_data["Introduction"]
        })
    
    if "" in part2_data:
        for ch_idx, segments in enumerate(part2_data[""]):
            unified_chapters.append({
                "title": f"Part 2 - Chapter {ch_idx + 1}",
                "key_prefix": f"root.text.Part 2..{ch_idx}",
                "segments": segments
            })

    # --- Part 3 Section ---
    part3_data = hebrew_data["text"]["Part 3"]
    if "Introduction" in part3_data:
        unified_chapters.append({
            "title": "Part 3 - Introduction",
            "key_prefix": "root.text.Part 3.Introduction",
            "segments": part3_data["Introduction"]
        })
    
    if "" in part3_data:
        for ch_idx, segments in enumerate(part3_data[""]):
            unified_chapters.append({
                "title": f"Part 3 - Chapter {ch_idx + 1}",
                "key_prefix": f"root.text.Part 3..{ch_idx}",
                "segments": segments
            })

    # 3. Build HTML Content
    rows_html = ""
    
    def repair_tags(html):
        # Stack-based repair for common tags used in the corpus
        tags_to_track = ['i', 'b', 'sup', 'span', 'em', 'strong']
        stack = []
        # Pattern to find tags like <i>, <i class="...">, </i>, but not <br> or <hr>
        pattern = re.compile(r'<(/?)(i|b|sup|span|em|strong)(\s+[^>]*)?>', re.IGNORECASE)
        
        for match in pattern.finditer(html):
            is_closing = match.group(1) == "/"
            tag_name = match.group(2).lower()
            
            if is_closing:
                if stack and stack[-1] == tag_name:
                    stack.pop()
                # Else: stray closing tag, we ignore it for safety
            else:
                stack.append(tag_name)
        
        # Append missing closing tags
        for tag in reversed(stack):
            html += f'</{tag}>'
        return html

    def process_en(en_text, is_asterisk=False, fn_counter=None):
        def replace_fn(match):
            fn_id_num = match.group(1)
            full_id = f"fn.{fn_id_num}"
            if is_asterisk:
                marker = "*"
            else:
                if fn_counter is not None:
                    fn_counter[0] += 1
                    marker = str(fn_counter[0])
                else:
                    marker = match.group(2) if match.lastindex >= 2 and match.group(2) else fn_id_num
            return f'<sup class="fn-ref" title="View Footnote" onclick="showFn(\'{full_id}\')">{marker}</sup>'
        
        en_processed = re.sub(r"\[\[fn:(\d+)(?:\|([^\]]+))?\]\]", replace_fn, en_text)
        en_processed = re.sub(r"\[\[t:\d+\]\]", "", en_processed)
        return repair_tags(en_processed)

    def render_row(he_text, en_text, key=None, is_asterisk=False, fn_counter=None):
        clean_he = re.sub(r'^(<br>)+|(<br>)+$', '', he_text).strip()
        row_id = f'id="row-{key}"' if key else ""
        
        # Load column alternative variant texts safely
        jrb_text = get_variant_text(jrb_main, key) if key else "[Text Missing in this Edition]"
        tibon_text = get_variant_text(tibon_main, key) if key else "[Text Missing in this Edition]"
        fr_text_raw = get_variant_text(french_main, key) if key else "[Text Missing in this Edition]"
        
        # Process French text to ensure any footnote references are clickable without advancing the shared counter
        saved_counter = fn_counter[0] if fn_counter is not None else None
        fr_processed = process_en(fr_text_raw, is_asterisk=is_asterisk, fn_counter=fn_counter)
        if fn_counter is not None and saved_counter is not None:
            fn_counter[0] = saved_counter
            
        return f"""
        <div class="parallel-row" {row_id}>
            <div class="he-cell">
                <span class="col2-variant variant-makbili">{repair_tags(clean_he)}</span>
                <span class="col2-variant variant-jrb">{repair_tags(jrb_text)}</span>
                <span class="col2-variant variant-tibon">{repair_tags(tibon_text)}</span>
                <span class="col2-variant variant-fr">{fr_processed}</span>
            </div>
            <div class="en-cell">
                <span class="col1-variant variant-en">{en_text}</span>
                <span class="col1-variant variant-fr">{fr_processed}</span>
            </div>
        </div>
        """


    # 4. Prepare Footnotes JSON & Chapter Index
    # Consolidate sub-footnotes (fn.X.sub_Y) into fn.X
    consolidated_footnotes = {}
    for key, text in english_footnotes.items():
        if ".sub_" in key:
            main_key = key.split(".sub_")[0]
            if main_key not in consolidated_footnotes:
                consolidated_footnotes[main_key] = ""
            # Append with a space if it's not the first part
            if consolidated_footnotes[main_key]:
                consolidated_footnotes[main_key] += " "
            consolidated_footnotes[main_key] += text
        else:
            consolidated_footnotes[key] = text
            
    footnotes_json = json.dumps(consolidated_footnotes)

    chapter_index_js = json.dumps([
        {"id": f"chapter-{ch['title'].replace(' ', '-').replace('/', '-')}", "title": ch['title']}
        for ch in unified_chapters
    ] + [{"id": "chapter-TOC", "title": "Contents"}])

    # 5. Generate Chapter Files
    accumulated_sections_html = ""
    
    # First, let's compile the landing grid HTML to place as the 'Contents' chapter section!
    landing_grid_html = ""
    landing_groups = { "Munk's Prefaces": [], "Munk's Endnotes": [], "Introductions": [], "Part 1": [], "Part 2": [], "Part 3": [] }
    for ch in unified_chapters:
        m = re.search(r"Part (\d)", ch["title"])
        if m: landing_groups[f"Part {m.group(1)}"].append(ch)
        elif ch["title"] in ["Introduction to Volume I", "Introduction to Volume II", "Introduction to Volume III", "Note On The Title"]:
            landing_groups["Munk's Prefaces"].append(ch)
        elif ch["title"] in ["Endnotes to Volume I", "Endnotes to Volume II", "Endnotes to Volume III"]:
            landing_groups["Munk's Endnotes"].append(ch)
        else:
            landing_groups["Introductions"].append(ch)
            
    for group_name, chapters in landing_groups.items():
        if not chapters: continue
        landing_grid_html += f'<div class="landing-section"><h3>{group_name}</h3><div class="landing-links">'
        for ch in chapters:
            display_name = ch["title"].replace("Part 1 - ", "").replace("Part 2 - ", "").replace("Part 3 - ", "")
            if display_name == "Letter to R Joseph son of Judah": display_name = "Letter to R. Joseph"
            landing_grid_html += f'<a href="javascript:void(0)" onclick="navigateToChapter(\'{ch["title"]}\')">{display_name}</a>'
        landing_grid_html += "</div></div>"

    toc_landing_page_html = f"""
    <div class="toc-landing-page">
        <h1 class="landing-title" style="font-size: 2.2rem; line-height: 1.2; margin-bottom: 20px;">
            AI-Assisted Translation of Salomon Munk's French Translation of the Guide to the Perplexed;<br>
            <span style="font-size: 1.5rem; opacity: 0.8;">Hebrew from Makbili Edition</span>
        </h1>
        
        <div style="text-align: center; margin-bottom: 40px; font-size: 0.9rem; color: var(--text-muted); line-height: 1.6;">
            Sources: 
            <a href="https://www.sefaria.org/Guide_for_the_Perplexed%2C_Letter_to_R_Joseph_son_of_Judah.2?ven=french|Guide_des_%C3%A9gar%C3%A9s,_trans._by_Salomon_Munk,_Paris,_1856_[fr]&amp;vhe=hebrew|Makbili_Edition,_Mif%27al_Mishneh_Torah,_2024&amp;lang=en&amp;with=Translations&amp;lang2=en" target="_blank" style="color: var(--accent);">Munk (French) via Sefaria</a> | 
            <a href="https://www.sefaria.org/Guide_for_the_Perplexed%2C_Letter_to_R_Joseph_son_of_Judah.2?vhe=hebrew|Makbili_Edition,_Mif%27al_Mishneh_Torah,_2024&amp;lang=he&amp;with=all&amp;lang2=en" target="_blank" style="color: var(--accent);">Makbili (Hebrew) via Sefaria</a>
            <br>
            <p style="max-width: 600px; margin: 10px auto; font-style: italic;">
                This digital edition is created for research and educational purposes. 
                The underlying source texts are utilized in accordance with their respective open licenses 
                and the principles of scholarly fair use.
            </p>
        </div>

        <div class="landing-grid">{landing_grid_html}</div>
    </div>
    """
    
    # Wrap the Contents landing page in the default visible chapter section
    accumulated_sections_html += f'<section class="chapter-section" id="chapter-Contents" data-title="Contents" style="display:block;">{toc_landing_page_html}</section>'
    
    # Now accumulate all individual unified_chapters
    for idx, ch in enumerate(unified_chapters):
        chapter_rows_html = f"<div class='chapter-header'><h2>{ch['title']}</h2></div>"
        
        is_asterisk = ch['title'] in ["Introduction to Volume I", "Introduction to Volume II", "Introduction to Volume III", "Note On The Title"]
        fn_counter = None if is_asterisk else [0]
        
        if "custom_segments" in ch:
            is_french_intro = ch.get("is_french_intro", False)
            for seg in ch['custom_segments']:
                en_processed = process_en(seg['en'], is_asterisk=is_asterisk, fn_counter=fn_counter)
                if seg.get("is_poem"):
                    en_processed = re.sub(r'</?i>', '', en_processed)
                    chapter_rows_html += f"""
                    <div class="parallel-row poem-row">
                        <div class="he-cell">{seg['he']}</div>
                        <div class="en-cell">{en_processed}</div>
                    </div>
                    """
                elif is_french_intro:
                    chapter_rows_html += f"""
                    <div class="parallel-row">
                        <div class="fr-cell">{process_en(seg['he'], is_asterisk=is_asterisk, fn_counter=fn_counter)}</div>
                        <div class="en-cell">{en_processed}</div>
                    </div>
                    """
                else:
                    chapter_rows_html += render_row(seg['he'], en_processed, key=None, is_asterisk=is_asterisk, fn_counter=fn_counter)
        else:
            for i, he_text in enumerate(ch['segments']):
                key = f"{ch['key_prefix']}.{i}"
                en_text = get_en_text(key, "[Translation Missing]")
                en_processed = process_en(en_text, is_asterisk=is_asterisk, fn_counter=fn_counter)
                chapter_rows_html += render_row(he_text, en_processed, key=key, is_asterisk=is_asterisk, fn_counter=fn_counter)
        
        # Add Navigation
        prev_ch = unified_chapters[idx-1] if idx > 0 else None
        next_ch = unified_chapters[idx+1] if idx < len(unified_chapters)-1 else None
        chapter_rows_html += generate_nav_links(prev_ch, next_ch)
        
        ch_id = 'chapter-' + ch['title'].replace(' ', '-').replace('/', '-').replace('.', '')
        accumulated_sections_html += f'<section class="chapter-section" id="{ch_id}" data-title="{ch["title"]}" style="display:none;">{chapter_rows_html}</section>'
        
    # Render final master HTML bundle
    master_html = render_html("The Guide for the Perplexed", accumulated_sections_html, chapter_index_js, footnotes_json)
    with open("Munk Viewer.html", "w", encoding="utf-8") as f:
        f.write(master_html)
        
    print("Success! Unified Single-Page Application bundle generated as 'Munk Viewer.html'.")

if __name__ == "__main__":
    build_viewer()
