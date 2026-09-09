// ── Organized Culturality · Service Worker (RU + EN) ─────────────────────
// Стратегия: Cache First для статики, Network First для HTML страниц.
// Офлайн-фолбэк выбирается по префиксу /en/ в пути запроса.
//
// ⚠️ Этот файл пересобирается в gen_en.py (после gen.py) — не правьте версию
// в gen.py изолированно: список PRECACHE_URLS здесь включает оба языка.

const SITE_VERSION = 44;
const CACHE_NAME = `orgculture-v${SITE_VERSION}`;
const STATIC_CACHE = `orgculture-static-v${SITE_VERSION}`;

const PRECACHE_URLS = [
  '/',
  '/manifesto/',
  '/texts/',
  '/projects/',
  '/recommendations/',
  '/about/',
  '/privacy/',
  '/cookies/',
  '/bot-rules/',
  '/en/',
  '/en/manifesto/',
  '/en/texts/',
  '/en/projects/',
  '/en/recommendations/',
  '/en/about/',
  '/en/privacy/',
  '/en/cookies/',
  '/en/bot-rules/',
  '/offline.html',
  '/en/offline.html',
  '/manifest.json',
  '/en/manifest.json',
  '/assets/icons/favicon.svg',
  '/assets/icons/favicon-192.png',
  '/assets/icons/favicon-512.png',
  '/assets/style.css?v=44'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(key => key !== CACHE_NAME && key !== STATIC_CACHE)
          .map(key => caches.delete(key))
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  if (url.origin !== location.origin) return;

  if (request.headers.get('accept')?.includes('text/html')) {
    event.respondWith(networkFirst(request));
    return;
  }

  if (
    url.pathname.startsWith('/assets/') ||
    url.pathname.startsWith('/images/') ||
    url.pathname.endsWith('.css') ||
    url.pathname.endsWith('.js') ||
    url.pathname.endsWith('.png') ||
    url.pathname.endsWith('.svg') ||
    url.pathname.endsWith('.ico')
  ) {
    event.respondWith(cacheFirst(request));
    return;
  }

  event.respondWith(networkFirst(request));
});

async function networkFirst(request) {
  const cache = await caches.open(CACHE_NAME);
  try {
    const response = await fetch(request);
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await cache.match(request);
    if (cached) return cached;
    if (request.headers.get('accept')?.includes('text/html')) {
      const url = new URL(request.url);
      const isEn = url.pathname.startsWith('/en/');
      const fallback = await cache.match(isEn ? '/en/offline.html' : '/offline.html');
      if (fallback) return fallback;
      const title = isEn ? 'Organized Culturality' : 'Организованная Культурность';
      const msg = isEn ? 'No internet connection' : 'Нет подключения к интернету';
      return new Response(
        `<html><body style="background:#0A0A0A;color:#F5F2ED;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;text-align:center"><div><h1 style="font-weight:300;">${title}</h1><p style="color:#9A968E;">${msg}</p></div></body></html>`,
        { headers: { 'Content-Type': 'text/html; charset=utf-8' } }
      );
    }
    return new Response('', { status: 503 });
  }
}

async function cacheFirst(request) {
  const cache = await caches.open(STATIC_CACHE);
  const cached = await cache.match(request);
  if (cached) return cached;
  try {
    const response = await fetch(request);
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    return new Response('', { status: 503 });
  }
}
