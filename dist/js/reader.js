let faurCommentary = null;
let faurAnnotationsEnabled = true;

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
    document.querySelectorAll('#btn-light, #btn-sepia, #btn-dark, .mobile-theme-panel button.theme-btn:not(#btn-mobile-faur-toggle)').forEach(b => {
        const text = b.textContent.trim().toLowerCase();
        b.classList.toggle('active', b.id === ('btn-' + mode) || text.includes(mode));
    });
}

function initFaurAnnotations() {
    let saved = 'on';
    try {
        saved = localStorage.getItem('munk-faur-annotations');
        if (saved === null) saved = 'on';
    } catch (e) {
        saved = 'on';
    }
    faurAnnotationsEnabled = (saved !== 'off' && saved !== 'false');
    applyFaurState();
}

function applyFaurState() {
    const mainCont = document.querySelector('.main-container');
    const stateStr = faurAnnotationsEnabled ? 'on' : 'off';
    if (mainCont) {
        mainCont.setAttribute('data-faur', stateStr);
    }
    const desktopBtn = document.getElementById('btn-faur-toggle');
    const mobileBtn = document.getElementById('btn-mobile-faur-toggle');
    [desktopBtn, mobileBtn].forEach(btn => {
        if (btn) {
            btn.classList.toggle('active', faurAnnotationsEnabled);
            btn.setAttribute('aria-pressed', faurAnnotationsEnabled ? 'true' : 'false');
        }
    });
    const tocSwitch = document.getElementById('btn-toc-faur-toggle');
    if (tocSwitch) {
        tocSwitch.classList.toggle('active', faurAnnotationsEnabled);
        tocSwitch.setAttribute('aria-checked', faurAnnotationsEnabled ? 'true' : 'false');
    }
}

function toggleFaurAnnotations() {
    faurAnnotationsEnabled = !faurAnnotationsEnabled;
    try {
        localStorage.setItem('munk-faur-annotations', faurAnnotationsEnabled ? 'on' : 'off');
    } catch (e) {}
    applyFaurState();
}

async function loadFaurCommentary() {
    if (faurCommentary) return faurCommentary;
    try {
        const res = await fetch('data/faur_commentary_map.json');
        if (res.ok !== undefined && !res.ok) {
            console.warn('Faur commentary map not found, proceeding without annotations.');
            faurCommentary = { metadata: {}, chapters: {}, tier2_by_row_key: {} };
            return faurCommentary;
        }
        faurCommentary = await res.json();
        return faurCommentary;
    } catch (e) {
        console.warn('Error loading Faur commentary map:', e);
        faurCommentary = { metadata: {}, chapters: {}, tier2_by_row_key: {} };
        return faurCommentary;
    }
}

const FAUR_PART_CHAPTER_MAP = {
    'Part One: Apophasis': 1,
    'Part Two: Imagination': 2,
    'Part Three: Cosmology': 3,
    'Part Four: Anthropology': 4
};

function escapeAttr(str) {
    return String(str || '')
        .replace(/&/g, '&amp;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
}

function formatFaurCitation(entry) {
    if (!entry) return 'Homo Mysticus';
    if (entry.citation) return entry.citation;
    const chNum = entry.faur_chapter || FAUR_PART_CHAPTER_MAP[entry.part_title];
    if (chNum && entry.section_title) {
        return `Homo Mysticus, Chapter ${chNum} - ${entry.section_title}`;
    }
    if (entry.part_title === 'Introduction' || entry.section_title === 'Introduction') {
        return 'Homo Mysticus, Introduction';
    }
    return entry.section_title ? `Homo Mysticus - ${entry.section_title}` : 'Homo Mysticus';
}

function formatFaurBadge(entry) {
    if (!entry) return 'HM';
    const chNum = entry.faur_chapter || FAUR_PART_CHAPTER_MAP[entry.part_title];
    if (chNum) return 'Ch. ' + chNum;
    if (entry.part_title === 'Introduction' || entry.section_title === 'Introduction') return 'Intro';
    return 'HM';
}

function formatFaurCleanTitle(entry) {
    if (!entry) return 'Commentary';
    return entry.section_title || 'Commentary';
}

function formatFaurCardHeading(entry) {
    if (!entry) return 'Homo Mysticus';
    const chNum = entry.faur_chapter || FAUR_PART_CHAPTER_MAP[entry.part_title];
    if (chNum) {
        return 'Chapter ' + chNum + ' — ' + (entry.section_title || 'Commentary');
    }
    if (entry.part_title === 'Introduction' || entry.section_title === 'Introduction') {
        return 'Introduction';
    }
    return entry.section_title || 'Homo Mysticus';
}

function formatFaurReadLink(entry) {
    const chNum = entry.faur_chapter || FAUR_PART_CHAPTER_MAP[entry.part_title];
    const chLabel = chNum ? `Chapter ${chNum}` : (entry.part_title === 'Introduction' ? 'Introduction' : (entry.section_title || 'Section'));
    return `Read full section in Homo Mysticus (${chLabel}) ↗`;
}

function formatFaurContent(htmlStr, slug) {
    if (!htmlStr) return '';
    return htmlStr.replace(/<sup class="fn-callout"><a [^>]*href="#(fn_[^"]+)"[^>]*>(\d+)<\/a><\/sup>/g, (m, fnId, num) => {
        return `<sup class="fn-ref faur-fn-ref" onclick="showFn('fn.faur.${slug}.${fnId}')" title="View Faur's Footnote">${num}</sup>`;
    });
}

function toggleFaurTopBox(forceState) {
    const topBox = document.getElementById('faur-top-box');
    const inlineBtn = document.getElementById('btn-chapter-faur');
    if (!topBox) return;
    const currentlyOpen = topBox.classList.contains('open');
    const nextOpen = typeof forceState === 'boolean' ? forceState : !currentlyOpen;
    topBox.classList.toggle('open', nextOpen);
    topBox.setAttribute('aria-hidden', nextOpen ? 'false' : 'true');
    if (inlineBtn) {
        inlineBtn.classList.toggle('active', nextOpen);
        inlineBtn.setAttribute('aria-expanded', nextOpen ? 'true' : 'false');
        const chev = inlineBtn.querySelector('.faur-inline-chevron');
        if (chev) chev.textContent = nextOpen ? '▲' : '▼';
    }
}

function switchFaurSubsection(index) {
    const topBox = document.getElementById('faur-top-box');
    if (!topBox) return;
    const cards = topBox.querySelectorAll('.faur-subsection-card');
    const tabs = topBox.querySelectorAll('.faur-subsection-tab');
    cards.forEach((card, idx) => {
        const isTarget = idx === index;
        const body = card.querySelector('.faur-subsection-body');
        const headerBtn = card.querySelector('.faur-subsection-header');
        const icon = card.querySelector('.faur-subsection-toggle-icon');
        card.classList.toggle('open', isTarget);
        if (body) body.classList.toggle('open', isTarget);
        if (headerBtn) headerBtn.setAttribute('aria-expanded', isTarget ? 'true' : 'false');
        if (icon) icon.textContent = isTarget ? '▲' : '▼';
    });
    tabs.forEach((tab, idx) => {
        const isTarget = idx === index;
        tab.classList.toggle('active', isTarget);
        tab.setAttribute('aria-selected', isTarget ? 'true' : 'false');
    });
}

function toggleFaurSubsection(btn) {
    const card = btn.closest('.faur-subsection-card');
    if (!card) return;
    const idx = parseInt(card.getAttribute('data-subsection-index'), 10);
    const body = card.querySelector('.faur-subsection-body');
    const icon = btn.querySelector('.faur-subsection-toggle-icon');
    const isExpanded = btn.getAttribute('aria-expanded') === 'true';
    const nextExpanded = !isExpanded;
    btn.setAttribute('aria-expanded', nextExpanded ? 'true' : 'false');
    card.classList.toggle('open', nextExpanded);
    if (body) body.classList.toggle('open', nextExpanded);
    if (icon) icon.textContent = nextExpanded ? '▲' : '▼';

    // Synchronize corresponding tab if multiple subsections exist
    if (nextExpanded && !isNaN(idx)) {
        const topBox = document.getElementById('faur-top-box');
        if (topBox) {
            topBox.querySelectorAll('.faur-subsection-tab').forEach((tab, tIdx) => {
                const isTarget = tIdx === idx;
                tab.classList.toggle('active', isTarget);
                tab.setAttribute('aria-selected', isTarget ? 'true' : 'false');
            });
        }
    }
}

function renderFaurTopBox(sections, slug) {
    if (!sections || !sections.length) return '';
    const hasMultiple = sections.length > 1;
    const tabsHtml = hasMultiple ? `
        <div class="faur-subsection-tabs" role="tablist" aria-label="Homo Mysticus Subsections">
            ${sections.map((entry, idx) => {
                const cit = formatFaurCitation(entry);
                const badge = formatFaurBadge(entry);
                const cleanTitle = formatFaurCleanTitle(entry);
                return `<button type="button" role="tab" class="faur-subsection-tab ${idx === 0 ? 'active' : ''}" aria-selected="${idx === 0 ? 'true' : 'false'}" title="${escapeAttr(cit)}" onclick="switchFaurSubsection(${idx})"><span class="faur-ch-badge">${badge}</span><span class="faur-tab-title">${cleanTitle}</span></button>`;
            }).join('')}
        </div>
    ` : '';

    const cardsHtml = sections.map((entry, idx) => {
        const citation = formatFaurCitation(entry);
        const badge = formatFaurBadge(entry);
        const cardHeading = formatFaurCardHeading(entry);
        const readLinkText = formatFaurReadLink(entry);
        const readLinkHref = `Homo_Mysticus_Sample_Chapters.html?ch=${encodeURIComponent(entry.slug || slug)}`;
        const processedContent = formatFaurContent(entry.content_html, entry.slug || slug);
        const isOpenInitially = (idx === 0);
        const keyTerms = entry.key_terms || [];
        const keyTermsHtml = keyTerms.length > 0 ? `
            <div class="faur-key-terms-bar">
                ${keyTerms.map(kt => `
                    <div class="faur-key-term-chip">
                        <span class="faur-key-term-label">Key Term:</span>
                        ${kt.term ? `<strong class="faur-key-term-name">${kt.term}</strong>` : ''}
                        ${kt.original_script ? `<span class="faur-key-term-orig" dir="rtl" lang="he">${kt.original_script}</span>` : ''}
                        ${kt.anchor_label ? `<span class="faur-key-term-desc">— ${kt.anchor_label}</span>` : ''}
                    </div>
                `).join('')}
            </div>
        ` : '';

        return `
            <div class="faur-subsection-card ${isOpenInitially ? 'open' : ''}" data-subsection-index="${idx}">
                <div class="faur-subsection-header">
                    <div class="faur-subsection-header-main">
                        <div class="faur-subsection-citation" data-citation="${escapeAttr(citation)}"><span class="faur-ch-badge">${badge}</span> ${cardHeading}<span class="sr-only"> (${citation})</span></div>
                    </div>
                </div>
                <div class="faur-subsection-body ${isOpenInitially ? 'open' : ''}">
                    ${keyTermsHtml}
                    <div class="faur-subsection-content">
                        ${processedContent}
                    </div>
                    <div class="faur-subsection-footer">
                        <a href="${readLinkHref}" target="_blank" rel="noopener" class="faur-read-link">${readLinkText}<span class="sr-only"> (opens in new tab)</span></a>
                        <span class="faur-footer-sep">·</span>
                        <span>José Faur, <em>Homo Mysticus: A Guide to Maimonides's Guide for the Perplexed</em> (Syracuse University Press, 1998)</span>
                    </div>
                    ${typeof renderHmFeedback === 'function' ? renderHmFeedback(entry.id, entry.slug || slug, entry.section_title) : ''}
                </div>
            </div>
        `;
    }).join('');

    return `
        <section id="faur-top-box" class="faur-top-box" aria-hidden="true" aria-label="Homo Mysticus Commentary">
            <div class="faur-box-banner">
                <span class="faur-box-banner-title"><strong>Homo Mysticus</strong> · José Faur Commentary</span>
                <span class="faur-box-banner-count">${sections.length} ${sections.length === 1 ? 'section' : 'sections'}</span>
            </div>
            ${tabsHtml}
            <div class="faur-subsections-list">
                ${cardsHtml}
            </div>
        </section>
    `;
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
    indexLink.style.display = 'block';
    indexLink.style.padding = '14px 16px';
    indexLink.style.fontWeight = '700';
    indexLink.innerHTML = 'Scriptural Index';
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

    // Check if this is a José Faur note (fn.faur.slug.fn_X)
    if (id.startsWith('fn.faur.') || id.startsWith('faur.')) {
        if (!faurCommentary) {
            await loadFaurCommentary();
        }
        const parts = id.replace(/^faur\./, 'fn.faur.').split('.');
        // Format: fn.faur.<slug>.<fn_id>
        const slug = parts[2];
        const fnId = parts.slice(3).join('.');
        
        let fnText = '';
        if (faurCommentary && faurCommentary.section_6_footnotes && faurCommentary.section_6_footnotes[fnId]) {
            fnText = faurCommentary.section_6_footnotes[fnId];
        } else if (faurCommentary && faurCommentary.chapters && faurCommentary.chapters[slug]) {
            const ch = faurCommentary.chapters[slug];
            for (const t1 of (ch.tier1 || [])) {
                if (t1.footnotes && t1.footnotes[fnId]) {
                    fnText = t1.footnotes[fnId];
                    break;
                }
            }
            if (!fnText) {
                for (const t2 of (ch.tier2 || [])) {
                    if (t2.footnotes && t2.footnotes[fnId]) {
                        fnText = t2.footnotes[fnId];
                        break;
                    }
                }
            }
            if (!fnText && ch.footnotes && ch.footnotes[fnId]) {
                fnText = ch.footnotes[fnId];
            }
        }
        if (!fnText) fnText = 'Footnote not found.';
        
        document.getElementById('fn-panel-body').innerHTML = `
            <div style="direction: ltr; text-align: left; font-family: var(--font-english);">
                <div style="font-weight: 700; color: #b45309; margin-bottom: 8px; font-size: 0.95rem; letter-spacing: 0.05em;">Faur's Note:</div>
                <div style="font-size: 1.05rem; line-height: 1.7; color: var(--text);">${fnText}</div>
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
    try {        const [res, commentary] = await Promise.all([
            fetch(`data/${slug}.json`),
            loadFaurCommentary()
        ]);
        const data = await res.json();
        document.getElementById('main-title').textContent = data.title;
        document.title = data.title + " - Munk's Guide";
        let html = '';
        const faurSections = (commentary && commentary.chapters && commentary.chapters[slug] && commentary.chapters[slug].tier1) || [];
        const hasFaur = faurSections.length > 0;
        const inlineFaurBtnHtml = hasFaur ? `
            <button type="button"
                    id="btn-chapter-faur"
                    class="faur-inline-btn"
                    onclick="toggleFaurTopBox()"
                    aria-expanded="false"
                    aria-controls="faur-top-box"
                    aria-label="Toggle Homo Mysticus Commentary"
                    title="Open Homo Mysticus Commentary (${faurSections.length} ${faurSections.length === 1 ? 'subsection' : 'subsections'})">
                <span class="faur-inline-glyph">❦ HM</span>
                <span class="faur-inline-chevron" aria-hidden="true">▼</span>
            </button>
        ` : '';
        html += `<div class="chapter-header"><div class="chapter-header-row"><h2>${data.title}</h2>${inlineFaurBtnHtml}</div></div>`;
        if (hasFaur) {
            html += renderFaurTopBox(faurSections, slug);
        }
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
        html += `<div class="chapter-nav" style="display:flex; justify-content:space-between; align-items:center; margin-top:40px; padding-top:20px; padding-bottom:calc(2rem + env(safe-area-inset-bottom)); border-top:1px solid var(--border);">`;
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
    initFaurAnnotations();
    if (savedLayout === 'vertical') {
        const mainCont = document.querySelector('.main-container');
        const btn = document.getElementById('layout-toggle-btn');
        if (mainCont && btn) {
            mainCont.setAttribute('data-layout-mode', 'vertical');
            btn.innerHTML = '📜 Stacked';
        }
    }
});
