# Munk Viewer PWA Implementation Plan

> **For Antigravity:** REQUIRED SUB-SKILL: Load executing-plans to implement this plan task-by-task.

**Goal:** Transform the static Munk Reader into a lightning-fast, offline-capable Progressive Web App (PWA) hosted on GitHub Pages, featuring Stale-While-Revalidate caching for seamless updates and integrated GitHub Issues feedback links.

**Architecture:** We introduce a `manifest.json` for standalone mobile app installation, a custom Service Worker (`sw.js`) implementing runtime chapter caching and background revalidation, and template modifications in `build_full_viewer.py` to wire up the registration, update notifications, and the "Propose an Edit" footer links.

**Tech Stack:** Vanilla JS Service Workers, HTML5/CSS3, Python static generation.

---

### Task 1: App Shell Manifest

**Files:**
- Create: `manifest.json`

**Step 1: Write `manifest.json`**
```json
{
  "name": "Dalalat al-Ha'irin Reader",
  "short_name": "Munk Reader",
  "description": "Parallel scholarly viewer for Munk's translation and Makbili's Hebrew edition of the Guide for the Perplexed.",
  "start_url": "./fulltext.html",
  "display": "standalone",
  "background_color": "#F2EBE1",
  "theme_color": "#8C1D04",
  "icons": [
    {
      "src": "https://raw.githubusercontent.com/google/material-design-icons/master/png/action/book/materialicons/24dp/2x/baseline_book_black_24dp.png",
      "sizes": "48x48",
      "type": "image/png"
    }
  ]
}
```
*(Note: Using a placeholder inline icon URL for immediate standalone compliance without binary bloat).*

**Step 2: Commit**
```bash
git add manifest.json
git commit -m "feat: add PWA manifest.json for standalone mobile installation"
```

---

### Task 2: Service Worker (`sw.js`)

**Files:**
- Create: `sw.js`

**Step 1: Write Service Worker implementation**
```javascript
const CACHE_NAME = 'munk-reader-v1';
const CORE_ASSETS = [
  './viewer_styles.css',
  './manifest.json'
];

// Install Event: Cache Core Assets
self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(CORE_ASSETS))
  );
});

// Activate Event: Cleanup Old Caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(name => {
          if (name !== CACHE_NAME) return caches.delete(name);
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch Event: Stale-While-Revalidate for HTML pages
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);
  // Only intercept local requests or static viewer files
  if (!url.pathname.endsWith('.html') && !url.pathname.endsWith('.css') && !url.pathname.endsWith('.json')) return;

  event.respondWith(
    caches.match(event.request).then(cachedResponse => {
      const fetchPromise = fetch(event.request).then(networkResponse => {
        // Cache valid responses silently in the background
        if (networkResponse && networkResponse.status === 200) {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, responseToCache));
        }
        return networkResponse;
      }).catch(() => { /* Ignore network errors silently for pure offline usage */ });

      // Return cached instantly if available, otherwise wait for network
      return cachedResponse || fetchPromise;
    })
  );
});
```

**Step 2: Commit**
```bash
git add sw.js
git commit -m "feat: implement sw.js service worker with Stale-While-Revalidate caching"
```

---

### Task 3: Viewer Template Wiring

**Files:**
- Modify: `build_full_viewer.py`

**Step 1: Inject template code**
Update `render_html` in `build_full_viewer.py` to insert:
1. `<link rel="manifest" href="../manifest.json">` inside `<head>`.
2. Service Worker registration script before `</body>`.
3. Option A footer div: `<div class="feedback-footer"><a href="https://github.com/rayhabbaz/Munk-Guide/issues/new?title=Correction:%20{display_title}" target="_blank">Propose an Edit on GitHub</a></div>`.

**Step 2: Run build script to verify generation**
Run: `python3 build_full_viewer.py`
Expected: `Success! Multi-page viewer generated in "viewer/" directory.`

**Step 3: Commit**
```bash
git add build_full_viewer.py
git commit -m "feat: integrate PWA manifest, service worker registration, and GitHub feedback link into viewer template"
```
