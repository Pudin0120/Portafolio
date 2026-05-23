import { sessionService } from "@/services/sessionService";
import {
	addOperation,
	clearSynced,
	getPendingOperations,
	removeOperation,
	updateOperation,
	updateOperationStatus,
	type PendingOperation,
} from "@/services/indexedDb/pwaSyncDb";
import {
	advanceOperationRetry,
	canSyncOperation,
	isOfflineNetworkError,
} from "@/services/sync/pwaSyncContracts";

const MAX_RETRIES = 5;

const API_BASE_URL: string = import.meta.env.VITE_API_URL;

const getAuthHeaders = (): Record<string, string> => {
	const token = sessionService.getAccessToken();
	if (!token) {
		throw new Error("User not authenticated");
	}

	return {
		Authorization: `Bearer ${token}`,
		"Content-Type": "application/json",
	};
};

const parseErrorMessage = async (response: Response): Promise<string> => {
	let errorMessage = `Error HTTP: ${response.status}`;

	try {
		const contentType = response.headers.get("content-type");
		const text = await response.text();

		if (
			text.toLowerCase().startsWith("<!doctype") ||
			text.toLowerCase().startsWith("<html") ||
			contentType?.includes("text/html")
		) {
			return `Error del servidor (HTTP ${response.status}). Please intenta nuevamente.`;
		}

		try {
			const errorData = JSON.parse(text) as {
				message?: string;
				error?: string;
			};
			return errorData.message || errorData.error || errorMessage;
		} catch {
			return text || errorMessage;
		}
	} catch {
		return errorMessage;
	}
};

export async function executePendingOperation(
	operation: PendingOperation,
): Promise<void> {
	if (!canSyncOperation(operation)) {
		throw new Error(
			`Operacion no soportada para sincronizacion: ${operation.entity}:${operation.operation}`,
		);
	}

	const response = await fetch(`${API_BASE_URL}${operation.endpoint}`, {
		method: operation.method,
		headers: getAuthHeaders(),
		body:
			operation.body === undefined ? undefined : JSON.stringify(operation.body),
	});

	if (!response.ok) {
		throw new Error(await parseErrorMessage(response));
	}
}

export async function syncPendingOperations(
	execute: (operation: PendingOperation) => Promise<void>,
): Promise<void> {
	const queue = await getPendingOperations();

	for (const operation of queue) {
		if (operation.status !== "pending") continue;
		if (!canSyncOperation(operation)) {
			await updateOperationStatus(
				operation.id,
				"error",
				`Operacion no soportada: ${operation.entity}:${operation.operation}`,
			);
			continue;
		}

		try {
			await execute(operation);
			await updateOperationStatus(operation.id, "synced", null);
		} catch (error: unknown) {
			const retries = operation.retries + 1;
			const message =
				error instanceof Error ? error.message : "Error de sincronizacion";
			const nextOperation = advanceOperationRetry(
				operation,
				retries,
				message,
				MAX_RETRIES,
			);
			await updateOperation(operation.id, nextOperation);

			if (nextOperation.status === "error") {
				continue;
			}

			if (isOfflineNetworkError(error)) {
				break;
			}
		}
	}

	await clearSynced();
}

export async function enqueueFailedOperation(
	operation: PendingOperation,
): Promise<void> {
	await addOperation(operation);
}

export async function markOperationError(
	id: string,
	lastError: string,
): Promise<void> {
	await updateOperationStatus(id, "error", lastError);
}

export async function deleteOperation(id: string): Promise<void> {
	await removeOperation(id);
}
