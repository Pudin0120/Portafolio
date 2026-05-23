# Proposal: route-acceptance-criteria

**Status**: Proposal  
**Created**: 2026-05-19  
**Target**: Define clear acceptance criteria for each route/layout in the app

---

## Problem

Currently there's no clear definition of when a route is "ready" or "in a good state". This leads to:

- Unpredictable test results (don't know what to wait for)
- Silent regressions (features break without detection)
- Inconsistent user experience (some pages load oddly, some don't)
- Hard to debug: "Is this page supposed to show empty? Or is it broken?"

**Examples of Unclear States**:

- `ProtectedView`: When is it "done"? (auth check complete? user loaded? role resolved?)
- `DashboardLayout`: When can user interact? (sidebar ready? all contexts loaded?)
- `MaterialsManager`: When is list ready? (initial fetch done? search settled?)
- `EmployeesDashboardPage`: When is profile visible? (hydration complete? all tabs ready?)

**Impact**:

- E2E tests flaky (wait for inconsistent conditions)
- Manual testing unpredictable (don't know when to try interactions)
- PR reviews lack clear acceptance signals

---

## Solution Direction

Define **Acceptance Criteria per Route**: a set of observable conditions that indicate the route is fully ready and interactive.

**Pattern**:

```typescript
// Example: MaterialsManager acceptance criteria
OK Materials list visible (not empty state, not loading spinner)
OK Search input interactive
OK First material card rendered with image + name
OK Action buttons (create, edit, delete) functional
OK Pagination controls visible if paginated
```

**Deliverable**:

- Document file: `docs/ROUTE_ACCEPTANCE_CRITERIA.md`
- Per-route checklist of observable states
- Test helpers (e.g., `waitForRoute(path)` assertion)
- E2E test samples showing correct wait strategies

---

## Scope

### In Scope

- Define acceptance criteria for all major routes:
  - `ProtectedView` (wrapper)
  - `DashboardLayout` (main container)
  - `DashboardPage` (client view)
  - `EmployeeDashboardPage` (employee view)
  - `MaterialsManager`, `EmployeesManager` (data pages)
  - `CreateMaterial`, `CreateEmployee` (modals/forms)
- Write test helpers to verify each criteria
- Document in accessible format (markdown + code examples)

### Out of Scope

- Changing UI implementations
- Adding new loading skeletons
- Changing animation timings
- Refactoring navigation logic

---

## Acceptance Criteria

- [ ] `docs/ROUTE_ACCEPTANCE_CRITERIA.md` created with 8 route definitions
- [ ] Each route has 3 observable acceptance signals
- [ ] Test helpers in `src/test-helpers/routeAcceptance.ts` cover all routes
- [ ] E2E tests use new helpers (no more ad-hoc `page.waitForTimeout`)
- [ ] Criteria docs reviewed for clarity + accuracy
- [ ] All existing tests still pass using new helpers

---

## Non-Goals

- Implement UI changes for better loading states
- Add loading skeletons
- Change CSS animations

---

## Workload Estimate

- **Files**: ~4-5 new/modified (docs, test helpers, test updates)
- **Lines**: ~300-400 LOC (docs + helpers)
- **Commits**: 2-3 (docs, helpers, test updates)
- **Duration**: 90-120 min
- **Review Risk**: Low (mostly docs + helpers, not product logic)

---

## Examples

**Route**: `ProtectedView`

```
OK User is authenticated OR session snapshot exists
OK Role is resolved (not null)
OK Child route (e.g., DashboardPage) is attempting to render
OK "Verificando autenticacion..." loading state has passed
```

**Route**: `MaterialsManager`

```
OK Materials list table is visible
OK At least 1 material row exists OR "Sin materials" message shown
OK "Create Material" button is clickable
OK Search input is responsive (typing updates list)
```

**Route**: `EmployeeDashboardPage`

```
OK User profile card is visible (with name, email)
OK Tab navigation is interactive (can click between tabs)
OK Current tab content is rendered (e.g., home page shows employee info)
OK Navigation breadcrumbs visible
```

---

## Next Steps

1. **Explore**: Map all routes/pages in app, identify observable signals
2. **Spec**: Detail each route's acceptance criteria
3. **Design**: Create test helper architecture
4. **Implement**: Write docs + helpers + test updates
5. **Verify**: Run full E2E suite with new helpers
