# Design: route-acceptance-criteria

## Goal

Create a single source of truth for when major routes are considered ready, so tests can wait on visible UI signals instead of timing guesses.

## Problem

The app has many route shells and manager pages, but no shared definition of "ready". Tests therefore either:

- wait too early and flake;
- wait too late and slow the suite down;
- or use ad-hoc delays that hide regressions.

The change should not alter navigation or product behavior. It should only standardize route readiness semantics for tests and reviewers.

## Options Considered

### Option 1 - Static route metadata registry + helper functions

Create a typed registry that maps route keys to readiness signals, recommended selectors, and notes. Export helper functions to read the metadata and wait/assert readiness in tests.

**Pros**

- Single source of truth.
- Easy to audit and update.
- Works for both docs and tests.
- Low behavioral risk.

**Cons**

- Requires keeping metadata in sync with UI changes.

### Option 2 - Scatter route-specific helpers near each page/component

Add a dedicated helper near each route implementation.

**Pros**

- Localized knowledge.

**Cons**

- Harder to discover.
- Duplicates logic.
- Makes tests harder to standardize.

### Option 3 - Encode readiness in runtime `data-testid` markers across the app

Add explicit readiness test IDs to every route shell.

**Pros**

- Very explicit.
- Strong selectors.

**Cons**

- Requires UI changes across many files.
- Larger review surface.
- More invasive than necessary for this sprint.

## Recommendation

**Choose Option 1.**

A metadata registry plus helper functions is the smallest useful abstraction. It lets us document readiness, reuse it in tests, and avoid invasive UI changes.

## Proposed Architecture

### 1) `src/test-helpers/routeAcceptance.ts`

Create a typed registry with one entry per major route/shell.

Each entry should define:

- `key` - stable route identifier;
- `label` - human-readable route name;
- `signals` - 3+ observable readiness signals;
- `selectors` - optional recommended selectors or locators;
- `notes` - role-specific constraints or special behavior.

Suggested route keys:

- `protected-view`
- `dashboard-layout`
- `dashboard-page`
- `employee-dashboard`
- `admin-dashboard`
- `manager-dashboard`
- `supervisor-dashboard`
- `materials-manager`
- `employees-manager`
- `products-manager`
- `quotations-manager`
- `works-manager`
- `tasks-manager`
- `payroll-page`

Helper functions should support:

- `getRouteAcceptance(key)`
- `listRouteAcceptanceKeys()`
- `assertRouteAcceptanceCount(key, minSignals = 3)`
- `getRouteReadySignals(key)`
- `waitForRouteReady(page, key)`

The helper should use existing accessible UI where possible: headings, tab labels, table aria-labels, buttons, breadcrumbs, and loading-state disappearance.

### 2) `openspec/changes/route-acceptance-criteria/spec.md`

The spec should describe readiness in observable terms only and stay aligned with the helper registry.

### 3) `docs/ROUTE_ACCEPTANCE_CRITERIA.md`

Create a reviewer-friendly reference that lists the readiness criteria per route in plain language.

It should be derived from the same registry as the helper so the docs and test contract do not drift.

## Route Readiness Model

### Shared readiness principles

Every route should answer the same questions:

1. Is the global loading gate gone?
2. Is the route's main shell visible?
3. Are the primary actions or content visible?
4. Are the route-specific interactive controls ready?

### Route categories

#### Auth shell

- `ProtectedView`
- `DashboardLayout`
- `DashboardPage`

Readiness focuses on the authenticated shell, role resolution, and the disappearance of startup loading.

#### Role dashboards

- `EmployeeDashboardPage`
- `AdminDashboardPage`
- `ManagerDashboardPage`
- `SupervisorDashboardPage`

Readiness focuses on the correct role-specific menu, breadcrumbs, and the visible default tab/section.

#### Data managers

- `MaterialsManager`
- `EmployeesManager`
- `ProductsManager`
- `QuotationsManager`
- `WorksManager`
- `TasksManager`
- `PayrollPage`

Readiness focuses on visible tables/tabs, action buttons, search/filter inputs, and the absence of the initial loading skeleton.

## Test Strategy

- Add a narrow route acceptance test file that validates the registry itself.
- Prefer helper-driven assertions over ad-hoc waits in any future E2E updates.
- Keep tests purely declarative where possible: verify the registry, not the full browser flow.

## Tradeoffs

- A static registry is only as accurate as the UI it documents; the benefit is that drift becomes obvious during review.
- Using existing UI labels keeps the change low-risk, but some routes may need one or two helper selectors refined as the suite matures.
- We should avoid overfitting to every component variant; route-level readiness is enough for now.

## Outcome

This design gives the team one route readiness vocabulary across docs and tests, without changing the app's runtime behavior.
