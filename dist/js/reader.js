
let footnotes = {};
let chapterIndex = [];
let activeChapterId = null;

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
    chapterIndex.forEach(ch => {
        const cat = ch.category || "Introductions";
        if (groups[cat]) groups[cat].push(ch);
    });

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
                tile.className = 'toc-tile'; tile.style.gridColumn = 'span 5'; tile.style.padding = '8px 16px'; tile.style.aspectRatio = 'auto';
                tile.textContent = ch.title.replace('Part 1 - ', '').replace('Part 2 - ', '').replace('Part 3 - ', '');
                tile.onclick = () => { window.location.href = 'reader.html?ch=' + ch.slug; };
                panel.appendChild(tile);
            });
            panel.style.padding = '8px 20px 20px'; panel.style.display = 'grid'; panel.style.gap = '8px';
        } else {
            const grid = document.createElement('div');
            grid.className = 'toc-tile-grid';
            chapters.forEach(ch => {
                const tile = document.createElement('div');
                tile.className = 'toc-tile'; 
                let num = ch.title.match(/Chapter (\d+)/) ? ch.title.match(/Chapter (\d+)/)[1] : "Intro";
                tile.textContent = num;
                if (num === "Intro") { tile.style.gridColumn = 'span 5'; tile.style.aspectRatio = 'auto'; tile.style.padding = '10px'; }
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
    const enInView = (col1 === 'en' || col2 === 'en');
    const frInView = (col1 === 'fr' || col2 === 'fr');
    
    let contentHtml = '';
    if (enInView && frInView) {
        contentHtml = `<div class="fn-dual-container"><div class="fn-col"><div class="fn-lang-label">English</div><div>${data.en}</div></div><div class="fn-col"><div class="fn-lang-label">French</div><div>${data.fr}</div></div></div>`;
    } else if (frInView && data.fr) contentHtml = data.fr;
    else contentHtml = data.en;
    
    contentHtml = contentHtml.replace(/\[\[fn:(\d+)(?:\|([^\]]+))?\]\]/g, (m, n, label) => `<sup class="fn-marker">${label || '*'}</sup>`);
    
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
    content.innerHTML = '<div style="padding:100px; text-align:center; font-style:italic; opacity:0.6;">Loading Manuscript...</div>';
    
    try {
        const res = await fetch(`data/${slug}.json`);
        const data = await res.json();
        
        document.getElementById('main-title').textContent = data.title;
        document.title = data.title + " - Munk's Guide";
        
        let html = `<div class='chapter-header'><h2>${data.title}</h2></div>`;
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
        
        html += `<div class="chapter-nav" style="display:flex; justify-content:space-between; margin-top:60px; padding:40px 0; border-top:2px solid var(--border);">`;
        if (data.prev) html += `<a href="reader.html?ch=${data.prev.slug}" class="landing-links a" style="flex:1; margin-right:10px;">← ${data.prev.title}</a>`;
        else html += '<div style="flex:1;"></div>';
        if (data.next) html += `<a href="reader.html?ch=${data.next.slug}" class="landing-links a" style="flex:1; margin-left:10px;">${data.next.title} →</a>`;
        else html += '<div style="flex:1;"></div>';
        html += `</div>`;
        
        content.innerHTML = html;
        document.querySelector('.main-container').scrollTop = 0;
        updateSelectionState(data.title);
    } catch (e) {
        content.innerHTML = '<div style="padding:100px; text-align:center; color:red;">Failed to retrieve segment data.</div>';
    }
}

function updateSelectionState(title) {
    const isMunkSection = title.includes('Volume') || title === 'Note On The Title';
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

document.addEventListener('DOMContentLoaded', () => {
    init();
    setTheme(localStorage.getItem('munk-theme') || 'light');
});
