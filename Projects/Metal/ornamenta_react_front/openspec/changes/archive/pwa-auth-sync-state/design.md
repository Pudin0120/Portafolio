# Design: pwa-auth-sync-state

## Problem to Solve

The frontend already has partial building blocks for persisted auth and offline queueing, but they are not wired together into a reliable offline-to-online workflow. The implementation must preserve the current session while offline, queue supported mutations, and replay them automatically without losing data.

## Proposed Architecture

### 1) Session persistence stays lightweight

Keep the existing auth snapshot approach in `src/services/auth/sessionStorage.ts` as the primary offline session record.

- Store: uid, email, displayName, role, state, accessToken, lastValidLoginAt
- Behavior: never clear the snapshot just because Firebase is unavailable offline
- Revalidation: only refresh the snapshot when online and `FirebaseAuth` can resolve the current user

This is the smallest safe change because the repo already uses snapshot-based auth hydration.

### 2) Queue operations as explicit replay records

Extend the IndexedDB queue record to carry replayable request metadata instead of only a generic payload.

Recommended fields:

- `id`
- `entity` (`employee` | `material`)
- `operation` (`create` | `update` | `activate` | `deactivate`)
- `endpoint`
- `method`
- `body`
- `status` (`pending` | `synced` | `error`)
- `retries`
- `createdAt`
- `updatedAt`
- `lastError`
- optional `requestKey` or `idempotencyKey`

This allows replay logic to be centralized instead of re-encoded per UI component.

### 3) Move replay orchestration to connectivity events

Use `ConnectivityProvider` as the reconnect trigger and keep the replay executor in the sync service.

Flow:

1. Browser comes online
2. Provider sets `isOnline = true`
3. Provider or a small sync hook calls the queue replay executor
4. Executor refreshes auth if needed
5. Executor processes queued operations in order
6. Status updates move `pending -> synced` or `pending -> error`

This avoids scattering reconnect logic across employees/materials screens.

### 4) Route supported mutations through the queue-aware API layer

Keep `apiClient` as the main outbound transport, but let it enqueue operations when offline or when a request fails due to network loss.

Supported offline operations:

- employee create
- employee activate/deactivate
- material create
- material edit

Unsupported offline operation:

- material delete

The direct REST calls in the current employee/material code should be normalized to call a queue-aware service path so the same fallback behavior is used everywhere.

### 5) Preserve local intent on conflict

Apply the chosen local-wins policy during replay reconciliation.

Meaning:

- local queued changes remain the source of truth for the replayed request
- a successful replay updates the local UI state to match the acknowledged server response
- we do not auto-discard a pending operation simply because the server state changed while offline

### 6) Fix queue retry correctness before expansion

`src/services/sync/syncManager.ts` currently re-adds the same operation id and then deletes it, which can delete the retried record.

Design correction:

- update the existing record in place when retrying
- never delete a retry target before the new retry record is durable
- only clear operations after successful sync or intentional cleanup of fully synced items

## Tradeoffs

### Option A: Keep sync logic inside `apiClient`

**Pros**

- Minimal call-site changes
- Easy to fallback to enqueue on network failure

**Cons**

- Can become a god object
- Harder to reason about replay policy and business rules

### Option B: Add a dedicated offline command service layer

**Pros**

- Clear separation of transport vs queueing vs business rules
- Easier to test and extend

**Cons**

- Slightly more wiring at call sites

### Recommended choice

Use a thin queue-aware service layer above `apiClient`, not inside every component. Keep `apiClient` as the transport primitive and let the service layer decide when to enqueue.

## Data Flow

### Online request path

Component -> domain service -> apiClient -> backend -> response -> UI state refresh

### Offline request path

Component -> domain service -> apiClient detects offline/network failure -> queue operation in IndexedDB -> UI marks pending -> later replay executor sends request -> status becomes synced/error

### Reconnect path

ConnectivityProvider -> replay executor -> auth revalidation if online -> process queue -> update statuses -> refresh UI caches where needed

## Functional Boundaries

### In scope

- persisted auth snapshot behavior
- IndexedDB queue model and replay executor
- employee create/activate/deactivate sync
- material create/edit sync
- queue status reporting
- offline-safe retries and error retention

### Out of scope

- material delete sync
- unrelated offline support for payroll/tasks/works/quotations
- new backend endpoints unless required by existing contract
- full-blown conflict resolution UI

## Testing Strategy

- Unit test queue status transitions and retry behavior
- Unit test auth snapshot behavior when offline vs online
- Integration-style test for reconnect-triggered replay
- Verify material deletion is excluded from queueing
- Verify unsupported offline actions do not lose local intent

## Risks and Mitigations

- **Risk**: stale auth token during replay
  - **Mitigation**: revalidate online before flush and refresh token from Firebase when possible
- **Risk**: duplicate replay submissions
  - **Mitigation**: include durable request keys and make replay idempotent where possible
- **Risk**: UI still disables offline actions in some screens
  - **Mitigation**: update all known employee/material action gates to depend on support rules, not raw connectivity alone
- **Risk**: retry bug causes data loss
  - **Mitigation**: fix in-place retry updates before wiring replay into reconnect handling
