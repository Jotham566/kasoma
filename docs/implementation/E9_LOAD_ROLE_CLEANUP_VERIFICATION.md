# Disposable load-role lifecycle — candidate

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
