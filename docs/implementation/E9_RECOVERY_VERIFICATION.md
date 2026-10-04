# E9 isolated local recovery verification

Requirements: NFR-REL-002, NFR-SEC-002, NFR-MNT-001 (local preparation only).
Decision: [ADR-042](../decisions/ADR/042-isolated-local-recovery-drill.md).
Status: implementation awaiting hosted real-database verification.

`make recovery-drill` creates its own source/destination databases, runs migrations and original
synthetic content/identity/assessment fixtures, backs up and restores using matching PostgreSQL
container tools, compares all table inventories, verifies pgvector and selected immutable guards,
then cleans up only the databases it created. The configured developer database is not copied or
modified. There is no external inference, messaging, cloud storage or production-data access.

Files: `scripts/recovery_drill.py`, `scripts/recovery_fixture.py`, Makefile, CI workflow and
`tests/contract/test_recovery_drill.py`. Sixteen contract cases cover unsafe profile/name rejection,
partial creation, migration-failure cleanup ownership and diagnostic minimization. Fixture mocking
does not constitute backup/restore acceptance.

Native `make recovery-drill` failed at database creation because local PostgreSQL/Docker is
unavailable. No databases were created or dropped by that attempt. Hosted clean-schema execution
is required. Production 35-day PITR, encrypted recovery copies, agreed RPO/RTO and pre-beta/quarterly
rehearsal remain open in the [release register](RELEASE_GATES.md).

Local `make format lint openapi-check test-unit security` passes 387 unit/contract and five tooling
checks, including the first 15 recovery safety cases, plus formatting/types/contracts and security/dependency
audits. The 162 integration cases remain deselected locally; real restore proof is still pending.

Follow-up adds explicit driver rejection and includes both recovery scripts in standard mypy
coverage. An initial duplicate-module diagnostic was fixed by making `scripts` an explicit package.
The recovery gate runs immediately after service/migration setup for earlier restore feedback;
all existing full application/browser/security gates still follow it.

Follow-up local lint/types/contracts and 388 unit/contract plus five tooling checks pass; the new
16th safety case rejects non-PostgreSQL schemes before any resource operation.

## First hosted failure and repair

[CI 37223461188](https://github.com/Jotham566/kasoma/actions/runs/37223461188) migrated and populated
the isolated source, then failed CAPTURE_INVENTORY. The nonempty-evidence check used `consents`
instead of the actual `consent_records` table. Cleanup succeeded with no databases left behind.
Use authoritative ORM table names for all five required evidence classes. Repeat real restore
and full hosted checks before acceptance; this failed run does not prove backup/restore.
