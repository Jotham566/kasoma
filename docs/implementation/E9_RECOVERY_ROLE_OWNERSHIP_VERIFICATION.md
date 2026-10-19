# Recovery owner-role cleanup correction - bounded engineering verified

Requirements: NFR-REL-002, NFR-SEC-002, NFR-MNT-001.
Status: bounded synthetic engineering accepted after full hosted39299684285 at adf4328.

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

## Combined practice-day candidate checks

The recovery branch integrates the activity candidate through 02c9abc (runtime source
78ca959) and academic-source documentation from main e7a4fc0. Four informational merge
conflicts retain both evidence histories; Make targets and runtime files merge without
changing their behavior. The practice-day branch's existing CI head is not replaced.

Combined `make test-recovery-role-cleanup test-progress test-fresh-session-response`
passes 98 role/isolation cases in 2.05s, 55 progress cases in 60.91s and 40 assessment
integration cases in 159.77s. The seven channel cases overlap the last two commands;
these totals are executions, not distinct integration-test counts. Strengthening the
actual source-collision test to require migration never runs also passes the 98-case
role target in 2.77s. Combined `make recovery-drill` passes 69 tables/686 rows in 329ms
with no cleanup failures and the existing encrypted/guard verification intact.

Combined `make lint openapi-check build`, `make test-unit` and
`make security security-source` pass: 1,154 unit/contract, 35 tooling, 196 typed source
files, matching generated contracts and no known vulnerabilities/source leaks. The
487 integration cases deselected by test-unit still require full hosted execution.
This is local combined-source evidence only; full hosted verification is pending.
Neither feature is accepted from the other's CI. No performance threshold or release
gate changes. Normal Docker remains healthy; the recovery helper is verification
tooling, with no additional application, schema or provider behavior.

## Hosted source and unrelated browser failure retained

Combined source adf432879a8b55eeb1f9e8d59f5d6b053f76bf56 is pushed on
codex/recovery-role-ownership; its exact full hosted run is
[39299684285](https://github.com/Jotham566/kasoma/actions/runs/39299684285), currently
in progress. Keep that remote head unchanged while it runs. Only Markdown evidence
closeout follows this runtime/test/Make tree.

Earlier activity source 78ca959's full run 39294126038 passes backend checks but fails
a WebKit data-request journey at the 30-second total test timeout, with no reported
failing-action stack. Unchanged `make test-web-privacy` passes all six native cases
on the combined source, including the long journey in 7.7/10.0/8.6s across the engines.
This does not explain or repair the hosted timeout. No timeout/assertion/retry change
is made, neither branch is promoted, and the new full run is required independently.
See [the exact failure boundary](E6_PRACTICE_ACTIVITY_VERIFICATION.md).

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

Actual PostgreSQL role-collision/replacement cases run in the 487-case full integration
suite. Both generated database cleanup and independently created/replaced role
preservation remain enforced. No application permission, migration SQL, unrelated
resource cleanup or account-erasure authority changes. The restore report explicitly
keeps object_storage_recovery_verified=false and production_rpo_rto_verified=false.
