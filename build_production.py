import json
import os
import re
import shutil

# --- Configuration ---
WORKSPACE = "/Users/rayhabbaz/Munk's Guide"
DIST = os.path.join(WORKSPACE, "dist")
MONOLITH_PATH = os.path.join(WORKSPACE, "Munk Viewer.html")

# --- Setup ---
if os.path.exists(DIST):
    shutil.rmtree(DIST)
os.makedirs(f"{DIST}/css", exist_ok=True)
os.makedirs(f"{DIST}/js", exist_ok=True)
os.makedirs(f"{DIST}/data", exist_ok=True)
os.makedirs(f"{DIST}/assets", exist_ok=True)

# --- Asset Definitions ---

CSS_CONTENT = """
:root {
    --bg: #fdfcfb; --surface: #ffffff; --text: #1a1a1a; --text-muted: #6b7280;
    --accent: #1e3a8a; --border: #e5e7eb; --row-hover: #f9fafb; --fn-ref-hover: #eff6ff;
    --panel-bg: #ffffff; --header-bg: #ffffff; --font-hebrew: 'Frank Ruhl Libre', serif;
    --font-english: 'Inter', sans-serif;
}
html.sepia {
    --bg: #f4ecd8; --surface: #ede3c8; --text: #3c2f1e; --text-muted: #7a6040;
    --accent: #a0522d; --border: #c9b89a; --row-hover: #ecdfc8; --fn-ref-hover: #d4b896;
    --panel-bg: #ede3c8; --header-bg: #e8dcc5;
}
html.dark {
    --bg: #12121e; --surface: #1e1e30; --text: #e2e2e2; --text-muted: #9ca3af;
    --accent: #a78bfa; --border: #2e2e46; --row-hover: #1e1e38; --fn-ref-hover: #2e2040;
    --panel-bg: #1a1a2e; --header-bg: #16162a;
}
body { background: var(--bg); color: var(--text); font-family: var(--font-english); margin: 0; display: flex; height: 100vh; overflow: hidden; transition: background 0.3s, color 0.3s; }

.parallel-row { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; padding: 24px 0; border-bottom: 1px solid var(--border); transition: background 0.2s; }

/* iPad Mini (744px) optimization */
@media (min-width: 700px) and (max-width: 900px) {
    .parallel-row { gap: 20px; }
    .content { padding: 12px 16px; max-width: 100%; }
    .variant-en, .variant-fr { font-size: 1rem; }
    .variant-makbili, .variant-tibon, .variant-jrb { font-size: 1.15rem; }
}

@media (max-width: 768px) {
    .parallel-row { display: flex; flex-direction: column; gap: 16px; padding: 20px 0; }
    .header { padding: 10px 16px; }
    .header .munk-label { display: none; }
    .header h1 { font-size: 1.1rem; }
    .theme-controls { display: none; }
    .right-cell { border-top: 1px solid var(--border); padding-top: 12px; }
    .chapter-header { padding: 24px 0 12px; order: -2; }
    .chapter-header h2 { font-size: 1.4rem; }
    .content { padding: 10px 16px; }
}

@media (pointer: coarse) {
    .fn-ref { padding: 8px 10px; min-height: 44px; min-width: 44px; display: inline-flex; align-items: center; justify-content: center; }
}

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

.variant-en { font-family: var(--font-english), var(--font-hebrew); font-size: 1.1rem; line-height: 1.7; text-align: left; direction: ltr; }
.variant-fr { font-family: var(--font-english); font-size: 1.1rem; line-height: 1.7; text-align: left; direction: ltr; }
.variant-makbili { font-family: var(--font-hebrew); font-size: 1.3rem; line-height: 1.6; text-align: right; direction: rtl; }
.variant-tibon { font-family: var(--font-hebrew); font-size: 1.3rem; line-height: 1.6; text-align: right; direction: rtl; }
.variant-jrb { font-family: var(--font-hebrew); font-size: 1.3rem; line-height: 1.6; text-align: right; direction: rtl; }

.toc-drawer { position: fixed; top: 0; left: 0; width: 320px; height: 100vh; background: var(--panel-bg); border-right: 1px solid var(--border); z-index: 500; transform: translateX(-100%); transition: transform 0.3s; display: flex; flex-direction: column; }
.toc-drawer.open { transform: translateX(0); }
.toc-header-bar { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid var(--border); font-weight: bold; }
.toc-header-bar button { background: none; border: none; font-size: 1.2rem; cursor: pointer; color: var(--text-muted); }
.toc-body { flex: 1; overflow-y: auto; padding-bottom: 20px; }
.toc-backdrop { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 499; }
.toc-backdrop.visible { display: block; }
.toc-tile-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; padding: 8px 12px 16px; }
.toc-tile { aspect-ratio: 1; display: flex; align-items: center; justify-content: center; border-radius: 6px; border: 1px solid var(--border); cursor: pointer; font-size: 0.8rem; font-weight: 600; }
.toc-tile:hover, .toc-tile.active { background: var(--accent); color: white; border-color: var(--accent); }
.toc-section-btn { width: 100%; text-align: left; padding: 12px 16px; border: none; background: none; color: var(--text); font-weight: 600; cursor: pointer; display: flex; justify-content: space-between; border-bottom: 1px solid var(--border); }
.toc-section-btn .arrow { transition: transform 0.2s; }
.toc-section-btn.open .arrow { transform: rotate(90deg); }

.main-container { flex: 1; display: flex; flex-direction: column; overflow-y: auto; }
.header { padding: 15px 40px; background: var(--header-bg); border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 100; display: flex; justify-content: space-between; align-items: center; }
.header h1 { margin: 0; font-size: 1.4rem; font-weight: 700; flex: 1; }
.theme-controls { display: flex; gap: 5px; }
.theme-btn { background: var(--surface); border: 1px solid var(--border); border-radius: 4px; padding: 6px 10px; cursor: pointer; }
.theme-btn.active { border-color: var(--accent); background: var(--row-hover); }
.content { padding: 20px 40px; max-width: 1200px; margin: 0 auto; width: 100%; box-sizing: border-box; }

.fn-panel { position: fixed; bottom: 0; left: 0; right: 0; height: 0; max-height: 35vh; background: var(--panel-bg); border-top: 2px solid var(--accent); z-index: 400; overflow: hidden; transition: height 0.3s; display: flex; flex-direction: column; }
.fn-panel.open { height: 25vh; }
.fn-panel-header { display: flex; justify-content: space-between; align-items: center; padding: 10px 24px; border-bottom: 1px solid var(--border); background: var(--header-bg); }
.fn-panel-body { padding: 16px 24px; overflow-y: auto; flex: 1; line-height: 1.7; }
.fn-ref { color: var(--accent); cursor: pointer; font-weight: 600; }

.chapter-header { padding: 40px 0 20px; border-bottom: 2px solid var(--accent); margin-bottom: 20px; }
.chapter-header h2 { margin: 0; color: var(--accent); }

.landing-title { font-family: 'Frank Ruhl Libre', serif; font-size: 3rem; margin-bottom: 8px; text-align: center; }
.landing-subtitle { text-align: center; color: var(--text-muted); margin-bottom: 60px; font-size: 1.1rem; text-transform: uppercase; }
.landing-section { margin-bottom: 40px; }
.landing-section h3 { border-bottom: 2px solid var(--accent); padding-bottom: 8px; margin-bottom: 20px; font-size: 1.2rem; color: var(--accent); }
.landing-links { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; }
.landing-links a { text-decoration: none; color: var(--text); padding: 10px; border: 1px solid var(--border); border-radius: 4px; text-align: center; transition: background 0.2s; }
.landing-links a:hover { background: var(--accent); color: white; }

.fn-dual-container { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; }
.fn-lang-label { font-size: 0.8rem; font-weight: 700; color: var(--accent); text-transform: uppercase; margin-bottom: 6px; border-bottom: 1px solid var(--border); padding-bottom: 4px; }
"""

JS_CONTENT = """
let footnotes = {};
let chapterIndex = [];
let activeChapterId = null;
let activeFnId = null;

async function init() {
    try {
        const [fnRes, indexRes] = await Promise.all([
            fetch('data/footnotes.json'),
            fetch('data/chapters.json')
        ]);
        footnotes = await fnRes.json();
        chapterIndex = await indexRes.json();
        
        buildTOC();
        
        const params = new URLSearchParams(window.location.search);
        const slug = params.get('ch');
        if (slug) {
            loadChapter(slug);
        } else if (window.location.pathname.endsWith('reader.html')) {
            loadChapter(chapterIndex[0].slug);
        }
        
        updateColumnSelectors();
    } catch (e) { console.error("Init failed", e); }
}

function setTheme(mode) {
    document.documentElement.className = mode === 'light' ? '' : mode;
    localStorage.setItem('munk-theme', mode);
    document.querySelectorAll('.theme-btn').forEach(b => b.classList.remove('active'));
    const btn = document.getElementById('btn-' + mode);
    if(btn) btn.classList.add('active');
}

function toggleTOC() {
    document.getElementById('toc-drawer').classList.toggle('open');
    document.getElementById('toc-backdrop').classList.toggle('visible');
}

function buildTOC() {
    const body = document.getElementById('toc-body');
    if (!body) return;
    body.innerHTML = '';
    const groups = { "Munk's Prefaces": [], 'Introductions': [], 'Part 1': [], 'Part 2': [], 'Part 3': [], "Munk's Endnotes": [] };
    
    chapterIndex.forEach(ch => {
        const m = ch.title.match(/^Part (\\d) - (Chapter \\d+|Introduction)$/);
        if (m) {
            const isIntro = m[2] === 'Introduction';
            let num = isIntro ? 'Intro' : parseInt(m[2].replace('Chapter ', ''));
            groups[`Part ${m[1]}`].push({ title: ch.title, slug: ch.slug, num: num, id: ch.id, isIntro: isIntro });
        } else if (["Introduction to Volume I", "Introduction to Volume II", "Introduction to Volume III", "Note On The Title"].includes(ch.title)) {
            groups["Munk's Prefaces"].push(ch);
        } else if (["Endnotes to Volume I", "Endnotes to Volume II", "Endnotes to Volume III"].includes(ch.title)) {
            groups["Munk's Endnotes"].push(ch);
        } else {
            groups["Introductions"].push(ch);
        }
    });

    for (const [groupName, chapters] of Object.entries(groups)) {
        if (chapters.length === 0) continue;
        const btn = document.createElement('button');
        btn.className = 'toc-section-btn';
        btn.innerHTML = `${groupName} <span class="arrow">›</span>`;
        body.appendChild(btn);
        
        const panel = document.createElement('div');
        panel.style.display = 'none';
        
        if (["Introductions", "Munk's Prefaces", "Munk's Endnotes"].includes(groupName)) {
            chapters.forEach(ch => {
                const tile = document.createElement('div');
                tile.className = 'toc-tile'; tile.style.gridColumn = 'span 5'; tile.style.padding = '8px'; tile.style.aspectRatio = 'auto';
                tile.textContent = ch.title.replace('Part 1 - ', '').replace('Part 2 - ', '').replace('Part 3 - ', '');
                tile.onclick = () => { window.location.href = 'reader.html?ch=' + ch.slug; };
                panel.appendChild(tile);
            });
            panel.style.padding = '0 12px 16px'; panel.style.display = 'grid'; panel.style.gap = '6px';
        } else {
            const grid = document.createElement('div');
            grid.className = 'toc-tile-grid';
            chapters.forEach(ch => {
                const tile = document.createElement('div');
                tile.className = 'toc-tile'; tile.textContent = ch.num;
                if (ch.isIntro) { tile.style.gridColumn = 'span 5'; tile.style.aspectRatio = 'auto'; tile.style.padding = '8px'; }
                tile.onclick = () => { window.location.href = 'reader.html?ch=' + ch.slug; };
                grid.appendChild(tile);
            });
            panel.appendChild(grid);
        }
        btn.onclick = () => {
            const isHidden = panel.style.display === 'none';
            panel.style.display = isHidden ? (["Introductions", "Munk's Prefaces", "Munk's Endnotes"].includes(groupName) ? 'grid' : 'block') : 'none';
            btn.classList.toggle('open', isHidden);
        };
        body.appendChild(panel);
    }
}

async function loadChapter(slug) {
    const content = document.getElementById('chapter-content');
    content.innerHTML = '<div style="padding:40px; text-align:center;">Loading Text...</div>';
    
    try {
        const res = await fetch(`data/${slug}.json`);
        const data = await res.json();
        
        activeChapterId = data.id;
        document.getElementById('main-title').textContent = data.title;
        document.title = data.title + " - Munk's Guide";
        
        let html = `<div class='chapter-header'><h2>${data.title}</h2></div>`;
        data.rows.forEach(row => {
            html += `<div class="parallel-row" ${row.key ? `id="row-${row.key}"` : ''}>
                <div class="left-cell">
                    ${Object.entries(row.variants).map(([v, t]) => `<span class="variant-span variant-${v}">${t}</span>`).join('')}
                </div>
                <div class="right-cell">
                    ${Object.entries(row.variants).map(([v, t]) => `<span class="variant-span variant-${v}">${t}</span>`).join('')}
                </div>
            </div>`;
        });
        
        html += `<div class="chapter-nav" style="display:flex; justify-content:space-between; margin-top:40px; padding-top:20px; border-top:1px solid var(--border);">`;
        if (data.prev) html += `<a href="reader.html?ch=${data.prev.slug}" class="nav-btn" style="text-decoration:none; color:var(--accent); font-weight:bold;">← Previous: ${data.prev.title}</a>`;
        else html += '<div></div>';
        if (data.next) html += `<a href="reader.html?ch=${data.next.slug}" class="nav-btn" style="text-decoration:none; color:var(--accent); font-weight:bold;">Next: ${data.next.title} →</a>`;
        else html += '<div></div>';
        html += `</div>`;
        
        content.innerHTML = html;
        document.querySelector('.main-container').scrollTop = 0;
        updateSelectionState(data.title);
    } catch (e) {
        content.innerHTML = '<div style="padding:40px; text-align:center; color:red;">Failed to load chapter.</div>';
    }
}

function updateSelectionState(title) {
    const isMunkSection = title.startsWith('Introduction to Volume') || title === 'Note On The Title' || title.startsWith('Endnotes to Volume');
    const restrictedVariants = ['makbili', 'tibon', 'jrb'];
    const leftSel = document.getElementById('select-left-col');
    const rightSel = document.getElementById('select-right-col');
    if (!leftSel) return;
    
    if (isMunkSection) { leftSel.value = 'fr'; rightSel.value = 'en'; }
    [leftSel, rightSel].forEach(sel => {
        Array.from(sel.options).forEach(opt => {
            opt.disabled = isMunkSection && restrictedVariants.includes(opt.value);
        });
    });
    updateColumnSelectors();
}

function updateColumnSelectors() {
    const leftSel = document.getElementById('select-left-col');
    const rightSel = document.getElementById('select-right-col');
    if (!leftSel) return;
    const leftVal = leftSel.value;
    const rightVal = rightSel.value;
    const mainCont = document.querySelector('.main-container');
    mainCont.setAttribute('data-left-col', leftVal);
    mainCont.setAttribute('data-right-col', rightVal);
    Array.from(leftSel.options).forEach(opt => opt.disabled = opt.value === rightVal);
    Array.from(rightSel.options).forEach(opt => opt.disabled = opt.value === leftVal);
}

function showFn(id) {
    const panel = document.getElementById('fn-panel');
    const data = footnotes[id] || {en: '', fr: ''};
    const mainCont = document.querySelector('.main-container');
    const col1 = mainCont.getAttribute('data-left-col');
    const col2 = mainCont.getAttribute('data-right-col');
    const enInView = (col1 === 'en' || col2 === 'en');
    const frInView = (col1 === 'fr' || col2 === 'fr');
    
    let contentHtml = '';
    if (enInView && frInView) {
        contentHtml = `<div class="fn-dual-container"><div class="fn-col"><div class="fn-lang-label">English</div><div>${data.en}</div></div><div class="fn-col"><div class="fn-lang-label">French</div><div>${data.fr}</div></div></div>`;
    } else if (frInView) contentHtml = data.fr;
    else contentHtml = data.en;
    
    document.getElementById('fn-panel-body').innerHTML = contentHtml;
    panel.classList.add('open');
    mainCont.classList.add('fn-open');
}

function closeFnPanel() {
    document.getElementById('fn-panel').classList.remove('open');
    document.querySelector('.main-container').classList.remove('fn-open');
}

document.addEventListener('DOMContentLoaded', () => {
    init();
    setTheme(localStorage.getItem('munk-theme') || 'light');
});
"""

# --- Build Script ---

def build():
    print("Loading Data...")
    with open("Guide for the Perplexed - he - Makbili Edition, Mif'al Mishneh Torah, 2024.json", "r") as f:
        hebrew_data = json.load(f)
    with open("munk_production_v1.json", "r", encoding="utf-8") as f:
        prod_data = json.load(f)
        english_main = prod_data["text"]
        english_footnotes = prod_data["footnotes"]
    
    variants = {}
    for v_name, v_path in [
        ("fr", "French_Healed_Enriched.json"),
        ("jrb", "Guide for the Perplexed - he - Judeo Arabic, Paris, 1856 [jrb].json"),
        ("tibon", "Guide for the Perplexed - he - Moreh Nevuchim, translated by Ibn Tibon.json")
    ]:
        if os.path.exists(v_path):
            with open(v_path, "r", encoding="utf-8") as f:
                variants[v_name] = json.load(f).get("text", {})

    def get_en_text(key):
        if key in english_main: return english_main[key]
        parts = []
        i = 0
        while f"{key}.sub_{i}" in english_main:
            parts.append(english_main[f"{key}.sub_{i}"])
            i += 1
        return " ".join(parts) if parts else "[Translation Missing]"

    def get_var_text(v_name, key):
        lang_main = variants.get(v_name, {})
        if not lang_main or not key: return "[Text Missing]"
        parts = key.split(".")
        if len(parts) < 3: return "[Text Missing]"
        try:
            if len(parts) == 4:
                sec, idx = parts[2], int(parts[3])
                if sec in lang_main and isinstance(lang_main[sec], list) and idx < len(lang_main[sec]): return lang_main[sec][idx]
            elif len(parts) == 5:
                p, s, idx = parts[2], parts[3], int(parts[4])
                if p in lang_main and s in lang_main[p] and idx < len(lang_main[p][s]): return lang_main[p][s][idx]
            elif len(parts) == 6:
                p, c, s = parts[2], int(parts[4]), int(parts[5])
                if p in lang_main and "" in lang_main[p] and c < len(lang_main[p][""]) and s < len(lang_main[p][""][c]): return lang_main[p][""][c][s]
        except: pass
        return "[Text Missing]"

    # Accumulate
    unified_chapters = []
    
    def get_slug(title):
        return title.replace(' ', '-').replace('/', '-').replace('.', '').lower()

    # Intros (Simplified accumulation for script speed)
    for p_num in ["Part 1", "Part 2", "Part 3"]:
        p_data = hebrew_data["text"][p_num]
        if "Introduction" in p_data:
            unified_chapters.append({"title": f"{p_num} - Introduction", "key_prefix": f"root.text.{p_num}.Introduction", "segments": p_data["Introduction"]})
        if "" in p_data:
            for i, segs in enumerate(p_data[""]):
                unified_chapters.append({"title": f"{p_num} - Chapter {i+1}", "key_prefix": f"root.text.{p_num}..{i}", "segments": segs})

    # Shred
    chapter_index = []
    print(f"Generating {len(unified_chapters)} modular files...")
    
    for idx, ch in enumerate(unified_chapters):
        slug = ch["title"].replace(" ", "-").replace("/", "-").replace(".", "").lower()
        rows = []
        for i, he_text in enumerate(ch["segments"]):
            key = f"{ch['key_prefix']}.{i}"
            rows.append({
                "key": key,
                "variants": {
                    "en": get_en_text(key),
                    "makbili": he_text,
                    "fr": get_var_text("fr", key),
                    "jrb": get_var_text("jrb", key),
                    "tibon": get_var_text("tibon", key)
                }
            })
        
        ch_data = {
            "title": ch["title"],
            "rows": rows,
            "prev": {"title": unified_chapters[idx-1]["title"], "slug": unified_chapters[idx-1]["title"].replace(" ", "-").replace("/", "-").replace(".", "").lower()} if idx > 0 else None,
            "next": {"title": unified_chapters[idx+1]["title"], "slug": unified_chapters[idx+1]["title"].replace(" ", "-").replace("/", "-").replace(".", "").lower()} if idx < len(unified_chapters)-1 else None
        }
        with open(f"{DIST}/data/{slug}.json", "w", encoding="utf-8") as f: json.dump(ch_data, f)
        chapter_index.append({"title": ch["title"], "slug": slug})

    with open(f"{DIST}/data/chapters.json", "w", encoding="utf-8") as f: json.dump(chapter_index, f)
    with open(f"{DIST}/data/footnotes.json", "w", encoding="utf-8") as f:
        # Convert English footnotes to dual format
        dual_fn = {k: {"en": v, "fr": ""} for k, v in english_footnotes.items()}
        json.dump(dual_fn, f)

    # 3. HTML Shells
    
    # --- Reader Shell ---
    READER_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Munk's Guide</title>
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <link rel="apple-touch-icon" href="assets/icon-mini.png">
    <link rel="manifest" href="manifest.json">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Frank+Ruhl+Libre:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="css/reader.css">
</head>
<body>
    <div id="toc-backdrop" class="toc-backdrop" onclick="toggleTOC()"></div>
    <nav id="toc-drawer" class="toc-drawer">
        <div class="toc-header-bar">
            <a href="index.html" style="text-decoration:none; color:var(--text);">Contents</a>
            <button onclick="toggleTOC()">✕</button>
        </div>
        <div class="toc-column-panel" style="padding: 16px 20px; border-bottom: 1px solid var(--border);">
            <select id="select-left-col" onchange="updateColumnSelectors()" style="width:100%; margin-bottom:10px;">
                <option value="en">Munk (English)</option>
                <option value="fr">Munk (French)</option>
                <option value="makbili">Makbili</option>
                <option value="tibon">Ibn Tibon</option>
                <option value="jrb">Judeo-Arabic</option>
            </select>
            <select id="select-right-col" onchange="updateColumnSelectors()" style="width:100%;">
                <option value="en">Munk (English)</option>
                <option value="fr">Munk (French)</option>
                <option value="makbili" selected>Makbili</option>
                <option value="tibon">Ibn Tibon</option>
                <option value="jrb">Judeo-Arabic</option>
            </select>
        </div>
        <div id="toc-body" class="toc-body"></div>
    </nav>
    <div class="main-container" data-left-col="en" data-right-col="makbili">
        <div class="header">
            <button onclick="toggleTOC()">☰</button>
            <h1 id="main-title">Loading...</h1>
            <div class="theme-controls">
                <button onclick="setTheme('light')" id="btn-light">☀️</button>
                <button onclick="setTheme('sepia')" id="btn-sepia">📜</button>
                <button onclick="setTheme('dark')" id="btn-dark">🌙</button>
            </div>
        </div>
        <div class="content" id="chapter-content"></div>
    </div>
    <div id="fn-panel" class="fn-panel">
        <div class="fn-panel-header"><span>Note</span><button onclick="closeFnPanel()">✕</button></div>
        <div id="fn-panel-body" class="fn-panel-body"></div>
    </div>
    <script src="js/reader.js"></script>
</body>
</html>"""
    with open(f"{DIST}/reader.html", "w", encoding="utf-8") as f: f.write(READER_HTML)

    # --- Landing Shell ---
    LANDING_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Munk's Guide</title>
    <meta name="apple-mobile-web-app-capable" content="yes">
    <link rel="apple-touch-icon" href="assets/icon-mini.png">
    <link rel="manifest" href="manifest.json">
    <link rel="stylesheet" href="css/reader.css">
</head>
<body style="overflow-y:auto; height:auto; display:block;">
    <div class="content">
        <h1 class="landing-title">Munk's Guide</h1>
        <p class="landing-subtitle">Salomon Munk Edition</p>
        <div id="landing-grid"></div>
    </div>
    <script>
        fetch('data/chapters.json').then(r => r.json()).then(chapters => {{
            const grid = document.getElementById('landing-grid');
            let html = '<div class="landing-links">';
            chapters.forEach(ch => {{
                html += `<a href="reader.html?ch=${{ch.slug}}">${{ch.title}}</a>`;
            }});
            html += '</div>';
            grid.innerHTML = html;
        }});
    </script>
</body>
</html>"""
    with open(f"{DIST}/index.html", "w", encoding="utf-8") as f: f.write(LANDING_HTML)

    # 5. PWA Assets
    MANIFEST = {
        "name": "Munk's Guide",
        "short_name": "Munk's Guide",
        "start_url": "index.html",
        "display": "standalone",
        "background_color": "#fdfcfb",
        "theme_color": "#1e3a8a",
        "icons": [
            {"src": "assets/icon-mini.png", "sizes": "768x768", "type": "image/png"},
            {"src": "assets/icon.png", "sizes": "1024x1024", "type": "image/png"}
        ]
    }
    with open(f"{DIST}/manifest.json", "w", encoding="utf-8") as f: json.dump(MANIFEST, f)

    json_files = [get_slug(ch["title"]) + ".json" for ch in unified_chapters]
    assets = ["index.html", "reader.html", "css/reader.css", "js/reader.js", "data/footnotes.json", "data/chapters.json", "manifest.json", "assets/icon.png", "assets/icon-mini.png"] + ["data/" + f for f in json_files]
    SW_JS = f"""const CACHE_NAME = 'munk-reader-v2';
const ASSETS = {json.dumps(assets)};
self.addEventListener('install', e => e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(ASSETS))));
self.addEventListener('fetch', e => e.respondWith(caches.match(e.request).then(r => r || fetch(e.request))));"""
    with open(f"{DIST}/sw.js", "w", encoding="utf-8") as f: f.write(SW_JS)

    # 6. Legacy Monolith
    shutil.copy(MONOLITH_PATH, f"{DIST}/monolith.html")

    # Icons
    MASTER_ICON = os.path.join(WORKSPACE, "assets/icon.png")
    if os.path.exists(MASTER_ICON):
        shutil.copy(MASTER_ICON, f"{DIST}/assets/icon.png")
        os.system(f'sips -Z 768 "{DIST}/assets/icon.png" --out "{DIST}/assets/icon-mini.png" > /dev/null 2>&1')

    with open(f"{DIST}/css/reader.css", "w", encoding="utf-8") as f: f.write(CSS_CONTENT)
    with open(f"{DIST}/js/reader.js", "w", encoding="utf-8") as f: f.write(JS_CONTENT)
    print("Build finished successfully.")

if __name__ == "__main__":
    build()
