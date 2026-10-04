# E9 browser engine verification

Requirements: NFR-COMP-001, NFR-ACC-001, NFR-MNT-001 (partial compatibility coverage).
Status: engine matrix configured; runtime acceptance pending hosted execution.

`make e2e` now runs the full existing journey suite separately in Chromium, Firefox and WebKit.
Each engine runs two sequential shards. Every invocation starts fresh isolated migrated synthetic
API fixtures and a web server; fixed fixture identities are never shared across engine runs.
`KASOMA_E2E_BROWSER` selects exactly one supported engine and rejects unknown values. No test is
skipped by browser. Existing keyboard, axe, authorization, lost-acknowledgement and offline retry
assertions remain enabled. No application behavior or architectural decision changes here.

Files: `playwright.config.ts`, Makefile, CI workflow, README and local runbook. `make e2e-install`
installs all three engines using the pinned Playwright package. CI permits up to 40 minutes for
the expanded sequential matrix, recovery drill and unchanged Python/security/container gates.

## Executed checks

`make format lint openapi-check e2e-list` passes. Test inventory lists 20 cases in 16 files for each
engine (60 planned executions); listing does not launch browsers or establish application acceptance.
Native `make e2e` failed when the isolated API could not connect to local PostgreSQL, before browser
assertions. The Docker installation remains unavailable; no local runtime acceptance is claimed.
Hosted real-database browser checks must pass for the final snapshot before promotion.

## Remaining compatibility gates

Playwright engines are useful regression targets, not proof of current and previous branded
Chrome/Edge/Firefox releases. WebKit on Linux does not establish Safari/macOS/iOS support. Physical
Android Chrome, branded/versioned browser checks, screen-reader/manual accessibility and low-bandwidth
transfer budgets remain release work. Record exact tested versions/platforms with their evidence;
do not infer full NFR-COMP-001 or WCAG acceptance from an automated axe or engine-suite pass.

## Cold question transfer budget

The existing assessment journey now opens a fresh browser context with only authentication cookies,
blocks service workers and loads the actual first-question session URL. After asserting that the
question renders, wait for initial network quiet and sum encoded response body plus header bytes
from every completed request. The original fixture has no question media, so nothing is excluded.
Require nonempty script transfers and nonnegative measurements; missing size data cannot pass.
Report only engine, aggregate bytes/request/script counts and the 250,000-byte ceiling. No URLs,
cookies, identities, answers or raw payloads enter metrics.

This deliberately conservative decimal 250 KB check addresses NFR-BW-001. It includes initial
prefetches and headers; it does not claim mobile-network latency or load-test acceptance. All three
engines must execute the same budget assertion. No runtime transfer measurement is claimed until
hosted execution succeeds.
