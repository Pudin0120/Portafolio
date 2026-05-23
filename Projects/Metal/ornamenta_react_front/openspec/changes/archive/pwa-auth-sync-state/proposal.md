# Proposal: pwa-auth-sync-state

## Intent

Enable the frontend to preserve authenticated session state across offline periods and queue supported offline mutations so they synchronize automatically when connectivity returns.

## Problem Statement

Today, the app only partially persists auth state and offline mutation handling is inconsistent. As a result, users can lose session continuity after reconnecting, supported employee/material changes are not reliably queued, and reconnect replay is incomplete. This prevents a smooth offline-to-online experience for field workflows.

## Goals

- Keep the authenticated session available while the user is offline and after the browser reconnects.
- Queue supported operations locally in IndexedDB when the network is unavailable.
- Replay queued operations automatically once connectivity returns.
- Support offline synchronization for:
  - employees: create, activate, deactivate
  - materials: create, edit
- Preserve the current rule that material deletion is not synchronized.
- Remove UI behavior that blocks supported employee/material edits solely because the app is offline.

## Non-Goals

- Syncing material deletion.
- Redesigning the backend API contract.
- Introducing new offline entities beyond employees and materials.
- Implementing conflict resolution beyond the existing local-wins policy.
- Building a full general-purpose offline-first framework for all future features.

## Scope

This change is limited to the auth/session persistence path, the IndexedDB operation queue, reconnect replay behavior, and the employee/material flows that should participate in offline queueing.

## Affected Areas

- `src/hooks/usePersistentAuth.ts`
- `src/services/auth/sessionStorage.ts`
- `src/services/indexedDb/pwaSyncDb.ts`
- `src/services/sync/syncManager.ts`
- `src/services/apiClient.ts`
- employee UI and material UI flows that currently disable or bypass offline-capable actions

## Assumptions

- The existing persistent auth/session storage is the right foundation to extend rather than replace.
- The current IndexedDB queue primitives can be reused for queued operations.
- Reconnect replay should happen automatically without requiring a manual refresh.
- The backend accepts the same operation semantics currently used online for supported create/update/state-toggle actions.
- Local-wins remains the conflict policy for offline edits.

## Open Questions

- Should queued operations be visible to the user in a status indicator, or is silent sync sufficient for this change?
- Should failed replay items be retried automatically with backoff only, or also surfaced for manual recovery?
- Are there any employee/material fields that must be excluded from offline edits even though the entity itself is supported?

## Risks

- Duplicate or out-of-order replay if queue state and reconnect detection are not tightly coordinated.
- Session persistence could mask expired credentials until the next network call if validation is too permissive.
- Existing UI assumptions about offline-disabled editing may conflict with the new queueable behavior.
- The known retry bug in sync manager could cause partial replay failures if not addressed in the same scope.

## Rollback

Rollback should be possible by disabling reconnect replay and offline queuing while leaving the existing online-only flows intact. The persistent auth layer can remain in place if needed, but queue consumption should be gated off cleanly.

## Acceptance Criteria

- A signed-in user can remain authenticated after going offline and returning online without losing session state.
- Supported employee create/activate/deactivate actions can be performed offline and are queued locally.
- Supported material create/edit actions can be performed offline and are queued locally.
- When connectivity returns, queued supported operations sync automatically.
- Material deletion continues to execute outside the offline sync queue.
- The UI no longer blocks supported employee/material changes only because the browser is offline.
- `bun run test` remains the validating test command for this change.

## Success Criteria

- Users can complete a realistic offline-to-online workflow without losing session continuity.
- Queued supported operations are replayed successfully after reconnect with no manual intervention in the common case.
- The implementation stays within the scoped employee/material behaviors and does not broaden offline sync to unrelated features.
