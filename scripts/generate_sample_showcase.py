"""
scripts/generate_sample_showcase.py
Generates a 100% self-contained, offline-compatible HTML showcase:
`Homo_Mysticus_Sample_Chapters.html`.
"""

import json
from pathlib import Path
import re

BASE_DIR = Path("/Users/rayhabbaz/Munk's Guide")

SAMPLE_SLUGS = [
    'part-1---chapter-5',
    'part-1---chapter-71',
    'part-1---chapter-1',
    'part-1---chapter-58',
    'part-3---chapter-51'
]

SAMPLE_TITLES = {
    'part-1---chapter-5': 'Guide I:5 (Rayyis / Gloss)',
    'part-1---chapter-71': 'Guide I:71 (Kalam Exegesis)',
    'part-1---chapter-1': 'Guide I:1 (Image & Likeness)',
    'part-1---chapter-58': 'Guide I:58 (Negative Attributes)',
    'part-3---chapter-51': 'Guide III:51 (The Palace Parable)'
}

print("Loading chapters...")
embedded_chapters = {}
for slug in SAMPLE_SLUGS:
    path = BASE_DIR / f"data/{slug}.json"
    with open(path, encoding='utf-8') as f:
        embedded_chapters[slug] = json.load(f)

print("Loading Faur commentary map...")
with open(BASE_DIR / "data/faur_commentary_map.json", encoding='utf-8') as f:
    full_faur = json.load(f)

embedded_faur = {
    'metadata': full_faur.get('metadata', {}),
    'chapters': {s: full_faur['chapters'][s] for s in SAMPLE_SLUGS if s in full_faur['chapters']},
    'tier2_by_row_key': {},
    'section_6_footnotes': full_faur.get('section_6_footnotes', {})
}

for row_key, entries in full_faur.get('tier2_by_row_key', {}).items():
    if any(e.get('slug') in SAMPLE_SLUGS for e in entries):
        embedded_faur['tier2_by_row_key'][row_key] = entries

print("Loading footnotes...")
with open(BASE_DIR / "data/qafih_footnotes.json", encoding='utf-8') as f:
    qafih_all = json.load(f)

with open(BASE_DIR / "data/footnotes.json", encoding='utf-8') as f:
    munk_all = json.load(f)

embedded_qafih = {}
embedded_munk = {}

for slug, ch_data in embedded_chapters.items():
    for row in ch_data.get('rows', []):
        for txt in row.get('variants', {}).values():
            for m in re.finditer(r'\[\[fn:([^|\]]+)', txt):
                fn_tok = m.group(1)
                for k in [fn_tok, 'fn.' + fn_tok, 'fn:' + fn_tok]:
                    if k in qafih_all:
                        embedded_qafih[k] = qafih_all[k]
                        embedded_qafih['fn.' + fn_tok] = qafih_all[k]
                for k in [fn_tok, 'fn.' + fn_tok, fn_tok.replace('fn.', '')]:
                    if k in munk_all:
                        embedded_munk[k] = munk_all[k]

print(f"Extracted {len(embedded_qafih)} Qafih notes and {len(embedded_munk)} Munk notes.")

css_text = (BASE_DIR / "css/reader.css").read_text(encoding='utf-8')
reader_html = (BASE_DIR / "reader.html").read_text(encoding='utf-8')
js_text = (BASE_DIR / "js/reader.js").read_text(encoding='utf-8')
# Patch init() to automatically load first sample chapter if no slug given, and route links locally
js_text = js_text.replace(
    "else if (window.location.pathname.endsWith('reader.html')) loadChapter(chapterIndex[0].slug);",
    "else loadChapter('part-1---chapter-5');"
).replace(
    "reader.html?ch=",
    "Homo_Mysticus_Sample_Chapters.html?ch="
)

showcase_css = """
/* Sample Showcase Navigation Bar */
body {
    flex-direction: column !important;
}
.sample-showcase-bar {
    position: sticky;
    top: 0;
    z-index: 1000;
    background: var(--header-bg, #ffffff);
    border-bottom: 2px solid var(--accent, #b45309);
    padding: 8px 16px;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    flex-shrink: 0;
}
.sample-showcase-label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 700;
    font-size: 0.95rem;
    color: var(--accent, #b45309);
    font-family: var(--font-english, 'Cinzel', serif);
}
.sample-showcase-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.sample-pill-btn {
    min-height: 44px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    box-sizing: border-box;
    background: var(--bg-secondary, #f8f6f0);
    border: 1px solid var(--border, #d1d5db);
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    color: var(--text, #1f2937);
    transition: all 0.2s ease;
}
.sample-pill-btn:hover {
    border-color: var(--accent, #b45309);
    color: var(--accent, #b45309);
    transform: translateY(-1px);
}
.sample-pill-btn.active {
    background: var(--accent, #b45309);
    color: #ffffff;
    border-color: var(--accent, #b45309);
    box-shadow: 0 2px 4px rgba(180, 83, 9, 0.3);
}
@media (max-width: 768px) {
    .sample-showcase-bar {
        padding: 6px 12px;
        gap: 8px;
    }
    .sample-showcase-pills {
        flex-wrap: nowrap;
        overflow-x: auto;
        max-width: 100%;
        -webkit-overflow-scrolling: touch;
        padding-bottom: 4px;
    }
    .sample-pill-btn {
        flex-shrink: 0;
        white-space: nowrap;
    }
}
.showcase-banner {
    background: var(--bg-secondary, #faf7f2);
    border-left: 4px solid var(--accent, #b45309);
    padding: 12px 18px;
    margin: 16px 0;
    border-radius: 0 8px 8px 0;
    font-size: 0.9rem;
    line-height: 1.5;
}
.showcase-banner h4 {
    margin: 0 0 6px 0;
    color: var(--accent, #b45309);
    font-size: 1rem;
}
"""

combined_css = css_text + "\n\n" + showcase_css

pills_html = "\n".join([
    f'<button class="sample-pill-btn{" active" if s == "part-1---chapter-5" else ""}" data-slug="{s}" onclick="switchSampleChapter(\'{s}\')">{SAMPLE_TITLES[s]}</button>'
    for s in SAMPLE_SLUGS
])

showcase_bar_html = f"""
<div class="sample-showcase-bar">
    <div class="sample-showcase-label">
        <span>❦</span>
        <span>Homo Mysticus Showcase</span>
    </div>
    <div class="sample-showcase-pills">
        {pills_html}
    </div>
</div>
"""

body_match = re.search(r'<body[^>]*>([\s\S]*?)</body>', reader_html)
if not body_match:
    raise RuntimeError("Could not find <body> in reader.html")
body_inner = body_match.group(1)

body_inner = re.sub(r'<script\b[^>]*>[\s\S]*?</script>', '', body_inner)
body_inner = re.sub(r'<link\b[^>]*rel=["\']stylesheet["\'][^>]*>', '', body_inner)

# Template for JS preamble (using pure template replacement to prevent f-string corruption)
js_preamble_template = """
// Embedded Data Store for 100% Offline / file:// Execution
const EMBEDDED_CHAPTERS = __EMBEDDED_CHAPTERS__;
const EMBEDDED_FAUR = __EMBEDDED_FAUR__;
const EMBEDDED_QAFIH = __EMBEDDED_QAFIH__;
const EMBEDDED_MUNK = __EMBEDDED_MUNK__;

// Pre-seed global cached objects
window.faurCommentary = EMBEDDED_FAUR;
window.qafihFootnotes = EMBEDDED_QAFIH;
window.footnotes = EMBEDDED_MUNK;

// Override global fetch to serve embedded data synchronously/locally
const originalFetch = window.fetch;
const localFetch = async function(url, options) {
    const cleanUrl = String(url).split('?')[0];
    if (cleanUrl === 'data/faur_commentary_map.json' || cleanUrl.endsWith('faur_commentary_map.json')) {
        return { ok: true, status: 200, json: async () => EMBEDDED_FAUR };
    }
    if (cleanUrl === 'data/qafih_footnotes.json' || cleanUrl.endsWith('qafih_footnotes.json')) {
        return { ok: true, status: 200, json: async () => EMBEDDED_QAFIH };
    }
    if (cleanUrl === 'data/footnotes.json' || cleanUrl.endsWith('footnotes.json')) {
        return { ok: true, status: 200, json: async () => EMBEDDED_MUNK };
    }
    if (cleanUrl === 'data/chapters.json' || cleanUrl.endsWith('chapters.json')) {
        const sampleList = [
            { "slug": "part-1---chapter-5", "title": "Part 1, Chapter 5", "part": 1, "chapter": 5, "category": "Part 1" },
            { "slug": "part-1---chapter-71", "title": "Part 1, Chapter 71", "part": 1, "chapter": 71, "category": "Part 1" },
            { "slug": "part-1---chapter-1", "title": "Part 1, Chapter 1", "part": 1, "chapter": 1, "category": "Part 1" },
            { "slug": "part-1---chapter-58", "title": "Part 1, Chapter 58", "part": 1, "chapter": 58, "category": "Part 1" },
            { "slug": "part-3---chapter-51", "title": "Part 3, Chapter 51", "part": 3, "chapter": 51, "category": "Part 3" }
        ];
        return { ok: true, status: 200, json: async () => sampleList };
    }
    for (const slug of Object.keys(EMBEDDED_CHAPTERS)) {
        if (cleanUrl.endsWith(slug + '.json')) {
            return { ok: true, status: 200, json: async () => EMBEDDED_CHAPTERS[slug] };
        }
    }
    console.warn('Unhandled fetch in offline mode:', url);
    return { ok: false, status: 404, json: async () => ({}) };
};

window.fetch = localFetch;
if (typeof globalThis !== 'undefined') {
    globalThis.fetch = localFetch;
}

// Interactive Chapter Switcher for Showcase
window.switchSampleChapter = async function(slug) {
    document.querySelectorAll('.sample-pill-btn').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-slug') === slug);
    });
    try {
        history.replaceState(null, '', `?ch=${slug}`);
    } catch (e) {}
    await loadChapter(slug);
    const mainCont = document.querySelector('.main-container');
    if (mainCont) mainCont.scrollTop = 0;
};
"""

js_preamble = js_preamble_template.replace(
    '__EMBEDDED_CHAPTERS__', json.dumps(embedded_chapters, ensure_ascii=False)
).replace(
    '__EMBEDDED_FAUR__', json.dumps(embedded_faur, ensure_ascii=False)
).replace(
    '__EMBEDDED_QAFIH__', json.dumps(embedded_qafih, ensure_ascii=False)
).replace(
    '__EMBEDDED_MUNK__', json.dumps(embedded_munk, ensure_ascii=False)
)

final_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>Salomon Munk's Guide for the Perplexed — José Faur Scholarly Integration</title>
    <style>
{combined_css}
    </style>
</head>
<body>
{showcase_bar_html}
{body_inner}
<script>
{js_preamble}
{js_text}

// Sync active pill button on DOM load
document.addEventListener('DOMContentLoaded', () => {{
    const params = new URLSearchParams(window.location.search);
    const initialSlug = params.get('ch') || 'part-1---chapter-5';
    document.querySelectorAll('.sample-pill-btn').forEach(btn => {{
        btn.classList.toggle('active', btn.getAttribute('data-slug') === initialSlug);
    }});
}});
</script>
</body>
</html>
"""

output_path = BASE_DIR / "Homo_Mysticus_Sample_Chapters.html"
with open(output_path, "w", encoding='utf-8') as f:
    f.write(final_html)

print(f"Generated standalone showcase: {output_path} ({len(final_html):,} bytes)")
