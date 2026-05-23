# Delta Spec: sw-dev-stability

## Goal

Stabilize the frontend development experience and service worker behavior so the app does not get stuck behind stale cache state, users are notified when a new build is available, and pending sync work is replayed when connectivity returns.

## Scope

This change covers:

- dev-server service worker cleanup and registration behavior;
- update notification behavior for new builds;
- reconnect-driven sync replay wiring.

It does not change the backend API contract or the offline sync data model.

## Requirements

### R1. Dev mode MUST not keep stale service worker control active

When the app runs in development mode, the frontend MUST not remain controlled by a stale production or preview service worker.

The app MUST proactively unregister stale registrations and clear stale caches before rendering the React tree in dev mode.

#### Scenario: dev startup after a preview session

- GIVEN the browser has an old service worker registration from a previous preview or production session
- AND the app is started in dev mode
- WHEN the app boots
- THEN the stale service worker registrations MUST be removed
- AND stale caches MUST be cleared before the React app renders
- AND the dev server MUST not depend on a manual hard refresh to become usable

### R2. The frontend MUST notify users when a new build is available

When a new service worker becomes available in production, the frontend MUST surface an update prompt instead of silently switching behavior.

The prompt MUST offer a clear refresh action and MUST reload the app into the updated build when accepted.

#### Scenario: new build detected in production

- GIVEN the app is running with an older cached build
- AND a newer service worker has been installed and is waiting
- WHEN the update is detected
- THEN the app MUST show an "Update available" prompt
- AND the user MUST be able to refresh into the new version

### R3. The custom service worker MUST support prompt-based updates

The custom inject-manifest service worker MUST support skip-waiting updates via a message channel so the app can control when the new build takes over.

#### Scenario: user accepts the update prompt

- GIVEN an updated service worker is waiting
- WHEN the user clicks refresh in the update prompt
- THEN the client MUST send the skip-waiting signal to the service worker
- AND the updated build MUST take control and reload the page

### R4. Reconnect-driven sync replay MUST continue to run automatically

Pending sync work MUST replay automatically when connectivity returns, using the existing auth/session context and the reconnect transition as the trigger.

#### Scenario: offline mutation then reconnect

- GIVEN a supported operation is queued while offline
- AND the browser transitions from offline to online
- WHEN the reconnect is observed
- THEN the app MUST attempt replay automatically without requiring a manual reload
- AND supported pending operations MUST preserve their status semantics during the replay

### R5. The change MUST remain non-invasive to product behavior

This change MUST not alter navigation, route semantics, or the offline queue schema. It is limited to dev/PWA lifecycle behavior and the reconnect replay trigger path.

## Acceptance Criteria

- Dev mode no longer relies on a stale service worker control path.
- The app can remove stale dev registrations/caches before rendering.
- The production app shows an update prompt when a new build is waiting.
- The user can accept the update and reload into the new build.
- Reconnect-triggered sync replay still works automatically.
- `bun run test` remains the validation command.

## Non-Goals

- Redesigning the sync queue format.
- Implementing a full update-history UI.
- Changing the offline queue business rules.
- Rewriting the service worker strategy globally.

## Risks

- Aggressive cache cleanup in dev could be too broad if it runs outside dev-only gates.
- Prompt-based updates require the custom service worker to honor skip-waiting messages.
- Update prompts should not become noisy; the prompt must be user-initiated and narrow in scope.
