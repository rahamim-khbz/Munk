/*
 * js/hm-feedback.js
 * Thumbs up / thumbs down feedback for Homo Mysticus (HM) commentary cards.
 * Submits feedback directly to Cloud Firestore REST API (no heavy SDK needed, completely static).
 * Preserves reader votes in localStorage across sessions.
 */
(function (root) {
    const FIREBASE_CONFIG = {
        apiKey: "AIzaSyDozMoxo2XCVWBtoOsvjUc2Ux9olnpG46c",
        projectId: "munk-guide"
    };

    const STORAGE_KEY = 'munk-hm-feedback';
    const CLIENT_KEY = 'munk-hm-client-id';
    const MAX_COMMENT = 500;
    const REASONS = [
        { id: 'not_relevant', label: 'Not relevant to this chapter' },
        { id: 'too_long', label: 'Too long' },
        { id: 'hard_to_follow', label: 'Hard to follow' },
        { id: 'text_errors', label: 'OCR / text errors' }
    ];
    const REASON_IDS = new Set(REASONS.map(r => r.id));

    function getStorage() {
        try { return root.localStorage || null; } catch (e) { return null; }
    }

    function loadVotes(storage) {
        if (!storage) return {};
        try {
            const parsed = JSON.parse(storage.getItem(STORAGE_KEY) || '{}');
            return (parsed && typeof parsed === 'object') ? parsed : {};
        } catch (e) {
            return {};
        }
    }

    function saveVote(storage, entryId, record) {
        const votes = loadVotes(storage);
        votes[entryId] = record;
        if (storage) {
            try { storage.setItem(STORAGE_KEY, JSON.stringify(votes)); } catch (e) {}
        }
        return votes;
    }

    function getClientId(storage) {
        let id = null;
        try { id = storage && storage.getItem(CLIENT_KEY); } catch (e) { id = null; }
        if (!id) {
            id = (root.crypto && typeof root.crypto.randomUUID === 'function')
                ? root.crypto.randomUUID()
                : 'c-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 10);
            if (storage) {
                try { storage.setItem(CLIENT_KEY, id); } catch (e) {}
            }
        }
        return id;
    }

    function buildPayload({ clientId, slug, entryId, sectionTitle, vote, reasons, comment }) {
        if (vote !== 'up' && vote !== 'down') throw new Error('invalid vote: ' + vote);
        const isDown = vote === 'down';
        return {
            client_id: String(clientId || '').slice(0, 64),
            chapter_slug: String(slug || '').slice(0, 120),
            entry_id: String(entryId || '').slice(0, 200),
            section_title: String(sectionTitle || '').slice(0, 200),
            vote,
            reasons: isDown ? (reasons || []).filter(r => REASON_IDS.has(r)) : [],
            comment: isDown ? String(comment || '').trim().slice(0, MAX_COMMENT) : '',
            ts: new Date().toISOString()
        };
    }

    /**
     * Send feedback to Cloud Firestore using its REST API.
     * Document ID is `doc_<clientId>_<entryId>` so subsequent votes by the same client
     * gracefully update the existing document rather than creating duplicates.
     */
    async function sendFeedback(payload, config = FIREBASE_CONFIG, fetchImpl = root.fetch) {
        if (!config || !config.projectId || typeof fetchImpl !== 'function') return false;

        const safeDocId = ('doc_' + payload.client_id + '_' + payload.entry_id).replace(/[^a-zA-Z0-9_-]/g, '_');
        const url = `https://firestore.googleapis.com/v1/projects/${config.projectId}/databases/(default)/documents/hm_feedback/${encodeURIComponent(safeDocId)}?key=${config.apiKey}`;

        // Transform into Firestore REST JSON format
        const body = {
            fields: {
                client_id: { stringValue: payload.client_id },
                chapter_slug: { stringValue: payload.chapter_slug },
                entry_id: { stringValue: payload.entry_id },
                section_title: { stringValue: payload.section_title },
                vote: { stringValue: payload.vote },
                reasons: {
                    arrayValue: {
                        values: (payload.reasons || []).map(r => ({ stringValue: r }))
                    }
                },
                comment: { stringValue: payload.comment || '' },
                timestamp: { timestampValue: payload.ts }
            }
        };

        try {
            const resp = await fetchImpl(url, {
                method: 'PATCH', // Upsert document
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            return resp.ok;
        } catch (e) {
            console.warn('Feedback submission error:', e);
            return false;
        }
    }

    function escapeAttr(s) {
        return String(s || '')
            .replace(/&/g, '&amp;')
            .replace(/"/g, '&quot;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }

    function renderHmFeedback(entryId, slug, sectionTitle) {
        const existing = loadVotes(getStorage())[entryId] || null;
        const vote = existing ? existing.vote : null;
        const chosen = new Set((existing && existing.reasons) || []);
        const chips = REASONS.map(r => `
            <button type="button" class="hm-reason-chip" data-reason="${r.id}"
                    aria-pressed="${chosen.has(r.id) ? 'true' : 'false'}"
                    onclick="hmToggleReason(this)">${r.label}</button>`).join('');
        const status = vote ? 'Thanks for your feedback!' : '';
        return `
            <div class="hm-feedback" data-entry-id="${escapeAttr(entryId)}" data-slug="${escapeAttr(slug)}" data-section-title="${escapeAttr(sectionTitle || '')}">
                <div class="hm-feedback-row">
                    <span class="hm-feedback-prompt">Was this Homo Mysticus note helpful?</span>
                    <button type="button" class="hm-vote hm-vote-up ${vote === 'up' ? 'active' : ''}" aria-pressed="${vote === 'up' ? 'true' : 'false'}" aria-label="Helpful" title="Helpful" onclick="hmVote(this, 'up')">👍</button>
                    <button type="button" class="hm-vote hm-vote-down ${vote === 'down' ? 'active' : ''}" aria-pressed="${vote === 'down' ? 'true' : 'false'}" aria-label="Not helpful" title="Not helpful" onclick="hmVote(this, 'down')">👎</button>
                    <span class="hm-feedback-status" role="status" aria-live="polite">${status}</span>
                </div>
                <div class="hm-feedback-reasons" ${vote === 'down' ? '' : 'hidden'}>
                    <div class="hm-feedback-reasons-label">What could be better? (optional)</div>
                    <div class="hm-reason-chips">${chips}</div>
                    <textarea class="hm-feedback-comment" maxlength="${MAX_COMMENT}" rows="2" placeholder="Anything else? (optional, anonymous)" aria-label="Additional feedback">${existing && existing.comment ? escapeAttr(existing.comment) : ''}</textarea>
                    <div class="hm-feedback-actions">
                        <button type="button" class="hm-feedback-submit" onclick="hmSubmitReasons(this)">Send</button>
                        <button type="button" class="hm-feedback-skip" onclick="hmCloseReasons(this)">Close</button>
                    </div>
                </div>
            </div>`;
    }

    function readContainer(el) {
        const box = el.closest('.hm-feedback');
        return box ? { box, entryId: box.dataset.entryId, slug: box.dataset.slug, sectionTitle: box.dataset.sectionTitle } : null;
    }

    function record(ctx, vote, reasons, comment) {
        const storage = getStorage();
        const payload = buildPayload({
            clientId: getClientId(storage),
            slug: ctx.slug,
            entryId: ctx.entryId,
            sectionTitle: ctx.sectionTitle,
            vote,
            reasons,
            comment
        });
        saveVote(storage, ctx.entryId, { vote, reasons: payload.reasons, comment: payload.comment, ts: payload.ts });
        sendFeedback(payload);
    }

    function setStatus(box, text) {
        const s = box.querySelector('.hm-feedback-status');
        if (s) s.textContent = text;
    }

    function hmVote(btn, vote) {
        const ctx = readContainer(btn);
        if (!ctx) return;
        const { box } = ctx;
        const upBtn = box.querySelector('.hm-vote-up');
        const downBtn = box.querySelector('.hm-vote-down');

        upBtn.classList.toggle('active', vote === 'up');
        upBtn.setAttribute('aria-pressed', vote === 'up' ? 'true' : 'false');

        downBtn.classList.toggle('active', vote === 'down');
        downBtn.setAttribute('aria-pressed', vote === 'down' ? 'true' : 'false');

        const panel = box.querySelector('.hm-feedback-reasons');
        record(ctx, vote, [], '');
        if (vote === 'down') {
            panel.hidden = false;
            setStatus(box, '');
            const first = panel.querySelector('.hm-reason-chip');
            if (first) first.focus();
        } else {
            panel.hidden = true;
            setStatus(box, 'Thanks for your feedback!');
        }
    }

    function hmToggleReason(chip) {
        const current = chip.getAttribute('aria-pressed') === 'true';
        chip.setAttribute('aria-pressed', current ? 'false' : 'true');
        chip.classList.toggle('active', !current);
    }

    function hmSubmitReasons(btn) {
        const ctx = readContainer(btn);
        if (!ctx) return;
        const reasons = Array.from(ctx.box.querySelectorAll('.hm-reason-chip[aria-pressed="true"]'))
            .map(c => c.dataset.reason);
        const comment = (ctx.box.querySelector('.hm-feedback-comment') || {}).value || '';
        record(ctx, 'down', reasons, comment);
        ctx.box.querySelector('.hm-feedback-reasons').hidden = true;
        setStatus(ctx.box, 'Thanks — this helps improve the notes.');
    }

    function hmCloseReasons(btn) {
        const ctx = readContainer(btn);
        if (!ctx) return;
        ctx.box.querySelector('.hm-feedback-reasons').hidden = true;
        setStatus(ctx.box, 'Thanks for your feedback!');
    }

    const api = {
        FIREBASE_CONFIG, REASONS, MAX_COMMENT,
        loadVotes, saveVote, getClientId, buildPayload, sendFeedback, renderHmFeedback,
        hmVote, hmToggleReason, hmSubmitReasons, hmCloseReasons
    };
    Object.assign(root, { renderHmFeedback, hmVote, hmToggleReason, hmSubmitReasons, hmCloseReasons });
    if (typeof exports !== 'undefined') {
        Object.assign(exports, api);
    }
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    }
})(typeof window !== 'undefined' ? window : (typeof globalThis !== 'undefined' ? globalThis : this));
