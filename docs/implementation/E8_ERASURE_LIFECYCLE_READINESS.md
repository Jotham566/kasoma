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
