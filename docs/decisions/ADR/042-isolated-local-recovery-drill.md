# ADR-042: Isolated synthetic logical recovery drill

Date: 4 October 2026
Status: Accepted within delegated test/engineering discretion; local synthetic implementation verified by CI 37223872075
Requirements: NFR-REL-002, NFR-SEC-002, NFR-MNT-001

## Decision

Add `make recovery-drill` to the normal hosted verification pipeline after service/migration setup and before the full regression suite. It
requires the standard loopback Compose development database profile. It never dumps, restores
over, seeds or drops the configured developer database. Instead, generate one random suffix and
create two new databases named `kasoma_drill_src_<32 hex>` and `kasoma_drill_dst_<32 hex>`.
There is no user-provided source/destination override. Refuse remote/nonstandard profiles and
database URL options. Use the existing local administrator connection only to create/drop the
two generated databases; remember each successful creation before allowing cleanup.

Run the prescribed migration command against the isolated source, then reuse the original
synthetic catalog/content helpers and fake identity/messaging services to create consent, one
submitted deterministic attempt/grade and mastery evidence. No real learner data or model calls.
Use the running PostgreSQL container's matching pg_dump/pg_restore clients for a custom-format
logical backup and restore into the empty destination. No network/cloud backup provider is added.

Compare every public table's row count and canonical-row digest before and after restoration.
Require nonempty attempts, grades, mastery, consent and reviewed content. Check pgvector version
and rejection of attempted mutations to restored attempts, grades and approved content; roll back
every verification mutation. Recompare source/destination inventories to detect accidental writes.
Do not expose row digests, credentials, tokens or records in the report. Report only status, fixed
failure stage, table/row counts, restore elapsed milliseconds, guard/extension outcomes and cleanup.

Backup files live briefly in a private temporary directory under ignored `.local`, with mode 0600,
and are removed on exit. Always dispose connections and attempt cleanup only for databases this
run successfully created. Never force-drop sessions, reset volumes, or sweep databases by prefix.
If cleanup fails, fail the command and report the exact generated name for inspection/recovery.
Provider/SQL/child-process exception diagnostics are suppressed to avoid exposing secrets.

## Limits and acceptance

This proves a local synthetic logical restore and selected immutable guards. It does not prove
managed 35-day PITR, encrypted same-geography recovery copies, production restore authorization,
full disaster rehearsal, or RPO ≤24 hours/RTO ≤8 hours. Those remain provider/pre-beta release
gates. Timing describes only this fixture restore, not production performance or data loss.

Contract tests must reject unsafe targets before connection, enforce generated names, prove partial
creation/migration-failure cleanup ownership, and preserve minimized error reporting. Hosted CI must
execute a real clean-source backup/restore and all existing application/security gates. No task is
accepted from mock tests alone. Native Docker absence is reported as a failed local attempt.

## Ownership enforcement correction - 19 October 2026

Derived role names are not proof of creation. The [candidate correction](../../implementation/E9_RECOVERY_ROLE_OWNERSHIP_VERIFICATION.md)
exclusively creates and commits the source's minimal NOLOGIN owner before migration,
records its OID and cleans only that identity after successful owned database removal,
subject to the existing load runner's attribute/membership/dependency checks. The
restored destination creates no role and confers no cleanup authority. No migration
SQL, application ACL, data policy or production entitlement changes. Complete hosted
verification remains required; this clarifies enforcement of the original isolation
decision rather than expanding its cleanup authorization.
