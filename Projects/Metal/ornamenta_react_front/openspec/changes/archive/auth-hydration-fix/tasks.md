## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~140-220 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | single PR |
| Delivery strategy | single-pr |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

## Implementation Order

1. **RED - lock the hydration regression with tests first**
   - Add a focused Playwright spec in `tests/auth-hydration-fix.spec.ts` **or** extend `tests/pwa-auth-sync-state.spec.ts` with the startup scenarios below.
   - Cover these cases with deterministic assertions:
     - authenticated snapshot present + online + profile refresh pending => route gate stays blocked and no `"Sin rol asignado"` flash is possible;
     - unauthenticated startup => auth finishes in the unauthenticated state;
     - fully hydrated authenticated session with `userRole === null` => the fallback is allowed.
   - Keep the test surface narrow; prefer pure helper assertions over DOM-only checks if that avoids a heavy browser harness.
   - Validate with `bun run test` and confirm the new expectation fails before code changes.

2. **GREEN - make hydration terminal only in `src/hooks/usePersistentAuth.ts`**
   - Keep snapshot-first restoration intact: apply the persisted snapshot immediately when present and do not clear it while remote revalidation is still pending.
   - Introduce or expose a small readiness signal for the current startup session so `loading`/ready state stays unresolved until one of these terminal outcomes is reached:
     - snapshot applied and usable,
     - remote profile resolved,
     - confirmed unauthenticated.
   - Preserve offline behavior: if a valid snapshot exists and the device is offline, the snapshot must remain usable without waiting for network revalidation.
   - If the hook exposes a new readiness field, update `src/types/auth.ts` to match and keep `src/context/AuthContext.tsx` as a thin pass-through.
   - Re-run `bun run test` after the hook change.

3. **GREEN - keep authenticated route rendering gated in `src/App.tsx`**
   - Continue blocking the protected route tree while auth hydration is not ready for the current session.
   - Use the hook's readiness/loading signal as the single startup gate for the authenticated shell.
   - Preserve the existing login route behavior and `LoadingState` presentation; do not add a new splash/skeleton.
   - Confirm the dashboard routes only render after readiness is terminal by re-running `bun run test`.

4. **TRIANGULATE / REFACTOR - make `src/pages/DashboardPage.tsx` terminal-only for the no-role fallback**
   - Treat `"Sin rol asignado"` as a terminal fallback only; do not let it represent in-progress hydration.
   - Add a guard so the page does not render the no-role branch until auth hydration has finished for the current session.
   - Preserve the inactive-account branch and the logout action from the terminal no-role state.
   - Keep the role-specific branch selection unchanged once hydration is complete.
   - Update the auth-related spec(s) so they verify:
     - the fallback does not appear during startup hydration,
     - the fallback does appear after hydration completes with a null role,
     - authenticated route rendering remains blocked until ready.
   - Finish with a full `bun run test` run.
