import { shouldCleanupDevServiceWorkers } from "@services/pwa/pwaLifecycle";

export interface DevServiceWorkerCleanupResult {
	registrationsRemoved: number;
	cachesCleared: number;
}

export const cleanupDevServiceWorkers = async (): Promise<DevServiceWorkerCleanupResult> => {
	if (
		!shouldCleanupDevServiceWorkers(
			import.meta.env.DEV,
			typeof window !== "undefined" ? window.location.hostname : "",
		)
	) {
		return { registrationsRemoved: 0, cachesCleared: 0 };
	}

	if (typeof navigator === "undefined" || !("serviceWorker" in navigator)) {
		return { registrationsRemoved: 0, cachesCleared: 0 };
	}

	const registrations = await navigator.serviceWorker.getRegistrations();
	const unregisterResults = await Promise.all(
		registrations.map((registration) => registration.unregister()),
	);

	let cachesCleared = 0;
	if (typeof caches !== "undefined") {
		const cacheKeys = await caches.keys();
		const deletions = await Promise.all(cacheKeys.map((key) => caches.delete(key)));
		cachesCleared = deletions.filter(Boolean).length;
	}

	return {
		registrationsRemoved: unregisterResults.filter(Boolean).length,
		cachesCleared,
	};
};
