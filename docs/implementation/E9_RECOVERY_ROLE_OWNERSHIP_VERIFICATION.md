# Recovery owner-role cleanup correction - candidate

Requirements: NFR-REL-002, NFR-SEC-002, NFR-MNT-001.
Status: local focused, quality, unit/security and logical restore checks pass; full hosted acceptance pending.

## Defect and correction

ADR-042 permits cleanup only of resources created by the current synthetic drill.
The prior recovery implementation derived role names from its source/destination
names, then removed any matching existing role after database cleanup. A derived
name does not establish ownership. Two actual PostgreSQL regressions fail against
that implementation: an independently created source role and an independently
created destination role are both removed by the drill.

Before migration, recovery now exclusively creates its source owner in a committed
READ COMMITTED transaction and records the observed OID. A pre-existing or concurrent
creator causes failure before migration, without acquiring cleanup authority over
that role. The restored destination creates no owner role and grants no authority
to remove one. Only after successful owned source database removal does cleanup
inspect the exact source role and require its original OID, minimal attributes and
absence of membership in either direction. An absent role is harmless; an observed
replacement, unsafe/shared role or PostgreSQL dependency fails closed. No role repair,
revocation, DROP OWNED, forced database drop or prefix sweep is added.

The already-verified load implementation supplies these same checks. They move to
`scripts/disposable_owner.py`, accepting only generated load/source-drill database
names. Load wrappers preserve their original narrower name validator and call sites;
no HTTP scenario, threshold, pool, clock or load semantics change. Mypy includes the
shared helper. Frozen migration 0041 and its application permissions are unchanged.
This enforces the existing ADR-042 ownership boundary, without a new architecture,
production permission, data-retention decision or account-erasure authorization.

## Verification

- Original implementation: two actual pre-existing-role regressions fail in 0.46s.
  Only fixture-created synthetic databases and roles participate; teardown never
  targets pre-existing developer/application resources.
- `make test-recovery-role-cleanup`: 98 cases pass in 2.00s, including the existing
  load lifecycle/measurement contracts, recovery failure/partial-cleanup controls,
  invalid helper namespace refusal and actual PostgreSQL role cases. A further
  end-to-end recovery regression replaces the source owner before cleanup and
  proves the replacement OID is preserved while both owned databases are removed.
- The first focused run after extraction has two failing orchestration mocks and
  95 passes. Update those mocks to represent explicit owner creation and verify
  the recorded OID is passed only after successful database removal. These failures
  remain recorded; they do not replace the actual PostgreSQL regressions.
- `make recovery-drill`: passes 69 tables/686 rows, restore 295ms, no cleanup failures.
  Restored pgvector, immutable guards, exact export receipt, encrypted short text and
  channel preservation pass; stripped retirement execution remains denied.

Logs are ignored `.local/recovery-role-{red,focused,focused-restore}.log`.
`make format`, `make lint openapi-check build`, `make test-unit` and
`make security security-source` pass: 1,138 unit/contract and 35 tooling cases,
195 typed source files, matching generated contracts, no known dependency
vulnerabilities and no source leaks. Three existing test warnings remain (TestClient
deprecation and two deliberate blocked-network checks). The 486 integration cases
are deselected by test-unit; focused real cases above do not replace the full suite.
Complete exact combined-source hosted verification is still required before promotion. No performance acceptance is inferred from helper
extraction or another branch's CI. Object-storage restore, production PITR/RPO/RTO,
academic/privacy/provider/physical/pilot gates and ADR-061 approval remain open.

## Files and next gate

Shared helper, recovery/load callers, mypy configuration, new standard Make target,
contract and actual PostgreSQL regressions; ADR-042 clarification, local runbook,
changelog, sprint and traceability. No API, database migration, dependency or product
UI change. Finish broader checks and exact-source hosted verification before merging.
Normal Docker services and review data are preserved.
