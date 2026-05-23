import { useCallback, useEffect, useState } from "react";
import {
	getPendingOperations,
	type PendingOperation,
} from "@/services/indexedDb/pwaSyncDb";

export function useSyncQueue() {
	const [operations, setOperations] = useState<PendingOperation[]>([]);
	const [isLoading, setIsLoading] = useState<boolean>(true);

	const refresh = useCallback(async (): Promise<void> => {
		setIsLoading(true);
		try {
			const queue = await getPendingOperations();
			setOperations(queue);
		} finally {
			setIsLoading(false);
		}
	}, []);

	useEffect(() => {
		let active = true;

		const fetchQueue = () => {
			void getPendingOperations()
				.then((queue) => {
					if (!active) return;
					setOperations(queue);
				})
				.finally(() => {
					if (!active) return;
					setIsLoading(false);
				});
		};

		fetchQueue();

		const intervalId = setInterval(fetchQueue, 3000);

		return () => {
			active = false;
			clearInterval(intervalId);
		};
	}, []);

	const pendingCount = operations.filter(
		(operation) => operation.status === "pending",
	).length;
	const errorCount = operations.filter(
		(operation) => operation.status === "error",
	).length;
	const syncedCount = operations.filter(
		(operation) => operation.status === "synced",
	).length;

	return {
		operations,
		isLoading,
		pendingCount,
		errorCount,
		syncedCount,
		refresh,
	};
}
