import type {
	PendingOperation,
	SyncStatus,
} from "@/services/sync/pwaSyncContracts";

import { openDatabase } from "./dbHelper";

const STORE_NAME = "operations";

type TransactionMode = "readonly" | "readwrite" | "versionchange";

const withStore = async <T>(
	mode: TransactionMode,
	callback: (store: IDBObjectStore) => IDBRequest<T>,
): Promise<T> => {
	const db = await openDatabase();

	return new Promise((resolve, reject) => {
		const tx = db.transaction(STORE_NAME, mode);
		const request = callback(tx.objectStore(STORE_NAME));

		request.onsuccess = () => resolve(request.result);
		request.onerror = () => reject(request.error);
		tx.oncomplete = () => db.close();
		tx.onerror = () => {
			db.close();
			reject(tx.error);
		};
	});
};

export const addOperation = async (
	operation: PendingOperation,
): Promise<void> => {
	await withStore("readwrite", (store) => store.put(operation));
};

export const getOperationById = async (
	id: string,
): Promise<PendingOperation | undefined> => {
	return withStore<PendingOperation | undefined>("readonly", (store) =>
		store.get(id),
	);
};

export const getPendingOperations = async (): Promise<PendingOperation[]> => {
	const operations = await withStore<PendingOperation[]>("readonly", (store) =>
		store.getAll(),
	);
	return operations.slice().sort((left, right) => {
		if (left.createdAt !== right.createdAt) {
			return left.createdAt - right.createdAt;
		}
		return left.updatedAt - right.updatedAt;
	});
};

export const updateOperation = async (
	id: string,
	patch: Partial<PendingOperation>,
): Promise<void> => {
	const operation = await getOperationById(id);
	if (!operation) return;

	await withStore("readwrite", (store) =>
		store.put({ ...operation, ...patch }),
	);
};

export const updateOperationStatus = async (
	id: string,
	status: SyncStatus,
	lastError: string | null = null,
): Promise<void> => {
	await updateOperation(id, {
		status,
		lastError,
		updatedAt: Date.now(),
	});
};

export const removeOperation = async (id: string): Promise<void> => {
	await withStore("readwrite", (store) => store.delete(id));
};

export const clearSynced = async (): Promise<void> => {
	const operations = await getPendingOperations();
	await Promise.all(
		operations
			.filter((operation) => operation.status === "synced")
			.map((operation) => removeOperation(operation.id)),
	);
};

export type { PendingOperation } from "@/services/sync/pwaSyncContracts";
