# ADR-048: Asynchronous owned export delivery

Date: 9 October 2026
Status: Accepted for local synthetic implementation; production approval remains gated
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

Linux WebKit control evidence requires explicit HTML download intent for native
attachments. Before dispatching that attachment, the learner UI checks the existing
recent-owner status endpoint with a ten-second client deadline and reports closed
failures on the privacy page; only READY starts a download. The status check is not
an authorization grant, does not buffer file bytes and cannot bypass the independent
download-time owner/session/expiry checks. Duplicate clicks share the in-flight check.
This candidate refinement requires native privacy/error/retry and hosted acceptance.

## Inventory, observability and acceptance

Include minimized job/generation status in owner exports and deletion-impact inventory; exclude
session-family grants, storage keys, ciphertext and previous artifact payloads. Keep execution
of deletion disabled and hold-coverage warnings honest. Disposable copies do not extend the
retention of linked request evidence. Operational views expose bounded queue/failure/age counts;
logs carry closed states/counts/timing and correlation IDs, never source data or storage diagnostics.

Before promotion or release: verify clean/upgrade migrations and immutable guards; histories above both old
caps; independent section counts and digest; concurrent snapshot/sealed-grade/grant changes;
duplicate claims/commands/publication; storage/DB failure, hard interruption and late upload cleanup;
owner/recent-auth/revocation/expiry/withdrawn-consent cases; bounded memory/time/object reads; frozen
retry; full browser queue/status/download/cancellation/corruption behavior; complete contracts and
all existing privacy/export/browser/security regression. Keep this proposal unaccepted and do not promote or deploy it until the remaining checks pass.
Candidate route/UI/worker wiring on the working branch is permitted for local synthetic acceptance;
it is not release authorization. Earlier disabled-state notes below record prior development stages.


## Implementation resolutions to verify

- Queue or explicit retry: three new commands/hour/account; matching receipt retries do not restart
  a job. Status: 60/minute/account; download: 10/minute/account. Distinct retries of FAILED jobs
  require fresh authentication and start a new at-most-three-attempt cycle. Internal transient
  retries wait 30 then 60 seconds. Closed failures are AUTH_REQUIRED, LIMIT_REACHED,
  PROCESSING_FAILED and REQUEST_COMPLETED. The durable request remains pending on failure.
- Queue/grant/job summary is minimized request accountability under the existing six-year-after-
  completion policy. Clear the temporary family/time grant at terminal failure/publication;
  no token is stored. Disposable generation/manifest metadata is removed only after expired/
  unpublished objects have been removed. Failed cleanup remains observable and retryable.
- Register a generation before any upload. Cleanup considers expired published copies or expired
  unpublished leases; it never deletes a live generation. It processes at most 20 removals and
  100 listed objects within a ten-second cooperative budget, with a 15/20-second cleanup task
  envelope on the separate export queue. Enforce read-time expiry regardless of cleanup delay.
- A bounded global scan of the exclusive versioned UUID prefix also removes unregistered objects
  older than 180 seconds. This catches late uploads after registry cleanup; it does not assume a
  failed upload wrote nothing or that lease expiry cancels an in-flight storage request. Confirm
  current database absence before removal, reject malformed keys, and never list/remove another
  prefix. A disposable database-scoped Redis scan cursor expires after one hour; scan completion
  wraps to the beginning. Losing a cursor causes repeat work, never deletion authority.
- The whole-download deadline is 300 seconds, separate from the existing eight-second initial
  upstream deadline. Preserve exact Content-Length across the API/proxy and abort on mismatch,
  cancellation, corruption, expiry or revocation. The browser saves an explicit attachment
  navigation, with no large Blob/browser-storage copy. Synthetic slow/interrupted tests must
  prove these boundaries before this proposal becomes accepted.

These concrete choices guide implementation and tests. They do not enable a route, grant privacy
or production approval, or supersede the pending verification requirements above.


Cleanup isolation resolution: scope the private prefix by an HMAC of database name and search-path
options under the existing lookup key. Native/Compose host and port aliases share scope, while
independent databases/test schemas and key domains cannot scan or remove one another's objects.
Keys and cursors must match that scope before listing/removal. The unscoped preparatory adapter
was never registered in application routes; cleanup must not sweep its old prefix. Changing the
database/schema identity or lookup key requires quiescing and cleaning the retired namespace under
a reviewed recovery/rotation plan; never infer cross-namespace cleanup authority. Production
recovery/rotation acceptance remains a gate.


Download transport resolution: use a cancellable async HTTP transport for private GETs, reusing
the installed MinIO SigV4 signer and the same local credentials/container/scope. Sign headers
for the approved local `us-east-1` default; do not generate presigned URLs or discover a cloud
region. Refuse ambiguous endpoint paths/credentials/queries, redirects, content encodings,
transfer encodings and invalid lengths. The existing HTTPX transport is used directly so its
client-level INFO logging cannot expose object paths. Disable environment proxies and retries.
Each read has a five-second absolute I/O deadline, independent of byte arrival, plus a one-second
shielded resource-close budget. The attachment has a 300-second transfer deadline; cancellation
closes the async producer and storage connection. Database authority checks run separately with
existing database timeouts and close transactions before yielding. The synchronous adapter stays
inside worker tasks with enforced process limits; it is not the learner download transport.

Worker task definitions use an exclusive `exports` queue with 110/120-second generation and
15/20-second cleanup limits. Proposed Beat entries expire after their 15/60-second periods so
stale ticks cannot become new owner commands; the database controls all jobs, leases and retries.
Only one scheduler and one single-concurrency prefork export worker may run. Queue isolation,
process-level timeout/recovery and launch scripts must be verified before registration.


Native process initialization resolution: the pinned Billiard uses spawn on macOS. In a real
CLI test, nested task definitions were absent from spawned task registries, and the fast trace
registry was empty. Export tasks now live in an importable shared-task module listed in Celery
imports. The child initialization signal binds Celery's task execution registry after imports.
This preserves the platform's spawn choice; do not force unsafe macOS fork or use a solo pool
for work requiring a hard deadline. The isolated CLI test verifies the production pool mechanism
with accelerated synthetic deadlines, a non-cooperative provider, process replacement and durable
lease recovery. Ordinary worker limits and provider restrictions remain unchanged.


Recovery evidence boundary: extend ADR-042's isolated synthetic fixture with a published export,
nonempty job/generation inventory and restored publication guards. Verify the restored encrypted
manifest/key domain reconstructs the original frozen bytes using only ephemeral fake objects.
Keep source/destination inventories unchanged. Explicitly report object-storage recovery as false:
this test does not authorize cross-database object-prefix remapping or establish production backup
or PITR acceptance. No runtime or retention decision changes.


Proposed browser failure resolution: use a plain same-origin attachment link with no download
attribute or client Blob collection. A pre-response upstream failure during explicit navigation
returns a no-store 303 to `/privacy` with an allowlisted error code and fixed alert. Never place
record IDs, credentials, diagnostics or arbitrary destinations in that redirect. Programmatic
callers retain closed status/JSON errors. Mid-stream failures abort the response; browser download
failure and repeat-download behavior still require native browser acceptance.


FR-OPS-002/003 export monitoring: the existing ADMIN-only operations endpoint now includes
bounded queued/running/current terminal-failure counts and oldest pending age from durable SQL.
Failure observations include only currently FAILED jobs with finished_at in the inclusive last
24 hours; future finishes are excluded. Explicit retry removes the failed observation and resets
pending age; automatic retry retains the original command age. No identifiers, grant fields,
manifest/object references or source data are returned. Counts reuse the 10,000 cap/at-least flag.
The generated contract and operations page include the metrics and unavailable-state wording.
Configurable local warning defaults are OPS_EXPORT_FAILURE_THRESHOLD=1 and
OPS_EXPORT_AGE_SECONDS=300 (bounded 1–10,000 and 60–86,400 respectively). These engineering
thresholds are not legal fulfillment deadlines or proof of delivery. ADR-048 remains proposed;
export API/worker activation and learner controls remain pending.


Launch evidence: the dedicated manual consumer uses `make worker-exports` with prefork,
concurrency 1, prefetch 1, explicit exports queue and shared-task imports. It never starts Beat.
The existing native/Compose worker explicitly selects operations/imports/messaging. A real
synthetic subprocess using this repository recipe verifies hard interruption, replacement,
lease recovery and an untouched foreign queue. Export scheduler registration and automatic
startup remain gated; the manual command does not establish full learner delivery acceptance.

The delivery service also enforces the five-second per-object read deadline around
every adapter invocation, independently of the private MinIO reader's own bound.
This prevents a stalled adapter or delayed browser disconnect from consuming the
entire 300-second download budget. Reader close remains bounded to one second.
Native cancellation observation permits those bounds plus one second of scheduling;
this is not an extension of either service deadline. Verification remains required.

### Firefox corruption acceptance driver

Pinned Playwright Firefox's download interceptor does not report native failure for
an interrupted attachment; a plain HTTP/1.1 control reproduces this without Kasoma.
The same pinned Firefox's ordinary download manager rejects truncation and exposes
its native error state. Keep the application corruption case mandatory and drive that
one Firefox case through its built-in Marionette protocol with the ordinary manager.
Playwright still starts the isolated application/schema and verifies the owner, baseline
bytes and final job state. No case is skipped, expected-failed or accepted by timeout.

The helper uses the existing pinned Firefox binary on macOS/Linux, a disposable owned
profile, fixed loopback origins, denied external proxy and no new runtime dependency.
Synthetic cookies travel only over stdin and are validated; errors expose fixed stages
and exception classes, never credentials/account contents. Profile ownership is verified
before privileged manager inspection. The actual privacy-page controls initiate both
downloads. Require native stopped/error/not-succeeded state, closed storage reader,
READY job, and a successful retry with independently matching byte count/SHA-256.
Downloaded paths must resolve inside the disposable profile. Timeouts terminate the
helper and its owned browser; profile cleanup runs on failure and interruption.
The proposal remains unaccepted until full native and hosted acceptance passes.

## Acceptance recorded 18 October 2026

Complete hosted verification passed at `5f959ef` in run
[38033307073](https://github.com/Jotham566/kasoma/actions/runs/38033307073), and
again with calibration preparation at `46a0f8a` in run
[38034913518](https://github.com/Jotham566/kasoma/actions/runs/38034913518).
Commit `46a0f8a` is on main. This supersedes earlier candidate/pending-hosted
statements in this record. Acceptance covers the documented local synthetic
implementation and engineering choices; real learner use, privacy/DPIA approval,
production providers, performance SLOs and pilot sign-off retain their separate gates.
