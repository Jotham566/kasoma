# ADR-061 synthetic account closure — implementation readiness

Requirements: FR-ID-006, BR-010, FR-OPS-003, NFR-SEC-002 and NFR-MNT-001.
Status: first lifecycle slice in progress; no execution or completion acceptance.
The human approval in [ADR-061](../decisions/ADR/061-synthetic-account-erasure-proposal.md)
includes the0044 source addendum. It excludes the normal review database, real data
and production. The entire approved lane still requires its preservation, removal,
finite retirement and recovery acceptance; initial closure is not rights fulfillment.

## Repository assessment and first slice

The existing pending DELETE intake, independent ADMIN claim, advisory inventory and
19 exact hold kinds are present. There is no account closure timestamp, durable erasure
job or erasure executor. Existing ACTIVE status checks stop several protected paths,
but do not constitute a permanent closure barrier or a verified race protocol. Existing
EXPORT retirement credentials/functions grant no account-erasure authority. Genuine
staff provenance and ambiguous embedded references must block before account closure.

Retain the approved modular monolith, Next.js/FastAPI, SQLAlchemy/Alembic, PostgreSQL,
Redis and private local adapters. No provider, consent, retention or grading thresholds
change. Work is isolated from the configuration candidate's frozen verification source.
Do not start a second Compose project or apply erasure execution to review public.

The first vertical slice is an independent recently authenticated ADMIN authorizing an
owned isolated synthetic DELETE case against a fresh version-bound plan. Database-clock
closure stops authentication, learning, linking, grading and dispatch publication; a
restart resumes the same durable job. Preserve the existing learner IN_REVIEW status.
No initial phase may mark completion or remove owned history. Complete exact-source
preservation, removal and retirement follow under the same approved decision.

## Contract boundary and implementation choices

[Closed contracts](../../services/erasure_contracts.py) accept only plan UUID,64-hex
version, decision UUID and an actual affirmative boolean. They reject subject IDs,
SQL, source/table selectors, cutoffs, bypasses and completion overrides. A plan has a
positive lifetime of at most ten minutes, aware timestamps, exact versioned policy/
manifest identifiers and distinct fixed blockers. Availability agrees with blockers;
it is not an executor capability or SQL clearance.

Status retains the last durable phase with a separate fixed blocker or failure code.
This represents FAILED/BLOCKED without losing restart position. Closure and completion
timestamps must agree with that phase and chronology. No source keys, private cursor,
contact, payload, token or raw diagnostic is accepted by these response types. These
types are not mounted API routes yet; no generated contract change is claimed.

The policy identifier is synthetic-account-erasure-v1; the approved baseline manifest
identifier is erasure-0044-v1. Subsequent additive lifecycle/preservation sources must
receive explicit dispositions and a new manifest version before authorization. These
identifiers are format choices within ADR-061, not new architecture or retention rules.

The [private profile](../../services/erasure_config.py) defaults disabled, reads no shared
.env and adds no credential to ordinary Settings. Only fake providers and development/
test are accepted. Loopback PostgreSQL must name an isolated identity_test UUID schema
or a dedicated kasoma_erasure_test UUID database; ordinary review public, Compose service
aliases, remote URLs and URL query overrides are refused even when disabled. These name
checks are necessary fences, not creation/ownership/SQL capability proof. Future execution
must independently validate the exclusively provisioned scope and restricted login.

The dedicated file loader checks its open descriptor for ownership, regular-file type,
private permissions and an8192-byte bound; symlinks and FIFOs are refused. Dotenv
interpolation is disabled, foreign/unknown keys fail validation and diagnostics are
withheld. No provisioner, SQL function, private entrypoint or normal-stack activation
exists at this stage.

## Local verification of the initial contract/profile source

make setup succeeds in the managed worktree, preserving an exclusively copied0600 local
environment. It starts no second Compose project. The initial52 contract cases and1329
unit/contract tests pass; after adding the private profile,75 focused and1352 unit/
contract tests pass with35 tooling checks. Existing socket-denial warnings are expected
failure-path probes, not external application calls. Generated OpenAPI/client checks
match because the new types have no routes yet.

The first lint attempt catches a formatting issue; the next catches a typed-constructor
error in the private loader. Repository formatting and model_validate correct those
issues; subsequent lint/Python/TypeScript checks pass. Dependency/security checks subsequently pass. These are initial foundation checks, not closure, integration, migration,
browser, restricted-role, recovery or complete hosted acceptance.

## Remaining implementation and acceptance

1. Executable closed source/disposition validation; lifecycle migration and permanent
   closure marker; independently provisioned isolated capability with SQL denial guards.
2. Exact independent claimant/plan authorization and atomic closure, all authentication,
   learning/channel/model/export races, crash/retry and restart invariants.
3. Case-only API/generated contracts and accessible confirmation/retry/conflict UI.
4. Full preservation/custody, bounded restricted removal, academic band disablement,
   finite accountability and quarantine/checkpoint recovery under ADR-061.
5. Clean/additive migrations, actual restricted logins, unit/integration/browser,
   quality/security/images/service/recovery and exact complete hosted verification.

Use make test-erasure-contracts for focused authority/format/chronology/profile denials;
make test-unit and make lint remain broader gates. No first-slice or full MVP completion
is inferred from contract checks.

## Structural manifest foundation

The immutable [source manifest](../../services/erasure_manifest.py) freezes all71 approved
0044 sources,501 ordered column name/type/nullability definitions and actual primary
keys, with the exact disposition codes from the approved proposal. Runtime code never
parses Markdown or accepts user-selected table/column names. Contract tests independently
compare the69 original table definitions to the factual inventory and the complete
primary-key/disposition map to the approved manifest, including the two shared controls.

The [read-only fence](../../services/erasure_inventory.py) inspects the current schema's
indexed catalogs and explicitly qualified migration marker. It refuses changed revision,
source set, key or column shape. Unknown foreign/materialized/view sources, changed relation kinds and custom
column types cannot silently disappear from inspection. Fixed catalog bounds exceed the
known baseline; mismatches produce only SOURCE_MANIFEST_CHANGED. It reads no learner
rows, embedded payload, identifier lookup or credential. It is not permission to mutate.
Type modifiers, CHECK/trigger definitions/grants, payload versions, ownership, preservation, locks and
all other execution prerequisites remain separate required checks.

The expanded source passes89 focused contract/profile/manifest cases,1366 unit/contract
and35 tooling checks plus lint/types. One actual isolated catalog/drift integration case
is written but deliberately queued until the separate configuration full backend run
finishes; migration-heavy concurrent verification previously produced unexplained browser
failures. No integration acceptance is inferred from static manifest equality. The source
has no own hosted acceptance and is not ready for main promotion.


## Existing disabled-account provisioning guard

Inspection finds local staff provisioning takes the account lock but never checks the
user's status before granting a role. The candidate now re-reads that user under the
same lock and refuses every grant/regrant for a disabled identity. Explicit role
revocation remains available and audited without reactivating the user. The new actual
integration case checks rejected ADMIN/regrant leaves roles and audit unchanged, then
permitted revocation removes the existing role with one audit. It is queued with the
metadata integration case until the frozen parent backend run ends.

This is a prerequisite protection on existing DISABLED state, not the permanent
closed_at implementation. SQL role-write barriers, closure-marker irreversibility and
all provisioning/closure races still need the lifecycle slice. No account is closed
or granted new authority by adding this check.


## Closure race inspection for the next implementation step

| Existing path | Observed coordination | Required closure acceptance |
| --- | --- | --- |
| Identity authenticate/refresh | Per-user keyed advisory transaction lock; ACTIVE check | Independently reject immutable closed_at; serialize permanent closure and refresh/reuse cleanup |
| OTP verify | Challenge row and identifier advisory lock; existing-user ACTIVE check without user lock | Acquire/recheck the existing user under closure coordination before credential creation; retain identifier ownership until old unbound challenges drain |
| Staff provisioning | User advisory lock; candidate adds disabled grant denial | SQL/application permanent-closure denial for new roles; revocation must remain possible |
| Web/shared assessment | User advisory lock and fresh ACTIVE/consent checks | closed_at check and independent SQL write barrier across owned learning publication |
| Short-text dispatch | Rechecks material before each call; callback transaction ends before provider invocation | A check alone leaves a dispatch gap: coordinate actual invocation with closure, within existing finite budgets; no provider/profile expansion |
| Short-text finish | User lock; absent material can still create a neutral terminal result | Explicit cancellation after closure; do not publish a new grade/mastery/diagnostic result as neutral cleanup |
| WhatsApp processing/delivery | User-before-global-channel locks; current ACTIVE/consent checks | Same closure order and fresh closure denial; keep STOP/unlink/privacy receipt handling available |
| Export snapshot/publication | Owner/job locks plus fresh SQL grant validation | Drain all accepted requests/copy cleanup before closure; no later publication or lost cleanup locator |
| Exact holds | Existing case/source guards and capture locks | Revalidate before barrier; new decision must atomically preserve or conflict under compatible locks |

These are source-inspection findings and required tests, not demonstrated vulnerabilities
or completed race fixes. The dedicated user closure marker, fixed SQL capability and
all mutation/dispatch guards must ship together before the first barrier is enabled.
Direct restricted-login tests must independently prove the denial; mock/session-only
checks cannot establish SQL enforcement. No statement/lock timeout or academic gate is
to be relaxed to make these races pass.


The final foundation source passes93 focused and1370 unit/contract cases,35 tooling,
lint/types, matching generated contracts, Bandit, dependency audits and source gitleaks.
The first Bandit attempt flags string-built qualified marker SQL despite identifier
quoting; the correction uses psycopg Identifier composition without suppressing the
scanner. No raw caller SQL is accepted. Web build also passes; no web source changed.
The two actual database cases remain pending behind the frozen parent suite.

Private-loader review additionally rejects every key outside the explicit public model
fields before constructing BaseSettings, including _env_file, _secrets_dir and parser
options. Canonical uppercase names avoid alias collisions.97 focused and1374 unit/
contract cases now pass with35 tooling and all quality/contracts/security/source checks.
The final private configuration remains absent; no erasure capability is provisioned.


## Actual isolated prerequisite verification

After the frozen configuration backend completes, make test-erasure-source passes both
actual integration cases in12.03s, terminal exit0. The fresh isolated0044 catalog matches
all71 baseline definitions. Extra text/custom-type columns and an extra view are refused;
fixture savepoint rollback restores the original shape. Disabled-role grant/regrant
attempts leave roles/audit unchanged, and explicit revocation adds exactly one audit
without reactivation. No review-public row is selected or modified by these probes.

All final foundation checks are local:97 focused,1374 unit/contract,35 tooling, two
actual integration cases, lint/types, generated contracts, build, Bandit, dependency and
source scans. No closure migration, erasure provisioning, API/UI, executor or removal
exists. Full combined backend/browser/recovery/images/hosted acceptance still follows
when the first complete lifecycle vertical slice is implemented. No MVP fulfillment or
permanent closure is claimed from this prerequisite commit.


Foundation source185174090d05c03127169df29271c03c85b3b2b3 is committed and pushed on
codex/erasure-lifecycle for its own complete hosted verification39328044945, confirmed
in progress. Its remote head stays unchanged while live. Main promotion and complete
lifecycle acceptance remain pending; a green parent/configuration run cannot accept
this separate prerequisite implementation.


## Complete hosted prerequisite verification

Hosted39328044945 is SUCCESS at exact185174090d05c03127169df29271c03c85b3b2b3:
1374 unit/contract,514 integration (1274.14s),35 tooling and117 full browser executions
plus all focused/setup/migration/seed/role/quality/contracts/build/security/images/service
gates. Logical recovery verifies71 tables/691 rows in607ms. Actual PG/MinIO recovery
verifies71/691/one42,060-byte encrypted object in193ms, with source services stopped,
exact storage scope, missing/corrupt rejection, immutable guards, retirement execution
denied and no cleanup failures. Production RPO/RTO remains unverified.

This accepts the closed contract/private-profile/structural-fence/disabled-role prerequisite
implementation only. It does not implement permanent account closure, routes, provisioning,
erasure, richer preservation, finite retirement or DELETE completion. Only Markdown
closeout follows the verified source; main integration still requires combined-source
verification with the separate browser-isolation work. Normal review execution stays off.

## Existing-login coordination candidate

The next implementation addresses the OTP race from the matrix above. Verification
pre-reads only a challenge's LOGIN type/lookup selector and current identifier owner,
then takes the existing keyed user transaction lock before consume/identifier locks.
It does not cache a Challenge ORM object before its locking consume query, which
would risk stale single-use state. LINK already holds its authenticated user's lock.
The serialized lookup must match that selected user; a changed/new binding refuses
credentials with the existing generic authentication error. The user status is
reloaded after the lock. This avoids a lookup-to-user lock inversion with LINK.

Tests add a real transaction holding the user barrier while verification starts,
a controlled concurrent new identifier binding and a second single-use concurrency
profile for an already registered user. Existing identity and LINK tests remain.
No SQL session-insert guard, immutable closure marker, OTP dispatch lease, erasure
capability, export/model/channel barrier or request completion is supplied by this
change. Those remain part of the required first vertical slice. Results are pending.

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

## SQL lifecycle work in progress on codex/erasure-barrier

FR-ID-003/005/006, BR-010, FR-OPS-003 and NFR-SEC-002/MNT-001: begin the private
control/plan/job mappings and a nullable deferred User.closed_at mapping. Deferred
server-default loading preserves pre-closure migration fixtures without inventing
closure dates. Add an HTTP regression refusing client-supplied closed_at/status while
leaving access and profile unchanged. The lifecycle SQL migration, permanent clock/
role/ownership guards, independent provisioning, atomic closure and resumable worker,
contracts/API/UI and full first-slice verification remain to be implemented. These
mappings are not yet migrated/registered and grant no activation or erasure authority.

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

## ADR-070 native scope and cleanup evidence

The SQL gate key includes the current schema OID and uses only the negative bigint
range, disjoint from existing HMAC keys. PostgreSQL additionally scopes the tag by
database. A schema-less transaction fails closed. The future fixed-search-path owner
must derive the key from its verified installed namespace, not pg_catalog or a caller
namespace. Exclusive closure acquisition must be nonblocking to avoid queueing behind
an in-flight session whose authorization may take another shared gate.

Native scoped verification passes29 identity/lifecycle/preview and19 model cases;
1,471 unit/contract,110 resource/controller, quality/types/contracts/build also pass.
Exact pg_locks tags and pg_stat_activity prove the provider gate is idle outside a
transaction. Actual injected unlock failure closes its owned physical connection;
no lock remains. Cached principal refresh and same-UUID schema separation pass. The
schema case first fails (one failure/27 passes) before adding the namespace binding.

The original combined fixture has five intended gate failures,24 passes and15 setup
errors. A controlled reproduction after the code fix has29 passes/15 errors and a
sanitized STORAGE_EXHAUSTED classification. It retains the same resource cap; no raw
stderr/environment is emitted. Fixed fresh identity/model cohorts pass within unchanged
512m memory/256m tmpfs and600s child limits. A duplicate contract/integration basename
initially breaks collection and is fixed with a unique pool-test basename. Failed runs
remain failed. No application failure is inferred from the temporary fixture capacity.

The earlier unscoped recovery/security results are preliminary only; final namespace
binding requires its own recovery/security checks and full native/hosted regression.
The first objective load passes:7,000 requests,zero errors,START p95 468.534ms,
ANSWER p95 25.784ms,all-HTTP p95 25.213ms,500 completed learners and owned cleanup.
No causal comparison with earlier load variance or production acceptance is inferred.
Mixed-history is running separately. No actual closure, erasure or completed DELETE.

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
