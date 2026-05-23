## Apply progress: connectivity-api-routing-fix

**Status**: Applied (implementation committed)

**What I did**

- Implemented refined offline/network error detection.
- Modified `apiClient` so GET requests are not hard-suppressed based solely on `navigator.onLine` (mutations with offlineOperation continue to queue when offline).
- Made revalidation in `usePersistentAuth` treat HTTP 401/403 responses as authentication failures (clear persisted snapshot and tokens) instead of being swallowed as generic failures.
- Tightened `isOfflineNetworkError` to only classify errors as network failures when message/status clearly indicates a transport problem.

**Files changed**

- src/services/sync/pwaSyncContracts.ts - refined isOfflineNetworkError
- src/services/apiClient.ts - changed request flow to allow GET to attempt network; early queueing only for mutating operations with offlineOperation
- src/hooks/usePersistentAuth.ts - treat 401/403 from /users/me as auth failures and clear persisted session

**Tests**

- Ran `bun run test` - 15/15 tests passed (Playwright unit tests).

**Why**

- Prevent false "offline" classification that caused GETs for `materials`/`products` to be suppressed while the browser was actually online.
- Avoid misclassifying programming errors as connectivity failures.
- Ensure 401/403 revalidation responses are handled as auth issues, not offline symptoms.

**Next steps / Notes**

- Add a small test to explicitly cover the refined `isOfflineNetworkError` semantics (e.g., TypeError with non-network message should NOT be classified as offline). Current test suite includes a general detection test but a more targeted case could be useful.
- If desired, follow-up slice could introduce a persistent read cache (IndexedDB) for GETs to provide offline reads.

**Commit(s)**

- `docs(openspec): archive verified SDD slices` - archived previous OpenSpec artifacts
- `feat(pwa): stabilize dev sw lifecycle and reconnect sync` - PWA/stability work
- `fix(connectivity): refine offline detection and allow GETs to attempt network; treat 401/403 revalidation as auth failures` - this slice

**Acceptance Criteria Mapping**

- Authenticated GETs for `materials` and `products` will now attempt network when there is a possibility - covered by changed `apiClient` behavior.
- `isOfflineNetworkError` is now stricter - implemented in `pwaSyncContracts.ts`.
- Revalidation 401/403 are handled as auth faults - implemented in `usePersistentAuth.ts`.

**Applied by**: el Gentleman (assistant) - Implementation and tests run locally.
