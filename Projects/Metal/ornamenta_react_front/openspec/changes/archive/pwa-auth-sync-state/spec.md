# Delta Spec: pwa-auth-sync-state

## Goal

Preserve the authenticated session across offline periods and synchronize supported employee/material mutations from IndexedDB once connectivity returns.

## Requirements

### R1. Persisted auth session survives offline

The client MUST preserve the authenticated session snapshot when the browser goes offline.

#### Scenario: offline refresh retains session

- **Given** the user is signed in and a valid local auth snapshot exists
- **When** the browser goes offline or the app reloads offline
- **Then** the app MUST continue treating the user as authenticated from the persisted snapshot
- **And** it MUST NOT clear the snapshot solely because Firebase cannot revalidate offline

#### Scenario: online revalidation only when connectivity returns

- **Given** a persisted auth snapshot exists
- **When** connectivity returns
- **Then** the client MUST revalidate the current Firebase user online
- **And** it MUST refresh the stored snapshot only after successful online validation

### R2. IndexedDB stores queued operations

The client MUST store supported offline mutations in IndexedDB as pending operations.

#### Scenario: offline mutation is queued

- **Given** the user performs a supported operation while offline
- **When** the mutation cannot be sent to the backend
- **Then** the client MUST persist a pending operation in IndexedDB
- **And** it MUST keep the original intent payload
- **And** it MUST record retry metadata and sync status

### R3. Sync states are tracked consistently

Each queued operation MUST have a sync status of `pending`, `synced`, or `error`.

#### Scenario: successful replay updates status

- **Given** a pending operation is replayed successfully online
- **When** the backend returns success
- **Then** the operation status MUST become `synced`

#### Scenario: repeated failure marks error

- **Given** a pending operation fails repeatedly beyond the retry budget
- **When** the client cannot recover automatically
- **Then** the operation status MUST become `error`
- **And** the queued data MUST remain available for recovery rather than being deleted

### R4. Reconnect triggers automatic replay

The client MUST automatically replay pending operations when connectivity returns.

#### Scenario: online event flushes queue

- **Given** there are pending supported operations in IndexedDB
- **When** the browser transitions from offline to online
- **Then** the client MUST attempt replay without requiring manual refresh
- **And** it MUST process operations in a deterministic order

### R5. Replay uses REST POST/operation requests

The sync layer MUST send queued operations through the backend REST contract used for supported mutations.

#### Scenario: create/activate/deactivate employee replays

- **Given** a queued employee create, activate, or deactivate operation exists
- **When** replay runs online
- **Then** the client MUST POST or PATCH the corresponding REST request required by the backend contract
- **And** it MUST reconcile the local view after success using local-wins intent

#### Scenario: create/edit material replays

- **Given** a queued material create or edit operation exists
- **When** replay runs online
- **Then** the client MUST POST or PATCH the corresponding REST request required by the backend contract
- **And** it MUST reconcile the local view after success using local-wins intent

### R6. Network errors do not lose data

Network failures MUST not remove queued operations or discard local intent.

#### Scenario: transient network failure preserves queue item

- **Given** a supported mutation fails because of a network error
- **When** the request cannot complete
- **Then** the operation MUST remain queued
- **And** it MUST keep enough data to retry later

### R7. Business rules restrict sync coverage

Only explicitly supported operations MAY enter replay.

#### Scenario: material deletion is not synced

- **Given** the user deletes a material
- **When** the deletion occurs
- **Then** the deletion MUST continue using the normal online flow
- **And** it MUST NOT be enqueued for offline replay

#### Scenario: unsupported operations are excluded

- **Given** an operation is outside the supported offline scope
- **When** it is performed offline
- **Then** the client MUST NOT claim it will synchronize later

### R8. UI no longer blocks supported offline actions

The UI MUST allow supported employee/material actions while offline instead of disabling them solely because there is no connection.

#### Scenario: employee edit remains available offline

- **Given** the user is offline
- **When** the user opens supported employee actions
- **Then** the UI MUST not disable those actions only due to connectivity

#### Scenario: material create/edit remains available offline

- **Given** the user is offline
- **When** the user performs supported material create/edit actions
- **Then** the UI MUST allow the action and rely on queueing if the network is unavailable

## Acceptance Criteria

- A signed-in user remains authenticated after offline reload and reconnect.
- Supported employee create/activate/deactivate operations queue offline and replay online.
- Supported material create/edit operations queue offline and replay online.
- Material deletion does not enter the sync queue.
- Replay preserves queued data through transient network failures.
- The sync layer exposes the `pending`, `synced`, and `error` states consistently.
- `bun run test` remains the validation command for the change.
