import { sessionService } from "./sessionService";
import { enqueueFailedOperation } from "@/services/sync/syncManager";
import type { QueueOperationInput } from "@/services/sync/pwaSyncContracts";
import {
	canSyncOperation,
	createPendingOperation,
	isOfflineNetworkError,
} from "@/services/sync/pwaSyncContracts";
import { connectivityBus } from "@/services/pwa/connectivityBus";

type ApiHeaders = Record<string, string>;

export interface ApiRequestOptions {
	requiresAuth?: boolean;
	headers?: ApiHeaders;
	method?: string;
	body?: string;
	offlineOperation?: QueueOperationInput;
}

export class ApiError extends Error {
	constructor(
		message: string,
		public status: number,
		public statusText?: string,
	) {
		super(message);
		this.name = "ApiError";
	}
}

export class ApiClient {
	private baseURL: string;
	private isLocallyOffline = false;

	constructor() {
		this.baseURL = import.meta.env.VITE_API_URL;

		if (typeof window !== "undefined") {
			connectivityBus.addEventListener("connection-restored", () => {
				this.isLocallyOffline = false;
				void this.resumePendingRequests();
			});
		}
	}

	private async resumePendingRequests(): Promise<void> {
		try {
			const { syncPendingOperations, executePendingOperation } = await import(
				"@/services/sync/syncManager"
			);
			await syncPendingOperations(executePendingOperation);
		} catch (err) {
			console.error("[ApiClient] Auto-sync after connection restore failed:", err);
		}
	}

	private async getAuthHeaders(): Promise<ApiHeaders> {
		const token = sessionService.getAccessToken();

		if (!token) {
			throw new Error("User not authenticated");
		}

		return {
			Authorization: `Bearer ${token}`,
			"Content-Type": "application/json",
		};
	}

	private async prepareHeaders(
		options: ApiRequestOptions = {},
	): Promise<ApiHeaders> {
		const { requiresAuth = true, headers = {} } = options;

		const baseHeaders: ApiHeaders = {
			"Content-Type": "application/json",
			...headers,
		};

		if (requiresAuth) {
			const authHeaders = await this.getAuthHeaders();
			Object.assign(baseHeaders, authHeaders);
		}

		return baseHeaders;
	}

	private async queueOfflineOperation<T>(
		options: ApiRequestOptions,
	): Promise<T> {
		if (
			!options.offlineOperation ||
			!canSyncOperation(options.offlineOperation)
		) {
			throw new ApiError("No internet connection", 0, "OFFLINE");
		}

		// Garantizar la inmutabilidad absoluta del payload mediante clonacion profunda y congelacion
		const clonedBody = JSON.parse(JSON.stringify(options.offlineOperation.body));
		const safeOfflineOperation: QueueOperationInput = {
			...options.offlineOperation,
			body: Object.freeze(clonedBody),
		};

		const queuedOperation = createPendingOperation(safeOfflineOperation);
		await enqueueFailedOperation(queuedOperation);
		return safeOfflineOperation.body as T;
	}

	async request<T = unknown>(
		endpoint: string,
		options: ApiRequestOptions = {},
	): Promise<T> {
		const { ...fetchOptions } = options;

		const url = endpoint.startsWith("http")
			? endpoint
			: `${this.baseURL}${endpoint}`;

		try {
			// Determine method (prefer explicit fetchOptions.method or options.method)
			const method = String(
				(fetchOptions as Record<string, unknown>).method ??
					options.method ??
					"GET",
			).toUpperCase();
			const isMutation = ["POST", "PUT", "PATCH", "DELETE"].includes(method);

			// For write operations with an offlineOperation provided, queue early when offline
			if (
				isMutation &&
				options.offlineOperation &&
				(this.isLocallyOffline || (typeof navigator !== "undefined" && !navigator.onLine))
			) {
				this.isLocallyOffline = true;
				return await this.queueOfflineOperation<T>(options);
			}

			const headers = await this.prepareHeaders(options);

			const response = await fetch(url, {
				...fetchOptions,
				headers,
			});

			if (response.ok) {
				this.isLocallyOffline = false;
			}

			if (!response.ok) {
				let errorMessage = `Error HTTP: ${response.status}`;

				try {
					const contentType = response.headers.get("content-type");
					const text = await response.text();

					if (
						text.toLowerCase().startsWith("<!doctype") ||
						text.toLowerCase().startsWith("<html") ||
						contentType?.includes("text/html")
					) {
						errorMessage = `Error del servidor (HTTP ${response.status}). Please intenta nuevamente.`;
					} else {
						try {
							const errorData = JSON.parse(text) as {
								message?: string;
								error?: string;
							};
							errorMessage =
								errorData.message || errorData.error || errorMessage;
						} catch {
							errorMessage = text || errorMessage;
						}
					}
				} catch (textErr) {
					console.error("Error leyendo respuesta de error:", textErr);
				}

				throw new ApiError(errorMessage, response.status, response.statusText);
			}

			const contentLength = response.headers.get("content-length");
			if (contentLength === "0" || response.status === 204) {
				return null as T;
			}

			const contentType = response.headers.get("content-type");

			if (!contentType?.includes("application/json")) {
				const text = await response.text();
				if (
					text.toLowerCase().startsWith("<!doctype") ||
					text.toLowerCase().startsWith("<html")
				) {
					throw new Error(
						"El servidor devolvio HTML en lugar de JSON. Verifica la configuration de la API.",
					);
				}
				if (text) {
					try {
						return JSON.parse(text);
					} catch {
						throw new Error("La respuesta del servidor no es JSON valid");
					}
				}
				return null as T;
			}

			const data = await response.json();
			return data;
		} catch (error) {
			if (isOfflineNetworkError(error)) {
				this.isLocallyOffline = true;
			}

			if (options.offlineOperation && isOfflineNetworkError(error)) {
				return await this.queueOfflineOperation<T>(options);
			}

			if (!(error instanceof Error) || error.name !== "AbortError") {
				// Silently handle errors - they will be thrown and handled by the caller
			}
			throw error;
		}
	}

	async get<T = unknown>(
		endpoint: string,
		options: ApiRequestOptions = {},
	): Promise<T> {
		return this.request<T>(endpoint, { ...options, method: "GET" });
	}

	async post<T = unknown>(
		endpoint: string,
		data?: unknown,
		options: ApiRequestOptions = {},
	): Promise<T> {
		return this.request<T>(endpoint, {
			...options,
			method: "POST",
			body: data ? JSON.stringify(data) : undefined,
		});
	}

	async put<T = unknown>(
		endpoint: string,
		data?: unknown,
		options: ApiRequestOptions = {},
	): Promise<T> {
		return this.request<T>(endpoint, {
			...options,
			method: "PUT",
			body: data ? JSON.stringify(data) : undefined,
		});
	}

	async patch<T = unknown>(
		endpoint: string,
		data?: unknown,
		options: ApiRequestOptions = {},
	): Promise<T> {
		return this.request<T>(endpoint, {
			...options,
			method: "PATCH",
			body: data ? JSON.stringify(data) : undefined,
		});
	}

	async delete<T = unknown>(
		endpoint: string,
		options: ApiRequestOptions = {},
	): Promise<T> {
		return this.request<T>(endpoint, { ...options, method: "DELETE" });
	}
}

export const apiClient = new ApiClient();
