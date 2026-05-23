# Delta Spec: route-acceptance-criteria

## Goal

Define observable readiness criteria for the app's major routes and layouts so E2E tests and manual checks can tell when a screen is truly ready.

## Scope

This change covers route-level readiness semantics, a shared route-acceptance helper module, and the documentation of route readiness criteria. It does not change product behavior or navigation logic.

## Requirements

### R1. Every major route MUST have explicit readiness signals

The app MUST define observable readiness signals for the major routes and shells used in the frontend.

At minimum, the following routes or shells MUST be covered:

- `ProtectedView`
- `DashboardLayout`
- `DashboardPage`
- `EmployeeDashboardPage`
- `AdminDashboardPage`
- `ManagerDashboardPage`
- `SupervisorDashboardPage`
- `MaterialsManager`
- `EmployeesManager`
- `ProductsManager`
- `QuotationsManager`
- `WorksManager`
- `TasksManager`
- `PayrollPage`

Each covered route MUST expose at least three observable readiness signals that a test can assert.

#### Scenario: route readiness is documented

- GIVEN a major route or shell in the application
- WHEN a developer checks the route acceptance reference
- THEN they MUST find at least three readiness signals for that route
- AND those signals MUST be framed in observable UI terms, not hidden implementation details

### R2. Readiness signals MUST be reusable by tests

The app MUST provide a shared helper module that centralizes route acceptance metadata for tests.

The helper module MUST allow tests to:

- look up the expected readiness signals for a route;
- assert that a route has at least the minimum number of signals;
- wait for a route to become ready using the documented signals.

#### Scenario: test helper returns route criteria

- GIVEN a route key such as `materials` or `employee-dashboard`
- WHEN a test asks the helper for that route's criteria
- THEN the helper MUST return the documented readiness signals
- AND the helper MUST preserve the route's current readiness contract in one place

### R3. Route readiness MUST be observable in existing UI elements

The readiness signals MUST be based on UI elements that already exist or can be inferred from existing route structure.

Examples of valid readiness signals include:

- visible headings or titles;
- accessible tables or tabs;
- actionable buttons or search inputs;
- route-specific cards, menus, or breadcrumbs;
- the absence of the global loading gate for authenticated routes.

The criteria MUST NOT depend on fragile timing hacks or arbitrary delays.

#### Scenario: materials route is ready

- GIVEN the materials route has loaded successfully
- WHEN the screen is ready for interaction
- THEN the materials table, search input, and create action MUST be observable
- AND the route MUST not rely on a sleep-based wait to declare readiness

### R4. Route readiness MUST reflect role-based shells

Role-specific dashboards MUST define readiness in terms of the visible shell content and role-appropriate tabs or sections.

#### Scenario: employee dashboard is ready

- GIVEN an employee session is authenticated
- WHEN the employee dashboard finishes rendering
- THEN the profile section, navigation tabs, and breadcrumbs MUST be visible
- AND the profile tab/content MUST be interactable

#### Scenario: tasks page for manager or supervisor is ready

- GIVEN a manager or supervisor session is authenticated
- WHEN the tasks page finishes rendering
- THEN the manager-only tab set MUST be visible
- AND the route MUST expose the role-appropriate task controls

### R5. The acceptance reference MUST remain route-focused and non-invasive

The route acceptance documentation and helper metadata MUST not change product behavior.

They MAY be used by tests and debugging tools, but they MUST remain a read-only contract about readiness.

## Acceptance Criteria

- At least 8 route definitions are documented, each with 3 or more readiness signals.
- A helper module exists for route readiness metadata and test wait helpers.
- Existing E2E tests can migrate away from ad-hoc `waitForTimeout` usage.
- The acceptance model stays aligned with visible UI behavior rather than internal state.
- `bun run test` remains the validation command for the change.

## Non-Goals

- Changing route implementations or navigation flow.
- Adding new loading skeletons or redesigning route UI.
- Refactoring product logic into the acceptance helper.
- Introducing a new test framework.

## Risks

- Some routes may expose fewer stable selectors than others; the helper may need to lean on headings, labels, or role-based tabs.
- If the acceptance criteria become too strict, they could make future UI improvements harder; the contract should stay descriptive, not prescriptive.
