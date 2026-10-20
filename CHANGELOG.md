# Changelog

## Dormant lifecycle0045 — isolated verification candidate

FR-ID-006/BR-010/FR-OPS-003 and NFR-SEC-002/MNT-001: additive0045 registers the
private control/plan/job schema and nullable server-owned closure metadata. Flags
are constrained false, owner/executor null and all lifecycle DML/truncation denied.
Direct closure is denied, including migration-role DML; no privileged role, executor,
API, job creation, closure, removal or DELETE completion exists. A forward capability
migration and independent isolated provisioning remain required. Existing DISABLED
identities receive no invented closure date. Plans have bounded clocks; durable jobs
cannot complete, remove rows or carry cursors in this dormant version.

The strict manifest advances to74 tables/545 columns/0045 and erasure-0045-v1, with
explicit lifecycle dispositions. Advisory preview includes case plans/jobs and claimant
staff provenance without changing its non-execution contract. Recovery additionally
checks dormancy and rejects forged activation/closure. No new architectural decision
or retention permission: this stages the already-approved ADR-061 persistence only.

Initial formatting exposed two overlong manifest strings, corrected before checks.
Local98 contracts and17 isolated SQL/identity cases pass, including additive populated
0044 upgrade, repeat upgrade, default state and drift/forgery denials. Broader preview,
recovery, full regression and hosted acceptance remain pending. Earlier mapping-only
notes are historical; these mappings are now registered in the candidate migration.
Normal review Docker remains on verified0044; do not migrate it from this worktree.

## Verified identity coordination and practice viewport

Complete hosted [39337786063](https://github.com/Jotham566/kasoma/actions/runs/39337786063)
is SUCCESS at exact12c6b60d3a76a82c5e10ee15fc51122f4a130fcb:1,444 unit/contract,
517 integration (1600.91s),35 tooling,11 owned identity cases and123 full browser
executions. All required setup/migration/seed, focused, restricted-role, quality,
contracts/build, security, image and service gates pass. Logical recovery verifies
71 tables/691 rows in530ms; actual PostgreSQL/MinIO recovery verifies71/691/one
42,084-byte ciphertext in311ms, stopped source services, fault/immutable guards,
denied stripped retirement and empty cleanup. Production RPO/RTO remains false.

FR-ID-003/005/006 and NFR-SEC-002/MNT-001: accept existing-user LOGIN coordination
and ADR-069's exclusively owned fake identity verification source. NFR-ACC-001/
COMP-001 and FR-REV-005: accept the viewport correction and delayed-hints pointer
regressions. Local source12c also passes123 browser executions with12 independently
absent owned containers. Earlier native integration/cache/attachment failures remain
failed; no unsupported root-cause claim. Main64e1f72 follow-up39339512181 also passes.
Only Markdown closeout follows this verified runtime/test/Make/workflow tree.
No permanent SQL closure, erasure executor or DELETE completion is accepted; those
remain the next bounded ADR-061 slice. Normal review activation stays disabled.

## OTP verification and the user barrier — unverified candidate

FR-ID-003/005/006 and NFR-SEC-002: an existing LOGIN now selects its user lock before
consuming the challenge or taking the identifier lock, matching LINK's user-first
order. The pre-read contains only the lookup selector and grants no authority. A
fresh identifier/user recheck refuses changed bindings or disabled identities; a
concurrently newly bound identifier requires fresh verification instead of taking
a user lock in reverse order. Existing generic errors, OTP single use and attempt
accounting remain. No API/schema, closure marker, activation or completion changes.
Three new executions cover barrier serialization, concurrent identifier binding and
single-use verification for an existing identity. Actual database verification and
full acceptance remain pending; this is a prerequisite within approved ADR-061.

## Practice review viewport stability — candidate

NFR-ACC-001/COMP-001 and FR-REV-005: combined source2966bab reproduces a Firefox
numeric solution click without a solution request, despite a fresh owned database.
A deterministic delayed-hints regression now measures viewport coordinates with the
pointer already placed at the action. Before the correction, Chromium reproduces
a48-pixel shift. The prior document-coordinate regression missed scroll adjustment.
Disable root browser scroll anchoring while the practice page is present; normal manual scrolling
and existing actions remain. Three-engine verification is in progress. No policy,
API/schema, provider, timeout, retry or authorization change.

## Verified configuration, erasure prerequisites and browser foundation

Complete hosted [39334774152](https://github.com/Jotham566/kasoma/actions/runs/39334774152)
is SUCCESS at exact2966bab656cc6520c57264e45acce2366ca40786:1,425 unit/contract,
514 integration (1022.25s),35 tooling and117 full browser executions, plus every
required setup/migration/seed, focused, role, quality/contracts/build, security, image
and service gate. Logical recovery verifies71 tables/691 rows in464ms; actual
database/MinIO recovery verifies71/691/one42,084-byte ciphertext in189ms, stopped
source services, fault/guard checks and empty cleanup. Production RPO/RTO is false.

FR-OPS-002/003 and NFR-SEC-002/OBS-001/ACC-001/LOC-001/MNT-001: accept the bounded
15-key warning configuration, immutable versions/audited retry and accessible editor.
NFR-MNT-001/PERF-001/002/SEC-002/OBS-001: accept the owned browser fixture and bounded
diagnostics. FR-ID-006/BR-010 receive strict internal contracts, private fake-only
profile,71-source structural drift fence and disabled-role prerequisites only.
No account closure, erasure, permanent SQL barrier or DELETE completion exists.

The native full run remains FAILED:513 integration pass and one Alembic upgrade-head
setup error for test_exact_history_hold_preserves_snapshot_without_freezing_new_transitions
(2294.28s). Its captured diagnostic does not establish a cause. The unchanged serial
make test-grading-work recheck passes26 cases in56.16s; no timeout, retry or assertion
changes and no schema/role/cache cleanup. This does not turn the failed native run
into a pass. All514 cases pass in the exact-source clean hosted run above.

Only Markdown closeout follows this verified runtime/test/Make/workflow tree. The
newer identity-coordination and practice-viewport candidates need their own complete
verification. Normal Docker stays healthy on0044 with retirement/short-text disabled.
Full privacy/erasure, academic, provider, physical/branded-device and pilot gates remain.


## Explicit private-profile parser dependency

NFR-MNT-001: declare the already locked python-dotenv1.2.3 dependency directly for
the ADR-061 private-profile parser. `make lock-python` resolves the existing lock
offline; no package versions or artifacts change. `make setup` retains frozen
installation. This grants no erasure activation or new data-processing authority.
Combined-source verification remains pending.


## ADR-061 lifecycle contracts — first slice in progress

FR-ID-006, BR-010, FR-OPS-003, NFR-SEC-002 and NFR-MNT-001: closed internal
plan/authorization/status types reject expanded caller authority, unbounded plan TTLs,
private source/cursor fields and contradictory closure/completion. The private fake-only
profile defaults disabled. A frozen71-source/501-column manifest and read-only catalog
fence detect structural drift without granting execution. Local staff provisioning now
refuses grants/regrants on existing disabled identities while retaining audited revocation.
Final97 focused,1374 unit/contract,35 tooling and two actual integration cases pass
with quality/contracts/build/security/source checks. Full first-slice/hosted acceptance
remains pending. No route, migration, executor, account closure or DELETE completion
is enabled. Verification and the full first vertical slice remain in progress; see
[readiness](docs/implementation/E8_ERASURE_LIFECYCLE_READINESS.md).

## ADR-061 bounded synthetic implementation approved

The human owner explicitly approves the updated ADR-061, including0044 source coverage,
for synthetic-only implementation and isolated tests. Approved choices include eligible
owned-row removal, exact richer encrypted preservation, restricted execution, affected-band
disablement and finite post-completion hold custody. The normal Docker review database,
real data, normal short-text activation and production remain excluded. First implement
closure barriers and resumable jobs; no partial phase may complete a DELETE request.
Engineering implementation/acceptance and external release gates remain outstanding.


## Versioned operational warning configuration - implementation candidate

FR-OPS-002/003, NFR-SEC-002/OBS-001/ACC-001/LOC-001/MNT-001: ADR-067 closes the
missing configuration route for the15 existing numeric warning thresholds only.
Additive0043 records immutable complete versions with a preserved namespace nonce,
atomic existing staff audit and a monotonic current pointer. ADMIN/recent OTP,
strict values, exact version checks and audit-backed retry authority apply. API and
worker warning snapshots resolve the same saved values; unavailable configuration
is explicitly labelled when startup warning defaults apply. Hard processing limits,
consent/retention/provider controls and feature activation are outside this allowlist.

An Operations-linked editor preserves an uncertain command for exact retry and requires
fresh review after conflicts. The first30 contract/SQL/concurrency/authorization checks
pass locally; the expanded34-case suite and dedicated three-engine journey now pass.
Forward0044 tightens single-key/prior-reference SQL guards. Full regression and own hosted
verification remain in progress.
This candidate has no own hosted acceptance and is not ready for main promotion.
See [readiness](docs/implementation/E8_OPERATIONS_CONFIGURATION_READINESS.md).

## Verified temporal diagnostic and history load profile

Complete hosted [39313955470](https://github.com/Jotham566/kasoma/actions/runs/39313955470)
succeeds at exact687d86cdd06bf188f7aa2a725b5e0f19a7e5423b:1,253 unit/contract,
502 integration,35 tooling and114 full browser executions, plus focused tests and
all setup/migration/role/quality/contracts/build/security/image/service gates.
Logical recovery69 tables/686 rows515ms and actual database/MinIO restore69/686/
one42,084-byte object298ms pass with empty cleanup; retirement execution stays denied.

ADR-066's three sequential native objective profiles also pass with7000 successful HTTP
requests/zero errors each: temporal35,000 grades/START p95410.622ms; original2,500/
428.329ms; recent27,500/424.046ms. All report cleanup_failed=false. Recent START
p991074.231ms remains visible. No deadline, threshold, consent or source evidence is
rewritten. These synthetic fixtures establish neither daily/provider failure soak,
production latency/resource attribution nor academic/privacy/release acceptance.
Only Markdown and aggregate evidence follow the verified tooling/test/runtime tree.
NFR-PERF-001/002 and NFR-MNT-001 are addressed within these measured boundaries.


## Provider recovery decision preparation - documentation only

NFR-REL-001/002,SEC-001/002,MNT-001: public primary-source research identifies
35-day PITR tier/default and secondary-region constraints for AWS/Azure/Google.
Budget/approved countries/compatibility/full-stack configuration/owner evidence
remain missing; no vendor, resource, cloud SDK, legal/retention exception or
production gate is selected/closed. Research is independent of live application CI.
[Evidence](docs/implementation/PROVIDER_RECOVERY_DECISION_EVIDENCE.md).


## Older/diagnostic history load - candidate

NFR-PERF-001/002,SCL-001 and FR-DIAG/MST: ADR-066 adds a fixed temporal fixture
profile without changing application/engine behavior or thresholds. Independent
historical clocks and normal OTP build completed diagnostics and old/recent evidence;
current credentials are issued only after preparation. Local quality/contracts/build,1,253 unit/contract,35 tooling,69 focused controls
and203 typed source files pass; dependency/source security checks pass. The first
full-size temporal measurement passes; original/recent rechecks and own hosted
verification remain pending.
[Verification](docs/implementation/E9_TEMPORAL_HISTORY_LOAD_VERIFICATION.md). First native profile PASSES:35000 grades,
7000 HTTP/zero errors,START p95410.622ms,cleanup_failed=false. Original and recent rechecks now both pass: START p95428.329/424.046ms,zero
errors,cleanup_failed=false. Own exactsource687d86c remains live in hosted
39313955470; no complete hosted or production acceptance is inferred.

## Verified database and private-object recovery

Complete hosted [39311093503](https://github.com/Jotham566/kasoma/actions/runs/39311093503)
succeeds at exact source29f1ddc8c57d8bbb2c0dae138c6dcb233972c2f5:1,239 unit/contract,
502 integration,35 tooling and114 full browser executions, plus focused checks and
all setup/migration/role/quality/contracts/build/security/image/service gates.
The separate actual database/MinIO recovery restores69 tables/686 rows and one
42,084-byte encrypted object in241ms, with both source services stopped. Exact
storage scope, missing/corrupt-object rejection, immutable guards and cleanup pass.
The unchanged logical restore separately passes504ms. Retirement execution remains denied.

This accepts ADR-065's isolated synthetic engineering rehearsal under NFR-REL-002,
NFR-SEC-002 and NFR-MNT-001. Production PITR, concurrent backup consistency, regional
copies, escrow and RPO/RTO remain unproved. Only Markdown integration/closeout follows
the verified source; the temporal-load candidate still needs its own complete hosted
acceptance. No ADR-061 approval or production release is inferred.


## Isolated database/private-object recovery - candidate

NFR-REL-002, NFR-SEC-002/MNT-001: ADR-065 adds a separate synthetic rehearsal with
four exclusively owned tmpfs services and no developer-data/volume access. One real
local restore passes69 tables/686 rows/one encrypted object after both source
services stop; missing/corrupt object probes fail closed and cleanup is empty.
Final local checks pass1,239 unit/contract,35 tooling,59 focused controls,
98 recovery-role and105 contract/34 integration preservation cases; quality/build/
contracts/security and real restore pass. Own full hosted verification remains pending; production PITR, regional copies and RPO/RTO remain unproved.
[Verification](docs/implementation/E9_OBJECT_RECOVERY_VERIFICATION.md). Source29f1ddc is pushed for own
full hosted39311093503, confirmed live; keep its remote head unchanged.

## Verified known-export-loss metric windows

Complete hosted [39308594889](https://github.com/Jotham566/kasoma/actions/runs/39308594889)
succeeds at exact source b5557a373f42bf24241f7034d4068b0d1a86da3f:1,180 unit/contract,
502 integration,35 tooling and114 full browser executions, plus focused and all
setup/migration/role/quality/contracts/build/security/image/service gates. Logical
recovery verifies69 tables/686 rows in425ms with cleanup empty and retirement denied.

This accepts ADR-064's finite namespace loss guard under FR-OPS-002 and NFR-OBS-001/
SEC-002/MNT-001. Known export loss cannot recover as measured zero; stored payloads,
scopes and expiry stay unchanged. All server readers must honor the marker; no mixed-
version or production rollout/completeness/billing claim. Only Markdown follows the
verified source. Object-recovery/temporal-load candidates need their own acceptance.
[Verification](docs/implementation/E8_METRIC_LOSS_VERIFICATION.md).


## Historical metric-loss candidate notes (superseded by verified result above)

FR-OPS-002, NFR-OBS-001/SEC-002/MNT-001: two actual SDK/Redis regressions reproduce
fresh zero after a lost nonempty export. ADR-064 extends the existing finite
uncertainty marker to current request/model readers, preserving payloads, scopes,
expiry and provider behavior. Local checks pass: 1,180 unit/contract, 35 tooling, 13 focused loss,
51 request, 43 model, 35 OTP/identity, 24 operations and six browser executions;
quality/contracts/build and security/images/service smoke pass. Own full hosted
acceptance remains pending. No production, billing, complete ledger or mixed-reader acceptance.
[Verification](docs/implementation/E8_METRIC_LOSS_VERIFICATION.md). Source b5557a3 is pushed for own full hosted39308594889, in progress.
OTP parent ceee401 is now fully verified and published on main557f90f;
its merged branch is removed locally/remotely. Metric-loss remote b5557a3 stays unchanged.

Parent OTP source ceee401 remains live and unchanged.


## Verified local OTP adapter observations

Complete hosted [39304052749](https://github.com/Jotham566/kasoma/actions/runs/39304052749)
succeeds at exact source ceee4012c7f74dcc0c387a45ab112ed35d657f1b:1,171 unit/contract,
498 integration,35 tooling and114 full browser executions (102 ordinary,12 synthetic
short-text), plus focused staff/transport/assessment/rubric/restricted-login and all
setup/migration/seed/quality/contracts/build/security/image/service gates. Logical
recovery verifies69 tables/686 rows in892ms, cleanup empty, stripped retirement denied.

This accepts ADR-063's bounded default-disabled synthetic API OTP counters/ADMIN
projection under FR-OPS-002,FR-ID-001,NFR-OBS-001/SEC-002/ACC-001/MNT-001. Adapter return
is not delivery/receipt/billing; no production provider or release approval. Only
Markdown closeout follows ceee401. Separate metric-loss/object-recovery candidates
are not accepted by this run. ADR-061, academic/privacy/provider/physical/pilot gates
remain. Main promotion and owned-branch cleanup require remote/ancestry proof.
[Detailed verification](docs/implementation/E8_OTP_OBSERVATIONS_VERIFICATION.md).


## Local OTP adapter observations - candidate

FR-OPS-002, FR-ID-001 and NFR-OBS-001/SEC-002/ACC-001/MNT-001: ADR-063 adds four
payload-free API adapter counters using the existing finite OTel/Redis pattern.
Default-disabled, development/test only, app-local and ADMIN-only; no delivery/billing,
quota, auth policy, migration or production permission changes. Initial SDK/Redis/API
controls pass; final local and own hosted verification remain pending. Closed alert
schema and offline presentation-harness failures are retained and corrected without
relaxing gates. Final local quality/contracts/build, 1,171 unit/contract, 35 tooling,
35 OTP/identity, 24 operations and 43 model cases, six browser executions and
security/images/service smoke pass. Known export loss stays unavailable across empty
recovery pulses through a finite marker. Own source ceee401 is pushed for complete hosted 39304052749, now in progress;
keep its remote head unchanged for Markdown closeout. Parent engineering is now
published on main87a93d7; this OTP feature remains unaccepted.
[Exact scope and evidence](docs/implementation/E8_OTP_OBSERVATIONS_VERIFICATION.md).

## Verified practice-day display and recovery ownership

Complete hosted [39299684285](https://github.com/Jotham566/kasoma/actions/runs/39299684285) passes at exact combined
source adf432879a8b55eeb1f9e8d59f5d6b053f76bf56: 1,154 unit/contract, 487 integration,
35 tooling and 111 full browser executions, plus focused assessment/transport/staff/
native WebKit controls and all setup/migration/seed/role/quality/contracts/build/
security/image/service gates. Logical recovery verifies 69 tables/686 rows in 493ms,
without cleanup failure; restored retirement execution remains denied.

This accepts the bounded synthetic practice-day indicator (FR-MST-004/005 and roadmap
3.5) and exact owned recovery-role correction (NFR-REL-002/SEC-002/MNT-001). Native
load observations remain pinned to activity source78ca959; no adf4328 load remeasurement
is invented. The earlier run39294126038 remains FAILED at an unexplained WebKit
privacy timeout; current full passes do not establish its cause or a transport fix.
Only Markdown closeout follows the verified application/test/Make tree. External
academic/privacy/provider, full preservation/erasure, production recovery, physical/
branded-device and pilot gates remain. No ADR-061 approval or OTP acceptance is inferred.

## Activity hosted timeout retained; combined verification active

Full source78ca959 run39294126038 passes 1,146 unit/contract,484 integration,35 tooling,
quality/build and 69-table/686-row recovery (548ms), but fails one WebKit privacy
journey at its unchanged 30-second test timeout. Later browser/security/image gates
are not run. Unchanged six-case native privacy diagnosis passes; no cause or fix is
inferred. Combined recovery/activity source adf4328 is pushed for complete hosted
39299684285, which is in progress. Main remains e7a4fc0; neither feature is promoted.
[Exact scope and evidence](docs/implementation/E6_PRACTICE_ACTIVITY_VERIFICATION.md). No timeouts, retries or assertions change.

## Recovery role ownership correction - candidate

NFR-REL-002, NFR-SEC-002 and NFR-MNT-001: [verification](docs/implementation/E9_RECOVERY_ROLE_OWNERSHIP_VERIFICATION.md)
records two actual pre-existing-role failures and the correction to require exclusive
committed source-role creation and exact OID/attribute/membership checks. A restored
destination grants no role cleanup authority. Shared load checks retain their existing
semantics. All 98 focused cases and a 69-table/686-row logical restore pass locally
(295ms, no cleanup failures). Quality/contracts/build, 1,138 unit/contract, 35 tooling and dependency/source security
also pass. Exact combined-source hosted acceptance remains pending.
No migration, production permission, erasure approval or release gate changes.
The practice-day candidate is integrated locally: 98 role, 55 progress and 40
assessment executions pass, plus 1,154 unit/contract, 35 tooling, quality/build/security
and a 69-table/686-row restore (329ms). Shared channel cases overlap; full combined
hosted verification remains pending and the original practice CI head is preserved.


## Official academic source discovery — review pending

FR-CNT-005, FR-DIAG-003 and NFR-MNT-001: the [source review register](docs/implementation/ACADEMIC_SOURCE_REVIEW_REGISTER.md)
records two official NCDC Lower Secondary PDF links, inspected byte hashes/page counts
and visually verified Senior 4 starting locators. Both rights states stay UNKNOWN_BLOCKED;
no source PDF/text/media is committed or imported. Academic currency, exact mappings,
independent item review and expert benchmark evidence remain pending. This is
documentation-only preparation, with no change to release gates or application acceptance.

## Practice-day consistency indicator — candidate

FR-MST-004/005, FR-ID-003, FR-WA-003, NFR-SEC-002/ACC-001/LOC-001/MNT-001:
approved roadmap 3.5 gains a private read-only count of graded-practice days in the
selected subject's seven Kampala calendar dates. ADR-062 records the definition,
additive compatible DTO and neutral accessible meter. Existing evidence/authorization
and unfinished diagnostic sealing remain unchanged; no new table, SQL, replay or
retention permission. Five missing-field baseline failures become 54 initial focused
passes; final 55 focused cases, 1,146 unit/contract, 35 tooling and three progress browser
journeys pass, plus quality/contracts/build, security/images and service smoke.
[Verification](docs/implementation/E6_PRACTICE_ACTIVITY_VERIFICATION.md) tracks expanded/backend/browser/hosted acceptance;
this is not a stored streak system, ADR-061 approval or real-data release. Combined
source 78ca959 also passes both native profiles: START p95 455.214/409.196ms and PROGRESS
p95 14.087/16.522ms, with 7,000 requests, zero errors and owned cleanup per profile.
Hosted 39294126038 is in progress; no runtime promotion or variance explanation is claimed.

## Verified fresh revision response — no empty evidence reads

NFR-PERF-001/002, FR-REV-001/002/005/006, FR-GRD-008, FR-WA-003, NFR-SEC-002
and NFR-MNT-001: the shared start transaction uses its known empty evidence only for
a newly inserted revision. Same-key retries, active resumes and reassessment views
retain current DB reads and full grade/provenance. Three baseline query-budget failures
and the passing answered-resume control become four focused passes with full committed
serialization parity. Expanded 40 integration, 1,130 unit/contract, 35 tooling and nine
three-engine browser cases pass, plus quality/contracts/build and source security.
[Verification](docs/implementation/E9_FRESH_SESSION_RESPONSE_VERIFICATION.md) records both passing native profiles (START p95 408.061/422.913ms),
image/service checks and source-pinned aggregate reports. Complete hosted 39286019222 at 58d598e passes 1,130 unit/contract, 483 integration,
35 tooling and 111 browser executions plus all focused/engineering gates. Recovery
verifies 69 tables/686 rows in 477ms. Only documentation/aggregate closeout follows
that verified runtime/test/Make tree. No claimed p95-variance fix or ADR-061 implementation.

## Proposed synthetic erasure decision — awaiting owner approval

FR-ID-003/005/006, BR-010, FR-GRD-003/004/005, FR-WA-006, FR-OPS-003,
NFR-SEC-002/OBS-001/MNT-001: [ADR-061](docs/decisions/ADR/061-synthetic-account-erasure-proposal.md) and its
[exact disposition manifest](docs/implementation/E8_ERASURE_DISPOSITION_PROPOSAL.md) now propose the full bounded learner
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
decision before learner-review destruction. [Readiness](docs/implementation/E8_ERASURE_TRANSFORM_READINESS.md)
records these factual dependencies without choosing an erasure transform, new anonymous
dataset or changed academic policy. No learner rows are selected or changed. The [complete catalog inventory](docs/implementation/E8_ERASURE_SOURCE_INVENTORY.md) now records all columns/FKs and guard names, independently compared
with live 0042. Readiness also records completed-case hold access, overlapping flag
provenance and unbound OTP ownership gaps. No execution or permission changes.

## Verified bounded disposable load-role lifecycle — 19 October 2026

[Complete hosted 39267916272](https://github.com/Jotham566/kasoma/actions/runs/39267916272)
passes at `a23e9bc020014271e8e697bd2518beda9b3a3393`:1,130 unit/contract,
479 integration,35 tooling and 111 full browser executions, plus9 focused assessment,
12 interception controls,3 staff UI and3 native WebKit controls. Setup/migration/seed,
restricted logins, lint/types/contracts/build, recovery, dependency/source/image security
and container smoke pass. Logical recovery verifies 69 tables/686 rows in561ms, with
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
CI remains in progress. [Evidence](docs/implementation/E9_LOAD_ROLE_CLEANUP_VERIFICATION.md).

## Retained history-load latency failure

NFR-PERF-001/002/NFR-SCL-001: corrected-sourcea23e9bc history load finishes all7,000
requests without errors and cleans its resources, but fails START p95 at559.306ms
against the unchanged500ms gate. Preserve that failed report. The application tree
is unchanged; cause remains unconfirmed. An unchanged diagnostic recheck is running,
with no performance acceptance inferred. [Evidence](docs/implementation/E9_LOAD_ROLE_CLEANUP_VERIFICATION.md).

## Next privacy boundary: account-erasure transform readiness

FR-ID-006/BR-010/FR-OPS-003/NFR-SEC-002/NFR-MNT-001: the
[readiness assessment](docs/implementation/E8_ERASURE_TRANSFORM_READINESS.md) ties the current
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
checks pass. Full revised verification is pending; see [evidence](docs/implementation/E9_LOAD_ROLE_CLEANUP_VERIFICATION.md).

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
See [verification](docs/implementation/E9_LOAD_ROLE_CLEANUP_VERIFICATION.md).

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

## Local verification complete — hosted publication pending

- Source `e33ec69` passes111 local browser executions, nine focused assessment cases,
  quality/build, updated source/image security and Docker smoke. All eight services
  are healthy on0042; retirement stays false.
- GitHub refuses39255125288 before any steps because account payments/spending capacity
  need owner attention. Complete hosted acceptance and main promotion remain pending.
  Preserve both earlier browser failures and the active unmerged branch; no gate bypass.

## Candidate — stable feedback actions during review-hint loading

- NFR-ACC-001/FR-REV-005/FR-GRD-006/NFR-MNT-001: reproduce a 47.421875-pixel
  displacement of Next when delayed post-grade hints load. Move optional review hints
  below feedback actions, preserving grading, weighting, permissions and pointer/keyboard
  journeys. Nine focused three-engine cases pass after the red regression. Add an
  early focused CI gate and payload-free failure diagnostics. Full verification remains
  pending; [evidence](docs/implementation/E3_REVIEW_ACTION_STABILITY_VERIFICATION.md).

## Candidate correction — bounded synthetic interception transport

- FR-WA-001/004/006, NFR-MNT-001 and NFR-SEC-002: retain the hosted 39243195783
  Chromium lost-response failure at source `94b40a6` (`route.fetch` socket reset
  during interception; commit status is unknown). Introduce a loopback-only, idempotency-key-guarded interception
  helper with one ECONNRESET retry and fixed private diagnostics; HTTP failures are
  not retried. Strengthen the channel journey to compare its exact committed code
  and retry key without printing them. Twelve three-engine transport controls,
  three focused channel journeys and the corrected full 108-execution browser matrix
  pass locally at `b6aea35`; hosted 39249423592 passes backend/transport but fails a
  different WebKit resumed-practice transition. See the layout correction above. No application retry or runtime policy changes.

## Candidate — isolated synthetic export retirement operations

- FR-ID-006/FR-OPS-003/BR-010/NFR-SEC-002/NFR-MNT-001: add private least-privilege
  executor provisioning, separate parameter-free maintenance consumer, gated scheduling,
  finite aggregate observations and read-only ADMIN health. Add migration 0042 due index
  and generated optional operations contracts. Review-stack execution remains disabled.
  Tests, runbook and [candidate evidence](docs/implementation/E8_EXPORT_RETIREMENT_OPERATIONS_VERIFICATION.md)
  track verification; no full acceptance or real-data authority is claimed.

## Verified engineering — restricted synthetic export evidence retirement

- FR-ID-006/FR-OPS-003/BR-010/NFR-SEC-002/NFR-MNT-001: implement approved ADR-060's
  parameter-free SQL capability, minimal NOLOGIN owner, independent due/hold guards,
  bounded fair scanning and atomic count-only audit. Default false and isolated
  synthetic scope checks exclude the normal review database and real processing.
  Preserve original UPDATE/grant/worker guards and align review-hold lock order.
- Test through real EXECUTE-only LOGINs, exact holds/races, held-prefix bounds,
  rollback and stripped-owner recovery. Final 31 focused cases, ten existing
  hold cases, three byte-recovery cases and six three-engine privacy journeys pass.
  Lint/types/contracts/security, 1,096 unit/contract, 35 tooling and image scans pass;
  complete hosted 39234377840 passes at `e5d3d98`: 456 integration, 108 browser
  executions and all role/recovery/security/image/service gates. Hosted logical
  recovery verifies 69 tables/686 rows in 713 ms; the interrupted local full run
  is not counted as a pass. No scheduler,
  account erasure or review-stack retirement is enabled.


## Verified engineering — exact export evidence holds

- Record explicit bounded synthetic ADR-060 approval for FR-ID-006/FR-OPS-003/BR-010/
  NFR-SEC-002/NFR-MNT-001. Add migration 0039 stable receipt UUIDs while preserving
  composite retry identity, forward 0040 receipt subject ownership, two gated exact
  hold targets, owner-checked paginated
  references and accessible operator selection. API and SQL independently validate
  ownership/terminal state; active holds use database time. No retirement permission
  or processor exists yet. Ten focused integration cases, including a real restricted
  login, six three-engine privacy journeys, 1,094 unit/contract and 35 tooling cases
  pass. Logical recovery preserves 68 tables/685 synthetic rows and the exact receipt
  hold in 365 ms. Corrected source `be2735e` passes complete hosted 39232307831:
  425 integration, 108 browser executions and all engineering gates.
- Correct the full-suite recovery fixture regression: retain the two-argument byte
  export helper and populate the exact receipt hold through a separate authorized
  helper in the complete drill. All original corruption checks remain. The previous
  full run has 422 passes/three failures; no full acceptance is inferred. Add
  `make test-export-recovery` for the affected byte-integrity cases.

## Verified engineering — profile reverification visibility

- FR-ID-001/005/NFR-ACC-001: show “Verify contact again” only with a loaded profile,
  keeping initial sign-in and logout focused on the contact form. Existing server
  authorization and verification handlers are unchanged. Add signed-out/signed-in/
  logout assertions to the real-API identity journey and `make test-web-identity`.
  The Chromium regression fails before the correction; lint/types/build pass after it.
  All nine corrected three-engine identity executions, 1,092 unit/contract,
  35 tooling, contracts and security pass locally; a public signed-out screenshot
  is recorded. Images build and the corrected Docker web preview is verified with
  all eight services healthy. Complete hosted 39222489376 passes at `44ae9ad`:
  415 integration, 108 browser executions and full recovery/role/security/image/
  service checks.
  No architectural change.

## Verified engineering — stalled fake grading isolation

- Add three FR-GRD-003/004/005 and FR-MST-001/004/005 regressions: 50 scheduled owned
  web reads finish while a fake model call is held; timeout/failure/fallback then
  produces exactly one neutral outcome with no grade/mastery/publication evidence.
  Add `make test-provider-fault-isolation`. Corrected focused tests, 1,092 unit/contract,
  35 tooling, lint/types/contracts and security pass. Complete hosted 39220793602
  passes at `8a938dd`: 415 integration, 108 browser executions and full
  recovery/role/security/image/service checks. No runtime, architecture or learner
  enablement changes; no full provider-load or availability acceptance claim.

## Verified engineering — synthetic history and numeric load

- Extend the isolated objective harness for NFR-PERF-001/002/NFR-SCL-001 with
  50 prior answers per active learner, varied evidence trajectories, Mathematics/
  Physics plans and numeric answers. Add `make load-history-mixed` and per-format
  latency gates without changing runtime limits or empty-history baseline behavior.
  All 37 harness cases, 1,092 unit/contract, lint/types/contracts and security pass;
  initial history setup fails safely and is corrected to normal refresh rotation.
  Final native full-size profile passes at `6b06c53`: 7,000 HTTP requests, zero errors,
  1,250 answers per format, 27,500 total grades and successful cleanup. START p95 is
  432.085 ms, numeric-answer p95 27.778 ms and progress p95 17.079 ms. Complete hosted
  39217860618 passes at that source: 1,092 unit/contract, 412 integration, 35 tooling,
  108 browser executions and full role/recovery/security/image/service checks.
  The original-baseline recheck also passes:
  7,000 requests, zero errors, START p95 421.751 ms and successful cleanup. Retain
  startup p99 above one second as a risk. No production or academic claim.
- Make format coverage independent of random item UUID order: the final fixture
  pool has 144 Mathematics choice and 144 Physics numeric items. The earlier
  293-item candidate completes with zero HTTP errors and successful cleanup but
  correctly fails because all timed answers are choice; its failed report is retained
  separately from the passing final-source evidence.
- Document the new command and sequential isolated execution in the local runbook
  and testing specification; preserve all broader performance/release gates.
- Publish through main `6ebdf71` and remove the merged load branch locally/remotely.
  Independent provider-isolation and UI candidates await their own hosted results.

## Proposed — completed export accountability retirement

- Prepare ADR-060 for FR-ID-006/FR-OPS-003/BR-010/NFR-SEC-002/NFR-MNT-001:
  exact eligible tables, six-year deadline, independent holds, object-cleanup
  prerequisites, restricted SQL execution, finite receipt retry semantics and
  synthetic acceptance gates. Human approval is pending; no runtime, migration,
  permission or deletion behavior changes. ADR-057 approval remains separate.
- Confirm complete main CI 39189901813 succeeds at `f1bd1ad`; all eight review
  services remain healthy. This increment supplies documentation readiness only.

## Verified — shared native select touch targets

- Extend the proven WebKit menu styling to shared single-select inputs, preserving
  native semantics and a visible arrow. NFR-ACC-001/NFR-COMP-001 tests reproduce a
  23-pixel practice menu before the correction. All three touch journeys and three
  staff UI harness cases pass with 320-pixel reflow and normal/200%-text targets;
  complete hosted 39185423895 passes at `6d53541`, including all 1,074 unit/contract,
  412 integration, 35 tooling and 108 browser executions, security/recovery/images
  and service smoke. The verified sources are on main and merged branches are removed.
  No API or permission change.

## Verified engineering — request-local progress replay reuse

- Reuse immutable skill estimates only within one progress read under ADR-024
  (FR-MST-004/005, NFR-PERF-001). Exact legacy summary/hash/change outputs remain
  unchanged; authorization, consent, evidence filtering and calculation time remain
  per request. No shared cache, migration, algorithm or API change.
- Add frozen legacy output and replay-work/isolation regressions; all 1,074 unit/contract
  cases pass. Complete hosted 39184552472 passes at `7148a1c`, including all 412
  integration and full browser/security/recovery/image/service gates. It is merged
  to main with the verified shared-selector follow-up.

## Verified — bounded synthetic channel capture

- Add additive 0038 source/capture, finite disposal, generated contracts, advisory
  inventory and operator controls under ADR-057. Expanded 34 focused integration (including
  both actual restricted logins), 105 contract/format and 108 browser executions pass;
  complete hosted 39183714273 verifies source `0a8f674` with all 1,055 unit/contract,
  412 integration, 35 tooling and full security/recovery/image/service gates. Source
  is on main and its merged branch is removed. Creation stays disabled.
- Reproduce and correct the existing advancing-clock conversation expiry mismatch
  using one timestamp per exact 24-hour pair; both regression cases and the real-time
  conversation/capture browser journey pass. No database invariant is relaxed.
- Give each request hold region a distinct accessible name and enforce 44-pixel
  capture dropdown targets, including WebKit and 200% text. No accessibility exclusion
  or test timeout is added.

## Verified format — approved synthetic channel preservation

- Record the user's explicit bounded ADR-057 implementation approval. Real-data
  processing, account erasure and production privacy/release gates remain separate.
- Add a private, bounded, strict link/conversation evidence format with purpose- and
  snapshot-bound authenticated encryption, UTC canonicalization and closed diagnostics.
  No runtime capture, storage, endpoint, permission or retention change is enabled.
- Add 82 offline format/tampering/allowlist/binding cases and the prescribed
  `make test-channel-preservation-format` command. That first increment did not
  supply capture acceptance; bounded capture is verified in the later entry above.
- Source `25b44b1` passes complete hosted [39176205670](https://github.com/Jotham566/kasoma/actions/runs/39176205670),
  all 1,022 unit/contract, 378 integration and 35 tooling cases, full browser/security/
  recovery/image/service gates. This is format acceptance only; capture is separate.
- Capture development exposes a real advancing-clock conversation expiry mismatch;
  the correction and new real-time coverage are now verified in `0a8f674`.

## Accepted engineering checkpoint — 19 October 2026

- Source 5d95f9d passes complete hosted [39171302022](https://github.com/Jotham566/kasoma/actions/runs/39171302022)
  and is on main with a documentation-only closeout. Merged branches are removed.
- Accept ADR-056/058/059 within their bounded engineering scope: wall-clock hold
  guards, aggregate ADMIN audit activity and disposable hosted storage safeguards.
  All 940 unit/contract, 378 integration, 35 tooling and full browser/security/restore/
  image/service checks pass. Historical failed/cancelled runs remain recorded below.
- Keep receipt creation and normal learner short-text delivery disabled. ADR-057
  remains an owner-review proposal; full preservation, erasure and real release gates
  remain incomplete. This acceptance supersedes older pending engineering status.

## Verified — disposable CI storage and navigation regression

- Preserve the failed hold-clock hosted run as failed disk-capacity evidence. Add
  ADR-059 hosted-only fixed SDK preparation, initial/phase capacity gates and read-only
  diagnostics; no local cleanup or reduction in application checks.
- Replace the obsolete absent-Audit navigation guard with its implemented exact target.
  All 105 browser executions, 22 storage safety and 940 unit/contract cases
  pass locally; corrected full-source hosted acceptance remains required.

## Verified — bounded ADMIN audit activity

- Implement the approved audit endpoint and navigation as fixed-category last-24-hour
  activity sampling under ADR-058, with live ADMIN checks, bounded reads and honest
  sample-cap reporting. No individual audit fields or extra support permission.
- Add an audit time-window index, strict generated contracts, real API/window/upgrade
  tests and accessible staff UI/browser coverage. Full local verification passes 918
  unit/contract, 35 tooling and 378 integration cases, restricted login, recovery,
  security and rebuilt Docker/browser smoke; complete hosted acceptance remains pending.

## Documentation — recovery and preservation review

- Record a nondestructive eight-service restart after a power interruption, preserving
  volumes and existing environment configuration, with fake-only smoke verification.
- Prepare ADR-057 for explicit owner review of bounded minimized link/conversation
  snapshots. No runtime behavior, new data retention or erasure authority is introduced.

## Verified — legacy hold DELETE clock

- Reproduce transaction-start time missing a later committed hold in all four legacy
  DELETE wrappers, using temporary probe rows while original evidence stays protected.
- Add forward migration 0036 to use database wall clock only in those wrappers, preserving the
  explicit historical predicate, source data, permissions, finite scope and independent
  immutable guards. Local verification passes 57 related integration cases, 918
  unit/contract and 35 tooling cases, restricted logins, populated recovery, security
  and rebuilt 0036 Docker smoke. Complete hosted acceptance remains pending.

## Verified — terminal channel receipt holds

- Preserve applied 0034 and add forward migration 0035 after a final real-menu regression catches
  PostgreSQL json equality failure on held no-op updates. Canonical JSONB comparison
  preserves menu order/core protection; clean and existing-hold upgrade/replay pass.
- Final 21-case receipt/clock/race/restricted-login verification passes alongside 918
  unit/contract,364 broad integration and 102 full browser executions. New creation
  remains disabled; the 0035 stack passes smoke/security/health with creation disabled. Complete hosted
  run 39165896953 passes at 397f562; it is on main and its merged branch is removed.

- Assess exact-record holds for already-minimized owned terminal inbound/outbound
  receipts under proposed ADR-055. Preserve normal callbacks, STOP/unlink and bounded
  unrelated cleanup, with database-clock guards and default-disabled staged creation.
  Live messages, links, conversations and usable code preservation remain unsupported.
  Add0034 guards, hold capabilities/UI, hold-aware cleanup and clean/upgrade/race/
  opt-out regressions. Initial 16-case receipt verification, existing holds/channels and
  restricted login/65-table/648-row recovery pass; final acceptance is in progress.

## Verified — bounded local model observations

- Add six private, attribute-free worker counters and bounded five-minute Redis
  aggregation under proposed ADR-054. Observe actual provider-port attempts after
  authorization; omitted usage stays unknown, explicit reported zero stays zero.
- Extend the ADMIN snapshot/dashboard with local attempt counts, known token
  subtotals, unavailable totals and a typed volume warning. No billing, fleet ledger,
  grading accuracy or quota enforcement claim. Only the ordinary development/test
  worker publishes freshness; fixed fake probes verify the running stack.
- Preserve the existing request histogram wire format while sharing its finite byte
  transport. Add SDK, real Redis, role/lifecycle, alert and accessible presentation
  regressions. Complete hosted run 39160113771 passes at `0c73c45`; the source is on main
  and its merged branch is removed. Learner scoring remains disabled.


## Verified — configurable per-job grading budgets

- Expose the existing shared request/token/deadline ceilings through typed server
  settings while preserving defaults and hard maxima of three requests, 16,384 tokens
  and five seconds. Both independent passes and the optional repair share one snapshot.
  The pre-dispatch deadline uses the same configured timeout.
- Verify stricter request, token and deadline exhaustion preserves the encrypted saved
  attempt, neutral no-score/no-mastery outcome and idempotent replay. No new quota
  policy, inference profile, approval, API, provider or persistence changes. Local
  verification passes 891 unit/contract, 21 flow and 33 review cases, restricted login,
  security, populated recovery and rebuilt image/service smoke; hosted acceptance
  passes at `f5f408e` in hosted run 39157127637. The source is on main and its merged
  branch is removed locally/remotely.

## Verified — grading queue operations

- Hosted run 39155326659 passes for `a357222`; promote to main and remove the merged
  grading-operations branch locally/remotely.
- Promote verified independent review, responsive navigation and offline report comparison
  through `17abb2d` to main after hosted runs 39150319607/39151730479 pass; remove all
  three merged source branches. Keep the current unmerged operations work separate.
- Fix host/VM completion-clock skew by capping at database time while retaining SQL
  guards. A rollback-only reproduction changes from nine failures in ten to ten successes.
  Await each diagnostic POST acknowledgement before checking its exact saved attempt.

- Propose ADR-053 and extend the existing ADMIN snapshot/dashboard with bounded
  grading queue/lease age, terminal outcomes, pending audits and post-activation
  disablement counts. Add a typed local stale-queue threshold and alert.
- Label GRADING_FAILED outcomes processing fallbacks because they include expected
  provider refusals and budget/validation outcomes. Do not infer academic error rate,
  model cost or an incident from those counts; existing unavailable metrics stay honest.
  Local verification passes 884 unit/contract and 333 broad integration cases, supplemented
  by 33 review/26 operational cases, restricted login, 104 browser executions, populated
  recovery and rebuilt image/security/smoke checks. Hosted acceptance remains pending.
  No grading policy, provider, persistence or retention changes.

## Work in progress — offline evaluation reports

- Propose ADR-052 and implement a strict payload-free synthetic short-text report
  contract and the required read-only `make eval-compare` command. Compare only matching
  frozen benchmark/schema/metric-policy references, include all planned cases in quality
  denominators and preserve unavailable usage. Reject ambiguous, oversized or private
  input and return closed errors. No inference, model/provider selection, approval or
  learner scoring is performed. Thirty-seven new cases, 881 total unit/contract and
  35 tooling cases, actual Make invocation, lint/contracts/security pass; hosted
  acceptance and actual benchmark/provider/evaluation gates remain open.

## Work in progress — staff mobile navigation

- Replace the always-expanded narrow-screen staff links with an explicit accessible
  workspace menu; retain visible desktop navigation and the current destination.
  Close the menu on navigation, keep sign-in touch-accessible and preserve the
  synthetic-data notice. No route permissions or learner workflows change.
- Verify keyboard disclosure, active links, navigation reset, 320-pixel reflow and
  reviewer-form state across browser engines before acceptance. Fix real 200% text
  overflow in the review grid using scoped wrapping and zero-minimum grid sizing;
  preserve content rather than clipping it. Record shared Playwright artifact collisions
  and require sequential native browser commands. Final serial acceptance passes 104
  browser executions, lint/build/contracts and rebuilt-image/service/security checks;
  exact-source hosted verification remains pending.

## Work in progress — independent grading review

- Implement ADR-051 candidate migration 0033, blinded academic-review API and responsive
  staff workspace. Validate every pinned criterion, calculate exact agreement in SQL,
  retain immutable completions and disable affected bands atomically on critical error
  or rolling agreement below 90%. Existing grades and mastery are never overridden.
- Preserve global publication ordinals and add versioned session/band sampling so
  permanently sealed diagnostic grades cannot consume released revision coverage.
- Add minimized owned exports, diagnostic sealing, exact review holds, deletion-impact
  inventory, correlated read/completion audit, restricted-login and populated recovery
  coverage. Recheck current consent, role and audit state at confidential access and
  each model pass/publication. Normal short-text scoring remains disabled.
- Verify the new accessible desktop/mobile journey across Chromium, Firefox and WebKit,
  including bounded pagination, explicit rubric inputs and exact retry after a lost
  acknowledgement. Thirty-two focused review cases, 844 unit/contract cases, restricted
  login, repeat populated recovery, 324 broad integration cases and rebuilt container
  checks pass. Exact-source hosted verification remains pending;
  see the expert-review verification register. No real academic approval is implied.

## Work in progress — short-text learner integration

- Promote disabled synthetic learner flow `853f80a` to main after complete hosted run
  39143803289 passes, including current container scans. Remove its merged branch.
  Restore the local review stack after a power interruption without resetting volumes.
  Actual learner scoring and the independent expert-review slice remain gated.

- Verify nine synthetic short-text browser journeys across Chromium, Firefox and
  WebKit, including mobile neutral fallback, review requests and sealed diagnostics.
  Fix the textarea accessible label and distinct report/hint React keys. Add duplicate
  worker, publication crash, revoked-report, broker failure and SQL atomicity coverage;
  extend isolated logical recovery with encrypted rubric evidence. Full regression and
  independent expert-review integration remain pending; normal scoring stays disabled.

- Route durable short-text work through the specified separate grading queue and
  retain periodic recovery after wake-up failure. Bound owned feedback reads and
  automatic client polling. Add a documented Trivy database-source override while
  preserving scanner version, freshness checks and HIGH/CRITICAL failure thresholds.

- Build the candidate encrypted submission/receipt/work flow, owned pending/fallback
  outcomes, finite-lease fake processor, atomic rubric grade/mastery/audit publication,
  schema/client changes, draft learner polling UI and diagnostic sealing coordination.
  Runtime enablement defaults false; genuine report/safety authorities remain unavailable.
  Ten intermediate PostgreSQL/API cases and 828 unit/contract plus 35 tooling cases pass;
  the full feature, audit review, browser, role and recovery gates remain under implementation.


- Begin the cohesive learner short-text flow with strict pinned rubric-result and
  partial-credit projection contracts. Revalidate exact answer evidence and reviewed
  feedback; reject inconsistent scores and hidden/unsupported fields. All 808
  unit/contract and 35 tooling cases pass with lint/types and unchanged HTTP contracts.
  Persistence, worker, ownership, polling/fallback and expert audit integration remain open.


- Add the publication/audit assignment ledger with band-locked ordinals, atomic sampling,
  immutable records, owned minimized exports, deletion inventory and exact-record holds.
  Generated contracts and staff hold controls include both types. Verification passes 12 focused SQL cases, 19 existing hold cases, restricted login,
  populated recovery, six browser executions, lint/types/contracts and rebuilt image
  scans. Full regression passes 780 unit/contract, 35 tooling and 291 integration cases;
  dependency security retry passes. Hosted publication acceptance remains required.
  Learner scoring, expert review and automatic disablement remain pending.

- Add immutable calibration-band metadata and exact transition history, disabled
  registration, locked snapshots and sticky disablement. Verify worker permissions
  allow disablement without approval/activation rights and extend populated recovery.
  No activation command or learner scoring is enabled. Full backend regression passes
  279 integration cases; a later reproduced topic-reparenting gap is closed with
  migration 0029's composite scope FK. Thirteen focused SQL cases, populated upgrade,
  restricted-login and recovery checks pass after that correction; hosted acceptance remains required.

- Add a versioned calibration/audit eligibility component with exact threshold counts,
  scope/version/length binding, approval-reference requirements, audit coverage and
  sticky-disablement checks. Propose a bounded rolling window and prefix-complete 10%
  audit selection under ADR-050; academic approval and durable/runtime integration remain
  required. No band or learner scoring is enabled by this component.
  Verification passes 780 unit/contract and 35 tooling tests, lint/types, generated
  contracts, source-secret and dependency/security checks.

- Define one-claim grading transitions with bounded queue/lease expiry and exact
  terminal replay. Interrupted claims fall back without resetting model-call budgets;
  late workers cannot publish. Durable persistence/worker wiring remains pending.

- Add a bounded authenticated answer envelope using the existing encryption interface,
  binding learner/attempt/assignment/item/rubric IDs and preserving exact answer text.
  Ciphertext replay, malformed data and provider diagnostics fail closed. Persistence
  and learner delivery remain disabled pending coordinated integration. All 730
  unit/contract and 35 tooling cases pass, with lint/types, contracts and secret scans.

- Reconcile readiness against existing assessment/mastery contracts and the mandatory
  beta expert-audit and automatic band-disablement rules. Scoring and learner selection
  remain disabled; this assessment provides no academic acceptance.

## Work in progress — hosted verification recovery

- Reproduce WebKit attachment timeouts in a network-isolated Linux control. Explicit
  HTML download intent passes complete/stalled/corrupt native transfers. Apply that
  intent to the background-export link; application error/retry acceptance is pending.
  Add bounded recent-owner status preflight and closed in-page errors after the
  attribute-only change failed signed-out notice regression; download authorization
  remains independent. Test unavailable status, no download and frozen recovery.
  Verification passes 90 native browser executions, three Linux transport controls,
  six final privacy executions, lint/types, contracts, source scanning and rebuilt
  container scans/smoke. Exact-head hosted acceptance remains required.

- Record the hosted Linux WebKit attachment failures after successful service/backend
  and Chromium/Firefox checks. Add a complete native-download loopback control with
  filename and exact-byte assertions; preserve mandatory application acceptance.

- Record continued PostgreSQL throttling after successful mirror configuration. Add
  optional, step-scoped Docker Hub authentication with a pinned official login action;
  preserve anonymous fork verification and automatic logout. Credentials remain external.

- Address the subsequent PostgreSQL pull throttle with a public Docker Hub cache
  configured only on disposable CI runners. Preserve daemon settings, validate before
  bounded restart, and test configuration merging and local-execution refusal.

- Address the observed 40-minute hosted timeout with a bounded 90-minute job and
  lock-keyed browser cache. Use the byte-identical official Mailpit mirror only in CI
  after Docker Hub throttled the runner. Every application/security check remains required.

## Work in progress — request aggregation

- Complete local acceptance: 259 integration cases, 666 unit/contract cases, 32 tooling
  checks, 90 browser executions, generated contracts, security scans/audits and both
  live container probes pass. Final-head hosted verification remains pending.

- Build/scan and refresh the local eight-service stack. Verify scheduled exports and
  real API-to-Redis metrics publication; add the bounded metrics probe to container smoke.
  Full backend/hosted acceptance remains pending.

- Verify all 90 native browser executions after strengthening consent/error selectors;
  operations display-state, mobile and accessibility checks pass. Full backend and
  container acceptance remain in progress.

- Trace and correct a browser-test consent race: the success substring also matched
  the paused-consent sentence. Anchor all 14 success assertions, preserving the actual
  consent gate. Scope export errors to main content to exclude Next's route announcer;
  retain synthetic browser traces only on failure.

- Wire API collection, minimized ADMIN snapshots, conservative sample-gated latency
  alerts and histogram-range presentation. Add typed thresholds, generated contracts
  and the alert event schema. Runtime/API/browser verification is in progress.

- Add bounded Redis interval retention and retry deduplication, corruption/freshness
  handling, and an owned background SDK collector with finite I/O/shutdown. Add
  local Redis and fake-store lifecycle tests; API/dashboard integration remains pending.

- Start an isolated, attribute-free OpenTelemetry histogram component with disabled
  exemplars, explicit resource metadata and honest percentile intervals. Add SDK and
  property tests and ADR-049 proposal. API wiring, Redis retention and dashboard
  integration remain pending; no runtime behavior changes yet.

- Add bounded canonical interval projection and fail-closed SDK/storage validation.
  Format/lint/types, 650 unit/contract cases, 32 tooling checks, OpenAPI comparison
  and source secret scanning pass. Runtime integration remains unverified.

## Work in progress — learner UI foundation

- Increase shared learner/staff navigation targets to 48px; retain the 44px acceptance minimum across browser bounding-box rounding. All 90 native browser executions pass.

- Correct the native macOS WebKit keyboard test to use Option-Tab for links, preserving skip-link/main-content focus assertions and ordinary Tab on other engines/platforms. All 30 native WebKit application cases pass after the correction.

- Style the content queue/editor and rubric/numeric fields consistently while retaining exact draft and independent-review semantics. Lint/types/build, mobile/axe/exact-save-reload and all 30 Chromium journeys pass; desktop/mobile captures reviewed.

- Apply shared presentation to operations, flags and synthetic imports; preserve unavailable metrics and explicit audited review controls. Lint/types/build and 30 Chromium cases pass; authenticated mobile/desktop captures reviewed.

- Add consistent staff workspace navigation for existing routes with active state, narrow-screen touch controls and unchanged server authorization. Lint/types/build, 30 Chromium journeys and the isolated editor check pass; desktop/mobile captures reviewed.

- Restyle privacy requests and WhatsApp linking for mobile, preserving explicit consent/re-authentication and retry controls; display link-code expiry explicitly in Kampala time. Lint/types/build and all 30 Chromium cases pass; mobile captures reviewed.

- Restyle confidence-aware progress and session history with responsive cards, explicit empty/auth recovery actions and consistent touch controls. Preserve server-derived estimates, diagnostic sealing and pagination; lint/types/build and 30 Chromium cases pass, with desktop/mobile screenshot review.

- Verify practice/diagnostic presentation with 30 Chromium cases and desktop/mobile screenshot review; verify the web dependency layer is cached after a source edit. Native MinIO and private storage initialization now work; all 59 storage checks pass, with full regression running.

- Separate web dependency installation from application source in the Docker build so UI-only changes can reuse the frozen dependency layer (NFR-MNT-001).

- Restyle practice/diagnostic questions and selected answers; share an accessible saved-answer progress indicator driven by server counts. Preserve scoring, hints, sealing and retry behavior; verification is in progress.

- Verify onboarding presentation and consent-gated diagnostic links in the 30-case Chromium suite; inspect desktop/mobile screenshots and refresh the running web container. Seed synthetic local learning fixtures while recording the still-unavailable storage initializer.

- Restyle onboarding fields/cards/actions, correct obsolete learning-availability copy and offer a diagnostic next step only when the server grants learning access. Guardian/consent/session semantics remain unchanged.

- Verify 30 full-Chromium cases with the new UI, 320/1280-pixel screenshot review, 200% text reflow, keyboard/axe checks and 175,609-byte cold question transfer. Web image rebuilt; remaining browser/pilot acceptance stays open.

- Introduce shared learner navigation, a keyboard skip link and a responsive home/recommendation presentation using existing authorized data. Preserve synthetic notices, consent and retry semantics; verification is in progress.

## Work in progress — asynchronous owned export lifecycle

- Verify Firefox corruption through the same pinned browser's ordinary download manager, with real privacy-page actions, native failure, closed reader, unchanged READY state and exact frozen retry. The case remains mandatory; all 90 native browser executions pass; final-head hosted acceptance remains pending.

- Enforce the five-second object-read deadline in the delivery service as well as the adapter. A stalled-adapter regression and all 42 focused export cases pass; Firefox cancellation, bounded cleanup and frozen retry now pass. Corruption acceptance remains open.

- Add a disposable-profile native Firefox download-manager diagnostic and bounded/redacted protocol checks; ordinary HTTP/1.1 corruption is rejected, while raw-server cancellation confirms delayed disconnects.

- Add standalone loopback attachment controls to distinguish browser automation failures from application transport. Chromium passes; Firefox reproduces both failures without Kasoma. No acceptance waiver.

- Add serial native export diagnostics with named failure/closure steps and retained local traces. Firefox cancellation/corruption failures reproduce; acceptance and main promotion remain gated.

- Document channel-preservation dependencies: terminal field clearing, STOP/unlink, relinking ownership and bounded expiry must remain compatible with any future hold mechanism. No retention or hold behavior changes.

- Pass updated-database HIGH/CRITICAL scans for both local API and web images after the bounded download-timeout adjustment.

- Audit export acceptance against concrete security, cleanup, large-history and interruption assertions; retain explicit browser/container/hosted promotion gates.

- Allow a finite configurable 30-minute container scan timeout after the default five-minute vulnerability database download timed out. Keep current database updates and HIGH/CRITICAL failure gates unchanged.

- Complete the native 245-case integration regression with real MinIO, dependency/security checks, populated logical recovery and isolated content-admin UI verification. Correct obsolete candidate registration comments; remaining browser/container/hosted gates still block promotion.

- Verify a complete owned export through the actual Docker scheduler, export worker, private MinIO and web gateway. Add the bounded fictional-account probe to container smoke; preserve running review services and hide private diagnostics.

- Record the next learner UI slice and its accessibility, responsive-layout, privacy and cold-transfer acceptance gates from the actual screens; implementation and visual acceptance remain pending.

- Verify both full pinned Chromium shards: 28 tests pass, including native export failure/cancellation/frozen retry, privacy review and operations metrics. Secret scanning and generated contracts pass; Firefox/WebKit/storage/container acceptance remains open.

- Scope administrator privacy-review browser assertions to the learner's exact request references so concurrent exports cannot make the test ambiguous. Native Chromium export cancellation/corruption journeys pass; full matrix verification continues.

- Add a documented full-Chromium headless test command using the pinned installed browser; retain the normal three-engine CI matrix and all assertions (NFR-COMP-001, NFR-MNT-001).

- Add isolated fake-store corruption/cancellation fixtures and frozen-retry acceptance journeys (FR-ID-006). Reject fixture installation outside random E2E schemas; native browser execution remains pending.

- Tighten the registered export gateway regression to require exact unauthenticated denial; 15 worker checks and three real gateway HTTP cases pass, along with lint, formatting and types.

- Target each Compose worker health probe to its own explicit node and require its pong, preventing another healthy consumer from masking failure (FR-OPS-002, NFR-MNT-001).
- Record the latest full regression: 594 unit/contract, 32 tooling and 243 integration passes; two unavailable-MinIO failures remain open. Candidate wiring is local and unaccepted. Earlier disabled-stage entries below are historical.

- Wire candidate owner routes, generated client, background prepare/status/retry/save controls, dedicated native/Compose worker and scheduler for local synthetic acceptance. Full promotion and browser/storage gates remain open.

- Add the dedicated `make worker-exports` launch policy and restrict ordinary workers to operations/imports/messaging. Verify the actual launch flags through synthetic hard-stop, process replacement and queue-isolation tests; automatic export scheduling remains disabled.

- Add capped export queue/failure/age metrics and configurable local warnings to the ADMIN operations view, with generated contracts and threshold/lifecycle tests (FR-OPS-002).

- Return failed attachment navigations to a fixed privacy-page alert using only closed error codes; preserve JSON errors for programmatic requests and abort incomplete transfers. Add actual Next/API HTTP checks.

- Verify a diagnostic completed during asynchronous generation cannot unseal an earlier snapshot; a later explicit request includes released grades. All 41 focused export integration cases pass.

- Populate the isolated logical recovery drill with a published synthetic export and verify restored guards, encrypted manifest and frozen bytes (FR-ID-006, NFR-REL-002). Object-storage recovery remains a separate gate.
- Connect the web gateway to exact-length streamed attachments with separate initial/transfer deadlines, closed errors and disconnect cancellation; 31 tooling cases pass. API registration and learner controls remain pending.

- Set local PostgreSQL shared memory to 512 MiB after the 64 MiB Docker default caused a full-regression outage (NFR-MNT-001). Preserve the existing volume and SQL timeouts; serial regression passes 238 integration cases with zero setup errors, while two unavailable-MinIO failures remain.

- Verify real CLI hard-stop/replacement and durable lease recovery with isolated synthetic fixtures. Use importable shared tasks and child initialization for the M4 macOS spawn path; preserve native process safety and ordinary worker limits.

- Add cancellable signed local object reads with total deadlines, shared chunk integrity checks and async attachment closure tests (FR-ID-006, NFR-SEC-001/002). Real loopback dribbling TCP cancellation passes.
- Test isolated owner queue/status/attachment routes, frozen retry, expiry and old synchronous `EXPORT_FILE_REQUIRED` compatibility. Define separate export tasks with hard-limit envelopes and minimized correlation logging; application activation remains gated.
- Include owned job/copy counts in advisory deletion inventory without exposing grants or enabling deletion.

- Prepare an exact-length attachment response with cancellation/closure tests; add consent-withdrawn privacy access, recent-auth expiry, transfer deadline and real Redis TTL tests. All routes remain disabled pending complete lifecycle acceptance.
- Add bounded database-scoped cleanup progress with a one-hour Redis TTL, safe restart on lost/malformed state and closed failure counts (FR-ID-006, FR-OPS-002, NFR-SEC-002). Thirteen deterministic cursor cases pass; scheduler/transport acceptance remains pending.

- Resolve the ADR-048 implementation contract and begin additive job/generation constraints and closed status types for FR-ID-006. No route or worker is enabled; the lifecycle remains unaccepted until the consuming implementation and acceptance tests pass.

## 9 October 2026 — verified private MinIO export adapter

- Reuse the approved local storage boundary for exact UUID-keyed encrypted chunks (FR-ID-006, NFR-SEC-001/002, NFR-MNT-001). Bound reads before allocation; verify lengths and always release responses.
- Add 24 fake-provider cases, an owned synthetic MinIO round trip/private-access test and `make test-export-storage`. Native MinIO remains unavailable; hosted CI 37962081120 passed 721 Python and 66 browser cases plus full recovery/security/container gates. Promoted `bb2f4eb` to main and removed its completed branch.
- Record ADR-048 as an unaccepted lifecycle proposal. No learner route, worker publication, new retention rule or cleanup policy is enabled.
- Record successful promotion of encoder `a485bb6` (657 Python/66 browser cases, CI 37949902270) and artifact format `8c08890` (696 Python/66 browser cases, CI 37950849215), with full recovery/security/container gates and branch cleanup.

## 9 October 2026 — verified private export artifact boundary

- Add ADR-047 and an internal authenticated chunk/manifest format for FR-ID-006 and NFR-SEC-001/002/MNT-001. Bind request, generation and ordinal; verify per-chunk and whole-file integrity before the final bytes.
- Bound plaintext chunks, ciphertext, total size and manifests; sanitize callback/cipher errors and close cancelled sources. Add fake-storage corruption, boundary, cancellation and projection round-trip tests.
- No learner route, worker publication, new provider or retention change. Existing synchronous caps remain unchanged; the artifact lifecycle is still pending.

## 9 October 2026 — verified incremental bounded export encoding

- Enforce the existing 2 MiB complete-envelope cap during allowlisted projection (FR-ID-006, NFR-SEC-001/002, NFR-MNT-001), stopping reads before an oversized history is fully hydrated.
- Bound collected encoding chunks to 16 KiB; retain exact row accounting, diagnostic sealing, atomic completion, encrypted retry compatibility and existing expiry. JSON member order may differ in new stored artifacts; v1 values/schema and old retry bytes remain unchanged.
- Add codec, exact-cap, cancellation, early-hydration and legacy retry tests. No new ADR, API, migration, provider or asynchronous large-history delivery. Acceptance is recorded in the export encoding report.

## 9 October 2026 — verified objective HTTP load baseline

- Add a local-only temporary-database profile for NFR-PERF-001/002 and NFR-SCL-001: 2,000 synthetic registrations, 500 active learners, 50 concurrent journeys, 288 original fixtures and paced objective answers.
- Report real HTTP percentiles, errors, completion, pacing and scoped resource evidence; preserve all application limits and strict latency gates.
- Add cleanup/isolation/metrics tests and strict typing. Runtime acceptance and broader history/provider/deployment scenarios remain pending.
- The initial run exposed 653 ms session-start p95 despite a 30 ms mixed p95. Require operation-specific latency gates and implement ADR-046 shared immutable-content locks plus focused topic selection; database concurrency/recheck tests pass, fresh load/full regression pending.
- Batch final plan eligibility/locking and bound manual candidate work. Final native baseline passes: 7,000 requests, zero errors, 500 sessions/2,500 grades, START p95 441 ms and answer p95 27 ms at 19.996 answer dispatches/s. Hosted CI 37933227560 passed 646 Python, 66 browser, five tooling and one isolated UI case plus full recovery/security/container gates; promoted `f2dbf8a` and removed its branch.

## 9 October 2026 — verified narrow learner journey

- Add NFR-ACC-001/NFR-COMP-001 coverage at 320 CSS pixels with touch enabled: onboarding, five-question practice, durable resume, feedback, progress and history.
- Check horizontal reflow, actual key touch-target dimensions and axe results; include the journey in all three existing engine runs and add `make test-web-mobile` for focused verification.
- Hosted CI 37925290651 passed 66 real-API browser executions, 621 Python, five tooling and one isolated UI case, plus full recovery/security/container gates. Promoted `83c6102` and removed its branch. This is emulated viewport evidence, not physical Android or branded Safari acceptance.

## 9 October 2026 — verified exact accountability-record holds

- Add FLAG_HISTORY and DATA_REQUEST_REVIEW under ADR-045 (FR-ID-006, BR-010, FR-OPS-003, NFR-SEC-002), using immutable parent ownership and exact primary-key references.
- Add migration 0024, strict generated contracts, administrator options and SQL DELETE protection; preserve normal triage, immutable evidence, finite decisions and disabled deletion.
- Hosted CI 37924489562 passed 621 Python, five tooling, 63 real-API browser and one isolated UI case, including migration/recovery, role/security and container smoke. Promoted `ce9d9f3` to main and removed its branch locally/remotely. Native focused cases pass; unavailable native storage remains separate.

## 9 October 2026 — verified MinIO download recovery

- Add at most three dependency-download attempts and terminal Go module verification after native network EOFs (NFR-MNT-001).
- Reuse locked module/build caches for the unchanged ADR-019 source/compiler/base pins; verify and compile within one build step.
- Hosted CI 37923437046 passed 615 Python, five tooling, 63 browser and one isolated UI test, actual service/seed, recovery, security scans and container smoke. Promoted `04de7ea` to main and removed its branch locally/remotely; native module downloads remain incomplete.

## 9 October 2026 — verified bounded export projection

Hosted CI [37918757085](https://github.com/Jotham566/kasoma/actions/runs/37918757085)
passed at `8c14590`: 427 unit/contract plus 184 integration tests (611 Python), five tooling tests,
63 real-API browser executions and one isolated editor test. Clean setup/migrations/seed, focused
rubric/role checks, lint/format/types/contracts/build, security/source/image scans and container smoke
passed. Recovery restored 54 tables/272 synthetic rows in 385 ms with pgvector/immutable guards and
no cleanup failures. Cold transfer was 191501/194260/193634 bytes, below 250000 for all engines.
The implementation is on main and its completed branch is removed locally and remotely.

- Native migrations, focused rubric/export tests, recovery, role and security checks pass. Full native integration has one unavailable-storage failure; MinIO/Playwright downloads encountered network interruptions.
- Record the asynchronous export design proposal and the next verified dependency-download resilience work; neither enables new learner scoring or large-history delivery.

## 9 October 2026 — bounded personal-export reads

- Replace retained ORM lookup collections with batched reads and owner-filtered SQL joins/subqueries (FR-ID-006, NFR-SEC-001/002, NFR-MNT-001).
- Preserve diagnostic sealing, exact related-row accounting, all-or-nothing synchronous limits and existing authorization/retention. No API, migration or architecture change.
- Add synthetic memory/batch, exact-cap and cursor-cleanup regressions plus focused database commands. Eight rubric and eleven focused export cases pass natively; full hosted acceptance is recorded above. Async large-history delivery is separate.

## 9 October 2026 — verified rubric, telemetry and dependency release

Hosted CI [37914864557](https://github.com/Jotham566/kasoma/actions/runs/37914864557)
passed at `ed7d7d5`: 427 unit/contract and 182 integration tests (609 Python total), five tooling
tests, 63 real-API browser journeys across Chromium/Firefox/WebKit and one isolated editor UI test.
Clean setup/migrations/seed, eight focused rubric cases, restricted-login verification,
lint/format/types/contracts/build, dependency/source/image security checks and container smoke all
passed. The isolated logical recovery restored 54 tables/272 synthetic rows in 455 ms and verified
pgvector/immutable guards; this is not production PITR/RPO/RTO evidence. Cold question transfers
were 191529/194251/193635 bytes, each below 250000. Commit `ed7d7d5` is on main; both completed
rubric/telemetry branches were deleted locally and remotely.

- Correct legacy JSON/JSONB rubric comparisons and remounted textarea label associations, with exact save/reload regressions.
- Patch runtime Next.js to 16.3.8 and affected Sharp/source-map-js to 0.35.5/1.2.2; retain ADR-031 lint tooling.
- Document the macOS Docker CLI PATH fix after daemon availability returned; native image builds/checks are still pending.
- Record FR-ID-006 large-history export readiness and the next bounded projection slice. No new architectural decision or learner-scoring enablement.

## 9 October 2026 — synthetic model-call telemetry

- Instrument the existing fake short-text rehearsal with correlated, closed per-call and outcome events (NFR-OBS-001, FR-OPS-002; AI gateway specification).
- Record bounded metadata, elapsed time and provider-reported usage; failures report unknown usage and omit provider diagnostics. Use disposable per-rehearsal HMAC fingerprints instead of stable answer hashes.
- Add privacy/schema/correlation/repair/failure tests. No live inference, learner scoring, cost estimate or aggregate dashboard acceptance is enabled.

## 9 October 2026 — reviewed rubric authoring

- Add version-pinned rubric/criterion persistence and independent short-text content review (FR-CNT-001–004, FR-GRD-003/004, NFR-SEC-002; ADR-044).
- Preserve legacy document hashes and request retries; require complete matching criteria before review and freeze normalized material with its item version.
- Add staff author/reviewer forms, generated contracts, SQL assignment exclusion and synthetic regression cases. Learner short-text delivery and model scoring remain disabled.
- Complete hosted acceptance is recorded below; learner scoring remains a separate gate.

## 9 October 2026 — verified holds, expiry and rubric context

- Promote `64394ac` after CI 37228984415: 587 Python (413 unit/contract, 174 integration), 60 browser and five tooling checks, clean migrations/recovery/security/container gates.
- This includes restricted-login permission verification, ADR-043 learning-record holds and bounded authentication expiry, also verified by CI 37228338121. Remove their four completed branches.
- The earlier missing users-row lock grant is fixed and verified. Production grants, full retention/erasure and academic grading approval remain open.

## 4 October 2026 — explicit synthetic rubric material

- Require criterion text, acceptable evidence, common errors and prohibited inferences in the offline short-text context (FR-GRD-003/004; specified rubric fields).
- Bound and redact criterion material, preserve explicit empty error/inference lists, and version both fake rehearsal prompts as v2.
- Add 13 context/privacy cases and verify both independent passes receive the complete rubric. Local 413 unit/contract checks pass; persistence, academic approval and learner scoring remain pending. No architecture or API change.

## 4 October 2026 — verified API timing

- Promote `74a4a8f` after CI 37226011029 passes 556 Python, 60 browser and five tooling checks, clean migration/recovery, security and container gates.
- Remove the completed request-timing branch; aggregated latency and load acceptance remain pending.

## 4 October 2026 — bounded ephemeral authentication expiry

- Move existing expired OTP/rate-bucket cleanup out of login requests into a bounded worker task every 60 seconds (FR-ID-001, security retention specification, NFR-OBS-001).
- Lock rate buckets before loading/refreshing them so concurrent cleanup cannot invalidate a request; skip locked rows and retain active windows.
- Add batch/boundary/concurrency/rollback/redaction tests and a closed count-only event schema. Preserve OTP validity, consent, sessions, learning and accountability evidence. No migration, provider or architectural change.

## 4 October 2026 — individual learning-record holds

- Extend FR-ID-006/BR-010 preservation to grades, mastery evidence and mastery history under ADR-043; keep independent recent-OTP ADMIN claim, finite exact-record decisions and immutable audit receipts.
- Add migration 0022 ownership/DELETE guards and generated API/client enums; clarify grade attempt references and seven supported types in the administrator UI.
- Add ownership, direct-SQL, release/expiry, immutable-evidence and export-boundary tests. Deletion remains disabled and hold coverage remains incomplete.

## 4 October 2026 — restricted assessment login verification

- Add a real temporary PostgreSQL login test for NFR-SEC-002: synthetic objective assessment and idempotent mastery recording with narrowly enumerated writes.
- Check schema changes, trigger bypass, evidence rewrites, role escalation and password-catalog reads are denied; remove only the generated role after each test.
- Add `make test-runtime-role` and update repository status/runbook. Local lint/types/contracts and 394 unit checks pass; native PostgreSQL is unavailable and hosted database acceptance is pending.
- Default application credentials remain unchanged; this is assessment-path verification, not production role provisioning or complete grant coverage. No architecture change.

## 4 October 2026 — verified recovery, browser engines and cold transfer

- Promote recovery `42a6e08` after CI 37223872075: 550 Python/20 browser/five tooling checks and a verified 52-table, 270-row synthetic restore with clean cleanup.
- Promote browser/transfer `96a16d0` after CI 37224172033: 550 Python/60 browser/five tooling checks, all security/container gates, and cold transfer of 191389–194127 bytes against 250000.
- Remove both completed branches. Production PITR/RPO/RTO, branded/mobile/browser-version and real-network gates remain open.

## 4 October 2026 — minimized API response-start timing

- Add monotonic response-start milliseconds to correlated API logs and spans (NFR-OBS-001/FR-OPS-002), including safe error paths.
- Extend the event schema additively; preserve worker events and omit URLs, query parameters, identities, credentials and payloads.
- Add six deterministic timing/redaction/compatibility cases. This is instrumentation, not aggregated p95 or load/SLO acceptance. No architectural decision changes.

## 4 October 2026 — browser engine regression matrix

- Add a cold-context first-question transfer assertion (NFR-BW-001), counting encoded bodies and headers against 250,000 bytes; runtime measurements remain pending.
- Extend `make e2e` to sequential Chromium, Firefox and WebKit runs with fresh synthetic fixtures per shard (NFR-COMP-001/NFR-ACC-001).
- Add prescribed engine install/list/focused commands and CI coverage; preserve all existing assertions. No application architecture change.
- Lint/types/contracts and three 20-case inventories pass; native execution fails at database setup, so 60 browser executions remain pending hosted verification. Branded/mobile/version coverage remains a release gate.

## 4 October 2026 — isolated synthetic recovery drill

- Add `make recovery-drill`, original synthetic assessment fixtures and a hosted CI recovery gate for NFR-REL-002.
- Restore only into a fresh database created by the drill; compare every table inventory, pgvector and selected immutable guards; never overwrite or copy the developer database.
- Fix the first hosted inventory check to use ORM table names, including `consent_records`; failed-run temporary database cleanup succeeded.
- Add ADR-042, 16 profile/cleanup contract cases and a runbook. Native database creation is unavailable; hosted restore acceptance and production PITR/RPO/RTO remain pending.

## 4 October 2026 — verified local channel operations

- Promote `34950b0` to main after full CI 37221185319: 479 Python, 20 browser and five tooling checks plus clean migrations, security scans and container smoke.
- Verify bounded ADMIN channel queues/status cohorts, sampled fake-feedback dispatch timing and configurable alerts (FR-OPS-002/004, NFR-OBS-001). Remove the completed branch.
- Synthetic fake acceptance timings do not establish production delivery or performance SLOs.

## 4 October 2026 — budgeted fake short-text rehearsal

- Add independent rubric passes, one global schema repair and bounded request/token/deadline handling through the existing ModelGateway (FR-GRD-003/004/005).
- Extend FakeModelProvider with deterministic candidate/exception fixtures; failures remain payload-free and agreement never enables learner scoring.
- Record ADR-041 and 15 new tests; local lint/types/contracts and 372 unit/contract plus five tooling checks pass. Hosted regression and academic/learner integration gates remain pending.

## 4 October 2026 — verified five-question WhatsApp conversations

- Promote `5063528` to main after full hosted CI 37220225176: 469 Python, 20 browser and five tooling checks plus clean migrations/security/container gates.
- Verify signed reply-bound practice, shared objective scoring/mastery, safe feedback, STOP/expiry, concurrent duplicate protection and broker-outage recovery.
- Remove the completed conversation branch. Production and academic acceptance remain gated.

## 4 October 2026 — synthetic short-text validation foundation

- Add strict version-pinned rubric candidate validation for FR-GRD-003/004/005, with 40 deterministic contract cases and ADR-040.
- Reject malformed/coerced output, unsupported evidence/context and caller safety flags; return candidates only, never learner scores.
- Local formatting/lint/types/contracts and 357 unit/contract plus five tooling checks pass. Academic calibration, gateway orchestration and learner integration remain pending.

## 3 October 2026 — verified local WhatsApp linking

- Add migration 0018, recent-auth/current-consent single-use codes and owner status/unlink (FR-WA-001/006).
- Add bounded signed durable webhook intake, atomic deduplication and immediate STOP barriers (FR-WA-004 foundation).
- Add transactional processing, fake delivery, bounded retries, configurable limits and transient expiry.
- Include owned channel records in exports and deletion previews; channel hold coverage remains pending.
- Add generated contracts, channel UI, local simulator, messaging worker and ADR-034.
- Commit `23da19c` passes full hosted CI: 395 Python, 20 browser and five tooling tests; setup/migrations/seed, lint/types/contracts/build and security/container gates pass.
- Record the native Docker interruption separately; no reset or weakened gate. Five-question practice and production messaging remain pending.

## 3 October 2026 — local operations visibility

- Publish bounded draft imports as `5bdd122` and remove the completed branch.
- Add ADMIN-only operational snapshots, bounded queue/flag counts, worker heartbeat and configurable threshold alerts (FR-OPS-002 partial).
- Add local periodic monitoring and safe alert logs; distinguish unavailable instrumentation from measured zeros. No external notification delivery.
- Fix cross-application Celery settings reuse with application-local task registration and regressions for monitoring/imports/export expiry.
- Record ADR-033, generated contracts, configuration/runbook and regression/browser coverage. Full hosted CI passes: 360 Python, 19 browser and five tooling tests plus all setup/migration/build/security/container gates.
- Publish `7218898` to main and remove the completed operations branch.


## 3 October 2026 — bounded synthetic draft imports

- Publish legal holds (`ec53ac4`) and lint security (`b766266`) to main after full hosted CI passed; remove completed branches.
- Add 1–20-record, 64 KiB synthetic JSON author imports (FR-CNT-001), source locators, owner-only status and draft links.
- Add migration 0017 and PostgreSQL-backed import commands, atomic draft creation, duplicate reporting, author rechecks and bounded retries/expiry.
- Preserve independent academic review, audit/outbox and synthetic-only eligibility. Add ADR-032, contracts, API/browser/worker tests and `make process-imports`.
- Add an explicit release-evidence register for missing academic, privacy and provider approvals.
- Docker recovered; all 347 Python, 18 browser and five tooling tests pass, alongside clean migrations/seed, lint/types/contracts/build, security scans and container smoke. Initial browser-selector failure was corrected; no final failed checks.

## 3 October 2026 — lint dependency security remediation

- Commit record legal holds as `ec53ac4` (FR-ID-006, BR-010); publication follows security verification.
- Remove the newly audited vulnerable braces dependency from Next lint tooling through
  a scoped tinyglobby override and pinned directory-discovery compatibility patch.
- Add actual-plugin glob/deep-pattern and lint-rule regressions to `make test-tooling`
  and `make test-unit`; add pinned-runtime `make deps-lock` for dependency maintenance.
- Record ADR-031; keep audit severity and all lint rules unchanged.
- Docker startup currently requires a macOS administrator prompt, blocking local
  database/container verification. Prior legal-hold integration/browser evidence is retained.

## 30 September 2026 — specific-record legal holds (local implementation)

- Deletion-impact preview committed and pushed to main as `6f7f210`; completed branch removed.
- Add recent-OTP independent ADMIN claimant controls for finite holds on owned consent,
  attempt, content-flag and data-request records, with opaque decision references.
- Add migration 0016, immutable scope, one-time release, atomic audit/outbox evidence,
  bounded read/write rates, retry receipts and active-hold DELETE guards.
- Add administrator create/list/release controls, generated contracts and SQL/API/browser
  tests for ownership, retries, expiry, rollback and preservation.
- Show active registered holds in the deletion preview while retaining incomplete-coverage
  and execution blockers. Exclude internal hold metadata/events from learner exports.
- Fix an initial-session-check race that could overwrite onboarding action errors; keep
  actions disabled until initialization settles and add a delayed-response browser regression.
- Record [ADR-030](docs/decisions/ADR/030-record-legal-holds.md), update sprint, traceability,
  API/data/runbook and [verification](docs/implementation/E8_LEGAL_HOLDS_VERIFICATION.md).
  This does not implement erasure, universal hold coverage or retention expiry.

## 29 September 2026 — deletion-impact preview (local implementation)

- Owned exports committed and pushed to main as `d20c344`; completed branch removed.
- Add a recent-OTP, independent-claimant ADMIN preview of linked record counts and
  retention/review categories for pending deletion requests, with audited access.
- Bound per-source counts, account for unbound login challenges and related staff
  provenance, and exclude another learner's bound guardian challenges from hash matching.
- Show unresolved legal-hold, erasure and anonymization gates explicitly. Preview does
  not decrypt personal records, revoke access, change data or authorize deletion.
- Add API/generated contracts, administrator UI and regression tests; no migration.
- Correct owner exports to decrypt the display name instead of returning its storage ciphertext;
  add a profiled-learner regression. Deletion previews still never decrypt personal data.
- Update [ADR-029](docs/decisions/ADR/029-deletion-impact-preview.md), sprint,
  traceability, API/data/runbook and [verification](docs/implementation/E8_DELETION_PREVIEW_VERIFICATION.md).

## 29 September 2026 — owned data exports (local implementation)

- Data-request intake committed and pushed to main as `68146b9`; completed branch removed.
- Add recent-OTP owner-only JSON exports with explicit field projections, diagnostic
  sealing, encrypted frozen retries, atomic completion and six-year retention deadlines.
- Add migration 0015, 24-hour download expiry, a bounded five-minute worker sweep and
  `make expire-exports`; expired copies are removed without deleting request evidence.
- Add learner download/retry UI, generated contracts and API/SQL/browser regressions.
- Record [ADR-028](docs/decisions/ADR/028-owned-data-exports.md) and update sprint,
  traceability, API/data/runbook and [verification](docs/implementation/E8_DATA_EXPORTS_VERIFICATION.md).
- Deletion/anonymization, large-history exports and accountability-retention/legal-hold
  processing remain pending; this does not establish production privacy acceptance.

## 29 September 2026 — data-request intake (local implementation)

- Multiple-choice support committed and pushed to main as `02f96bc`; completed branch removed.
- Add recent-OTP export/deletion request intake, owned status and safe acknowledgement,
  including after learning-consent withdrawal and before profile completion.
- Add an independent ADMIN review queue/claim, atomic audits/outbox, deduplicated retries,
  immutable evidence and explicit six-year-after-completion retention policy.
- Add migration 0014, generated contracts, learner/admin screens and regression tests.
- Forward request pagination through the web gateway and install repository-local Corepack
  shims so nested build tasks retain pinned pnpm despite unrelated global installations.
- Update ADR-027, API/data/runbook documentation, sprint and traceability; see
  [verification](docs/implementation/E8_DATA_REQUESTS_VERIFICATION.md). Fulfillment,
  completion evidence, deletion/anonymization and retention jobs remain pending.

## 28 September 2026 — deterministic multiple choice (local implementation)

- Flags/triage committed and pushed to main as `bd9dae3`; completed branch removed.
- Add reviewed multiple-choice keys, exact-set scoring and checkbox delivery through
  shared revision, diagnostic and reassessment paths. Preserve hint/evidence controls.
- Canonicalize selection order for idempotent retries; reject duplicate/unknown IDs.
- Add additive migration 0013, generated contracts, synthetic fixtures and tests.
- Run browser tests in two fresh isolated shards to retain the production OTP peer limit.
- Update ADR-026, API/data/runbook documentation, sprint and traceability; see
  [verification](docs/implementation/E4_MULTIPLE_CHOICE_VERIFICATION.md). Academic
  content approval, short-text benchmark and production deployment remain gated.

## 28 September 2026 — learner flags and triage (local implementation)

- Progress/history committed and pushed to main as `df855ab`; completed branch removed.
- Add owned attempt-bound reports, encrypted optional comments, safe receipt recovery,
  rate limits and exact retry handling across browser interruption/reload.
- Add reviewer/admin queue, independent self-assignment, priorities, revision-checked
  resolution/reopening and atomic audit/history/outbox records.
- Preserve grades, mastery and sealed diagnostics; require two reviewers for disputed
  successor content. Migrations 0011–0012 are additive and enforce the approved retention due date.
- Add ADR-025, generated contracts, tests, traceability and
  [verification](docs/implementation/E8_FLAGS_VERIFICATION.md). Production support,
  retention jobs, safeguarding/legal approval and academic calibration remain gated.

## 28 September 2026 — progress and session history (local implementation)

- Unseen reassessment committed and pushed to main as `73c1fba`; completed branch removed.
- Add consent-aware subject/topic/competency progress with evidence confidence, coverage
  and guarded recent-change text; unfinished diagnostic evidence remains sealed.
- Add owned, cursor-paginated session history with resume/review and Kampala timestamps.
- Add ADR-024, generated contracts, regression tests and documentation; no new migration.
- See [verification](docs/implementation/E6_PROGRESS_VERIFICATION.md). Academic calibration
  and production acceptance remain separate gates.

## 28 September 2026 — unseen reassessment (local implementation)

- Reviewed hints committed and pushed to main as `3c0c3ba`; hosted CI passed and completed branch removed.
- Add reviewed equivalent-version claims with independent review of both sides.
- Add one-item unseen reassessment, same-skill/difficulty fallback, conservative clone
  exclusion, durable source linkage and replayable selection evidence.
- Reuse the shared player/grader/mastery service; preserve the original result and
  record separate independent evidence with safe lifecycle events.
- Add migration 0010, generated contracts, synthetic fixtures and regression coverage.
- See [verification](docs/implementation/E4_REASSESSMENT_VERIFICATION.md). Academic
  transfer validity, calibrated resolution criteria and production gates remain pending.

## 28 September 2026 — reviewed revision hints (local implementation)

- Recommended practice merged to main as `88dd880`; hosted CI passed and its branch was removed.
- Add authored/reviewed progressive hints, durable disclosure and safe retry/resume.
- Freeze pre-answer usage and highest level for mastery independence weighting;
  post-answer remediation preserves original grading/evidence and diagnostics block hints.
- Add migration 0009, generated contracts, synthetic fixtures and API/browser tests.
- Require changelog, sprint, traceability and relevant verification/runbook updates
  alongside each implementation change in `AGENTS.md`.
- See [verification evidence](docs/implementation/E4_HINTS_VERIFICATION.md); production
  academic/privacy gates and unseen reassessment remain pending.

## E5 recommended practice (local synthetic verification)

- Versioned synthetic ranking, prerequisite redirection and immutable replay snapshots.
- Explained home recommendation and resumable 5–10-item recommended plans.
- Shared reservation exclusion for manual and adaptive practice.

- E2: synthetic single-choice authoring, independent review, version immutability,
  role checks and append-only content audit, with migration and browser/API tests.

- E1: local OTP identity, protected learner profiles, rotating sessions and separate
  guardian-consent/learner-assent flows with migration, contracts and tests.

Record meaningful repository and product changes here. A documentation baseline is not an application release.

## Unreleased

### Changed

- Moved product documents to `docs/product/` and the engineering pack to `docs/specifications/`.
- Renamed the software requirements document to `01_SRD.md` and updated references.
- Expanded root engineering instructions while preserving the approved source-of-truth hierarchy.

### Added

- E0 local runtime foundation, locked toolchains, health contract/client, migration,
  synthetic fixtures, provider boundaries, tests and initial CI (verification in current sprint).
- Phase 0 assessment and ADR-013 for delegated bootstrap choices.

- ADR navigation, current sprint and implementation traceability for all 61 SRD requirements.
- Workspace directory scaffolding, a safe environment example and a reserved Compose file.
- Make targets for documentation validation and explicit errors for pending runtime commands.

## 2026-09-22 — Initial specification baseline

- Product whitepaper, roadmap and engineering specification pack.
- README, contributor guidance, agent instructions, pull request template and Git/editor conventions.

### E3 first assessment slice

- Add consent-aware topic practice, approved version selection, immutable attempts,
  deterministic single-choice grades, solution gating and transactional result events.
- Add learner resume/retry UI, synthetic fixture command and ADR-016.
- E2 `b5cfd75` pushed to main; hosted CI passed and completed E1/E2 branches removed.

### E4 numeric grading and readiness

- Merge E3 `22773fd`, verify hosted CI and remove its completed branch.
- Resolve difficulty-label mapping and Week 5/6 sequencing in ADR-017 without
  changing published content or weakening quality gates.
- Add numeric authoring/review, safe learner input, exact rational grading,
  units/tolerance/precision policy, immutable response storage and regression tests.

## 28 September 2026 — diagnostic and initial mastery

- E4 numeric grading and the pinned MinIO source-build CI repair merged to main.
- Added synthetic resumable subject diagnostics with hidden in-session grades.
- Added immutable mastery evidence, baseline estimates/history and offline replay.
- Added generated contracts, browser results, migration and regression evidence.
- Full adaptive recommendation factors and academic calibration remain pending.

### Verified — shared assessment transactions (FR-WA-003/004)

- Extract internal actor-authorized start/serve/submit methods while preserving web contracts.
- Keep deterministic grading, mastery, receipts and outbox events in the caller transaction.
- Add rollback/committed-retry and current account/consent/enrollment/ownership regressions.
- Record ADR-035. Commit `50044d4` passed hosted CI 37149982356: 398 Python, 20 browser
  and five tooling tests, including clean migrations and security/container gates; published to main.

### In progress — objective channel formatting (FR-WA-002/003/005)

- Add explicit WHATSAPP suitability and bounded plain-text question rendering.
- Normalize numbered choice/multiple-choice and exact numeric replies into shared contracts.
- Record ADR-036 and add key-leakage, malformed-response, length and shared-grader regressions.
- Question/reply binding and the conversation worker remain pending.

### In progress — channel assessment provenance (FR-WA-002/003/004)

- Record ADR-037 and additive migration 0019 for immutable WHATSAPP attempt provenance.
- Filter supported questions before selection and validate complete five-item plans on continuation.
- Preserve WEB HTTP schemas and receipt hashes; separate internal WHATSAPP fingerprints.
- Add objective score/mastery parity, replay, current approval and database guard regressions.
- Webhook conversation and delivery integration remain pending.

### In progress — concise channel feedback (FR-WA-005)

- Extend ADR-036 with bounded shared-grade feedback and authenticated web solution links.
- Preserve complete academic instructions or use the web fallback; reject secret-bearing origins.
- Add format, length, continuation and link-safety regressions; delivery integration remains pending.

### 4 October 2026 — verified channel assessment foundation

- Publish `c0b5b55` to main after all hosted gates passed: 437 Python, 20 browser and five tooling
  tests, including six channel capability/parity regressions. Remove completed foundation branches.

### In progress — signed local five-question conversation (FR-WA-002–006)

- Record ADR-038; add migration 0020 for expiring link-revision-bound conversation pointers and
  encrypted transient structured replies. Bind numbered menus/answers to the exact sent question.
- Reuse shared atomic assessment operations; reconstruct approved question and grade references
  under current authorization before fake delivery. STOP/unlink clears the channel pointer.
- Add bounded local wake-up after durable intake, transport schemas, exports/inventory and complete
  synthetic flow, replay, withdrawal, STOP, rollback and expiry tests. Hosted verification pending.

- Align local channel instructions and development runbook with exact-reply practice controls.
- Recheck the requested channel on serving/submission so a WHATSAPP-only version cannot be
  answered through WEB simply by resuming its shared session.

### In progress — local channel operations (FR-OPS-002/004)

- Record ADR-039 and add operational indexes in migration 0021.
- Extend minimized ADMIN snapshots with bounded queue/status cohorts, oldest age and sampled
  local fake-dispatch p95; expose no-sample state and sample truncation explicitly.
- Add typed local thresholds, safe alert schema, generated contracts, dashboard and regression tests.
- No production messaging, external notifications or release latency acceptance is implied.

## 4 October 2026 — restricted-login row-lock correction

- Fix the NFR-SEC-002 test grant profile after CI 37227070209 exposed the attempt-hint guard's users-row lock requirement.
- Permit only the existing mutable display_name field; add explicit denied identity/status/birth-date writes and exact column-grant cleanup. Production credentials remain unchanged; rerun required.

FR-GRD-004/005 and NFR-SEC-002: internal `services/short_text_contracts.py` adds bounded
answer input and distinct pending/neutral outcomes, rejecting scores and hidden/provider
material. ADR-050 remains proposed; runtime routes, worker and privacy integration are
not implemented by these contracts. Verification passes: 699 unit/contract tests (33 new outcome/input cases), 35 tooling
checks, format/lint/types and generated-contract comparison. No HTTP schema changed.

FR-GRD-004/005 / NFR-SEC-002: migration 0026, grading-work models and transactional
storage are under verification. Commands have one claim, bounded expiry and immutable
transition snapshots. No learner/worker path is enabled. Use `make test-grading-work`;
privacy inventory/export/hold coverage and restricted-role checks remain integration gates.

Durable-store focused verification passes 24 cases (seven PostgreSQL, 17 transition),
including contention, rollback, expiry, publication consistency and owned/foreign
export projection. Work/history counts are in deletion inventory. Full backend
regression is running; exact-record holds and restricted-role extension still gate
runtime enablement. See `docs/implementation/E4_DURABLE_GRADING_VERIFICATION.md`.

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

Durable grading/history local gate now passes: full migration/backend run has 747
unit/contract, 35 tooling and 266 integration cases; two additional history-hold cases
and the extended restricted-login check pass separately. Six three-engine privacy
journeys, populated logical recovery, source/dependency checks, final rebuilt image
scans and eight-service smoke pass. Exact-head hosted acceptance remains required;
worker/learner/scoring integration is still disabled.


NFR-MNT-001/OBS-001: frozen configuration backend passes1277 unit/contract,35 tooling
and512 integration, but serial local Chromium fails two cases with HTTP500. Promotion
remains pending. A bounded fake-only/owned-schema driver-error diagnostic is a separate
local test-harness candidate; it logs fixed categories only, changes no timeout/retry
and does not claim a fix. See E8_OPERATIONS_CONFIGURATION_READINESS.md.


Complete hosted39322035839 is SUCCESS at exact configuration source3e6175b:1277
unit/contract,512 integration,35 tooling and117 full browser executions plus every
mandatory engineering gate. Recovery verifies71 tables/691 rows (logical531ms; actual
PG/MinIO one42,060-byte object308ms), guards/scope/fault probes and empty cleanup.
Local serial/browser diagnosis still reproduces an assessment500 with QUERY_CANCELLED;
no cause/fix is claimed, and main promotion remains deferred. The separate bounded
local diagnostic harness has24 focused/1301 unit cases but no own hosted acceptance.
ADR-061 foundation1851740 is separately pushed for complete hosted39328044945; its
head stays fixed and its acceptance remains pending. See configuration/erasure readiness.


ADR-068 (NFR-MNT-001/PERF-001/002/SEC-002/OBS-001) is a separate browser-isolation
candidate after observing11.3GB of shared system catalogs. Only a new owned bounded
PostgreSQL service hosts the standard synthetic browser fixture; normal services and
all existing schemas remain. Scope/cleanup/private-key tests and actual browser/hosted
acceptance are pending. No prior HTTP500 or pointer failure is declared fixed.


ADR-068 local transport guard rejects remote Docker hosts/contexts before daemon calls,
pins a Unix endpoint for the synthetic harness and restores process environment.86
resource controls and1328 unit/contract checks pass; actual final-source/native and
combined hosted acceptance remain pending. Normal services/global Docker context stay
unchanged.

ADR-061 prerequisite source1851740 passes complete hosted39328044945:1374 unit/contract,
514 integration,35 tooling and117 browsers plus all engineering gates. Recovery71 tables/
691 rows passes logical607ms and actual PG/MinIO one42,060-byte object193ms with empty
cleanup and stripped retirement denied. Only closed contracts/private configuration,
structural drift checks and disabled-role grant refusal are accepted; no closure or
account-erasure execution/fulfillment exists. Only Markdown closeout follows this source.
Combined integration and full approved lifecycle/preservation/removal acceptance remain.


The combined codex/browser-isolation candidate now integrates independently hosted-
verified configuration3e6175b and ADR-061 foundation1851740 (only Markdown follows),
plus locally verified ADR-068 browser isolation and pinned-local Docker transport.
All117 pre-integration browser executions pass with nine exact owned containers removed;
the transport follow-up passes nine actual assessment executions with empty cleanup.
The merge changes no application schema beyond0044. Combined-source backend/browser/
recovery/security/image/service and complete hosted acceptance are still required.
Main remains eb05457; review execution stays off and no account closure/removal exists.

ADR-069 adds make test-erasure-identity-isolated: the closed identity/race target runs
on one freshly owned local PostgreSQL source with separate purpose/label, private
keys, fake providers and exact-ID cleanup. Existing browser/recovery defaults remain.
The first103 resource/controller controls pass; native before/after and complete
engineering acceptance remain pending. No execution capability or review-data access.

## Identity coordination and owned-source verification — local results

FR-ID-003/005/006, NFR-SEC-002/MNT-001: the existing-source baseline fails both
new barrier/binding regressions (two fail, nine pass,34.78s). The candidate passes
all11 identity/LINK/single-use/provisioning cases in19.64s and, after the final
supervisor/diagnostic correction,17.37s. Both completed sources report empty cleanup;
the initial two exact IDs are independently confirmed absent. First invocation refused
the normal Mailpit setting before creating any resource; the test entrypoint now
explicitly selects fake model/email adapters, matching the existing browser entrypoint.

Quality/types215 files,1,444 unit/contract,35 tooling,105 resource/controller controls
and generated-contract checks pass. Initial Bandit reports three low-severity command
findings. A fixed absolute /usr/bin/make removes path selection; two narrowly documented
B404/B603 annotations cover only the reviewed constant argv/no-shell child boundary.
Subsequent full source/dependency/secret checks pass (5.71MB secret scan, no leaks).
No global scanner exclusion or application security gate changes.

ADR-069 records the test-resource choice; CI invokes the same owned-source target.
Complete combined backend/browser/recovery/image/service and own hosted acceptance
remain pending. This is identity coordination, not a permanent closed_at/SQL session
guard, account-closure authorization, actual erasure or DELETE fulfillment.

The final focused assessment matrix passes15 executions: five each in Chromium,
Firefox and WebKit, including pointer stability at320 and1280 pixels. The original
document-position regression, lost acknowledgement/resume and grading gates remain.
Screenshots confirm readable narrow feedback/actions. Complete browser, backend,
image/service/recovery and own exact-source hosted acceptance remain pending.

The first final full-browser attempt fails Chromium shard2 at WhatsApp onboarding:
OTP request returns202, verification returns400/OTP_INVALID and no profile appears
(17 pass). This is an authentication rejection, not another proved pointer miss.
The expanded36-test engine cohort now uses three fresh API shards to retain the
unchanged20-per-peer OTP policy; no production rate or test deadline is increased.
The removed fixture's exact suppression cause is unproven. A new complete matrix
is required; focused15 passes do not accept this failed full run.

The three-shard standard cohort passes108 executions (12 in each of nine fresh
shards), with nine empty cleanup reports and independent exact-ID absence confirmed
for all nine containers. The focused15 assessment cases also pass at320/1280 pixels.
This supersedes the failed two-shard cohort for this local standard-browser matrix
only; configuration/short-text/full hosted engineering acceptance remain separate.

## Current combined verification candidate

This source combines the ADR-061 identity lock/ADR-069 owned test source with the
practice root-scroll correction and three-shard browser budget. Local component
evidence is1,444 unit/contract,105 resource/controller,11 actual identity and15
focused/108 standard browser passes; prior failures remain recorded. Combined-source
checks and complete exact-source hosted verification must pass before main publication.
No permanent closure marker, authorization/executor, erasure or DELETE completion exists.

Combined source12c6b60 passes local quality/types,1,444 unit/contract,35 tooling,
105 resource/controller,11 owned-database identity cases, contracts/build and full
source/dependency/secret checks. Only two reviewed constant-command findings are annotated; Bandit's commentary
parsing warnings do not suppress any additional check. A comment-only cleanup attempt
fails import-order lint and is reverted before freezing source12c6b60. Complete
hosted/native browser/recovery acceptance is pending.

The first managed-checkout browser attempt has12 launch failures before any journey:
the checkout has no local Playwright executable cache. Its owned API source cleans
up successfully. No application failure or pass is inferred. The rerun uses the
existing verified root browser cache through the standard Make variable, after an
exact pnpm-lock.yaml comparison; source and test deadlines remain unchanged.

The shared-cache rerun passes Chromium36 and Firefox shard1 twelve cases, but
Firefox shard2 has11 passes/one native attachment verifier RuntimeError. That helper
resolves its repository-local Firefox1509 path, which is absent in this checkout;
a Playwright cache override does not cover it. The run is failed, not full browser
acceptance. Run the prescribed make e2e-install locally, preserve all existing caches
and rerun the complete matrix without an override. No application/source change.

## Frozen identity/UI source12c6b60 — complete local browser and recovery results

The default-cache complete matrix passes123 browser executions:108 standard,12
short-text and three configuration. Twelve owned standard/configuration PostgreSQL
containers have empty cleanup reports and independently confirmed exact-ID absence.
The separate short-text runner retains its existing schema scope; no cleanup of
older developer schemas/roles/caches occurs. Recovery passes71 tables/691 rows318ms
logically and71/691/one42,084-byte ciphertext163ms with actual MinIO, stopped source
services, fault/immutable guards, denied stripped retirement and empty cleanup.
Actual restricted-login verification passes. Production RPO/RTO remains false.

Full own hosted39337786063 remains in progress at exact12c6b60d3a76a82c5e10ee15fc51122f4a130fcb.
Only Markdown closeout follows that runtime/test/Make/workflow tree. Earlier missing
browser/native-cache failures remain failed and are not application acceptance.

Separately, verified foundation source2966bab is published through main64e1f72ee10a3ed39a344525f49b9252341224b6
after complete hosted39334774152. Its configuration, erasure-foundation and browser
branches are proven merged and removed locally/remotely. A remote deletion response
reported ref errors, but independent ls-remote and fetch/prune confirm all three
remote refs absent; no unmerged source is discarded. The main follow-up39339512181
remains live. Docker is8/8 healthy on0044, with the locally verified viewport preview
36cb6e9 and retirement/normal short-text disabled. Host-native Ollama connectivity
is restored without inference. Account closure, erasure and DELETE fulfillment remain
unimplemented; approved ADR-061's SQL barrier/resumable job is the next vertical slice.

Current runtime candidate remains12c6b60 (own full hosted39337786063 pending);
only Markdown follows it and incorporates main64e1f72's accepted2966bab foundation
closeout. The complete local123-browser/identity/recovery checks do not constitute
hosted acceptance or account erasure. Next implement ADR-061's permanent SQL barrier
and resumable job in a new branch; keep both live remote CI heads unchanged.

## SQL lifecycle work in progress on codex/erasure-barrier

FR-ID-003/005/006, BR-010, FR-OPS-003 and NFR-SEC-002/MNT-001: begin the private
control/plan/job mappings and a nullable deferred User.closed_at mapping. Deferred
server-default loading preserves pre-closure migration fixtures without inventing
closure dates. Add an HTTP regression refusing client-supplied closed_at/status while
leaving access and profile unchanged. The lifecycle SQL migration, permanent clock/
role/ownership guards, independent provisioning, atomic closure and resumable worker,
contracts/API/UI and full first-slice verification remain to be implemented. These
mappings are not yet migrated/registered and grant no activation or erasure authority.

## Lifecycle0045 local engineering checkpoint

The candidate passes quality/format/types (217 Python sources),1,445 unit/contract,
35 tooling,98 focused contracts and22 owned actual PostgreSQL identity/lifecycle/
preview cases. Populated0044-to0045 and repeated upgrade pass; the deferred mapping
also preserves historical identity fixtures. OpenAPI consistency/build and dependency,
source, secret and Bandit security checks pass. The initial two E501 strings were
fixed; Bandit's existing narrow-annotation parser warnings are not failures.

Logical recovery verifies74 tables/692 rows in333ms; PostgreSQL/MinIO verifies
74/692/one42,084-byte ciphertext in173ms with source stopped, immutable/dormant guards,
missing/corrupt rejection, stripped-retirement denial and no cleanup failure. These
are synthetic recovery checks, not production RPO/RTO or erasure/checkpoint acceptance.
Full local browsers and exact-source hosted/full integration acceptance remain pending.
No account is closed or erased, and no request is completed. The next implementation
is the independent isolated capability plus atomic authorization/closure and durable
worker continuation under the approved ADR-061 locks and preservation barriers.

## Frozen lifecycle sourcecb0cd22 — complete local browser checkpoint

All123 browser executions pass on the0045 candidate:108 standard,12 short-text and
three configuration. Twelve owned standard/configuration source containers report
empty cleanup and independently confirmed exact-ID absence; all three owned native
identity sources from this iteration are also independently absent. The separate
short-text runner retains its legacy isolated-schema scope; no older schemas, roles,
volumes, images or caches were cleaned. Actual restricted-login verification passes
(one case,15.40s). Existing review Docker is8/8 healthy on verified main72c9c17/0044.

Exact sourcecb0cd2211c7ae82611c6d430d78e913f49f15bec is frozen for complete hosted
[39346406621](https://github.com/Jotham566/kasoma/actions/runs/39346406621), confirmed
in progress. Only Markdown closeout follows that runtime/test/Make/workflow tree;
full522 integration and hosted image/service acceptance remain pending. Do not promote
this candidate from local/browser checks alone. No account closure, erasure, completed
DELETE, production recovery, normal short-text activation or full MVP acceptance.

## 0045 hosted additive-upgrade correction — verification pending

Complete hosted39346406621 atcb0cd22 is FAILED:1,445 unit/contract and521 integration
pass, but the0042 configuration-upgrade fixture compares whole physical user JSON
before/after head. Its only reported difference is the added closed_at:null field.
Later browser/security/image/service stages are unexecuted, not accepted. The source
has no new closure/erasure authority and is not promoted. Main72c9c17's separate
follow-up39345752803 is SUCCESS; it cannot accept0045.

Update that regression to compare all existing row values and require the exact
new closed_at:null addition for users. Every other field/table remains an exact
comparison; do not omit columns, invent a clock, alter the migration or waive checks.
Focused operations/quality verification and a new exact-source full hosted run remain
required. Prior native/browser results remain scoped to their original commands.

## Corrected0045 additive regression — local check

The exact nullable-column expectation correction passes all34 operations configuration
cases, including the populated0042-to-head upgrade. Quality/format/types pass. Every
existing user value and other table row remains an exact parsed-JSON comparison; the
new clock is required null. No application/migration/API behavior or architecture changes.
Own full hosted verification remains required before promotion. The earlier failed
39346406621 remains FAILED, with later stages unexecuted. Review stays on0044/main72c9c17.

## SQL-visible account processing gate — ADR-070 candidate

FR-ID-003/005/006, FR-GRD-003/004, FR-WA-006, FR-OPS-003, BR-010 and
NFR-SEC-002/MNT-001: preserve existing HMAC serialization and add explicit lock_user
shared SQL coordination at account entrypoints. Refresh cached authority after the
gate. Each fake grading dispatch uses an owned idle session's shared gate through
the provider call, without an open transaction, row, band or HMAC lock across inference.
Uncertain acquisition/release invalidates the connection; no gate grants authority.
ADR-070 records the narrow technical amendment to ADR-050, without changing privacy,
retention, provider/academic enablement or erasure permissions. No executor is installed.

Before implementation, three actual access/refresh/LOGIN cases fail and22 controls
pass. An expanded44-case combined fixture gives five expected gate failures,24 passes
and15 Alembic setup errors; no captured diagnostic establishes the setup cause. Its
owned source cleans up. Split identity and model cohorts into two fixed Make targets,
each in a fresh source under the same512m/256m tmpfs bounds and600s child supervision;
never accept an arbitrary caller target. The identity/lifecycle cohort now passes25
cases. Model/pool cleanup tests and complete local/hosted verification remain pending.
Initial B008 fixture-clock lint is corrected by capturing the synthetic instant before
the callback. No account closure, erasure or completed DELETE is accepted. The frozen
0045 sourcecb0cd22 remains separately in hosted39346406621, with its head unchanged.

## ADR-070 scope and failure corrections — candidate

Bind the processing gate to database/schema/subject with negative keys separate from
HMAC serialization. Native29 identity and19 model cases pass, plus1,471 unit/contract
and110 controller controls. An actual unlock failure releases the physical session;
cached principals refresh. The same-UUID cross-schema regression fails before the fix.
Sanitized migration categories identify STORAGE_EXHAUSTED in the failed combined
fixture; two fixed fresh cohorts pass under unchanged caps. Correct a duplicate test
basename; no cache cleanup. Objective load passes7,000 requests/zero errors with
START p95 468.534ms. Mixed-history and final broad/hosted verification remain pending.

## Parent0045 verification failure and correction

Hosted39346406621 atcb0cd22 is FAILED:1,445 unit/contract,521 integration pass; the
0042 configuration-upgrade fixture does not expect the newly added closed_at:null.
No later browser/image/service acceptance is inferred. Correct the test to require
exactly that addition and preserve every old field/row/table; no migration/clock or
application behavior changes. Parent correction is separately verified/published;
this ADR-070 branch includes the same regression fix and still needs its own full CI.
Main72c9c17's follow-up39345752803 succeeds, without accepting either candidate.

## ADR-070 complete local regression checkpoint

Both sequential native load profiles pass7,000 requests with zero errors and exact
owned cleanup. Objective START/ANSWER p95 are468.534/25.784ms. Mixed history includes
25,000 prior grades; START/ANSWER p95 are431.664/26.499ms, with choice/numeric feedback.
No production acceptance or explanation of earlier variance is inferred.

All123 browser executions pass (108 standard,12 short-text,three configuration).
The twelve browser source containers and all30 recorded test-source IDs from this
iteration are independently absent; cleanup reports are empty. The separate short-text
runner keeps its existing schema scope. No older schema, role, volume, SDK or cache
cleanup is performed. Channel/ingress34, channel assessment7, conversation11, export
worker15, export lifecycle42 and configuration34 checks pass (some contracts overlap).
Actual restricted login passes. Final scoped recovery verifies74 tables/692 rows371ms
logically and74/692/one42,084-byte ciphertext194ms with MinIO/source stopped, faults,
immutable/dormant guards, denied stripped retirement and empty cleanup. Production
RPO/RTO remains false.

Dependency/source/secret security passes. Bandit initially flags the fixed transaction
SQL template as B608. Its only interpolated fragment is the module constant; subject
is a UUID bind and the schema OID comes from PostgreSQL. Record a single-line reviewed
B608 exception, without a scanner-wide exclusion; executable AST equality is verified
before/after the annotation. This is not an application SQL correction. Existing two
subprocess exceptions are narrowed to their closed target validation. A bounded probe
of33 local logs finds zero known-secret matches, long connection-password candidates
or bearer candidates; it is not proof about unknown secrets or every artifact.

The parent regression correction passes34 operations cases and1,445 unit/contract
locally and is frozen atb4b20f1 for full hosted39350745638. Previous39346406621 remains
failed (one null-column expectation failure/521 integration passes). Main72c9c17's
separate follow-up succeeds. The same exact null-column expectation fix is included
here; no migration, API, closure clock or retention behavior changes for that fix.

This candidate still needs its own complete hosted acceptance. The full531 integration
suite and image/service acceptance cannot be inferred from focused/native checks.
No erasure executor/authorization, closed identity or completed DELETE exists. Next is
the independently provisioned SQL capability and atomic reviewed plan/authorization/
closure with durable continuation, complete preservation and later bounded removal.

## Frozen ADR-070 candidate and parent correction

Runtime/test/Make/workflow source94feeab6e946c2905202da19a0a85952f5b26036 is frozen
for full hosted [39352281782](https://github.com/Jotham566/kasoma/actions/runs/39352281782),
confirmed in progress. It merges parentb4b20f1 with the identical regression fix;
the merge changes Markdown only relative to verified application/test sourcec2880bc.
Final quality/unit/controller/owned checks pass:1,471 unit/contract,110 resource controls,
29 identity/lifecycle/preview and19 model cases. Full531 integration and exact-source
hosted image/service acceptance remain unproved until that run completes. Retain the
remote head; only Markdown closeout follows it. Parentb4b20f1 hosted39350745638 is
separate and in progress; main stays72c9c17 with its successful39345752803 follow-up.
All local commands have terminated; thirty recorded source containers are independently
absent. Normal Docker is kept running on0044 with erasure/retirement/short-text disabled.
No closure/erasure/DELETE completion or production/academic/device acceptance is inferred.



## Accepted dormant lifecycle source — hosted39350745638

Complete hosted [39350745638](https://github.com/Jotham566/kasoma/actions/runs/39350745638)
is SUCCESS atb4b20f1b0e44d1ae08ae58091f35bb9c060e957f:1,445 unit/contract,
522 integration,35 tooling,22 owned identity/lifecycle checks and123 full browser
executions. All required setup, clean/additive migrations, seed, focused/restricted
login, quality/contracts/build, recovery, dependency/source/image security and service
smoke gates pass. Logical recovery verifies74 tables/692 rows in559ms. Actual stopped-
source PostgreSQL/MinIO restore verifies74/692/one42,084-byte ciphertext in316ms,
with fault/immutable/dormant guards, stripped retirement denied and empty cleanup.
Production RPO/RTO remains false. Prior39346406621 stays failed; this source corrects
only the additive-upgrade test's expected closed_at:null, preserving all old fields.

Accept0045 dormant lifecycle persistence, the structural manifest and denial tests.
No plan/job creation, SQL erasure owner/executor, authorization, permanent closure,
removal or DELETE completion is accepted. Normal review activation stays false.
Coordination94feeab and source ownership752cda1 need their own complete hosted runs;
this acceptance covers neither. Only Markdown closeout follows the verified runtime/
test/Make/workflow tree. Native review images rebuild successfully; make migrate and
container-smoke pass with all eight services healthy on0045. Direct count-only inspection
confirms scope/creation/execution=false, owner/executor absent and zero closed users.
Existing review data/volumes remain; no account-erasure operation is performed.

Native rebuilt API/web image HIGH/CRITICAL scanning also passes before publication.


## Accepted account-processing coordination source — hosted39352281782

Complete hosted [39352281782](https://github.com/Jotham566/kasoma/actions/runs/39352281782)
is SUCCESS at94feeab6e946c2905202da19a0a85952f5b26036:1,471 unit/contract,
531 integration,35 tooling,29 owned identity/lifecycle and19 owned fake-dispatch
checks, plus123 full browsers and every mandatory engineering gate. Logical recovery
verifies74 tables/692 rows in438ms; actual stopped-source PostgreSQL/MinIO restore
verifies74/692/one42,060-byte ciphertext in217ms, with fault/immutable/dormant guards,
stripped retirement denied and empty cleanup. Production RPO/RTO remains false.

Accept ADR-070's compatible SQL-visible shared gate, fresh authority reads and bounded
idle-connection fake-dispatch coordination, alongside the unchanged original HMAC locks.
No permanent closure, erasure authorization/executor or completed DELETE exists. The
future exclusive closure must use nonblocking transaction acquisition and all independent
case/source/hold/export/SQL guards. Provider cancellation after process loss remains
unproved outside the fake lane. Normal review execution stays disabled.

Integrate accepted main2f3031b's Markdown closeout only. Resolve five competing appended
verification sections by preserving both histories; there is no application/test/Make/
workflow change relative to hosted94feeab. Main follow-up39355923737 remains live and
unchanged. Promotion to main and corresponding review rebuild wait for that fixed-head
run; do not cancel it. Source ownership/audit752cda1/4db1cec remain separate candidates.


## Publication of accepted ADR-070 coordination

Main parent2f3031b follow-up [39355923737](https://github.com/Jotham566/kasoma/actions/runs/39355923737)
is terminal SUCCESS. Promote the separately complete hosted39352281782 coordination
source94feeab through prepared Markdown mergee37cd55. Runtime/test/Make/workflow content
remains exactly that verified source; publication closeout adds Markdown only.
Native make containers migrate container-smoke security-containers all pass. All eight
review services are healthy on0045; direct aggregate inspection confirms false scope/
creation/execution, absent erasure owner/executor and zero closed users. No normal review
erasure, retirement, short-text enablement, data/cache/volume cleanup or real inference.

This accepts compatible account processing/fake-dispatch coordination, not SQL erasure
execution. Full reviewed plan/authorization/closure, preservation/removal/retirement,
closed-account support and genuine release gates remain. Source audit4db1cec and disabled
bootstrap3f865e4 are separate pending candidates with fixed live remote heads. Remove
only the merged coordination branch after successful main publication and ancestry proof.


## ADR-061 source ownership reader — local verification

FR-ID-006/BR-010, FR-OPS-003 and NFR-SEC-002/MNT-001: add a closed74-source
relational selection registry and bidirectional ownership-edge checks for the future
versioned plan. K/shared opaque T sources have no account predicate; owned ephemeral
plans remain case-scoped. Unbound OTPs are never attributed by lookup hash. Return
only counts and a keyed streaming fingerprint, with PostgreSQL row digests, ordered
primary keys and xmin versions under a read-only repeatable-read snapshot. Bind the
fold to subject/database/schema; never transfer source bodies, credentials or key lists.
No LIMIT truncates the reader; test above10,000 owned events.

This reference is explicitly NOT semantic clearance or an issued plan. Payload/version
validation, staff/audit classification, exact holds, lifecycle self-write reconciliation,
independent SQL privileges/scope and server authorization/closure remain required.
No route, executor, role, deletion, identity closure or completion is added. A malicious
relation is tested only in a separately created disposable mirror; original guards
and rows are never disabled or rewritten.

Preserve frozen parentb4b20f1 hosted39350745638 and coordination94feeab hosted39352281782
while this separate branch develops. Add a third closed fresh-source cohort for the
reader/corruption cases, keeping existing resource/supervision caps and no caller target.
Initial format failures and a registry check incorrectly treating every T disposition
as shared are corrected; owned temporary plans are explicit. The first mirror fixture
failed its existing revision-session topic constraint; correct the fixture, preserving
all original guards. Earlier failed runs remain failed.

Final local quality/contracts/build,1,476 unit/contract,110 resource controls and all
three owned cohorts pass:29 identity/lifecycle/preview,19 fake dispatch and nine reader
checks (five contract/four native). Tests include10,001 owned events without truncation,
unrelated learner stability, changed private key, immutable counts, cross-owner inputs,
revoked staff roles and original learner reporting after independent staff triage.
The reader always returns semantic_clearance=false. It has no serving consumer.

The first security run reports five B608 findings in SQL templates interpolating only
fixed registry constants. Review UUID parameter binding and psycopg identifier quoting;
add five line-specific B608 exceptions, not a global exclusion. Executable AST equality
is checked before/after annotations. Final format/lint/types/contracts/build and security/
source/dependency checks pass. All nine recorded owned source containers are independently
absent; cleanup reports are empty. The initial independent absence probe falsely rejects
Docker's lowercase no-such-object message; the corrected case-insensitive probe verifies
all nine without removing anything. Full exact-source hosted acceptance remains pending.
No migration, route, dependency, provider, retention or new architectural decision is
introduced. Normal review stays disabled on0044, with eight healthy services.


## Frozen source ownership candidate

Read-only implementation/test/Make source752cda1469f4d824182c00f65afae1367b4bc273
is pushed for complete hosted [39354774163](https://github.com/Jotham566/kasoma/actions/runs/39354774163),
confirmed in progress. Preserve that remote head. Only Markdown closeout follows it.
This adds no semantic clearance, issued plan, SQL capability or account closure.
Parentb4b20f1 hosted39350745638 and coordination94feeab hosted39352281782 remain
independently in progress; neither is accepted from these local reader checks.
Main remains72c9c17 with a healthy eight-service review preview on0044. Next is the
independently owned SQL capability and complete server plan/authorization/closure;
full payload/hold/export-drain checks must precede any actual closure or removal.


## ADR-061 exact audit-source gate — implementation in progress

FR-ID-006/BR-010, FR-OPS-003 and NFR-SEC-002/MNT-001: the native unknown-action
regression fails before the change (one failure/nine passes): another actor's audit
against an owned case is absent from the action-filtered fingerprint. Expand the private
audit scope through frozen typed source UUID identities, including explicit0039 receipt
identity, without matching composite retry keys or opaque hashes. Unknown actions must
change the source version and fail the separate exact classification gate.

Implement the33 explicitly approved ADR-061 action rules and0043/0044 addendum, with
exact owner/staff actor and case/hold/flag/grading-review target bindings and current
EXPORT/DELETE case-kind constraints. Unknown/missing/ambiguous associations or malformed
clocks fail closed; learner original reports remain distinct from independent triage.
No prefix classification, fabricated deadline, SQL role, route, erasure authority or
new retention/architecture decision is introduced. Root/deadline, source/payload integrity,
holds and independent SQL authorization still require their own complete checks.
Initial type errors are corrected; final local and own full hosted verification remain
pending. Preserve all frozen live verification heads and normal review disablement.


## Exact audit gate local verification

Final format/lint/types and1,483 unit/contract pass; three isolated cohorts pass29
identity/lifecycle/preview,19 fake dispatch and16 source checks (six contract/ten native).
Unknown audits against both an owned case and an owned attempt enter the fingerprint
and require review. No composite retry key is used as a target identity. Original
learner flags followed by independent triage classify correctly. Wrong targets, wrong
EXPORT/DELETE kind, missing actors, subject staff reads and future clocks fail closed.
All nine recorded sources, including the failed before-regression run, are independently
absent with empty cleanup. OpenAPI/build and dependency/source/secret security pass;
initial type failures remain failed. No new scanner exception or architecture change.

Parentb4b20f1 complete hosted39350745638 is SUCCESS for dormant0045 only (1,445 unit,
522 integration,123 browser executions and all mandatory gates). Coordination94feeab
and read-only predecessor752cda1 still require their own outcomes. Even a green
predecessor run cannot accept this audit correction; promote the combined reader/audit
source only after its own full hosted acceptance. No source classifier establishes
payload, exact-hold, deadline, SQL-scope or closure/removal clearance. The next complete
ADR-061 slice remains independently restricted SQL plan/authorization/closure, not a
count-only or empty-account erasure substitute. Keep normal review execution disabled.


## Frozen combined audit candidate and accepted parent publication

Runtime/test/Make/workflow source4db1cec65674419bab9a81eeaf4e5da0262f927c is frozen
for complete hosted [39355841664](https://github.com/Jotham566/kasoma/actions/runs/39355841664),
confirmed in progress. Preserve its remote head; only Markdown closeout follows it.
Predecessor752cda1 hosted39354774163 is separate, and cannot accept the correction for
unknown audits demonstrated by the failing before-regression. Source/hold/payload/SQL
capability and account closure/removal/DELETE completion remain unaccepted.

Dormant0045 parentb4b20f1 is accepted by complete hosted39350745638 and published
through main2f3031b4100cbaa3856a1561260d62e9451166a2 after native images/migration/
service smoke and HIGH/CRITICAL scans pass. Its merged local/remote branch is removed
with ancestry proof. Main follow-up39355923737 is confirmed live; do not move main while
that run needs its fixed head. Coordination94feeab hosted39352281782 is still separate
and live. Normal review has eight healthy services on0045, scope/creation/executionfalse,
no erasure owner/executor and zero closed identities. No data/cache/volume sweep.


## Accepted read-only source and audit policy — hosted39355841664

Complete hosted [39355841664](https://github.com/Jotham566/kasoma/actions/runs/39355841664)
is SUCCESS at4db1cec65674419bab9a81eeaf4e5da0262f927c:1,483 unit/contract,
541 integration,35 tooling,29 identity/lifecycle,19 fake dispatch,16 owned-source
checks and123 full browser executions. All setup/migration/seed, focused/restricted
login, quality/contracts/build, dependency/source/image security and service smoke gates
pass. Logical recovery verifies74 tables/692 rows in613ms. Actual stopped-source PG/
MinIO recovery verifies74/692/one42,084-byte ciphertext in325ms, with fault/immutable/
dormant checks and empty cleanup; productionRPO/RTO remains false.

Accept the closed ownership reader and exact33-action audit classifier together, including
rejection of unknown other-actor audit on an owned case/attempt. Predecessor752cda1's
success does not cure its known audit omission; this combined corrected source does.
Source hashes/counts remain read-only with semantic_clearance=false. They are not full
payload/retention/hold/private-catalog clearance, authorization, closure or fulfillment.
The initial unknown-audit regression remains a recorded failure before correction.

Main40aa7d2 follow-up39359937884 is terminal SUCCESS. This merge preserves both
Markdown evidence histories; its executable/test/Make/workflow tree is identical to
hosted-verified4db1cec. New bootstrap3f865e4 and planf645a54 have separate frozen live
heads39359471826/39364234883; do not move or infer acceptance for them. Normal review
remains dormant; remove only ancestry-proven merged source/audit branches after publication.


Native publication checks for the accepted audit/source tree pass: `make containers
migrate container-smoke security-containers`. All eight normal services remain healthy
on0045; no erasure provisioning, activation or account closure is performed. Main40aa7d2
follow-up is terminal success; publication may advance main to this Markdown-only
closeout of hosted-verified4db1cec. Separate live bootstrap/plan heads remain fixed.


## ADR-061 SQL capability work — fresh-source bootstrap in progress

FR-ID-006/BR-010, FR-OPS-003 and NFR-SEC-002/MNT-001: begin the independently
restricted SQL capability slice with an exclusively created source proof, issued before
migrations. Bind exact owned container/label/loopback port and database/schema OIDs,
fake-only profile and process-local issuance/lifetime. Reject configuration-only,
reconstructed, retargeted, expired or already-populated source issuance. Standard test
resource caps and exact cleanup remain; neither normal review data nor existing roles/
schemas/volumes are adopted or removed. Preserve standard browser/test fixture behavior.

The new prescribed make test-erasure-fresh-scope target always creates its own bounded
source; never point it at an existing schema. This implementation is in progress,
not an issued plan, SQL owner/executor, activation, closure, removal or completed first
slice. Continue through independent SQL authority, server plan/authorization, permanent
closure and durable continuation with all source/preservation/export guards. No new
privacy/retention policy or architecture decision is inferred from this bootstrap proof.


## ADR-071 disabled SQL installation — implementation in progress

Record the technical bootstrap decision in ADR-071 under approved ADR-061. An explicit
forward installer only accepts the live registered source proof, rejects existing roles/
crypto/control namespaces and unknown source namespaces, and creates separate NOLOGIN
owner/authorizer/maintenance principals without memberships or elevated flags. It adds
one private16-column shared control table (K), purpose-specific HMAC key and qualified
pgcrypto1.3 namespace; these are additional capability inventory, never learner-owned
rows or a substitute for full source/guard/ACL validation. Normal migrations/startup
never read this installer. Normal review remains dormant and untouched.

A narrowly bound forward state guard records source/role OIDs and nonce only in this
owned source. Creation/execution CHECKs remain false, plans/jobs remain unwritable and
closed_at remains forbidden. The only login entrypoint is minimized disabled readiness;
private initialization/scope functions and source/control tables are not granted to
those logins. PostgreSQL-side fixed error handlers protect dynamic-login failures and
rejected private-key row validation from uncaught secret-bearing SQL details. No audit
suppression, trigger-disable flag, arbitrary SQL/cutoff or general DELETE grant exists.

Initial actual-login/source checks pass7 cases after format fixes. Add later-failure
rollback and PostgreSQL log-boundary proof, standard HMAC comparison, unknown-namespace
and broader regression checks before acceptance. The SQL authorization/closure slice
is still incomplete: no server plan, authorization, permanent closure, restartable job,
full preservation/removal/retirement or completed DELETE exists. Keep this branch in
progress until those requirements are implemented and independently verified.


## ADR-071 bootstrap local checkpoint

Final local format/lint/types (222 sources),1,487 unit/contract,110 resource controls,
11 fresh-scope/SQL cases, OpenAPI/build and dependency/source/secret security pass.
Actual logins prove only minimized disabled readiness, no source/control reads or
protected writes, no owner role assumption, private function denial and temporary
search-path shadowing resistance. Owner LOGIN drift and crypto-namespace rename make
readiness fail. Replays, pre-existing role adoption and unknown namespaces fail.
The complete installed inventory is75 tables/561 columns; ordinary public remains74/545.

A late invalid-key initialization rolls back roles, extension/namespaces and source
handoff. The corrected log probe captures both Docker streams, observes the fixed
server error and finds neither the rejected key marker (text/hex) nor either generated
login credential. The earlier stdout-only probe was insufficient evidence; the first
corrected fixture failed because its credential callback was not wired. Earlier format,
duplicate-basename and invalid-settings fixture failures stay recorded. No scanner
exception is added; the privileged modules are explicitly included in make security.

All123 browser executions pass after the shared factory extension (108 standard,
12 short-text,three configuration), with12 recorded browser source containers
independently absent and empty cleanup. Each native fresh-source/capability context
also independently checks exact container absence. The legacy short-text runner keeps
its existing schema scope. No existing schema/role, SDK/cache, volume or image cleanup.
Main review remains eight healthy services on0045 with erasure/retirement disabled.

This is disabled bootstrap engineering evidence, not completed FR-ID-006 or first-slice
acceptance. Full source/private-catalog/ACL integrity, payload and exact-hold checks,
server plan/authorization/closure, durable continuation, preservation/removal/retirement
and erasure recovery remain required. No ordinary authorizer source CRUD is granted yet.
No plan/job is created, closed_at is unchanged and no DELETE request is completed.
Full exact-source hosted acceptance remains pending; do not infer it from parent runs.


## Frozen ADR-071 disabled-bootstrap candidate

Implementation/test/Make/workflow source3f865e440dae523b7c415efd0c6838b012d76435
is pushed for complete hosted [39359471826](https://github.com/Jotham566/kasoma/actions/runs/39359471826),
confirmed in progress. Preserve that remote head; only Markdown closeout follows it.
Local11 fresh-source/SQL,110 resource,1,487 unit/contract and123 browser executions
pass alongside quality/contracts/build/security. Its full548 integration and exact-source
hosted/image/service acceptance remain pending. No normal-review erasure is enabled.

The prepared coordination acceptancee37cd55 changes Markdown only beyond verified94feeab
and integrates accepted main2f3031b. Main follow-up39355923737 remains separately live;
do not move its head. Source ownership752cda1 and combined audit4db1cec have their own
live runs; they cannot accept this bootstrap source. Full SQL server plan/authorization,
permanent closure, durable continuation and complete ADR-061 fulfillment remain work.


## Accepted disabled fresh-source bootstrap — hosted39359471826

Complete hosted [39359471826](https://github.com/Jotham566/kasoma/actions/runs/39359471826)
is SUCCESS at3f865e440dae523b7c415efd0c6838b012d76435:1,487 unit/contract,
548 integration,35 tooling,29 identity/lifecycle,19 fake dispatch,16 source checks
and123 browser executions. All required setup/migration/seed, focused/restricted-login,
quality/contracts/build, dependency/source/image security and service smoke gates pass.
Recovery74/692 passes571ms logical and330ms stopped-source PG/MinIO with one42,084-byte
ciphertext, immutable/fault/dormant checks and empty cleanup. ProductionRPO/RTO remains
false, and baseline recovery is not erasure checkpoint recovery.

Accept only the disabled ADR-071 fresh-source capability v1: in-process registered
pre-migration source proof, exclusive NOLOGIN owner and separate private authorizer/
maintenance logins, qualified bundled pgcrypto1.3 HMAC, immutable private control and
one-time fresh-source identity handoff. It never provisions normal migrations/startup
or review, and readiness remains false. No plan/job/closure/DELETE completion is accepted
from this source. Full catalog/ACL/source/payload/hold validation remains required.
The later v2 planf645a54 and staff coordination have their own pending verification.

This prepared merge preserves both Markdown evidence histories; executable/test/Make/
workflow files equal hosted-verified3f865e4. Main600db71 and its follow-up39364455335
remain live and fixed. Do not advance main, remove the unmerged bootstrap branch, or
infer acceptance for newer work until the main follow-up is terminal successful.


Native prepared-bootstrap publication checks pass: `make containers migrate
container-smoke security-containers`. All eight normal review services are healthy
on0045; the ordinary source remains ineligible/dormant with no erasure provisioning.
Main600db71 follow-up39364455335 is still live; preserve main. New plan/staff/private
gate work has separate frozen candidates and cannot inherit this bootstrap acceptance.
The prepared merge remains only Markdown beyond complete hosted-verified3f865e4.


## Disabled bootstrap publication after parent acceptance

Main 600db71 follow-up 39364455335 is terminal SUCCESS. Disabled bootstrap
3f865e4 passes complete own hosted 39359471826: 1,487 unit/contract, 548 integration,
35 tooling and 123 full browser executions, plus every focused/setup/migration/seed/
restricted-role/quality/contracts/build/security/image/service gate. Recovery verifies
74 tables/692 rows logically in 571 ms and one 42,084-byte private ciphertext with
stopped source PostgreSQL/MinIO in 330 ms; fault/immutable/dormant guards and empty
cleanup pass. Production RPO/RTO remains false.

Only Markdown differs from that verified runtime/test/Make/workflow tree. Native
image rebuild/migration/service smoke and image security pass for the prepared
publication. All eight normal review services remain healthy on 0045; no private
erasure capability is installed there, no identity closed and no DELETE completed.
Later plan, staff, private-gate and catalog candidates retain separate exact-source
acceptance; bootstrap acceptance does not clear them or full ADR-061 execution.


## ADR-072 server plan/authority path — implementation in progress

FR-ID-006/BR-010, FR-OPS-003 and NFR-SEC-002/MNT-001: extend the explicit fresh-source
recipe to private capability v2, leaving ordinary0045 migrations and normal review
unchanged. The separate authorizer is EXECUTE-only; it receives no ordinary API source
CRUD. SQL checks its actual principal, server-observed source binding, current recent
ADMIN session and independent current claimant of a pending verified DELETE case.
The API must end normal authentication before the private call, then SQL revalidates.
ADR-072 records this delegation and future atomic authorization/barrier decision.

Compile fixed manifest/ownership SQL at installation, with qualified names and UUID
parameters. Issue database-clock plans and exact read audits before an uncapped keyed
source fold. Normalize only this plan's self-referential version. Keep creation and
execution false and return explicit disabled/incomplete blockers; this is not full
source/preservation/hold clearance or first-slice completion. Only maintenance expires
plans, at most100 removals from200 candidates, using database time and fixed cleanup.
The trusted installer may choose a bounded1–600-second plan lifetime (default600);
no API/maintenance caller supplies a cutoff or rewrites an existing clock.

Exact new erasure_plan_read and erasure_plan_expiry_batch action names are classified
under ADR-061's approved security/access/batch rule, without wildcard acceptance or a
new retention permission. Native SQL, server/API, stale-source/clock/role/ownership,
large-history and full own-source checks remain in progress. Job creation, actual
closure and erasure/removal/retirement are still required implementation work.


## ADR-072 v2 local verification before hosted acceptance

The private plan/API candidate passes `make format lint test-erasure-plans
 test-erasure-fresh-scope test-erasure-identity-isolated test-unit openapi-check build
 security security-source`:18 plan/compiler/API cases,11 fresh-scope/SQL cases,
29 identity/lifecycle,19 fake dispatch,16 source checks and1,490 unit/contract tests.
Actual authorizer/maintenance/ordinary logins enforce separation; a revoked ADMIN
between ordinary authentication and private SQL is refused. Native tests verify
10,001-event nontruncation, self-seal reconciliation, unrelated-subject stability,
server clocks and100/10/0 expiry batches over110 plans. Trusted lifetime input is
strictly1–600 seconds; maintenance/API cannot choose a cleanup clock. The first positive
run failed permission checks despite nine passing denials; narrow NOLOGIN-owner ID
UPDATE grants enable PostgreSQL row locks. That earlier run remains a failure.

Full local browsers are running. Exact-source hosted integration/browser/image/service
acceptance remains pending. No job, closure or DELETE completion is implemented; source
semantic/payload/hold/catalog clearance, atomic authorization/barrier and complete durable
fulfillment remain required. Normal review is healthy and dormant on main40aa7d2.


## Staff preservation/triage coordination — implementation in progress

FR-ID-006/BR-010, FR-GRD-009/FR-CNT-006, FR-OPS-003 and NFR-SEC-002/MNT-001:
ADR-070's staff addendum requires subject shared coordination before case/flag row locks.
Use immutable server-owned case user_id/flag reporter_id after current staff authority;
re-read the resource under its existing row/ownership/revision checks. Cover case claim/preview,
legal-hold access (including channel capture), flag detail and triage/replay audit.
No API/schema/retention permission or closure capability is added. Concurrency regression
and full acceptance remain pending; the existing dormant normal review is not an erasure
execution target. Source/audit main600db71 is separately hosted-verified at4db1cec;
main follow-up39364455335 is live. Preserve bootstrap3f865e4 and planf645a54 live heads.


Plan candidatef645a54 passes all123 local browser executions across Chromium/Firefox/
WebKit, including encrypted fake short text and operations configuration. All12 recorded
owned browser containers are independently absent. Runtime staff source changes began
only after that browser command exited0. Exact-source hosted39364234883 remains live;
this local result is not hosted acceptance or account erasure completion.

Disabled-bootstrap3f865e4 passes complete hosted39359471826:1,487 unit/contract,
548 integration,35 tooling and123 browsers plus setup/migration/seed, focused/restricted
login, quality/contracts/build, dependency/source/image security and service smoke gates.
Recovery74/692 passes571ms logical and330ms stopped-source PG/MinIO with one42,084-byte
ciphertext, immutable/fault/dormant guards and empty cleanup. ProductionRPO/RTO stays
false; baseline restoration is not erasure checkpoint recovery. Only its disabled fresh
bootstrap is accepted, not planf645a54 or new staff coordination. Preserve main600db71
while follow-up39364455335 is live; later promote bootstrap only with its exact verified
runtime/test/Make/workflow tree and explicit documentation closeout.

The first staff regression confirms3 bypasses (hold create/release/case claim), with
28 passing cases and one disposable fixture STORAGE_EXHAUSTED error at512MiB. That run
remains failed and its resource is cleaned. Move the six staff cases into a fourth
closed independently owned cohort rather than enlarge tmpfs or touch review volumes.
Staff coordination is now implemented before resource row locks; green verification
is running and does not yet establish acceptance. No account is closed or erased.


## Staff gate local candidate verification

Six real-PostgreSQL concurrency cases pass in their own fresh512MiB source: hold
creation/release, case claim, audited deletion preview, flag detail and triage wait at
the subject shared gate while an independent transaction can lock the target row
NOWAIT. Unrelated subjects remain independent. Four exact owned source containers are
independently absent after the first green29/19/16/6 cohort run. That run passes1,490
unit/contract tests, contracts/build/security/source checks; final format/lint/types
also pass after adding preview coordination. A final unchanged-source owned-cohort run
and full browser regression are still running; full570 integration and exact hosted/
image/service acceptance remain pending. No grant, migration, API contract, retention
permission, account closure or erasure is added by this staff amendment.

Record the original3 regression bypass failures and disposable STORAGE_EXHAUSTED setup
error as failures, not passes. Splitting staff tests into a fourth closed cohort keeps
source RAM bounded and leaves normal Docker volumes untouched. The normal review has
eight healthy services on0045 with erasure/retirement/normal short text disabled.
The exact disabled-bootstrap source passes hosted39359471826; its prepared main merge
7c621de is Markdown only beyond3f865e4 and waits for live main39364455335. New plan
candidatef645a54 hosted39364234883 remains separate. Full approved ADR-061 erasure and
external acceptance gates remain unfinished; this is prerequisite work only.


## Private plan processing coordination — implementation in progress

FR-ID-006/BR-010, FR-OPS-003 and NFR-SEC-002/MNT-001: extend the fresh isolated
recipe to private capability v3 under the ADR-070/072 amendments. After principal,
source and current ADMIN authority checks, derive the subject from its immutable case,
try its shared transaction gate using the pinned public namespace OID, then lock/recheck
case/review/subject. Busy calls must write no plan or audit. The subject row lock must
reject a REPEATABLE READ snapshot predating a committed subject change. The API verifies
exact private readiness version before issuing; an older credential/namespace is not
silently adopted. The v2 fingerprint algorithm/public0045 remain unchanged. Normal
review remains dormant; there is still no authorization/job/closure/removal/completion.

The added busy regression fails before correction (one failure/18 passes) with exact
owned cleanup. Verification of the new v3 recipe and stale-snapshot regression is pending.
Staff41c6eaa's unchanged runtime passes final29/19/16/6 owned checks and all123 local
browsers; its separate hosted39365013049 remains live. Preserve all live remote heads.


## Private v3 plan gate — local verification candidate

`make format lint test-erasure-plans test-erasure-fresh-scope test-unit openapi-check
build security security-source` passes:21 plan/compiler/API cases,11 fresh-source/SQL
checks and1,490 unit/contract tests. Strengthened contention rerun passes all21 cases:
an independently held case row cannot delay the fixed busy-gate denial; successful
plans hold the correct public-subject gate until commit, unrelated subjects proceed,
and a changed subject row after snapshot raises40001 before any plan/read audit.
The API refuses an actual fresh historical v2 recipe without creating a plan. All
recorded owned native source containers from both runs are independently absent.

The initial added busy regression stays failed (one failure/18 passes before repair).
An initial formatting-only run also failed two long test SQL literals; split literals
and final format/lint/types pass. No broader scanner exclusion was introduced.
Full local browser regression is running; full573 integration and exact-source hosted/
image/service acceptance remain pending. Keep existing remote candidates fixed. Normal
review remains dormant and healthy on0045. Full catalog/ACL/payload/hold/export clearance,
exact richer preservation, permanent SQL write barriers, atomic authorization/closure,
durable bounded removal/verification/retirement and quarantined erasure recovery remain
required. No case completion or full MVP acceptance is inferred from these prerequisites.


Private gate candidate81f1d843e6e7d3fdbfd342f0626a883981bf9aef is pushed for complete
hosted39365821234. Preserve that remote head. Native exact-container cleanup evidence
comes from assertions inside each fresh scope/source context after its cleanup, using
independent Docker inventory. Successful pytest captures those container logs: the
separate quiet-log scan found no IDs and provides no additional cleanup evidence.
The21-case strengthened gate run and11-case bootstrap run pass; local browsers remain
in progress. Full573 hosted integration/image/service acceptance is pending.

Main600db71 follow-up39364455335 remains live. Prepared accepted-bootstrapf9cd1fb is
only Markdown beyond hosted-verified3f865e4 and has passing native image/migration/
service/security checks; keep main fixed while its run is live. Staff41c6eaa passes
final29/19/16/6 local owned cohorts and123 local browsers, with four wrapper-source
and twelve browser source IDs independently confirmed absent; its hosted39365013049
and planf645a54 hosted39364234883 stay separate. All eight normal review services are
healthy on0045. No erasure/retirement/normal short-text activation or case completion.


## Private v3 full local browser closeout

Source81f1d84 passes `make e2e`:123 executions across Chromium/Firefox/WebKit,
including the fake encrypted short-text and operations configuration journeys. The
command exits0. All12 recorded exact owned browser containers are independently absent.
This complements21 plan/compiler/API,11 bootstrap and1,490 unit/contract passes, final
lint/types/format, contracts/build and dependency/source security. It does not replace
full573 integration, exact hosted39365821234, image/service acceptance or erasure recovery.

Only Markdown closeout follows the frozen81f1d84 runtime/test/Make/workflow tree; do not
move its live remote head. Main600db71 follow-up39364455335, planf645a54 hosted39364234883
and staff41c6eaa hosted39365013049 remain live and separate. Accepted disabled bootstrap
3f865e4 is prepared atf9cd1fb with native checks; main stays fixed during its follow-up.
All eight normal review services remain healthy on0045. No ordinary review erasure is
provisioned or activated, no account closed and no DELETE completed. Next implement
complete private source-catalog/ACL and ownership/payload clearance, exact preservation
coverage and permanent closed-write/credential/export gates before atomic authorization/
closure, bounded durable removal and quarantined checkpoint recovery. Academic/privacy/
provider/physical-device/production approval remains genuine external acceptance work.


## ADR-073 frozen pre-install catalog — implementation in progress

FR-ID-006/BR-010, FR-OPS-003 and NFR-SEC-002/MNT-001: pin32 technical catalog categories
from independently created fake-only sources migrated to0045. Compare behavior/privilege
metadata before creating any erasure principal; the existing shape check cannot detect
body-only trigger/function drift. The new regression demonstrates old bootstrap accepting
a changed closure guard (one failed/six passed). The read-only verifier already rejects
that drift; connect it to privileged installation before any role/schema/key mutation.

Counts/SHA256 are computed within PG, without learner-row reads or live body transfer.
The four approved ADR-060 owner-dependent code templates are generated only from fresh
migrations. Render their checked expected code with the exact database/public owner;
never normalize live body literals or approve arbitrary role prefixes. The artifact also
binds the ordinary migration helper/source files. Separate fresh resources reproduce
identical metadata despite different database names; transient connection search path,
timezone and timeout settings are restored. Query budgets are5s/100ms; no LIMIT truncates
the catalog reader. Physical statistics/storage IDs and passwords are excluded.

Fresh private capability v4 records the stricter installation provenance, reusing the v3
SQL plan gate. The API refuses legacy v2/v3 readiness; no old source is adopted. Public
0045 stays74 tables/545 columns; installed private scope stays75/561. No erasure execution
or new preservation/retention permission. Complete installed-catalog/ACL, SQL ownership/
payload/hold/export validation, exact richer preservation, permanent closed-write gates,
atomic authorization/closure and bounded durable fulfillment remain mandatory.

Broader strict type checking finds three existing trusted-script errors: psycopg SQL
composition inference and an untyped role-OID map. Explicit composable/map types preserve
behavior. Initial formatting failures are recorded; native drift/role/API/bootstrap,
full unit/browser/security and own hosted verification remain pending. Keep main600db71
and all live earlier candidate heads fixed. Normal Docker review remains healthy/dormant.


ADR-073 raw safety stage: compare nine raw code/type and stored-expression
metadata categories before any PostgreSQL expression/definition deparser. This rejects
changed type I/O routines and unknown raw expressions before they could be invoked by
constant formatting. Render only the checked expected four dynamic code templates;
never normalize live code. Both stages return only counts/digests. Savepoint rollback
restores local settings on mismatch/query failure; success restores them explicitly.
The explicit fresh-migration generator can create the initial raw expectation, while
the runtime verifier must load it from the versioned artifact. The32 full metadata
categories are supplemented by these nine safety categories, not silently redefined.
Pinned PostgreSQL/vector core and the privileged creator/host remain trusted; this does
not claim protection from a hostile administrator controlling the engine or artifact.


## ADR-073 final native catalog boundary

The final nine-raw/32-full-category candidate passes25 catalog,22 plan and11
fresh-scope/bootstrap cases,1,495 unit/contract and35 tooling checks, lint/type checks
(228 Python sources), baseline reproduction, generated contracts, build and dependency/
source security. The initial subprocess scan failure is corrected using the existing
bounded command helper without scanner suppression. Full browser/own hosted acceptance
remains pending. The interrupted earlier run remains unaccepted. The owner-authorized
exact orphan removal is independently confirmed; all eight review services are healthy
and host-native Ollama connectivity passes without inference. See the
[catalog verification record](docs/implementation/E8_ERASURE_CATALOG_VERIFICATION.md) for exact evidence
and remaining installed-catalog/SQL/hold/payload/closure/removal/recovery gaps.


Final ADR-073 local browser evidence: make e2e passes 123 executions (108 standard,
12 short-text and three configuration). Twelve exact recorded owned source containers
have empty cleanup reports and independent full-ID absence. Full hosted 39371164944
is live at frozen 854afaa; only Markdown follows. Main 0053a7b now publishes the
verified disabled bootstrap, whose merged branches are removed. V3 plan/staff source
81f1d84 independently passes complete hosted 39365821234 and has a prepared publication;
main follow-up 39371028143 remains live. None of these accepts catalog hosted results,
erasure execution, physical devices or full release. See the catalog verification record.


## ADR-074 closed credential intake/dispatch — implementation candidate

FR-ID-001/002/005/006, BR-010, NFR-SEC-002/MNT-001: coordinate current retained LOGIN binding
before rates/identifier serialization, recheck that exact binding and closure, and
return generic acceptance without a code/provider call for a closed identity. A
changed binding requires fresh issuance instead of a late account-lock inversion.
Bound dispatch holds only the existing idle session-shared subject gate and rechecks
before the provider, with no row/HMAC/open transaction across send. Suppression and
gate failure do not masquerade as provider failures; cleanup targets only this
invocation's exact newly created challenge. Closed LOGIN rejects before challenge
consumption; closed refresh rejects before unbounded family mutation. Ordinary
nonclosed reuse protection remains. See ADR-074 for protocol and fixture limitations.

The first four native cases produce three failures/one pass on the unchanged parent:
closed email/phone still dispatch and closed rotated refresh rewrites its family.
After the change those four pass. The expanded matrix, full local/own hosted checks
remain pending. Synthetic future-state fixtures restore the exact closure trigger
before consumer checks; they do not prove a closure executor or authorization. No
erasure is activated, no DELETE completed, no real data or normal review changed.
Full installed catalog/SQL/payload/hold/export validation, unbound ten-minute drain,
permanent write guards, durable fulfillment and checkpoint recovery remain required.
Catalog remote 854afaa stays fixed for live 39371164944; main 0053a7b follow-up
39371028143 remains live. V3 plan publication is prepared separately.


ADR-074 correction evidence: the one-connection case fails before gate-connection reuse
(17 pass/one failure). A separate broad identity run fails the unchanged pre0045
fixture on deferred closed_at access (28 pass/one failure). ACTIVE consumers now use
the existing immutable closed-implies-DISABLED SQL invariant; non-ACTIVE closure
checks do not gain a missing-column fallback. The existing None-valued model gate
port is preserved while OTP rechecks reuse the same owned connection. All18 native
credential cases now pass; full broader/browser/own hosted gates remain pending.
See the closed credential verification record for failure history and fixture limits.


ADR-074 final local gates pass: 18 closed-consumer/dispatch cases, 29 identity/lifecycle,
19 model dispatch, 16 source ownership and six staff cases, one OTP observation API
case, 1,495 unit/contract, 35 tooling and 123 browser executions, plus lint/types
(228 Python sources), unchanged generated contracts, build and dependency/source
security. The unchanged populated0044 upgrade passes. Twelve exact browser IDs and
nine captured native IDs are independently absent; final native contexts also assert
exact cleanup. See E8_CLOSED_CREDENTIAL_VERIFICATION.md for retained failures, fixture
limits and the pending LINK/GUARDIAN dispatch race. Full own hosted/image/service/
recovery acceptance remains pending; no erasure or DELETE completion is enabled.


## Frozen closed LOGIN candidate

Exact source 4e5b2abc0b11551acd5cab6a163e17ec2edc39fc is pushed on
codex/erasure-credential-guards for its own live full hosted 39373055520. Keep that
remote head fixed; only Markdown closeout follows its runtime/test/Make/workflow tree.
All local engineering and 123 browser checks pass as recorded above; full hosted
612-integration/image/service/recovery acceptance remains pending. Parent catalog
854afaa/39371164944 and main 0053a7b/39371028143 are separately live, not accepted
by this push. The prepared verified v3 publication remains at 7c729f2.

Normal Docker remains eight healthy services on0045 with false activation, no
erasure principals and zero closed identities. Host-native Ollama connectivity
passes without inference. LINK/GUARDIAN post-authentication dispatch races are the
next credential slice, before full installed SQL/ACL/payload/preservation/export
clearance and real atomic closure, bounded removal and checkpoint recovery. No
account-erasure, physical-device or external academic/privacy/provider/release
acceptance is inferred.


## ADR-075 LINK/GUARDIAN dispatch — implementation candidate

FR-ID-001/002/003/005/006, BR-010 and NFR-SEC-002/MNT-001: extend the credential
barrier to current actor and bound recipient. Coordinate the recipient before rate/
identifier work with a shared gate, without acquiring a second account HMAC lock.
One owned connection holds at most two sorted/deduplicated session-shared gates; a
fresh short transaction rechecks recent actor authentication and exact binding before
send. Commit before provider I/O. Partial/uncertain acquisition or release invalidates
the connection, preserving the existing model gateway port and one-connection behavior.

Only the invocation's exact pending new challenge can be cleaned up under its expected
actor binding. Actor closure leaves the original source/clock for the restricted
lifecycle/expiry; consumed evidence is never discarded. No hash sweep or ownership/
retention permission is inferred. The unchanged-parent regression gives eight failures/
11 passes; the first correction passes19 and the expanded matrix passes40 plus18
existing credential cases. Recency and both binding-change stages, broader engineering/
browser and own complete hosted acceptance remain in verification. No account closure,
DELETE completion, normal review activation or external release clearance is enabled.
Parent 4e5b2ab/39373055520, catalog854afaa/39371164944 and main0053a7b/39371028143
remain separate live sources; preserve their remote heads.


ADR-075 final local gates pass: 44 linked-dispatch controls (17 contract/27 native),
18 existing credential cases, 29 identity/lifecycle, 19 model, 16 source, six staff,
one OTP API case, 1,501 unit/contract, 35 tooling and 123 browsers, plus lint/types
(228 Python sources), contracts/build and dependency/source security. Twelve exact
browser and12 captured native IDs are independently absent; final native contexts
also assert their own exact cleanup. Initial eight failures remain retained. See
E8_LINKED_DISPATCH_VERIFICATION.md. Own complete hosted/image/service/recovery
acceptance remains pending; guardian consumption, staff revocation and full erasure
SQL/preservation/checkpoint controls remain required before any activation.
