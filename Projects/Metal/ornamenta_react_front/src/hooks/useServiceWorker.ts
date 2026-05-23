import { useEffect, useRef, useState } from "react";
import { registerSW } from "virtual:pwa-register";

interface ServiceWorkerState {
	/** El SW is ready and controlling the page */
	isReady: boolean;
	/** A new version is available */
	needRefresh: boolean;
	/** El SW is being installed for the first time */
	isInstalling: boolean;
	/** Forces the update to the new SW */
	updateSW: () => void;
}

/**
 * Hook para interactuar con el Service Worker registrado por vite-plugin-pwa.
 *
 * En este proyecto usamos update prompts en produccion y deshabilitamos la
 * registracion automatica en desarrollo para evitar SWs stale controlando localhost.
 */
export function useServiceWorker(): ServiceWorkerState {
	const [isReady, setIsReady] = useState(false);
	const [needRefresh, setNeedRefresh] = useState(false);
	const [isInstalling, setIsInstalling] = useState(false);
	const updateFnRef = useRef<(() => Promise<void>) | null>(null);

	useEffect(() => {
		const updateSW = registerSW({
			immediate: true,
			onRegisteredSW(_swUrl, registration) {
				setIsReady(Boolean(registration));

				// Heartbeat: Check for updates every hour
				if (registration) {
					const interval = setInterval(
						() => {
							void registration.update();
						},
						60 * 60 * 1000,
					);

					// Check on window focus
					const handleFocus = () => {
						void registration.update();
					};
					window.addEventListener("focus", handleFocus);

					return () => {
						clearInterval(interval);
						window.removeEventListener("focus", handleFocus);
					};
				}
			},
			onNeedRefresh() {
				setNeedRefresh(true);
			},
			onOfflineReady() {
				setIsInstalling(false);
			},
			onRegisterError() {
				setIsReady(false);
			},
		});

		updateFnRef.current = updateSW;
	}, []);

	return {
		isReady,
		needRefresh,
		isInstalling,
		updateSW: () => {
			void updateFnRef.current?.();
		},
	};
}
