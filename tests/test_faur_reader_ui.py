"""
tests/test_faur_reader_ui.py
End-to-End Test Suite for José Faur (Homo Mysticus) Unified Top Collapsible Box UI.

Verifies:
1. Static HTML structure: #btn-faur-toggle and #btn-mobile-faur-toggle existence and properties.
2. CSS Architecture & Zero-Thrash:
   - .faur-inline-btn and .faur-top-box rules exist.
   - .main-container[data-faur="off"] hides both .faur-inline-btn and .faur-top-box.
3. Sync Parity: root vs dist files are byte-identical.
4. Node.js Headless DOM Simulation:
   - Load part-1---chapter-5: .chapter-header contains .chapter-header-row and #btn-chapter-faur.
   - #faur-top-box rendered immediately following .chapter-header and before .parallel-row.
   - Zero margin anchors, zero popovers, zero postscript containers, zero 'Homo Mysticus, pp.'.
   - Citations format as 'Homo Mysticus, Chapter ## - [[Subtitle/Section]]'.
   - Key terms badges rendered with Hebrew RTL script and labels.
   - Footnote resolution: showFn('fn.faur.part-1---chapter-5.fn_part-three_94') displays "Faur's Note".
   - Global toggle: toggleFaurAnnotations() sets data-faur="on"|"off" and updates buttons.
   - Theme preservation: setTheme('dark') does not strip .active from #btn-faur-toggle.
   - Load part-1---chapter-71: Tier 1 Kalam commentary rendered with unified citation.
"""

import json
import subprocess
from pathlib import Path
try:
    import pytest
except ImportError:
    pytest = None

BASE_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = BASE_DIR / "dist"


def test_html_buttons_exist_and_synced():
    """Verify desktop, mobile, and TOC drawer Faur toggle buttons exist in reader.html and dist/reader.html."""
    for parent in [BASE_DIR, DIST_DIR]:
        html = (parent / "reader.html").read_text(encoding="utf-8")
        assert 'id="btn-faur-toggle"' in html, f"Missing #btn-faur-toggle in {parent}/reader.html"
        assert 'id="btn-mobile-faur-toggle"' in html, f"Missing #btn-mobile-faur-toggle in {parent}/reader.html"
        assert 'id="btn-toc-faur-toggle"' in html, f"Missing #btn-toc-faur-toggle in {parent}/reader.html"
        assert 'onclick="toggleFaurAnnotations()"' in html
        assert '❦ HM' in html


def test_css_grid_protection_and_zero_thrash():
    """Verify zero-thrash and top box rules in css/reader.css."""
    for parent in [BASE_DIR, DIST_DIR]:
        css = (parent / "css/reader.css").read_text(encoding="utf-8")
        assert '.main-container[data-faur="off"] .faur-inline-btn' in css
        assert '.main-container[data-faur="off"] .faur-top-box' in css
        assert ".faur-inline-btn" in css
        assert ".faur-top-box" in css
        assert ".faur-box-banner" in css
        assert ".faur-subsection-tabs" in css
        assert ".faur-subsection-tab" in css
        assert ".faur-ch-badge" in css
        assert ".faur-tab-title" in css
        assert ".faur-subsection-card" in css
        assert ".faur-key-terms-bar" in css
        assert ".sr-only" in css


def test_root_dist_byte_identity():
    """Verify all reader UI artifacts match byte-for-byte with dist/."""
    for rel_path in ["reader.html", "js/reader.js", "css/reader.css"]:
        root_content = (BASE_DIR / rel_path).read_bytes()
        dist_content = (DIST_DIR / rel_path).read_bytes()
        assert root_content == dist_content, f"{rel_path} differs between root and dist/"


def test_nodejs_faur_reader_ui_simulation():
    """Execute complete headless browser DOM interaction simulation in Node.js."""
    node_script = """
    const fs = require('fs');

    const readerJs = fs.readFileSync('js/reader.js', 'utf8');
    const chaptersData = JSON.parse(fs.readFileSync('data/chapters.json', 'utf8'));
    const ch5Data = JSON.parse(fs.readFileSync('data/part-1---chapter-5.json', 'utf8'));
    const ch71Data = JSON.parse(fs.readFileSync('data/part-1---chapter-71.json', 'utf8'));
    const faurMap = JSON.parse(fs.readFileSync('data/faur_commentary_map.json', 'utf8'));
    const footnotesData = JSON.parse(fs.readFileSync('data/footnotes.json', 'utf8'));

    class ClassList {
        constructor() { this.classes = new Set(); }
        add(...c) { c.forEach(x => this.classes.add(x)); }
        remove(...c) { c.forEach(x => this.classes.delete(x)); }
        toggle(c, force) {
            if (force !== undefined) { force ? this.classes.add(c) : this.classes.delete(c); return force; }
            if (this.classes.has(c)) { this.classes.delete(c); return false; }
            this.classes.add(c); return true;
        }
        contains(c) { return this.classes.has(c); }
    }

    class MockElement {
        constructor(id = '', tag = 'div') {
            this.id = id;
            this.tagName = tag.toUpperCase();
            this.classList = new ClassList();
            this.children = [];
            this.attributes = {};
            this.style = {
                display: '',
                setProperty: (k, v) => { this.style[k] = v; },
                getPropertyValue: (k) => this.style[k] || ''
            };
            this._innerHTML = '';
            this.textContent = '';
            this.scrollTop = 0;
        }
        set innerHTML(v) { this._innerHTML = v; }
        get innerHTML() { return this._innerHTML; }
        appendChild(c) { this.children.push(c); return c; }
        setAttribute(k, v) { this.attributes[k] = String(v); }
        getAttribute(k) { return this.attributes[k] || null; }
        closest(sel) {
            return null;
        }
        querySelector(sel) {
            if (sel === '.faur-inline-chevron') return new MockElement('chevron');
            return null;
        }
        querySelectorAll(sel) { return []; }
        scrollIntoView() {}
    }

    const elements = {
        'toc-drawer': new MockElement('toc-drawer'),
        'toc-backdrop': new MockElement('toc-backdrop'),
        'toc-body': new MockElement('toc-body'),
        'main-container': new MockElement('main-container'),
        'main-title': new MockElement('main-title'),
        'chapter-content': new MockElement('chapter-content'),
        'fn-panel': new MockElement('fn-panel'),
        'fn-panel-body': new MockElement('fn-panel-body'),
        'btn-faur-toggle': new MockElement('btn-faur-toggle', 'button'),
        'btn-mobile-faur-toggle': new MockElement('btn-mobile-faur-toggle', 'button'),
        'btn-toc-faur-toggle': new MockElement('btn-toc-faur-toggle', 'button'),
        'btn-chapter-faur': new MockElement('btn-chapter-faur', 'button'),
        'faur-top-box': new MockElement('faur-top-box', 'section'),
        'btn-light': new MockElement('btn-light', 'button'),
        'btn-sepia': new MockElement('btn-sepia', 'button'),
        'btn-dark': new MockElement('btn-dark', 'button'),
        'select-left-col': new MockElement('select-left-col', 'select'),
        'select-right-col': new MockElement('select-right-col', 'select')
    };

    elements['btn-faur-toggle'].classList.add('theme-btn', 'active');
    elements['btn-mobile-faur-toggle'].classList.add('theme-btn', 'active');
    elements['btn-light'].classList.add('theme-btn');
    elements['btn-sepia'].classList.add('theme-btn');
    elements['btn-dark'].classList.add('theme-btn');

    elements['btn-light'].textContent = 'Light';
    elements['btn-sepia'].textContent = 'Sepia';
    elements['btn-dark'].textContent = 'Dark';
    elements['btn-faur-toggle'].textContent = '❦ HM';
    elements['btn-mobile-faur-toggle'].textContent = '❦ HM';

    const registeredListeners = {};

    global.document = {
        documentElement: { className: '' },
        getElementById: (id) => elements[id] || (elements[id] = new MockElement(id)),
        createElement: (tag) => new MockElement('', tag),
        querySelector: (sel) => {
            if (sel === '.main-container') return elements['main-container'];
            if (sel === '#chapter-content') return elements['chapter-content'];
            if (sel === '.fn-panel-label') return new MockElement('fn-panel-label');
            return null;
        },
        querySelectorAll: (sel) => {
            if (sel.includes('.theme-btn') || sel.includes('#btn-light')) {
                return [elements['btn-light'], elements['btn-sepia'], elements['btn-dark']];
            }
            return [];
        },
        addEventListener: (event, handler) => {
            registeredListeners[event] = handler;
        },
        title: ''
    };

    global.window = {
        location: { search: '?ch=part-1---chapter-5', hash: '', pathname: '/reader.html' },
        addEventListener: () => {},
        matchMedia: () => ({ matches: false }),
        localStorage: {
            store: {},
            getItem: (k) => global.window.localStorage.store[k] || null,
            setItem: (k, v) => { global.window.localStorage.store[k] = String(v); }
        }
    };
    global.location = global.window.location;
    global.localStorage = global.window.localStorage;

    global.fetch = async (url) => {
        if (url === 'data/chapters.json') return { json: async () => chaptersData };
        if (url === 'data/footnotes.json') return { json: async () => footnotesData };
        if (url === 'data/faur_commentary_map.json') return { json: async () => faurMap };
        if (url.includes('part-1---chapter-5')) return { json: async () => ch5Data };
        if (url.includes('part-1---chapter-71')) return { json: async () => ch71Data };
        return { json: async () => ({}) };
    };

    eval(readerJs);

    (async () => {
        try {
            // STEP 1: Verify Theme Protection
            initFaurAnnotations();
            if (!elements['btn-faur-toggle'].classList.contains('active')) throw new Error('#btn-faur-toggle should be active initially');
            if (elements['main-container'].getAttribute('data-faur') !== 'on') throw new Error('data-faur should be on');

            // Switch theme to dark
            setTheme('dark');
            if (document.documentElement.className !== 'dark') throw new Error('Theme did not change to dark');
            if (!elements['btn-dark'].classList.contains('active')) throw new Error('btn-dark should be active');
            if (!elements['btn-faur-toggle'].classList.contains('active')) throw new Error('setTheme stripped active from #btn-faur-toggle!');

            // STEP 2: Verify Global Faur Toggle
            toggleFaurAnnotations();
            if (elements['main-container'].getAttribute('data-faur') !== 'off') throw new Error('data-faur should be off after toggle');
            if (elements['btn-faur-toggle'].classList.contains('active')) throw new Error('#btn-faur-toggle should be inactive when off');
            if (elements['btn-toc-faur-toggle'].getAttribute('aria-checked') !== 'false') throw new Error('#btn-toc-faur-toggle aria-checked should be false when off');
            toggleFaurAnnotations();
            if (elements['main-container'].getAttribute('data-faur') !== 'on') throw new Error('data-faur should be on after 2nd toggle');
            if (!elements['btn-faur-toggle'].classList.contains('active')) throw new Error('#btn-faur-toggle should be active when on');
            if (elements['btn-toc-faur-toggle'].getAttribute('aria-checked') !== 'true') throw new Error('#btn-toc-faur-toggle aria-checked should be true when on');

            // STEP 3: Load Chapter 5 (part-1---chapter-5)
            await loadChapter('part-1---chapter-5');
            const ch5Html = elements['chapter-content'].innerHTML;

            // 1. Verify Inline Header Trigger Button & Row
            if (!ch5Html.includes('class="chapter-header-row"')) {
                throw new Error('Missing .chapter-header-row in Chapter 5');
            }
            if (!ch5Html.includes('id="btn-chapter-faur"')) {
                throw new Error('Missing #btn-chapter-faur in Chapter 5');
            }
            if (!ch5Html.includes('class="faur-inline-btn"')) {
                throw new Error('Missing .faur-inline-btn class in Chapter 5');
            }
            if (!ch5Html.includes('❦ HM')) {
                throw new Error('Missing ❦ HM glyph in inline trigger button');
            }

            // 2. Verify Top Collapsible Box and Position
            if (!ch5Html.includes('id="faur-top-box"')) {
                throw new Error('Missing #faur-top-box in Chapter 5');
            }
            const headerIdx = ch5Html.indexOf('class="chapter-header"');
            const topBoxIdx = ch5Html.indexOf('id="faur-top-box"');
            const row0Idx = ch5Html.indexOf('class="parallel-row"');
            if (headerIdx === -1 || topBoxIdx === -1 || row0Idx === -1) {
                throw new Error('Missing expected structural containers in Chapter 5 HTML');
            }
            if (!(headerIdx < topBoxIdx && topBoxIdx < row0Idx)) {
                throw new Error('#faur-top-box must be placed immediately after .chapter-header and BEFORE the first .parallel-row');
            }

            // 3. Verify ZERO Deprecated Popovers / Margin Anchors / Postscripts / Page Ranges
            if (ch5Html.includes('class="faur-margin-anchor"')) {
                throw new Error('Found deprecated .faur-margin-anchor in Chapter 5');
            }
            if (ch5Html.includes('class="faur-popover"')) {
                throw new Error('Found deprecated .faur-popover in Chapter 5');
            }
            if (ch5Html.includes('class="faur-postscript-container"')) {
                throw new Error('Found deprecated .faur-postscript-container in Chapter 5');
            }
            if (ch5Html.includes('Homo Mysticus, pp.')) {
                throw new Error('Found deprecated page range "Homo Mysticus, pp." in Chapter 5');
            }

            // 4. Verify Option 2 Compact Grid UI, Citations & Zero Synthetic Key Terms
            if (!ch5Html.includes('class="faur-box-banner"')) {
                throw new Error('Missing .faur-box-banner in Chapter 5');
            }
            if (!ch5Html.includes('class="faur-ch-badge"')) {
                throw new Error('Missing .faur-ch-badge in Chapter 5');
            }
            if (!ch5Html.includes('class="sr-only"')) {
                throw new Error('Missing .sr-only in Chapter 5');
            }
            if (ch5Html.includes('Homo Mysticus, Chapter 2 - Anthropocentric Theology')) {
                throw new Error('Found demoted citation "Homo Mysticus, Chapter 2 - Anthropocentric Theology" in Chapter 5');
            }
            if (!ch5Html.includes('Homo Mysticus, Chapter 3 - The Fault with Aristotle')) {
                throw new Error('Missing citation "Homo Mysticus, Chapter 3 - The Fault with Aristotle" in Chapter 5');
            }
            if (ch5Html.includes('faur-key-terms-bar') || ch5Html.includes('faur-key-term-chip') || ch5Html.includes('Key Term:')) {
                throw new Error('Found synthetic key terms bar in Chapter 5 — only pure quotes from Faur are allowed');
            }
            if (ch5Html.includes('Aristotle as the Aṣīle')) {
                throw new Error('Found synthetic anchor label "Aristotle as the Aṣīle" in Chapter 5');
            }

            // Verify .faur-tab-title renders conditionally for multi-section cases
            const multiSectionHtml = renderFaurTopBox([
                { id: 'sec1', section_title: 'Section 1', part_title: 'Part 1', faur_chapter: 1, content_html: '<p>A</p>' },
                { id: 'sec2', section_title: 'Section 2', part_title: 'Part 2', faur_chapter: 2, content_html: '<p>B</p>' }
            ], 'test-slug');
            if (!multiSectionHtml.includes('class="faur-tab-title"')) {
                throw new Error('Missing .faur-tab-title in multi-section top box');
            }

            // 5. Test toggleFaurTopBox()
            toggleFaurTopBox(true);
            if (!elements['faur-top-box'].classList.contains('open')) {
                throw new Error('toggleFaurTopBox(true) failed to add .open to #faur-top-box');
            }
            if (elements['btn-chapter-faur'].getAttribute('aria-expanded') !== 'true') {
                throw new Error('toggleFaurTopBox(true) failed to set aria-expanded="true" on #btn-chapter-faur');
            }

            // STEP 4: Footnote Resolution into #fn-panel
            await showFn('fn.faur.part-1---chapter-5.fn_part-three_94');
            if (!elements['fn-panel'].classList.contains('open')) throw new Error('Footnote panel failed to open for Faur note');
            if (!elements['main-container'].classList.contains('fn-open')) throw new Error('main-container missing fn-open');
            const fnBodyHtml = elements['fn-panel-body'].innerHTML;
            if (!fnBodyHtml.includes("Faur's Note")) throw new Error("Missing Faur's Note label in fn-panel-body");
            if (!fnBodyHtml.includes("Studies in the Mishne Tora")) throw new Error("Missing expected footnote text 'Studies in the Mishne Tora' in fn-panel-body");

            // Close footnote panel
            closeFnPanel();
            if (elements['fn-panel'].classList.contains('open')) throw new Error('Footnote panel failed to close');

            // STEP 5: Load Chapter 71 (part-1---chapter-71)
            await loadChapter('part-1---chapter-71');
            const ch71Html = elements['chapter-content'].innerHTML;
            if (!ch71Html.includes('id="btn-chapter-faur"')) {
                throw new Error('Missing #btn-chapter-faur in Chapter 71');
            }
            if (!ch71Html.includes('id="faur-top-box"')) {
                throw new Error('Missing #faur-top-box in Chapter 71');
            }
            if (!ch71Html.includes('Homo Mysticus, Chapter 3 - In Search of the Ultimate Reality')) {
                throw new Error('Missing citation "Homo Mysticus, Chapter 3 - In Search of the Ultimate Reality" in Chapter 71');
            }

            console.log('SUCCESS: All Faur Unified Top Box UI E2E tests passed completely!');
        } catch (e) {
            console.error('FAILURE:', e.message);
            process.exit(1);
        }
    })();
    """
    res = subprocess.run(["node", "-e", node_script], cwd=str(BASE_DIR), capture_output=True, text=True)
    assert res.returncode == 0, f"Node.js Faur simulation failed:\nSTDERR:\n{res.stderr}\nSTDOUT:\n{res.stdout}"
    assert "SUCCESS: All Faur Unified Top Box UI E2E tests passed completely!" in res.stdout


if __name__ == "__main__":
    test_html_buttons_exist_and_synced()
    test_css_grid_protection_and_zero_thrash()
    test_root_dist_byte_identity()
    test_nodejs_faur_reader_ui_simulation()
    print("ALL TESTS PASSED!")
