# E8 individual learning-record holds

Requirements: FR-ID-006, BR-010, FR-OPS-003, NFR-SEC-002.
Status: implemented; hosted migration/API/SQL/browser acceptance pending.

[ADR-043](../decisions/ADR/043-learning-record-holds.md) extends the existing independent ADMIN
hold journey with GRADE, MASTERY_EVIDENCE and MASTERY_HISTORY. Migration 0022 widens the strict
target constraint, retains all existing hold validation and adds ownership joins/locks and DELETE
guards. Grade references use the attempt_id primary key. No immutable evidence is rewritten,
no hold scope cascades and no deletion/anonymization processor is enabled.

The administrator form labels the three additions and explains the grade reference. Deletion
preview accurately lists seven supported types but still reports LEGAL_HOLD_COVERAGE_INCOMPLETE
and execution_enabled=false. Generated API and TypeScript contracts match the strict target enum.

Three contract cases exercise the new kinds. Six real-database cases check lifecycle/replay,
multiple holds, exact-record scope, direct DELETE rejection, release/expiry, continuing immutable
protection, preview/export boundaries, missing/foreign API targets and direct-SQL ownership guards.
Existing hold authorization, rate, audit, concurrency and rollback tests remain part of regression.
The browser journey checks all seven labels and grade-reference guidance alongside its existing
create/retry/release/accessibility assertions.

Local `make openapi format lint test-unit` passes 397 unit/contract and five tooling checks.
Native `make migrate` fails connecting to PostgreSQL; the focused `make test` run passes the
three new contract cases but all six integration fixtures fail before assertions at the same
connection boundary. Hosted clean migration and application tests are required before promotion. This is partial preservation coverage, not account erasure clearance or
production legal/privacy approval. Remaining source/channel/embedded-reference/log/backup coverage,
accountability expiry, reviewed transforms and real recovery/privacy gates remain open.

## Hosted acceptance recorded 9 October 2026

Commit `64394ac` passed [CI 37228984415](https://github.com/Jotham566/kasoma/actions/runs/37228984415):
413 unit/contract, 174 integration, 60 browser and five tooling checks, plus focused restricted-login,
clean migrations/seed, isolated recovery (52 tables, 272 rows), lint/types/contracts/build, security
and container smoke. It is promoted to main. This supersedes earlier hosted-pending statements.
Native PostgreSQL remains unavailable; production, academic and other stated scope limits remain.
The restricted-login users-row lock grant correction is included and verified.
