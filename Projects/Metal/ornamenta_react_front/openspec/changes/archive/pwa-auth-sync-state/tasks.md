# Tasks: pwa-auth-sync-state

## Review Forecast

Estimated change size: **280-360 lines** across auth, sync, API, and employee/material integration points.

Because the estimated review size stays under the 400-line budget, this can proceed as a single change slice unless implementation expands beyond the forecast.

## Task 1 - Stabilize persisted auth session

- [x] Keep the local auth snapshot intact while offline.
- [x] Revalidate Firebase session only when online.
- [x] Preserve access token and user role/state from the snapshot when offline.
- [x] Ensure logout still clears persisted session intentionally.

## Task 2 - Correct IndexedDB queue model and retry behavior

- [x] Extend queued operation metadata for replayable requests.
- [x] Track `pending`, `synced`, and `error` consistently.
- [x] Fix retry logic so it updates the existing record instead of deleting the retried entry.
- [x] Keep failed operations available for later recovery.

## Task 3 - Add reconnect replay executor

- [x] Trigger replay when connectivity returns.
- [x] Revalidate auth before flushing the queue.
- [x] Process pending operations in deterministic order.
- [x] Mark operations as synced or error after replay.

## Task 4 - Route supported employee/material mutations through queue-aware flow

- [x] Employee create, activate, deactivate must enqueue when offline or network-failing.
- [x] Material create and edit must enqueue when offline or network-failing.
- [x] Material deletion must remain non-queued.
- [x] Remove offline-only UI disables for supported employee/material actions.

## Task 5 - Add focused tests

- [x] Auth persistence tests for offline hydration and online revalidation.
- [x] Queue tests for retry/status transitions.
- [x] Replay tests for reconnect-triggered flush.
- [x] Business rule tests for supported vs unsupported operations.

## Implementation Order

1. Auth persistence
2. Queue model and retry fix
3. Reconnect replay
4. Employee/material wiring
5. Tests
