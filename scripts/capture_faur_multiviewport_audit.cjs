const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const PORT = 8092;
const CHROME_PORT = 9226;
const ROOT_DIR = path.resolve(__dirname, '..');
const PROFILE_DIR = path.join(ROOT_DIR, 'scratch/chrome_audit_profile');
const SCREENSHOT_DIR = path.join(ROOT_DIR, 'scratch/faur_multiviewport_audit');
const CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

// 1. Static HTTP Server
function startServer() {
    const mimeTypes = {
        '.html': 'text/html; charset=utf-8',
        '.css': 'text/css; charset=utf-8',
        '.js': 'text/javascript; charset=utf-8',
        '.json': 'application/json; charset=utf-8',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.ico': 'image/x-icon'
    };

    const server = http.createServer((req, res) => {
        let reqPath = decodeURI(req.url.split('?')[0]);
        if (reqPath === '/') reqPath = '/Homo_Mysticus_Sample_Chapters.html';
        const filePath = path.join(ROOT_DIR, reqPath);

        if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
            res.writeHead(404, { 'Content-Type': 'text/plain' });
            res.end('Not Found');
            return;
        }

        const ext = path.extname(filePath).toLowerCase();
        const contentType = mimeTypes[ext] || 'application/octet-stream';
        res.writeHead(200, {
            'Content-Type': contentType,
            'Access-Control-Allow-Origin': '*'
        });
        fs.createReadStream(filePath).pipe(res);
    });

    return new Promise((resolve) => {
        server.listen(PORT, '127.0.0.1', () => {
            console.log(`✓ Audit HTTP Server running at http://127.0.0.1:${PORT}`);
            resolve(server);
        });
    });
}

// 2. Launch Chrome Headless
function launchChrome() {
    if (fs.existsSync(PROFILE_DIR)) {
        try { fs.rmSync(PROFILE_DIR, { recursive: true, force: true }); } catch (e) {}
    }
    fs.mkdirSync(PROFILE_DIR, { recursive: true });

    const chrome = spawn(CHROME_BIN, [
        '--headless=new',
        '--no-sandbox',
        '--disable-gpu',
        '--disable-dev-shm-usage',
        `--remote-debugging-port=${CHROME_PORT}`,
        `--user-data-dir=${PROFILE_DIR}`,
        '--window-size=1440,900',
        'about:blank'
    ], { stdio: 'pipe' });

    chrome.stderr.on('data', d => {
        console.error('[Chrome STDERR]', d.toString());
    });
    chrome.on('exit', (code, sig) => {
        console.error(`[Chrome EXITED] code=${code} sig=${sig}`);
    });

    return chrome;
}

// 3. CDP Client
class CDPClient {
    constructor(wsUrl) {
        this.ws = new WebSocket(wsUrl);
        this.msgId = 1;
        this.callbacks = new Map();

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.id && this.callbacks.has(data.id)) {
                const { resolve, reject } = this.callbacks.get(data.id);
                this.callbacks.delete(data.id);
                if (data.error) reject(data.error);
                else resolve(data.result);
            }
        };
    }

    ready() {
        return new Promise((resolve, reject) => {
            this.ws.onopen = resolve;
            this.ws.onerror = reject;
        });
    }

    send(method, params = {}) {
        return new Promise((resolve, reject) => {
            const id = this.msgId++;
            this.callbacks.set(id, { resolve, reject });
            this.ws.send(JSON.stringify({ id, method, params }));
        });
    }

    async evaluate(expression) {
        const res = await this.send('Runtime.evaluate', {
            expression,
            returnByValue: true,
            awaitPromise: true
        });
        if (res.exceptionDetails) {
            throw new Error(`Eval error: ${JSON.stringify(res.exceptionDetails)}`);
        }
        return res.result ? res.result.value : undefined;
    }

    async captureScreenshot(outputPath) {
        const res = await this.send('Page.captureScreenshot', { format: 'png' });
        fs.writeFileSync(outputPath, Buffer.from(res.data, 'base64'));
        console.log(`  ✓ Saved: ${path.basename(outputPath)} (${(fs.statSync(outputPath).size / 1024).toFixed(1)} KB)`);
    }

    close() {
        this.ws.close();
    }
}

async function sleep(ms) {
    return new Promise(r => setTimeout(r, ms));
}

async function getDebuggerUrl() {
    for (let i = 0; i < 30; i++) {
        try {
            const res = await fetch(`http://127.0.0.1:${CHROME_PORT}/json/list`);
            const targets = await res.json();
            const page = targets.find(t => t.type === 'page');
            if (page && page.webSocketDebuggerUrl) {
                return page.webSocketDebuggerUrl;
            }
        } catch (e) {
            await sleep(250);
        }
    }
    throw new Error('Could not connect to Chrome debugging port');
}

const VIEWPORTS = [
    {
        name: 'desktop',
        width: 1440,
        height: 900,
        deviceScaleFactor: 2,
        mobile: false,
        userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    },
    {
        name: 'ipad_mini',
        width: 768,
        height: 1024,
        deviceScaleFactor: 2,
        mobile: true,
        userAgent: 'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
    },
    {
        name: 'iphone_ios_safari',
        width: 390,
        height: 844,
        deviceScaleFactor: 3,
        mobile: true,
        userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
    }
];

async function run() {
    let server;
    let chrome;
    let cdp;

    try {
        if (!fs.existsSync(SCREENSHOT_DIR)) {
            fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
        }

        server = await startServer();
        chrome = launchChrome();
        const wsUrl = await getDebuggerUrl();
        cdp = new CDPClient(wsUrl);
        await cdp.ready();
        await cdp.send('Page.enable');
        await cdp.send('Runtime.enable');

        console.log(`\n======================================================================`);
        console.log(`Multi-Viewport José Faur (Homo Mysticus) Interactive CDP Audit`);
        console.log(`======================================================================\n`);

        for (const vp of VIEWPORTS) {
            console.log(`\n▶ Auditing Viewport: ${vp.name.toUpperCase()} (${vp.width}x${vp.height}, Scale: ${vp.deviceScaleFactor})`);

            await cdp.send('Emulation.setDeviceMetricsOverride', {
                width: vp.width,
                height: vp.height,
                deviceScaleFactor: vp.deviceScaleFactor,
                mobile: vp.mobile
            });
            await cdp.send('Emulation.setTouchEmulationEnabled', {
                enabled: vp.mobile
            });
            await cdp.send('Network.setUserAgentOverride', {
                userAgent: vp.userAgent
            });

            // 1. Load Homo_Mysticus_Sample_Chapters.html (Part 1 - Chapter 5 initial collapsed)
            await cdp.send('Page.navigate', { url: `http://127.0.0.1:${PORT}/Homo_Mysticus_Sample_Chapters.html` });
            await sleep(1500);

            const initialAudit = await cdp.evaluate(`(() => {
                const btn = document.getElementById('btn-chapter-faur');
                const h2 = document.querySelector('.chapter-header h2');
                const topBox = document.getElementById('faur-top-box');
                const row0 = document.querySelector('.parallel-row');

                if (!btn || !h2 || !topBox || !row0) {
                    return { error: 'Missing core elements in initial state' };
                }

                const btnRect = btn.getBoundingClientRect();
                const h2Rect = h2.getBoundingClientRect();
                const btnCenterY = btnRect.top + btnRect.height / 2;
                const h2CenterY = h2Rect.top + h2Rect.height / 2;
                const deltaY = Math.abs(btnCenterY - h2CenterY);
                const isInline = deltaY < 24; // within baseline tolerance
                const heightOk = btnRect.height >= 40;
                const isCollapsed = window.getComputedStyle(topBox).display === 'none';

                return {
                    isInline,
                    deltaY,
                    btnHeight: btnRect.height,
                    heightOk,
                    isCollapsed,
                    row0Top: row0.getBoundingClientRect().top
                };
            })()`);

            if (initialAudit.error) throw new Error(`[${vp.name}] ${initialAudit.error}`);
            if (!initialAudit.isCollapsed) throw new Error(`[${vp.name}] Top box should be collapsed initially`);

            await cdp.captureScreenshot(path.join(SCREENSHOT_DIR, `01_${vp.name}_ch5_collapsed.png`));

            // 2. Click inline ❦ HM button (#btn-chapter-faur) to expand
            const expandAudit = await cdp.evaluate(`(() => {
                const btn = document.getElementById('btn-chapter-faur');
                const row0Before = document.querySelector('.parallel-row').getBoundingClientRect().top;
                btn.click();
                const topBox = document.getElementById('faur-top-box');
                const isDisplayBlock = window.getComputedStyle(topBox).display === 'block';
                const row0After = document.querySelector('.parallel-row').getBoundingClientRect().top;
                const pushDownDelta = row0After - row0Before;

                const firstCit = topBox.querySelector('.faur-subsection-citation');
                const citText = firstCit ? firstCit.textContent.trim() : '';
                const hasPageRange = topBox.innerHTML.includes('Homo Mysticus, pp.');
                const hasReadLink = Boolean(topBox.querySelector('.faur-read-link'));
                const hasFeedback = topBox.innerHTML.includes('Was this Homo Mysticus note helpful?');

                return {
                    isDisplayBlock,
                    pushDownDelta,
                    citText,
                    hasPageRange,
                    hasReadLink,
                    hasFeedback
                };
            })()`);

            await sleep(400);
            if (!expandAudit.isDisplayBlock) throw new Error(`[${vp.name}] Top box did not expand`);
            if (expandAudit.pushDownDelta < 150) throw new Error(`[${vp.name}] Push-down delta too small: ${expandAudit.pushDownDelta}`);
            if (!expandAudit.citText.includes('Homo Mysticus, Chapter 3 - The Fault with Aristotle')) {
                throw new Error(`[${vp.name}] Unexpected citation: ${expandAudit.citText}`);
            }
            if (expandAudit.hasReadLink) {
                throw new Error(`[${vp.name}] Found removed .faur-read-link`);
            }
            if (expandAudit.hasFeedback) {
                throw new Error(`[${vp.name}] Found removed feedback widget`);
            }
            if (expandAudit.hasPageRange) throw new Error(`[${vp.name}] Found deprecated page range "Homo Mysticus, pp."`);

            await cdp.captureScreenshot(path.join(SCREENSHOT_DIR, `02_${vp.name}_ch5_expanded_sub1.png`));

            // 3. Verify active subsection (Homo Mysticus, Chapter 3 - The Fault with Aristotle) and pure Faur quote (no synthetic key terms)
            const subAudit = await cdp.evaluate(`(() => {
                const openBody = document.querySelector('.faur-subsection-card.open .faur-subsection-body') ||
                                 document.querySelector('.faur-subsection-body');
                const contentHtml = openBody ? openBody.innerHTML : '';
                const activeCit = document.querySelector('.faur-subsection-card.open .faur-subsection-citation');
                const citText = activeCit ? activeCit.textContent.trim() : '';
                const hasRayyis = contentHtml.includes('rayyis');
                const hasKeyTermsBar = contentHtml.includes('faur-key-terms-bar') || contentHtml.includes('Key Term:');

                return {
                    citText,
                    hasRayyis,
                    hasKeyTermsBar
                };
            })()`);

            await sleep(300);
            if (!subAudit.citText.includes('Chapter 3 - The Fault with Aristotle')) {
                throw new Error(`[${vp.name}] Active subsection citation mismatch: ${subAudit.citText}`);
            }
            if (!subAudit.hasRayyis) {
                throw new Error(`[${vp.name}] Missing Faur quote text in active subsection`);
            }
            if (subAudit.hasKeyTermsBar) {
                throw new Error(`[${vp.name}] Found synthetic key terms bar in active subsection`);
            }

            await cdp.captureScreenshot(path.join(SCREENSHOT_DIR, `03_${vp.name}_ch5_sub3_rayyis.png`));

            // 4. Click a footnote callout inside #faur-top-box (targeting note 94: Studies in the Mishne Tora)
            const fnAudit = await cdp.evaluate(`(async () => {
                const fnRefs = Array.from(document.querySelectorAll('.faur-subsection-card.open .faur-fn-ref'));
                const targetRef = fnRefs.find(el => el.getAttribute('onclick') && el.getAttribute('onclick').includes('fn_part-three_94')) || fnRefs[0];
                if (targetRef) {
                    targetRef.click();
                } else {
                    await showFn('fn.faur.part-1---chapter-5.fn_part-three_94');
                }
                const panel = document.getElementById('fn-panel');
                const body = document.getElementById('fn-panel-body');
                const isOpen = panel.classList.contains('open');
                const hasFaurLabel = body.innerHTML.includes("Faur's Note");
                const hasNoteContent = body.innerHTML.includes("Studies in the Mishne Tora");

                return {
                    isOpen,
                    hasFaurLabel,
                    hasNoteContent
                };
            })()`);

            await sleep(400);
            if (!fnAudit.isOpen || !fnAudit.hasFaurLabel || !fnAudit.hasNoteContent) {
                throw new Error(`[${vp.name}] Footnote panel failed to open with Faur label and Studies in the Mishne Tora`);
            }

            await cdp.captureScreenshot(path.join(SCREENSHOT_DIR, `04_${vp.name}_ch5_footnote_open.png`));

            // Close footnote panel
            await cdp.evaluate(`closeFnPanel()`);
            await sleep(200);

            // 5. Themes (Sepia & Dark)
            await cdp.evaluate(`setTheme('sepia')`);
            await sleep(300);
            await cdp.captureScreenshot(path.join(SCREENSHOT_DIR, `05_${vp.name}_ch5_sepia.png`));

            await cdp.evaluate(`setTheme('dark')`);
            await sleep(300);
            await cdp.captureScreenshot(path.join(SCREENSHOT_DIR, `06_${vp.name}_ch5_dark.png`));

            await cdp.evaluate(`setTheme('light')`);
            await sleep(200);

            // 6. Switch sample chapter to Guide I:71
            const ch71Audit = await cdp.evaluate(`(async () => {
                await switchSampleChapter('part-1---chapter-71');
                const btn = document.getElementById('btn-chapter-faur');
                btn.click();
                const topBox = document.getElementById('faur-top-box');
                const cit = topBox.querySelector('.faur-subsection-citation');
                return {
                    citText: cit ? cit.textContent.trim() : ''
                };
            })()`);

            await sleep(500);
            if (!ch71Audit.citText.includes('Homo Mysticus, Chapter 3 - In Search of the Ultimate Reality')) {
                throw new Error(`[${vp.name}] Chapter 71 citation mismatch: ${ch71Audit.citText}`);
            }

            await cdp.captureScreenshot(path.join(SCREENSHOT_DIR, `07_${vp.name}_ch71_expanded.png`));

            // 7. Full Reader navigation (reader.html?ch=part-1---chapter-5)
            await cdp.send('Page.navigate', { url: `http://127.0.0.1:${PORT}/reader.html?ch=part-1---chapter-5` });
            await sleep(1500);

            const readerAudit = await cdp.evaluate(`(() => {
                const btn = document.getElementById('btn-chapter-faur');
                const row0Before = document.querySelector('.parallel-row').getBoundingClientRect().top;
                btn.click();
                const row0After = document.querySelector('.parallel-row').getBoundingClientRect().top;
                const pushDownDelta = row0After - row0Before;
                const hasOverflow = document.documentElement.scrollWidth > window.innerWidth;

                return {
                    pushDownDelta,
                    hasOverflow
                };
            })()`);

            await sleep(400);
            if (readerAudit.pushDownDelta < 150) {
                throw new Error(`[${vp.name}] reader.html push down delta too small: ${readerAudit.pushDownDelta}`);
            }
            if (readerAudit.hasOverflow) {
                throw new Error(`[${vp.name}] reader.html has horizontal overflow on ${vp.name}`);
            }

            await cdp.captureScreenshot(path.join(SCREENSHOT_DIR, `08_${vp.name}_reader_ch5_expanded.png`));

            console.log(`✓ [${vp.name.toUpperCase()}] 8 inspection checkpoints verified completely.`);
        }

        console.log(`\n======================================================================`);
        console.log(`ALL MULTI-VIEWPORT AUDIT CHECKS PASSED (24 Screenshots Generated)`);
        console.log(`======================================================================\n`);

    } catch (e) {
        console.error(`\n✗ AUDIT FAILURE:`, e);
        process.exitCode = 1;
    } finally {
        if (cdp) cdp.close();
        if (chrome) chrome.kill();
        if (server) server.close();
    }
}

run();
