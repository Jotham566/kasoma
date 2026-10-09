# E1 bounded ephemeral authentication expiry

Requirements: FR-ID-001 and the approved OTP retention control in security specification §6;
supporting NFR-OBS-001. Status: local checks pass; hosted database acceptance pending.

Previously each OTP request deleted all expired challenges and rate buckets, while idle periods
provided no cleanup. The existing Celery operations worker now runs kasoma.expire_identity every
60 seconds. Each transaction selects at most 100 expired OTP challenges and 100 expired rate
buckets, ordered by expiry/key and locked with SKIP LOCKED. It deletes only those selected rows.
Expiry is inclusive at expires_at <= the single sampled clock. Active and locked rows are retained.
The same ten-minute verification check still rejects expired challenges even if cleanup is delayed.

OTP requests no longer perform bulk cleanup. Rate-counter refresh keeps the existing advisory key
lock and adds a row lock before reading, so cleanup cannot remove a row between reading and
updating it. The worker never takes rate advisory locks, preventing an inverse locking cycle.
It performs no decryption and no provider calls. Profile, sessions, consent/accountability and
learning evidence are outside its scope; no retention period or architectural decision changes.

A committed batch emits identity.ephemeral_expiry with UUID correlation, status and two counts
under packages/analytics-schema/identity-expiry.schema.json. Transaction failure rolls back both
categories, reports zero committed deletions and withholds database diagnostics. No identifiers,
OTP hashes/values, contacts, bucket keys or arbitrary exception text are logged. Replay after a
successful batch is safe; locked/backlogged rows are eligible on the next scheduled run.

Tests cover scheduling and app-factory setting isolation, event boundaries, 210-row batching,
expiry equality, preserved live login/rate/account evidence, locked rows, two concurrent jobs,
actual task invocation, rollback and redacted failure events. A barrier pauses a real rate refresh
after SELECT; concurrent cleanup must skip that row before refresh commits. Removing the row lock
would make this regression fail.

This does not implement session/security-log retention, legal-hold expansion, account inactivity,
anonymization or six-year accountability expiry. Worker availability and backlog drainage matter;
60 seconds is the scheduling interval, not an unconditional deletion SLA. Existing worker-heartbeat
monitoring and minimized failure events support investigation. Production remains gated.

Local `make format lint openapi-check test-unit security` passes 400 unit/contract and five tooling
checks, Python/TypeScript lint/types, schema formatting/contract comparison, Bandit, secret checks
and both dependency audits. The first local test collection caught an unavailable JSON-schema
library import; tests now use the repository's existing dependency-free event-boundary approach.
Native focused `make test` reaches only contract checks: all five database fixtures fail before
assertions because PostgreSQL on localhost:55432 remains unavailable. Hosted execution is required
before promotion. No model, email, messaging or cloud runtime call is made.

## Hosted acceptance recorded 9 October 2026

Commit `64394ac` passed [CI 37228984415](https://github.com/Jotham566/kasoma/actions/runs/37228984415):
413 unit/contract, 174 integration, 60 browser and five tooling checks, plus focused restricted-login,
clean migrations/seed, isolated recovery (52 tables, 272 rows), lint/types/contracts/build, security
and container smoke. It is promoted to main. This supersedes earlier hosted-pending statements.
Native PostgreSQL remains unavailable; production, academic and other stated scope limits remain.
The restricted-login users-row lock grant correction is included and verified.
