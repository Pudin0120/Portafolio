## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~220-320 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | single PR |
| Delivery strategy | single-pr |

Decision needed before apply: No
Chained PRs recommended: No

## Implementation Order

1. **RED - lock the lifecycle contract with helper tests**
   - Add a focused test file for the PWA/dev lifecycle helpers and reconnect trigger helpers.
   - Cover these cases:
     - dev mode cleanup is only enabled in dev;
     - the update prompt contract exists and exposes an update action;
     - reconnect signaling is explicit and can be observed by the sync path.
   - Keep the test surface small and pure where possible.

2. **GREEN - add dev-only service worker cleanup before bootstrap**
   - Add a small utility to unregister stale service workers and clear stale caches when `import.meta.env.DEV` is true.
   - Call it before the React tree renders in `src/main.tsx`.
   - Ensure the cleanup is skipped in production.

3. **GREEN - switch the PWA registration to prompt-based updates**
   - Update `vite.config.ts` so the app uses prompt-based update behavior.
   - Update the custom service worker in `public/sw.ts` to support skip-waiting messages instead of auto-skipping on install.
   - Update the app-side PWA hook so it can surface `needRefresh` and invoke the update action.

4. **TRIANGULATE - render the update prompt in the app shell**
   - Add a small, themeable update banner component.
   - Render it from the app shell so the user can refresh when a new build is waiting.
   - Keep the banner non-invasive and independent from route rendering.

5. **GREEN - make reconnect replay explicit**
   - If needed, extend `ConnectivityProvider` with a reconnect epoch or counter.
   - Ensure the sync path observes that reconnect signal instead of relying on timers.
   - Preserve the existing auto-replay behavior for supported pending operations.

6. **VERIFY - run the full test suite**
   - Validate with `bun run test`.
   - Confirm the dev/update/sync helpers remain compatible with the existing auth and route SDD changes.

## Files to Touch

- `vite.config.ts`
- `public/sw.ts`
- `src/main.tsx`
- `src/hooks/useServiceWorker.ts`
- `src/components/common/UpdateAvailableBanner.tsx`
- `src/providers/ConnectivityProvider.tsx`
- `src/hooks/usePersistentAuth.ts`
- `src/services/pwa/devServiceWorkerCleanup.ts`
- `tests/sw-dev-stability.spec.ts`

## Verification

- Run `bun run test` after the helpers and app shell changes are in place.
- Prefer helper-level assertions for the lifecycle contract.
- Keep the change inside the PWA/dev lifecycle and reconnect trigger scope.
