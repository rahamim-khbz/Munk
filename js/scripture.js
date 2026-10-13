/**
 * Scriptural Index Interactive UI (js/scripture.js)
 */

function intToHeb(n) {
    if (!n || n <= 0) return '';
    const pairs = [
        [400, 'ת'], [300, 'ש'], [200, 'ר'], [100, 'ק'],
        [90, 'צ'], [80, 'פ'], [70, 'ע'], [60, 'ס'], [50, 'נ'],
        [40, 'מ'], [30, 'ל'], [20, 'כ'], [10, 'י'],
        [9, 'ט'], [8, 'ח'], [7, 'ז'], [6, 'ו'], [5, 'ה'],
        [4, 'ד'], [3, 'ג'], [2, 'ב'], [1, 'א']
    ];
    let rem = n;
    let res = '';
    for (const [val, letter] of pairs) {
        while (rem >= val) {
            res += letter;
            rem -= val;
        }
    }
    return res.replace(/יה/g, 'טו').replace(/יו/g, 'טז');
}

function setTheme(theme) {
    document.documentElement.className = (theme === 'light') ? '' : theme;
    localStorage.setItem('reader-theme', theme);
}

// Global state
let scriptureData = null;
let chaptersMap = {}; // slug -> sort order index

const selBook = document.getElementById('sel-book');
const selChapter = document.getElementById('sel-chapter');
const selVerse = document.getElementById('sel-verse');
const resultsSection = document.getElementById('results');

function initTheme() {
    const savedTheme = localStorage.getItem('reader-theme');
    if (savedTheme) {
        setTheme(savedTheme);
    }
}

async function init() {
    initTheme();

    try {
        const [indexResp, chaptersResp] = await Promise.all([
            fetch('data/scripture_index.json'),
            fetch('data/chapters.json')
        ]);
        scriptureData = await indexResp.json();
        const chaptersList = await chaptersResp.json();
        chaptersList.forEach((ch, idx) => {
            chaptersMap[ch.slug] = idx;
        });

        populateBooks();

        // Check URL params
        const params = new URLSearchParams(window.location.search);
        const b = params.get('b');
        const c = params.get('c');
        const v = params.get('v');

        if (b && scriptureData.books.some(bk => bk.id === b)) {
            selBook.value = b;
            onBookChange(false);
            if (c) {
                selChapter.value = c;
                onChapterChange(false);
                if (v) {
                    selVerse.value = v;
                    render();
                } else {
                    selVerse.value = 'all';
                    render();
                }
            }
        }
    } catch (err) {
        console.error('Failed to load scripture index:', err);
        resultsSection.innerHTML = '<p class="empty-state">Error loading scripture index data.</p>';
    }
}

function populateBooks() {
    selBook.innerHTML = '<option value="">— בחר ספר —</option>';

    const sections = {
        torah: { label: 'תורה', group: document.createElement('optgroup') },
        neviim: { label: 'נביאים', group: document.createElement('optgroup') },
        ketuvim: { label: 'כתובים', group: document.createElement('optgroup') }
    };

    for (const key of Object.keys(sections)) {
        sections[key].group.label = sections[key].label;
    }

    for (const book of scriptureData.books) {
        const opt = document.createElement('option');
        opt.value = book.id;
        opt.textContent = book.he;
        if (sections[book.section]) {
            sections[book.section].group.appendChild(opt);
        } else {
            selBook.appendChild(opt);
        }
    }

    for (const key of Object.keys(sections)) {
        if (sections[key].group.children.length > 0) {
            selBook.appendChild(sections[key].group);
        }
    }
}

function onBookChange(updateUrl = true) {
    const bookId = selBook.value;
    selChapter.innerHTML = '<option value="">— בחר פרק —</option>';
    selVerse.innerHTML = '<option value="">—</option>';
    selChapter.disabled = !bookId;
    selVerse.disabled = true;
    resultsSection.innerHTML = '';

    if (!bookId) {
        if (updateUrl) updateHistory('', '', '');
        return;
    }

    const book = scriptureData.books.find(b => b.id === bookId);
    if (!book || !book.chapters) return;

    const chapters = Object.keys(book.chapters).map(Number).sort((a, b) => a - b);
    for (const ch of chapters) {
        const opt = document.createElement('option');
        opt.value = String(ch);
        opt.textContent = intToHeb(ch);
        selChapter.appendChild(opt);
    }

    if (updateUrl) {
        updateHistory(bookId, '', '');
    }
}

function onChapterChange(updateUrl = true) {
    const bookId = selBook.value;
    const chapStr = selChapter.value;

    selVerse.innerHTML = '';
    resultsSection.innerHTML = '';

    if (!chapStr) {
        selVerse.disabled = true;
        if (updateUrl) updateHistory(bookId, '', '');
        return;
    }

    selVerse.disabled = false;

    const book = scriptureData.books.find(b => b.id === bookId);
    if (!book || !book.chapters || !book.chapters[chapStr]) return;

    // All verses option
    const optAll = document.createElement('option');
    optAll.value = 'all';
    optAll.textContent = 'כל הפסוקים';
    selVerse.appendChild(optAll);

    const verses = Object.keys(book.chapters[chapStr]).map(Number).sort((a, b) => a - b);
    for (const v of verses) {
        const opt = document.createElement('option');
        opt.value = String(v);
        opt.textContent = intToHeb(v);
        selVerse.appendChild(opt);
    }

    selVerse.value = 'all';
    render();

    if (updateUrl) {
        updateHistory(bookId, chapStr, 'all');
    }
}

function onVerseChange() {
    render();
    const bookId = selBook.value;
    const chapStr = selChapter.value;
    const verseStr = selVerse.value;
    updateHistory(bookId, chapStr, verseStr);
}

function updateHistory(b, c, v) {
    const params = new URLSearchParams();
    if (b) params.set('b', b);
    if (c) params.set('c', c);
    if (v) params.set('v', v);
    const qs = params.toString() ? '?' + params.toString() : window.location.pathname;
    history.replaceState(null, '', qs);
}

function sortHits(hits) {
    return hits.slice().sort((a, b) => {
        const ordA = chaptersMap[a.slug] !== undefined ? chaptersMap[a.slug] : 9999;
        const ordB = chaptersMap[b.slug] !== undefined ? chaptersMap[b.slug] : 9999;
        if (ordA !== ordB) return ordA - ordB;
        return (a.row || '').localeCompare(b.row || '');
    });
}

function createHitCard(hit) {
    const a = document.createElement('a');
    a.className = 'hit';
    a.href = `reader.html?ch=${encodeURIComponent(hit.slug)}#row-${encodeURIComponent(hit.row)}`;

    const meta = document.createElement('div');
    meta.className = 'hit-meta';

    const loc = document.createElement('span');
    loc.className = 'hit-loc';
    loc.innerHTML = `${hit.title_en} · <span lang="he" dir="rtl">${hit.title_he}</span>`;

    const badge = document.createElement('span');
    badge.className = `badge ${hit.source === 'note' ? 'badge-note' : 'badge-text'}`;
    badge.textContent = hit.source === 'note' ? "Munk's note" : 'Text';

    meta.appendChild(loc);
    meta.appendChild(badge);
    a.appendChild(meta);

    if (hit.snippet_he) {
        const pHe = document.createElement('p');
        pHe.className = 'snippet-he';
        pHe.dir = 'rtl';
        pHe.lang = 'he';
        pHe.textContent = hit.snippet_he;
        a.appendChild(pHe);
    }

    if (hit.snippet_en) {
        const pEn = document.createElement('p');
        pEn.className = 'snippet-en';
        pEn.textContent = hit.snippet_en;
        a.appendChild(pEn);
    }

    return a;
}

function render() {
    const bookId = selBook.value;
    const chapStr = selChapter.value;
    const verseStr = selVerse.value;

    resultsSection.innerHTML = '';

    if (!bookId || !chapStr || !verseStr) {
        return;
    }

    const book = scriptureData.books.find(b => b.id === bookId);
    if (!book || !book.chapters || !book.chapters[chapStr]) {
        resultsSection.innerHTML = '<p class="empty-state">No passages found.</p>';
        return;
    }

    const chObj = book.chapters[chapStr];

    if (verseStr !== 'all') {
        const rawHits = chObj[verseStr] || [];
        const hits = sortHits(rawHits);

        const total = hits.length;
        const textCount = hits.filter(h => h.source === 'text').length;
        const noteCount = hits.filter(h => h.source === 'note').length;

        const headerDiv = document.createElement('div');
        headerDiv.className = 'results-header';

        const h2 = document.createElement('h2');
        h2.innerHTML = `<span lang="he" dir="rtl">${book.he} ${intToHeb(Number(chapStr))}:${intToHeb(Number(verseStr))}</span> · ${book.en} ${chapStr}:${verseStr}`;
        headerDiv.appendChild(h2);

        const pCount = document.createElement('p');
        pCount.className = 'results-counts';
        pCount.textContent = `cited in ${total} ${total === 1 ? 'passage' : 'passages'} (${textCount} in text, ${noteCount} in Munk's note${noteCount === 1 ? '' : 's'})`;
        headerDiv.appendChild(pCount);

        resultsSection.appendChild(headerDiv);

        if (hits.length === 0) {
            const pEmpty = document.createElement('p');
            pEmpty.className = 'empty-state';
            pEmpty.textContent = 'No citing passages found for this verse.';
            resultsSection.appendChild(pEmpty);
        } else {
            for (const hit of hits) {
                resultsSection.appendChild(createHitCard(hit));
            }
        }
    } else {
        // All verses in chapter
        const verseKeys = Object.keys(chObj).map(Number).sort((a, b) => a - b);
        let allHits = [];
        for (const vk of verseKeys) {
            allHits = allHits.concat(chObj[String(vk)] || []);
        }

        const total = allHits.length;
        const textCount = allHits.filter(h => h.source === 'text').length;
        const noteCount = allHits.filter(h => h.source === 'note').length;

        const headerDiv = document.createElement('div');
        headerDiv.className = 'results-header';

        const h2 = document.createElement('h2');
        h2.innerHTML = `<span lang="he" dir="rtl">${book.he} ${intToHeb(Number(chapStr))}</span> · ${book.en} ${chapStr}`;
        headerDiv.appendChild(h2);

        const pCount = document.createElement('p');
        pCount.className = 'results-counts';
        pCount.textContent = `cited in ${total} ${total === 1 ? 'passage' : 'passages'} (${textCount} in text, ${noteCount} in Munk's note${noteCount === 1 ? '' : 's'})`;
        headerDiv.appendChild(pCount);

        resultsSection.appendChild(headerDiv);

        for (const vk of verseKeys) {
            const hits = sortHits(chObj[String(vk)] || []);
            if (hits.length === 0) continue;

            const subHead = document.createElement('h3');
            subHead.className = 'verse-subheading';
            subHead.dir = 'rtl';
            subHead.lang = 'he';
            subHead.textContent = `פסוק ${intToHeb(vk)} (${book.en} ${chapStr}:${vk})`;
            resultsSection.appendChild(subHead);

            for (const hit of hits) {
                resultsSection.appendChild(createHitCard(hit));
            }
        }
    }
}

// Event listeners
selBook.addEventListener('change', () => onBookChange(true));
selChapter.addEventListener('change', () => onChapterChange(true));
selVerse.addEventListener('change', onVerseChange);

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
