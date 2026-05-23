# Proposal: connectivity-api-routing-fix

## Intent

Fix the frontend's online/offline decisioning so API reads and authenticated views do not incorrectly behave as offline when the browser is online, and do not incorrectly behave as online when the app is actually offline.

## Problem Statement

We currently have a connectivity/cache heuristic bug that causes the app to misclassify network state in real usage.

Symptoms observed:

- While the browser is online and the backend responds correctly, some authenticated screens show messages like **"No hay user autenticado"** or suppress expected GET requests for `materials` and `products` as if the app were offline.
- In other flows, especially around quotations, the app appears to assume online behavior even when it should respect the offline path.
- This creates inconsistent request routing, stale UI state, and confusion between real auth state and transport/cache state.

This is distinct from the auth hydration flash fixed by `auth-hydration-fix`: here the issue is the app's **connectivity/API routing semantics**, not the startup role hydration order.

## Goals

- Ensure authenticated API reads use the backend normally when the browser is online.
- Ensure offline behavior is only activated when the app truly has no usable network path.
- Stop conflating auth/session errors with offline transport state.
- Make `materials`, `products`, and related data-loading paths behave consistently with actual connectivity.
- Preserve the existing offline queueing/sync behavior for truly offline mutations.

## Non-Goals

- Redesigning the backend API contract.
- Reworking the auth snapshot model from `auth-hydration-fix`.
- Removing service worker caching entirely.
- Building a new general-purpose network monitoring framework.
- Changing quotation domain behavior beyond correcting its online/offline routing decisions.

## Scope

This change is limited to the connectivity decision path, API request routing, and any UI/service logic that currently suppresses online requests because it incorrectly believes the app is offline.

## Affected Areas

Likely touchpoints, subject to exploration:

- `src/services/apiClient.ts`
- `src/providers/ConnectivityProvider.tsx`
- `src/services/sync/syncManager.ts`
- `src/services/auth/sessionStorage.ts` if auth state is being misread as transport state
- `src/components/*` or `src/pages/*` where data loading is suppressed based on the wrong offline signal
- service worker / cache configuration only if it is proven to be the source of the misclassification

## Assumptions

- The browser's online/offline signal should remain the primary transport signal, but it may need to be combined with a stricter API reachability check.
- Authenticated views should not treat a missing remote response as equivalent to offline unless the failure is genuinely a network failure.
- Current offline queueing should remain intact for supported mutations.

## Open Questions

- Is the misclassification caused by the service worker, the connectivity provider, or request-level error handling?
- Should online state be derived from browser events alone, or should it be confirmed with a lightweight backend probe before suppressing reads?
- Which screens currently skip GETs incorrectly: materials, products, quotations, or all three?
- Are auth/session errors being misreported to the UI as connectivity failures?

## Risks

- Fixing the online/offline heuristic in one layer may expose hidden assumptions in other views that currently rely on the wrong signal.
- If the service worker is part of the bug, the fix may require a second slice for cache behavior.
- Over-correcting toward "always online" could break genuine offline flows and queueing.

## Acceptance Criteria

- When the browser is online and the backend responds, the app must issue the expected GET requests for online-capable read flows.
- Authenticated screens must not show **"No hay user autenticado"** merely because a cached/offline heuristic misfires.
- `materials` and `products` data loading must not be skipped while the browser is actually online.
- Quotation flows must not incorrectly force the opposite transport assumption.
- Existing offline queueing and replay behavior must continue to work for true offline cases.
- `bun run test` must remain the validating command for this change.

## Success Criteria

- Online users see fresh backend data instead of cache-driven false offline states.
- Offline users still get queueing and replay behavior where supported.
- The transport decision logic becomes explicit and testable instead of being inferred indirectly from auth/cache symptoms.
