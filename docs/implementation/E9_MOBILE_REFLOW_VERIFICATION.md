# E9 narrow learner journey verification

Requirements: NFR-ACC-001, NFR-COMP-001. Status: verified in hosted CI 37925290651 at `83c6102`;
promoted to main. Physical/branded/mobile release gates remain separate.

The existing real-API engine suite adds one synthetic learner journey at a 320×640 CSS-pixel
viewport with touch enabled. It verifies contact/profile/consent controls, five-question practice,
feedback and worked solution, a reload retaining the first saved answer, completion, progress and
history. At each meaningful state, document and body scroll widths must fit the viewport. Key
buttons, answer-label targets and navigation links must measure at least 44×44 CSS pixels and
accept actual Playwright taps. Axe scans cover completed practice and history.

The existing isolated fixture database, fake OTP/provider and unique synthetic account are reused.
There are no real identifiers, model/provider calls or application/data-contract changes. No new
architecture is introduced. This test measures selected core states; it does not establish complete
WCAG conformance, every content shape, screen-reader acceptance or physical-device compatibility.
It intentionally avoids an Android/iOS user-agent claim: viewport/touch emulation in the three
engines is not branded Chrome, Edge or Safari release evidence.

Run `make build e2e-install test-web-mobile` for the default Chromium case, or set
`KASOMA_E2E_BROWSER=firefox` / `webkit` for a focused alternative. Full `make e2e` includes the
journey in every engine. `make format lint e2e-list` passed after a second formatting pass;
inventory now contains 22 cases per engine (66 executions). Listing is not runtime acceptance.
Native browser installation is still encountering download timeouts/resets. Hosted execution,
including existing cold-transfer and accessibility regressions, is required before promotion.

`make check-docs test-web-mobile` passed links/whitespace and started the isolated API/web servers,
but browser launch failed because the pinned Chromium headless-shell download is incomplete.
No journey assertion ran; this is an environment failure, not a passed mobile test.

Physical Android Chrome, current/previous branded browser releases, macOS/iOS Safari, assistive
technology and agreed low-bandwidth/load performance remain release gates. Preserve these gaps
even if all emulated checks pass.

## Hosted acceptance

[CI 37925290651](https://github.com/Jotham566/kasoma/actions/runs/37925290651) passed 22 real-API
cases in each engine (66 browser executions), including the new narrow touch journey, plus one
isolated editor case. All 621 Python and five tooling cases passed. Clean services/migrations/seed,
role checks, lint/types/contracts/build, security/source/image scans and container smoke passed.
Recovery restored 54 tables/272 rows in 454 ms with pgvector/immutable guards and no cleanup
failure. Cold question transfers were 192785/194253/193654 bytes, all below 250000.
Commit `83c6102` is on main and its completed branch was removed locally/remotely. No application
layout changes were necessary. Earlier native launch failure remains an independent environment
gap while the pinned browser downloads complete.
