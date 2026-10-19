# Current sprint: verified disposable load-role lifecycle

## Fresh revision response candidate — no empty evidence reads

NFR-PERF-001/002, FR-REV-001/002/005/006, FR-GRD-008, FR-WA-003, NFR-SEC-002
and NFR-MNT-001: the shared start transaction uses its known empty evidence only for
a newly inserted revision. Same-key retries, active resumes and reassessment views
retain current DB reads and full grade/provenance. Three baseline query-budget failures
and the passing answered-resume control become four focused passes with full committed
serialization parity. Expanded 40 integration, 1,130 unit/contract, 35 tooling and nine
three-engine browser cases pass, plus quality/contracts/build and source security.
[Verification](E9_FRESH_SESSION_RESPONSE_VERIFICATION.md) remains candidate pending broader
checks and new load evidence; no claimed p95-variance fix or ADR-061 implementation.

## Proposed synthetic erasure decision — awaiting owner approval

FR-ID-003/005/006, BR-010, FR-GRD-003/004/005, FR-WA-006, FR-OPS-003,
NFR-SEC-002/OBS-001/MNT-001: [ADR-061](../decisions/ADR/061-synthetic-account-erasure-proposal.md) and its
[exact disposition manifest](E8_ERASURE_DISPOSITION_PROPOSAL.md) now propose the full bounded learner
execution/retirement lane against all 69 existing sources, with actual primary keys.
The explicit choices include eligible row removal instead of an unreviewed replacement
identity, exact encrypted profile/contact/reply preservation, post-completion custody,
finite original deadlines and affected-band disablement without counter resets.
A bounded OTP drain prevents pre-closure challenges becoming new registrations after
identifier removal. Staff/representative cases and real-data/release gates remain gaps.
This is documentation only: no migration, new permission, execution or acceptance.
ADR-057/060 approvals do not cover these new choices.

## Erasure proposal assessment — schema and academic dependencies

FR-ID-006/BR-010/FR-GRD-003/004/005/NFR-SEC-002/NFR-MNT-001: schema-only inspection
records 69 tables, 488 columns, 120 foreign keys and 97 triggers. Shared grading counters
and the last 100-review disablement window require an explicit preservation/fail-closed
decision before learner-review destruction. [Readiness](E8_ERASURE_TRANSFORM_READINESS.md)
records these factual dependencies without choosing an erasure transform, new anonymous
dataset or changed academic policy. No learner rows are selected or changed. The [complete catalog inventory](E8_ERASURE_SOURCE_INVENTORY.md) now records all columns/FKs and guard names, independently compared
with live 0042. Readiness also records completed-case hold access, overlapping flag
provenance and unbound OTP ownership gaps. No execution or permission changes.

## Verified bounded disposable load-role lifecycle — 19 October 2026

[Complete hosted39267916272](https://github.com/Jotham566/kasoma/actions/runs/39267916272)
passes at `a23e9bc020014271e8e697bd2518beda9b3a3393`:1,130 unit/contract,
479 integration,35 tooling and111 full browser executions, plus9 focused assessment,
12 interception controls,3 staff UI and3 native WebKit controls. Setup/migration/seed,
restricted logins, lint/types/contracts/build, recovery, dependency/source/image security
and container smoke pass. Logical recovery verifies69 tables/686 rows in561ms, with
no cleanup failure and refused execution after stripped ownership. No object-storage
recovery, production RPO/RTO or external release approval is inferred.

NFR-MNT-001/NFR-SEC-002: both load profiles now clean only a confirmed, exclusively
created role with the same OID, safe attributes and no memberships, after successful
owned database drop. A real two-connection red regression and replacement tests prove
the stronger boundary. All 69 focused native cases pass. No API/schema, grading,
mastery, provider or architecture change; no existing orphan/debug/application resource
cleanup. The normal Docker review stack stays healthy on0042 with retirement false.

Corrected-source objective and unchanged history recheck pass at START p95
428.912/448.045ms with zero errors and successful cleanup. The initial corrected
history run fails at559.306ms and remains failed. Main follow-up39264562568 fails
in initial OTP fixture transport; its exact cause remains unknown, although unchanged
focused Firefox and the current full hosted suite pass. No variance or transport fix
is claimed, no threshold is relaxed and no blanket retry is added. These risks remain
MVP/release work. The following earlier notes retain their then-current status.
Only documentation/aggregate evidence follows the exact verified source tree.

## Diagnostic history recheck and main follow-up failure

The unchanged a23e9bc history recheck passes at START p95 448.045ms with zero errors
and successful cleanup. Its initial559.306ms miss remains failed; variability is
unresolved. Separately, main follow-up39264562568 fails on the export gateway journey's
initial OTP POST socket reset, before export creation; cause/commit state are unknown.
Retain both results without blanket retry or broad acceptance. Current corrected-source
CI remains in progress. [Evidence](E9_LOAD_ROLE_CLEANUP_VERIFICATION.md).

## Retained history-load latency failure

NFR-PERF-001/002/NFR-SCL-001: corrected-sourcea23e9bc history load finishes all7,000
requests without errors and cleans its resources, but fails START p95 at559.306ms
against the unchanged500ms gate. Preserve that failed report. The application tree
is unchanged; cause remains unconfirmed. An unchanged diagnostic recheck is running,
with no performance acceptance inferred. [Evidence](E9_LOAD_ROLE_CLEANUP_VERIFICATION.md).

## Next privacy boundary: account-erasure transform readiness

FR-ID-006/BR-010/FR-OPS-003/NFR-SEC-002/NFR-MNT-001: the
[readiness assessment](E8_ERASURE_TRANSFORM_READINESS.md) ties the current
coded blockers, request/user states and19 hold kinds to the required exact source,
transform, preservation and recovery proposal. It chooses no new policy or execution
behavior and grants no erasure authority. Implementation follows current candidate
publication and a concrete approved destructive-transform decision.

## Candidate correction: exclusive load-role ownership

NFR-MNT-001/NFR-SEC-002: a deterministic two-connection PostgreSQL regression proves
that absence alone can misidentify a concurrently created role as owned. Retain that
one-failure/65-pass red result. Exclusive transactional role creation, confirmed OID
and an identity check at cleanup now pass69 focused cases (55 contract/14 integration),
including concurrent creation and replacement refusal. The original two native HTTP
profiles pass at4614bd3, but do not accept the revised ownership boundary. Lint/types/contracts/build,1,130 unit/contract plus35 tooling and security/source
checks pass. Full revised verification is pending; see [evidence](E9_LOAD_ROLE_CLEANUP_VERIFICATION.md).

## Candidate: disposable load-role lifecycle

NFR-MNT-001/NFR-SEC-002: the shared objective/history-mixed load harness checks that its
exact derived owner role is absent before migration. After stopping its server, closing
engines and successfully dropping its own generated database, it inspects only that
role and removes it only if non-login, non-elevated and without memberships. Absent
roles succeed; unsafe/shared roles, lookup/drop failures and PostgreSQL dependencies
fail cleanup with closed diagnostics. Pre-existing roles and failed-database-drop
resources are preserved. No sweep, DROP OWNED, privilege revocation or application
resource cleanup is introduced. No API/schema/architecture or load thresholds change.

The new regressions first fail16 cases against the old implementation (37 existing
cases pass). `make test-load-role-cleanup` now passes65 cases:53 contract and12 actual
PostgreSQL tests. The latter include fresh migrations through0042 for both profiles,
intentional stops before learner fixtures, all seven prohibited role attributes,
both membership directions and actual dependency refusal. These are lifecycle tests,
not completed HTTP load or performance acceptance. Lint/types/contracts/build,
1,128 unit/contract plus35 tooling, security and source scans pass; full acceptance
remains pending.
See [verification](E9_LOAD_ROLE_CLEANUP_VERIFICATION.md).

## Complete hosted engineering verification — 19 October 2026

[Run 39256037485, attempt 2](https://github.com/Jotham566/kasoma/actions/runs/39256037485/attempts/2)
passes completely at `d8fc0310120fb0b6366f193fdb6aec5f4c799255`. Its application,
tests, contracts, Makefile and workflow match `e33ec69`; later changes are Markdown only.
Verified results: 1,112 unit/contract, 465 integration, 35 tooling and 111 full browser
executions (99 ordinary plus 12 disabled fake short-text), nine focused assessment,
12 interception controls, three staff UI and three native WebKit transport controls.
Setup/migration/seed, actual restricted logins, lint/types/contracts/build,
security/dependency/source/image checks and container smoke all pass. Logical recovery
verifies 69 tables/686 rows in 465 ms, with no cleanup failure and denied execution
after stripped ownership. Object-storage recovery and production RPO/RTO are not proved.

This verifies ADR-060's bounded synthetic executor operations, the guarded test
interception helper and stable feedback actions. It does not complete FR-ID-006/BR-010,
full preservation, account erasure, real-data authority or the MVP release gates.
The eight-service Docker review stack is healthy on 0042 with retirement false;
normal learner short-text scoring remains disabled. No new architecture is adopted.
The next assessed implementation is the bounded disposable load-role lifecycle.

The owner explicitly authorized public repository visibility. GitHub confirms PUBLIC;
current-source and all 125 locally available commit secret scans pass. Earlier billing
refusals and browser failures remain historical failures. The following earlier stage
notes preserve their then-current status; this complete run supersedes their pending
engineering acceptance without retrospectively converting failures into passes.

## Publication held for external Actions capacity

Latest application/test source `e33ec69` is pushed to `codex/export-retirement-operations`.
The confirmed delayed-hints layout correction passes all111 local browser executions,
nine focused assessment cases, lint/types/contracts/build, updated image/source security
and Docker service smoke. All eight services are healthy on0042 at http://localhost:3000;
retirement stays false. See [layout evidence](E3_REVIEW_ACTION_STABILITY_VERIFICATION.md).

Hosted39255125288 is refused before any steps because GitHub reports failed account
payments or insufficient spending capacity. The owner has been asked once to restore
Actions capacity. Main remains verified `e9f688e`; no merge, gate bypass or destruction
of the unmerged branch occurs. A complete hosted run remains required. The earlier
94b40a6/b6aea35 hosted browser failures remain failures. The next
[load-role lifecycle assessment](E9_LOAD_ROLE_CLEANUP_PLAN.md) is ready but unimplemented.

## Active ADR-060 executor operations candidate

FR-ID-006/FR-OPS-003/BR-010/NFR-SEC-002/NFR-MNT-001: separate private LOGIN/configuration,
bounded queue scheduling, count-only finite observations, ADMIN health and read-only
responsive presentation are in verification. See [candidate evidence](E8_EXPORT_RETIREMENT_OPERATIONS_VERIFICATION.md).
Verified SQL and foundation are published through main `e9f688e`; both merged owned
branches are removed locally/remotely. Accepted-main images rebuild and container smoke
pass after power recovery, with all eight services healthy and state false on 0041.
The operations candidate remains separate; no scheduled executor is enabled.
Its 25 focused cases, 1,112 unit/contract and 35 tooling cases, six focused three-engine
browser journeys and 69-table/686-row logical recovery pass locally. The native spawn
registration defect is fixed by a private AppLoader. Final full native verification
passes 465 integration and 108 browser executions, plus image/security/service gates;
source `94b40a6` fails hosted39243195783 in one Chromium `route.fetch` socket reset
during interception; commit status is unknown. All hosted backend/role/recovery/UI/transport gates preceding
that browser step pass. A bounded, guarded test-transport correction and exact
committed-code/retry-key checks are in verification; no application policy changes
or main promotion occur. Corrected source `b6aea35` passes 12 transport controls,
three focused channel journeys, three native Linux attachment controls and all 108
browser executions locally. Hosted39249423592 passes all backend and transport controls but fails a different
WebKit resumed-session pointer transition after 79 ordinary browser passes. No main
promotion occurs. A [review-action layout correction](E3_REVIEW_ACTION_STABILITY_VERIFICATION.md)
reproduces a 47.421875-pixel shift under delayed hints, moves optional review hints
below actions and passes nine focused three-engine cases. Full verification remains
pending; no grading, permissions, API or storage change. Review stack is now 0042 with persisted retirement false.

## Verified synthetic SQL retirement kernel

Approved ADR-060 implementation through source `e5d3d986a66d37fb4e3ee294065c92173777c5dd`
passes complete hosted [39234377840](https://github.com/Jotham566/kasoma/actions/runs/39234377840):
1,096 unit/contract, 456 integration, 35 tooling and 108 browser executions, plus
staff UI/native transport controls, actual restricted logins, migration/seed,
contracts/types/build, recovery, security/image scans and container smoke. Recovery
verifies 69 tables/686 rows in 713 ms, including exact receipt holds and refused
retirement after stripped ownership. The [SQL evidence](E8_EXPORT_RETIREMENT_VERIFICATION.md)
records its four-table scope, bounds and default-disabled isolated execution.

The corrected [hold foundation](E8_EXPORT_EVIDENCE_HOLDS_VERIFICATION.md) separately
passes complete hosted [39232307831](https://github.com/Jotham566/kasoma/actions/runs/39232307831)
at `be2735e`: 1,094 unit/contract, 425 integration, 35 tooling, 108 browser executions
and all engineering gates; logical recovery is 68 tables/685 rows in 602 ms.
Old `5fa939d`/39229138880 remains cancelled after its known three local recovery-helper
failures. The corrected fixture retains all original corruption assertions.

The local full SQL suite was interrupted near its final WhatsApp tests when the
local processes and Docker services stopped. It has no terminal success and is not
counted as a pass. PostgreSQL and all eight services have recovered with existing
volumes/images; no application data, SDK or cache cleanup occurs. Schema is 0041,
retirement state remains false and review public is excluded. Executor operations
are a separate unfinished implementation; no scheduled executor is enabled.

Only Markdown acceptance closeout follows the exact tested SQL/code/test/Makefile/
workflow tree. Full preservation, other retention classes, account erasure, real-data
and external academic/privacy/provider/production release gates remain incomplete.
Provider and UI corrections are already verified/published through main `29eaeee`.

## Earlier verified load source

Load tooling/test source `6b06c53` passes complete hosted
[39217860618](https://github.com/Jotham566/kasoma/actions/runs/39217860618): 1,092
unit/contract, 412 integration, 35 tooling and 108 browser executions, plus UI/transport,
restricted-role, recovery, security, image and service checks. Both native load profiles
also pass, including 25,000 prior grades in the mixed case. Documentation/aggregate
report closeout preserves that exact code/test/Makefile/workflow tree. The full MVP
and real-data/release gates remain incomplete.

The verified source and documentation are published to `main` through `6ebdf71`.
Its merged load branch is removed locally and remotely. Later closeout edits remain
documentation-only and preserve the exact code/test/Makefile/workflow source above.

Independent candidates retain their own acceptance boundaries: provider-fault
isolation source `8a938dd` passes complete hosted
[39220793602](https://github.com/Jotham566/kasoma/actions/runs/39220793602); profile
visibility source `44ae9ad` passes complete hosted
[39222489376](https://github.com/Jotham566/kasoma/actions/runs/39222489376). The latter
passes nine local identity executions and is running in the healthy Docker web
preview. Their complete hosted results are verified separately from this load source.

## Earlier verified application increments

Application/test source `6d53541` passes complete hosted [39185423895](https://github.com/Jotham566/kasoma/actions/runs/39185423895) and is pushed to main
through Markdown-only merge `5de2ce5`. That earlier documentation closeout preserves that
exact application/test/workflow tree. All three merged implementation branches are
removed locally/remotely. Capture source `0a8f674` passes complete hosted
[39183714273](https://github.com/Jotham566/kasoma/actions/runs/39183714273); progress
source `7148a1c` passes complete hosted [39184552472](https://github.com/Jotham566/kasoma/actions/runs/39184552472). Superseded progress run
39184146180 at `3291ef7` is cancelled, not a pass.

## Requirements and implementation

- FR-ID-001/005, NFR-ACC-001 and NFR-MNT-001: the
  [profile reverification visibility correction](E1_CONTACT_REVERIFY_VISIBILITY_VERIFICATION.md)
  removes an unrelated action from the signed-out form. The new regression fails
  before the presentation correction; lint/types/build pass afterward. Corrected
  three-engine verification now passes all nine identity executions, alongside
  1,092 unit/contract, 35 tooling, contracts and security. A public signed-out
  screenshot is recorded. Images build and the corrected Docker web preview is
  verified with all eight services healthy. Complete hosted 39222489376 passes at `44ae9ad`, including 415 integration,
  108 browser executions and full role/recovery/security/image/service checks.

- FR-GRD-003/004/005, FR-MST-001/004/005, NFR-SEC-002 and NFR-MNT-001:
  [fake provider isolation](E9_PROVIDER_FAULT_ISOLATION_VERIFICATION.md) adds three
  bounded regressions for owned web reads during a stalled fake call and neutral
  publication after timeout/failure/fallback. Corrected focused cases, 1,092 unit/contract,
  35 tooling, lint/types/contracts and security pass. Complete hosted 39220793602
  passes with 415 integration, 108 browser executions and full recovery/role/security/
  image/service checks. Normal learner scoring remains off.

- NFR-PERF-001/002, NFR-SCL-001, FR-MST-004/005 and NFR-MNT-001: an independent
  synthetic history/mixed objective load profile is verified independently while ADR-060
  was awaiting approval. It uses normal domain histories and real loopback HTTP without
  runtime changes. See [scope and evidence](E9_HISTORY_MIXED_LOAD_VERIFICATION.md).
  Native profile and complete hosted engineering verification now pass.
  Final fixture coverage is deterministic by subject (144 choice/144 numeric);
  the earlier 293-item candidate correctly fails for missing numeric delivery despite
  zero HTTP errors and successful cleanup. Final source `6b06c53` passes the native
  profile: 7,000 HTTP requests, 1,250 timed answers per format, 27,500 total grades,
  zero errors and successful cleanup; START p95 432.085 ms, numeric answer 27.778 ms.
  The sequential original-baseline recheck also passes: 7,000 requests, zero errors,
  START p95 421.751 ms and successful cleanup. Complete hosted 39217860618 passes
  at that source; startup p99 and broader performance/release gaps remain.
  The local runbook and testing specification now describe the optional command,
  generated-database boundary and sequential execution.

- FR-ID-006, FR-WA-006, FR-OPS-003, BR-010, NFR-SEC-002 and NFR-MNT-001:
  approved ADR-057 exact owned encrypted link/conversation snapshots, additive 0038,
  independent API/SQL guards, atomic finite decisions, replay, disposal, inventory
  and accessible controls. Contacts, message bodies, codes and tokens are excluded.
  STOP/unlink/withdrawal and operational expiry remain independent. The advancing-clock
  conversation correction also addresses FR-WA-002. See
  [capture evidence](E8_CHANNEL_PRESERVATION_VERIFICATION.md).
- FR-MST-004/005, NFR-PERF-001 and NFR-MNT-001: request-local immutable estimate reuse
  under unchanged ADR-024. No shared cache, stored aggregate, math, API or consent
  change. Thirty-one frozen original summaries preserve hashes and nonnumeric fields;
  only the two floating-point oracle fields use machine-precision tolerance. See
  [progress evidence](E6_PROGRESS_REUSE_VERIFICATION.md).
- NFR-ACC-001/NFR-COMP-001/NFR-MNT-001: shared single-select appearance preserves
  native semantics and a visible arrow while correcting WebKit's 23-pixel menus.
  Three-engine 320-pixel touch/keyboard/axe journeys and normal/200%-text targets pass;
  staff controls also pass. See [select evidence](E6_SELECT_TARGET_VERIFICATION.md).

## Verification and retained failures

Latest complete hosted verification passes 1,074 unit/contract, 412 integration,
35 tooling and 108 browser executions (32 ordinary plus four fake short-text journeys
per engine), three UI harness and three native WebKit transport controls, actual
restricted logins, generated contracts, security/images and service smoke. Hosted
logical recovery verifies 68 tables/680 rows in 532 ms; local recovery records 302 ms.
These are synthetic engineering checks, not production PITR/RPO/RTO or academic approval.

The historical 0034 fixture is corrected without dropping JSON rejection, held replay
or two forward upgrades; its 21-case suite passes. The later local full backend run
passes 411/412 with a privileged temporary-role provisioning failure before application
checks. Its unchanged standalone recheck and both complete follow-up hosted suites
pass. Password diagnostics remain withheld; underlying local cause is unconfirmed.
The first broader progress browser run has one Firefox pointer click without a
follow-up request; unchanged rechecks and final local/hosted full matrices pass.
No timeout or permission is broadened. Original macOS/Linux math differs by at most
1.1102230246251565e-16; the portable oracle keeps all input hashes/other fields exact
and uses absolute 1e-15 only for mastery/confidence. No product threshold changes.

A 48-row/five-scope pure Linux probe records medians 29.959 ms before and 5.103 ms
after, 30 samples each; replay calls fall from 24 to eight. This excludes API/SQL and
hosted concurrency. Historical objective ANSWER p95 27.221 ms remains historical;
no current agreed-load or provider latency claim follows from either measurement.

## Running review stack and next boundary

All eight Docker services are healthy on 0041 at http://localhost:3000; existing
volumes are preserved. Capture and receipt creation remain false, and normal learner
short-text scoring remains disabled. Host-native Ollama was down after power recovery;
the pinned `make ollama-serve`, ready-state `make ollama-check` and API-container
connectivity probe now pass. No model download, inference, Gemini or external model/
messaging/cloud application call is made. Use fictional data only.

The next narrow design boundary is completed EXPORT-request evidence retirement at
its existing six-calendar-year deadline. Current immutable DELETE guards, key/receipt
expiry semantics, exact holds and object-purge proof require a separately reviewed ADR
before execution. Pending DELETE/snapshot parents have no invented completion or expiry.
The approved [ADR-060 decision](../decisions/ADR/060-completed-export-accountability-retirement-proposal.md)
now specifies the table allowlist, exact receipt/job holds, restricted maintenance
capability, cleanup prerequisites, finite retries and synthetic test sequence.
Explicit bounded synthetic approval is recorded on 19 October 2026. The additive
preservation foundation and SQL kernel pass full hosted verification; executor operations remain in verification.
Complete main CI [39189901813](https://github.com/Jotham566/kasoma/actions/runs/39189901813)
also passes at the prior documentation closeout `f1bd1ad`.
Full preservation, erasure/anonymization and accountability processing remain incomplete.
Academic inventory/rights/benchmark/calibration, privacy/safeguarding and provider/budget
approvals, production recovery, physical/branded devices and pilot sign-offs remain
[release gates](RELEASE_GATES.md). No approval or completion is inferred from tests.
