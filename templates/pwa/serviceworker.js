console.log("SERVICE WORKER LOADED");

const CACHE_NAME = "novel-v2";
const OFFLINE_URL = "/static/offline.html";
const OFFLINE_IMAGE = "/static/dashboard/images/offline.png";

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll([
        OFFLINE_URL,
        OFFLINE_IMAGE,
        "/static/dashboard/css/bootstrap.min.css",
        "/static/dashboard/css/style.css",
      ]);
    }),
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        }),
      ),
    ),
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const request = event.request;

  if (request.method !== "GET" || !request.url.startsWith("http")) {
    return;
  }

  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (!response || response.status !== 200) {
            return response;
          }

          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, clone).catch(() => {});
          });

          return response;
        })
        .catch(async () => {
          const cached = await caches.match(request);
          return cached || caches.match(OFFLINE_URL);
        }),
    );
    return;
  }

  event.respondWith(
    caches.match(request).then((cached) => {
      if (cached) return cached;

      return fetch(request)
        .then((response) => {
          if (!response || response.status !== 200) {
            return response;
          }

          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, clone).catch(() => {});
          });

          return response;
        })
        .catch(async () => {
          if (request.destination === "image") {
            return caches.match(OFFLINE_IMAGE);
          }
        });
    }),
  );
});


// // Push Notification ------------------------------------------------------
self.addEventListener("push", (event) => {
  if (!event.data) return;

  const data = event.data.json();

  const title   = data.title || "Novel Update";
  const options = {
    body:  data.body  || "",
    icon:  "/static/dashboard/images/logo.png",
    badge: "/static/dashboard/images/logo.png",
    data:  { url: data.url || "/" },
    vibrate: [200, 100, 200],
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

// // Notification Click ------------------------------------------------------
self.addEventListener("notificationclick", (event) => {
  event.notification.close();

  const url = event.notification.data?.url || "/";

  event.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if (client.url === url && "focus" in client) {
          return client.focus();
        }
      }
      // မရှိရင် tab အသစ် ဖွင့်
      if (clients.openWindow) {
        return clients.openWindow(url);
      }
    })
  );
});