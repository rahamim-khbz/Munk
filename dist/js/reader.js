
// Version: 1.1.0 - Rabbi Yosef Qafih Hebrew Translation & Isolated Footnote System
let footnotes = {};
let qafihFootnotes = null;
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
        window.addEventListener('hashchange', focusHashRow);
    } catch (e) { console.error("Init failed", e); }
}

function setTheme(mode) {
    if (!['light', 'sepia', 'dark'].includes(mode)) {
        mode = 'light';
    }
    document.documentElement.className = mode === 'light' ? '' : mode;
    try {
        localStorage.setItem('munk-theme', mode);
        localStorage.setItem('reader-theme', mode);
    } catch (e) {}
    document.querySelectorAll('.theme-btn').forEach(b => {
        const text = b.textContent.trim().toLowerCase();
        b.classList.toggle('active', b.id === ('btn-' + mode) || text.includes(mode));
    });
}

function toggleTOC() {
    document.getElementById('toc-drawer').classList.toggle('open');
    document.getElementById('toc-backdrop').classList.toggle('visible');
}

function buildTOC() {
    const body = document.getElementById('toc-body');
    if (!body) return;
    body.innerHTML = '';

    const indexLink = document.createElement('a');
    indexLink.href = 'scripture.html';
    indexLink.className = 'toc-section-btn';
    indexLink.style.textDecoration = 'none';
    indexLink.style.color = 'var(--accent)';
    indexLink.style.display = 'flex';
    indexLink.style.alignItems = 'center';
    indexLink.style.justifyContent = 'space-between';
    indexLink.style.padding = '14px 16px';
    indexLink.style.fontWeight = '700';
    indexLink.innerHTML = `<span>📖 Scriptural Index</span><span dir="rtl" lang="he" style="font-family:var(--font-hebrew); font-weight:600;">מפתח פסוקים</span>`;
    body.appendChild(indexLink);

    const groups = { "Introductions": [], 'Part 1': [], 'Part 2': [], 'Part 3': [] };
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
                tile.textContent = ch.title;
                tile.onclick = () => { window.location.href = 'reader.html?ch=' + ch.slug; };
                panel.appendChild(tile);
            });
            panel.style.padding = '8px 32px 24px'; panel.style.display = 'grid'; panel.style.gap = '8px';
        } else {
            const grid = document.createElement('div'); grid.className = 'toc-tile-grid';
            chapters.forEach(ch => {
                const tile = document.createElement('div'); tile.className = 'toc-tile'; 
                let isFullWidth = false;
                let text = ch.title;
                if (ch.title.includes("Munk's Introduction")) {
                    text = "Munk's Introduction";
                    isFullWidth = true;
                } else if (ch.title.includes("Maimonides' Introduction") || ch.title.endsWith(" - Introduction")) {
                    text = "Maimonides' Introduction";
                    isFullWidth = true;
                } else if (ch.title.includes("Munk's Endnotes") || ch.title.includes("Endnotes")) {
                    text = "Munk's Endnotes";
                    isFullWidth = true;
                } else {
                    const m = ch.title.match(/Chapter (\d+)/);
                    if (m) text = m[1];
                }
                tile.textContent = text;
                if (isFullWidth) {
                    tile.style.gridColumn = 'span 5';
                    tile.style.aspectRatio = 'auto';
                    tile.style.padding = '12px';
                }
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

function formatFootnoteToken(match, n, label) {
    let displayLabel = label;
    if (!displayLabel) {
        if (n.startsWith('qafih.') || n.startsWith('fn.qafih.')) {
            const lastPart = n.split('.').pop();
            displayLabel = lastPart.startsWith('ast') ? '*' + lastPart.slice(3) : lastPart;
        } else {
            displayLabel = '*';
        }
    }
    const fullId = (n.startsWith('fn.') ? n : 'fn.' + n).replace(/'/g, "\\'");
    return `<sup class="fn-ref" onclick="showFn('${fullId}')">${displayLabel}</sup>`;
}

async function showFn(id) {
    const panel = document.getElementById('fn-panel');
    const mainCont = document.querySelector('.main-container');

    // Check if this is a Rabbi Yosef Qafih note
    if (id.startsWith('fn.qafih.') || id.startsWith('qafih.')) {
        const normId = id.startsWith('fn.') ? id : 'fn.' + id;
        if (!qafihFootnotes) {
            try {
                const res = await fetch('data/qafih_footnotes.json');
                qafihFootnotes = await res.json();
            } catch (e) {
                console.error("Failed to load Qafih footnotes", e);
            }
        }
        const noteText = (qafihFootnotes && qafihFootnotes[normId]) || 'הערה אינה נמצאת.';
        
        document.getElementById('fn-panel-body').innerHTML = `
            <div style="direction: rtl; text-align: right; font-family: var(--font-hebrew);">
                <div style="font-weight: 700; color: #10b981; margin-bottom: 8px; font-size: 0.95rem; letter-spacing: 0.05em;">Qafih's Note:</div>
                <div style="font-size: 1.15rem; line-height: 1.8;">${noteText}</div>
            </div>
        `;
        panel.classList.add('open');
        mainCont.classList.add('fn-open');
        return;
    }

    // Salomon Munk note - resolve canonical fn.N key and support flat string or mapped format
    if (!footnotes || Object.keys(footnotes).length === 0) {
        try {
            const res = await fetch('data/footnotes.json');
            footnotes = await res.json();
        } catch (e) {
            console.error("Failed to load footnotes", e);
        }
    }

    let data = footnotes[id];
    if (data === undefined && typeof id === 'string') {
        if (!id.startsWith('fn.')) {
            data = footnotes['fn.' + id];
        } else {
            data = footnotes[id.replace(/^fn\./, '')];
        }
    }

    let rawEn = '';
    let rawFr = '';
    if (typeof data === 'string') {
        // Flat string format from canonical data/footnotes.json
        rawEn = data;
        rawFr = '';
    } else if (data && typeof data === 'object') {
        // Mapped keys format { en: '...', fr: '...' } or { text: '...' }
        rawEn = data.en || data.text || '';
        rawFr = data.fr || '';
    }

    if (!rawEn && !rawFr) {
        rawEn = 'Note content missing.';
    }

    const col1 = mainCont ? mainCont.getAttribute('data-left-col') : 'en';
    const col2 = mainCont ? mainCont.getAttribute('data-right-col') : 'fr';
    const isComparingEnglishFrench = (
        (col1 === 'en' && col2 === 'fr') || 
        (col1 === 'fr' && col2 === 'en')
    );
    
    let contentHtml = '';
    
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

    contentHtml = contentHtml.replace(/\[\[fn:([^|\]]+)(?:\|([^\]]+))?\]\]/g, formatFootnoteToken);
    
    document.getElementById('fn-panel-body').innerHTML = `
        <div style="direction: ltr; text-align: left; font-family: var(--font-english);">
            <div style="font-weight: 700; color: #3b82f6; margin-bottom: 8px; font-size: 0.95rem; letter-spacing: 0.05em;">Munk's Note:</div>
            <div>${contentHtml}</div>
        </div>
    `;
    panel.classList.add('open');
    mainCont.classList.add('fn-open');
}

function closeFnPanel() {
    document.getElementById('fn-panel').classList.remove('open');
    document.querySelector('.main-container').classList.remove('fn-open');
}

async function loadChapter(slug) {
    const content = document.getElementById('chapter-content');
    if (!/^[a-zA-Z0-9_-]+$/.test(slug)) {
        content.innerHTML = '<div style="padding:80px; text-align:center; color:var(--text-muted);">Invalid chapter identifier.</div>';
        return;
    }
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
                        let processed = t.replace(/\[\[fn:([^|\]]+)(?:\|([^\]]+))?\]\]/g, formatFootnoteToken);
                        return `<span class="variant-span variant-${v}">${processed}</span>`;
                    }).join('')}
                </div>
                <div class="right-cell">
                    ${Object.entries(row.variants).map(([v, t]) => {
                        let processed = t.replace(/\[\[fn:([^|\]]+)(?:\|([^\]]+))?\]\]/g, formatFootnoteToken);
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
        if (!location.hash || !location.hash.startsWith('#row-')) {
            const mainCont = document.querySelector('.main-container');
            if (mainCont) mainCont.scrollTop = 0;
        }
        updateSelectionState(data.title);
        focusHashRow();
    } catch (e) { content.innerHTML = '<div style="padding:80px; text-align:center; color:var(--text-muted);">Chapter unavailable.</div>'; }
}

let highlightTimeout = null;

function focusHashRow() {
    if (!location.hash || !location.hash.startsWith('#row-')) return;
    const rawId = location.hash.slice(1);
    let decodedId = rawId;
    try {
        decodedId = decodeURIComponent(rawId);
    } catch (e) {
        decodedId = rawId;
    }

    const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const scrollBehavior = prefersReduced ? 'auto' : 'smooth';

    const attemptScroll = (retryCount = 0) => {
        const el = document.getElementById(decodedId) || document.getElementById(rawId);
        if (el) {
            el.scrollIntoView({ behavior: scrollBehavior, block: 'center' });
            document.querySelectorAll('.row-highlight').forEach(r => r.classList.remove('row-highlight'));
            el.classList.add('row-highlight');
            if (highlightTimeout) {
                clearTimeout(highlightTimeout);
                highlightTimeout = null;
            }
            highlightTimeout = setTimeout(() => {
                el.classList.remove('row-highlight');
                highlightTimeout = null;
            }, 3000);
        } else if (retryCount < 6) {
            setTimeout(() => attemptScroll(retryCount + 1), 60 * (retryCount + 1));
        }
    };

    requestAnimationFrame(() => attemptScroll(0));
}

function updateSelectionState(title) {
    const isMunkSection = title.includes("Munk's") || title.includes('Volume') || title.includes('Note On The Title') || title.includes('Endnote');
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
    const hebrewVariants = ['makbili', 'tibon', 'jrb', 'qafih'];
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
        const semitic = ['makbili', 'tibon', 'jrb', 'qafih'];
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
    try {
        localStorage.setItem('munk-layout-mode', newMode);
    } catch (e) {}
}

function navigateToLanding() { window.location.href = 'index.html'; }

document.addEventListener('DOMContentLoaded', () => { 
    init(); 
    let savedTheme = 'light';
    let savedLayout = 'side-by-side';
    try {
        savedTheme = localStorage.getItem('munk-theme') || localStorage.getItem('reader-theme') || 'light';
        savedLayout = localStorage.getItem('munk-layout-mode') || 'side-by-side';
    } catch (e) {}
    setTheme(savedTheme);
    if (savedLayout === 'vertical') {
        const mainCont = document.querySelector('.main-container');
        const btn = document.getElementById('layout-toggle-btn');
        if (mainCont && btn) {
            mainCont.setAttribute('data-layout-mode', 'vertical');
            btn.innerHTML = '📜 Stacked';
        }
    }
});
