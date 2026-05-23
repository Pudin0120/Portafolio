# Auth Specification

## Purpose

Define the startup and hydration behavior for authenticated sessions so the dashboard never renders a temporary "Sin rol asignado" state while role/profile data is still being resolved.

## Scope

This change covers the session hydration path owned by `src/hooks/usePersistentAuth.ts`, the authenticated shell in `src/App.tsx`, and the dashboard fallback rendering in `src/pages/DashboardPage.tsx`.

## Requirements

### Requirement: Hydration must complete before the authenticated UI is considered ready

The system MUST keep the authenticated startup state unresolved until the current session has either:

- applied a persisted snapshot role/state for the session,
- resolved role/state from the remote profile source, or
- been confirmed unauthenticated.

The system MUST NOT signal that authenticated startup is complete while the current user still has an unresolved role decision.

#### Scenario: Online session with a valid snapshot and pending profile refresh

- GIVEN a persisted authenticated snapshot exists
- AND the user is online
- AND Firebase reports an authenticated user
- WHEN the app starts
- THEN the authenticated UI MUST remain blocked until the session role/state is resolved
- AND the dashboard MUST NOT render the temporary no-role state during that hydration window

#### Scenario: Unauthenticated startup

- GIVEN no persisted snapshot exists
- AND Firebase reports no authenticated user
- WHEN the app starts
- THEN the system MUST finish startup in the unauthenticated state
- AND the login flow MAY render normally

### Requirement: Snapshot-first behavior must remain the initial source of truth

When a persisted session snapshot exists, the system MUST restore the snapshot role and profile state as the first authenticated session data made available to the UI.

If remote revalidation later returns updated role or state values, the system MAY update the authenticated session after startup completes.

#### Scenario: Offline startup with a persisted snapshot

- GIVEN a persisted authenticated snapshot exists
- AND the device is offline
- WHEN the app starts
- THEN the authenticated session MUST be restored from the snapshot without waiting for network revalidation
- AND the dashboard MUST render using the snapshot role/state

#### Scenario: Snapshot role differs from the remote profile

- GIVEN a persisted authenticated snapshot exists
- AND the user is online
- AND the remote profile returns a different role or state
- WHEN hydration completes
- THEN the UI MUST never pass through the temporary no-role state
- AND the final authenticated session MAY reflect the updated remote role/state

### Requirement: The dashboard MUST only show the no-role fallback after hydration has finished

`src/pages/DashboardPage.tsx` MUST treat the "Sin rol asignado" view as a terminal fallback for a fully hydrated authenticated session whose resolved role is still null.

The dashboard MUST NOT use that fallback to represent an in-progress hydration state.

#### Scenario: Slow profile hydration

- GIVEN the user is authenticated
- AND the role/profile request is still pending
- WHEN the dashboard would otherwise mount
- THEN the dashboard MUST remain hidden behind the app loading gate until hydration finishes
- AND the no-role fallback MUST NOT appear transiently

#### Scenario: Fully hydrated session with no assigned role

- GIVEN the user is authenticated
- AND hydration has finished
- AND the resolved role is still null
- WHEN the dashboard renders
- THEN the no-role fallback MAY be shown
- AND the user MUST still be able to log out from that state

### Requirement: App startup must gate route rendering on auth readiness

`src/App.tsx` MUST continue to block authenticated route rendering while auth hydration is not ready.

The app MUST only render the dashboard routes after auth readiness is true for the current session.

#### Scenario: Initial startup before auth readiness

- GIVEN the app has not finished auth initialization
- WHEN the root application renders
- THEN the route tree MUST remain blocked
- AND the loading state MUST be visible instead of the dashboard

#### Scenario: Auth ready with a resolved role

- GIVEN auth initialization has completed
- AND the session has a resolved role or a confirmed snapshot role
- WHEN the route tree renders
- THEN the dashboard MUST render directly into the resolved role view
- AND it MUST NOT render the no-role fallback first

## Acceptance Criteria

- The authenticated startup flow MUST never display "Sin rol asignado" as a transient flash during hydration.
- The startup path MUST preserve the existing snapshot-first model.
- Offline sessions with a valid snapshot MUST remain usable without waiting for remote profile hydration.
- A fully hydrated authenticated session with no role assigned MUST still be allowed to show the no-role fallback.
- The validating command for this micro-sprint MUST be `bun run test`.

## Non-Goals

- Adding a new dashboard loading skeleton or placeholder.
- Changing the authentication persistence format or storage mechanism.
- Refactoring the connectivity provider, sync manager, or Firebase integration.
- Altering dashboard role-to-view mappings beyond the hydration gating behavior.

## Risks

- The proposal does not define an explicit Capabilities section, so this spec assumes the affected domain is auth/session hydration.
- If other active changes modify the same auth startup path, the hydration gate may need coordination to avoid conflicting behavior.
