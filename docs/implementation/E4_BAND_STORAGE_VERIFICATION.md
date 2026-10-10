# Durable calibration-band state

Date: 10 October 2026. Requirements: FR-GRD-003/004, FR-MST-001, NFR-SEC-001/002,
NFR-REL-002 and NFR-MNT-001. Decision: [ADR-050 proposal](../decisions/ADR/050-short-text-pending-and-eligibility.md).

## Storage boundary

Migration 0028 adds `grading_bands` and exact immutable `grading_band_history`.
All report/scope/version/count/approval-reference metadata is immutable after insertion.
Topic must belong to subject. New bands start disabled, with no activation timestamp.
Activation requires consistent timestamps, non-null approval metadata, approved subgroup
review, zero critical errors and the separate 85%/90% count thresholds at SQL level.
Those structural checks do not resolve or authenticate real academic evidence.
No activation application command, endpoint, seed report or enabled runtime band is added.

A band can activate at most once, then disable once; an unused band can be withdrawn
without activation. Disablement is sticky. Replays preserve original reason/time/history.
Any newly reviewed replacement must have its actual approval evidence independently
resolved by the future authority service; assigning new IDs is not approval. Database
owners used in isolated fixtures exercise the activation transition solely to verify guards.

`services/grading_band_store.py` registers disabled metadata, locks and refreshes current
state even with a stale ORM identity map, and disables atomically. Publication must retain
the band lock through its grade/mastery/audit transaction. Concurrent disablement serializes
on that lock. SQL generates history in the same transaction; rollback removes both changes.
The future grading worker still needs to call this boundary before dispatch/publication.

These tables contain global calibration metadata, aggregate benchmark counts and opaque
report/approval references, not learner IDs, answers, grades or reviewer identities. They
are not added to personal exports. Per-learner grading/audit assignments have not been
created here and still require owned export, hold, deletion and retention coverage when
implemented. Existing work/history privacy controls remain unchanged. Delete/overwrite
of calibration evidence is rejected; a future reviewed retention operation is required.

## Permissions and recovery

The existing real restricted-login test now permits band SELECT and UPDATE only on
`enabled`, `disabled_at`, `disable_reason`, `revision`, `updated_at`, plus history INSERT
for the SQL trigger. It denies approval/benchmark mutation, activation timestamp writes,
history rewrite/deletion and band deletion. Activation needs the separately controlled
`activated_at` column, so the worker's disable permission cannot activate a band. These
are isolated verification grants, not a production role deployment.

The recovery fixture creates an explicitly unapproved, disabled synthetic report and
withdraws it; it does not invent academic approval. Restore compares both tables and
checks calibration/history immutability, alongside the existing guards, pgvector and
frozen export checks. Current isolated logical drill passes 60 tables / 294 rows in
267 ms, with no cleanup failures. It does not prove object-store recovery or production
PITR/RPO/RTO.

## Verification

Commands: `make migrate test-grading-bands`, `make test-runtime-role recovery-drill`,
`make test`, `make format lint openapi-check security security-source`.

Initial focused integration passes 11 cases using actual clean migrations and PostgreSQL:
registration/history, exact disable replay, concurrent disable, stale-map refresh/row
locking, rollback, immutable metadata/history, missing approval/threshold/critical/subgroup
constraints, and scope/timestamp validation. Restricted-login and populated recovery pass.
A later direct-SQL enabled-insert assertion is included in the full backend regression,
which is running. Logs: `.local/grading-band-integration.log`,
`.local/grading-band-role-recovery.log`, `.local/grading-band-full-backend.log` and
`.local/grading-band-final-quality.log`.

Formatting, lint/types, generated contracts, dependency/security and source-secret
checks pass. Alembic metadata now includes both grading-work and calibration models;
the repeated head migration passes (`.local/grading-band-metadata-check.log`). The
rebuilt application/container vulnerability checks and eight-service health, scheduled
export/frozen retry and request-metrics smoke pass (`.local/grading-band-containers.log`).
The full backend regression remains active; this is not a completion claim.

The learner/API/worker path remains disabled. Genuine approval resolution, audit assignment,
independent blinded review, rolling-result persistence/automatic disablement, atomic grade/
mastery publication and complete learner fallback remain open. This slice provides the
storage and permission boundary, not automatic-scoring acceptance.

## Regression and persistent scope correction

The full backend run passes 780 unit/contract cases, 35 tooling cases and 279 integration
cases (549.23 seconds), including the direct-SQL enabled-insert guard. Subsequent review
added a regression for moving a topic to another subject after band registration; it
failed against 0028, proving that insertion-time checks alone did not preserve scope.
Migration 0029 adds a composite foreign key to the topic/subject pair, with a matching
unique key on the curriculum table. This additive constraint does not rewrite either
curriculum or calibration data, and an invalid existing binding would fail migration.

Final `make format lint migrate test-grading-bands test-runtime-role recovery-drill`
passes: 13 focused SQL cases, restricted login, clean migration and populated 0028→0029
upgrade/replay. The restore now also rejects topic reparenting beneath a stored band;
60 tables / 294 rows restore in 250 ms, with no cleanup failures. Logs:
`.local/grading-band-scope-regression.log` (the reproduced failure) and
`.local/grading-band-scope-fix-checks.log` (passing correction). The earlier full run
predates this final FK correction; complete exact-head hosted verification remains required.

The follow-up branch is `codex/grading-band-state`, preserving the in-flight export
candidate verification on its existing branch. No main or academic acceptance is claimed.
Final rebuilt images including 0029 pass vulnerability scans and eight-service health,
scheduled export/frozen retry and request-metrics smoke (`.local/grading-band-scope-containers.log`).
Final document links/whitespace, generated contracts and source-secret checks also pass
(`.local/grading-band-final-source.log`). The candidate is ready to commit/push for
complete hosted verification; no activation authority has been added.
