# Delta Spec: sw-dev-stability

## Goal

Improve the development experience by stabilizing the Service Worker lifecycle, ensuring users receive update notifications in production, and automating data synchronization upon reconnection.

## Requirements

### R1. Dev Server Lifecycle Stability

The Service Worker MUST NOT block development updates.

- **Scenario**: Developer changes a file in `src/`.
- **Given** the app is running in development mode.
- **When** the file is saved.
- **Then** the browser MUST reflect the change immediately without a manual "Force Reload" (Ctrl+Shift+R).
- **Technical Constraint**: Stale Service Workers from previous sessions MUST be cleared or bypassed in `localhost`.

### R2. Background Update Checks

The app SHOULD proactively check for new versions without requiring a manual refresh.

- **Scenario**: A new version is deployed to production.
- **Given** a user has the app open.
- **When** the Service Worker registry detects a manifest change.
- **Then** the `UpdateAvailableBanner` MUST appear within a reasonable timeframe (max 1 hour or on focus).

### R3. Automated Reconnect Sync

The app MUST automatically attempt to replay the offline mutation queue when connectivity returns.

- **Scenario**: User performs an offline operation, then regains internet.
- **Given** there are pending operations in IndexedDB.
- **When** `navigator.onLine` transitions from `false` to `true`.
- **Then** the `syncPendingOperations` function MUST be triggered automatically.
- **And** the UI MUST show a syncing indicator during the process.

## Design Decisions

### D1. Dev Mode SW Handling

We will enable `devOptions` in `VitePWA` but ensure that Vite's internal modules (`/@vite/client`, `/@fs/`, etc.) are never cached. We will also implement an "aggressive cleanup" phase in the SW when running on localhost.

### D2. Update Check Interval

Use `registration.update()` every 60 minutes via `setInterval` in the `onRegisteredSW` callback of the PWA registration hook.

### D3. Connectivity Trigger

The `ConnectivityProvider` will host a `useEffect` that watches the `isOnline` state. To prevent multiple sync loops, we will use a `syncing` flag and ensure only one sync process runs at a time.

## Acceptance Criteria

- **Dev Stability**: Making a visible change in `App.tsx` triggers HMR and is visible without a force refresh.
- **Update Banner**: Mocking a SW update (`registration.update()`) triggers the `UpdateAvailableBanner`.
- **Auto-Sync**: Manually toggling "Offline" in DevTools, performing an action, then toggling "Online" triggers a network request for the queued operation.

## Tasks

### Task 1: Stabilize Dev SW

- Update `vite.config.ts` to enable `devOptions`.
- Modify `sw.ts` to skip caching for Vite-specific development paths.

### Task 2: Implement Periodic Update Checks

- Update `useServiceWorker.ts` to include a 1-hour interval check.
- Add a listener for window focus to trigger an immediate check.

### Task 3: Wire Auto-Sync

- Update `ConnectivityProvider.tsx` to watch `isOnline` and call `syncPendingOperations`.
- Add/Update a "Syncing..." UI state in a global toast or status bar.
