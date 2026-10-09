# Large-history personal export readiness

Reviewed 9 October 2026. Requirements: FR-ID-006, NFR-SEC-001/002, NFR-OBS-001,
NFR-MNT-001. This is implementation preparation, not export acceptance or an ADR.

## Existing behavior and limits

ADR-028 authorizes an owner with recent OTP to create/retrieve a complete versioned JSON snapshot.
The synchronous projection counts at most 10,000 related queried rows and permits at most 2 MiB
serialized JSON. Either limit returns EXPORT_LIMIT_REACHED with the request pending; no truncation
or partial completion is permitted. Retries return the same encrypted snapshot for 24 hours.
Completion/receipt/audit/outbox evidence commits atomically and sets six-calendar-year retention.

The current projection materializes sessions, attempts, assignment/version lookup maps, released
attempt IDs and mastery histories in memory. Merely increasing MAX_RECORDS/MAX_BYTES would retain
that memory/latency problem and the synchronous browser-proxy timeout. The proxy currently awaits
upstream.text(), so an API streaming response alone would still be buffered by the web tier.

The allowlist includes owned profile/identifier/consent metadata, answers with attempted-question
context, released grades, visible mastery, reports, requests and minimized channel/account events.
It excludes credentials, guardian evidence, staff internals, unattempted keys/rubrics/solutions and
sealed diagnostic scores or projections depending on them. Those controls are required in every
large-history implementation. Learning consent withdrawal must not block privacy access.

## Smallest complete next vertical slice

1. Refactor the read projection into bounded batches within a consistent database snapshot. Replace
   unbounded Python sets/maps and IN lists with owned joins/subqueries and stable keyset ordering.
   Preserve explicit fields and diagnostic sealing, including every input_attempt_id in materialized
   mastery estimates/history. Keep the current synchronous limits and v1 delivery behavior intact.
2. Add an idempotent, visible asynchronous export job linked to the existing verified EXPORT request.
   Enqueue/claim/retry rules must not retain access tokens. Duplicate/concurrent commands cannot
   publish two artifacts or double-complete a request. Expired/revoked authorization is rechecked
   on every owner download; administrators cannot retrieve another account's artifact.
3. Specify an encrypted artifact/delivery contract under a new ADR before implementation. Decide
   between streaming owner delivery and independently bounded parts; account for buffering in the
   proxy and browser, authenticated retry, integrity, resource ceilings and original 24-hour copy
   expiry. Use the approved local storage/worker boundaries; no public URL or cloud dependency.
4. Publish completion only when all sections and integrity metadata are available atomically. Failed
   or interrupted generation must remain visibly incomplete and retryable without disclosing or
   presenting a partial file as complete. Define cleanup for unpublished artifacts, including
   failure between storage and database commits. Start availability/retention clocks explicitly.
5. Provide the owner UI for queue/status, recoverable failure, complete download and expiry. Preserve
   explicit requests, no-store attachment responses and the existing recent-OTP requirement.
6. Extend owned export inventory, deletion preview and accountability/expiry evidence for the job
   and artifact metadata. Disposable copies are distinct from retained request accountability.

The storage and snapshot choices in step 3 remain proposals, not accepted architecture. Existing
PostgreSQL bounded retry copies are not precedent for storing unlimited bulk files in the database.
No destructive migration, account erasure, new retention period or legal interpretation is needed
for this export slice.

## Required acceptance evidence

- Real synthetic history exceeding both current row and byte limits exports completely without
  truncation; section counts and an independently computed manifest agree.
- Peak batching bounds are exercised, including one oversized source record and exhausted worker
  resource limits; failures leave no completed/partially downloadable artifact.
- Stable snapshot and exact replay while new answers, consent updates and diagnostic completion
  occur concurrently. No mixed sealed/unsealed history or cross-owner data is disclosed.
- Guardian evidence is never decrypted; hidden keys/rubrics, unserved items and staff internals
  remain absent. Empty sections and existing v1 requests remain compatible.
- Duplicate jobs/commands, worker interruption, storage/database failures, retries and rollback
  preserve once-only completion and auditable status without raw payload/error logs.
- Owner/recent-auth/revocation/rate controls apply to status and every download surface, including
  any part or manifest reference. Withdrawn learning consent still permits owner privacy access.
- Expiry is enforced at read time and by bounded cleanup; completion/accountability evidence and
  applicable record holds survive disposable copy cleanup. Exact six-year deadlines remain.
- Fresh/upgrade migrations, generated contracts, all existing export/privacy regressions and a real
  browser queue/download/retry/expiry journey pass before promotion.

The approved SRD does not prescribe an arbitrary larger synchronous limit. Engineering resource
ceilings must be documented and tested without presenting them as legal response deadlines or
agreed pilot performance. Academic/provider approvals are independent and do not block this
synthetic engineering work.

Sources: [ADR-028](../decisions/ADR/028-owned-data-exports.md),
[architecture](../specifications/02_System_Architecture.md),
[API](../specifications/04_API_and_Integration_Contract.md),
[privacy/retention](../specifications/09_Security_Privacy_and_Safeguarding.md),
[release acceptance](../specifications/10_Testing_Acceptance_and_Release.md).

Implementation note: most authenticated application mutations hold an account advisory lock, but
channel/status and shared-reference changes must still be considered. A repeatable-read snapshot
must not be naively started before waiting for authentication locks: stale session/revocation reads
would weaken authorization. Specify the worker's durable authorization boundary, isolation/retry
policy and connection usage explicitly; test concurrency rather than assuming that a transaction
alone makes every read current and consistent.
