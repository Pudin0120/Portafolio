import React, {
	createContext,
	useContext,
	useEffect,
	useMemo,
	useState,
	useRef,
	useCallback,
} from "react";
import {
	executePendingOperation,
	syncPendingOperations,
} from "@services/sync/syncManager";
import { emitConnectionRestored } from "@services/pwa/connectivityBus";

interface ConnectivityContextValue {
	isOnline: boolean;
	lastOnline: number | null;
	connectionEpoch: number;
	syncing: boolean;
	setSyncing: (syncing: boolean) => void;
}

const ConnectivityContext = createContext<ConnectivityContextValue | undefined>(
	undefined,
);

export const ConnectivityProvider: React.FC<{ children: React.ReactNode }> = ({
	children,
}) => {
	const [isOnline, setIsOnline] = useState<boolean>(navigator.onLine);
	const [lastOnline, setLastOnline] = useState<number | null>(() =>
		navigator.onLine ? Date.now() : null,
	);
	const [connectionEpoch, setConnectionEpoch] = useState<number>(() =>
		navigator.onLine ? 1 : 0,
	);
	const syncTasksRef = useRef<number>(0);
	const [syncing, setSyncingState] = useState<boolean>(false);

	const setSyncing = useCallback((val: boolean) => {
		if (val) {
			syncTasksRef.current += 1;
		} else {
			syncTasksRef.current = Math.max(0, syncTasksRef.current - 1);
		}
		setSyncingState(syncTasksRef.current > 0);
	}, []);

	const prevIsOnlineRef = useRef<boolean>(isOnline);

	useEffect(() => {
		// Detect transition from offline to online
		if (isOnline && !prevIsOnlineRef.current) {
			void (async () => {
				setSyncing(true);
				try {
					await syncPendingOperations(executePendingOperation);
				} catch (err) {
					console.error("[ConnectivityProvider] Auto-sync failed:", err);
				} finally {
					setSyncing(false);
				}
			})();
		}
		prevIsOnlineRef.current = isOnline;
	}, [isOnline]);

	useEffect(() => {
		const handleOnline = (): void => {
			setIsOnline(true);
			setLastOnline(Date.now());
			setConnectionEpoch((current) => current + 1);
			emitConnectionRestored();
		};

		const handleOffline = (): void => {
			setIsOnline(false);
		};

		window.addEventListener("online", handleOnline);
		window.addEventListener("offline", handleOffline);

		return () => {
			window.removeEventListener("online", handleOnline);
			window.removeEventListener("offline", handleOffline);
		};
	}, []);

	const value = useMemo(
		() => ({ isOnline, lastOnline, connectionEpoch, syncing, setSyncing }),
		[isOnline, lastOnline, connectionEpoch, syncing],
	);

	return (
		<ConnectivityContext.Provider value={value}>
			{children}
		</ConnectivityContext.Provider>
	);
};

export const useConnectivity = (): ConnectivityContextValue => {
	const context = useContext(ConnectivityContext);
	if (!context) {
		throw new Error(
			"useConnectivity must be used within a ConnectivityProvider",
		);
	}
	return context;
};
