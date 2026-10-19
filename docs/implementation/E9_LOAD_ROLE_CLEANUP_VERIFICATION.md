# Disposable load-role lifecycle — bounded engineering verified

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
the stronger boundary. All69 focused native cases pass. No API/schema, grading,
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

Requirements: NFR-MNT-001 and NFR-SEC-002. Supports repeatable performance verification
without adding a product feature, changing load profiles or making a performance claim.
Scope follows the [assessed plan](E9_LOAD_ROLE_CLEANUP_PLAN.md), approved ADR-060's
existing derived-role lifecycle and unchanged ADR-046 objective locking boundary.
No new architectural decision, API contract, migration or application runtime change.

## Change and boundaries

`scripts/objective_load.py` preserves the existing local-only development validator,
generated database naming, fakes, HTTP scenarios, timeouts and latency thresholds.
It requires exact derived-role absence before migration, then exclusively creates
the role in a READ COMMITTED transaction and records its OID before confirmed commit.
Database creation/drop remain AUTOCOMMIT. Frozen migration0041 reuses that known-owned
minimal role and installs the same grants/guards. A concurrent role creator prevents
exclusive creation; no cleanup authority is inferred from an absence result alone.

After successful owned database drop, and only if exclusive creation and commit were
confirmed, cleanup queries that exact role and requires the same OID. Absence succeeds;
a replaced identity fails closed. LOGIN, SUPERUSER,
CREATEDB, CREATEROLE, INHERIT, REPLICATION, BYPASSRLS or membership in either direction
refuse removal. Standard restrictive DROP ROLE preserves PostgreSQL dependency checks.
No attributes are repaired, dependencies revoked, DROP OWNED issued or names swept.
Database cleanup failure preserves the role. Cleanup failure sets cleanup_failed=true
and status=FAILED, retaining the original processing-stage failure and fixed diagnostics.
The original server-stop/engine-disposal ordering remains unchanged.

This does not remove existing orphan roles, retained debugging schemas, review
application data, volumes, SDKs or caches. It creates no production role lifecycle
or erasure capability. Tests manipulate and tear down only their exclusively created
synthetic resources; fixture privilege injection is not runtime cleanup policy.

## Executed verification

- `make test-load-profile` against the old implementation:16 new regressions fail,
  37 original cases pass. This is retained red evidence, not acceptance.
- After implementation, `make test-load-role-cleanup`:65 pass in1.77s (53 contract,
  12 integration). Contract cases cover both profiles, pre-existing roles, absent/safe/
  unsafe states, failed database drop, failed role drop, failed queries and withheld
  diagnostics. Existing load isolation, measurement and pacing checks remain intact.
- Actual PostgreSQL tests migrate two fresh databases through0042, confirm owner
  creation, intentionally stop before learner fixtures, then verify both database
  and role absence. Their FAILED processing reports are expected; cleanup succeeds.
- Nine actual role cases prove all seven prohibited attributes and membership in
  either direction are preserved. A separate fresh database grant proves dependency
  refusal. No privileged role or database pre-existing the tests is cleaned.

`make format`, `make lint openapi-check build`, `make test-unit` (1,128 unit/contract
and35 tooling) and `make security security-source` pass. The final focused recheck
passes65 cases in1.67s. Existing unit warnings are the TestClient deprecation and
two deliberately blocked network-guard checks. Actual HTTP profiles, full integration/
browser suites and complete hosted acceptance remain pending. No main promotion or full MVP acceptance is claimed.

## Files

`scripts/objective_load.py`, `tests/contract/test_objective_load.py`,
`tests/integration/test_load_role_lifecycle.py`, `Makefile`, changelog, current sprint,
requirements traceability, the assessment plan, local runbook and this evidence record.

## Ownership correction — active candidate

The initial `4614bd3` candidate passes both native HTTP profiles (7,000 requests each,
zero errors and cleanup_failed=false), with aggregate reports for
[objective](evidence/E9_LOAD_ROLE_OBJECTIVE_LOCAL_2026_10_19_4614bd3.json) and
[history-mixed](evidence/E9_LOAD_ROLE_HISTORY_MIXED_LOCAL_2026_10_19_4614bd3.json).
The mixed profile starts with25,000 grades and finishes with27,500. START p95 is
474.497/376.901ms, while START p99 is1,129.678/1,103.493ms. Those retain the startup
tail risk and are old-source evidence, not acceptance of the ownership correction.

A new actual two-connection regression creates a separate role after the absence
SELECT has executed. Against `4614bd3`, it fails because cleanup removes that
separately created role (one failed,65 passed in2.42s). The tool now exclusively
creates the role, records its OID in the same transaction, and grants cleanup
authority only after confirmed commit. A failed exclusive CREATE preserves the
other creator's role and stops before migration. Cleanup also refuses a same-name
replacement with a different OID. No role identifier enters the report.

`make test-load-role-cleanup` now passes69 cases in1.81s:55 contract and14 actual
PostgreSQL cases. The race and replacement regressions pass; prior isolation,
attribute/membership/dependency and redaction assertions remain. Revised-source `make format`, `make lint openapi-check build`, `make test-unit`
(1,130 unit/contract plus35 tooling) and `make security security-source` pass.
Full hosted suites and revised native profile checks remain pending.
The in-progress initial-source hosted run is not acceptance of this correction.

## Corrected source native objective profile

Source `a23e9bc020014271e8e697bd2518beda9b3a3393` passes `make load-objective`:
7,000 requests, zero errors, 500 completed learners, 2,500 grades and cleanup_failed=false.
START p95 is428.912ms; ANSWER p95 is27.405ms. START p99 remains1,134.858ms, so the
existing tail-latency risk remains. [Aggregate report](evidence/E9_LOAD_ROLE_OBJECTIVE_LOCAL_2026_10_19_a23e9bc.json).
The revised history-mixed profile is running sequentially; no result is inferred.

Complete hosted [39267916272](https://github.com/Jotham566/kasoma/actions/runs/39267916272)
is running at that corrected source. Superseded initial-source39265408306 is cancelled,
not accepted. GitHub had already completed cancellation when a manual cancellation
request arrived; no current-source run is restarted or gate bypassed. Main remains
verified226ecf3 while this separate candidate is checked. Review retirement stays false.

## Corrected history profile — retained latency failure

The first corrected-source `make load-history-mixed` exits2 (Make failure): START p95
is559.306ms, exceeding the unchanged500ms operation gate. The mixed p95 of27.478ms
does not override that failure. All7,000 requests finish without errors, the25,000
prior grades grow to27,500, both answer formats have1,250 timed answers, and
cleanup_failed=false. START p99 is1,210.911ms. This is a failed full profile, not
performance acceptance. [Failed aggregate report](evidence/E9_LOAD_ROLE_HISTORY_MIXED_LOCAL_2026_10_19_a23e9bc_initial_failed.json).

Application/domain/worker/client source is unchanged from verified main226ecf3; the
new load code changes ownership setup and final cleanup outside the timed HTTP body.
That does not establish the cause of the latency miss. A post-run/pre-recheck memory
snapshot reports51% system-wide free memory and1,036.44MB encrypted swap in use;
it does not measure pressure during the failed requests or establish causality.
One unchanged, sequential diagnostic recheck is running. Its result is pending,
without threshold changes, forced success or removal of this failed evidence.

## Unchanged diagnostic recheck and main follow-up

The unchanged corrected-source history recheck passes:7,000 requests, zero errors,
25,000 prior/27,500 final grades,1,250 timed answers per format and cleanup_failed=false.
START p95 is448.045ms; numeric/choice ANSWER p95 is28.435/29.064ms. START p99 remains
1,106.124ms. [Recheck aggregate](evidence/E9_LOAD_ROLE_HISTORY_MIXED_LOCAL_2026_10_19_a23e9bc_recheck.json).
Post-run memory observations again show51% free and1,028.44MB encrypted swap in use.
They do not explain the earlier559.306ms miss. That failed run remains failed; no
startup-variance fix or broad performance acceptance is inferred from one recheck.

Separately, follow-up main [39264562568](https://github.com/Jotham566/kasoma/actions/runs/39264562568)
at226ecf3 fails in the ordinary browser matrix. `export-gateway.spec.ts` fails at
its initial `/api/v1/auth/otp/request` POST with `apiRequestContext.post: socket hang up`,
before verification or export creation. The earlier complete39256037485 attempt2
remains valid for its exact tree; this later failure is new counterevidence, not a
pass. The cause and OTP commit state are unconfirmed. Intentional aborted-export
protocol errors elsewhere in the log do not establish causality. No blanket retry,
non-idempotent mutation replay or weaker assertion is introduced. Current corrected
source39267916272 remains in progress; later image/service gates on the failed main
follow-up were skipped. No claim is made that latest main CI is green.

`KASOMA_E2E_BROWSER=firefox make test-export-gateway` passes all three unchanged
local cases in11.9s, including exact frozen bytes/length, replay, intentional corrupt/
stalled transfer closure and safe navigation/authorization failure. This diagnostic
does not reproduce or explain the hosted initial-OTP reset; the failed hosted run
is not retrospectively accepted. All eight review Docker services remain healthy.
