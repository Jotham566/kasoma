# Requirements Traceability

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
[readiness](E8_ERASURE_LIFECYCLE_READINESS.md).

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
See [readiness](E8_OPERATIONS_CONFIGURATION_READINESS.md).

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
[Evidence](PROVIDER_RECOVERY_DECISION_EVIDENCE.md).


## Older/diagnostic history load - candidate

NFR-PERF-001/002,SCL-001 and FR-DIAG/MST: ADR-066 adds a fixed temporal fixture
profile without changing application/engine behavior or thresholds. Independent
historical clocks and normal OTP build completed diagnostics and old/recent evidence;
current credentials are issued only after preparation. Local quality/contracts/build,1,253 unit/contract,35 tooling,69 focused controls
and203 typed source files pass; dependency/source security checks pass. The first
full-size temporal measurement passes; original/recent rechecks and own hosted
verification remain pending.
[Verification](E9_TEMPORAL_HISTORY_LOAD_VERIFICATION.md). First native profile PASSES:35000 grades,
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
[Verification](E9_OBJECT_RECOVERY_VERIFICATION.md). Source29f1ddc is pushed for own
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
[Verification](E8_METRIC_LOSS_VERIFICATION.md).


## Historical metric-loss candidate notes (superseded by verified result above)

FR-OPS-002, NFR-OBS-001/SEC-002/MNT-001: two actual SDK/Redis regressions reproduce
fresh zero after a lost nonempty export. ADR-064 extends the existing finite
uncertainty marker to current request/model readers, preserving payloads, scopes,
expiry and provider behavior. Local checks pass: 1,180 unit/contract, 35 tooling, 13 focused loss,
51 request, 43 model, 35 OTP/identity, 24 operations and six browser executions;
quality/contracts/build and security/images/service smoke pass. Own full hosted
acceptance remains pending. No production, billing, complete ledger or mixed-reader acceptance.
[Verification](E8_METRIC_LOSS_VERIFICATION.md). Source b5557a3 is pushed for own
full hosted39308594889, in progress. OTP parent ceee401 is now fully verified and published on main557f90f;
its merged branch is removed locally/remotely. Metric-loss remote b5557a3 stays unchanged.

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
[Detailed verification](E8_OTP_OBSERVATIONS_VERIFICATION.md).


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
[Exact scope and evidence](E8_OTP_OBSERVATIONS_VERIFICATION.md).

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
[Exact scope and evidence](E6_PRACTICE_ACTIVITY_VERIFICATION.md). No timeouts, retries or assertions change.

## Recovery role ownership correction - candidate

NFR-REL-002, NFR-SEC-002 and NFR-MNT-001: [verification](E9_RECOVERY_ROLE_OWNERSHIP_VERIFICATION.md)
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

FR-CNT-005, FR-DIAG-003 and NFR-MNT-001: the [source review register](ACADEMIC_SOURCE_REVIEW_REGISTER.md)
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
[Verification](E6_PRACTICE_ACTIVITY_VERIFICATION.md) tracks expanded/backend/browser/hosted acceptance;
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
[Verification](E9_FRESH_SESSION_RESPONSE_VERIFICATION.md) records both passing native profiles (START p95 408.061/422.913ms),
image/service checks and source-pinned aggregate reports. Complete hosted 39286019222 at 58d598e passes 1,130 unit/contract, 483 integration,
35 tooling and 111 browser executions plus all focused/engineering gates. Recovery
verifies 69 tables/686 rows in 477ms. Only documentation/aggregate closeout follows
that verified runtime/test/Make tree. No claimed p95-variance fix or ADR-061 implementation.

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

## Current publication boundary

Source `e33ec69` passes111 local browser executions, nine focused assessment cases,
quality/security/image/service checks and runs in healthy Docker on0042 with retirement
false. Its backend tree is unchanged from the1,112-unit/465-integration/35-tooling
verified tree. [Layout evidence](E3_REVIEW_ACTION_STABILITY_VERIFICATION.md) records
the red/green47.421875-pixel regression. Hosted 39255125288 starts no steps because
GitHub reports an account payment/spending-capacity problem. Owner action is requested
once; complete hosted acceptance/main promotion remain pending, with no gate waiver.
The [operations evidence](E8_EXPORT_RETIREMENT_OPERATIONS_VERIFICATION.md) retains both
earlier browser failures. No full FR-ID-006/BR-010 or release acceptance is inferred.

## Active synthetic retirement operations candidate

FR-ID-006 / FR-OPS-002/003 / BR-010 / NFR-SEC-002 / NFR-MNT-001 / NFR-ACC-001:
[private executor operations evidence](E8_EXPORT_RETIREMENT_OPERATIONS_VERIFICATION.md)
maps separate credential provisioning, restricted authentication, parameter-free queue,
default-off scheduler, finite count-only observations, ADMIN health and responsive
read-only UI to runtime, integration, contract and browser checks. Migration 0042 is
additive. Local full verification passes 1,112 unit/contract, 465 integration,
35 tooling and 108 browser executions, plus recovery/security/image/service checks.
Exact source `94b40a6` fails hosted 39243195783 in one Chromium channel interception
socket reset, after all 465 hosted integration and 1,112 unit/contract cases pass.
The FR-WA-001/004/006 / NFR-MNT-001 / NFR-SEC-002 correction adds guarded single-reset
transport handling, private failure diagnostics and exact committed-code/key assertions.
Corrected `b6aea35` passes 12 transport controls and the full local 108-execution
browser matrix. Hosted 39249423592 passes backend/transport gates but fails a WebKit
resumed-practice transition after79 ordinary passes. NFR-ACC-001 / FR-REV-005 /
FR-GRD-006 / NFR-MNT-001: [stable review-action evidence](E3_REVIEW_ACTION_STABILITY_VERIFICATION.md)
records a deterministic47.421875-pixel red regression and nine green focused cases
with review hints below actions. Full hosted acceptance/main promotion remain pending. No review purge or account erasure.

## Verified bounded synthetic completed-EXPORT kernel

FR-ID-006 / FR-OPS-003 / BR-010 / NFR-SEC-002 / NFR-MNT-001:
[SQL retirement evidence](E8_EXPORT_RETIREMENT_VERIFICATION.md) records approved
ADR-060's exact four-table due/hold policy, actual EXECUTE-only LOGIN boundary,
default-off isolated scope, fair 100/200 bounds and atomic minimized audit.
Complete hosted [39234377840](https://github.com/Jotham566/kasoma/actions/runs/39234377840)
passes at `e5d3d98`: 1,096 unit/contract, 456 integration, 35 tooling, 108 browser
executions and complete role/recovery/security/image/service gates. Hosted recovery
verifies 69 tables/686 rows in 713 ms and refuses stripped-owner execution.
[Exact holds](E8_EXPORT_EVIDENCE_HOLDS_VERIFICATION.md) separately pass complete
hosted 39232307831 at `be2735e` (425 integration); the prior recovery-helper failure
is corrected without relaxing tests. The later local full SQL run is interrupted,
not accepted as a pass. Executor configuration/scheduling/health, other lifecycle
classes and external release gates remain pending. No review-stack purge, real-data
processing or account erasure is authorized or enabled.

## Verified profile presentation correction

FR-ID-001/005 / NFR-ACC-001 / NFR-MNT-001:
[reverification visibility evidence](E1_CONTACT_REVERIFY_VISIBILITY_VERIFICATION.md)
records the reproduced unconditional signed-out action, a profile-bound rendering
condition and retained authenticated handler. The real-API regression fails before
the correction; lint/types/build pass afterward. All nine corrected three-engine
identity cases, 1,092 unit/contract, 35 tooling, contracts and security pass locally.
Public screenshot evidence and the rebuilt Docker web preview are verified; all
eight services are healthy. Complete hosted 39222489376 passes at `44ae9ad`,
including 415 integration, 108 browser executions and full role/recovery/security/
image/service checks.
No new permission, authentication rule, API or architectural decision.

## Verified independent provider fault isolation

FR-GRD-003/004/005 / FR-MST-001/004/005 / NFR-SEC-002 / NFR-MNT-001:
[provider isolation evidence](E9_PROVIDER_FAULT_ISOLATION_VERIFICATION.md) covers
50 scheduled owned reads before releasing one stalled fake model call, followed by
single-dispatch neutral timeout/failure/fallback without grade/mastery evidence.
All three corrected focused cases, 1,092 unit/contract, 35 tooling, lint/types/contracts
and security pass. Complete hosted 39220793602 passes at `8a938dd`, including
415 integration, 108 browser executions and full recovery/role/security/image checks.
This supports resilience testing, not NFR-REL-001 availability or full provider-load
acceptance. No runtime policy, architecture, real inference or enablement change.

## Current verified load increment

NFR-PERF-001/002 / NFR-SCL-001 / FR-MST-004/005 / NFR-MNT-001:
[history/mixed load evidence](E9_HISTORY_MIXED_LOAD_VERIFICATION.md) defines a
50-prior-answer synthetic history profile, varied trajectories and numeric timed
submissions under unchanged operation/format latency gates. All 37 harness cases,
1,092 unit/contract, lint/types/contracts and security pass. Initial history setup
fails before timing with successful cleanup; the refresh correction passes at full
size in the final-source native result recorded below. Complete hosted
[39217860618](https://github.com/Jotham566/kasoma/actions/runs/39217860618) passes at
`6b06c53`: 1,092 unit/contract, 412 integration, 35 tooling, 108 browser executions
and full UI/transport/role/recovery/security/image/service checks.
No runtime, retention, provider or academic enablement changes.
Final fixture generation guarantees both formats with 144 items per subject; the
earlier 293-item candidate correctly fails for missing numeric delivery despite zero
HTTP errors and successful cleanup. `6b06c53` passes the native profile with 7,000 HTTP
requests, zero errors, 1,250 answers per format, 27,500 total grades and successful
cleanup. START p95 432.085 ms, numeric-answer p95 27.778 ms and progress p95 17.079 ms
pass unchanged gates. This closes only this recent-history mixed objective profile;
the sequential original-baseline recheck also passes 7,000 requests with zero errors,
START p95 421.751 ms and successful cleanup. Full performance and external release
acceptance remain pending. Startup p99 remains a risk. Documentation/aggregate-report
closeout preserves the exact verified code/test/Makefile/workflow tree.
Publication through main `6ebdf71` is verified and the merged load branch is removed
locally/remotely. Independent provider/UI candidate acceptance remains separate.
The local runbook and testing specification document both optional isolated profiles
and their unchanged thresholds; documenting the command grants no new acceptance.

## Approved synthetic retention boundary — implementation in progress

FR-ID-006 / FR-OPS-003 / BR-010 / NFR-SEC-002 / NFR-MNT-001:
[ADR-060](../decisions/ADR/060-completed-export-accountability-retirement-proposal.md)
defines a reviewable synthetic completed-EXPORT accountability retirement slice.
It identifies exact receipt/job holds, six-year eligibility, object cleanup and
restricted SQL prerequisites, finite retry semantics and acceptance tests. Human
approval is recorded on 19 October 2026; application acceptance remains separate.
The [exact preservation foundation](E8_EXPORT_EVIDENCE_HOLDS_VERIFICATION.md) adds
receipt identity, gated receipt/job holds and bounded source lookup with tests.
Ten focused integration cases (including restricted LOGIN and upgrades), six
three-engine privacy journeys, 1,094 unit/contract, 35 tooling, types/contracts/build
and populated exact-hold recovery pass. Full integration/hosted acceptance remains
pending at source `5fa939d` in hosted 39229138880; its 425-case local suite finishes with 422 passes and three recovery-helper signature
failures. The corrected helper separation passes all three affected cases, full
exact-hold recovery (312 ms), lint/types/contracts and security; all 15 consolidated
privacy/identity browser executions pass. Old 5fa939d is not an accepted source. No retirement
permission, processor or account-erasure capability is introduced.
Existing retention/erasure gaps remain open. Main closeout `f1bd1ad` separately
passes complete hosted [39189901813](https://github.com/Jotham566/kasoma/actions/runs/39189901813).

## Earlier accepted application checkpoint — 19 October 2026

Application/test source `6d53541` passes complete hosted [39185423895](https://github.com/Jotham566/kasoma/actions/runs/39185423895) and is pushed to main
through Markdown-only merge `5de2ce5`; all merged implementation branches are removed
locally/remotely. Subsequent closeout changes only Markdown. All 1,074 unit/contract,
412 integration, 35 tooling, 108 browser and UI/transport/security/recovery/image/
service gates pass. This supersedes older candidate engineering status below.
ADR-057 bounded capture passes 39183714273 at `0a8f674`; progress replay reuse passes
39184552472 at `7148a1c`; latest shared controls pass 39185423895 at `6d53541`.
Real-data processing, full preservation/erasure, academic and production acceptance
remain excluded. See [current checkpoint/file inventory](IMPLEMENTATION_CHECKPOINT_2026_10_19_PRESERVATION.md).


NFR-MNT-001 candidate: [ADR-059](../decisions/ADR/059-disposable-ci-runner-storage.md)
and [CI storage evidence](E0_CI_STORAGE_VERIFICATION.md) address the observed hosted
disk failure without reducing tests or touching developer data. Hosted-only SDK
preparation and read-only capacity gates pass 22 safety/940 unit-contract cases;
complete hosted acceptance remains required.

FR-OPS-003 / NFR-SEC-002 / NFR-ACC-001 / NFR-PERF-001 / NFR-MNT-001 candidate:
[ADR-058](../decisions/ADR/058-bounded-admin-audit-activity.md) and
[audit readiness](E8_AUDIT_ACTIVITY_READINESS.md) and
[verification](E8_AUDIT_ACTIVITY_VERIFICATION.md) define an aggregate-only ADMIN audit
activity page, fixed categories and newest-10,000 sampling. No individual audit read
permission or retention change. Five focused and all 378 integration cases, 918 unit/contract, 35 tooling,
restricted login, recovery, security, rebuilt Docker and six browser/UI cases pass
locally; complete hosted acceptance remains required. No application acceptance or full audit-coverage claim.

FR-ID-006 / FR-WA-006 / FR-OPS-003 / BR-010 / NFR-SEC-002 / NFR-MNT-001:
[ADR-057](../decisions/ADR/057-minimized-channel-preservation-proposal.md) has explicit
bounded synthetic approval. Source `0a8f674` passes complete hosted [39183714273](https://github.com/Jotham566/kasoma/actions/runs/39183714273):
0038 exact source versions, bound encryption, independent current claim/ownership,
atomic finite decisions and disposal, default-disabled API/UI, minimized export and
advisory inventory. All 34 focused integration, 105 format/contracts, advancing-clock,
actual restricted-role and full broader gates pass; 68-table/680-row logical restore
verifies evidence after operational source removal and disposal/sequence guards.
See [capture verification](E8_CHANNEL_PRESERVATION_VERIFICATION.md). The earlier
private format source `25b44b1` passes 39176205670. This closes only the approved
bounded engineering slice, not full FR-ID-006/BR-010 or legal preservation sufficiency.

FR-WA-002 / FR-WA-006 / NFR-MNT-001 verified at `0a8f674`: real-time conversation testing exposes
two clock reads violating the exact 24-hour expiry constraint. Both new advancing-clock
cases fail before the one-instant correction and pass afterward; the new real-time
conversation/capture browser path passes in all three engines. No SQL constraint or
provider/release gate is relaxed.
NFR-REL-002 local recovery instructions now include nondestructive power-interruption
restart; this does not replace the separately required production recovery evidence.


FR-ID-006 / BR-010 / NFR-SEC-002 / NFR-MNT-001 candidate: forward migration 0036 corrects
four legacy DELETE wrappers using transaction-start time. Four real-trigger probe
reproductions fail before the change and pass after it; original records/append-only
protections remain. Upgrade/replay, 57 related integration cases, 918 unit/contract,
35 tooling cases, restricted logins, recovery, security and 0036 Docker smoke pass
locally; complete hosted acceptance remains pending. See
[clock verification](E8_HOLD_DELETE_CLOCK_VERIFICATION.md). No erasure authority,
retention change, API/data transform or complete preservation claim.

FR-ID-006 / FR-WA-006 / FR-OPS-003 / BR-010 / NFR-SEC-002 / NFR-MNT-001:
[terminal receipt readiness](E8_CHANNEL_RECEIPT_HOLD_READINESS.md) and
[ADR-055 proposal](../decisions/ADR/055-terminal-channel-receipt-holds.md) define the
next bounded hold slice: original owned already-minimized receipts, no live payload/
capability preservation, staged creation and incomplete coverage. Isolated migration/
SQL/API/race/upgrade, restricted login and populated recovery pass; final acceptance
passes in complete hosted run 39165896953 at source 397f562 (918 unit/contract,
368 integration). The source is on main and its merged branch is removed. See
[receipt evidence](E8_CHANNEL_RECEIPT_HOLD_VERIFICATION.md).

FR-OPS-002 / NFR-OBS-001 / NFR-SEC-002 / NFR-ACC-001 / NFR-MNT-001 merged at `0c73c45`:
[ADR-054](../decisions/ADR/054-bounded-worker-model-usage.md) adds six fixed private
worker SDK counters, separate bounded Redis intervals and an ADMIN aggregate/volume
warning. Missing usage is unknown; subtotals and explicit zero remain distinct.
No identities/content/provider labels, billing or accuracy claim. See
[readiness](E8_MODEL_USAGE_READINESS.md) and
[verification](E8_MODEL_USAGE_VERIFICATION.md); complete hosted run 39160113771 passes.

Runtime budgets merged at `f5f408e`: FR-OPS-004/FR-GRD-004 and NFR-SEC/MNT-001 expose only
existing per-job resource ceilings through Settings, keeping the same default/hard
maxima. Local 891 unit/contract, 21 actual flow, 33 review and restricted-login cases,
security, populated recovery and rebuilt-image/service smoke pass; complete hosted
run 39157127637 passes and the merged branch is removed. See
[runtime-budget evidence](E4_RUNTIME_BUDGET_VERIFICATION.md).
No new daily/fleet quota or inference approval policy is inferred.

Grading operations merged at `a357222`: FR-OPS-002, NFR-OBS-001, NFR-SEC-002 and NFR-ACC/COMP-001 add bounded
ADMIN queue/lease/terminal/pending-audit/disabled-band counts and a typed stale-age
alert under ADR-053. Actual encrypted synthetic transitions and authorization/boundary
checks pass: 26 operational and 33 review cases, 884 unit/contract plus 333 broad
integration cases, 104 browser executions, restricted login/recovery/security/containers.
See [grading evidence](E8_GRADING_OPERATIONS_VERIFICATION.md); hosted run
39155326659 passes and the merged branch is removed. Model usage and academic error rate remain unavailable.

Offline reports merged at `17abb2d`: FR-GRD-003/004, FR-OPS-002 and NFR-MNT-001 add a
strict versioned payload-free report reader/comparator and the required `make eval-compare`
command under ADR-052. Thirty-seven new cases, 881 total unit/contract and 35 tooling
cases, lint/types/contracts/security and actual Make invocation pass; see
[report evidence](E4_EVALUATION_REPORT_VERIFICATION.md). Complete hosted run 39151730479 passes. It does not run
inference, establish benchmark truth/approval or enable a learner grading band.

Staff mobile navigation merged at `17abb2d`: NFR-ACC-001/NFR-COMP-001 uses the existing
staff destinations with an explicit narrow-screen disclosure, keyboard activation,
active destination, >=44-pixel controls and close-on-navigation. Desktop navigation
remains visible. Lint/build/contracts, two UI harness and 102 three-engine executions,
including 200% text, pass; final rebuilt container/source checks pass. See
[navigation evidence](E6_STAFF_NAVIGATION_VERIFICATION.md). The complete later report-source hosted run passes; the navigation-only diagnostic save-ack race is retained and corrected in the active follow-up.

Independent review merged at `2164209`: FR-GRD-003/004/005, FR-ID-003/006 and NFR-SEC-002 are
addressed by migration 0033, `services/grading_reviews.py`, blinded staff routes/UI,
release-unit sampling, immutable complete-rubric reviews, sticky rolling disablement,
owned export/inventory/hold integration and per-pass processor rechecks. See
[expert-review verification](E4_EXPERT_REVIEW_VERIFICATION.md) for executed evidence
and complete hosted run 39150319607. The completion-clock cap is a separate active follow-up.
This does not replace academic/provider/privacy release
approval or enable ordinary learner short-text scoring.

Live implementation evidence for every requirement in the [SRD](../specifications/01_SRD.md). The [specification matrix](../specifications/14_Requirements_Traceability_Matrix.md) defines required coverage and evidence. Update this register with each implementation slice; completion requires passing acceptance evidence.

E0 through E6 synthetic learning and E8 learner-flag evidence is recorded below. Local synthetic journeys are not
production-pilot acceptance; delivery-provider and legal approval gates remain. See the [assessment](PHASE_0_ASSESSMENT.md).

| Requirement | Implementation | Tests / evidence | Status |
| --- | --- | --- | --- |
| FR-ID-001 | Email/phone OTP, purpose binding, five-attempt/ten-minute limits, per-contact/peer/device sends; initial UI check serializes sign-in actions | `tests/integration/test_identity.py`, `tests/e2e/identity.spec.ts` | Local implemented; SES/SMS production gates pending |
| FR-ID-002 | Verified identifier linking with uniqueness, encryption and keyed lookup; existing identities never auto-merge | API linking, collision and one-identity tests | Local implemented |
| FR-ID-003 | Birth date, adult consent, separately verified guardian evidence/learner assent, withdrawal, policy gate | Minor/adult API and browser tests; ownership, idempotency and policy-change tests | Local implemented, including channel issue/consume/delivery consent checks; approved wording remains pending |
| FR-ID-004 | Server-restricted S4 Mathematics/Physics profile and subject selection | Profile validation and browser journeys | Local implemented |
| FR-ID-005 | Opaque sessions, refresh rotation/reuse revocation, current/all logout | Expiry, family reuse and revocation API tests; browser logout | Local implemented |
| FR-ID-006 | Recent-OTP intake/review, encrypted bounded JSON and asynchronous private artifacts with 24-hour copy expiry; deletion preview and exact-record holds | [Export evidence](E8_DATA_EXPORTS_VERIFICATION.md); [hold evidence](E8_LEGAL_HOLDS_VERIFICATION.md); [review privacy candidate](E4_EXPERT_REVIEW_VERIFICATION.md) | Partial: intake/export/async delivery/expiry and advisory deletion preview merged; independent review privacy merged; erasure/anonymization, full hold coverage and accountability expiry pending |
| FR-DIAG-001 | Subject diagnostic start/resume; actor lock and partial unique index | Concurrent start and browser reload tests | Local synthetic implemented |
| FR-DIAG-002 | Versioned 15-item adaptive plan; database bounds 10–15 | Full choice/numeric diagnostics; client count override rejected | Local synthetic implemented; early stop intentionally not configured |
| FR-DIAG-003 | CORE first per available topic; competency coverage and response-dependent difficulty | Three-topic/two-competency coverage; strong/weak trajectories | Local synthetic implemented; academic inventory/mapping approval pending |
| FR-DIAG-004 | Atomic acknowledgement with attempt, grade, mastery and outbox; same-key replay | Lost acknowledgement browser retry, rollback and resume tests | Local implemented |
| FR-DIAG-005 | Frozen skill estimates, uncertainty and first explained topic practice recommendation | Completion API, browser result and recommendation link | Local synthetic implemented; current ranking is available through recommended practice |
| FR-REV-001 | `services/recommendations.py`, shared RECOMMENDED start, frozen plan snapshot | 5/10-item API flows, concurrent start, replay, browser lost-ack retry | Local synthetic implemented; academic calibration pending |
| FR-REV-002 | Topic-selected 5–10-item plans through shared assessment service | Assessment API and browser five-question journey | Local manual focus and synchronous mastery updates implemented |
| FR-REV-003 | Content-owned selector, S4/enrollment checks, current approval and retirement lock | Draft/retired/non-web inventory exclusion; identity subject checks | Local synthetic single/multiple-choice and numeric paths implemented |
| FR-REV-004 | Configurable seven-day served-item exclusion across versions; no silent shortage fallback | Completed plan cannot immediately repeat; insufficient-inventory API tests | Local implemented; reassessment enforces all-time unseen selection; academic ranking calibration pending |
| FR-REV-005 | Durable fixed assignments and answered history; active-plan lookup; lost-ack retry | Concurrent replay, separate browser resume and completion after reload | Local choice/numeric revision and diagnostic resume implemented |
| FR-REV-006 | Versioned reasons, home target/time card, per-item selection reasons and diagnostic action | API safe projection, sparse text, accessible browser practice | Local synthetic implemented |
| FR-GRD-001 | Pinned single-choice and canonical exact-set multiple-choice graders, reviewed keys and checkbox delivery | Exhaustive subset/permutation tests, publication/API/DB/retry/replay/diagnostic/reassessment and browser checks; [verification](E4_MULTIPLE_CHOICE_VERIFICATION.md) | Local deterministic implementation; synthetic evidence is not academic benchmark approval |
| FR-GRD-002 | Reviewed numeric contracts, exact rational grading, unit conversions, inclusive tolerances, precision and accepted forms | `tests/contract/test_numeric.py`, `tests/integration/test_numeric_workflow.py`, `tests/e2e/numeric.spec.ts` | Local deterministic implementation; synthetic regression/property cases are not expert academic benchmark approval |
| FR-GRD-003 | Version-pinned encrypted rubric grades, bounded fake dual-pass processor and disabled synthetic learner flow (ADR-050); independent review candidate (ADR-051) | Flow/API/SQL/role/browser/recovery tests; [review evidence](E4_EXPERT_REVIEW_VERIFICATION.md) | Synthetic learner path, independent review and offline reports merged after hosted acceptance; genuine calibration/provider/academic approval and actual scoring remain gated |
| FR-GRD-004 | Distinct pending/neutral outcomes, finite work leases and global request/time/token/repair budget; current consent/band checks and candidate atomic sticky review disablement | Rehearsal, worker rollback/revocation, pending/fallback/retry browser and review window tests | Disabled synthetic fallback and independent review merged after hosted verification; clock-skew follow-up merged after complete hosted acceptance and actual scoring approval pending |
| FR-GRD-005 | Authored-feedback allowlists, exact pinned criterion evidence, encrypted result projection and owned rubric feedback; blinded independent review keeps model outcomes hidden | Strict candidate/result contracts, learner and reviewer browser/API cases | Synthetic learner feedback merged; real academic calibration and scoring approval pending |
| FR-GRD-006 | Reviewed versioned hints, append-only usage and frozen pre-answer count/highest level; independence weighting with unchanged points | `tests/contract/test_hint_contract.py`, `tests/integration/test_hints.py`, `tests/e2e/hints.spec.ts`; [verification](E4_HINTS_VERIFICATION.md) | Local synthetic verified (235 Python tests / 12 browser tests); production hint academic review pending |
| FR-GRD-007 | Owned submitted-attempt prerequisite for worked solution; safe learner DTO | Direct pre-attempt denial, IDOR and browser solution gate | Local revision gating and permanent diagnostic solution block implemented |
| FR-GRD-008 | Reviewed equivalence claims and same-primary-skill/difficulty fallback; all-time unseen/clone exclusion; one-item linked session with independent evidence | Reassessment unit/API/browser suites, migration 0010 and `make replay-reassessments`; [verification](E4_REASSESSMENT_VERIFICATION.md) | Local synthetic verified (249 Python tests / 13 browser tests); academic transfer validity and calibrated misconception-resolution criteria pending |
| FR-GRD-009 | Owned attempt/version-bound reporting, encrypted bounded comments, safe receipt recovery | Flag contract/API/browser suites; [verification](E8_FLAGS_VERIFICATION.md) | Local synthetic implementation; current consent and diagnostic sealing enforced |
| FR-MST-001 | Unique append-only attempt/skill evidence; synchronous deterministic grading; consented legacy reconciliation | Duplicate replay, rollback, immutable DB records and integration tests | Local deterministic path implemented |
| FR-MST-002 | Specified weighted prior, score, coverage/recency confidence and display state | Hand calculations, property tests and diagnostic UI | Local implemented |
| FR-MST-003 | Versioned configuration, original inputs, hashes, estimate history and offline replay | make replay-mastery; nonempty current/history replay integration tests | Offline reproduction implemented; no authenticated learner-level support replay UI/permission yet. API section9 requires explicit support permission/audit; aggregate ADMIN access does not grant record access |
| FR-MST-004 | Evidence-derived subject/topic/competency rollups, coverage, recent change and owned session history; roadmap 3.5 practice-day candidate | Progress engine/API/browser tests; [verified baseline](E6_PROGRESS_VERIFICATION.md); [activity candidate](E6_PRACTICE_ACTIVITY_VERIFICATION.md) | Baseline and practice-day synthetic engineering verified at adf4328 by full hosted39299684285; native loads remain pinned to78ca959. Prior WebKit timeout remains unexplained. Academic aggregation and release approval remain pending |
| FR-MST-005 | Confidence/coverage shown throughout progress; numeric mastery hidden below 0.25; unfinished diagnostic evidence excluded | Sparse/established engine tests, sealed diagnostic API/browser checks and axe/keyboard retry | Local diagnostic and general progress implemented; no absolute academic claims |
| FR-MST-006 | `services/recommendation_engine.py`, immutable inputs/configuration/plan snapshots; prerequisite graph from approved synthetic metadata | Factor direction, prerequisite redirection, cycle rejection, bounds, deterministic replay, API/browser flow | Local synthetic implemented; reviewed curriculum importance/graph, scenario metadata and teacher calibration remain release gates |
| FR-WA-001 | `services/whatsapp_linking.py`, migration 0018, owned web channel UI | [E7 evidence](E7_LINKING_READINESS.md); expiry/replay/concurrency, consent/minor and sender-collision tests | Local fake linking verified; production provider/pilot gates remain |
| FR-WA-002 | Shared five-item channel selection; reply-bound menus and conversation pointers | `test_channel_assessment.py`; [conversation evidence](E7_CONVERSATION_VERIFICATION.md) | Local signed five-question conversation verified; production gates remain |
| FR-WA-003 | Shared transactional graders/mastery with immutable channel provenance | [Foundation evidence](E7_SHARED_TRANSACTIONS_VERIFICATION.md); three-format database parity | Local internal and signed webhook parity verified |
| FR-WA-004 | Signed bounded intake, durable message-ID hashes, atomic replay/conflict handling, monotonic status callbacks | [E7 evidence](E7_LINKING_READINESS.md); signature, duplicate/conflict, callback and rollback tests | Local transport and answer/mastery replay invariants verified |
| FR-WA-005 | Bounded question/feedback formatters and authenticated web fallback | `test_whatsapp_format.py`, `test_whatsapp_feedback.py`; [conversation evidence](E7_CONVERSATION_VERIFICATION.md) | Formatting and authorized fake delivery verified; production pending |
| FR-WA-006 | Immediate STOP barrier, owner unlink, fake outbound rechecks | [E7 evidence](E7_LINKING_READINESS.md); STOP before worker/delivery, stale code and retry tests | Local opt-out and transient practice invalidation verified; learning evidence retained |
| FR-CNT-001 | `services/content.py`, strict draft DTO, staff editor; bounded JSON import API/UI and transactional worker | Content tests; import contract/API/browser regressions; [import evidence](E2_IMPORTS_VERIFICATION.md) | Create/edit and bounded synthetic JSON import verified under ADR-032; real academic inventory/rights release remains gated. Other file formats are outside that accepted slice |
| FR-CNT-002 | Role checks and immutable author ownership; self-review blocked even with both roles | API self-review denial; SQL review guard; disabled author approval in browser | Local implemented |
| FR-CNT-003 | Return, approval, high-risk/disputed second review, retirement and append-only reviews | Full API/browser workflow; two-reviewer and retired-selection tests | Local implemented with synthetic content |
| FR-CNT-004 | Immutable approved versions, explicit successor drafts, normalized frozen mappings and version-pinned reviewed rubrics | API mutation rejection; direct SQL history/mapping/attempt/rubric tests; retired-version grades/solutions remain unchanged | Choice/numeric provenance, ADR-044 rubric authoring and ADR-050 disabled synthetic learner-attempt integration verified; real academic release remains gated |
| FR-CNT-005 | Submission and approval revalidate rights, mappings, weights, answer, solution and remediation | Field-specific 409 tests; approval revalidates changed curriculum references | Local single/multiple-choice/numeric validation and version-pinned short-text rubric authoring verified; real academic evidence and short-text enablement remain gated |
| FR-CNT-006 | Reviewer/admin queue, independent claim, priority/status/resolution, immutable history and revision-checked retries | Triage API/browser, role/ownership, audit/rollback and disputed-successor tests | Local synthetic implementation; approved live support and retention jobs remain production gates |
| FR-OPS-001 | `services/observability.py`, `packages/analytics-schema/` | `tests/contract/test_foundation.py`, `tests/contract/test_identity_contract.py`, identity integration outbox assertions: safe operational and identity-event shape | Registration/consent, assessment, diagnostic start/completion and mastery-update events persist atomically; hint-use and reassessment lifecycle events also persist atomically; flag lifecycle events use the content outbox; data-request intake/review and export completion events also use the identity outbox; channel code/link/unlink/STOP events and safe correlated processing logs are implemented; remaining dispatch pending |
| FR-OPS-002 | ADMIN snapshot/dashboard, bounded imports/flags/channel/exports and response-start histograms; grading queue and verified local model observations | [Operations evidence](E8_OPERATIONS_VERIFICATION.md); [grading candidate](E8_GRADING_OPERATIONS_VERIFICATION.md); threshold/recovery, authorization, safe logs and browser checks | Partial: existing local visibility merged; grading queue/lease/fallback and bounded local model observations merged; model spend, academic/technical error-rate distinctions, SMS/email/mastery/provider telemetry and production alerting remain pending |
| FR-OPS-003 | Atomic content/role audit, database history guards | Direct SQL audit rewrite rejection, role-action records and content events | Partial: content/local roles and flag read/triage audit; bounded aggregate ADMIN audit activity verified at 5d95f9d; individual support access and retention processing remain gated |
| FR-OPS-004 | Typed channel attempt/outbound limits and feature flag; configurable shared short-text per-job request/token/time ceiling with finite lease/hard task bounds | [E7 evidence](E7_LINKING_READINESS.md); [runtime-budget candidate](E4_RUNTIME_BUDGET_VERIFICATION.md); actual fake exhaustion and exact replay | Local channel controls merged; typed runtime budget passes local and complete hosted checks; actual provider usage/billing and production acceptance remain gated. No unspecified learner/day/fleet quota is invented |
| NFR-PERF-001 | Isolated objective and mixed recent-history HTTP load; ADR-046 locks/batched eligibility | [Baseline evidence](E9_OBJECTIVE_LOAD_VERIFICATION.md); [mixed history](E9_HISTORY_MIXED_LOAD_VERIFICATION.md) | Native 6b06c53 profiles and complete hosted 39217860618 pass; mixed START p95 432.085 ms. Deployment, older/diagnostic histories and provider acceptance remain pending |
| NFR-PERF-002 | Deterministic choice/numeric response feedback; bounded channel wake-up | [Current baseline/mixed evidence](E9_HISTORY_MIXED_LOAD_VERIFICATION.md); [channel evidence](E7_CONVERSATION_VERIFICATION.md) | Native 6b06c53 mixed ANSWER p95 27.487 ms; numeric subset 27.778 ms, 1,250 samples per format. Full AI/provider/WhatsApp/deployment acceptance remains pending |
| NFR-REL-001 | — | — | Not started |
| NFR-REL-002 | Isolated synthetic logical recovery with exclusive source-role/OID cleanup (ADR-042) | [Recovery evidence](E9_RECOVERY_VERIFICATION.md); [ownership correction](E9_RECOVERY_ROLE_OWNERSHIP_VERIFICATION.md) | Full hosted39299684285 at adf4328 verifies69 tables/686 rows in493ms and preserves unowned/replaced roles; object-storage and production PITR/RPO/RTO remain pending |
| NFR-SCL-001 | Synthetic 2,000-registration/500-active/50-concurrent objective and mixed-history profiles | [Load evidence](E9_HISTORY_MIXED_LOAD_VERIFICATION.md) | Both native 6b06c53 7,000-request profiles pass; mixed final totals 27,500 grades/5,500 sessions, zero errors, successful cleanup. Complete hosted regression passes; daily soak/deployed/provider scale acceptance pending |
| NFR-SEC-001 | `services/config.py`, loopback Compose, generated ignored secrets | Fail-closed/redaction tests; source/dependency scans | Partial; production TLS/encryption pending |
| NFR-SEC-002 | Identity ownership, recent-auth/consent controls and staff content-role enforcement | Identity integration and cross-origin browser tests | Partial; content RBAC implemented; assessment consent/ownership guards verified; production MFA/role governance and future route integration pending |
| NFR-ACC-001 | `apps/web/app`, `packages/ui` | Playwright keyboard retry and axe scan | Shell, onboarding, staff review, assessment, diagnostic, progress/history and flag/triage axe/keyboard checks; remaining journey matrix pending |
| NFR-BW-001 | Cold-context first-question encoded transfer check, including headers/prefetch and no media exclusions for the synthetic fixture | Existing assessment E2E journey; [browser evidence](E9_BROWSER_COVERAGE_VERIFICATION.md) | Synthetic cold transfer verified across three engines: 191389–194127 bytes; media/mobile/latency release checks remain |
| NFR-COMP-001 | Full journey harness for isolated Chromium/Firefox/WebKit runs | [Browser matrix evidence](E9_BROWSER_COVERAGE_VERIFICATION.md), [narrow viewport regression](E9_MOBILE_REFLOW_VERIFICATION.md) | 66 browser executions, including 320-pixel touch journey, verified in CI 37925290651; branded/current-previous/physical mobile acceptance pending |
| NFR-OBS-001 | UUID web/API/worker correlation; console OTel; safe JSON logs; API response-start and synthetic model-call timing | Unit redaction and real worker propagation tests; [model telemetry evidence](E8_MODEL_TELEMETRY_VERIFICATION.md) | Minimized timing verified through hosted CI 37914864557; durable aggregation/domain tracing remains partial |
| NFR-MNT-001 | pnpm/Turbo + uv locks; Alembic; generated client; Make/CI | Setup, lint/types, migration tests, OpenAPI diff, web build/E2E | Full hosted synthetic regression evidence recorded per slice; release acceptance remains separately gated |
| NFR-LOC-001 | English shell; UTC storage/wire; progress/history dates in Africa/Kampala | Configuration and browser history checks | Progress/history presentation implemented; wider localization review pending |

FR-GRD-003/004/005 / FR-MST-001 / FR-ID-006: the 10 October
[short-text readiness update](E4_SHORT_TEXT_INTEGRATION_READINESS.md) records inspected
pending/neutral contract gaps and mandatory beta audit/automatic disablement controls.
This is design-readiness evidence only; learner short-text acceptance remains incomplete.

E4 numeric execution evidence: [verification report](E4_VERIFICATION.md).

NFR-MNT-001: [CI runtime/mirror remediation](E9_CI_RUNTIME_VERIFICATION.md) addresses
an observed whole-job timeout and registry throttling. The disposable-runner cache
configuration preserves existing settings and has isolated tooling regression tests. It does not waive any test
or constitute main/release acceptance; new exact-head hosted verification is required.

FR-ID-006 / NFR-COMP-001 / NFR-MNT-001: hosted run 38004530911 passed startup,
backend and Chromium/Firefox checks but failed three Linux WebKit attachments.
`tests/browser-control/download.spec.ts` adds a successful native attachment control
with exact filename/bytes. All three controls pass on macOS WebKit; Linux diagnosis
and full hosted acceptance remain pending. See [CI evidence](E9_CI_RUNTIME_VERIFICATION.md).

Linux ARM64 comparison reproduces the three control timeouts; explicit HTML download
intent passes the same filename/byte/cancellation/corruption checks. The background
export link adopts that intent, with application regression pending. The documented
`make test-export-download-control-linux` preserves a bounded, isolated reproduction.
The complete native browser matrix now passes 90 executions, including streamed fault
rejection, native frozen retry and recent-owner preflight errors. Rebuilt container
security/health/export/metrics smoke passes; final expired-notice privacy regression
passes all six executions with format/lint/types/build. Exact-head hosted acceptance
remains pending. No release gate is waived.

FR-OPS-002 / NFR-OBS-001 / NFR-SEC-002 / NFR-MNT-001 in progress:
[request aggregation](E8_REQUEST_AGGREGATION_VERIFICATION.md) adds an isolated OTel
histogram component and percentile/property tests under proposed ADR-049. Runtime
components now include bounded Redis expiry/deduplication and a background SDK collector.
Integration is under verification; REQUEST_LATENCY remains unavailable when collection
is absent/stale/invalid, and these requirements
remain partial. No application acceptance is inferred from the component.

E5 diagnostic/mastery evidence: [verification report](E5_VERIFICATION.md).

FR-GRD-003/004 / FR-MST-001 / NFR-SEC-001/002 / NFR-REL-002: migration 0028 and
`services/grading_band_store.py` add immutable global calibration metadata, locked
state and sticky disablement with exact history. Eleven focused PostgreSQL cases,
restricted disable-only worker permissions and populated recovery pass; full regression
passes 279 integration cases. Additive migration 0029 then closes a reproduced
topic-reparenting gap with a composite FK; 13 focused SQL cases, populated upgrade,
restricted login and recovery pass on that correction. Exact-head hosted verification
is pending. [Evidence and remaining runtime/approval gates](E4_BAND_STORAGE_VERIFICATION.md).

FR-GRD-003/004/005 / FR-MST-001 / NFR-SEC-002: the proposed ADR-050 eligibility
component binds calibration evidence and audit state to the exact band/scope/versions.
It rejects insufficient counts, missing approvals, harmful/pending subgroup review,
critical errors, incomplete audit coverage and rolling agreement below 90%.
[Verification and remaining runtime gates](E4_ELIGIBILITY_VERIFICATION.md). This is
not academic approval, durable automatic disablement or learner grading acceptance.
Component checks pass 780 unit/contract and 35 tooling cases, lint/types, generated
contracts and security scans; runtime and approval gates remain open.

E5 recommended practice: [verification report](E5_RECOMMENDATIONS_VERIFICATION.md).

E4 reviewed hints: [verification report](E4_HINTS_VERIFICATION.md).

E4 unseen reassessment: [verification report](E4_REASSESSMENT_VERIFICATION.md).

E6 progress and session history: [verification report](E6_PROGRESS_VERIFICATION.md).

E8 learner flags: [verification report](E8_FLAGS_VERIFICATION.md).

E8 record legal holds: [verification report](E8_LEGAL_HOLDS_VERIFICATION.md), covering
FR-ID-006, BR-010, FR-OPS-003, NFR-SEC-002, NFR-ACC-001 and NFR-MNT-001.
Partial coverage never authorizes account erasure.

E9 lint dependency security remediation (NFR-MNT-001/NFR-SEC-001):
[ADR-031](../decisions/ADR/031-lint-glob-security.md) and
[verification](E9_LINT_SECURITY_VERIFICATION.md). No application acceptance inferred.

### E7 verified local linking (FR-WA-001/004/006, FR-ID-003/006, FR-OPS-001/003/004)

Code `23da19c` and [E7 evidence](E7_LINKING_READINESS.md) record migration 0018, owner routes/UI,
signed durable intake, STOP barriers, transactional processing/fake delivery, expiry and owned
export/deletion inventory. Hosted CI passed 395 Python, 20 browser and five tooling tests plus
all setup/migration/lint/type/contract/build/security/container gates. Native Docker interruption
is recorded separately. FR-WA-002/003/005 practice/grading and production transport remain pending.

### Verified shared-service foundation (FR-WA-002/003/004)

ADR-035 and `tests/integration/test_assessment_transactions.py` cover the verified internal
transaction boundary needed for channel parity. Web behavior, schemas and receipt hashes remain
unchanged. Commit `50044d4` passed hosted CI 37149982356: 398 Python tests, 20 browser and
five tooling checks, including all three new database regressions and the complete release pipeline.
This is not evidence that WhatsApp practice or parity is implemented.

ADR-036 adds an independent channel-formatting boundary and contract regressions toward
FR-WA-002/003/005. This boundary neither chooses approved versions nor binds learner replies;
those integration gates and full channel parity remain pending.

ADR-037, migration 0019 and `tests/integration/test_channel_assessment.py` address internal
FR-WA-002/003/004, FR-CNT-004, FR-GRD-001/002 and FR-MST-001 channel capability/provenance.
The six added parity/database cases passed in CI 37217857047 for `c0b5b55`.
Conversation/reply binding, outbound practice and end-to-end parity remain separate gates.

FR-WA-005: `services/whatsapp_feedback.py` and `tests/contract/test_whatsapp_feedback.py` add
concise shared-grade projection, lossless-or-web fallback and safe local session links. Actual
channel feedback delivery remains pending conversation integration.

### E7 channel foundation verified; conversation in progress

Commit `c0b5b55` passed CI 37217857047 with 437 Python, 20 browser and five tooling checks plus
clean migrations, contracts, security and containers. This proves internal FR-WA-002/003/004 capability/parity. ADR-038, migration 0020,
`services/whatsapp_practice.py`, `whatsapp_render.py`, `whatsapp_wakeup.py` and
`tests/integration/test_whatsapp_practice.py` address signed end-to-end FR-WA-002/003/004/005/006
and transient FR-ID-006 inventory; those application acceptance gates remain pending.
NFR-PERF-002 has a bounded wake-up implementation, but measured p95 latency remains unverified.

Follow-up FR-CNT-004/FR-WA-003 regression rejects WEB serving/submission of WHATSAPP-only
versions, including direct database insertion, while preserving valid channel attempts.
The conversation suite adds pending hosted checks for accepted intake after a failed broker
wake-up and one attempt/mastery update for concurrent distinct replies to one question.

ADR-039, `services/channel_operations.py`, migration 0021 and the channel operations contract/
integration/browser checks address local FR-OPS-002/004 and NFR-OBS-001 visibility. New operational
acceptance is pending; counts and fake-dispatch timings do not establish NFR-PERF-002 or production
messaging/notification coverage. [Verification](E8_CHANNEL_OPERATIONS_VERIFICATION.md).

FR-GRD-003/004/005 offline validation: [E4 evidence](E4_SHORT_TEXT_VALIDATION_VERIFICATION.md).
Strict output, rubric/evidence/context checks are implemented; validated candidates never authorize
scores. Production eligibility, academic calibration and the learner vertical path remain pending.

### E7 final signed conversation acceptance

Commit `5063528` passed [CI 37220225176](https://github.com/Jotham566/kasoma/actions/runs/37220225176),
469 Python, 20 browser and five tooling checks with all setup/migration/build/security/container
gates. This supersedes the preceding conversation-pending notes for FR-WA-002/003/004/005/006
and FR-CNT-004. See [final evidence](E7_CONVERSATION_VERIFICATION.md). Production transport,
academic approval and measured latency/load remain pending.

FR-GRD-003/004/005 and NFR-SEC-002 rehearsal: [E4 evidence](E4_SHORT_TEXT_REHEARSAL_VERIFICATION.md)
covers 15 FakeModelProvider orchestration cases and bounded dual passes/repair. No scoring, model
inference, academic calibration, full gateway telemetry or learner fallback acceptance is claimed.

ADR-039 local channel operations acceptance is now verified for `34950b0` by
[CI 37221185319](https://github.com/Jotham566/kasoma/actions/runs/37221185319): 479 Python,
20 browser and five tooling checks plus clean migrations/security/container gates. This supersedes
the pending telemetry note above; remaining AI/HTTP/production metrics and release SLOs stay open.

NFR-REL-002/NFR-SEC-002/NFR-MNT-001 local recovery preparation: [E9 evidence](E9_RECOVERY_VERIFICATION.md).
Isolated source/destination backup/restore, row parity and immutable guards require hosted execution;
profile/cleanup contract tests alone do not establish recovery acceptance. Production PITR remains open.

ADR-041 fake orchestration is verified for `2ce14c3` by
[CI 37222368566](https://github.com/Jotham566/kasoma/actions/runs/37222368566): 534 Python,
20 browser and five tooling checks plus clean migrations/security/container gates. All automatic
learner scoring remains disabled. This supersedes earlier rehearsal-pending notes.

NFR-OBS-001/FR-OPS-002/NFR-SEC-002: [request timing evidence](E8_REQUEST_TIMING_VERIFICATION.md)
covers the additive privacy-safe response-start field and six contract cases. Aggregated latency,
full network timing and load/SLO acceptance remain pending; a log sample is not a percentile gate.

E9 final local acceptance: recovery `42a6e08` passed CI 37223872075 (550 Python/20 browser/five
tooling checks, 52-table/270-row logical restore). Browser/transfer `96a16d0` passed CI 37224172033
(550 Python/60 browser/five tooling checks, 191389–194127 response bytes). See the linked reports
for exact scope and limits; earlier pending entries are historical, not current acceptance status.

NFR-SEC-002 assessment database permission profile: [verification](E9_RUNTIME_ROLE_VERIFICATION.md).
The focused real-login integration test is implemented; hosted acceptance is pending. Local database
setup is unavailable. Production role provisioning and complete module grant coverage remain partial.

FR-ID-006/BR-010, FR-OPS-003 and NFR-SEC-002 learning-record holds:
[verification](E8_LEARNING_HOLDS_VERIFICATION.md), [ADR-043](../decisions/ADR/043-learning-record-holds.md).
Grade/mastery evidence/history ownership and guards are implemented with hosted acceptance pending;
full hold coverage and deletion remain incomplete.

FR-ID-001 and security §6 ephemeral OTP retention, supporting NFR-OBS-001:
[bounded expiry verification](E1_EPHEMERAL_EXPIRY_VERIFICATION.md). Scheduled cleanup and
rate-refresh locking are implemented; hosted acceptance is pending. Account/session/audit retention
and other privacy processors remain separate gaps.

NFR-OBS-001/FR-OPS-002 timing is verified at `74a4a8f` in hosted CI 37226011029: 556 Python,
60 browser and five tooling checks plus recovery, security and container gates. Main updated and
the completed branch removed. Aggregated p95/load evidence remains pending.

NFR-SEC-002 restricted-login follow-up: first hosted execution found a missing users-row locking
grant in the test profile. The narrow display_name update grant now enables the existing trigger;
identity/status/birth-date denial assertions remain. Acceptance is pending a complete rerun.

FR-GRD-003/004 criterion-material follow-up: the offline context now requires the specified
criterion text, acceptable evidence, common errors and prohibited inferences. Thirteen new
boundary/privacy cases pass locally; fake prompt versions are v2. See
[validation evidence](E4_SHORT_TEXT_VALIDATION_VERIFICATION.md). Persistence, academic approval,
calibrated enablement and the learner fallback path remain incomplete.

## 9 October 2026 verified rubric, telemetry and dependency slices

Hosted CI [37914864557](https://github.com/Jotham566/kasoma/actions/runs/37914864557)
passed at `ed7d7d5`: 427 unit/contract and 182 integration tests (609 Python total), five tooling
tests, 63 real-API browser journeys across Chromium/Firefox/WebKit and one isolated editor UI test.
Clean setup/migrations/seed, eight focused rubric cases, restricted-login verification,
lint/format/types/contracts/build, dependency/source/image security checks and container smoke all
passed. The isolated logical recovery restored 54 tables/272 synthetic rows in 455 ms and verified
pgvector/immutable guards; this is not production PITR/RPO/RTO evidence. Cold question transfers
were 191529/194251/193635 bytes, each below 250000. Commit `ed7d7d5` is on main; both completed
rubric/telemetry branches were deleted locally and remotely.

This supersedes earlier pending entries for restricted-login checks (NFR-SEC-002), bounded identity
expiry (FR-ID-001), learning-record holds (FR-ID-006/BR-010) and rubric context (FR-GRD-003/004).

FR-CNT-001/002/003/004, FR-GRD-003/004 and NFR-SEC-002:
[ADR-044](../decisions/ADR/044-reviewed-rubric-persistence.md) and
[rubric verification](E2_REVIEWED_RUBRICS_VERIFICATION.md). Migration 0023, shared contracts, content
service, staff editor/reviewer, generated API schemas, learner selection/SQL exclusion and staff
inventory are verified. Three contract cases, eight database cases and the new three-engine journey
cover the boundary; one isolated UI regression verifies save/reload. No academic or learner-scoring
acceptance is implied.

NFR-OBS-001/FR-OPS-002: [synthetic telemetry](E8_MODEL_TELEMETRY_VERIFICATION.md) connects
services/model_telemetry.py, short_text_orchestration.py and model-telemetry.schema.json to eleven
additional contract cases. Closed call/outcome events and disposable fingerprints are verified.
Durable aggregation, threshold alerts, production usage/cost and retention remain gaps.

NFR-MNT-001/security gate: [dependency verification](E9_DEPENDENCY_REFRESH_2026_10_09.md) records
patched runtime dependencies and complete source/container acceptance. Earlier JSON/JSONB and
textarea-label failures are corrected and retained in the rubric verification report.

FR-ID-006 next: [large-history export readiness](E8_LARGE_HISTORY_EXPORT_READINESS.md) maps the
existing bounded synchronous implementation to projection, async delivery and privacy/expiry gates.
This is assessment only; large-history fulfillment remains incomplete. Native Docker now responds,
but local migration/seed/application assertions await the approved image builds/browser downloads.

## Export projection acceptance and native recovery

FR-ID-006/NFR-SEC-001/002/NFR-MNT-001: services/data_export_projection.py and
tests/integration/test_data_exports.py verify batched ORM hydration, owned SQL reference/sealing
queries, exact row-cap accounting and cursor cleanup. See
[projection evidence](E8_EXPORT_PROJECTION_VERIFICATION.md).

Hosted CI [37918757085](https://github.com/Jotham566/kasoma/actions/runs/37918757085)
passed at `8c14590`: 427 unit/contract plus 184 integration tests (611 Python), five tooling tests,
63 real-API browser executions and one isolated editor test. Clean setup/migrations/seed, focused
rubric/role checks, lint/format/types/contracts/build, security/source/image scans and container smoke
passed. Recovery restored 54 tables/272 synthetic rows in 385 ms with pgvector/immutable guards and
no cleanup failures. Cold transfer was 191501/194260/193634 bytes, below 250000 for all engines.
The implementation is on main and its completed branch is removed locally and remotely.

Native Docker is available (29.8.2). The documented CLI PATH adjustment and
`make services-db migrate test-reviewed-rubrics test-data-exports` passed: PostgreSQL/Redis healthy,
eight rubric and eleven export cases verified. Full native `make lint test` passed 427 unit/contract
and 183 integration cases; its storage/Mailpit case failed because MinIO was not running. Separate
contract, recovery (54 tables/272 rows, 221 ms), restricted-role and security checks passed, with no
known vulnerabilities reported. This is not a full native acceptance pass.

The MinIO source download passed its checksum, but `go mod download` later failed with unexpected
EOFs in four module downloads. Native Playwright installed Chromium/FFmpeg; the headless-shell
transfer encountered timeout/connection resets and is retrying. No data or volumes were reset.

This supersedes earlier pending projection/native-database entries. Large-history delivery remains
incomplete; the readiness document is a proposal, not accepted asynchronous behavior. NFR-MNT-001
next covers bounded verified dependency-download recovery without replacing the MinIO source pin.

NFR-MNT-001 native setup resilience: infra/containers/minio.Dockerfile,
infra/containers/download-go-modules.sh and tests/contract/test_minio_download_recovery.py connect
bounded download retries and mandatory integrity verification to four deterministic subprocess
cases. [Verification](E0_MINIO_DOWNLOAD_RECOVERY.md): full hosted CI 37923437046 passed at `04de7ea`
(615 Python, 63 browser, one isolated UI and five tooling checks), including actual services and
security/container gates. Promoted to main; native image download remains incomplete. ADR-019 pins
and runtime behavior are unchanged; browser download recovery is a separate environment issue.

FR-ID-006/BR-010/FR-OPS-003/NFR-SEC-002 accountability hold coverage:
[ADR-045](../decisions/ADR/045-accountability-record-holds.md), migration 0024,
services/legal_holds.py and legal_hold_contracts.py, the administrator selector, generated API
contracts, expanded exact-record integration cases and the administrator browser journey.
[Verification](E8_ACCOUNTABILITY_HOLDS_VERIFICATION.md): 19 focused native cases and hosted CI
37924489562 pass (621 Python, 63 browser, one isolated UI, five tooling plus full security/container
gates). Promoted `ce9d9f3` to main and removed its branch. FLAG_HISTORY and
DATA_REQUEST_REVIEW add preservation only; incomplete coverage and disabled deletion remain.


FR-ID-006/NFR-SEC-001/002/NFR-MNT-001 incremental encoding: `services/data_export_encoding.py`,
`services/data_export_projection.py` and `services/data_exports.py` apply the existing full-envelope
byte cap before collecting the projected history. Codec and database cases cover exact byte counts,
Unicode/escaping, empty sections, early hydration stop, cancellation/cursor closure, all-or-nothing
completion and pre-existing frozen retry copies. [Verification](E8_EXPORT_ENCODING_VERIFICATION.md).
This does not enable asynchronous fulfillment or raise either synchronous limit.

ADR-046 objective load regression: hosted CI 37933227560 passed at `f2dbf8a` (646 Python,
66 real-API browser, five tooling, one isolated UI, full service/recovery/security/container checks).
Promoted to main and removed the branch. Representative deployment/history/provider acceptance
remains open; see the [load evidence](E9_OBJECTIVE_LOAD_VERIFICATION.md).


FR-ID-006/NFR-SEC-001/002/NFR-MNT-001 private artifact preparation: ADR-047,
`services/export_artifacts.py`, synthetic fake-storage contract cases and the owned projection
round-trip integration case. [Verification](E8_PRIVATE_EXPORT_ARTIFACT_VERIFICATION.md).
Delivery remains disabled pending the atomic job/storage/expiry/download lifecycle; existing
synchronous limits, authorization and retention remain unchanged.


FR-ID-006/NFR-SEC-001/002/NFR-MNT-001 private MinIO adapter: `services/export_storage.py`,
24 fake-provider cases and a real local-only owned-object integration case. Bounds apply before
reads and connections close on all paths. [Verification](E8_PRIVATE_EXPORT_STORAGE_VERIFICATION.md).
Native storage is unavailable; hosted actual-service CI 37962081120 passed at `bb2f4eb`, now on main. No runtime delivery
path or new retention decision is enabled; ADR-048 remains proposed.

Incremental encoding and private format hosted regression passed at `a485bb6` (CI 37949902270,
657 Python) and `8c08890` (CI 37950849215, 696 Python), each with 66 browser, five tooling, one
isolated UI and full service/recovery/security/container checks. Both are on main; completed
branches removed. This verifies their internal boundaries, not full asynchronous fulfillment.


FR-ID-006 async lifecycle work in progress: ADR-048 proposal, internal export job/status types
and additive migration 0025 are under implementation. No route/worker registration or completed
requirement is claimed. Queue/snapshot/publication/cleanup/download and acceptance tests must
travel together before this slice is committed or promoted.

Async export progress: [in-progress evidence](E8_ASYNC_EXPORT_VERIFICATION.md) records 23 isolated
PostgreSQL queue/claim/snapshot/publication/cleanup/download/failure cases and complete fake-storage
delivery of a 12,000-event synthetic history beyond both original caps. Fifteen existing export
regressions pass. Authenticated API/browser/worker integration remains incomplete; no requirement
is marked complete from these internal results.

FR-ID-006/FR-OPS-002/NFR-SEC-002 in-progress cleanup cursor: `services/export_cleanup_cursor.py`
and 13 deterministic contract cases enforce scoped keys, bounded reads, finite one-hour retention,
phase alternation and safe restart after invalid state/cache outages. Eight attachment transport
cases cover exact lengths, failure/cancellation and resource closure. The current 554 unit/contract
and five tooling checks pass. No scheduled worker or HTTP route is enabled by these helpers.


Migration 0025 clean-schema coverage and synthetic logical recovery pass (56 tables/272 rows,
280 ms); restricted-role regression and source/dependency security checks pass. Job/generation
recovery fixtures, absolute provider-read cancellation, enabled worker/API/proxy/UI acceptance
and actual scoped MinIO lifecycle verification remain outstanding under ADR-048.


FR-ID-006/NFR-SEC-001/002/NFR-OBS-001/NFR-MNT-001 async transport progress: the signed local
reader passes 22 deterministic plus one real TCP dribble/cancellation case; isolated API routes
and shared authenticated decoding pass ownership, frozen transfer, corruption/revocation and
expiry checks. 590 unit/contract, 35 focused lifecycle/API and 15 existing export cases pass.
Worker tasks have dedicated-queue envelopes and closed observability, but runtime registration,
hard-kill recovery, web proxy/UI, operations and complete acceptance are outstanding.
See [current evidence](E8_ASYNC_EXPORT_VERIFICATION.md); ADR-048 remains proposed.


FR-ID-006/FR-OPS-002/NFR-MNT-001 worker evidence: `make test-export-worker` passes five policy/
closed-error cases and an isolated real CLI hard-kill/replacement/lease-recovery case on macOS.
The test exposed and verified the fix for spawned task registration. No ordinary worker timeout,
provider, data or deletion permission changes. Actual application activation remains gated.


NFR-MNT-001 local resource correction: a broad native run passed 151 integration cases but had
86 fixture errors after PostgreSQL exhausted Docker's default 64 MiB `/dev/shm` and entered
recovery, plus the two known unavailable-MinIO failures. Compose now sets `shm_size: 512mb`.
`make services-db` recreated only the PostgreSQL container with its existing named volume intact;
inspection confirms a healthy service and 536870912-byte shared-memory ceiling. SQL timeouts,
acceptance thresholds and developer schemas remain unchanged. The serial rerun passes 590 unit/contract and 238 integration cases with zero setup errors;
its only two failures are the unavailable-MinIO cases. Actual storage acceptance remains open.

The real Uvicorn/API/middleware client-disconnect test passes: closing a partial attachment cancels
the in-flight async reader and closes its resources. Current focused lifecycle/API count is 37.


FR-ID-006/NFR-REL-002 recovery follow-up: the isolated logical drill now publishes a synthetic
async export before backup, requires nonempty job/generation records, verifies restored publication
guards and decrypts the restored manifest against in-memory synthetic encrypted objects. Frozen
bytes match; source/destination inventories remain unchanged. Native `make recovery-drill` passes
56 tables/285 rows in 262 ms with no cleanup failure. This is database/key compatibility evidence,
not object-storage backup, namespace remapping, production PITR or RPO/RTO acceptance.

The unwired web attachment helper passes exact-length, metadata, cancellation and deadline checks.
`make format lint test-tooling openapi-check` passes, including 21 tooling cases; application
contracts remain unchanged. ADR-048 and the complete async delivery slice remain unaccepted.

Recovery follow-up regression: `make format lint test-export-jobs test-unit` passes 40 focused
PostgreSQL cases, 590 unit/contract and 21 tooling cases. Three new cases prove read-only export
verification rejects corrupt ciphertext, missing objects and mismatched expected bytes.


FR-ID-006/NFR-SEC-001/002 web gateway integration: owner export-job paths accept GET/POST;
export-file accepts GET only and rejects cross-site/same-site attachment requests. The attachment
uses the private cookie-derived Authorization header, requests identity encoding, rejects redirects
and keeps credentials out of URLs. Initial headers retain the eight-second deadline; successful
attachments move to the separate 300-second streaming deadline. Closed error mapping cancels the
unread upstream error body. Disconnects abort either phase. `make format lint test-tooling` passes
31 tooling cases, including ten new private-fetch/error/deadline cases. This supersedes the earlier
unwired-helper note; API registration and learner controls remain pending.


Snapshot sealing regression passes: after the export's repeatable-read snapshot is established,
the independent API commits the final diagnostic answer before export sections are read. The
result still contains the original 14 unreleased answers and no grades/mastery disclosure; retry
is byte-identical. A new request includes all 15 released results. `make format lint test-export-jobs
build` passes 41 focused PostgreSQL cases and the production web build. Final formatting/lint/types/
documentation/OpenAPI checks pass; generated application contracts remain unchanged.


Attachment navigation failure handling (FR-ID-006, NFR-SEC-001/002): before a successful
attachment response starts, a closed upstream failure on an explicit navigation returns a
no-store 303 to the fixed local privacy page. Its query contains only an allowlisted error code,
never credentials, record identifiers, diagnostics or a return URL. The privacy page resolves
that code to a fixed accessible alert. Programmatic requests retain JSON/status errors;
cross-site/same-site rejection does not redirect. Mid-stream errors still abort the transfer and
cannot be converted into a successful file or a late redirect. Native attachment links must rely
on server Content-Disposition, without a `download` attribute that might save a redirected page.
`make format lint test-tooling build` passes 32 tooling cases and the production web build.
Real Next/API HTTP checks are running through `make test-export-gateway`; these do not require or
claim a browser-engine download journey. Learner queue/status controls and API activation remain
pending under ADR-048.

`make format lint test-export-gateway` passes both real Next/API HTTP cases in 6.8 seconds.
Navigation gets a fixed local redirect and rendered alert; programmatic errors stay JSON;
unsupported methods and same-site/cross-site requests are denied. These HTTP-client checks do
not assert native browser save/cancellation behavior or successful MinIO attachment delivery.


FR-OPS-002/003 export monitoring: the existing ADMIN-only operations endpoint now includes
bounded queued/running/current terminal-failure counts and oldest pending age from durable SQL.
Failure observations include only currently FAILED jobs with finished_at in the inclusive last
24 hours; future finishes are excluded. Explicit retry removes the failed observation and resets
pending age; automatic retry retains the original command age. No identifiers, grant fields,
manifest/object references or source data are returned. Counts reuse the 10,000 cap/at-least flag.
The generated contract and operations page include the metrics and unavailable-state wording.
Configurable local warning defaults are OPS_EXPORT_FAILURE_THRESHOLD=1 and
OPS_EXPORT_AGE_SECONDS=300 (bounded 1–10,000 and 60–86,400 respectively). These engineering
thresholds are not legal fulfillment deadlines or proof of delivery. ADR-048 remains proposed;
export API/worker activation and learner controls remain pending.

Operations evidence: `make test-operations` passes 19 contract/PostgreSQL cases, including real
queue-to-running-to-terminal-failure/retry transitions, inclusive 24-hour bounds, exclusion of
future finishes, exact alert thresholds/recovery and minimized output. The first broad unit run
caught omitted EXPORT_FAILED/EXPORT_STALLED values in the analytics alert schema; the schema was
updated without weakening its exact-match guard. Final `make format lint test-unit build
openapi-check` passes 593 unit/contract and 32 tooling cases plus generated contracts and production
web build. Browser assertions for the metrics were added but remain unexecuted pending engines.


FR-ID-006/FR-OPS-002/NFR-MNT-001 launch policy: `make worker-exports` now defines the dedicated
single-concurrency prefork consumer, prefetch multiplier 1, explicit exports queue and importable
shared tasks. It starts no Beat scheduler. Native and Compose ordinary workers explicitly consume
only operations/imports/messaging. The normal development launcher still starts only the existing
ordinary worker/scheduler; export Beat registration, automatic startup and owner routes remain
disabled pending the complete slice. The manual consumer command is not feature acceptance.

`make format lint test-export-worker` passes seven cases. The real subprocess test derives its
launch flags from `make -n worker-exports`, substituting only the isolated synthetic application,
queue/node identity and diagnostic verbosity. A non-cooperative provider is hard-killed, a new PID
runs, the database lease recovers, and a message on another generated queue remains unconsumed.
The test removes only its own Redis namespace after stopping its subprocess group. Production
110/120-second limits remain unchanged; the test fixture accelerates them to 0.5/1.5 seconds.

Launch follow-up `make format lint test-unit openapi-check` passes 594 unit/contract and
32 tooling cases; generated contracts match. The separate seven-case worker run includes real
hard-stop and foreign-queue isolation evidence. Automatic launch/scheduler, owner UI and full
storage/browser acceptance remain pending; no commit or promotion is claimed.


Candidate wiring for local synthetic acceptance (not promotion): the application now registers
owned export commands/status/attachments and the two scheduled tasks. `make dev` starts the
dedicated consumer alongside the existing sole scheduler; the application Compose profile includes
an export-worker with its own targeted health check. Ordinary workers retain exclusive selection
of operations/imports/messaging. Container smoke includes and preserves the prior running state
of the new worker. Generated contracts include the actual registered owner endpoints.

Learner controls use the generated client for explicit prepare/status/retry, retain ambiguous
command keys in memory, and save READY copies via a plain attachment link without a Blob. A
separate synthetic E2E fixture uses in-memory encrypted objects; no live storage/model/messaging
provider participates in those tests. The real Next/API HTTP journey now passes command/replay,
READY polling, exact-length frozen attachment and pre-response failure navigation (three cases).
The registered API's 41 focused PostgreSQL cases and seven worker cases pass. Browser journeys
were added but remain unexecuted while engine installation runs. ADR-048's prior disabled notes
are historical; its promotion/release gate is unchanged. No production deployment is authorized.


FR-OPS-002/NFR-MNT-001: each Compose worker now checks its explicit node identity and requires
that node's pong. A healthy export consumer cannot mask an unavailable ordinary worker (or vice
versa). Deterministic checks exercise both actual Compose probes with own, foreign, missing and
invalid replies. This corrects health reporting; queue separation and the sole scheduler remain
unchanged. Runtime container verification remains pending image completion.


Health and gateway follow-up: `make format lint test-export-worker` passes all 15 cases,
including both actual Compose probes rejecting foreign/missing/invalid replies and the real
hard-stop/lease-recovery case. `make format lint test-export-gateway` passes all three real
Next/API HTTP cases. Unauthenticated attachment requests must now return exactly 401
REAUTH_REQUIRED (or the corresponding fixed navigation redirect); a missing route/404 no longer
passes the regression. These are not native browser download or complete container acceptance.
Docker PostgreSQL, Redis, Mailpit and web are currently healthy; API/worker images, MinIO and
browser engines are still building/installing. No commit or main promotion is claimed.


FR-ID-006 interrupted-download acceptance: the isolated E2E process now offers per-generation
corruption/stall controls over its in-memory encrypted store and a bounded 700-event synthetic
history. Installation refuses any database search path other than the harness's random E2E
schema. Fixture routes are absent from application entry points, images and generated contracts;
the web gateway does not expose them. No real storage or external provider participates.
Four deterministic fixture checks pass within the 606-case unit suite. New browser journeys
require mid-stream corruption/cancellation to fail, release the reader and preserve a complete
frozen retry. They are added but not yet executed pending browser installation. The actual
Next/API HTTP suite additionally exercises the same faults independently of native browsers.


Fault transport result: `make format lint test-export-gateway` passes all three HTTP cases
(8.7 seconds), now including a multi-chunk synthetic export, corrupt second-chunk failure,
client timeout/disconnect during a stalled second read, observed reader closure and exact frozen
retry after each failure. This uses the real API/Next transport with fake storage. It does not
substitute for native browser save/cancel or MinIO verification. `make check-docs` passes.


NFR-COMP-001/NFR-MNT-001: add `make e2e-chromium-full`, an explicit supplementary command
using the installed pinned full Chromium in new headless mode. It retains both shards and all
assertions; normal CI and the three-engine acceptance requirement remain unchanged. This allows
real-browser progress during the separate headless-shell download, without restarting the live
installer or substituting an unpinned system browser. Execution evidence follows separately.


First full-Chromium shard: 13/14 tests passed, including native background-command recovery,
saving frozen attachments, user cancellation, corrupt second-chunk failure and successful retry.
The old administrator privacy-review test selected every export in the shared queue; concurrent
new export fixtures made its final assertion ambiguous. Scope its export/deletion locators to
the exact references returned by that learner's requests, retaining all permission/review/
download assertions. Both Chromium shards are being rerun; no complete browser pass is claimed.


Full pinned Chromium result: `make format lint e2e-chromium-full` passes both shards,
14 + 14 = 28 tests (25 browser journeys and three HTTP-only gateway cases). This includes
background-command lost acknowledgement, native attachment saves/frozen retry, cancellation,
corrupt second-chunk failure and reader closure, existing privacy review/holds, operations
metrics, narrow touch reflow and the existing learning/content/channel journeys. The ambiguous
admin locator failure is resolved using exact owned references; no assertions were removed.
`make security-source openapi-check` also passes: no secret leaks and matching generated contracts.
Firefox/WebKit, default headless-shell execution, native MinIO, full application containers and
hosted regression remain outstanding. This does not grant production or ADR-048 acceptance.


Learner UI next-slice readiness: [review and acceptance plan](E6_LEARNER_UI_READINESS.md)
identifies the existing functional screens and the remaining shared navigation/home/recommendation
work for FR-REV-006 and NFR-ACC-001/BW-001/COMP-001. No visual acceptance or new feature is claimed.


Learner UI foundation candidate (FR-REV-006, NFR-ACC-001/BW-001/COMP-001): shared learner
navigation and skip link, consistent home/recommendation styling and explicit synthetic-preview
notice now use existing routes and API state. Shared navigation replaces redundant progress/history
menus; staff routes retain their separate workspace. Navigation prefetch is disabled. No backend,
consent, grade, mastery or retention behavior changes. New 320/1280-pixel, enlarged-text, keyboard,
axe and anonymous-state browser checks accompany the existing authenticated recommendation suite.
Build/lint/types passed before the new tests; full regression and screenshot review are pending.


Learner UI foundation verification: `make format lint build e2e-chromium-full` passes all
30 tests (15 per shard), including both new 320/1280-pixel home checks, 200% text reflow,
44-pixel navigation targets, keyboard skip/focus, active destinations, staff separation, axe,
and the existing authenticated recommendation/learning/privacy/channel journeys. Cold first-
question transfer is 175,609 bytes against the unchanged 250,000-byte ceiling. Desktop and
320-pixel screenshots were inspected with no clipping; local copies are under `.local/ui-review`.
The web container rebuild succeeded. This is Chromium engineering evidence, not full browser,
physical-device, screen-reader, academic, brand or pilot acceptance. Subsequent page design
and the remaining export acceptance gates are still open. No new ADR or API/migration is needed.


Onboarding presentation candidate (FR-ID-001/003/004/005, NFR-ACC-001/COMP-001): apply
consistent field/button/card styling and remove obsolete claims that learning and diagnostics
are unimplemented. When the server reports learning_allowed, offer the existing diagnostic
route as a next action. Preserve separate guardian verification/assent, withdrawal, OTP limits,
session security and synthetic notices. Browser and screenshot verification is in progress.

Local runtime update: API and ordinary worker images built and both containers are healthy.
Web, PostgreSQL, Redis and Mailpit remain healthy. Fictional email sign-in codes are available
only through local Mailpit at localhost:8025. MinIO and the dependent export worker remain
pending; do not equate partial stack health with complete export acceptance.


Onboarding result: `make format lint build e2e-chromium-full` passed 30 cases; after adding
explicit consent-gated next-action and onboarding reflow/screenshot assertions, `make format
lint e2e-chromium-full` again passed 30 cases. Desktop and 320-pixel onboarding screenshots
were inspected and retained under `.local/ui-review`. The rebuilt web container is healthy.
Existing adult/minor/guardian, withdrawal, cookie and retry protections continue to pass.

Local review setup: an initial assessment seed failed because the developer catalog was empty.
`make seed` populated S4/two subjects/six clusters; its storage-init step still fails because
MinIO is unavailable. Standard assessment/numeric/diagnostic/reassessment/multiple-choice seeds
then passed. The consecutive hints seed hit the existing shared fixture OTP cooldown; retrying
`make seed-hints` after the cooldown passed without weakening authentication limits. All fixtures
are synthetic and excluded from academic release counts. API, ordinary worker, web, PostgreSQL,
Redis and Mailpit are healthy; storage/export-worker and other browser engines remain pending.


Practice/diagnostic presentation candidate (FR-DIAG-004, FR-REV-005/006, FR-GRD-006,
NFR-ACC-001/BW-001/COMP-001): apply consistent question cards, selected answer controls and
primary submit actions. Shared SavedProgress displays only the server's saved-answer count,
never mastery or a diagnostic score. Preserve hint/solution gating, immutable submissions and
same-key retries. Browser assertions cover saved progress after acknowledgements, and captures
cover desktop/mobile questions. Verification is running; no acceptance claim yet.


NFR-MNT-001 container build refinement: copy workspace manifests and dependency patches
before installing the frozen web lockfile, then copy application/package source. This preserves
pinned dependencies and runtime image behavior while allowing ordinary UI edits to reuse the
install layer. The previous Dockerfile copied all source before installation, causing repeated
network downloads on every local visual update. Build/cache evidence remains pending.


Practice/diagnostic result: `make format lint build e2e-chromium-full` passes 30 cases after
the final spacing/button corrections. Native saved-progress values are checked against server
acknowledgements, including lost-response recovery; keyboard/axe/320-pixel journeys still pass.
Desktop practice/diagnostic and mobile practice screenshots were inspected. The rebuilt web
image now reuses the frozen dependency-install layer (`CACHED`) after a source-only change;
its latest container is healthy. No grading, consent or diagnostic disclosure rules changed.


Native storage gate update: the pinned MinIO source build completed and its service is healthy.
`make seed` now passes both catalog and private storage initialization. `make test-export-storage`
passes all 59 cases, including real signed async MinIO reads, scope/listing, encrypted round trip,
anonymous denial and owned-object cleanup. The earlier unavailable-MinIO failures are not waived;
`make migrate test security` is running again with storage available. The new export worker has
started and its readiness is being checked. Browser installation remains live.


FR-ID-006/NFR-MNT-001 full Docker delivery evidence: `make smoke-export` passed through
the running Next/API/ordinary Beat/export-worker/MinIO topology. A fresh fictional account
receives its OTP only in local Mailpit; the probe searches only its own unpredictable recipient,
verifies via secure-cookie gateway flow, queues a request and waits at most 45 status reads.
The real scheduled worker published a 2,191-byte private export; exact length, own identifier,
no-store and frozen retry matched. The probe revokes only its session; normal retention handles
its synthetic request/copy. No credentials, OTP, identifier or contents are printed.

Add this journey to `make container-smoke`, retaining existing preservation of already-running
services. Two deterministic fake-transport tests verify bounded local behavior and reject a
changed retry file; the unit suite passes 608 cases. Full native integration remains in progress.
This proves local delivery, not production or long-history load acceptance.


### Native regression acceptance update — 9 October 2026

FR-ID-006, FR-OPS-002/003, NFR-SEC-001/002, NFR-REL-002 and NFR-MNT-001:
`make migrate test security` completed successfully with 606 unit/contract, 32 tooling and
245 integration cases; the later two smoke-probe cases passed in the 608-case unit run.
Actual MinIO checks now pass, resolving the earlier unavailable-storage failures. Bandit,
secret boundaries and Python/Node dependency audits pass. `make recovery-drill test-web-content`
also passes: 56 tables/285 rows restored in 256 ms, immutable/export guards verified, and
one isolated content-admin browser case. Object-storage recovery and production RPO/RTO
remain unverified. Evidence: `.local/async-export-complete-native-regression.log` and
`.local/async-export-final-recovery-ui.log`. Remaining browser matrix, container vulnerability
scan and hosted CI still gate promotion; ADR-048 remains proposed.


### Progress and history presentation candidate — 9 October 2026

FR-MST-004/005, NFR-ACC-001/COMP-001/LOC-001/MNT-001: progress now uses responsive
subject/topic/competency cards with explicit evidence labels and the existing confidence-gated
mastery display. History uses consistent session cards and touch controls; empty history links
to the existing diagnostic. Authentication/consent blocks offer profile recovery. Private session
links disable prefetch. Server selection, paging, diagnostic sealing, confidence thresholds and
Kampala timestamps are unchanged. Browser checks now include 320-pixel progress/history reflow,
active navigation, history touch targets and screenshots. Lint/build/browser verification is
running; this entry is not acceptance. No API/migration change or new ADR is needed.


Progress/history verification: `make format lint build e2e-chromium-full` passes all 30
Chromium cases (15 per shard), including sparse-evidence suppression, offline recovery,
owned pagination, diagnostic sealing/resume, 320-pixel reflow and 44-pixel history controls.
Desktop progress and mobile progress/history captures were inspected with no clipping.
Evidence: `.local/progress-history-ui-checks.log` and `.local/ui-review/`. The web image
build passed and the restarted local web is healthy. No API, migration or ADR change. Remaining
engines, physical-device/screen-reader and pilot acceptance are still open.


### Privacy and channel presentation candidate — 9 October 2026

FR-ID-006, FR-WA-001/006 and NFR-ACC-001/COMP-001/LOC-001/MNT-001: apply the existing
card/control styles to privacy requests and channel linking, wrap long request references,
keep export actions usable at 320 pixels and remove duplicate learner Home links. Preserve
owner/re-authentication, ambiguous-command retries, explicit status checks, deletion-pending
wording and fake-only delivery. Link-code expiry now explicitly uses Africa/Kampala and a
semantic time element instead of the browser's local timezone. Browser checks include
320-pixel privacy/channel layout, privacy axe and the displayed expiry timestamp.
Verification is running. No API, migration, provider or architectural decision changes.


NFR-SEC-001/NFR-MNT-001 scan environment update: the native Trivy database download
exceeded its default five-minute deadline before scanning either image. The pinned CLI
confirms a `--timeout` duration option. `make security-containers` now supplies a configurable
30-minute per-image bound; database freshness, severity and failure rules are unchanged.
A retry is running. The initial run is recorded as incomplete, not clean.


Privacy/channel result: `make format lint build e2e-chromium-full` passes all 30 Chromium
cases (15 per shard), including mobile privacy axe, 320-pixel request-reference/control
reflow, background frozen export, lost command recovery and channel STOP/unlink. Link-code
time is checked against the server expiry in Africa/Kampala. Privacy/channel mobile captures
were inspected without clipping. Source/contract/doc checks pass. Evidence:
`.local/privacy-channel-ui-checks.log` and `.local/privacy-channel-contract-checks.log`.
Other browser engines and real-device/pilot acceptance remain open.


### Staff navigation candidate — 9 October 2026

FR-CNT-001/003/006, FR-OPS-002, FR-ID-006 and NFR-ACC-001/SEC-002/MNT-001:
add one shared staff header with links to existing content/review, imports, flags, privacy
review and operations routes. Active destination and 44-pixel controls support narrow screens.
No staff role is inferred from navigation; each existing API continues to enforce access.
No Audit link is invented while a dedicated audit screen remains absent. Learner navigation
stays separate. Browser checks cover narrow/wide header reflow, active destination, axe and
unauthorized operational denial. Verification is running; no API, migration or ADR change.


Staff navigation verification: `make format lint build e2e-chromium-full test-web-content`
passes 30 Chromium journey cases plus the isolated rubric-editor case. Narrow/wide captures
were inspected without clipping. Active navigation, 44-pixel targets, axe and anonymous
operations denial pass. Source secret, generated contract and documentation checks pass.
The rebuilt web image is ready for local review. Evidence: `.local/staff-navigation-checks.log`,
`.local/staff-navigation-source-checks.log` and `.local/ui-review/staff-*.png`. No new ADR
or API/migration change. Full browser/pilot acceptance and remaining staff page design are open.


FR-ID-006 promotion coverage audit: inspected explicit assertions for revoked publication,
12,000-event complete exports, late orphan cleanup, storage failure/retry, cross-owner reads,
mid-read cancellation/corruption and privacy access after consent withdrawal. The export
verification document records exact tests and remaining scope. Hosted/browser/container
acceptance remains pending; this review does not mark ADR-048 or the MVP accepted.


### Staff operational screens candidate — 9 October 2026

FR-OPS-002, FR-CNT-001/006 and NFR-ACC-001/COMP-001/MNT-001: apply shared control
and card presentation to operations, flag triage and synthetic imports. Group service health,
alerts and workloads into named regions; keep metric tables bounded at narrow widths.
No metrics are invented and missing data remains explicitly unavailable. Explicit refresh,
review/claim/retry, role checks and draft-only import behavior are unchanged. Operations
checks now include authenticated desktop/mobile captures, 320-pixel reflow and axe.
Verification is running; no new API, migration or ADR.


Staff operations result: `make format lint build e2e-chromium-full` passes 30 Chromium
journeys, including independent flag triage, bounded draft import and authenticated operations
at 320 pixels. Desktop/mobile operations captures were inspected without clipping; missing
heartbeat and unmeasured instrumentation remain explicit. Source, contract and documentation
checks pass. Web image rebuilt. Evidence: `.local/staff-operations-ui-checks.log`,
`.local/staff-operations-source-checks.log` and `.local/ui-review/operations-*.png`.
No API, migration or architecture changes; other engines/pilot gates remain open.


### Content editor presentation candidate — 9 October 2026

FR-CNT-001/003/005 and NFR-ACC-001/COMP-001/MNT-001: style the existing content/review
queue, staff preview, author fields and rubric/numeric controls consistently. Fieldsets have
bounded width and a named draft form; save remains explicit. No document/schema, review,
rights, eligibility or versioning behavior changes. The isolated controlled-rubric test adds
desktop/mobile captures, 320-pixel reflow and axe before verifying exact save/reload.
Verification is running. No API, migration or architectural decision changes.


Content editor result: `make format lint build test-web-content e2e-chromium-full` passes
the isolated mobile/axe/exact-rubric-save/reload test and all 30 Chromium journeys.
Desktop/mobile captures were inspected without clipping; the long authoring form still needs
human usability acceptance. Source/contract/doc checks pass. The web image built successfully.
Evidence: `.local/content-editor-ui-checks.log`, `.local/content-editor-source-checks.log`
and `.local/ui-review/content-editor-*.png`. No academic eligibility or publication change;
no API/migration or ADR change. Remaining browser/pilot gates stay open.


Native container security result: `make security-containers` completed successfully for both
`kasoma-api` and `kasoma-web` with the updated vulnerability database and no HIGH/CRITICAL
findings. Evidence: `.local/async-export-container-security-retry.log`. The initial attempt
failed before scanning due to the database-download deadline; extending only the finite
timeout resolved it. This closes the local image-scan gate, not hosted/latest-head browser
acceptance or production security approval.


Latest UI container verification: `make container-smoke` passes with all eight services healthy
and an actual scheduled owned export through web/API/Beat/export-worker/MinIO. The 2,191-byte
synthetic JSON copy has an exact-length frozen retry; the smoke session is revoked afterward.
Existing services remain running. Evidence: `.local/final-ui-container-smoke.log`.
The completed UI follow-ups are now queued for one final-head hosted run; the earlier candidate
run is superseded, not treated as passed. Main/ADR acceptance still requires the final run.


FR-ID-006/FR-WA-006/BR-010 readiness: [channel preservation assessment](E8_CHANNEL_HOLD_READINESS.md)
records concrete ownership, message disposal, STOP/unlink and relinking constraints from existing
code and database guards. It defines required ADR decisions and acceptance tests, not an accepted
implementation or legal decision. Current retention and incomplete-hold warnings remain unchanged.


FR-ID-006 / NFR-COMP-001 candidate acceptance update (9 October): two native
Firefox attachment cases fail in both the full first shard and focused serial reproduction.
Cancellation reader closure and corruption download completion remain unresolved; Chromium evidence
does not satisfy this gate. See [export verification](E8_ASYNC_EXPORT_VERIFICATION.md).

A plain HTTP native-download control reproduces both failures in pinned Firefox,
while Chromium passes. This narrows diagnosis; it does not establish Firefox acceptance
or replace the real-gateway requirement. The standalone diagnostic command starts no
application/database services.

NFR-ACC-001 / NFR-COMP-001: native WebKit export fault cases pass; its first-shard
keyboard test required macOS Option-Tab for links. The corrected test retains skip-link
and main-content focus assertions; all 30 native WebKit application cases pass; Firefox remains open.

FR-ID-006 / NFR-SEC-001 / NFR-COMP-001: delivery enforces a five-second object-read
bound independently of the storage adapter. The stalled-adapter integration regression
passes with all 42 focused export cases; Firefox stall/cancel/frozen retry now passes.
Raw native-manager corruption controls narrow the remaining automation discrepancy
but do not establish application acceptance. See export verification.

FR-ID-006 / NFR-COMP-001: the mandatory real-application Firefox corruption case
passes through the pinned browser's ordinary download manager, verifying rejection,
reader closure, READY state and byte-count/SHA-256-identical native retry. The driver
changes only that case's automation boundary; no requirement or failure is skipped.
Full Firefox and hosted final-head acceptance remain required.

NFR-ACC-001 / NFR-COMP-001: shared learner/staff navigation minimum height is now
48px, leaving margin above the unchanged 44px acceptance threshold after Firefox
reported fractional bounding-box values at an exactly 44px height. Full matrix pending.
The complete timeout-fix integration/security run passes 246 integration cases.

Final native follow-up evidence: all 90 browser executions pass (30 Chromium,
30 Firefox, 30 WebKit), including the mandatory real-gateway export faults and
48px navigation. All 246 integration cases/security checks and the later 625-case
unit plus 32-tooling run pass. Rebuilt eight-service smoke and API/web image scans
pass. Hosted final-head verification and ADR-048 promotion remain pending.

FR-GRD-004/005 and NFR-SEC-002: internal `services/short_text_contracts.py` adds bounded
answer input and distinct pending/neutral outcomes, rejecting scores and hidden/provider
material. ADR-050 remains proposed; runtime routes, worker and privacy integration are
not implemented by these contracts. Verification passes: 699 unit/contract tests (33 new outcome/input cases), 35 tooling
checks, format/lint/types and generated-contract comparison. No HTTP schema changed.

NFR-MNT-001: CI cache configuration passed remotely in run 37993094065, but PostgreSQL
pull throttling persisted. Optional read-only registry authentication is prepared; hosted
acceptance remains open. See [CI evidence](E9_CI_RUNTIME_VERIFICATION.md).

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

## 18 October 2026 acceptance reconciliation

FR-ID-006 / FR-OPS-002 / NFR-OBS-001 / NFR-MNT-001: main is `46a0f8a`, with
complete hosted runs 38033307073 and 38034913518 passing. ADR-048/049 now record
local synthetic acceptance. Completed export, timing and earlier short-text branches
are removed; the current grading branch retains the unpublished audit-ledger work.
FR-GRD-003/004 / FR-MST-001 / FR-ID-006: publication tests pass as recorded in the
[verification report](E4_PUBLICATION_VERIFICATION.md). Full regression passes 780
unit/contract, 35 tooling and 291 integration cases; 12 final publication and 13 band
cases cover later assertions. The security retry passes after a PyPI timeout.
No learner short-text grading, academic approval or production acceptance is inferred.

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

18 October verification follow-up: nine synthetic short-text browser executions pass
across Chromium/Firefox/WebKit, including 320-pixel neutral review, exact retry and
sealed diagnostic. Fourteen focused PostgreSQL cases prove duplicate claims cannot
restart model budgets, publication rollback preserves no partial grade/audit/mastery,
and revoked report authority after pass two prevents scoring. Broker-failure/SQL-atomicity
extensions and complete regressions are under verification. Source/dependency security
passes; the recovery fixture now includes encrypted rubric results (initial restore:
63 tables/602 rows/281 ms). Explicit restored decryption, final container checks and
full acceptance remain pending. See [current evidence](E4_SHORT_TEXT_FLOW_IMPLEMENTATION.md).

Final local follow-up: the stable complete browser command passes 99 executions;
18 flow cases, actual restricted-login publication, 831 unit/contract and 35 tooling
cases, lint/types, contracts, source/dependency security, populated encrypted recovery
and the rebuilt eight-service export/metrics smoke all pass. Grading uses its separate
queue and polling has server/client bounds. Broad backend and current container scans
remain in progress; expert review/rolling disablement and real learner enablement
remain unimplemented. Exact logs and limits are in the linked current evidence.

The broad backend run is now terminal: 307 integration cases pass in 901.92 seconds.
Its earlier collection is supplemented by the final 18-case flow and 831-case unit
runs above. Container vulnerability-database download and hosted verification still
gate promotion. This is verified disabled synthetic engineering, not MVP acceptance.

## Independent expert-review candidate — 18 October 2026

FR-GRD-003/004/005, FR-ID-003/006 and NFR-SEC-002: the next branch proposes ADR-051
and begins draft migration 0033 plus blinded review contracts. It addresses the
unimplemented completed-review/rolling-disablement path and adds release-unit sampling
to cover diagnostics that remain sealed. No application acceptance is claimed; tests,
staff/runtime wiring, exact holds, export/inventory and recovery remain pending. See
[readiness](E4_EXPERT_REVIEW_READINESS.md).

18 October recovery/promotion update: disabled learner-flow commit `853f80a` passes the
complete hosted run [39143803289](https://github.com/Jotham566/kasoma/actions/runs/39143803289)
including rebuilt-image security and container smoke. It is promoted to main and the
merged branch removed. Local scan interruption is not a local pass. The next review
branch remains uncommitted/unverified after its initial 20 contract/SQL cases; no
complete grading, real-data or MVP acceptance is claimed.

Historical pre-hosted FR-ID-006 / FR-WA-006 / NFR-ACC-001 capture evidence: full
1,055-unit/contract and 35-tooling suites pass; first full integration run passes
411/412, with a historical 0034 fixture invoking the current conversation ORM.
The corrected fixture retains original-schema JSON rejection and held-record replay
through forward upgrades; the corrected 21-case receipt/restricted-login suite passes.
All 108 browser executions, three UI harness and three
WebKit transport controls pass; the subsequent 44-pixel select regression reproduces
23-pixel native WebKit output and passes after scoped styling in all three engines
at normal and 200% text. Complete capture 39183714273 and latest 39185423895
supersede that pending engineering status; production acceptance stays separate.

FR-MST-004 / FR-MST-005 / NFR-PERF-001 / NFR-MNT-001 verified at `7148a1c`: request-local
immutable skill replay reuse under unchanged ADR-024, calculation time, hashes and
confidence/change semantics. Frozen 31 complete legacy summaries and
1,074 unit/contract cases pass; dense scoped replay work falls from 24 to eight
distinct calls. Complete hosted 39184552472 passes all 412 integration and full
browser/security/recovery/image/service gates. The verified sources are on main; merged branches are removed. Agreed-load hosted
latency remains gated. See [progress verification](E6_PROGRESS_REUSE_VERIFICATION.md).

NFR-ACC-001 / NFR-COMP-001 / NFR-MNT-001 candidate: shared single-select CSS now
reuses the verified native-menu appearance/arrow treatment. A new actual 320-pixel
journey assertion reproduces the existing 23-pixel WebKit practice selector before
the fix; all three normal/200%-text touch journeys and three staff UI checks pass.
Complete hosted 39185423895 passes at `6d53541`, including image/service and all
regression gates. Source is on main; merged branches are removed. No API, permission,
data or architectural decision changes. See
[select target verification](E6_SELECT_TARGET_VERIFICATION.md).


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

### ADR-070 implementation mapping — native prerequisite evidence

| Requirements | Implementation | Verification / remaining boundary |
| --- | --- | --- |
| Gate scope: FR-ID-003/005/006, BR-010 | `services/account_processing.py`, `services/identity.py`, `services/staff.py` | `test_account_processing.py`: SQL wait/recheck, cache refresh, schema separation and actual failed-unlock cleanup. No closed_at/executor authority. |
| Gate scope: FR-GRD-003/004 | `services/short_text_processor.py`, `services/assessment.py`, `services/grading_reviews.py` | `test_short_text_processing.py`: exact idle gate, success/failure release; existing withdrawal/band/budget controls. Normal scoring disabled. |
| Gate scope: FR-WA-006 | `services/whatsapp_processing.py`, `services/whatsapp_delivery.py`; linking through authentication | Shared account order preserved; full channel/browser regression still required. No new transport. |
| Gate scope: FR-OPS-003, NFR-SEC-002/MNT-001 | `scripts/erasure_identity_check.py`, `scripts/migration_diagnostics.py`, integration fixture | Two fixed fresh-source cohorts, unknown-target/interrupt cleanup, bounded sanitized migration categories. No cleanup of developer resources. |
| Gate scope: NFR-SEC-002, FR-ID-006 | `services/export_jobs.py`, `services/content_imports.py` | Existing account coordination and refreshed current user. Full exact-source worker/export regression remains required. |

Final scoped source passes1,471 unit/contract,110 resource/controller controls,29 native
identity/lifecycle/preview and19 native model executions. The schema isolation case
fails before the namespace fix (one failure/27 passes). The prior combined fixture's
setup cause is now reproduced with STORAGE_EXHAUSTED; that failed29-pass/15-error run
is not acceptance. Fresh fixed cohorts pass without raising memory/tmpfs/deadline caps.
Performance, final scoped recovery/security and own full hosted acceptance remain open.

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
