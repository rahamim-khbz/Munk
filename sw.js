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
