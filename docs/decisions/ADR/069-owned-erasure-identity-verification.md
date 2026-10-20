# ADR-069: Owned synthetic identity verification source

Date:20 October2026 (Africa/Kampala)
Status: Accepted within delegated engineering discretion;105 local controls and11 native identity cases pass; complete hosted39337786063 accepted at12c6b60
Requirements: FR-ID-003/005/006, NFR-SEC-002, NFR-MNT-001

## Context and decision

ADR-061 explicitly approves isolated synthetic implementation/tests, excluding the
normal review database. Its identity lock prerequisites need actual PostgreSQL race
checks while the normal shared database's broad regression runs serially. Reuse the
ADR-065/068 exclusively owned local test-service primitive for a separate closed
**erasure** test purpose; only source-db is permitted. Browser/recovery defaults stay.

Use a fresh kasoma_erasure_test_UUID database in a new local immutable-approved-image
PostgreSQL container:512m memory,256 PIDs,256m tmpfs, random IPv4 loopback port,
no persistent mounts/pulls. Require the standard local development profile, fake
providers and pinned Unix Docker endpoint. Generate new private identity/database
keys and a distinct org.kasoma.synthetic-erasure-test invocation label. Only the full
returned creation ID plus that same label permits cleanup. Do not adopt by name,
sweep older schemas/roles, connect to review data or provision an erasure executor.

The controller invokes only make test-erasure-identity, with no caller SQL/target/
selector, no shell and forced fake child providers. Bound the test process to600s;
this is supervision, not an increased API/SQL/assertion deadline. Stop its exclusively
spawned process group with bounded TERM/KILL escalation before unwinding container
cleanup. Termination never counts as a successful test. Propagate failed verification
and cleanup. No credentials enter argv/logs. Container ID/invocation and count-only
cleanup status are infrastructure metadata, not subject identifiers.

This adds test-resource ownership only. It does not activate account closure, create
an authorization/job, perform erasure, enable private profile execution, confer SQL
rights or waive ADR-061's populated backup/held-record/quarantine/checkpoint acceptance
before destructive account-erasure tests. Normal eight-service Docker remains running.
No application architecture, retention, provider or API policy changes.

## Verification and rollback

Retain all existing recovery/browser resource controls; test erasure-purpose label
separation, rejected unsafe profiles, bounded child failure/interrupt cleanup and
private fake environment. Run actual existing identity/LINK/single-use checks and the
new user-barrier/binding races against a fresh owned source. Record before/after
results and exact cleanup; require broad quality/security and exact-source hosted
acceptance. Remove only the test target/entrypoint to roll back; no data migration.

## Fixed-cohort extension under ADR-070 — verification pending

The processing-gate tests add two closed cohorts: test-erasure-identity and
test-erasure-dispatch. Each receives its own fresh owned source, destroyed before
starting the next; the resource caps and600s per-child supervision remain unchanged.
Only this exact target allowlist is callable, with no shell or environment selector.
Original test results remain historical; the expanded combined failure and fresh-source
verification are recorded in the current erasure readiness evidence. This adds no
executor, account processing permission, cleanup scope or erasure activation.
