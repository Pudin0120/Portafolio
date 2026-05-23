# Design: auth-hydration-fix

## Goal

Prevent the transient **"Sin rol asignado"** flash during authenticated startup without breaking the existing snapshot-first offline auth model.

## Context

The current startup flow is split across three places:

- `src/hooks/usePersistentAuth.ts` owns auth/session hydration, snapshot restore, and remote profile revalidation.
- `src/App.tsx` blocks route rendering while auth is loading.
- `src/pages/DashboardPage.tsx` renders a no-role fallback whenever `userRole` is `null`.

The flash occurs when the dashboard becomes renderable before role resolution is truly terminal for the current session.

The spec requires two things at once:

1. keep snapshot-first restoration for offline usability;
2. ensure the no-role fallback is only shown after hydration is fully complete.

## Options Considered

### Option 1 - Add a narrow hydration-ready signal in the auth hook

Introduce a dedicated startup readiness marker in `usePersistentAuth` that becomes terminal only when the current session is one of:

- authenticated with snapshot role/state applied,
- authenticated with remote profile resolved,
- unauthenticated.

`App.tsx` continues to be the route gate, and `DashboardPage.tsx` only shows the no-role fallback when hydration is complete.

**Pros**

- Smallest safe change.
- Keeps snapshot-first behavior intact.
- Centralizes startup semantics in the hook that already owns hydration.
- Low review risk.

**Cons**

- Adds another bit of auth state.
- Needs careful naming so it is not confused with online revalidation.

### Option 2 - Move all startup gating into `App.tsx`

Make the app shell decide when routes can render, while `DashboardPage` remains unchanged.

**Pros**

- Simple mental model.
- Fewer page-level edits.

**Cons**

- Less defensive: the flash could return if `DashboardPage` ever mounts outside the main gate.
- The terminal-only rule is not enforced at the page boundary.

### Option 3 - Replace the boolean flow with a full session state machine

Replace `loading` / `authReady` with a typed enum such as `booting`, `snapshot-applied`, `remote-resolving`, `ready`, `unauthenticated`.

**Pros**

- Best long-term clarity.
- Eliminates boolean ambiguity.

**Cons**

- Too large for this micro-sprint.
- More review surface and higher regression risk.

## Decision

**Choose Option 1.**

It is the smallest change that satisfies the spec, preserves offline snapshot-first behavior, and keeps the review surface within the expected micro-sprint budget.

## Proposed Architecture

### 1) `src/hooks/usePersistentAuth.ts`

Own the hydration lifecycle in the hook, but separate the concept of:

- **auth/session visibility**: whether the app has a usable session snapshot or remote identity;
- **hydration completion**: whether the current startup session is terminal.

Recommended implementation shape:

- keep the snapshot restore path intact;
- restore the snapshot immediately when present;
- do not clear the snapshot just because remote profile revalidation is pending;
- mark hydration complete only after one of these outcomes is reached:
  - snapshot applied and usable,
  - remote profile resolved,
  - confirmed unauthenticated;
- keep revalidation after startup as a separate concern.

This can be exposed either as:

- a new `hydrationComplete` / `sessionReady` field in the auth context, or
- a derived `loading` value that remains true until the session is terminal.

The first option is easier to reason about and safer for future changes.

### 2) `src/App.tsx`

Continue to gate the protected route tree on auth readiness.

The app should:

- show the loading state while hydration is incomplete;
- avoid rendering dashboard routes until the startup session is terminal;
- keep login routing unchanged.

This ensures the dashboard cannot mount while role resolution is still in-flight.

### 3) `src/pages/DashboardPage.tsx`

Make the no-role state terminal-only.

The dashboard should:

- render the resolved role view when a role exists;
- render the no-role fallback only after hydration is complete and the resolved role is still `null`;
- keep the inactive-account branch intact;
- preserve logout behavior from the terminal no-role state.

The page should not be used as a loading-state substitute.

## State Flow

### Current flow

1. App starts.
2. `usePersistentAuth` initializes.
3. `App.tsx` waits on `loading`.
4. The route tree can become visible before role resolution is terminal.
5. `DashboardPage` sees `userRole === null` and flashes **"Sin rol asignado"**.

### Proposed flow

1. App starts.
2. `usePersistentAuth` restores the snapshot synchronously if it exists.
3. Hydration proceeds:
   - snapshot is applied immediately if available;
   - remote profile may revalidate later when online;
   - unauthenticated is confirmed only when no session exists.
4. A dedicated readiness signal becomes terminal only when the session is fully resolved for startup.
5. `App.tsx` renders authenticated routes only after readiness is terminal.
6. `DashboardPage` only reaches the no-role branch when hydration has already completed.

## Data and Boundary Decisions

- **Do not change** the snapshot storage format.
- **Do not change** Firebase integration or connectivity handling.
- **Do not move** hydration logic into `DashboardPage`.
- **Do not** introduce a new loading skeleton.
- **Do** keep remote revalidation as a follow-up after startup, not as a prerequisite for showing the snapshot.

## Test Strategy

Validation command: `bun run test`

### Coverage to add or update

1. **Hydration behavior**
   - snapshot exists and network is slow
   - dashboard never passes through the no-role flash
   - snapshot role/state are restored first
   - startup readiness only turns terminal at the correct point

2. **Dashboard fallback behavior**
   - hydration incomplete -> no-role fallback does not render
   - hydration complete + null role -> no-role fallback does render
   - logout remains available in the terminal no-role state

3. **App route gating**
   - protected routes remain blocked while auth is not ready
   - loading state is visible instead of dashboard content
   - authenticated routes render only after readiness is terminal

## Risks

- A second change touching the same auth startup path could introduce conflicting readiness semantics.
- If the readiness field name is vague, future refactors may conflate "startup terminal" with "remote revalidated."
- If tests only cover the hook and not the app shell, the flash could reappear through route composition.

## Outcome

This design keeps the fix narrow:

- snapshot-first auth remains intact;
- startup still blocks routes until ready;
- the no-role fallback becomes terminal-only;
- the transient **"Sin rol asignado"** flash is eliminated without broad auth refactoring.
