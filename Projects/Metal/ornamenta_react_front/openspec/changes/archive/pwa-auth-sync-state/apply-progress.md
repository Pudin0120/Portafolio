# Apply Progress: pwa-auth-sync-state

## Completed Tasks

- Stabilized persisted auth session behavior for offline use and online-only revalidation.
- Added replayable IndexedDB operation metadata with `pending | synced | error` status handling.
- Fixed retry handling so retried operations are updated in place instead of being deleted/reinserted unsafely.
- Wired reconnect-driven replay through the auth/connectivity path.
- Routed supported employee mutations through queue-aware service calls.
- Routed supported material create/edit mutations through queue-aware service calls.
- Removed UI blocking for supported employee actions while offline.
- Added focused tests for queue contract behavior.

## Files Changed

- `src/services/sync/pwaSyncContracts.ts`
- `src/services/indexedDb/pwaSyncDb.ts`
- `src/services/sync/syncManager.ts`
- `src/services/apiClient.ts`
- `src/services/userService.ts`
- `src/services/employeeService.ts`
- `src/hooks/usePersistentAuth.ts`
- `src/components/employees/CreateEmployeeModal.tsx`
- `src/components/employees/EmployeesManager.tsx`
- `src/components/products/material-creation/useMaterialForm.ts`
- `tests/pwa-auth-sync-state.spec.ts`
- `openspec/changes/pwa-auth-sync-state/spec.md`
- `openspec/changes/pwa-auth-sync-state/design.md`
- `openspec/changes/pwa-auth-sync-state/tasks.md`

## Test Commands Run

- `bun run test tests/pwa-auth-sync-state.spec.ts`
- `bun run test`
- `bun x tsc --noEmit`  
  - Reported pre-existing repository errors in unrelated files outside this change.
- `bun x tsc --noEmit --pretty false 2>&1 | rg 'useMaterialForm|EmployeesManager|CreateEmployeeModal|userService|employeeService|syncManager|apiClient|usePersistentAuth|pwaSyncContracts|pwaSyncDb'`
  - No errors in changed files.

## TDD Evidence

| Phase | Evidence |
| --- | --- |
| RED | Added `tests/pwa-auth-sync-state.spec.ts` before implementing `src/services/sync/pwaSyncContracts.ts`; test import failed as expected. |
| GREEN | Implemented queue contract helpers and sync plumbing; `bun run test` passed. |
| TRIANGULATE | Verified the helper contract covers creation, supported-ops filtering, retry escalation, and offline error detection. |
| REFACTOR | Simplified queue metadata types, fixed retry mutation flow, and moved offline mutation routing into queue-aware services. |

## Deviations from Design

- Material offline create/edit queueing is wired through `apiClient` and the material form, but the broader material data-loading path still depends on online data for initial fetches.
- Synced queue items are still cleared after replay, matching the current queue cleanup behavior.

## Remaining Tasks

- Broaden offline-safe material UX where forms still depend on live data fetches.
- Consider adding UI badges/toasts for queued vs synced operations.
- Add targeted tests for auth snapshot hydration and reconnect replay if needed.

## Workload / PR Boundary

- Review size stayed within the forecasted small slice.
- This change is suitable as a single PR for the approved scope.
