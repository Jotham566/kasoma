# Historical sprint checkpoints — 18 October 2026

This preserved snapshot records earlier candidate stages. Its pending/current wording
is historical and does not override [CURRENT_SPRINT.md](CURRENT_SPRINT.md) or the live
requirements/release evidence. It is retained to preserve failure and promotion history.

# Current sprint: short-text grading integration

Updated 18 October 2026. This header supersedes the historical slice notes below.
Current verified source on main is `17abb2d`: independent review, responsive staff
navigation and offline report comparison pass hosted runs 39150319607/39151730479.
Their merged branches are removed locally and remotely. Active follow-up is
`codex/grading-operations`; only that unmerged work remains. The disabled synthetic learner-flow source passes hosted run
[39143803289](https://github.com/Jotham566/kasoma/actions/runs/39143803289) and is
promoted to main. Its merged branch is removed locally and remotely.
Current next-slice branch: `codex/grading-expert-review`, based on that candidate.
Do not promote the next branch ahead of its verification.

## Active slice: grading queue operations

Offline report comparison `17abb2d` passes local verification and is pushed for
[hosted acceptance](https://github.com/Jotham566/kasoma/actions/runs/39151730479).
Active branch `codex/grading-operations` addresses FR-OPS-002, NFR-OBS-001 and
NFR-SEC-002 through the existing bounded ADMIN snapshot and dashboard. It adds grading
queue/lease age, terminal/processing-fallback counts, pending audits and historical
post-activation disablement, with a local stale-queue alert. No model cost, academic
error rate or scoring approval is inferred. See
[readiness](E8_GRADING_OPERATIONS_READINESS.md) and
[ADR-053](../decisions/ADR/053-bounded-grading-operations.md); acceptance is pending.

## Active follow-up: offline report comparison

Staff navigation `3775ae1` passes local serial/browser/image verification and is pushed
for [hosted acceptance](https://github.com/Jotham566/kasoma/actions/runs/39151218081).
Active branch `codex/offline-evaluation-reports` implements FR-GRD-003/004, FR-OPS-002
and NFR-MNT-001 through the missing offline comparison command only. See
[readiness](E4_EVALUATION_REPORT_READINESS.md) and
[ADR-052](../decisions/ADR/052-offline-evaluation-report-comparison.md).
No model, Gemini, messaging or cloud call is made; no academic approval or actual
scoring is enabled. Local lint/types/contracts, 881 unit/contract and 35 tooling cases,
37 new reader/contract/CLI cases, actual Make invocation and source/dependency security
pass. See [report verification](E4_EVALUATION_REPORT_VERIFICATION.md). Hosted acceptance
remains required before promotion.

## Active follow-up: compact staff navigation

Expert-review candidate `2164209` is committed/pushed and undergoing exact-source
[hosted verification](https://github.com/Jotham566/kasoma/actions/runs/39150319607).
The next UI-only slice is on `codex/staff-mobile-navigation`, based on that candidate:
NFR-ACC-001/NFR-COMP-001, an explicit keyboard-accessible mobile workspace menu,
unchanged desktop destinations and close-on-navigation behavior. It addresses the
excessive header height observed in review screenshots. No API/schema or architectural
change is needed. See [navigation evidence](E6_STAFF_NAVIGATION_VERIFICATION.md).
Local lint/build/contracts and serial acceptance pass (104 browser executions including
200% text). Final rebuilt images, service/export/metrics smoke and vulnerability/source
scans pass. Exact-source hosted verification remains required before promotion.

## Current verification and promotion state

- Export/UI/request-aggregation candidate `5f959ef` passes the complete hosted pipeline
  [38033307073](https://github.com/Jotham566/kasoma/actions/runs/38033307073), including
  Linux WebKit controls, all browser engines, backend, recovery, security and containers.
  This resolves the earlier transport/registry acceptance failures for that source.
- Calibration-band commit `46a0f8a` passes hosted verification in run
  [38034913518](https://github.com/Jotham566/kasoma/actions/runs/38034913518).
- Publication/audit assignment migrations 0030/0031 and privacy integration are merged.
  Twelve focused SQL cases, 19 existing hold cases, restricted-login verification,
  six privacy browser executions, populated recovery, lint/types/contracts, rebuilt-image
  scans and eight-service export/metrics smoke pass. Full backend regression passes 780 unit/contract, 35 tooling and
  291 integration cases, supplemented by the final focused assertions. Security
  retry passes after a PyPI network timeout. Exact-source hosted run
  [39137945443](https://github.com/Jotham566/kasoma/actions/runs/39137945443) passes;
  the verified commit was promoted to main and merged branches were removed.
  See [publication evidence](E4_PUBLICATION_VERIFICATION.md).
- Candidate migration 0032 and the synthetic learner flow are under verification:
  encrypted submissions/results, durable one-claim processing, pending/neutral UI,
  diagnostic sealing, owned exports and restricted-login execution. The ordinary
  application has neither report nor safety authority and defaults to disabled.
  See [current checklist](E4_SHORT_TEXT_FLOW_IMPLEMENTATION.md).
- Latest candidate evidence: 99 stable browser executions, 18 focused flow cases,
  actual restricted-login encrypted publication, 831 unit/contract and 35 tooling
  cases, lint/types/contracts, source/dependency security, populated encrypted logical
  recovery and rebuilt eight-service export/metrics smoke pass. The broad backend
  passes 307 integration cases (later additions pass in focused runs).
  Hosted verification, including current container vulnerability scanning, now passes.
  Normal runtime is disabled;
  independent expert review and rolling disablement are the next implementation.

After a power interruption, Git work is intact. Docker Desktop and all eight persistent
services are restored and healthy from existing volumes. Local scanner transport failure
and interruption are not reported as passing evidence; the hosted source gate passes.

## Immediate implementation sequence

The [expert review readiness assessment](E4_EXPERT_REVIEW_READINESS.md) identifies
completed-review storage/access, exact privacy coverage and a release-subset sampling
gap. [ADR-051](../decisions/ADR/051-blinded-review-and-release-unit-sampling.md) proposes
additional within-session/band sampling without rewriting global ordinals. Candidate migration 0033, staff API/UI, privacy coverage and atomic runtime disablement
are implemented and pass local verification: 844 unit/contract, 35 tooling, 324 broad
integration cases plus final 32-case review/18-case encrypted-flow checks, 102 browser
executions, restricted login, repeat populated restore and rebuilt container scans/smoke.
See [expert-review evidence](E4_EXPERT_REVIEW_VERIFICATION.md). Exact-source hosted
verification remains required before promotion; real grading remains disabled.

Finish learner-flow regression and recovery acceptance, independent blinded expert review and atomic band
disablement with the short-text worker, grade/mastery transaction and learner fallback.
No short-text learner assignment, real model call or genuine calibration approval is
implied by the storage fixtures. External academic/privacy/provider/pilot gates remain
in [the release register](RELEASE_GATES.md).

## Local review stack

The local review stack now runs additive migration 0033 and rebuilt expert-review
candidate images; health, synthetic scheduled export and scoped metrics smoke pass.
Normal learner short-text scoring remains disabled. Current vulnerability scans pass.

All eight Compose services are running and healthy: web, API, ordinary worker, dedicated export
worker, PostgreSQL/pgvector, Redis, private MinIO and Mailpit. Keep them running for user review.

- UI: http://localhost:3000
- Local email capture: http://localhost:8025
- Use fictional details only; real learner/guardian data is prohibited.
- Synthetic choice, numeric, diagnostic, hints, multiple-choice and reassessment fixtures are seeded.
- `make seed` now passes catalog and private storage initialization.

Earlier MinIO download failures are resolved. The browser installer completed pinned Chromium, its headless shell, Firefox and WebKit.  See the [local runbook](../runbooks/LOCAL_DEVELOPMENT.md).

## Candidate export slice

Requirements: FR-ID-006, FR-OPS-002/003, NFR-SEC-001/002, NFR-OBS-001 and NFR-MNT-001.
[ADR-048](../decisions/ADR/048-asynchronous-owned-export-delivery.md) remains proposed until its
full acceptance gates pass. Candidate API, learner controls and scheduler/worker wiring are
active locally; do not promote unverified work to main.

Implemented: recent-owner queue/status/frozen download, additive job/generation constraints,
consistent bounded projection, authorization rechecks, encrypted publication, bounded cleanup,
separate hard-limited worker, exact-length cancellable transport, native browser downloads and
minimized operational metrics. Existing synchronous exports remain compatible. This does not
enable deletion or change legal accountability retention.

Current evidence:

- 608 unit/contract and 32 tooling cases pass; lint, formatting and types pass.
- 59 storage cases pass, including actual signed MinIO reads, private-access denial and owned cleanup.
- 41 focused lifecycle/API cases and 15 worker checks pass, including real process hard-stop/recovery.
- Complete native `make migrate test security` passes: 606 unit/contract cases, 32 tooling cases
  and 245 integration cases, including the previously unavailable real MinIO checks. Two later
  smoke-probe unit cases also pass in the separate 608-case unit run. Dependency/security checks pass.
- Full pinned Chromium passes 30 cases across both shards, including native cancellation/corruption,
  frozen retry, privacy review and operational metrics. Firefox/WebKit and hosted regression remain open. Native Firefox now reproduces two
  attachment failures (cancellation cleanup and corruption download-completion timeout); focused
  serial reproduction also fails. See export verification; do not promote this candidate.
- Populated synthetic logical recovery passes again (56 tables/285 rows, 256 ms); object-storage restore
  and production PITR/RPO/RTO are explicitly unverified.
- `make container-smoke` passes both eight-service health and a real scheduled export through
  Next/API/Beat/export-worker/MinIO, with exact-length frozen retry and scoped session logout.
- Source secret scanning and generated OpenAPI/client checks pass.

Full chronology and evidence boundaries: [export verification](E8_ASYNC_EXPORT_VERIFICATION.md).
The isolated content-admin browser check also passes. Container vulnerability scanning now passes for API and web with no HIGH/CRITICAL findings.
The initial five-minute database-download timeout was resolved by the configurable 30-minute bound.
Before promotion: finish the remaining browser matrix, container security and hosted CI; resolve any failures, then record ADR status and promotion evidence.

## Learner UI work

Requirements: FR-ID-001/003/004/005, FR-DIAG-004/005, FR-REV-005/006, FR-GRD-006,
FR-MST-004/005 and NFR-ACC-001/BW-001/COMP-001/LOC-001/MNT-001.

The running web now includes shared learner navigation and keyboard skip access, a responsive
home/recommendation layout, onboarding cards/fields and consent-gated diagnostic navigation,
and clearer practice/diagnostic questions with a server-derived saved-answer progress bar.
Synthetic notices and existing consent, scoring, hint/solution, sealing and replay rules remain.
Staff routes remain separate. No external assets, fonts, analytics or provider dependencies were added.

Thirty Chromium cases pass, including 320/1280-pixel home/onboarding checks, 200% text reflow,
44-pixel navigation targets, keyboard/axe, existing learning journeys and saved-progress assertions.
Desktop/mobile captures were inspected and retained under `.local/ui-review`. The current web image
is deployed locally; source-only rebuilds reuse the frozen dependency layer. This is not physical-
device, screen-reader, approved-brand or pilot acceptance.

Progress/history presentation passes lint/types/build and all 30 Chromium cases, including
320-pixel reflow, touch targets, owned paging and sealed diagnostic resume. Screenshots were
inspected without clipping; its rebuilt local web is healthy.
Privacy/channel presentation passes lint/types/build and all 30 Chromium cases, including mobile
privacy axe/reflow, frozen export retry, channel STOP/unlink and Kampala expiry. Captures reviewed.
Shared staff navigation passes lint/types/build, 30 Chromium journeys, isolated editor and
source/contract checks. Desktop/mobile captures reviewed; the rebuilt web image is available.
Operations/flags/import presentation passes lint/types/build and 30 Chromium journeys;
authenticated operations captures reviewed at desktop and 320 pixels.
Content editor presentation passes lint/types/build, mobile/axe/exact-save-reload and all
30 Chromium journeys. Captures reviewed; human usability acceptance remains open.
Next UI work: final learner action hierarchy and supported-device acceptance;
review action hierarchy and supported-device usability. Keep API state authoritative, sparse-evidence
wording accurate and the 250,000-byte cold-question transfer gate unchanged.
[Plan and evidence](E6_LEARNER_UI_READINESS.md).

## Verified main baseline

Main `bb2f4eb` passed hosted CI 37962081120 for the private storage adapter: 721 Python cases,
66 browser executions and the full recovery/security/container pipeline. Its completed branch was
removed. Earlier merged evidence includes [incremental exports](E8_EXPORT_ENCODING_VERIFICATION.md),
[encrypted artifact format](E8_PRIVATE_EXPORT_ARTIFACT_VERIFICATION.md),
[objective load](E9_OBJECTIVE_LOAD_VERIFICATION.md), [mobile reflow](E9_MOBILE_REFLOW_VERIFICATION.md),
[reviewed rubrics](E2_REVIEWED_RUBRICS_VERIFICATION.md) and
[accountability holds](E8_ACCOUNTABILITY_HOLDS_VERIFICATION.md).
See [requirements traceability](REQUIREMENTS_TRACEABILITY.md) for the complete historical register.

## Short-text integration follow-up

Durable calibration metadata/state is under full regression: migration 0028 enforces
disabled registration, immutable report metadata, one-time activation and sticky
disablement with automatic exact history. Twelve focused SQL cases, the real restricted
login and populated 60-table recovery pass. There is no activation application command
or learner enablement. See [band storage verification](E4_BAND_STORAGE_VERIFICATION.md).
Lint/types, contracts, security/source scans and rebuilt container health/export/metrics
smoke also pass. Full backend regression passes 279 integration and 780 unit/contract
cases plus 35 tooling checks. A later scope-reparenting regression found a missing
persistent binding; additive migration 0029 fixes it. All 13 focused SQL cases, populated
upgrade, restricted login and recovery pass after that fix. Follow-up branch
`codex/grading-band-state` awaits complete hosted acceptance before main promotion.

FR-GRD-003/004/005 / FR-MST-001: versioned calibration/audit eligibility passes
780 unit/contract and 35 tooling cases, lint/types, contracts and security checks.
It enforces separate overall/held-out thresholds, exact scope/version/
length matching, approved subgroup review, critical-error exclusion and audit coverage.
ADR-050 proposes the rolling/sampling policy; no academic acceptance, report authority,
durable disablement or learner scoring is inferred. Next wire approved report/state
persistence and atomic audit assignment before worker publication. See
[eligibility verification](E4_ELIGIBILITY_VERIFICATION.md).

FR-GRD-003/004/005, FR-MST-001 and FR-ID-006: the updated
[readiness assessment](E4_SHORT_TEXT_INTEGRATION_READINESS.md) identifies pending/neutral
contract changes, immutable-grade/mastery boundaries and privacy coverage dependencies.
It now includes the required >=10% blinded beta audit and automatic band disablement
below 90% exact agreement or after a critical error. No learner grading is enabled.
Next: propose the eligibility/pending-workflow ADR, then implement the complete synthetic
worker-to-learner path with neutral fallback and corresponding persistence/privacy tests.

## Remaining MVP and release gates

[Channel-hold readiness](E8_CHANNEL_HOLD_READINESS.md) records the inspected mutable-state and
sensitive-field clearing constraints. A preservation design/ADR is required before implementation;
no current hold, retention or deletion behavior changes.

Learner short-text integration/fallback and academic calibration, aggregate telemetry, complete
hold coverage, deletion/anonymization and accountability-retention processors remain incomplete.
Do not expand into mature whitepaper features or silently reduce these requirements.

The [release register](RELEASE_GATES.md) retains external gates: kickoff/capacity, approved academic
mappings/rights/inventory/benchmark, privacy and safeguarding approval, Week 8 providers, production
security/operations, PITR/RPO/RTO, supported devices and pilot sign-offs. Synthetic tests are not
substitutes. No kickoff date or delivery-week acceptance is inferred from engineering progress.

Native export diagnosis: plain loopback HTTP controls reproduce both Firefox behaviors
without Kasoma; Chromium passes the corrected controls. This narrows investigation to
the pinned Firefox automation boundary, but does not waive the application gate.

NFR-ACC-001 / NFR-COMP-001: WebKit's first shard passed 14 cases (including both
export faults) and failed the Tab-to-link assumption. The test now uses the macOS
WebKit Option-Tab shortcut, with unchanged focus assertions; all 30 native WebKit application cases now pass.

FR-ID-006 transport hardening: a five-second service-side object-read bound now
protects against stalled adapters independently of browser disconnects. All 42 focused
export integration cases pass; Firefox's real-gateway stall/cancel/frozen-retry case
now passes. Native-manager controls reject HTTP/1.1 corruption, but the real-gateway
Firefox corruption acceptance remains open. CI 37981771037 failed on the prior head.

Updated local stack evidence: rebuilt images and all eight healthy services pass the
real scheduled export smoke and frozen retry. API/web image scans report no
HIGH/CRITICAL findings. Lint/types, generated-contract/source-secret checks and
624 unit/contract plus 32 tooling cases pass. Full integration/security regression
is active in `.local/export-bound-full-regression.log`; final result pending.

Firefox corruption now passes against the real application using the same pinned
browser's ordinary download manager. It verifies native rejection, closed reader,
READY state and exact frozen retry; the case remains mandatory. Full Firefox suite
is running. Native helper input/protocol checks pass; ADR-048 records the verification
resolution and remains proposed until complete native/hosted gates pass.

The full service-bound integration/security run passed all 246 integration cases and
dependency/security checks. Firefox's export shard passes. Two later home-navigation
checks found fractional rounding below the 44px target minimum; shared learner/staff
navigation is now 48px, preserving the >=44px assertion. Full three-engine rerun active.

FR-GRD-004/005 and NFR-SEC-002: internal `services/short_text_contracts.py` adds bounded
answer input and distinct pending/neutral outcomes, rejecting scores and hidden/provider
material. ADR-050 remains proposed; runtime routes, worker and privacy integration are
not implemented by these contracts. Verification passes: 699 unit/contract tests (33 new outcome/input cases), 35 tooling
checks, format/lint/types and generated-contract comparison. No HTTP schema changed.

NFR-SEC-002 / FR-GRD-003 / FR-ID-006: `services/short_text_answers.py` implements the
bounded authenticated answer format proposed by ADR-050. Synthetic real-crypto tests
cover exact Unicode/escape preservation, cross-record replay, tampering, wrong keys,
bounds and closed errors. Verification passes: 730 unit/contract cases (31 new
answer-protection cases), 35 tooling checks, formatting/lint/types, generated-contract
comparison and source secret scanning. No database/API path is enabled;
exports and new workflow-record hold/retention coverage remain required before integration.

FR-GRD-003/004/005 and NFR-SEC-002: `services/short_text_workflow.py` adds the proposed
one-claim transition policy, inclusive queue/lease expiry, clock/state validation and
immutable terminal replay. A crashed claim cannot reset the global model-call budget.
Verification passes: `make format lint test-unit openapi-check security-source`,
including 747 unit/contract cases (17 new transitions) and 35 tooling checks. Log:
`.local/short-text-workflow-checks.log`. This is a transition component only; durable SQL locking,
worker wiring, eligibility, grade/mastery publication and privacy coverage are unimplemented.

FR-GRD-004/005 / NFR-SEC-002: migration 0026, grading-work models and transactional
storage are under verification. Commands have one claim, bounded expiry and immutable
transition snapshots. No learner/worker path is enabled. Use `make test-grading-work`;
privacy inventory/export/hold coverage and restricted-role checks remain integration gates.

Durable-store focused verification passes 24 cases (seven PostgreSQL, 17 transition),
including contention, rollback, expiry, publication consistency and owned/foreign
export projection. Work/history counts are in deletion inventory. Full backend
regression is running; exact-record holds and restricted-role extension still gate
runtime enablement. See `docs/implementation/E4_DURABLE_GRADING_VERIFICATION.md`.

NFR-SEC-001/002: the durable-work restricted-login extension passes independently:
queue, claim and neutral completion work with bounded grants; history mutation,
command deletion, schema changes and immutable attempt-ID edits are rejected. Source
secret scanning and generated-contract comparison pass. Full backend run remains live;
new history hold coverage and worker/publication integration are still pending.

FR-ID-006 / BR-010 / NFR-SEC-002: migration 0027 and the existing hold service now
support exact immutable grading-history records, preserving ownership and independent
review. The administrator selector/generated contracts include GRADING_HISTORY;
incomplete-coverage wording no longer reports a stale record count. Focused integration
and three-engine privacy verification are pending; learner grading remains disabled.

Durable grading/history local evidence: 26 focused cases and six privacy browser
executions pass across Chromium/Firefox/WebKit. Populated isolated recovery passes
(58 tables, 291 rows, 948 ms) with immutable grading snapshots. Container refresh and
both smoke probes pass. Bandit found a runtime assert in the earlier workflow helper;
explicit validation replaces it and Bandit passes. Full backend/final security checks
remain active; see `docs/implementation/E4_DURABLE_GRADING_VERIFICATION.md`.

Latest hosted run 38004530911 at `84772f1` has passed full backend regression and moved
to browser/security/container checks. Current local durable-storage/history code has
747 unit/contract and 35 tooling cases passing, plus complete source/dependency checks.
Its broad integration run and final image scan/refresh are still active; nothing is
promoted to main before the relevant hosted gate completes.

Durable grading/history local gate now passes: full migration/backend run has 747
unit/contract, 35 tooling and 266 integration cases; two additional history-hold cases
and the extended restricted-login check pass separately. Six three-engine privacy
journeys, populated logical recovery, source/dependency checks, final rebuilt image
scans and eight-service smoke pass. Exact-head hosted acceptance remains required;
worker/learner/scoring integration is still disabled.

## Publication and audit assignment preparation — 10 October 2026

FR-GRD-003/004, FR-MST-001, FR-ID-006 and NFR-SEC-002: migrations 0030/0031
add a band-locked publication ordinal, atomic minimum-10% audit assignment, immutable
records and exact publication/assignment holds. Owned exports omit calibration IDs,
ordinals and sampling flags; deletion inventory includes both personal record types.
The generated hold contract and staff selector include the new types. These are
format-independent storage controls tested with valid synthetic objective grades;
learner short-text scoring remains disabled. Grade/mastery integration, blinded expert
review, rolling audit outcomes and automatic disablement remain required.

Initial eight PostgreSQL cases pass after correcting a test-only projection import.
Additional negative and restricted-login checks are running. Full regression, populated
recovery and browser acceptance remain required; no completion or promotion is claimed.
See [publication verification](E4_PUBLICATION_VERIFICATION.md).

Verification update: `make test-grading-publications` passes 10 PostgreSQL cases;
`make test-legal-holds` passes 19 existing preservation cases; the real restricted-login
case passes with INSERT-only publication/assignment rights and guarded counter UPDATE.
It denies record rewriting/deletion and band activation/approval changes. Formatting,
lint/types and generated contracts pass. The isolated populated recovery now compares
63 tables / 302 rows, restores in 282 ms and verifies publication/assignment/counter
immutability, with no cleanup failures. Its synthetic owner-only band transition is
restricted to the generated recovery-source database name and is not academic evidence.
Full backend and three-engine privacy regressions are running; acceptance remains open.

Diagnostic disclosure follow-up: all 11 focused publication cases pass, including a
complete 15-question diagnostic proving publication/audit records remain absent from
owned exports until completion. The first privacy-browser run used a stale production
web build and failed the new option-list assertion (one pass, one failure). No assertion
was weakened; `make build test-web-privacy` is rerunning against the rebuilt source.
The full backend run began before this final diagnostic test was added; its evidence
must be read alongside the 11-case focused result, not claimed as an exact final-tree run.

Rebuilt browser acceptance: `make build test-web-privacy` passes all six executions
across Chromium, Firefox and WebKit, including the new hold selector and unchanged
ownership/retry/export protections. Final `make lint openapi-check` also passes.
The earlier stale-build failure is resolved. Full backend/security regression and
rebuilt-container checks remain live; no commit or main promotion is claimed yet.

Final focused checks pass 12 publication cases and 13 band cases, including foreign
scope/replay rejection and populated upgrade counter backfill. Rebuilt container scans,
eight-service export/metrics smoke and source checks pass. Full backend/security
regression remains running; the [publication report](E4_PUBLICATION_VERIFICATION.md)
consolidates final evidence and the resolved initial test/browser failures.

## Learner short-text flow in progress — 18 October 2026

Requirements: FR-GRD-003/004/005, FR-MST-001 and FR-ID-006. The next cohesive
slice connects encrypted submission, bounded worker execution, authorized outcomes,
mastery, audit and learner resume/poll/fallback. Current rubric results now have a strict
partial-credit contract with matching rubric/item version, unique criteria, coherent
score/totals, finite confidence and minimized representations. Candidate projection
rechecks answer evidence and authored feedback. This formatter grants no eligibility,
publication or disclosure authority. Its evidence excerpts require encrypted persistence
and current owner authorization before learner projection.

`make format lint test-unit openapi-check` passes 808 unit/contract and 35 tooling
checks. The 28 new result cases reject forged evidence/feedback, invalid/mismatched
rubrics, duplicate criteria, inconsistent scores and unsupported fields. HTTP schemas,
assignment guards and learner delivery remain unchanged at this intermediate point.
No short-text feature completion is claimed; see the flow implementation checklist.

## Cohesive short-text candidate under verification — 18 October 2026

FR-GRD-003/004/005, FR-MST-001, FR-ID-003/006 and NFR-SEC-002: the working
branch now includes draft migration 0032, encrypted result storage/projection, pinned
assignment bands, atomic encrypted attempt/receipt/work submission, owned pending and
neutral result retrieval, and a finite-lease processor. The processor releases locks
for model work, rechecks current consent/content/report/band before each dispatch and
publication, and commits grade/mastery/audit together. The default report and safety
authorities are unavailable, runtime enablement defaults false, and only deterministic
fake providers are implemented in this candidate. No real report or safety approval
has been created. Trusted isolated fixtures supply synthetic authorities for tests.

The intermediate API/worker suites pass 10 cases, including a complete synthetic
pending-to-grade-to-mastery/audit/export path and before-second-pass withdrawal,
disablement and lease-expiry barriers. The result encryption suite passes 828 unit/
contract and 35 tooling cases. Existing rubric/band checks pass after fixing an ORM
foreign-key registration regression; the reproduced objective failure is retained in
`.local/short-text-objective-regression.log` and its passing test remains in the suite.

Newer additions (diagnostic terminal/sealing coordination, queue wake-up/scheduler,
learner pending/poll/fallback UI and reassessment guards) are under verification.
Migration 0032 has only run in isolated test schemas; the persistent Docker review
stack remains on the verified 0031 images. Full regressions, database grants/recovery,
independent blinded expert audit/rolling disablement and browser acceptance remain
required. No learner-flow completion or main promotion is claimed.
