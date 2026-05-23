# Delta Spec: connectivity-api-routing-fix

## Goal

Ensure the app correctly routes API requests based on actual connectivity, preventing false "offline" states for online users and accurately handling real offline scenarios.

## Requirements

### R1. Reliable Connectivity Detection

The app MUST NOT rely solely on `navigator.onLine` to suppress requests, especially for GET operations.

#### Scenario: online GET proceeds regardless of `navigator.onLine` hint

- **Given** the browser reports `navigator.onLine = false` (potential false negative)
- **And** the user is attempting to load materials or products
- **When** the app issues a GET request
- **Then** the `apiClient` SHOULD attempt the fetch if no `offlineOperation` is provided
- **And** it MUST only fall back to an "offline" error if the fetch actually fails with a verifiable network error.

### R2. Refined Error Classification

The app MUST distinguish between genuine network failures, backend errors, and programming bugs.

#### Scenario: `TypeError` is not automatically a connectivity failure

- **Given** a request fails with a `TypeError`
- **When** `isOfflineNetworkError` evaluates the error
- **Then** it MUST NOT return `true` unless the error message or context explicitly points to a network/transport failure (e.g., "Failed to fetch", "DNS resolution failed").
- **And** it MUST NOT treat code-driven `TypeErrors` (like accessing a property of null) as offline states.

### R3. Transparent Auth Revalidation

The auth layer MUST differentiate between a connectivity failure and a session expiration.

#### Scenario: revalidation failure provides feedback

- **Given** the app is online
- **When** `revalidateSession` or `syncUserProfile` fails
- **Then** it MUST NOT silently swallow the error if it's an HTTP 401/403 (Unauthorized/Forbidden).
- **And** it MUST trigger an appropriate auth-failure flow (e.g., logout or token refresh) instead of assuming the user is just "offline".

### R4. GET requests MUST NOT be hard-suppressed

`apiClient.request` MUST allow GET requests to reach the network if there is a possibility of connection, unless a persistent cache fallback is specifically requested.

#### Scenario: material loading ignores false offline hint

- **Given** the browser is actually online but `navigator.onLine` is unstable
- **When** `employeeService.getEmployees` or similar is called
- **Then** the `apiClient` MUST attempt the network request.
- **And** if it succeeds, the UI MUST show the fresh data.

### R5. Preserve mutation queueing for true offline

Destructive operations (POST/PUT/PATCH/DELETE) MUST continue to use the sync queue when a real network failure occurs and an `offlineOperation` is defined.

#### Scenario: material creation queues only on real failure

- **Given** the user is creating a material
- **When** a real network failure occurs (confirmed by fetch failure)
- **Then** the operation MUST be enqueued in IndexedDB as a pending operation.

## Acceptance Criteria

- Authenticated GET requests for `materials` and `products` reach the backend when online, even if `navigator.onLine` is flaky.
- `isOfflineNetworkError` no longer marks logical `TypeErrors` as offline.
- Auth revalidation errors (401/403) are handled as auth issues, not connectivity issues.
- No "Sin user autenticado" messages appear due to incorrect offline routing.
- `bun run test` passes and covers the refined error classification.

## Non-Goals

- Implementing a full offline GET cache (out of scope for this slice).
- Changing the IndexedDB schema.
- Redesigning the `ConnectivityProvider` UI.
