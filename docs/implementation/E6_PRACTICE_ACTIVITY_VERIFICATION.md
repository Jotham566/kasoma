# Owned practice-day indicator — candidate verification

Requirements: FR-MST-004/005, FR-ID-003, FR-WA-003, NFR-SEC-002,
NFR-ACC-001, NFR-LOC-001 and NFR-MNT-001; approved roadmap 3.5.
Status: implementation candidate; not accepted or promoted.

## Requirement and decisions

The approved roadmap includes a simple streak or consistency indicator. Existing
Progress has no such display. [ADR-062](../decisions/ADR/062-owned-practice-activity.md)
records a read-only seven-Kampala-calendar-day count, including today, for the selected
subject. It preserves [ADR-024](../decisions/ADR/024-progress-history.md)'s access,
sealed diagnostics and absence of a stored streak/reward system. This ordinary MVP
display decision grants no new privacy/erasure permission and does not approve ADR-061.

Use the same explicit read timestamp and validated visible GRADED evidence already
loaded for progress. Distinct dates deduplicate mappings/attempts naturally. Include
wrong graded answers and all channels. Exclude pending grades and every incomplete
or abandoned/expired diagnostic. Original attempt dates determine the count even if
short-text results become available later. No extra SQL, replay, writes, cache or table.

The optional additive DTO supports older-server rollout; the new backend always emits
an object. Missing/unsupported data renders unavailable rather than zero. The modern
responsive card shows text, date range and a labelled meter using existing styles.
No rankings, notifications, penalties, public identity or academic-accuracy claim.

## Regression evidence and commands

Before implementation, new activity assertions fail in five integration cases with
missing practice_activity; 26 existing contract/history controls pass. This confirms
a missing approved MVP display rather than inferring it from a roadmap checkbox.
Initial implementation passes 54 focused cases. Expanded tests add normal OTP/grade
transactions across Kampala midnight, wrong-answer activity, selected-subject isolation
and explicit web/WhatsApp counts, alongside duplicate/date/DTO/sealed-result controls.

- `make test-progress`: expanded pure/rollup/replay, progress and shared channel suites;
  55 focused cases pass in 56.85s, including 14 actual PostgreSQL integration cases
  and 41 pure/rollup/replay cases; these are not 55 integration cases.
- `make openapi` regenerates the additive schema and TypeScript contracts.
- `make test-web-progress`: new standard three-engine progress journey target; covers
  empty/positive meter, incomplete diagnostics, older-response absence, offline retry,
  keyboard/axe and 320-pixel layout. The final three-engine run passes Chromium 13.2s, Firefox 15.8s and WebKit 13.5s.
  Screenshot review places the primary continuation action before the secondary
  activity card; a bounding-box assertion protects that order at 320 pixels.
  Initial unnamed-project screenshots collided; browserName now keeps three distinct
  images. The final Chromium positive screenshot is visually inspected; full physical/
  branded-browser review is not inferred.
- `make format`, `make lint openapi-check build` pass after final UI ordering.
  Generated contracts match. `make test-unit` passes 1,146 unit/contract and 35 tooling
  cases; the three existing deprecation/intentional network-denial warnings remain.
- `make security security-source` passes with no known dependency vulnerabilities
  or source leaks. `make containers security-containers container-smoke` passes;
  all services remain running. No migration or dependency change is introduced.
- The feature's own full hosted acceptance and combined-source load verification
  remain pending. Performance run 39286019222 at 58d598e cannot establish acceptance
  of this new activity/API/UI tree. Integrate the verified performance baseline before
  the final combined-source load/hosted run; do not replace its active branch head.

Native app/branded-browser review was unavailable because the Mac was locked. Existing
IAB/automated engines do not substitute for physical/branded browser acceptance. Keep
all normal Docker services running. No real data, inference, Gemini or external delivery.

## Verified performance baseline integrated

Main 83f30cc publishes complete hosted 39286019222's verified performance source58d598e
plus Markdown/aggregate closeout. Its merged branch is removed. That baseline is now
merged into the activity candidate; overlapping documentation and Make targets retain
both changes. The combined tree still requires its own targeted/load/hosted verification;
the earlier performance CI does not accept this API/UI feature. ADR-061 stays unapproved.

## Combined native checks before publication

After integrating main 83f30cc, `make test-progress test-fresh-session-response` passes
55 focused cases in 59.12s and 40 assessment integration cases in 158.43s. Seven channel
cases occur in both targets; these are 95 executions, not 95 distinct integration tests.
`make test-unit` passes 1,146 unit/contract and 35 tooling cases, with 484 integration
cases deselected. Quality/types/contracts/build, security/source/images and eight-service
container smoke pass. The combined progress journey passes Chromium 18.1s, Firefox 19.1s
and WebKit 16.1s, including real graded activity, sealed diagnostic exclusion, legacy
absence, offline retry, axe and narrow primary-action order. Native branded/physical
review remains separate. Both source-pinned load profiles and the feature's own full
hosted run are still required; no prior CI result substitutes for this combined tree.

## Published candidate and objective load observation

Combined runtime/test/Make source 78ca959da5e2866d6489d88bfb8f148bc6366cd8 is pushed
on codex/practice-consistency. Its own hosted 39294126038 is in progress. Do not replace
that branch head while verification runs. Main 83f30cc retains the separately accepted
performance runtime; the activity feature is not promoted or accepted.

Standard `make load-objective` passes at this combined source: 7,000 HTTP requests,
zero errors, 500 completed learners/2,500 grades and 50 peak concurrent requests.
START p95/p99 is 455.214/1,002.465ms; PROGRESS p95 is 14.087ms and ANSWER p95 is 27.497ms.
Owned database/role cleanup succeeds. The [source-pinned aggregate report](evidence/E6_PRACTICE_ACTIVITY_OBJECTIVE_LOCAL_2026_10_19_78ca959.json)
contains no learner/source identifiers or payloads and explicitly excludes production
acceptance/database resource measurement. The mixed-history observation below completes this native pair; these
positive observations do not explain prior START variance or close release gates.

## Manual-review environment

The native UI inventory reports the Mac locked and automatic unlock unavailable.
Unlock was requested once from the owner; no bypass or inferred manual acceptance.
The three-engine isolated screenshot/keyboard/axe checks above remain valid within
their own scope. Actual branded browsers, assistive technology and physical devices
still require their separate observations/evidence.

## Mixed-history result at the same combined source

Standard `make load-history-mixed` passes at 78ca959 with 25,000 prior grades and 27,500
final grades/5,500 completed sessions. All 7,000 requests succeed; 500 learners complete
at 50 peak concurrent HTTP requests, and owned cleanup succeeds. START p95/p99 is
409.196/985.502ms; PROGRESS p95 is 16.522ms. Numeric/choice ANSWER p95 is 28.493/28.537ms
with 1,250 timed answers per format; observed answer dispatch is 20/s.
The [source-pinned aggregate report](evidence/E6_PRACTICE_ACTIVITY_HISTORY_MIXED_LOCAL_2026_10_19_78ca959.json)
contains counts/timings only, not learner/source identifiers or payloads. Database
resources and production acceptance remain explicitly unmeasured/unapproved.

Both native profiles ran once sequentially after other native checks completed; no
threshold, warm-up or retry change. Earlier failed history START p95 559.306ms remains
failed and unexplained. These passes do not establish real-provider/soak/release SLOs.
The exact source's full hosted 39294126038 remains in progress; keep its branch head
unchanged. Only Markdown/aggregate JSON closeout follows runtime/test/Make source 78ca959.

## Files in the implementation increment

- Projection/contracts: services/practice_activity.py, services/progress.py and
  services/progress_contracts.py.
- UI/generated clients: apps/web/app/learning-dashboard.tsx,
  packages/api-client/openapi.json and packages/api-client/src/schema.d.ts.
- Commands/tests: Makefile; tests/contract/test_practice_activity.py;
  tests/integration/test_progress.py and test_channel_assessment.py;
  tests/e2e/progress.spec.ts.
- Decisions/specifications: ADR-062, ADR-024 follow-up, ADR index and decision log;
  domain/API/UX specifications.
- Evidence/tracking: AGENTS.md, CHANGELOG.md, current sprint, requirements traceability,
  this verification and the two aggregate reports. No migration, dependency or provider
  implementation/configuration change.

## Hosted failure and unchanged focused diagnosis

Full hosted [39294126038](https://github.com/Jotham566/kasoma/actions/runs/39294126038)
at exact source 78ca959 is terminal FAILED. Setup/migrations/seed, focused controls,
1,146 unit/contract, 484 integration (1,512.52s), 35 tooling, lint/types/contracts/build,
restricted login and logical recovery pass. Recovery verifies 69 tables/686 rows in
548ms, no cleanup failures and stripped retirement execution denied.

The ordinary browser stage passes Chromium 33, Firefox 33 and 16 WebKit cases, then
fails WebKit's data-requests.spec.ts:167 journey at the unchanged 30-second total
test timeout. There is no failing-action stack in the hosted report. The remaining
16 ordinary WebKit cases, 12 short-text cases and later security/image/service stages
are not executed; this is not complete hosted acceptance. Deliberate truncated-export
transport errors appear in the fault tests and do not identify this timeout's cause.

Unchanged `make test-web-privacy` on the combined recovery candidate passes six native
browser executions. The long journey takes 7.7s Chromium, 10.0s Firefox and 8.6s WebKit;
whole commands take 21.0/23.8/21.7s including setup. These focused native passes do not
explain the hosted failure or prove a fix. No timeout, assertion, retry, action or
product behavior is changed. The failed result remains failed.

Separate combined runtime/test/Make source adf432879a8b55eeb1f9e8d59f5d6b053f76bf56
includes the independently needed recovery-role correction and this activity feature.
Its full hosted [39299684285](https://github.com/Jotham566/kasoma/actions/runs/39299684285)
started before the preceding timeout result was inspected and remains in progress.
Neither branch is promoted; main remains e7a4fc0. Do not replace the live combined
head for Markdown closeout. Full MVP/release gates and the unresolved timeout remain.
