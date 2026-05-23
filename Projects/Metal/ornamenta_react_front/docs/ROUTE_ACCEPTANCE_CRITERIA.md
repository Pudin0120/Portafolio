# Route Acceptance Criteria

This document defines when the main routes and shells in the frontend are considered ready.

The goal is to give developers and E2E tests a shared, observable definition of "route ready" without changing product behavior.

## Shared Rules

A route is ready when:

1. the global loading gate has cleared;
2. the route shell is visible;
3. the primary content or navigation is present;
4. the route-specific interactive controls can be used.

## ProtectedView

Ready signals:

- the session verification loading state is gone;
- the authenticated outlet is mounted;
- the install prompt or protected shell is visible.

## DashboardLayout

Ready signals:

- the menu toggle is visible;
- the breadcrumbs are visible;
- the network status indicator is visible.

## DashboardPage

Ready signals:

- a role-specific dashboard view is visible;
- the startup verification message is no longer visible;
- the session state has been resolved.

## EmployeeDashboardPage

Ready signals:

- the profile section is visible;
- the tab navigation is visible;
- the breadcrumbs are visible.

## AdminDashboardPage

Ready signals:

- the manager management section is visible;
- the branding tab is available;
- the profile section is visible.

## ManagerDashboardPage

Ready signals:

- the employee management section is visible;
- the products section is visible;
- the materials section is visible.

## SupervisorDashboardPage

Ready signals:

- the works section is visible;
- the tasks section is visible;
- the profile section is visible.

## MaterialsManager

Ready signals:

- the materials table is visible;
- the create material action is visible;
- the search input is visible and interactive.

## EmployeesManager

Ready signals:

- the employees table is visible;
- the create employee action is visible;
- row actions are visible.

## ProductsManager

Ready signals:

- the products list tab is visible;
- the create simple tab is visible;
- the create composite tab is visible.

## QuotationsManager

Ready signals:

- the quotations list tab is visible;
- the create quotation tab is visible;
- the tab navigation is visible.

## WorksManager

Ready signals:

- the in-progress works list is visible;
- the delivered tab is visible;
- the edit flow is available.

## TasksManager

Ready signals:

- the my-tasks tab is visible;
- the role-gated all-tasks tab is visible for managers and supervisors;
- the task options tablist is visible.

## PayrollPage

Ready signals:

- the payroll title is visible;
- the tab navigation is visible;
- the role-specific payroll tab is visible.

## Notes for Test Authors

- Prefer route headings, table aria-labels, tabs, and action buttons.
- Avoid sleep-based waits such as `waitForTimeout`.
- Keep the acceptance contract in sync with the helper registry in `src/test-helpers/routeAcceptance.ts`.
