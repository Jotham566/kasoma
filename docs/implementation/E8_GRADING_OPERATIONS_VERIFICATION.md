# Grading operations verification

18 October 2026. ADR-053 candidate; FR-OPS-002, NFR-OBS-001, NFR-SEC-002, NFR-ACC-001, NFR-COMP-001.

Read-only bounded grading work, terminal/processing-fallback, audit and activated-band
aggregates extend the existing ADMIN snapshot and accessible dashboard. Typed local
stale-age alerting reuses existing safe monitoring. No schema migration, retention,
provider or learner-policy change. Processing fallbacks are explicitly not academic
errors or automatically declared incidents. Model usage/error-rate metrics stay unavailable.

Initial 26 focused contract/API/PostgreSQL cases pass; the final rerun includes an
explicit rejected-never-activated band exclusion. Actual encrypted queue, finite claim,
lease expiry/recovery, fake provider exception, neutral outcome, definitive publication,
blinded critical review, disabled-band counts, exact 24-hour boundaries, stale-alert
recovery and non-ADMIN denial are covered. Full backend/browser/build/contracts,
security/recovery/container acceptance remains pending before promotion.


The first broad unit run caught an omitted shared analytics-alert enum update for
GRADING_STALLED. The event schema now matches the closed API/domain enum; the strict
cross-schema test remains unchanged. Full backend acceptance is being rerun.


A broader browser run passed 90 existing engine executions but failed two short-text
cases: a delayed diagnostic and a review HTTP 500. Rollback-only reproduction of the
same review, with fresh synthetic authentication, failed the fixed review guard in
nine of ten attempts. PostgreSQL was 0.5–0.7 ms behind the host. Completion now caps the
domain timestamp at an authoritative database timestamp under its existing lock; SQL
future/assignment/band/prior-completion guards remain unchanged. A deterministic
thirty-second ahead host-clock integration test and complete affected reruns are required.
The final retained diagnostic state is completed (15 saved, 14 graded, one neutral),
so its earlier timeout remains separate and must be rerun; no cause is invented for it.


The superseded navigation-only hosted run failed the diagnostic's first immediate
GET: click completion was treated as a save acknowledgement, so answered_attempts
could still be empty. The later report-source run passes the complete hosted pipeline,
including the same UI. The test now awaits each actual successful POST acknowledgement
and binds the first saved attempt ID to that receipt before asserting sealing. No sleep,
timeout relaxation or weaker privacy assertion is introduced.


The shared staff page applies zero-minimum grid sizing and anywhere wrapping, extending
existing review-page behavior to operations and other staff views. The operations
journey now checks actual 200% text reflow/axe at 320 pixels without clipping, followed
by unchanged standard-size state/alert assertions. Complete staff/browser acceptance
is rerun after rebuilding the native bundle; no concurrent native browser commands.


## Final local acceptance

- `make format lint test openapi-check`: 884 unit/contract and 35 tooling cases,
  333 broad integration cases pass. That broad run precedes the clock cap; final
  `make test-grading-reviews` passes all 33 cases including the new skew regression,
  and `make test-grading-operations` passes 26 operational cases.
- Final `make test-runtime-role` passes actual restricted-login encrypted publication
  and independent completion, including database-clock access without extra grants.
- Final serial `make format lint build test-web-content e2e`: two UI harness cases,
  90 existing matrix executions and 12 encrypted learner/reviewer executions pass.
  This includes receipt-bound diagnostic sealing, actual review retry, keyboard/menu
  behavior, 320-pixel reflow and 200% text/axe across three engines. Normal/large-text
  operations screenshots were inspected; no remote asset or clipping is introduced.
- Final `make test-web-short-text recovery-drill test-unit security security-source`
  passes again: 65 tables/616 rows, 290 ms restore, no cleanup failure, exact restored
  encrypted review evidence, 884 unit/contract cases, dependency/source/secret scans.
  The initial historical population failure is not assigned an invented cause.
- Final rebuilt API/web images pass current HIGH/CRITICAL vulnerability scans;
  eight-service health, scheduled private synthetic export/frozen retry and scoped
  request-metrics smoke pass. Persistent stack is updated and left running.

No destructive migration, external inference/Gemini, real learner data or production
approval. Exact-source hosted run 39155326659 passes at `a357222`, now on main; the merged
source branch is removed locally/remotely. The
current sprint is now concise; earlier detailed checkpoints are preserved verbatim in
[the historical snapshot](SPRINT_HISTORY_2026_10_18.md), with their status explicitly
superseded to avoid treating old candidate notes as current instructions.
