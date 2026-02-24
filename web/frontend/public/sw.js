// Aibolit AI — Service Worker
// Cache-first для статики, Network-first для API

const CACHE_VERSION = 'aibolit-v1';
const STATIC_CACHE = `${CACHE_VERSION}-static`;
const API_CACHE = `${CACHE_VERSION}-api`;

const STATIC_ASSETS = [
  '/',
  '/manifest.json',
  '/offline.html',
];

// Install — кэшировать статику
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  // Активировать сразу, не дожидаясь закрытия старых вкладок
  self.skipWaiting();
});

// Activate — очистить старые кэши
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== STATIC_CACHE && name !== API_CACHE)
          .map((name) => caches.delete(name))
      );
    })
  );
  // Взять контроль над всеми клиентами немедленно
  self.clients.claim();
});

// Fetch — cache-first для статики, network-first для API
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Пропускать не-GET запросы
  if (request.method !== 'GET') {
    return;
  }

  // Пропускать запросы к другим доменам
  if (url.origin !== self.location.origin) {
    return;
  }

  // API-запросы — network-first
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request));
    return;
  }

  // Статические ресурсы — cache-first
  event.respondWith(cacheFirst(request));
});

// Cache-first стратегия: берём из кэша, если нет — из сети
async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) {
    return cached;
  }

  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    // Если оффлайн и нет в кэше — показать offline-страницу для навигационных запросов
    if (request.mode === 'navigate') {
      const offlinePage = await caches.match('/offline.html');
      if (offlinePage) {
        return offlinePage;
      }
    }
    return new Response('Offline', { status: 503, statusText: 'Service Unavailable' });
  }
}

// Network-first стратегия: берём из сети, если нет — из кэша
async function networkFirst(request) {
  try {
    const response = await fetch(request);
    return response;
  } catch (error) {
    const cached = await caches.match(request);
    if (cached) {
      return cached;
    }

    // Offline fallback для API
    return new Response(
      JSON.stringify({
        error: 'offline',
        message: 'Нет подключения к интернету. Проверьте соединение и попробуйте снова.',
      }),
      {
        status: 503,
        statusText: 'Service Unavailable',
        headers: { 'Content-Type': 'application/json; charset=utf-8' },
      }
    );
  }
}
