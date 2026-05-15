import json
import os
import shutil
import re

# --- Configuration ---
WORKSPACE = "/Users/rayhabbaz/Munk's Guide"
DIST = os.path.join(WORKSPACE, "dist")

# --- Setup ---
if os.path.exists(DIST): shutil.rmtree(DIST)
os.makedirs(f"{DIST}/css", exist_ok=True)
os.makedirs(f"{DIST}/js", exist_ok=True)
os.makedirs(f"{DIST}/data", exist_ok=True)
os.makedirs(f"{DIST}/assets", exist_ok=True)

# --- Asset Definitions ---

CSS_CONTENT = r"""
/* === Faithful port from Munk Viewer.html === */
:root {
    --bg: #fdfcfb; --surface: #ffffff; --text: #1a1a1a; --text-muted: #6b7280;
    --accent: #1e3a8a; --border: #e5e7eb; --row-hover: #f9fafb; --fn-ref-hover: #eff6ff;
    --panel-bg: #ffffff; --header-bg: #ffffff;
    --font-hebrew: 'Frank Ruhl Libre', serif;
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
.variant-makbili { font-family: var(--font-hebrew); font-size: 1.3rem; line-height: 1.6; text-align: right; direction: rtl; color: var(--text); }
.variant-tibon { font-family: var(--font-hebrew); font-size: 1.3rem; line-height: 1.6; text-align: right; direction: rtl; color: var(--text); }
.variant-jrb { font-family: var(--font-hebrew); font-size: 1.3rem; line-height: 1.6; text-align: right; direction: rtl; color: var(--text); }
.left-cell, .right-cell { width: 100%; box-sizing: border-box; }
.toc-drawer { position: fixed; top: 0; left: 0; width: 320px; height: 100vh; background: var(--panel-bg); border-right: 1px solid var(--border); z-index: 500; transform: translateX(-100%); transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1); display: flex; flex-direction: column; box-shadow: 4px 0 20px rgba(0,0,0,0.15); }
.toc-drawer.open { transform: translateX(0); }
.toc-header-bar { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid var(--border); font-weight: bold; color: var(--text); }
.toc-header-bar button { background: none; border: none; font-size: 1.2rem; cursor: pointer; color: var(--text-muted); }
.mobile-theme-panel { display: none; }
@media (max-width: 768px) { .mobile-theme-panel { display: flex; justify-content: space-around; padding: 16px; background: var(--header-bg); border-bottom: 1px solid var(--border); } }
.toc-body { flex: 1; overflow-y: auto; padding-bottom: 20px; }
.toc-backdrop { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 499; }
.toc-backdrop.visible { display: block; }
.toc-tile-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; padding: 8px 12px 16px; }
.toc-tile { aspect-ratio: 1; display: flex; align-items: center; justify-content: center; border-radius: 6px; border: 1px solid var(--border); cursor: pointer; font-size: 0.8rem; font-weight: 600; transition: background 0.15s, color 0.15s; color: var(--text); background: var(--surface); }
.toc-tile:hover, .toc-tile.active { background: var(--accent); color: white; border-color: var(--accent); }
.toc-section-btn { width: 100%; text-align: left; padding: 12px 16px; border: none; background: none; color: var(--text); font-weight: 600; font-size: 0.9rem; cursor: pointer; display: flex; justify-content: space-between; border-bottom: 1px solid var(--border); }
.toc-section-btn .arrow { transition: transform 0.2s; }
.toc-section-btn.open .arrow { transform: rotate(90deg); }
.main-container { flex: 1; display: flex; flex-direction: column; overflow-y: auto; transition: padding-bottom 0.3s; }
.main-container.fn-open { padding-bottom: 25vh; }
.header { padding: 15px 40px; background: var(--header-bg); border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 100; display: flex; justify-content: space-between; align-items: center; transition: background 0.3s, border-color 0.3s; }
.header-left { display: flex; align-items: center; gap: 20px; flex: 1; }
#hamburger-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: var(--text); padding: 5px; }
.header h1 { margin: 0; font-size: 1.4rem; color: var(--text); font-weight: 700; flex: 1; }
.header .munk-label { color: var(--text-muted); font-size: 0.8rem; margin-right: 20px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.theme-controls { display: flex; gap: 5px; }
.theme-btn { background: var(--surface); border: 1px solid var(--border); border-radius: 4px; padding: 6px 10px; cursor: pointer; font-size: 1rem; color: var(--text); }
.theme-btn.active { border-color: var(--accent); background: var(--row-hover); }
.content { padding: 20px 40px; max-width: 1200px; margin: 0 auto; width: 100%; box-sizing: border-box; }
.parallel-row { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; padding: 24px 0; border-bottom: 1px solid var(--border); transition: background 0.2s; }
.parallel-row:hover { background: var(--row-hover); }

/* Single Column Mode */
.main-container[data-right-col="none"] .parallel-row { grid-template-columns: 1fr; }
.main-container[data-right-col="none"] .right-cell { display: none; }

/* Vertical Stacking Mode */
.main-container[data-layout-mode="vertical"] .parallel-row { display: flex; flex-direction: column; gap: 24px; }
.left-cell { order: var(--left-order, 1); }
.right-cell { order: var(--right-order, 2); }
.main-container[data-layout-mode="vertical"] .right-cell { border-top: 1px solid var(--border); padding-top: 16px; }
.chapter-header { grid-column: span 2; padding: 40px 0 20px; border-bottom: 2px solid var(--accent); margin-bottom: 20px; }
.chapter-header h2 { margin: 0; color: var(--accent); font-weight: 700; }
.poem-segment { color: var(--text-muted); font-size: 0.95rem; font-style: italic; }
.header-row { border-bottom: none; padding-bottom: 0; padding-top: 32px; }
.header-row .he-cell, .header-row .right-cell { border-bottom: 2px solid var(--accent); display: inline-block; width: auto; padding-bottom: 4px; }
.chapter-thematic-title { display: block; color: var(--accent); font-size: 1.2rem; font-weight: 700; margin-bottom: 12px; margin-top: 4px; width: 100%; }
.mediumGrey { display: block; color: #6b7280; font-size: 1.15rem; font-weight: 700; border-bottom: 2px solid var(--accent); padding-bottom: 6px; margin-bottom: 16px; margin-top: 12px; width: 100%; }
.variant-makbili b, .variant-makbili strong { color: #6b7280; }
.variant-en b, .variant-en strong { color: #6b7280; }
.fn-lang-label { display: none !important; }
@media (max-width: 768px) {
    .header { padding: 10px 16px; }
    .header .munk-label { display: none; }
    .header h1 { font-size: 1.1rem; }
    .theme-controls { display: none; }
    .parallel-row { display: flex; flex-direction: column; gap: 16px; padding: 20px 0; }
    .left-cell { order: var(--left-order, 1); }
    .right-cell { order: var(--right-order, 2); border-top: 1px solid var(--border); padding-top: 12px; }
    .chapter-header { padding: 24px 0 12px; order: -2; }
    .chapter-header h2 { font-size: 1.4rem; }
    .content { padding: 10px 16px; }
}
.toc-landing-page { padding: 40px 0; max-width: 900px; margin: 0 auto; }
.landing-title { font-family: var(--font-hebrew); font-size: 3rem; margin-bottom: 8px; color: var(--text); text-align: center; }
.landing-subtitle { text-align: center; color: var(--text-muted); margin-bottom: 60px; font-size: 1.1rem; letter-spacing: 0.1em; text-transform: uppercase; }
.landing-section { margin-bottom: 40px; }
.landing-section h3 { border-bottom: 2px solid var(--accent); padding-bottom: 8px; margin-bottom: 20px; font-size: 1.2rem; color: var(--accent); }
.landing-links { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; }
.landing-links a { color: var(--text); text-decoration: none; padding: 8px 12px; border-radius: 4px; background: var(--surface); border: 1px solid var(--border); font-size: 0.9rem; transition: all 0.2s; display: block; text-align: center; }
.landing-links a:hover { background: var(--accent); color: white; border-color: var(--accent); }
.fn-panel { position: fixed; bottom: 0; left: 0; right: 0; height: 0; max-height: 45vh; background: var(--panel-bg); border-top: 1px solid var(--accent); z-index: 400; overflow: hidden; transition: height 0.3s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 -4px 25px rgba(0,0,0,0.15); display: flex; flex-direction: column; border-radius: 16px 16px 0 0; }
.fn-panel.open { height: 35vh; }
.fn-handle { width: 36px; height: 4px; background: var(--border); border-radius: 2px; margin: 8px auto 0; flex-shrink: 0; }
.fn-panel-header { display: flex; justify-content: space-between; align-items: center; padding: 10px 24px; border-bottom: 1px solid var(--border); background: var(--header-bg); flex-shrink: 0; }
.fn-panel-label { font-weight: 700; color: var(--accent); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em; }
.fn-panel-close { background: none; border: 1px solid var(--border); border-radius: 6px; padding: 4px 12px; cursor: pointer; color: var(--text-muted); font-size: 0.8rem; transition: all 0.2s; }
.fn-panel-close:hover { background: var(--accent); color: white; border-color: var(--accent); }
.fn-panel-body { font-family: var(--font-english), var(--font-hebrew); padding: 16px 24px; overflow-y: auto; flex: 1; font-size: 1rem; line-height: 1.7; color: var(--text); }
.fn-ref { color: var(--accent); cursor: pointer; font-weight: 600; transition: background 0.15s; padding: 0 2px; border-radius: 2px; }
.fn-ref:hover { background: var(--fn-ref-hover); }
.fn-dual-container { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; }
.fn-col { display: flex; flex-direction: column; }
.fn-lang-label { font-size: 0.8rem; font-weight: 700; color: var(--accent); text-transform: uppercase; margin-bottom: 6px; border-bottom: 1px solid var(--border); padding-bottom: 4px; display: block !important; }
@media (max-width: 640px) {
    .fn-dual-container { display: flex; flex-direction: column; gap: 16px; }
}
.feedback-footer { margin-top: 60px; padding-top: 24px; border-top: 1px solid var(--border); text-align: center; }
.feedback-footer a { display: inline-block; padding: 10px 20px; font-size: 0.95rem; font-weight: 600; color: var(--text-muted); background: var(--surface); border: 1px solid var(--border); border-radius: 6px; text-decoration: none; transition: all 0.2s; }
.feedback-footer a:hover { background: var(--accent); color: white; border-color: var(--accent); }
.chapter-nav-link { text-decoration: none; color: var(--accent); font-weight: bold; }
"""


JS_CONTENT = r"""
let footnotes = {};
let chapterIndex = [];

async function init() {
    try {
        const [fnRes, indexRes] = await Promise.all([fetch('data/footnotes.json'), fetch('data/chapters.json')]);
        footnotes = await fnRes.json();
        chapterIndex = await indexRes.json();
        buildTOC();
        const params = new URLSearchParams(window.location.search);
        const slug = params.get('ch');
        if (slug) loadChapter(slug);
        else if (window.location.pathname.endsWith('reader.html')) loadChapter(chapterIndex[0].slug);
        updateColumnSelectors();
    } catch (e) { console.error("Init failed", e); }
}

function setTheme(mode) {
    document.documentElement.className = mode === 'light' ? '' : mode;
    localStorage.setItem('munk-theme', mode);
    document.querySelectorAll('.theme-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('btn-' + mode)?.classList.add('active');
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
    chapterIndex.forEach(ch => { if (groups[ch.category]) groups[ch.category].push(ch); });
    for (const [groupName, chapters] of Object.entries(groups)) {
        if (chapters.length === 0) continue;
        const btn = document.createElement('button');
        btn.className = 'toc-section-btn';
        btn.innerHTML = `${groupName} <span class="arrow">›</span>`;
        body.appendChild(btn);
        const panel = document.createElement('div');
        panel.style.display = 'none';
        const isGrid = groupName.startsWith("Part");
        if (!isGrid) {
            chapters.forEach(ch => {
                const tile = document.createElement('div');
                tile.className = 'toc-tile'; tile.style.gridColumn = 'span 5'; tile.style.padding = '12px 20px'; tile.style.aspectRatio = 'auto';
                tile.textContent = ch.title.replace('Part 1 - ', '').replace('Part 2 - ', '').replace('Part 3 - ', '');
                tile.onclick = () => { window.location.href = 'reader.html?ch=' + ch.slug; };
                panel.appendChild(tile);
            });
            panel.style.padding = '8px 32px 24px'; panel.style.display = 'grid'; panel.style.gap = '8px';
        } else {
            const grid = document.createElement('div'); grid.className = 'toc-tile-grid';
            chapters.forEach(ch => {
                const tile = document.createElement('div'); tile.className = 'toc-tile'; 
                let num = ch.title.match(/Chapter (\d+)/) ? ch.title.match(/Chapter (\d+)/)[1] : "Intro";
                tile.textContent = num;
                if (num === "Intro") { tile.style.gridColumn = 'span 5'; tile.style.aspectRatio = 'auto'; tile.style.padding = '12px'; }
                tile.onclick = () => { window.location.href = 'reader.html?ch=' + ch.slug; };
                grid.appendChild(tile);
            });
            panel.appendChild(grid);
        }
        btn.onclick = () => {
            const isHidden = panel.style.display === 'none';
            panel.style.display = isHidden ? (isGrid ? 'block' : 'grid') : 'none';
            btn.classList.toggle('open', isHidden);
        };
        body.appendChild(panel);
    }
}

function showFn(id) {
    const panel = document.getElementById('fn-panel');
    const data = footnotes[id] || {en: 'Note content missing.', fr: ''};
    const mainCont = document.querySelector('.main-container');
    const col1 = mainCont.getAttribute('data-left-col');
    const col2 = mainCont.getAttribute('data-right-col');
    const isComparingEnglishFrench = (
        (col1 === 'en' && col2 === 'fr') || 
        (col1 === 'fr' && col2 === 'en')
    );
    
    let contentHtml = '';
    const rawEn = data.en;
    const rawFr = data.fr;
    
    if (rawEn && rawFr && isComparingEnglishFrench) {
        contentHtml = `<div class="fn-dual-container">
            <div class="fn-col"><span class="fn-lang-label">English</span><div>${rawEn}</div></div>
            <div class="fn-col"><span class="fn-lang-label">French</span><div>${rawFr}</div></div>
        </div>`;
    } else if (rawEn && (col1 === 'en' || col2 === 'en')) {
        contentHtml = `<div>${rawEn}</div>`;
    } else if (rawFr && (col1 === 'fr' || col2 === 'fr')) {
        contentHtml = `<div>${rawFr}</div>`;
    } else {
        contentHtml = `<div>${rawEn || rawFr || 'Note missing.'}</div>`;
    }
    
    contentHtml = contentHtml.replace(/\[\[fn:(\d+)(?:\|([^\]]+))?\]\]/g, (m, n, label) => `<sup class="fn-ref" onclick="showFn('fn.${n}')" style="cursor:pointer;">${label || '*'}</sup>`);
    
    document.getElementById('fn-panel-body').innerHTML = contentHtml;
    panel.classList.add('open');
    mainCont.classList.add('fn-open');
}

function closeFnPanel() {
    document.getElementById('fn-panel').classList.remove('open');
    document.querySelector('.main-container').classList.remove('fn-open');
}

async function loadChapter(slug) {
    const content = document.getElementById('chapter-content');
    content.innerHTML = '<div style="padding:150px; text-align:center; font-style:italic; opacity:0.4;">Retrieving Manuscript...</div>';
    try {
        const res = await fetch(`data/${slug}.json`);
        const data = await res.json();
        document.getElementById('main-title').textContent = data.title;
        document.title = data.title + " - Munk's Guide";
        let html = `<div class="chapter-header"><h2>${data.title}</h2></div>`;
        data.rows.forEach(row => {
            html += `<div class="parallel-row" ${row.key ? `id="row-${row.key}"` : ''}>
                <div class="left-cell">
                    ${Object.entries(row.variants).map(([v, t]) => {
                        let processed = t.replace(/\[\[fn:(\d+)(?:\|([^\]]+))?\]\]/g, (match, n, label) => `<sup class="fn-ref" onclick="showFn('fn.${n}')">${label || '*'}</sup>`);
                        return `<span class="variant-span variant-${v}">${processed}</span>`;
                    }).join('')}
                </div>
                <div class="right-cell">
                    ${Object.entries(row.variants).map(([v, t]) => {
                        let processed = t.replace(/\[\[fn:(\d+)(?:\|([^\]]+))?\]\]/g, (match, n, label) => `<sup class="fn-ref" onclick="showFn('fn.${n}')">${label || '*'}</sup>`);
                        return `<span class="variant-span variant-${v}">${processed}</span>`;
                    }).join('')}
                </div>
            </div>`;
        });
        html += `<div class="chapter-nav" style="display:flex; justify-content:space-between; margin-top:40px; padding-top:20px; border-top:1px solid var(--border);">`;
        if (data.prev) html += `<a href="reader.html?ch=${data.prev.slug}" class="chapter-nav-link">← ${data.prev.title}</a>`;
        else html += '<div></div>';
        if (data.next) html += `<a href="reader.html?ch=${data.next.slug}" class="chapter-nav-link">${data.next.title} →</a>`;
        else html += '<div></div>';
        html += `</div>`;
        content.innerHTML = html;
        document.querySelector('.main-container').scrollTop = 0;
        updateSelectionState(data.title);
    } catch (e) { content.innerHTML = '<div style="padding:80px; text-align:center; color:var(--text-muted);">Chapter unavailable.</div>'; }
}

function updateSelectionState(title) {
    const isMunkSection = title.includes('Volume') || title === 'Note On The Title';
    const leftSel = document.getElementById('select-left-col');
    const rightSel = document.getElementById('select-right-col');
    if (!leftSel) return;
    if (isMunkSection) { leftSel.value = 'fr'; rightSel.value = 'en'; }
    updateColumnSelectors();
}

function updateColumnSelectors() {
    const leftSel = document.getElementById('select-left-col');
    const rightSel = document.getElementById('select-right-col');
    if (!leftSel) return;
    const leftVal = leftSel.value;
    const rightVal = rightSel.value;
    
    // (2) Force English Left / Hebrew Right swap logic
    const hebrewVariants = ['makbili', 'tibon', 'jrb'];
    if (hebrewVariants.includes(leftVal) && rightVal === 'en') {
        leftSel.value = 'en';
        rightSel.value = leftVal;
        updateColumnSelectors();
        return;
    }

    const mainCont = document.querySelector('.main-container');
    if (mainCont) {
        mainCont.setAttribute('data-left-col', leftSel.value);
        mainCont.setAttribute('data-right-col', rightSel.value);

        // Smart Ordering for Vertical Mode
        const semitic = ['makbili', 'tibon', 'jrb'];
        const isLeftSemitic = semitic.includes(leftVal);
        const isRightSemitic = semitic.includes(rightVal);
        
        if (isRightSemitic && !isLeftSemitic) {
            mainCont.style.setProperty('--left-order', '2');
            mainCont.style.setProperty('--right-order', '1');
        } else {
            mainCont.style.setProperty('--left-order', '1');
            mainCont.style.setProperty('--right-order', '2');
        }
    }
}

function toggleLayoutMode() {
    const mainCont = document.querySelector('.main-container');
    const btn = document.getElementById('layout-toggle-btn');
    if (!mainCont || !btn) return;

    const isVertical = mainCont.getAttribute('data-layout-mode') === 'vertical';
    const newMode = isVertical ? 'side-by-side' : 'vertical';
    
    mainCont.setAttribute('data-layout-mode', newMode);
    btn.innerHTML = newMode === 'vertical' ? '📜 Stacked' : '📖 Parallel';
    localStorage.setItem('munk-layout-mode', newMode);
}

function navigateToLanding() { window.location.href = 'index.html'; }

document.addEventListener('DOMContentLoaded', () => { 
    init(); 
    setTheme(localStorage.getItem('munk-theme') || 'light');
    const savedLayout = localStorage.getItem('munk-layout-mode') || 'side-by-side';
    if (savedLayout === 'vertical') {
        const mainCont = document.querySelector('.main-container');
        const btn = document.getElementById('layout-toggle-btn');
        if (mainCont && btn) {
            mainCont.setAttribute('data-layout-mode', 'vertical');
            btn.innerHTML = '📜 Stacked';
        }
    }
});
"""

READER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Munk Guide">
    <link rel="apple-touch-icon" href="https://raw.githubusercontent.com/google/material-design-icons/master/png/action/book/materialicons/24dp/2x/baseline_book_black_24dp.png">
    <title>Reader - Munk Parallel Guide</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=Frank+Ruhl+Libre:wght@400;700&family=Amiri&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="css/reader.css">
</head>
<body>
    <div id="toc-backdrop" class="toc-backdrop" onclick="toggleTOC()"></div>
    <nav id="toc-drawer" class="toc-drawer">
        <div class="toc-header-bar">
            <span onclick="navigateToLanding()" style="cursor:pointer">Contents</span>
            <button onclick="toggleTOC()">&#x2715;</button>
        </div>
        <div class="mobile-theme-panel">
            <button onclick="setTheme('light')" class="theme-btn">&#9728;&#65039; Light</button>
            <button onclick="setTheme('sepia')" class="theme-btn">&#128220; Sepia</button>
            <button onclick="setTheme('dark')" class="theme-btn">&#127769; Dark</button>
        </div>
        <div class="toc-column-panel" style="padding: 16px 20px; border-bottom: 1px solid var(--border); background: var(--header-bg);">
            <div style="display: flex; flex-direction: column; gap: 12px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <label for="select-left-col" style="font-size: 0.8rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Left Column</label>
                    <select id="select-left-col" onchange="updateColumnSelectors()" style="padding: 6px 10px; border-radius: 6px; border: 1px solid var(--border); background: var(--surface); color: var(--text); font-size: 0.9rem; font-weight: 600; cursor: pointer; outline: none; width: 160px;">
                        <option value="en" selected>Munk (AI-English)</option>
                        <option value="fr">Munk (French)</option>
                        <option value="makbili">&#x05DE;&#x05E7;&#x05D1;&#x05D9;&#x05DC;&#x05D9;</option>
                        <option value="tibon">&#x05D0;&#x05D1;&#x05DF; &#x05EA;&#x05D9;&#x05D1;&#x05D5;&#x05DF;</option>
                        <option value="jrb">Judeo-Arabic</option>
                    </select>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <label for="select-right-col" style="font-size: 0.8rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Right Column</label>
                    <select id="select-right-col" onchange="updateColumnSelectors()" style="padding: 6px 10px; border-radius: 6px; border: 1px solid var(--border); background: var(--surface); color: var(--text); font-size: 0.9rem; font-weight: 600; cursor: pointer; outline: none; width: 160px;">
                        <option value="none">None (Single Column)</option>
                        <option value="en">Munk (AI-English)</option>
                        <option value="fr">Munk (French)</option>
                        <option value="makbili" selected>&#x05DE;&#x05E7;&#x05D1;&#x05D9;&#x05DC;&#x05D9;</option>
                        <option value="tibon">&#x05D0;&#x05D1;&#x05DF; &#x05EA;&#x05D9;&#x05D1;&#x05D5;&#x05DF;</option>
                        <option value="jrb">Judeo-Arabic</option>
                    </select>
                </div>
            </div>
        </div>
        <div id="toc-body" class="toc-body"></div>
    </nav>
    <div class="main-container" data-left-col="en" data-right-col="makbili">
        <div class="header">
            <div class="header-left">
                <button id="hamburger-btn" onclick="toggleTOC()" aria-label="Table of Contents">&#9776;</button>
                <h1 id="main-title">The Guide for the Perplexed</h1>
                <span class="munk-label">Dalalat al-Ha'irin</span>
            </div>
            <div class="theme-controls">
                <button onclick="toggleLayoutMode()" title="Toggle Layout" class="theme-btn" id="layout-toggle-btn">📖 Parallel</button>
                <button onclick="setTheme('light')" title="Light" class="theme-btn" id="btn-light">&#9728;&#65039;</button>
                <button onclick="setTheme('sepia')" title="Sepia" class="theme-btn" id="btn-sepia">&#128220;</button>
                <button onclick="setTheme('dark')"  title="Dark"  class="theme-btn" id="btn-dark">&#127769;</button>
            </div>
        </div>
        <div class="content" id="chapter-content"></div>
    </div>
    <div id="fn-panel" class="fn-panel">
        <div class="fn-handle"></div>
        <div class="fn-panel-header">
            <span class="fn-panel-label">Note</span>
            <button class="fn-panel-close" onclick="closeFnPanel()">Close</button>
        </div>
        <div id="fn-panel-body" class="fn-panel-body"></div>
    </div>
    <script src="js/reader.js"></script>
</body>
</html>"""

LANDING_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Munk Guide">
    <link rel="apple-touch-icon" href="https://raw.githubusercontent.com/google/material-design-icons/master/png/action/book/materialicons/24dp/2x/baseline_book_black_24dp.png">
    <title>The Guide for the Perplexed - Munk Parallel Reader</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=Frank+Ruhl+Libre:wght@400;700&family=Amiri&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="css/reader.css">
</head>
<body style="overflow-y:auto; height:auto; display:block;">
    <div class="content">
        <div class="toc-landing-page">
            <h1 class="landing-title" style="font-size: 2.2rem; line-height: 1.2; margin-bottom: 20px;">
                AI-Assisted Translation of Salomon Munk&#x2019;s French Translation of the Guide to the Perplexed;<br>
                <span style="font-size: 1.5rem; opacity: 0.8;">Hebrew from Makbili Edition</span>
            </h1>
            <div style="text-align: center; margin-bottom: 40px; font-size: 0.9rem; color: var(--text-muted); line-height: 1.6;">
                Sources:
                <a href="https://www.sefaria.org/Guide_for_the_Perplexed" target="_blank" style="color: var(--accent);">Munk (French) via Sefaria</a> |
                <a href="https://www.sefaria.org/Guide_for_the_Perplexed" target="_blank" style="color: var(--accent);">Makbili (Hebrew) via Sefaria</a><br>
                <p style="max-width: 600px; margin: 10px auto; font-style: italic;">
                    This digital edition is created for research and educational purposes.
                    The underlying source texts are utilized in accordance with their respective open licenses
                    and the principles of scholarly fair use.
                </p>
            </div>
            <div id="landing-grid"></div>
        </div>
    </div>
    <script>
        fetch('data/chapters.json').then(r => r.json()).then(chapters => {
            const grid = document.getElementById('landing-grid');
            const groups = { "Munk's Prefaces": [], "Introductions": [], "Part 1": [], "Part 2": [], "Part 3": [], "Munk's Endnotes": [] };
            chapters.forEach(ch => { if (groups[ch.category]) groups[ch.category].push(ch); });
            let html = '';
            for (const [name, list] of Object.entries(groups)) {
                if (list.length === 0) continue;
                html += '<div class="landing-section"><h3>' + name + '</h3><div class="landing-links">';
                list.forEach(ch => { html += '<a href="reader.html?ch=' + ch.slug + '">' + ch.title + '</a>'; });
                html += '</div></div>';
            }
            grid.innerHTML = html;
        });
    </script>
</body>
</html>"""

def build():
    print("Loading Data...")
    with open("Guide for the Perplexed - he - Makbili Edition, Mif'al Mishneh Torah, 2024.json", "r") as f:
        hebrew_data = json.load(f)
    with open("munk_production_v1.json", "r", encoding="utf-8") as f:
        prod_data = json.load(f)
        english_main = prod_data["text"]
        english_footnotes = prod_data["footnotes"]
    
    # Modernize terminology: Replace 'Doctors' with 'Sages' in all English text
    for key in english_main:
        if isinstance(english_main[key], str):
            english_main[key] = re.sub(r'\bDoctors\b', 'Sages', english_main[key])
    for key in english_footnotes:
        if isinstance(english_footnotes[key], str):
            english_footnotes[key] = re.sub(r'\bDoctors\b', 'Sages', english_footnotes[key])

    # Patch English phrasing per user request
    awkward_key = "root.text.Part 2..43.0"
    if awkward_key in english_main:
        english_main[awkward_key] = re.sub(r'Prophecy takes not place save by means of', 'Prophecy only takes place by means of', english_main[awkward_key])
    
    all_unified_footnotes = {}
    def process_row_footnotes(en_text, fr_text, row_key):
        if not row_key: return en_text, fr_text
        final_en = en_text; final_fr = fr_text
        
        # English
        en_matches = list(re.finditer(r"\[\[fn:(\d+)(?:\|([^\]]+))?\]\]", final_en))
        for i in range(len(en_matches)-1, -1, -1):
            m = en_matches[i]; u_id = f"{row_key}.fn_{i+1}"; old_id = f"fn.{m.group(1)}"
            if u_id not in all_unified_footnotes: all_unified_footnotes[u_id] = {"en": "", "fr": ""}
            all_unified_footnotes[u_id]["en"] = english_footnotes.get(old_id, "")
            label = m.group(2) or str(i+1)
            final_en = final_en[:m.start()] + f'<sup class="fn-ref" onclick="showFn(\'{u_id}\')">{label}</sup>' + final_en[m.end():]

        # French
        fr_matches = []; search_ptr = 0
        while True:
            m = re.search(r'<sup[^>]*class=["\']footnote-marker["\'][^>]*>\s*\(?(.*?)\)?\s*</sup>\s*<i[^>]*class=["\']footnote["\'][^>]*>', final_fr[search_ptr:])
            if not m: break
            s = search_ptr+m.start(); marker = m.group(1).strip(); f_s = search_ptr+m.end(); d = 1; c = f_s
            while d > 0 and c < len(final_fr):
                no = final_fr.find('<i', c); nc = final_fr.find('</i>', c)
                if nc == -1: c = len(final_fr); d = 0; break
                if no != -1 and no < nc: d += 1; c = no+2
                else: d -= 1; c = nc+4
            fr_matches.append({"start": s, "end": c, "content": final_fr[f_s:c-4], "marker": marker}); search_ptr = c

        for i in range(len(fr_matches)-1, -1, -1):
            m = fr_matches[i]; u_id = f"{row_key}.fn_{i+1}"
            if u_id not in all_unified_footnotes: all_unified_footnotes[u_id] = {"en": "", "fr": ""}
            all_unified_footnotes[u_id]["fr"] = m["content"]
            final_fr = final_fr[:m["start"]] + f'<sup class="fn-ref" onclick="showFn(\'{u_id}\')">({m["marker"]})</sup>' + final_fr[m["end"]:]
        return final_en, final_fr
    
    variants = {}
    for v_name, v_path in [("fr", "French_Healed_Enriched.json"), ("jrb", "Guide for the Perplexed - he - Judeo Arabic, Paris, 1856 [jrb].json"), ("tibon", "Guide for the Perplexed - he - Moreh Nevuchim, translated by Ibn Tibon.json")]:
        if os.path.exists(v_path):
            with open(v_path, "r", encoding="utf-8") as f: variants[v_name] = json.load(f).get("text", {})

    def get_en_text(key):
        if key in english_main: return english_main[key]
        parts = []; i = 0
        while f"{key}.sub_{i}" in english_main: parts.append(english_main[f"{key}.sub_{i}"]); i += 1
        return " ".join(parts) if parts else "[Translation Missing]"

    def get_var_text(v_name, key):
        lang_main = variants.get(v_name, {}); parts = key.split(".")
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

    unified_chapters = []
    preface_files = [("preface_resegmented.json", "preface_english_final.json", "Introduction to Volume I"), ("preface_vol2.json", None, "Introduction to Volume II"), ("preface_vol3.json", None, "Introduction to Volume III"), ("munk_title_note.json", None, "Note On The Title")]
    for fr_fn, en_fn, title in preface_files:
        if os.path.exists(fr_fn):
            with open(fr_fn, "r", encoding="utf-8") as f: fr_data = json.load(f)
            fr_paras = fr_data.get("fr", []) if isinstance(fr_data, dict) else fr_data
            en_paras = fr_data.get("en", []) if isinstance(fr_data, dict) else []
            if not en_paras and en_fn and os.path.exists(en_fn):
                with open(en_fn, "r", encoding="utf-8") as f: en_paras = json.load(f)
            custom_segs = []
            for i in range(len(fr_paras)): custom_segs.append({"he": fr_paras[i], "en": en_paras[i] if i < len(en_paras) else "[Translation Missing]"})
            unified_chapters.append({"title": title, "custom_segments": custom_segs, "is_munk_intro": True, "category": "Munk's Prefaces"})
    
    letter_he = hebrew_data["text"]["Letter to R Joseph son of Judah"]
    letter_segments = [{"he": "<br>".join(letter_he[0].split("<br>")[:-1]), "en": get_en_text("root.text.Letter to R Joseph son of Judah.Poem"), "key": "root.text.Letter to R Joseph son of Judah.Poem"}, {"he": letter_he[0].split("<br>")[-1], "en": get_en_text("root.text.Letter to R Joseph son of Judah.0"), "key": "root.text.Letter to R Joseph son of Judah.0"}, {"he": letter_he[2], "en": get_en_text("root.text.Letter to R Joseph son of Judah.1") + " " + get_en_text("root.text.Letter to R Joseph son of Judah.2"), "key": "root.text.Letter to R Joseph son of Judah.1"}]
    if len(letter_he) > 3: letter_segments.append({"he": letter_he[3], "en": get_en_text("root.text.Letter to R Joseph son of Judah.3"), "key": "root.text.Letter to R Joseph son of Judah.3"})
    unified_chapters.append({"title": "Letter to R Joseph son of Judah", "custom_segments": letter_segments, "category": "Introductions"})
    unified_chapters.append({"title": "Prefatory Remarks", "key_prefix": "root.text.Prefatory Remarks", "segments": hebrew_data["text"]["Prefatory Remarks"], "category": "Introductions"})
    
    for p_num in ["Part 1", "Part 2", "Part 3"]:
        p_data = hebrew_data["text"][p_num]
        if "Introduction" in p_data: unified_chapters.append({"title": f"{p_num} - Introduction", "key_prefix": f"root.text.{p_num}.Introduction", "segments": p_data["Introduction"], "category": p_num})
        if "" in p_data:
            for i, segs in enumerate(p_data[""]): unified_chapters.append({"title": f"{p_num} - Chapter {i+1}", "key_prefix": f"root.text.{p_num}..{i}", "segments": segs, "category": p_num})
    
    endnote_files = [("endnotes_vol1.json", "Endnotes to Volume I"), ("endnotes_vol2.json", "Endnotes to Volume II"), ("endnotes_vol3.json", "Endnotes to Volume III")]
    for fn, title in endnote_files:
        if os.path.exists(fn):
            with open(fn, "r", encoding="utf-8") as f: en_data = json.load(f)
            custom_segs = []
            for i in range(len(en_data["fr"])): custom_segs.append({"he": en_data["fr"][i], "en": en_data["en"][i]})
            unified_chapters.append({"title": title, "custom_segments": custom_segs, "is_munk_intro": True, "category": "Munk's Endnotes"})

    def get_slug(title): return title.replace(' ', '-').replace('/', '-').replace('.', '').lower()
    chapter_index = []
    print(f"Generating modular files...")
    for idx, ch in enumerate(unified_chapters):
        slug = get_slug(ch["title"])
        rows = []
        if "custom_segments" in ch:
            for s_idx, seg in enumerate(ch["custom_segments"]):
                rk = seg.get("key") or f"custom.{idx}.{s_idx}"
                fr_val = seg["he"] if ch.get("is_munk_intro") else "[Text Missing]"
                en_p, fr_p = process_row_footnotes(seg["en"], fr_val, rk)
                rows.append({"key": rk, "variants": {"en": en_p, "fr": fr_p, "makbili": seg["he"] if not ch.get("is_munk_intro") else "[Text Missing]", "jrb": "[Text Missing]", "tibon": "[Text Missing]"}})
        else:
            for i, he_text in enumerate(ch["segments"]):
                key = f"{ch['key_prefix']}.{i}"
                en_raw = get_en_text(key)
                fr_raw = get_var_text("fr", key)
                en_p, fr_p = process_row_footnotes(en_raw, fr_raw, key)
                rows.append({"key": key, "variants": {"en": en_p, "makbili": he_text, "fr": fr_p, "jrb": get_var_text("jrb", key), "tibon": get_var_text("tibon", key)}})
        ch_data = {"title": ch["title"], "rows": rows, "prev": {"title": unified_chapters[idx-1]["title"], "slug": get_slug(unified_chapters[idx-1]["title"])} if idx > 0 else None, "next": {"title": unified_chapters[idx+1]["title"], "slug": get_slug(unified_chapters[idx+1]["title"])} if idx < len(unified_chapters)-1 else None}
        with open(f"{DIST}/data/{slug}.json", "w", encoding="utf-8") as f: json.dump(ch_data, f)
        chapter_index.append({"title": ch["title"], "slug": slug, "category": ch["category"]})
    
    with open(f"{DIST}/data/chapters.json", "w", encoding="utf-8") as f: json.dump(chapter_index, f)
    with open(f"{DIST}/data/footnotes.json", "w", encoding="utf-8") as f: json.dump(all_unified_footnotes, f)
    with open(f"{DIST}/reader.html", "w", encoding="utf-8") as f: f.write(READER_HTML)
    with open(f"{DIST}/index.html", "w", encoding="utf-8") as f: f.write(LANDING_HTML)
    with open(f"{DIST}/css/reader.css", "w", encoding="utf-8") as f: f.write(CSS_CONTENT)
    with open(f"{DIST}/js/reader.js", "w", encoding="utf-8") as f: f.write(JS_CONTENT)
    print("Build finished successfully.")

if __name__ == "__main__": build()
