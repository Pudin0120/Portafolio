# Design: sw-dev-stability

## Goal

Fix the development and update lifecycle around the PWA so stale service worker state stops breaking dev sessions, production users can see when a new build is ready, and reconnect replay stays automatic.

## Problem

The current PWA setup has three overlapping issues:

1. the dev server can be held hostage by a stale service worker from a previous session;
2. update detection is not surfaced to the user in a controlled way;
3. reconnect replay relies on the connectivity/auth path but is not clearly modeled as a reconnect event.

The change needs to keep the scope tight. It should not change the offline queue schema or route behavior.

## Options Considered

### Option 1 - Dev-only cleanup + prompt-based update UI + reconnect epoch

Use a dev-only service worker cleanup before app render, switch the PWA registration behavior to prompt mode, add a small update banner, and expose a reconnect epoch from connectivity so replay can be triggered from online transitions.

**Pros**
- Addresses all three issues with small, isolated pieces.
- Keeps the dev fix explicit and local.
- Makes update prompts user-visible and controlled.
- Gives reconnect replay a real event source.

**Cons**
- Requires touching app bootstrap, the PWA service worker, and the connectivity provider.

### Option 2 - Keep autoUpdate and only add a banner in the app

Leave the PWA behavior mostly as-is and just show a banner when the app sees a new SW.

**Pros**
- Smaller PWA config change.

**Cons**
- Does not address stale dev SW control well.
- Harder to control when the new build activates.
- Risk of masking the lifecycle problem instead of fixing it.

### Option 3 - Replace the custom SW with a generated default SW

Switch away from the custom inject-manifest service worker and let the plugin generate everything.

**Pros**
- Less SW code to maintain.

**Cons**
- Too invasive for this sprint.
- Loses current custom routing behavior.
- Higher regression risk.

## Decision

**Choose Option 1.**

It is the best compromise between correctness and review size. It fixes dev breakage, preserves the current custom SW approach, and gives the app an explicit update prompt.

## Proposed Architecture

### 1) Dev-only service worker cleanup before render

Add a small utility that runs before the React tree mounts:

- if the app is running in dev mode, enumerate existing service worker registrations;
- unregister them;
- clear stale caches;
- then render the app.

This is intentionally boot-time only. It should not run in production.

Suggested location:

- `src/services/pwa/devServiceWorkerCleanup.ts`

### 2) Prompt-based update registration

Change the PWA registration behavior from silent auto-update to prompt mode so a waiting service worker becomes visible to the user.

Update flow:

1. the new SW becomes waiting;
2. the client receives an `onNeedRefresh` signal;
3. the app shows a small banner with an update action;
4. when the user accepts, the app sends the skip-waiting message and reloads into the new build.

Suggested touchpoints:

- `vite.config.ts`
- `public/sw.ts`
- `src/hooks/useServiceWorker.ts`
- `src/components/common/UpdateAvailableBanner.tsx`
- `src/App.tsx`

### 3) Reconnect replay keeps using the connectivity/auth path

The current reconnect replay logic should remain coupled to online transitions and session availability.

To make the reconnect trigger explicit, the connectivity provider can expose a reconnect epoch or counter that increments when the browser returns online. The sync layer can observe that value and replay pending operations without relying on arbitrary timers.

Suggested touchpoints:

- `src/providers/ConnectivityProvider.tsx`
- `src/hooks/usePersistentAuth.ts`
- `src/services/sync/syncManager.ts`

## State Flow

### Dev startup

1. App boots in dev mode.
2. Dev cleanup unregisters stale SWs and clears stale caches.
3. React renders against a clean dev environment.
4. No manual hard reload should be needed.

### Production update

1. User is on an older build.
2. New build deploys and the SW waits.
3. App shows an update banner.
4. User accepts.
5. New SW activates and page reloads into the new build.

### Reconnect sync

1. Offline mutation is queued.
2. Browser returns online.
3. Connectivity emits a reconnect signal.
4. Auth/session replay logic flushes pending operations.

## Test Strategy

Validation command: `bun run test`

### Coverage to add or update

- a focused test file for PWA/dev helpers and prompt metadata;
- a test that validates the dev cleanup path is gated to dev;
- a test that validates the update prompt contract or helper behavior;
- a test that confirms reconnect signal handling is explicit and testable.

The tests should avoid depending on a live service worker shell if a pure helper can represent the behavior.

## Tradeoffs

- Prompt-based updates are safer for users, but require a more explicit service worker lifecycle than autoUpdate.
- Dev cleanup is a blunt tool, but it is the smallest reliable fix for stale local SW control.
- A reconnect epoch is more testable than relying only on `navigator.onLine` booleans.

## Outcome

This design keeps the current PWA architecture, but makes its lifecycle visible and deterministic in the three places that currently cause friction: dev startup, update delivery, and reconnect replay.
