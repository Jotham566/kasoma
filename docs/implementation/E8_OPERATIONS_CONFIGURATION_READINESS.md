# Versioned operations configuration readiness

19 October2026. FR-OPS-002/003,NFR-SEC-002/OBS-001/ACC-001/LOC-001/MNT-001.
[ADR-067](../decisions/ADR/067-versioned-operational-warning-configuration.md).

Read API section9, SRD administrator/operations scope, bootstrap configuration, security
and UX; inspect ADR-033/053, existing OperationThresholds/Settings bounds, staff/recent
OTP authorization, immutable AuditLog, request retry conventions and current staff UI.
The generic configuration route is absent. Existing warning values come from Settings.
No conflicting accepted decision requires them to remain startup-only forever.

Implement a closed15-key numeric warning configuration, version-reference checks and
existing-audit-backed exact retry authority. Keep secrets, academic controls, hard caps,
consent/retention, provider and activation outside this allowlist. Global version rows
hold no learner/actor/contact/answer or free text; AuditLog remains the existing staff
accountability authority. The current erasure proposal is not approval; refresh the
source inventory/disposition for the new shared configuration tables before its review.

Additive schema/API/service, existing worker snapshot integration and Operations-linked
UI form the complete slice. Configuration0 preserves environment defaults until the
first explicit administrative edit freezes the full resolved map. A changed environment
invalidates a stale version0 form. Exact retries return the original recorded version;
subsequent current configuration is loaded separately. Lost acknowledgement never silently
regenerates a key or overwrites a newer version.

On unavailable configuration, saved-state editing is unavailable; operational warning
sampling applies its explicitly labeled startup defaults and a warning, preserving core
unconditional alarms. No processing policy is inferred from a warning threshold.
Required gates: contracts/ranges, real PostgreSQL concurrency/SQL/rollback/role/worker,
three-engine browser/a11y/retry, clean/upgrade/restricted-login/populated recovery, normal
quality/security/images/service and own full hosted acceptance. No inference, external
model/messaging/cloud call, real data or destructive migration is needed or authorized.

## Verification in progress and retained failures

Initial30 focused cases pass23.50s; the expanded31-case rollback suite passes27.76s.
Initial logical restore at0043 passes71 tables/691 rows305ms; separate actual MinIO
restore passes71/691/one42,060-byte object179ms, sources stopped, integrity probes and
cleanup empty. Actual restricted-login test passes9.65s; initial quality/contracts/build,
source/dependency security and image/service smoke pass with eight healthy services.
Normal synthetic preview is advanced additively to0043 without cleanup or activation.
These checks precede0044 and do not accept that newer guard.

Retain failures: direct pytest invocation lacks the Make PATH for subprocess uv; a test
module name collision stops collection; test expectations initially use403 instead of
existing REAUTH_REQUIRED401, and literal JSON is parsed as a SQL bind. All corrected in
the focused tests. A worker-observation spy initially accepts four instead of seven
arguments; fix the spy without weakening the actual worker execution. The new upgrade
probe exposes trailing-public configuration fallback; require exact current-schema tables.
The first0044 draft accidentally includes0043 table creation and is refused by duplicate
relations in isolated upgrades; restrict0044 to CREATE OR REPLACE FUNCTION only. That
draft never advances the normal preview to0044.

Initial browser trials detect overflow at320px/200% text, including a WebKit-only residual
scroll extent after form bounds fit. Root/element geometry and screenshots are diagnostic;
no clipping of the document or relaxed reflow assertion is accepted. Final three-engine
acceptance remains pending. Keep original full-regression interruption explicit:1,277
unit/contract pass; integration is intentionally interrupted after47 passes/231.14s to
freeze corrected tests and SQL before restarting. It is not a full regression pass.
Two broad read-only catalog counts hit existing statement timeouts; indexed per-relation
inspection succeeds71 tables/501 columns/121 FKs/102 triggers, without timeout increases
or schema cleanup. Both parent candidates have since passed their own hosted runs;
none of that parent evidence accepts this configuration implementation.

## Frozen0044 candidate evidence

make test-operations-configuration passes34 contract/actual PostgreSQL cases in52.92s,
including every stored lower/upper range, stale/multi-key SQL rejection, independent
worker defaults, exact concurrent retries, recent/revoked roles, injected audit rollback,
chunked byte limits and populated0042→0044 preservation. Current-schema lookup is now
explicit; a pre0043 isolated schema cannot fall through to the review database.

The final dedicated browser journey passes once in each Chromium/Firefox/WebKit engine:
edit, actual committed lost response, same-key retry, stale conflict, offline/reload,
keyboard,320px/200% text and Axe. Native control overflow handling and two paint frames
preserve the strict document scroll-width assertion; document overflow is not hidden.
Initial broad runs and the invalid0044 draft remain failures above. The final candidate
uses a separate Playwright config/schema to avoid changing other suites' global warnings.

make format/lint, generated OpenAPI/client check, type checking (208 source files),
build, dependency/source security and final image scans pass. make migrate seed and
container-smoke advance the normal synthetic review DB to0044 and pass frozen export,
request/model probes; eight services remain healthy. No configuration edit or provider/
retirement/short-text activation is performed in that review database. Full frozen
backend/browser regression and own exact-source hosted run remain required before merge.

Final0044 source repeats both populated drills successfully: logical71 tables/691 rows
476ms, and actual database/MinIO71/691/one42,084-byte object173ms. Both report empty
cleanup, immutable guards and retirement denial. Actual restricted-login test passes
10.39s. The frozen full unit/contract suite passes1,277 cases6.03s with35 tooling checks;
512-case integration and full117-execution browser regression are running, not accepted.

## Candidate publication and bounded native review

Exact candidate3e6175bfd8d4b501aa5a01c2432bbe32bbf33bc2 is pushed for its own complete
hosted [39322035839](https://github.com/Jotham566/kasoma/actions/runs/39322035839),
confirmed in progress. Keep that remote head unchanged while it runs. Main is separately
verifiedeb05457706ad70b3ebda4a16b41567ddfe542652: both completed parent branches have
been removed locally/remotely after remote SHA and ancestry proof. The active configuration
branch remains intentionally unmerged until its own required verification passes.

Native Microsoft Edge Beta accessibility becomes available after the user's unlock.
In a separate newly created local preview tab, the warning-settings layout and unauthorized
load feedback are visibly correct; native F6/Tab entry reaches Skip to content and Return
changes the fragment to#main-content and focuses its container. The active native window
then changes during the next keyboard action, so review stops without further keyboard
input or assumptions. No native full journey, physical device, screen-reader or branded
release acceptance is inferred. No OTP, role grant, learner data or setting mutation is
performed in that manual session. The native temporary tab is not closed after the active
window changes; do not risk closing an unrelated user window. Existing user tabs are preserved.

## Retained full-browser failure during overlapping local regression

The first frozen make e2e run passes both17-case Chromium shards, then fails three
Firefox shard1 journeys with14 passing: lost-acknowledgement assessment gets HTTP500,
rubric creation returns no expected document, and diagnostic progression does not reach
its third saved answer. It stops there; neither remaining browser coverage nor the full
117-execution gate is accepted. HTTP500 response-start times include2104,2077 and2141ms,
but that timing does not establish the exception or cause. Deliberate incomplete-export
transport errors in other passing fault tests are separate expected probes.

This browser run overlaps the512-case integration run against the same development
PostgreSQL service. A read-only aggregate catalog probe finds10,222 retained identity_test
schemas and about2,293,760 table/index bytes in the latest synthetic schema. No schema,
role, volume, cache or data is removed. A20-minute aggregate Docker-log error probe finds
no classified database errors; it does not establish absence of SQL errors or causality.
The limited resource snapshot (PostgreSQL about40% CPU/892MiB;16GiB free host disk) is not
a performance acceptance or reconstruction of the failure moment. Finish the unchanged
backend run, then repeat full browser verification serially under unchanged gates.
The hosted exact3e6175b run continues; do not replace its head or infer local acceptance.


## Frozen local backend verification —20 October2026 Kampala

make lint openapi-check build test completes successfully at the unchanged3e6175b
runtime/test/Makefile tree (only approval Markdown follows).35 tooling,1277 unit/contract
and512 integration cases pass; integration duration2290.76s. The expected Starlette
httpx deprecation warning remains visible. This is a terminal exit0, unlike the earlier
interrupted run. Hosted39322035839 has passed its backend gate and is in full browser
verification; complete hosted acceptance is still pending.

The earlier local Firefox three-case/HTTP500 failure remains FAILED and unexplained.
Full local browsers will run serially after the isolated follow-up metadata/disabled-role
checks finish. No SQL timeout, retry, assertion, database schema or cleanup policy is
weakened; the previous failure is not attributed to concurrency without evidence.


## Serial browser failure and bounded diagnosis candidate

The serial make e2e run is terminal FAILED at Chromium shard1:15 passed/two failed.
Assessment submission returns500 in2252.781ms and the resumed keyboard journey never
reaches Answer saved. Export-request creation returns500 in2731.831ms before the
intentional mid-transfer corruption scenario. No later shards/engines execute. The
previous concurrency explanation is unproven and insufficient. The frozen backend
pass does not accept this browser result. Main promotion remains blocked by verification.

Read-only aggregate Docker log probes return no PostgreSQL log lines; empty capture
cannot establish absence of SQL errors. Private transfer truncation errors occur in
these logs but do not establish the cause of the earlier export-request creation500.

A separate test-only candidate attaches an SQLAlchemy handle_error observer solely to
scripts.e2e_api's fresh owned e2e UUID schema and fake provider profile. At most16 events
per process contain only six static driver-error categories and elapsed milliseconds.
No SQL, parameters, exception message/repr, body, credential, source ID or error details
are inspected/output. Optional diagnosis never suppresses/replaces the original error.
Normal API/worker entrypoints never import this helper. No timeout, retry, assertion,
schema-retention policy or developer resource is changed. Focused denial/privacy/bound
controls precede a diagnostic Chromium reproduction; this is not a claimed runtime fix.
Hosted39322035839 remains pinned at3e6175b and cannot accept this new local harness.


The final diagnostic source passes16 focused controls and1293 unit/contract cases,
35 tooling, lint/types (209 checked sources), matching generated contracts, Bandit and
dependency audits. The new helper is explicitly included in mypy/Bandit. Earlier
interleaved local check output is not used as the final evidence; the serial final
command has its own log and exits0.

Diagnostic Chromium passes both17-case shards (36.2s/32.1s), with no database-failure
event observed. Intentional corrupt-transfer pipe errors remain visible. This does not
reproduce or fix the prior500s and does not establish their cause. Remaining browser
engines/profiles are running serially with the same assertions and existing deadlines.


## Complete hosted result at frozen configuration source

Hosted39322035839 is SUCCESS at exact3e6175bfd8d4b501aa5a01c2432bbe32bbf33bc2.
All required steps pass:1277 unit/contract,512 integration (1574.89s),35 tooling,
117 full browser executions plus focused content/attachment/interception/assessment/
rubric/role controls, setup/clean migrations/seed/quality/contracts/build/security/
images/service smoke. Logical recovery verifies71 tables/691 rows in531ms; actual
PG/MinIO verifies71/691/one42,060-byte encrypted object in308ms, correct scope,
source services stopped, missing/corrupt rejection, immutable guards, retirement denied
and no cleanup failures. Production RPO/RTO remains false. Optional registry-login
skip is conditional; mandatory gates all succeed.

Local diagnostic Firefox still fails one assessment case (16 pass) with a2056.774ms
HTTP500; later engines/profiles are unexecuted. No fix is established. Playwright ignores
server stdout by default, so the initial print observer was not visible in captured
logs. The corrected candidate writes the same bounded fixed categories to stderr;
privacy tests now assert stdout stays empty. This is a diagnostic visibility correction,
not a new timeout, retry or runtime fix. Fresh checks/reproduction use separate logs.

Main promotion remains deferred while the local failure is investigated. Hosted success
at3e6175b cannot accept the separate diagnostic harness or ADR-061 foundation source.


The stderr reproduction records QUERY_CANCELLED immediately before the assessment500
(response start2106ms), then ends FAILED (16 passed/one failed). This establishes a
cancelled database query in the failing request; it does not yet distinguish a user
lock, expensive read/write, other cancellation or the source of waiting. No blanket
concurrency or catalog-bloat explanation is claimed.

A further bounded diagnostic tags only READ/fixed write classes from compiled SQLAlchemy
metadata, plus exact equality with the fixed parameterized user-advisory-lock template.
Neither parameter values nor SQL bodies are emitted; unknown tables/templates become
WRITE/OTHER. Source names never become log labels.24 privacy/scope/operation controls,
1301 unit/contract,35 tooling and quality/contracts/security pass. The first mypy attempt
catches Join lacking a table name; explicit TableClause handling corrects it. A fresh
Firefox reproduction is running with this source and unchanged deadlines/assertions.


## ADR-068 browser database isolation candidate

Read-only pg_catalog statistics estimate10842 namespaces and11,307,737,088 bytes across
pg_class/pg_attribute/pg_constraint/pg_depend/pg_namespace with indexes/TOAST. Tuple
estimates are3,226,840/15,456,539/3,806,169/22,997,306/10842 respectively. No learner
row is selected. This is a shared catalog dependency/reproducibility risk, not proof
of the cancelled query's cause. The operation-tag Firefox run passes shard1 but fails
numeric worked-solution visibility in shard2 (16 pass), with no solution request or
500 in that learner trace. It is a separate unresolved pointer/enablement transition.
The unchanged focused assessment target passes all nine executions; this is no fix.

[ADR-068](../decisions/ADR/068-owned-browser-database-services.md) gives only the standard
synthetic browser API a fresh approved PostgreSQL/pgvector container per process. It
reuses existing exact creation-ID/label/no-volume guards with a closed browser purpose
and distinct labels;512m memory,256 pids,256m tmpfs and random loopback port. Private
DB/encryption/lookup/JWT keys are fresh. The existing e2e UUID schema, fake providers,
export fault routes and deadlines/assertions remain. No fallback or existing data/cache/
volume/schema cleanup occurs. The configuration profile inherits the same API isolation; the separate short-text
API keeps its existing scope.

The current root branch is codex/browser-isolation; accepted configuration remote3e6175b
is preserved. New bounded startup/cleanup/profile/private-key/purpose controls and all
existing recovery resource controls precede actual browser verification and its own
complete hosted source acceptance. No test-resource cleanup is account erasure.


Shutdown inspection of the pinned Uvicorn source confirms it re-raises captured SIGTERM
with original handlers after server shutdown. The browser entrypoint therefore uses a
test-only handler that unwinds its owned context, and Playwright requests SIGTERM with
a ten-second cleanup budget. HTTP/SQL/assertion/test deadlines are unchanged. An actual
signal unit case verifies cleanup and previous-handler restoration. The controller emits
only returned container ID/invocation and final cleanup failures as infrastructure
metadata, never credentials or learner IDs; this records creation provenance for this
run rather than discovering resources by name. Unexpected setup/body diagnostics are
withheld after attempting owned cleanup. Actual container/browser acceptance is pending.


ADR-068 foundation checks pass:78 combined browser-resource/existing object-recovery
controls,24 failure-diagnostic controls,1320 unit/contract,35 tooling, lint/types (210
sources), matching generated contracts and security/dependency checks. Fresh invocation
DB/encryption/lookup/JWT keys are preserved when adding the existing e2e schema options.
An unexpected setup/body exception is withheld after owned cleanup. The first actual
fresh-container Firefox run is in progress; these unit controls alone do not accept it.


The first actual fresh-container Firefox target passes both17-case shards (30.8s/29.5s),
with two empty cleanup reports. Independent exact-ID inspection confirms both returned
containers absent. The eight normal review services stay healthy. An ID/label-checked
read-only snapshot of a live Chromium fixture finds the same five system catalogs total
2,801,664 bytes, compared with the shared database's11,307,737,088-byte observation.
These are separate environments/observations, not causal attribution or production
performance evidence. Remaining browser profiles are running; no full acceptance yet.


## Complete local browser cohort with owned fixture services

The final unchanged source passes all117 executions: Chromium34, Firefox34, WebKit34,
short-text12 and configuration3. The four remaining standard shards pass17 each in
20.9s/20.6s/24.8s/24.5s; short-text four per engine31.3s/32.0s/32.7s; configuration
one per engine10.9s/11.7s/10.7s. Together with the earlier Firefox34, the commands exit0.
All nine standard/configuration returned containers report empty cleanup and independent
exact-ID inspection confirms all nine absent. The separate short-text API retains its
previous schema scope. Normal review services stay healthy; no existing resource is swept.

This accepts the local browser-isolation behavior only. Previous failures and unknown
causes remain recorded; source-preserving fresh isolation is not a proved historical
root-cause fix. Complete combined backend/recovery/images/service and exact-source
hosted verification remain required before main promotion. Main remains eb05457.


The local-only provisioner additionally refuses TCP/SSH Docker endpoints, including a
remote selected context, before daemon/image/resource commands. It pins the verified
Unix endpoint for child commands and restores the original process environment on exit;
no global Docker context is changed.86 combined browser/recovery controls and1328 unit/
contract plus35 tooling/lint/types pass; a mocked content UI target also passes3 cases; actual three-engine assessment controls
are now running before integration with separately hosted-verified ADR-061 source1851740. The existing
recovery profile/55432 guard is unchanged. No remote Docker/cloud provisioning is added.


The pinned-local-endpoint source passes all nine actual assessment executions across
Chromium/Firefox/WebKit (14.8s/16.9s/16.5s), with three returned creation IDs and three
empty cleanup reports. The mocked content target's earlier3-case pass was only a UI
control, not database acceptance. Full combined-source verification still follows.
