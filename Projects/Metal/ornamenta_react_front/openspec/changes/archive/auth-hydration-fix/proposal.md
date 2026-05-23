# Proposal: auth-hydration-fix

**Status**: Proposal  
**Created**: 2026-05-19  
**Target**: Eliminate "Sin rol asignado" flash during app initialization

---

## Problem

When the app initializes, users briefly see the "Sin rol asignado" (no role assigned) screen before the proper dashboard loads. This creates a poor UX experience and indicates async hydration issues in the auth flow.

**Root Cause**:

- `usePersistentAuth()` triggers `syncUserProfile()` asynchronously
- `setLoading(false)` executes before `syncUserProfile()` completes
- React renders `DashboardPage` with `userRole=null` momentarily
- Only after profile syncs does `userRole` update and correct page displays

**Current Flow** (Broken):

```
1. Firebase onAuthStateChanged fires
2. setUser(currentUser)
3. setLoading(false)   TOO EARLY
4. DashboardPage renders with userRole=null  "Sin rol asignado" flash
5. Async syncUserProfile() finishes
6. setUserRole(newRole)  renders correct page
```

**Impact**:

- UX broken: visual jarring, confuses users
- Inconsistent: sometimes appears, sometimes doesn't (network timing dependent)
- Regression: users report "app looks broken"

---

## Solution Direction

Ensure `userRole` is always resolved **before** `loading` is set to `false`.

**New Flow** (Proposed):

```
1. Firebase onAuthStateChanged fires
2. setUser(currentUser)
3. Await syncUserProfile() to complete (fetch /users/me)
4. setUserRole(resolvedRole) + setUserState(resolvedState)
5. THEN setLoading(false)
6. DashboardPage renders with correct userRole
```

**Key Changes**:

- Reorder effect logic: don't set `loading=false` until role is resolved
- Use intermediary state (e.g., `hydrating=true`) if needed
- Ensure offline scenario still works (use snapshot role if no network)

---

## Scope

### In Scope

- Fix `usePersistentAuth()` hydration order
- Ensure no flash of wrong role
- Maintain offline-first behavior (use snapshot as fallback)
- Update tests to verify no flash occurs

### Out of Scope

- Changing auth architecture
- Changing UI components (ProtectedView, DashboardLayout)
- Storage mechanism changes

---

## Acceptance Criteria

- [ ] No "Sin rol asignado" appears at app startup
- [ ] `userRole` resolved before `loading=false` in all paths (online + offline)
- [ ] Offline snapshot role used immediately without network wait
- [ ] Tests verify role is present before dashboard renders
- [ ] Build passes with 6+ tests green

---

## Non-Goals

- Add loading skeleton (out of scope for this fix)
- Change auth persistence strategy
- Refactor ConnectivityProvider

---

## Workload Estimate

- **Files**: ~2-3 modified (usePersistentAuth.ts, DashboardPage.tsx, maybe tests)
- **Lines**: ~50-100 LOC
- **Commits**: 1-2
- **Duration**: 30-60 min
- **Review Risk**: Low (isolated auth logic)

---

## Risks

| Risk                 | Mitigation                                        |
| -------------------- | ------------------------------------------------- |
| Breaks offline flow  | Ensure snapshot role always available as fallback |
| Async race condition | Use ref + proper dependency array                 |
| Mobile timing issues | Test on slow network (Throttle 3G in DevTools)    |

---

## Next Steps

1. **Explore**: Verify current auth flow in usePersistentAuth + DashboardPage
2. **Spec**: Detail exact async ordering required
3. **Design**: Pick strategy (move await earlier, or use intermediary state)
4. **Implement**: Apply fix with tests
5. **Verify**: Confirm no flash appears
