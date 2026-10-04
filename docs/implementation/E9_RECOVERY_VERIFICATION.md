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
`tests/contract/test_recovery_drill.py`. Fifteen contract cases cover unsafe profile/name rejection,
partial creation, migration-failure cleanup ownership and diagnostic minimization. Fixture mocking
does not constitute backup/restore acceptance.

Native `make recovery-drill` failed at database creation because local PostgreSQL/Docker is
unavailable. No databases were created or dropped by that attempt. Hosted clean-schema execution
is required. Production 35-day PITR, encrypted recovery copies, agreed RPO/RTO and pre-beta/quarterly
rehearsal remain open in the [release register](RELEASE_GATES.md).

Local `make format lint openapi-check test-unit security` passes 387 unit/contract and five tooling
checks, including 15 recovery safety cases, plus formatting/types/contracts and security/dependency
audits. The 162 integration cases remain deselected locally; real restore proof is still pending.
