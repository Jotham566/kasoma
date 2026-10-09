# Large-history personal export readiness

Reviewed 9 October 2026. Requirements: FR-ID-006, NFR-SEC-001/002, NFR-OBS-001,
NFR-MNT-001. This is implementation preparation, not export acceptance or an ADR.

## Existing behavior and limits

ADR-028 authorizes an owner with recent OTP to create/retrieve a complete versioned JSON snapshot.
The synchronous projection counts at most 10,000 related queried rows and permits at most 2 MiB
serialized JSON. Either limit returns EXPORT_LIMIT_REACHED with the request pending; no truncation
or partial completion is permitted. Retries return the same encrypted snapshot for 24 hours.
Completion/receipt/audit/outbox evidence commits atomically and sets six-calendar-year retention.

The accepted projection refactor batches ORM reads and replaces retained assignment/version maps
and released-ID lists with owned SQL joins/subqueries. The incremental encoding slice now stops projection at the existing byte limit and collects
16 KiB chunks. The successful bounded bundle is still decoded for the synchronous response.
Merely increasing MAX_RECORDS/MAX_BYTES would retain that output memory/latency problem and the synchronous browser-proxy timeout. The proxy currently awaits
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

## Async delivery design to resolve in the implementation ADR

The following is a design proposal, not a new accepted contract or permission to publish artifacts.

- Keep existing small synchronous exports and their retry documents compatible. A separate explicit,
  recent-OTP owner command queues a durable job for the pending EXPORT request. Queue/status/download
  must remain owner-only; ADMIN review does not grant download access. Never persist a bearer token.
- Use one job per request and a new unpredictable generation ID per claim. Database claim state,
  finite leases, attempt limits and a closed failure reason support visible retry/dead-letter status.
  A late worker cannot publish after losing its lease or after another path completes the request.
- Establish the read snapshot only after the account authorization lock has been acquired. A short
  coordinating transaction may hold that lock while a separate repeatable-read transaction starts
  and validates the durable request/active account. Release the coordinator once the snapshot is
  established, rather than blocking all learning for the entire export. Final publication rechecks
  the live account, request and generation lease in a fresh transaction. Test this two-connection
  protocol against revocation, closure, competing synchronous completion and interrupted workers.
- Stream the same explicit allowlist into a versioned, understandable JSON artifact. Bound database
  fetch batches, individual serialized records, plaintext chunks, overall bytes/rows and execution
  time. Resource exhaustion leaves the request pending with a visible failure, never truncated
  completion. An increased resource ceiling is not a legal response deadline or pilot SLO.
- Store independently encrypted bounded chunks in the approved private MinIO boundary. Object keys
  use unpredictable generation/chunk references without identity fields. Bind ciphertext to its
  generation, ordinal and format; authenticate each chunk and verify recorded sizes/digests. The
  existing local encryption boundary may be reused only with explicit cross-object binding; raw
  standalone ciphertext must not be swappable between export requests.
- Only a complete manifest with exact section counts, ordered chunk references, whole-artifact
  integrity and generated-at time can be published. Commit request completion, retention deadline,
  manifest pointer, receipt/audit/outbox evidence and availability expiry atomically. A failed
  storage upload/database commit leaves private unpublished objects for bounded orphan cleanup.
  Readers must never discover artifacts merely by listing a bucket or guessing an object key.
- Serve through an authenticated application endpoint with recent OTP and current revocation/owner
  checks. Do not expose public or bearer object URLs. The API and web proxy must preserve streaming,
  no-store, server-generated attachment names, bounded timeouts and incomplete-transfer failure.
  Verify chunk integrity before emitting its plaintext and abort if the artifact cannot complete;
  test that the web download does not treat an interrupted response as a successful complete file.
- Fix availability to 24 hours after successful publication. Read-time expiry is mandatory even if
  cleanup is delayed. Cleanup removes disposable manifest/chunks and unpublished generations while
  retaining minimized six-year request accountability and applicable holds. Do not delete an object
  based on age alone without confirming the generation's publication/lease state.
- Include job/manifest metadata in owner export and deletion-impact inventory only through an
  explicit minimized projection. Do not recursively include past plaintext artifacts or storage
  keys. Operational events carry counts, durations, closed reasons and correlation IDs, never raw
  answers, identities, object locations, bearer tokens or provider diagnostics.

Before accepting this design, verify the existing worker's 15/20-second task limits, the database's
2-second statement timeout and the proxy's 8-second request timeout against the chosen bounded job
and download protocol. Do not silently increase global limits or assume Celery redelivery alone
provides exactly-once completion. Dedicated bulk-operation limits, recovery behavior and tests must
be part of the ADR and implementation. The current projection refactor does not change these limits.

The proposed encrypted chunk envelope should include the request ID, generation ID, ordinal,
format version and payload inside the authenticated ciphertext; successful decryption alone does
not establish that an object belongs to the requested export. Compare each envelope to trusted
manifest metadata before emitting any plaintext. Verify whole-file integrity before emitting the
last chunk so an integrity failure cannot produce an apparently complete attachment.

Prefer a same-origin authenticated attachment navigation for large downloads, avoiding a full
JavaScript Blob allocation on constrained learner devices. If adopting that path, retain strict
cookie/site-origin controls, server-injected API authorization, explicit user action, current owner/
revocation checks, bounded streaming time, cancellation and Content-Length/incomplete-transfer
behavior. A test must show that a revoked or corrupted mid-stream download is reported as failed.
The existing buffered synchronous route remains compatible until a separately tested replacement
is enabled. Choosing chunk/artifact/job limits and API routes remains part of the future ADR.


The [incremental encoder](E8_EXPORT_ENCODING_VERIFICATION.md) is an internal prerequisite, not an
accepted asynchronous delivery design. It preserves ADR-028's existing isolation and disclosure
policy; it does not establish the stronger concurrent snapshot protocol proposed above.


[ADR-047](../decisions/ADR/047-private-export-artifact-format.md) now decides only the bounded
private chunk/envelope/manifest format. [Its verification](E8_PRIVATE_EXPORT_ARTIFACT_VERIFICATION.md)
uses fake storage and the existing projection, with delivery disabled. The remainder of the async
lifecycle above is still a proposal and must be decided/tested before any route or worker enables it.
