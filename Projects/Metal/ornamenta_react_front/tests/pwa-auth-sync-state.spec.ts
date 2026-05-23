import { expect, test } from "@playwright/test";
import { getOfflineBannerContainerClassName } from "../src/components/offline/offlineBannerLayout";
import { buildAuthSessionSnapshot } from "../src/services/auth/sessionStorage";
import {
	advanceOperationRetry,
	canSyncOperation,
	createPendingOperation,
	isOfflineNetworkError,
} from "../src/services/sync/pwaSyncContracts";
import {
	canShowNoRoleFallback,
	resolveProfileAccessToken,
	shouldBlockAuthenticatedRoutes,
} from "../src/services/auth/authUiGuards";

test("creates a replayable pending operation with pending status and timestamps", () => {
	const operation = createPendingOperation({
		entity: "employee",
		operation: "create",
		endpoint: "/admin/users",
		method: "POST",
		body: { email: "demo@example.com" },
	});

	expect(operation.id).toBeTruthy();
	expect(operation.status).toBe("pending");
	expect(operation.retries).toBe(0);
	expect(operation.entity).toBe("employee");
	expect(operation.operation).toBe("create");
	expect(operation.endpoint).toBe("/admin/users");
	expect(operation.method).toBe("POST");
	expect(operation.body).toEqual({ email: "demo@example.com" });
	expect(operation.createdAt).toBeLessThanOrEqual(Date.now());
	expect(operation.updatedAt).toBe(operation.createdAt);
});

test("only syncs supported employee and material operations", () => {
	expect(
		canSyncOperation({ entity: "employee", operation: "create" }),
	).toBeTruthy();
	expect(
		canSyncOperation({ entity: "employee", operation: "activate" }),
	).toBeTruthy();
	expect(
		canSyncOperation({ entity: "employee", operation: "deactivate" }),
	).toBeTruthy();
	expect(
		canSyncOperation({ entity: "material", operation: "create" }),
	).toBeTruthy();
	expect(
		canSyncOperation({ entity: "material", operation: "update" }),
	).toBeTruthy();
	expect(
		canSyncOperation({ entity: "material", operation: "delete" }),
	).toBeFalsy();
});

test("keeps retried operation record and marks error after the retry budget", () => {
	const operation = createPendingOperation({
		entity: "material",
		operation: "update",
		endpoint: "/materials/123",
		method: "PATCH",
		body: { name: "Steel" },
	});

	const retried = advanceOperationRetry(operation, 5, "Network error");
	expect(retried.id).toBe(operation.id);
	expect(retried.retries).toBe(5);
	expect(retried.status).toBe("error");
	expect(retried.lastError).toBe("Network error");
	expect(retried.updatedAt).toBeGreaterThanOrEqual(operation.updatedAt);
});

test("builds auth snapshot with resolved role and state", () => {
	const snapshot = buildAuthSessionSnapshot(
		{
			uid: "uid-123",
			email: "demo@example.com",
			displayName: "Demo User",
		},
		"EMPLOYEE",
		"A",
		"token-123",
		123456789,
	);

	expect(snapshot.uid).toBe("uid-123");
	expect(snapshot.email).toBe("demo@example.com");
	expect(snapshot.displayName).toBe("Demo User");
	expect(snapshot.role).toBe("EMPLOYEE");
	expect(snapshot.state).toBe("A");
	expect(snapshot.accessToken).toBe("token-123");
	expect(snapshot.lastValidLoginAt).toBe(123456789);
});

test("places offline banner outside the layout flow", () => {
	expect(getOfflineBannerContainerClassName(false, true)).toContain("fixed");
	expect(getOfflineBannerContainerClassName(false, true)).toContain(
		"left-[276px]",
	);
	expect(getOfflineBannerContainerClassName(true, true)).toContain("fixed");
	expect(getOfflineBannerContainerClassName(true, true)).toContain("inset-x-3");
});

test("detects offline network errors", () => {
	expect(
		isOfflineNetworkError(new Error("No internet connection")),
	).toBeTruthy();
	expect(
		isOfflineNetworkError(
			Object.assign(new Error("Offline"), { status: 0, statusText: "OFFLINE" }),
		),
	).toBeTruthy();
	expect(isOfflineNetworkError(new Error("Server error"))).toBeFalsy();
});

test("blocks authenticated routes until startup is ready", () => {
	expect(shouldBlockAuthenticatedRoutes(true, false)).toBeTruthy();
	expect(shouldBlockAuthenticatedRoutes(false, false)).toBeTruthy();
	expect(shouldBlockAuthenticatedRoutes(false, true)).toBeFalsy();
});

test("only shows the no-role fallback after hydration completes", () => {
	expect(canShowNoRoleFallback(false, null)).toBeFalsy();
	expect(canShowNoRoleFallback(true, null)).toBeTruthy();
	expect(canShowNoRoleFallback(true, "EMPLOYEE")).toBeFalsy();
});

test("prefers the persisted session token when resolving profile requests", () => {
	expect(resolveProfileAccessToken("session-token", "firebase-token")).toBe(
		"session-token",
	);
	expect(resolveProfileAccessToken(null, "firebase-token")).toBe(
		"firebase-token",
	);
	expect(resolveProfileAccessToken(null, null)).toBeNull();
});
