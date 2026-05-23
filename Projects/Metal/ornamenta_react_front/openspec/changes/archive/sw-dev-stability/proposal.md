# Proposal: sw-dev-stability

**Status**: Proposal  
**Created**: 2026-05-19  
**Target**: Stabilize dev server and SW, implement update notifications, activate sync on build changes

---

## Problem

**Issue 1: Dev server stuck loading**

- When `bun run dev` starts, app loads infinitely without manual `Ctrl+Shift+R`
- Root: Service worker serves stale bundle from preview session
- Asset URLs mismatch, hot reload breaks, modules can't resolve
- Impact: DX broken, dev workflow blocked

**Issue 2: Service worker doesn't notify on build changes**

- User builds new version, but SW continues serving old code
- No mechanism to invalidate old cache or notify app of new version
- Users stuck on old version unless they clear storage manually
- Impact: Deployed fixes don't reach users, cache pollution

**Issue 3: Sync queue doesn't auto-activate**

- Sync queue exists but isn't wired to auto-trigger on reconnect
- Even when online, pending operations may not replay
- Only manual page reload triggers sync
- Impact: Offline mutations stuck forever until hard refresh

**Current Flow** (Broken):

```
Dev:
1. bun run dev  vite starts on localhost:5173
2. SW (from previous preview) intercepts requests
3. Assets don't load  infinite loading spinner

Production:
1. User on v1.0, all cached
2. Deploy v2.0
3. SW keeps serving v1.0 cache
4. User manually clears storage to see v2.0
5. Offline mutations never replay (no wiring)
```

---

## Solution Direction

**For Dev Server**:

- Detect dev vs. preview mode in SW
- Skip caching for localhost:5173 during dev (or use different cache name)
- Clear stale cache on dev server startup

**For Update Notifications**:

- SW posts `message` event when new version detected
- App listens and shows "Update available" prompt
- User can refresh to load new version
- Optional auto-refresh after delay

**For Sync Activation**:

- Wire reconnect event to trigger `syncPendingOperations()` automatically
- Ensure sync runs after auth hydration completes
- Add tests verifying sync executes on reconnect

---

## Scope

### In Scope

1. **Dev Server Stability** (~100 LOC):
   - Update `vite.config.ts` to skip SW precache during dev
   - Or: configure separate cache strategy for dev mode
   - Test: start dev server, confirm app loads without force reload

2. **Update Notifications** (~150 LOC):
   - SW detects new version (e.g., via `__WB_MANIFEST` checksum)
   - Posts `message` to clients
   - App shows "Update available" banner
   - User can click "Refresh" or auto-refresh after timeout

3. **Sync Auto-Activation** (~100 LOC):
   - ConnectivityProvider emits event on `isOnline=true`
   - usePersistentAuth or DashboardLayout listens
   - Triggers `syncPendingOperations()` automatically
   - Tests verify sync completes after offline operation + reconnect

### Out of Scope

- Changing SW caching strategies globally (only dev-specific fixes)
- Rewriting sync manager
- Changing auth flow
- UI redesign for update banner

---

## Acceptance Criteria

- [ ] Dev server starts, app loads to dashboard without `Ctrl+Shift+R`
- [ ] No console errors about failed module loads in dev
- [ ] Production build generates SW with update detection
- [ ] App shows "Update available" banner when new version deployed
- [ ] Sync queue auto-triggers on reconnect (online state change)
- [ ] Offline mutation  go online  queue replays automatically
- [ ] Tests green: sync flow, dev server, update notifications
- [ ] Build passes with Infisical injection

---

## Non-Goals

- Change sync queue data structure
- Implement persistent update preferences
- Add analytics tracking for updates
- Change offline-first strategy

---

## Workload Estimate

- **Files**: ~5-7 modified (vite.config.ts, sw.ts, usePersistentAuth.ts, ConnectivityProvider, tests)
- **Lines**: ~300-400 LOC
- **Commits**: 3-4 (dev fix, update notifications, sync wiring)
- **Duration**: 2-3 hours
- **Review Risk**: Medium (touches SW, connectivity, tests)

---

## Technical Details

### Dev Server Fix

```typescript
// vite.config.ts
export default defineConfig({
  plugins: [
    VitePWA({
      strategies:
        process.env.NODE_ENV === "production" ? "injectManifest" : "generateSW",
      // OR: disable SW caching for localhost in dev
    }),
  ],
});
```

### Update Notification Flow

```
SW:
1. Check __WB_MANIFEST hash changes
2. If changed: self.clients.matchAll()  post {type: 'UPDATE_AVAILABLE'}

App:
1. navigator.serviceWorker.onmessage listener
2. Show banner "Nouv version disponible"
3. User clicks "Actualizar"  location.reload()
```

### Sync Auto-Trigger

```
ConnectivityProvider:
emit 'reconnected' event when isOnline: falsetrue

usePersistentAuth or DashboardLayout:
useEffect(() => {
  if (!isOnline) return;
  void syncPendingOperations(); // auto-replay queue
}, [isOnline]);
```

---

## Risks

| Risk                       | Mitigation                                             |
| -------------------------- | ------------------------------------------------------ |
| SW update breaks offline   | Keep old SW running during transition, gradual rollout |
| Auto-sync runs too often   | Debounce reconnect, track last sync timestamp          |
| Dev cache collision        | Use separate cache names for dev/prod                  |
| Users ignore update prompt | Add timeout auto-refresh + persisten banner            |

---

## Next Steps

1. **Explore**: Verify current SW behavior, vite config, sync wiring
2. **Spec**: Detail update detection algorithm + sync trigger points
3. **Design**: SW message protocol, app listener architecture
4. **Implement**: Apply fixes with tests
5. **Verify**: Test dev server, build + production update flow
