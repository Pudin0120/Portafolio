# Code Context

## Files Retrieved
1. `src/services/apiClient.ts` (lines 1-180) - Central entry point for all API requests. Implements logic for checking `navigator.onLine` and queuing operations.
2. `src/providers/ConnectivityProvider.tsx` (lines 1-65) - Manages global `isOnline` state via window events.
3. `src/services/sync/syncManager.ts` (lines 1-110) - Handles the execution and retry logic of queued operations.
4. `src/hooks/usePersistentAuth.ts` (lines 1-270) - Manages authentication lifecycle, revalidation, and triggers sync on reconnection.
5. `src/services/employeeService.ts` (lines 1-110) - Implementation of data loading with local memory caching.
6. `src/services/userService.ts` (lines 1-60) - Basic user profile and role fetching logic.
7. `src/services/sync/pwaSyncContracts.ts` (lines 1-135) - Defines types for syncable operations and error classification.

## Key Code

### Request Routing in `apiClient.ts`
```typescript
// src/services/apiClient.ts (lines 92-94)
if (typeof navigator !== "undefined" && !navigator.onLine) {
    return await this.queueOfflineOperation<T>(options);
}
```
If `navigator.onLine` is false, `request` immediately tries to queue the operation. For `GET` requests, `options.offlineOperation` is usually `undefined`, leading to a "No internet connection" `ApiError`.

### Network Error Classification
```typescript
// src/services/sync/pwaSyncContracts.ts (lines 104-135)
export const isOfflineNetworkError = (error: unknown): boolean => {
    // Returns true for status 0, "OFFLINE" text, TypeError (Fetch failure), 
    // or regex match for offline/network error messages.
};
```
This function is used in `apiClient.ts` to catch failed fetch attempts and convert them to queued operations if applicable.

## Architecture

1.  **Connectivity State**: `ConnectivityProvider` tracks the browser's online status.
2.  **Request Guard**: `apiClient.ts` acts as the gatekeeper. It checks `navigator.onLine` before every request.
3.  **Operation Queuing**: If offline (or a network error occurs), and the request is a write operation (POST/PUT/PATCH/DELETE with `offlineOperation` defined), it's saved to IndexedDB via `syncManager`.
4.  **Data Persistence (GET)**: Currently, `GET` requests (like `employeeService.getEmployees`) rely on local memory caches. If offline and the cache is expired, they fail with an `ApiError`. There is no logic in `apiClient` to serve `GET` requests from a persistent cache (like IndexedDB) automatically.
5.  **Reconnection Sync**: `usePersistentAuth` listens for `connectionEpoch` changes. When back online, it triggers `syncPendingOperations` to replay the queue.

## Start Here
Start with `src/services/apiClient.ts` (line 92). This is where the hard suppression of requests happens when `navigator.onLine` is false. Any fix for `GET` request routing or persistent caching must be integrated here or in the calling services.

## Issues & Risk
1.  **Auth/Connectivity Conflation**: `usePersistentAuth.ts`'s `revalidateSession` (lines 101-140) and `syncUserProfile` (lines 62-108) swallow errors in `catch` blocks. If an auth token expires while offline, the app might stay in an inconsistent "partially authenticated" state.
2.  **Hard Suppression of GET**: `apiClient.ts` does not differentiate between "Safe to fail" and "Must have" `GET` requests when offline.
3.  **isOfflineNetworkError logic**: Matches "TypeError", which is standard for fetch failures but also occurs for code bugs, potentially leading to incorrect offline queuing for logical errors.
