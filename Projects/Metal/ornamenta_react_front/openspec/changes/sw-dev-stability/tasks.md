# Tasks: sw-dev-stability

- [ ] **Task 1: SW Dev Stability**
  - [ ] Modify `vite.config.ts`: Set `devOptions.enabled = true`.
  - [ ] Update `public/sw.ts`: Add `denylist` for Vite HMR paths in `NavigationRoute`.
  - [ ] Update `public/sw.ts`: Implement `self.skipWaiting()` and `clients.claim()` more aggressively for dev.

- [ ] **Task 2: Proactive Update Notifications**
  - [ ] Update `src/hooks/useServiceWorker.ts`: Add `setInterval` for `registration.update()`.
  - [ ] Add `visibilitychange` listener to check for updates when user returns to the tab.

- [ ] **Task 3: Reconnect Auto-Sync**
  - [ ] Update `src/providers/ConnectivityProvider.tsx`: Add `useEffect` watching `isOnline`.
  - [ ] Import `syncPendingOperations` and `executePendingOperation`.
  - [ ] Ensure `syncing` state is correctly updated to show UI feedback.

- [ ] **Task 4: Verification**
  - [ ] Verify dev HMR works without force refresh.
  - [ ] Verify update banner appears when mocking a registration update.
  - [ ] Verify offline mutation auto-syncs on network return.
