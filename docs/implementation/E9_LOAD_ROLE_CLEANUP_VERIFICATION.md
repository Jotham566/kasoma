# Disposable load-role lifecycle — candidate

Requirements: NFR-MNT-001 and NFR-SEC-002. Supports repeatable performance verification
without adding a product feature, changing load profiles or making a performance claim.
Scope follows the [assessed plan](E9_LOAD_ROLE_CLEANUP_PLAN.md), approved ADR-060's
existing derived-role lifecycle and unchanged ADR-046 objective locking boundary.
No new architectural decision, API contract, migration or application runtime change.

## Change and boundaries

`scripts/objective_load.py` preserves the existing local-only development validator,
generated database naming, fakes, HTTP scenarios, timeouts and latency thresholds.
It requires exact derived-role absence before migration, so a fresh database cannot
confer ownership over an existing role. Unknown lookup results refuse migration.

After successful owned database drop, and only if absence was confirmed before
migration, cleanup queries that exact role. Absence succeeds. LOGIN, SUPERUSER,
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
