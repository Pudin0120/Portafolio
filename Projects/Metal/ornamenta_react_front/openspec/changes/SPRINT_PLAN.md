# Sprint Planning: PWA Quality & Stability (3-Part SDD)

**Created**: 2026-05-19  
**Scope**: Three sequential micro-SDDs to fix auth flashes, define route acceptance, and stabilize dev/build

---

## Overview

After `pwa-auth-sync-state` (Reconnect + Cache), we've identified 4 critical issues blocking production quality:

1. **Auth Flash**: "Sin rol asignado" appears momentarily (UX broken)
2. **Dev Server Dead**: App loads infinitely without force reload (DX broken)
3. **No Acceptance Criteria**: Routes lack clear "ready" signals (testing hard)
4. **Cache/Sync Dead**: Build doesn't trigger update notifications or sync (production risk)

**Strategy**: Break into **3 sequential micro-SDDs**, each with tight scope and fast implementation. Execute in order; each adds value independently.

---

## Phase 1: `auth-hydration-fix`

**Priority**:  HIGH  
**Effort**: ~50-100 LOC, 30-60 min  
**Goal**: Eliminate "Sin rol asignado" flash

### What

- Fix async ordering in `usePersistentAuth()`
- Ensure `userRole` resolved **before** `loading=false`
- Use snapshot role as offline fallback (no network wait)

### Outcome

- No flash at startup
- Role always present when dashboard renders
- Offline still works (uses snapshot immediately)

### Files

- `src/hooks/usePersistentAuth.ts`
- `src/pages/DashboardPage.tsx` (maybe)
- Tests + verification

### Success Criteria

```
OK App starts: role visible immediately, no "Sin rol asignado"
OK Offline: uses snapshot role, renders without waiting
OK Online: fetches profile, updates role
OK Tests verify no flash occurs
```

---

## Phase 2: `route-acceptance-criteria`

**Priority**:  MEDIUM  
**Effort**: ~300-400 LOC, 90-120 min  
**Goal**: Define clear "ready" signals for each route

### What

- Document acceptance criteria per route (ProtectedView, DashboardLayout, pages, etc.)
- Create test helpers (`waitForRoute`, `assertRouteReady`, etc.)
- Update E2E tests to use helpers instead of ad-hoc waits

### Outcome

- E2E tests reliable (wait for clear conditions)
- Manual testing predictable (know when to interact)
- Developers have checklist for new routes
- Regressions easier to catch

### Deliverables

- `docs/ROUTE_ACCEPTANCE_CRITERIA.md` (8+ routes)
- `src/test-helpers/routeAcceptance.ts` (helpers)
- Updated E2E tests using helpers
- Examples + patterns for future routes

### Success Criteria

```
OK Docs cover all major routes with 3 signals each
OK Test helpers work across all E2E tests
OK No more ad-hoc page.waitForTimeout() calls
OK Tests consistently pass (no flakiness)
```

---

## Phase 3: `sw-dev-stability`

**Priority**:  HIGH (Dev) /  MEDIUM (Production)  
**Effort**: ~300-400 LOC, 2-3 hours  
**Goal**: Fix dev server, add update notifications, wire sync auto-trigger

### What

**Part A: Dev Server** (~100 LOC)

- Fix vite.config.ts or SW to not cache localhost:5173 during dev
- Clear stale cache on dev startup
- Test: start dev, app loads without force reload

**Part B: Update Notifications** (~150 LOC)

- SW detects new build (via manifest checksum)
- Posts `message` to clients with `{type: 'UPDATE_AVAILABLE'}`
- App shows "Update available" banner
- User can refresh or auto-refresh after timeout

**Part C: Sync Auto-Activation** (~100 LOC)

- ConnectivityProvider emits event on `isOnline: falsetrue`
- usePersistentAuth or DashboardLayout listens
- Triggers `syncPendingOperations()` automatically
- Tests verify: offline op  online  queue replays

### Outcome

- Dev server works smoothly (no force reload needed)
- Users see updates when deployed (not stuck on old version)
- Offline mutations auto-sync when reconnected
- Production cache reliability improved

### Files

- `vite.config.ts`
- `public/sw.ts`
- `src/hooks/usePersistentAuth.ts` or `src/components/DashboardLayout.tsx`
- `src/providers/ConnectivityProvider.tsx` (emit events)
- Tests + verification

### Success Criteria

```
OK bun run dev: app loads to dashboard without Ctrl+Shift+R
OK No console errors about module resolution in dev
OK Deploy new build: app shows "Update available" banner
OK User clicks "Actualizar": loads new version
OK Offline mutation  reconnect: queue auto-replays
OK All tests green (sync, dev, update flow)
```

---

## Phase 4: `connectivity-api-routing-fix`

**Priority**:  HIGH (Data correctness)
**Effort**: ~150-250 LOC, 60-90 min
**Goal**: Stop the app from misclassifying online API reads as offline, and vice versa

### What

- Separate real offline transport from auth/session state
- Ensure online GETs for materials/products still fire when the browser is online
- Prevent quotation flows from forcing the opposite transport assumption
- Keep offline queueing only for true offline/network-failure cases

### Outcome

- Online users fetch fresh backend data normally
- Offline users still use supported queueing/sync behavior
- Auth errors no longer masquerade as connectivity failures
- Request routing is explicit instead of cache-driven

### Files

- `src/services/apiClient.ts`
- `src/providers/ConnectivityProvider.tsx`
- `src/services/sync/syncManager.ts`
- Relevant data-loading screens for materials/products/quotations
- Tests + verification

### Success Criteria

```
OK Online browser => expected GETs fire for materials/products
OK Authenticated session => no false "No hay user autenticado" from transport misclassification
OK Offline browser => supported queueing still works
OK Quotation flows respect the correct transport assumption
OK bun run test passes
```

---

## Execution Plan

### Timeline

```
Sprint N+1:
  Day 1: `auth-hydration-fix` (explore  implement  verify)
  Day 2: `route-acceptance-criteria` (design  docs  helpers  tests)
  Day 3: `sw-dev-stability` (part A + B + C  integration tests  verify)
```

### Per Micro-SDD Flow

```
SDD Init
  
Explore (read current code)
  
Proposal (already done! )
  
Spec (detail exact changes needed)
  
Design (architecture decisions)
  
Tasks (implementation breakdown)
  
Apply (code changes)
  
Verify (tests + manual check)
  
Archive (record learnings)
```

### Commits Strategy

Each micro-SDD generates 1-2 commits:

- `feat(auth): fix hydration flash -- avoid "sin rol" momentaneamente`
- `docs(route-acceptance): define acceptance criteria per route + test helpers`
- `fix(sw): stabilize dev server + add update notifications`
- `feat(sync): wire auto-activation on reconnect`

**Total**: ~4-6 commits, organized by concern

### PR Strategy

- **Option A**: 1 PR covering all 3 (not recommended, too big)
- **Option B**: 3 PRs, one per micro-SDD (recommended)
  - PR1: auth-hydration-fix (small, fast review)
  - PR2: route-acceptance-criteria (docs + helpers, straightforward)
  - PR3: sw-dev-stability (most complex, but scoped)

---

## Dependencies & Blockers

| SDD                | Blocks          | Blocked By             | Ready? |
| ------------------ | --------------- | ---------------------- | ------ |
| Phase 1 (auth)     | Phase 2, 3      | None                   | OK     |
| Phase 2 (route AC) | Phase 3 (maybe) | Phase 1 (nice to have) | OK     |
| Phase 3 (SW)       | None            | None                   | OK     |

**Note**: Phases are **independent** but **sequential** for code review + merge order.

---

## Risk Mitigation

| Risk                       | Phase | Mitigation                                   |
| -------------------------- | ----- | -------------------------------------------- |
| Auth fix breaks offline    | 1     | Extensive testing with/without network       |
| Route AC too rigid         | 2     | Make criteria advisory, not enforced in code |
| Dev server cache collision | 3A    | Use separate cache names, clear on dev start |
| Update prompt spams users  | 3B    | Add "remind me later" + debounce + timeout   |
| Sync auto-trigger loops    | 3C    | Debounce reconnect, track last sync time     |

---

## Deliverables Checklist

### Phase 1 

- [ ] usePersistentAuth.ts updated (no role flash)
- [ ] Tests verify hydration order
- [ ] Offline fallback works
- [ ] 6+ tests green

### Phase 2 

- [ ] ROUTE_ACCEPTANCE_CRITERIA.md (8 routes)
- [ ] routeAcceptance.ts helpers
- [ ] All E2E tests use helpers
- [ ] Docs reviewed + merged

### Phase 3 

- [ ] Dev server works without force reload
- [ ] Update notification banner appears + works
- [ ] Sync auto-triggers on reconnect
- [ ] All tests green
- [ ] Build passes with Infisical

---

## Next: SDD Init for Phase 1

Ready to start Phase 1 (`auth-hydration-fix`) immediately after planning approval.

Choose execution mode:

- **Interactive**: Pause between phases, ask for approval
- **Auto**: Run all 3 back-to-back (fast, less ceremony)

**Recommended**: Interactive (allows feedback after Phase 1 + 2)
