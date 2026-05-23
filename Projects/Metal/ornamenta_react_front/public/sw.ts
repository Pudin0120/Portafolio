/// <reference lib="webworker" />
// @ts-check

import {
	cleanupOutdatedCaches,
	createHandlerBoundToURL,
	precacheAndRoute,
	type PrecacheEntry,
} from "workbox-precaching";
import { NavigationRoute, registerRoute } from "workbox-routing";
import { NetworkFirst, CacheFirst, StaleWhileRevalidate } from "workbox-strategies";
import { CacheableResponsePlugin } from "workbox-cacheable-response";
import { ExpirationPlugin } from "workbox-expiration";

// Declarar que self tiene __WB_MANIFEST inyectado por vite-plugin-pwa
// eslint-disable-next-line @typescript-eslint/no-explicit-any
declare const self: any & {
	__WB_MANIFEST: (PrecacheEntry | string)[];
};

// 
// VERSIONADO DE CACHE
// Para actualizar los runtime caches en una nueva version del SW, basta con
// incrementar CACHE_VERSION (ej: "v1"  "v2"). Los caches obsoletos se
// eliminan automaticamente en el evento activate.
// 
const CACHE_VERSION = "v1";

const CACHE_NAMES = {
	api: `api-${CACHE_VERSION}`,
	images: `images-${CACHE_VERSION}`,
	catalog: `catalog-${CACHE_VERSION}`,
} as const;

// Rutas de datos de catalogo (cambian poco, ideales para Stale While Revalidate).
// Se sirve el cache inmediatamente y se actualiza en segundo plano.
const CATALOG_PATHS = [
	"/unit-measures",
	"/material-types",
	"/measurement-strategies",
	"/roles",
] as const;

/** Conjunto de runtime caches valids para esta version del SW. */
const KNOWN_RUNTIME_CACHES = new Set<string>(Object.values(CACHE_NAMES));

// 
// TIPOS HELPERS
// 
type ExtendableEventLike = Event & {
	waitUntil: (promise: Promise<unknown>) => void;
};

type MessageEventLike = Event & {
	data?: { type?: string };
};

// 
// INSTALL
// 
// El precache del App Shell es declarativo: Workbox lo gestiona internamente
// a traves de precacheAndRoute() registrando su propio listener de install.
//
// NO se llama skipWaiting() aqui: el proyecto usa registerType:"prompt", por
// lo que el user confirma antes de que un nuevo SW se active. En la primera
// instalacion, clients.claim() en el evento activate toma el control de inmediato.
self.addEventListener("install", (_event: Event) => {
	// No-op intencional - el precaching lo realiza precacheAndRoute() abajo.
});

// 
// MENSAJE - SKIP WAITING (update prompt desde la UI)
// 
self.addEventListener("message", (event: MessageEventLike) => {
	if (event.data?.type === "SKIP_WAITING") {
		self.skipWaiting();
	}
});

// 
// ACTIVATE
// 
self.addEventListener("activate", (event: Event) => {
	(event as ExtendableEventLike).waitUntil(
		Promise.all([
			// 1. Tomar control inmediato de todos los clients sin esperar un reload
			//    (necesario en la primera instalacion para que el SW sirva la app).
			self.clients.claim() as Promise<void>,

			// 2. Limpiar runtime caches de versiones anteriores del SW.
			//    Se conservan los caches del precache de Workbox (gestionados por
			//    cleanupOutdatedCaches) y los caches runtime de la version actual.
			(caches.keys() as Promise<string[]>).then((keys) =>
				Promise.all(
					keys
						.filter(
							(key) =>
								!key.startsWith("workbox-precache") &&
								!KNOWN_RUNTIME_CACHES.has(key),
						)
						.map((key) => {
							console.log(`[SW] Eliminando cache obsoleto: ${key}`);
							return caches.delete(key);
						}),
				),
			),
		]),
	);
});

// 
// PRECACHE - App Shell
// 
// Cachea todos los assets listados en __WB_MANIFEST (JS, CSS, HTML, iconos,
// fuentes, imagenes estaticas) usando Cache First con revision por hash.
// Cualquier cambio en el contenido genera un hash nuevo  actualizacion automatica.
precacheAndRoute(self.__WB_MANIFEST);

// Elimina entradas de precache obsoletas de versiones anteriores del SW
// (archivos que ya no estan en el manifest actual).
cleanupOutdatedCaches();

// 
// ESTRATEGIAS DE ROUTING
// 

// 1. Fallback offline para la SPA.
//    Cada request de navegacion recibe el index.html cacheado, permitiendo que
//    React Router maneje las rutas sin importar la conexion.
//    Un reload sin conexion a /works, /tasks, etc. nunca retorna 404.
try {
	const handler = createHandlerBoundToURL("/index.html");
	const navigationRoute = new NavigationRoute(handler, {
		denylist: [/^\/api\//, /^\/@vite\//, /^\/@fs\//, /^\/@id\//, /\.vite\//],
	});
	registerRoute(navigationRoute);
} catch (e) {
	console.error("[SW] Fallo la creation de NavigationRoute:", e);
}

// 2. Datos de catalogo - Stale While Revalidate.
//    Endpoints de referencia (unidades, tipos de material, estrategias, roles)
//    que cambian poco. Sirve el cache inmediatamente para respuesta instantanea
//    y actualiza en segundo plano para que la proxima carga ya tenga datos frescos.
//    Max. 20 entradas, expiran en 7 dias.
registerRoute(
	({ url, request }) => {
		if (request.method !== "GET") return false;
		return CATALOG_PATHS.some((path) => url.pathname.startsWith(path));
	},
	new StaleWhileRevalidate({
		cacheName: CACHE_NAMES.catalog,
		plugins: [
			new ExpirationPlugin({
				maxEntries: 20,
				maxAgeSeconds: 7 * 24 * 60 * 60, // 7 dias
			}),
		],
	}),
);

// 3. Datos maestros - Network First con fallback en cache.
//    Endpoints de materials, composiciones y estrategias que se necesitan
//    para la creation offline. Cachea por 7 dias con hasta 100 entradas.
registerRoute(
	({ url }) =>
		url.pathname.includes("/materials") ||
		url.pathname.includes("/material-types") ||
		url.pathname.includes("/compositions") ||
		url.pathname.includes("/measurement-strategies"),
	new NetworkFirst({
		cacheName: "master-data-cache",
		networkTimeoutSeconds: 3,
		plugins: [
			new CacheableResponsePlugin({
				statuses: [0, 200],
			}),
			new ExpirationPlugin({
				maxEntries: 100,
				maxAgeSeconds: 7 * 24 * 60 * 60, // 7 dias
			}),
		],
	}),
);

// 4. Llamadas a la API - Network First.
//    Prioriza datos frescos de la red; si falla (offline o timeout de 3 s)
//    sirve la respuesta cacheada. Limite: 50 entradas, expiran en 1 dia.
registerRoute(
	/\/api\//,
	new NetworkFirst({
		cacheName: CACHE_NAMES.api,
		networkTimeoutSeconds: 3,
		plugins: [
			new ExpirationPlugin({
				maxEntries: 50,
				maxAgeSeconds: 24 * 60 * 60, // 1 dia
			}),
		],
	}),
);

// 5. Imagenes - Cache First.
//    Mantiene logos y recursos remotos visibles sin reconectar.
//    Limite: 60 entradas, expiran en 30 dias.
registerRoute(
	({ request }) => request.destination === "image",
	new CacheFirst({
		cacheName: CACHE_NAMES.images,
		plugins: [
			new ExpirationPlugin({
				maxEntries: 60,
				maxAgeSeconds: 30 * 24 * 60 * 60, // 30 dias
			}),
		],
	}),
);

// 
// PUSH NOTIFICATIONS (preparado)
// 
// self.addEventListener('push', (event) => {
//   ...
// })
