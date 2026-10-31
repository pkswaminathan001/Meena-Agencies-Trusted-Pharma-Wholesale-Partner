// Meena Agencies — Service Worker (minimal)
self.addEventListener('install', (e) => {
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(clients.claim());
});

self.addEventListener('fetch', (e) => {
  // Network-first, let Streamlit handle everything
  e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
});
