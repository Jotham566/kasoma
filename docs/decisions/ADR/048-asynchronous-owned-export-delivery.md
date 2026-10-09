# ADR-048: Asynchronous owned export delivery

Date: 9 October 2026
Status: Proposed — implementation contract being verified; not enabled
Requirements: FR-ID-006, FR-OPS-002/003, NFR-SEC-001/002, NFR-OBS-001, NFR-MNT-001

## Intended outcome and compatibility

An explicitly requesting, recently OTP-authenticated owner can prepare a larger export in the
background, see its bounded status and download one understandable JSON attachment. Keep the
existing ADR-028 synchronous endpoint, copies, limits and owner controls. No administrator may
queue or download for another account. Withdrawal of learning consent does not block privacy access.
The larger path uses the same allowlist and diagnostic sealing; it does not adjudicate additional
legal disclosure or enable deletion. No model, messaging, email or cloud provider is involved.

The proposed API adds POST/GET /me/data-requests/{target}/export-job and GET
/me/data-requests/{target}/export-file. POST requires an empty closed body and idempotency key.
Use the existing request receipt namespace with a distinct operation fingerprint. A lost reply
returns current job state without restarting it; a distinct explicit command may retry a confirmed
failure with a newly verified authorization grant. Existing synchronous completion and asynchronous
publication serialize on the same request row. Only one may complete it.

The existing synchronous download of an asynchronously completed request must report a distinct
large-file delivery requirement while its copy is available, and normal expiry afterward. Do not
misreport a live async copy as expired. The browser offers prepare/status/retry/attachment controls,
retains ambiguous command keys only in memory, and does not collect the larger file into a Blob.
A missing background worker remains visibly queued rather than falsely completed.

## Authorization and snapshot

A job stores a minimized grant: the verified session family and original authenticated-at time,
never bearer/refresh tokens, identifiers or guardian evidence. Active account and an unrevoked,
unrotated, unexpired session in that family must still exist, with the same verified time and a
valid recent-OTP window, when snapshot creation and publication occur. Normal token refresh does
not by itself invalidate the family grant. Logout/reuse detection, closure and grant expiry fail
closed; an explicit fresh owner command can retry. A future privacy processor does not inherit
this narrow self-service grant.

Follow the existing lock order: account advisory lock, request row, then job/generation rows.
Select candidate identities before locking, then refresh every authority check while holding the
account lock. Never take a job lock and then wait for an account lock held by an API command.

Use a short coordinating transaction with the account lock. Only after it is acquired, open a
separate READ ONLY REPEATABLE READ transaction and establish/validate its snapshot. Release the
coordinator once the snapshot is established. Stream the allowlisted projection within that
snapshot; new learning, consent or diagnostic completion cannot mix visibility states. Do not
hold account locks for the entire upload. Before publication take a fresh ordinary transaction,
reacquire locks in the same order, and recheck the current grant, request, generation and lease.
This avoids stale authorization caused by starting a repeatable-read snapshot before waiting.

## Claims, bounds and scheduling

One durable job belongs to one request. Claims use a fresh unpredictable generation and finite
lease, with at most three automatic attempts per explicit owner authorization cycle. Only transient
storage/processing failures retry, with bounded backoff; authorization and resource-limit failures
remain visible until an explicit owner action/review. Duplicate or stale tasks cannot publish.
Owner queue/retry commands are bounded separately from status and download reads. Exact command
limits and failure taxonomy will be frozen in the implementation before this ADR is accepted.

Generation has a 90-second cooperative deadline, a dedicated task's 110/120-second soft/hard
limits, a 180-second lease, 100,000 related queried rows, and ADR-047's 16 MiB/256-by-64-KiB format
ceilings. Preserve the global 2-second database statement timeout and ordinary worker limits.
These are engineering ceilings, not legal deadlines or pilot SLOs. Resource exhaustion never
publishes a truncated file. Use a separate single-concurrency export worker/queue so generation
cannot monopolize the operations/import/messaging worker. Native execution must use a worker
pool that enforces hard limits; solo-pool settings alone are not a hard-stop guarantee.

## Publication and object lifecycle

Use only the approved private local MinIO boundary. Object names live under a versioned export
prefix with unpredictable generation/object UUIDs, never identities. Register the generation
before upload; storage adapters bound ciphertext reads before allocation, close responses on every
path, disable retries that exceed the job budget and return closed errors. No presigned/public URL.

Only a complete ADR-047 manifest can become available. Additive database guards require pending
owned EXPORT requests, consistent generation/manifest/digest/size, once-only publication and atomic
request completion. Publication time starts the 24-hour availability period and six-calendar-year
minimized request-accountability deadline. The snapshot's generated_at is not proof of download.
Existing immutable request/artifact/hold guards remain; a compatible forward fix is the rollback.

The lifecycle must handle uploads without acknowledgements and failure between storage and database
commits. Cleanup checks live publication/lease state, uses bounded work and removes expired/private
unpublished objects without touching other storage prefixes or retained request accountability.
Read-time expiry is unconditional even when cleanup is delayed. Cleanup must also find late objects
whose generation registry was removed; an expired lease alone is not proof that a pending storage
write cannot finish later. Final orphan/tombstone/cursor rules and their finite retention must be
resolved and tested before acceptance. Never invent an indefinite metadata or object-retention rule.

## Download

Recheck current owner/recent OTP, active account, request completion, manifest binding and 24-hour
expiry before starting and between emitted chunks. The reader checks authenticated per-chunk
integrity and the whole-file digest before the last chunk. Authentication locks and DB transactions
must close before yielding to slow clients. No rate counter is incremented once per chunk.

The API and web proxy preserve streaming, no-store, server-generated attachment names and exact
Content-Length. Retain the ordinary eight-second initial upstream deadline; a separately bounded
whole-transfer deadline must permit low-bandwidth downloads. Same-origin explicit attachment
navigation uses existing secure cookies and server-injected authorization, with no credential in
URLs. Cancellation closes upstream/storage resources. A missing/corrupt/expired/revoked chunk or
incomplete upstream response must abort the download, not produce a successful truncated JSON file.
Exact whole-transfer limits and browser failure UX require evidence before acceptance.

## Inventory, observability and acceptance

Include minimized job/generation status in owner exports and deletion-impact inventory; exclude
session-family grants, storage keys, ciphertext and previous artifact payloads. Keep execution
of deletion disabled and hold-coverage warnings honest. Disposable copies do not extend the
retention of linked request evidence. Operational views expose bounded queue/failure/age counts;
logs carry closed states/counts/timing and correlation IDs, never source data or storage diagnostics.

Before enabling: verify clean/upgrade migrations and immutable guards; histories above both old
caps; independent section counts and digest; concurrent snapshot/sealed-grade/grant changes;
duplicate claims/commands/publication; storage/DB failure, hard interruption and late upload cleanup;
owner/recent-auth/revocation/expiry/withdrawn-consent cases; bounded memory/time/object reads; frozen
retry; full browser queue/status/download/cancellation/corruption behavior; complete contracts and
all existing privacy/export/browser/security regression. Keep this proposal unaccepted and routes
disabled until its remaining lifecycle/resource details are resolved safely.
