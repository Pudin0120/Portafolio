export type SyncEntity = "employee" | "material";
export type SyncOperation =
	| "create"
	| "update"
	| "activate"
	| "deactivate"
	| "delete";
export type SyncStatus = "pending" | "synced" | "error";

export interface PendingOperation {
	id: string;
	entity: SyncEntity;
	operation: SyncOperation;
	endpoint: string;
	method: string;
	body: unknown;
	status: SyncStatus;
	retries: number;
	createdAt: number;
	updatedAt: number;
	lastError: string | null;
}

export interface QueueOperationInput {
	id?: string;
	entity: SyncEntity;
	operation: SyncOperation;
	endpoint: string;
	method: string;
	body: unknown;
}

const SUPPORTED_ENTITY_OPERATIONS: Record<
	SyncEntity,
	ReadonlySet<SyncOperation>
> = {
	employee: new Set(["create", "update", "activate", "deactivate"]),
	material: new Set(["create", "update"]),
};

const MAX_RETRIES_DEFAULT = 5;

const createOperationId = (): string => {
	if (
		typeof crypto !== "undefined" &&
		typeof crypto.randomUUID === "function"
	) {
		return crypto.randomUUID();
	}

	return `op_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
};

export const canSyncOperation = (
	operation: Pick<QueueOperationInput, "entity" | "operation">,
): boolean => {
	return SUPPORTED_ENTITY_OPERATIONS[operation.entity].has(operation.operation);
};

export const createPendingOperation = (
	input: QueueOperationInput,
): PendingOperation => {
	const now = Date.now();
	return {
		id: input.id ?? createOperationId(),
		entity: input.entity,
		operation: input.operation,
		endpoint: input.endpoint,
		method: input.method,
		body: input.body,
		status: "pending",
		retries: 0,
		createdAt: now,
		updatedAt: now,
		lastError: null,
	};
};

export const advanceOperationRetry = (
	operation: PendingOperation,
	retryCount: number,
	lastError: string,
	maxRetries: number = MAX_RETRIES_DEFAULT,
): PendingOperation => {
	const status: SyncStatus = retryCount >= maxRetries ? "error" : "pending";

	return {
		...operation,
		retries: retryCount,
		status,
		updatedAt: Date.now(),
		lastError,
	};
};

export const markOperationSynced = (
	operation: PendingOperation,
): PendingOperation => {
	return {
		...operation,
		status: "synced",
		updatedAt: Date.now(),
		lastError: null,
	};
};

export const isOfflineNetworkError = (error: unknown): boolean => {
	if (!error || typeof error !== "object") return false;

	const candidate = error as {
		message?: unknown;
		status?: unknown;
		statusText?: unknown;
		name?: unknown;
		code?: unknown;
	};

	// Explicit sentinel/status-based indicators
	if (candidate.status === 0 || candidate.statusText === "OFFLINE") {
		return true;
	}

	// Fetch failures in browser always throw a TypeError (e.g. Failed to fetch, Load failed)
	if (candidate.name === "TypeError" || error instanceof TypeError) {
		return true;
	}

	if (typeof candidate.message === "string") {
		return /offline|sin conexi[oo]n|network|failed to fetch|NetworkError|load failed|ENOTFOUND|EAI_AGAIN/i.test(
			candidate.message as string,
		);
	}

	return false;
};
