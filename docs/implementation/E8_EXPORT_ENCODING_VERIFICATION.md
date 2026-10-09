# E8 incremental personal-export encoding

Requirements: FR-ID-006, NFR-SEC-001/002, NFR-MNT-001. Native focused checks pass;
full regression and hosted acceptance pending.

The allowlisted projection yields each section and row into a compact JSON encoder. Its byte
counter covers the entire envelope, including metadata, escaped strings, empty arrays and
punctuation. Crossing the existing 2 MiB limit raises EXPORT_LIMIT_REACHED immediately. Reads
stop before the remaining history is hydrated; no artifact or completion is committed. The
10,000-related-row cap, including hidden lookup and sealed rows, remains unchanged.

Encoded fragments are collected into at most 16 KiB chunks. This avoids retaining both the whole
projected object graph and a list of tiny JSON fragments before checking the byte bound. It is not
a universal constant-memory claim: a source record can be large, each field is encoded in memory,
and successful bounded documents are still joined/decrypted/validated for synchronous delivery.
Database cursors and generators close on exhaustion, source errors and consumer cancellation.

No disclosure field, owner filter, diagnostic sealing, guardian exclusion, authentication check,
transaction isolation, rate limit, retention period or API/schema changes. New stored documents
may have a different JSON member order, with the same v1 values and total compact byte count.
Integrity binds each artifact's actual stored bytes; old encrypted retry copies are read unchanged
without regeneration. Snapshot time remains captured after projection. ADR-028 remains controlling;
no new architecture decision or migration is required.

## Verification

`make format lint test-data-exports` passed the initial 13 PostgreSQL cases, including two new
regressions for exact envelope size/cancellation and early byte exhaustion across a 350-event
synthetic history. The latter counts hydrated account-event objects and proves remaining rows
were not read; it also verifies no artifact or completion exists after failure.

Eight deterministic codec cases cover exact limits, Unicode/escaping, empty sections, metadata
accounting, malformed section sequences, non-finite values, source closure and cancellation.
An additional PostgreSQL case writes a legacy canonical-order artifact through the original
transaction boundary, then verifies frozen retry without re-encoding or ciphertext mutation.
Final command results are recorded below before promotion.

Existing cases retain ownership/recent-OTP/revocation/expiry, concurrent retry, rollback,
withdrawn-consent access, sealed mastery, guardian non-decryption and immutable completion guards.
Automated tests use synthetic data and deterministic providers only.

## Remaining work

This refactor neither streams HTTP to a learner nor exports histories beyond the original caps.
Async jobs, snapshot/lease correctness, private encrypted storage publication, authenticated
streaming through the web proxy and orphan/expiry cleanup remain in the
[large-history readiness](E8_LARGE_HISTORY_EXPORT_READINESS.md). It grants no production acceptance.


Native final focused run: `make format test-data-exports` passed all 14 PostgreSQL cases.
`make test-unit openapi-check security` passed 458 unit/contract plus five tooling cases,
unchanged generated contracts, Bandit and dependency/secret checks (no known vulnerabilities).
Lint/format/Python and TypeScript checks pass. Full native regression is running; full hosted
service/browser/container regression is required before promotion. Native MinIO and browser
installation remain blocked by exhausted dependency-download retries, not by stopped Docker.
