# Delta Spec: auth-hydration-fix

## Goal

Eliminate the transient **"Sin rol asignado"** flash during authenticated startup while preserving the snapshot-first offline auth model.

## Scope

This change covers auth/session hydration semantics, startup readiness gating, and the dashboard no-role fallback boundary. It does not change the auth storage format, Firebase integration, or the overall navigation model.

## Requirements

### R1. Snapshot-first restoration MUST remain available

When a persisted auth snapshot exists, the client MUST restore it immediately so the session remains usable offline and during slow startup.

#### Scenario: offline refresh retains the snapshot session

- **Given** the user is signed in and a valid auth snapshot exists locally
- **When** the browser goes offline or the app reloads offline
- **Then** the app MUST continue treating the user as authenticated from the snapshot
- **And** it MUST NOT clear the snapshot solely because remote revalidation is unavailable

#### Scenario: online startup may revalidate after snapshot restore

- **Given** a persisted auth snapshot exists and the browser is online
- **When** the app starts
- **Then** the snapshot MUST be applied immediately
- **And** the client MAY revalidate the remote profile after snapshot restore

### R2. Startup hydration MUST stay unresolved until a terminal outcome is known

The auth layer MUST expose a startup readiness signal that stays unresolved until the current session is terminal.

The startup session is terminal only when one of these outcomes is reached:

- a valid snapshot has been applied and is usable;
- the remote profile has been resolved;
- unauthenticated startup has been confirmed.

#### Scenario: authenticated snapshot with pending profile refresh stays blocked

- **Given** a persisted authenticated snapshot exists
- **And** remote profile refresh is still pending
- **When** the app boots
- **Then** startup readiness MUST remain unresolved until the session is terminal
- **And** the app MUST NOT expose the dashboard fallback as if hydration were complete

#### Scenario: unauthenticated startup resolves cleanly

- **Given** no persisted session exists
- **When** the app starts
- **Then** the auth layer MUST settle into the unauthenticated state
- **And** startup readiness MUST become terminal without showing authenticated content

### R3. Protected authenticated routes MUST remain blocked while startup is unresolved

The authenticated route tree MUST not render until the startup readiness signal is terminal.

#### Scenario: dashboard routes wait for auth readiness

- **Given** the app is starting with an authenticated or snapshot-based session
- **When** startup readiness is unresolved
- **Then** the protected route tree MUST remain blocked
- **And** the app MUST continue showing the existing loading state instead of dashboard content

#### Scenario: login behavior remains unchanged

- **Given** the user is not authenticated
- **When** startup readiness becomes terminal
- **Then** the login route MUST behave as it does today
- **And** no new splash or skeleton UI is introduced

### R4. The dashboard no-role fallback MUST be terminal-only

The **"Sin rol asignado"** state MUST only appear after hydration is complete and the resolved role is still null.

#### Scenario: no-role fallback does not flash during startup

- **Given** hydration is still in progress for the current session
- **When** the dashboard shell is deciding what to render
- **Then** the no-role fallback MUST NOT be shown as an intermediate state

#### Scenario: no-role fallback appears after terminal hydration with null role

- **Given** hydration has completed for the current session
- **And** the resolved role is still null
- **When** the dashboard renders
- **Then** the no-role fallback MAY be shown
- **And** the logout action MUST remain available from that terminal state

### R5. Existing inactive-account and role-specific behavior MUST be preserved

The inactive-account branch, role-specific views, and logout behavior MUST continue to work as they do today.

#### Scenario: inactive account still shows the restricted profile view

- **Given** the user is authenticated and inactive
- **When** the dashboard renders after readiness is terminal
- **Then** the inactive-account branch MUST still render
- **And** the user MUST still be able to log out

## Acceptance Criteria

- A persisted snapshot is restored immediately during startup.
- Startup readiness remains unresolved until the session is terminal.
- The protected route tree stays blocked while auth hydration is unresolved.
- **"Sin rol asignado"** does not appear as a transient startup flash.
- The no-role fallback only appears after terminal hydration with a null role.
- Offline snapshot behavior remains intact.
- `bun run test` remains the validation command for the change.

## Non-Goals

- Reworking the auth persistence format.
- Adding a new loading skeleton or redesigning the startup UI.
- Changing Firebase auth architecture.
- Refactoring route structure beyond the startup gate.

## Risks

- If the readiness signal is named too loosely, future changes may confuse startup terminal state with remote revalidation.
- Tests that only cover the hook may miss route-level regressions, so the app shell and dashboard fallback both need coverage.
- Over-eager loading logic could break the offline snapshot-first experience if it waits on network revalidation too early.
