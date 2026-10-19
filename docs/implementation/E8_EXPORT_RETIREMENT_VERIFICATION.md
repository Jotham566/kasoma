# E8 bounded synthetic export accountability retirement

Requirements: FR-ID-006, FR-OPS-003, BR-010, NFR-SEC-002, NFR-MNT-001.
Status: SQL capability verified at `e5d3d98` by complete hosted39234377840.
Executor operations and real-data/release acceptance remain separate.

## Authority and exact scope

[ADR-060](../decisions/ADR/060-completed-export-accountability-retirement-proposal.md)
has explicit user approval for bounded synthetic implementation. This increment
builds on the [exact receipt/job hold foundation](E8_EXPORT_EVIDENCE_HOLDS_VERIFICATION.md).
Its prior full run finds three byte-fixture signature failures; corrected foundation
source `be2735e` passes complete hosted39232307831. Source5fa939d/39229138880 is cancelled
and not accepted. Foundation and SQL kernel are published through main `e9f688e`;
their two merged owned branches are removed locally and remotely. Executor operations
remain a [separate candidate](E8_EXPORT_RETIREMENT_OPERATIONS_VERIFICATION.md).

Only the four approved tables may lose eligible rows: data_request_receipts,
data_request_reviews, personal_export_jobs and data_subject_requests. The parent must
be a completed EXPORT, have finite valid timestamps and exactly completion plus six
UTC calendar years as its persisted due date, now due by database wall clock. Copies
and every generation row must already be absent. The processor never deletes copy
objects, locators, grants, users, learning, consent, legal holds or general audit rows.
Pending requests, DELETE cases, future/malformed deadlines and uncleared exports fail
closed. No account erasure, closure or pending DELETE completion exists.

## SQL capability and authorization

Migration 0041 installs a frozen SQL asset through install_v1. Future changes must use
a forward migration/versioned asset. The database/schema-derived owner is NOLOGIN,
NOINHERIT, non-superuser, without role/database creation, replication or RLS bypass.
It receives only the allowlist DELETE/SELECT, necessary locking-column UPDATE,
read-only dependency/hold checks, state UPDATE and audit INSERT permissions. Temporary
schema CREATE for ownership assignment is revoked. No ordinary role gains membership.
Runtime role-safety checks also reject owner security drift and stripped ownership.

The parameter-free SECURITY DEFINER routine has a fixed search path; PUBLIC EXECUTE
is revoked. A separate actual LOGIN may receive schema USAGE and only EXECUTE on
that routine. It receives no source SELECT/DELETE, state changes, DDL, owner SET ROLE
or private-helper execution. Caller cutoffs, clocks, GUCs and temporary search paths
are not deletion authority. SQL source DELETE guards independently repeat role,
activation, policy, source state and exact wall-clock hold checks. UPDATE immutability
and existing grant/worker transition guards remain intact.

Activation is persisted false by default and resets false on privileged installation
or restore repair. SQL execution also independently requires an owned synthetic scope:
identity_test_<32hex> schema, or public in generated kasoma_retirement_test_<32hex> /
kasoma_drill_src_<32hex> / kasoma_drill_dst_<32hex> databases. The normal review public
schema and production scopes are rejected even with the state flag enabled. No
maintenance executor is configured or scheduled in the review stack.

## Bounds, races and accountability

One transaction serializes the batch state with NOWAIT, then rotates through the
four allowlisted tables. At most 200 distinct UUID candidates are read/considered,
at most 100 rows removed, with a five-second cooperative clock budget, 100-ms database
lock timeout and the existing two-second statement timeout. SKIP LOCKED parents and
leaves prevent an active source transaction from monopolizing the batch. These are
engineering ceilings, not a production real-time/SLO claim.

Stable per-table pointers and wrap preserve progress past a held prefix. Pointers
refer to existing source rows, never removed identifiers or a retry tombstone log.
At a full-page boundary, the final retained row can be revisited once before later
rows; processing still advances. Metadata stores at most four opaque pointers.

Take EXPORT parent before exact leaf. Existing DATA_REQUEST_REVIEW hold insertion
now uses that same explicit order in API and SQL. A concurrent hold either commits
before deletion and preserves its exact leaf, or refuses the missing source; it
cannot acknowledge a lost hold. Parent holds do not hold every child. Held leaves
retain only necessary parent references; unheld siblings can retire. Foreign keys
and parent dependency checks remain effective.

A minimized system audit is inserted atomically with removals and cursor movement:
NULL actor, generated batch/correlation UUID, fixed operation code, timestamp,
per-table counts and closed skip categories. No source/account/receipt IDs, keys,
hashes, bodies or per-record tombstones are copied into its reason. This follows
ADR-060's bounded synthetic security-audit classification; investigation preservation
and finite audit disposal remain required before real processing. Failures/rollback
retain source evidence and cursor state; no partial success is reported.

After lawful receipt retirement, current authenticated/rate-limited intake can use
the old UUID key for a fresh request under existing pending deduplication. It never
resurrects the retired request; retained keys keep their exact binding. Retired reads
use the existing absent response. No indefinite retry registry is added.

## Verification record

The first two focused cases pass through a real EXECUTE-only LOGIN. The expanded
13-case set passes, followed by21 cases (68.61s) and23 cases (73.09s). Existing exact
hold and byte-recovery regressions pass 10 and 3 cases respectively after0041.
Final coverage adds populated0040 upgrade, scope/calendar corruption, fresh retry,
actual finite hold expiry, concurrent batch serialization and lock-timeout rollback;
record its terminal result below before counting it accepted. Formatting/type checks
catch ordinary SQL-line wrapping/import issues; these are corrected without weakening
assertions. No model inference or external delivery occurs.

`make migrate seed recovery-drill` passes:69 tables/686 rows,423-ms logical restore,
exact receipt hold, immutable guards, encrypted short-text/channel evidence, frozen
export bytes and denied retirement after ownership/ACL stripping. The drill removes
only its own generated databases and corresponding isolated NOLOGIN owner roles;
failed database cleanup preserves its role. Installation/repair is separately tested
to restore restricted ownership/ACLs and require a fresh explicit opt-in. This is
not object-storage recovery, production PITR or RPO/RTO acceptance.

## Files and outstanding gates

- SQL/migration: migrations/sql/0041_export_retirement.sql,
  versions/0041_export_retirement.py and services/export_retirement_install.py.
- Compatible review-hold lock order: services/legal_holds.py.
- Tests/commands: tests/integration/test_export_retirement.py and Makefile.
- Recovery: scripts/recovery_drill.py, including fail-closed execution verification
  and cleanup of roles derived from the drill's newly created database names.
- Documentation: this report, CHANGELOG, current sprint, traceability, ADR060
  implementation notes, domain/API specifications and the local runbook.

Next: typed independent executor configuration/provisioning, default-disabled bounded
scheduling, aggregate operational health and runbook controls. The review stack stays
disabled. Complete local/hosted regressions, container checks and exact source evidence
are required before accepting/promoting the SQL increment. Full preservation, other
retention classes, account erasure and external academic/privacy/provider/production
release gates remain incomplete.

## Final focused and quality checkpoint

Final corrected role-installer source passes all 31 focused integration cases in
146.55s. This includes populated0040 upgrade with preserved holds, scope refusal,
malformed/DST calendar deadlines, copied/generation prerequisites, finite key reuse,
wall-clock hold expiry despite advancing application time,31-case concurrency/bounds/
rollback/privilege coverage. Existing hold and byte-recovery regressions pass 10 and 3.
`make build test-web-privacy` passes all six operator/privacy executions across the
three engines, preserving accessibility, narrow/large-text and existing retry/release
checks. No new UI or API payload is introduced by this SQL increment.

The first security run flags string-built SQL in the role installer (BanditB608).
Replace it with psycopg SQL.Identifier/Literal composition; security then passes
without exemptions. Two recovery unit mocks assume a truthy unspecified role-existence
result. Give them explicit absent-role responses and add positive/failed-database
cleanup cases, preserving the underlying cleanup policy. `make lint openapi-check
security test-unit` now passes1,096 unit/contract and 35 tooling cases, all types/
formatting, unchanged contracts and both dependency audits. Container builds, source
secret scanning and high/critical image scans also pass.

The local `make test` run with 456 integration cases was interrupted and is not a pass.
Complete hosted acceptance is recorded below; configuration/scheduler/health remain
a separate candidate. The review stack remains healthy on 0041, default disabled; no application
volumes or review-stack records are removed.

## Complete hosted acceptance and local interruption

[39234377840](https://github.com/Jotham566/kasoma/actions/runs/39234377840) succeeds
at exact source `e5d3d986a66d37fb4e3ee294065c92173777c5dd`: 1,096 unit/contract,
456 integration, 35 tooling and 108 browser executions, plus staff UI/native WebKit
controls, actual restricted logins, clean/additive migration, seed, contracts/types/
build, security/dependency/image scans and container smoke. Logical recovery restores
69 tables/686 rows in 713 ms, including exact receipt holds and refused stripped-owner
execution. Optional registry authentication is skipped without credentials; no
application acceptance gate is skipped. This verifies the bounded synthetic SQL
kernel, not the still-pending runtime executor operations or full MVP/release.

The native full run stops near its final WhatsApp tests during a local process/Docker
interruption; its handle is gone and no pytest success exists. It is not a full pass.
All eight services recover on existing images/volumes; PostgreSQL accepts connections
and schema0041/default false are retained. No application-volume, SDK or build-cache
cleanup is used. Subsequent acceptance closeout changes only Markdown, preserving
the exact hosted code, SQL, tests, Makefile and workflow source above.
