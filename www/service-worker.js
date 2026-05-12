/**
 * SAMUDRA AI — Service Worker
 * Enables offline-first functionality for Maharashtra fishermen.
 * Strategy:
 *   - App shell (HTML/JS/CSS): Cache-first → instant load even at sea
 *   - PFZ / ocean data: Network-first → fresh data when online, cached fallback offline
 *   - External CDN (Leaflet, fonts): Cache-first with long TTL
 */

const CACHE_NAME    = 'samudra-v2';
const DATA_CACHE    = 'samudra-data-v2';
const OFFLINE_URL   = '/';

// App shell — cache on install
const SHELL_ASSETS = [
  '/',
  '/manifest.json',
];

// Data endpoints — network-first, cache fallback (work offline)
const DATA_URLS = [
  '/pfz_data.geojson',
  '/wind_data.json',
  '/current_data.json',
  '/wave_data.json',
  '/sst_data.json',
  '/chl_data.json',
];

// API endpoints to cache for offline use
const CACHEABLE_APIS = [
  '/api/pfz/live',
  '/api/forecast/6day',
  '/api/incois/advisory',
  '/api/samudra/coordinates',
  '/api/health',
];

// ── Install: pre-cache app shell ──────────────────────────────────────────────
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(SHELL_ASSETS))
      .then(() => self.skipWaiting())
  );
});

// ── Activate: delete old caches ───────────────────────────────────────────────
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME && k !== DATA_CACHE)
            .map(k => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

// ── Fetch: routing strategy ───────────────────────────────────────────────────
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Skip non-GET and browser-extension requests
  if (event.request.method !== 'GET') return;
  if (!url.protocol.startsWith('http')) return;

  const path = url.pathname;

  // API endpoints: network-first with cache for offline
  if (path.startsWith('/api/')) {
    const isCacheable = CACHEABLE_APIS.some(u => path.startsWith(u));
    event.respondWith(networkFirst(event.request, DATA_CACHE, isCacheable ? 10000 : 8000));
    return;
  }

  // Data JSON files: network-first, cache fallback (work offline)
  if (DATA_URLS.some(u => path === u || path.startsWith(u + '?'))) {
    event.respondWith(networkFirst(event.request, DATA_CACHE, 10000));
    return;
  }

  // External CDN (Leaflet, Google Fonts): cache-first
  if (!url.origin.includes(self.location.hostname)) {
    event.respondWith(cacheFirst(event.request, CACHE_NAME));
    return;
  }

  // App shell: cache-first → fast load
  event.respondWith(cacheFirst(event.request, CACHE_NAME));
});

// ── Strategies ────────────────────────────────────────────────────────────────

/** Cache-first: serve from cache, fetch + update cache if not found */
async function cacheFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request);
  if (cached) return cached;
  try {
    const fresh = await fetch(request);
    if (fresh.ok) cache.put(request, fresh.clone());
    return fresh;
  } catch {
    return new Response('Offline — cached data not available', { status: 503 });
  }
}

/** Network-first with timeout: try network (with timeout), fall back to cache */
async function networkFirst(request, cacheName, timeoutMs = 8000) {
  const cache = await caches.open(cacheName);
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const fresh = await fetch(request, { signal: controller.signal });
    clearTimeout(timer);
    if (fresh.ok) cache.put(request, fresh.clone());
    return fresh;
  } catch {
    clearTimeout(timer);
    const cached = await cache.match(request);
    if (cached) return cached;
    return new Response(
      JSON.stringify({ error: 'Offline — no cached data available', offline: true }),
      { status: 503, headers: { 'Content-Type': 'application/json' } }
    );
  }
}

// ── Background sync: queue PFZ refresh when back online ──────────────────────
self.addEventListener('sync', event => {
  if (event.tag === 'pfz-refresh') {
    event.waitUntil(
      fetch('/api/pfz/live').then(r => {
        if (r.ok) {
          caches.open(DATA_CACHE).then(c => c.put('/api/pfz/live', r));
          self.clients.matchAll().then(clients =>
            clients.forEach(c => c.postMessage({ type: 'PFZ_UPDATED' }))
          );
        }
      }).catch(() => {})
    );
  }
});

// ── Periodic cache warming for offline readiness ─────────────────────────────
self.addEventListener('message', event => {
  if (event.data?.type === 'CACHE_WARM') {
    // Pre-fetch critical API endpoints for offline use
    const cache = caches.open(DATA_CACHE);
    CACHEABLE_APIS.forEach(url => {
      fetch(url).then(r => {
        if (r.ok) cache.then(c => c.put(url, r));
      }).catch(() => {});
    });
  }
});
