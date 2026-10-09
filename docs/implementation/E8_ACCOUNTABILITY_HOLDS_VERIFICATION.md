# E8 exact accountability-record hold verification

Requirements: FR-ID-006, BR-010, FR-OPS-003, NFR-SEC-002.
Status: verified in hosted CI 37924489562 at `ce9d9f3`, promoted to main. Native migration and
19 focused hold cases pass; full native storage acceptance remains separate.

[ADR-045](../decisions/ADR/045-accountability-record-holds.md) extends the existing exact-record
registry to FLAG_HISTORY and DATA_REQUEST_REVIEW. Flag history uses its own id and the immutable
flag reporter; request review uses request_id and the reviewed request owner. The staff actor is
not substituted for ownership. SQL and service queries key-share lock the target and parent.

Migration 0024 preserves all previous guard validation, expands the strict type constraint and
adds two exact DELETE guards. The administrator selector and generated contracts expose nine
supported types and explain request/grade primary-key references. Existing disclosure, claimant,
recent OTP, rate, idempotency, finite expiry/release and evidence rules remain unchanged.

Neither hold freezes an account, sibling rows or the parent workflow. An active history hold permits
ordinary flag triage to append another immutable revision. Release/expiry cannot bypass immutable
UPDATE/DELETE protection. Existing preview inventory already includes these rows and its normal
active-hold count applies. Deletion remains disabled and coverage remains explicitly incomplete.

## Verification

`make migrate test-legal-holds` passed all 19 focused cases, including the original seven types.
Four new parameterized cases cover the two types' API/SQL ownership, missing/foreign targets,
replay, exact scope, multiple holds, release/expiry, protected DELETE, preview and safe export.
Two further cases cover continued parent triage with immutable old history, and upgrading twice
from 0023 while preserving a previous hold and its retry before adding a request-review hold.
Post-release UPDATE denial is also checked alongside DELETE for all five learning/accountability
targets. Native regression including these added assertions passed 431 unit/contract and 189
integration cases; the one storage/Mailpit case failed because native MinIO was still unavailable.

The existing three-engine administrator journey now checks all nine options and creates an
actual DATA_REQUEST_REVIEW hold alongside a DATA_REQUEST hold, preserving lost-acknowledgement,
retry, pagination and release coverage. Browser acceptance awaits hosted CI.

Run `make format openapi lint openapi-check test`, `make test-legal-holds`, recovery/role checks and
the complete existing browser/security/container pipeline. Rollback must preserve recorded holds
and immutable evidence; disable new options/routes and use a compatible forward fix.
No destructive processor, retention period, provider call or real-data fixture was introduced.

Additional native checks passed: `make lint openapi-check build security`, with both dependency
audits reporting no known vulnerabilities, and `make recovery-drill test-runtime-role` (54 tables,
272 rows, 235 ms restore, pgvector/immutable guards, no cleanup failures). Full native acceptance
and hosted browser/container acceptance remain pending; local MinIO downloads are still incomplete.

## Final hosted acceptance

[CI 37924489562](https://github.com/Jotham566/kasoma/actions/runs/37924489562) passed at `ce9d9f3`:
431 unit/contract plus 190 integration cases (621 Python), five tooling checks, 63 real-API browser
executions and one isolated editor case. Clean setup/services/migrations/seed, focused rubric and
restricted-role checks, lint/types/contracts/build, security/source/image scans and container smoke
all passed. Recovery restored 54 tables/272 rows in 478 ms with pgvector/immutable guards and no
cleanup failures. Cold question transfers were 191510/194227/193605 bytes across the three engines.
Promoted to main; the completed branch was removed locally/remotely. This supersedes the earlier
hosted-pending observations; native MinIO download remains incomplete.
