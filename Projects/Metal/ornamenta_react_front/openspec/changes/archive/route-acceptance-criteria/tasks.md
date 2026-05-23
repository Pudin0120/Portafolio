## Review Workload Forecast

| Field                   | Value     |
| ----------------------- | --------- |
| Estimated changed lines | ~300-380  |
| 400-line budget risk    | Low       |
| Chained PRs recommended | No        |
| Suggested split         | single PR |
| Delivery strategy       | single-pr |

Decision needed before apply: No
Chained PRs recommended: No

## Implementation Order

1. **Explore and lock route vocabulary**
   - Confirm the major route/shell keys and the observable readiness signals for each one.
   - Keep the route list aligned with the current app shells in `src/App.tsx`, `src/components/DashboardLayout.tsx`, and the role dashboards under `src/pages/`.
   - Preserve the distinction between shell readiness and content readiness.

2. **Write the shared route acceptance registry**
   - Add `src/test-helpers/routeAcceptance.ts` as the canonical route readiness map.
   - Expose typed helpers to list routes, read readiness signals, and assert the minimum signal count.
   - Make the helper read-only; do not couple it to runtime app state.

3. **Write the reference documentation**
   - Add `docs/ROUTE_ACCEPTANCE_CRITERIA.md` with one section per route.
   - Document the 3+ readiness signals per route in reviewer-friendly language.
   - Keep the docs aligned with the helper registry by using the same route keys and labels.

4. **Add focused tests**
   - Create a small test file that validates the helper registry and route coverage.
   - Assert that the selected route list meets the minimum coverage target.
   - Ensure the test file fails if a route is missing signals or coverage drops below the threshold.

5. **Triangulate and refine**
   - Revisit route signals that are too brittle or too vague.
   - Favor accessible labels, headings, tabs, tables, and button text.
   - Avoid adding `waitForTimeout` or timing-based assertions.

## Files to Touch

- `src/test-helpers/routeAcceptance.ts`
- `docs/ROUTE_ACCEPTANCE_CRITERIA.md`
- `tests/route-acceptance-criteria.spec.ts`
- Possibly minor selector or accessibility tweaks only if a route lacks a stable observable signal.

## Verification

- Run `bun run test` after the helper and docs are in place.
- Keep the test coverage centered on route metadata and signal counts.
- Do not expand the scope into UI redesign or route behavior changes.
