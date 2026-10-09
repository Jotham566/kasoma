# E8 asynchronous export lifecycle — work in progress

Latest local status: all eight Compose services (web, API, ordinary worker, export worker,
PostgreSQL, Redis, MinIO and Mailpit) are running and healthy. Keep them running for user review.
Private MinIO storage acceptance passes all 59 focused checks; full native regression is running.
The latest UI passes all 30 full-Chromium cases; Firefox/WebKit and hosted acceptance remain open.
Earlier unavailability/disabled-stage notes below are historical and are superseded by this status.


Requirements: FR-ID-006, FR-OPS-002/003, NFR-SEC-001/002, NFR-OBS-001, NFR-MNT-001.
Decision: [ADR-048 proposal](../decisions/ADR/048-asynchronous-owned-export-delivery.md).
This slice is uncommitted and unaccepted. Candidate API, learner controls and worker scheduling
are wired on the working branch for synthetic acceptance; main remains unchanged.

## Current status — 9 October 2026

The full registered-application regression passed 594 unit/contract, 32 tooling and 243
integration cases. Two integration cases failed because local MinIO was unavailable:
`test_private_minio_artifact_round_trip_and_owned_cleanup` and `test_local_storage_and_mailpit`.
No failures are waived. The pinned MinIO build and browser installation remain in progress.
Full pinned Chromium now passes 28 tests, including native download/cancellation/corruption
and frozen retry. The latest unit suite passes 606 cases. Firefox/WebKit, actual storage transport,
complete container checks and hosted regression still gate ADR acceptance and promotion.

Docker web is available for visual review at http://localhost:3000; PostgreSQL, Redis and Mailpit
are healthy. API and worker images are still building. Static-page availability does not establish
working sign-in or complete service readiness. Keep the review stack running during development.

The sections below preserve chronological development evidence. Disabled/unregistered statements
describe earlier stages; the final candidate-wiring section supersedes those activation notes.

## Implemented so far

Additive migration 0025 defines minimized job/grant and disposable generation records, exact
transition/attempt/grant constraints, immutable publication, once-only request completion and
deferrable completion/ready guards. Existing synchronous completion remains compatible. The
migration has run in fresh isolated integration schemas and the configured developer database.

Internal owner commands use recent authentication, ownership, exact receipts, separate limits and
closed status. Claims follow account/request/job lock order, refresh authority, retain command
correlation, use fresh generation UUIDs and recover expired leases without stale-worker mutation.
Transient failures have 30/60-second backoff and a three-attempt cycle; terminal outcomes clear
session-family/time grants. Explicit verified retry is separate from ambiguous-command replay.

Snapshot creation acquires authorization locks before establishing a separate read-only repeatable-
read snapshot, then releases account locks before projection/upload. Publication uses fresh locks
and authorization and atomically stores the encrypted manifest, request completion, six-year
deadline, 24-hour expiry and audit/outbox evidence. No previous snapshot authority is trusted then.

The internal processor uses the same allowlist, 100,000 queried-row/16 MiB limits, 64 KiB output
chunks and a 90-second cooperative deadline. Every uploaded chunk is read back and compared
before publication. Partial/unverified generations remain unpublished. Owner projections include
minimized job/copy status, excluding grants, object references and old encrypted payloads. The
original synchronous limits remain unchanged.

## Current evidence

`make format typecheck test-export-jobs` passed 16 PostgreSQL cases, each with isolated fresh
migration/fixtures. Cases cover ownership/minimized status, receipt replay, concurrent claims,
backoff/exhaustion/retry, revoked grants, lease recovery, SQL guards, atomic rollback, repeated
publication, read-only consistent snapshots, release of account locks, revocation committed while
waiting for the lock, revocation after snapshot and direct-SQL publication without completion.

A real synthetic 12,000-event history exceeds both original synchronous caps and round-trips in
full through the processor, authenticated artifact format and fake object store, with independently
counted events and byte size. Failure cases cover ambiguous upload, corrupt readback, revocation,
cooperative deadline and byte exhaustion with no partial completion. All inference/messaging stays
fake; no external service is used. The 15 existing PostgreSQL export cases also passed after the
projection/schema changes. These results do not establish complete lifecycle acceptance.

## Initial acceptance checklist (historical; see current status above)

- Expired/unpublished and late-orphan cleanup with bounded exclusive-prefix scanning and finite
  disposable cursor handling; generation/job state and authorization race tests.
- Authenticated bounded API download, safe incomplete-transfer/cancellation behavior and a web
  proxy that preserves streaming, length, no-store and attachment headers.
- API/status contracts, queue/retry/download UI, dedicated hard-limited export worker/queue,
  operations counts/alerts, inventory and updated generated clients/runbooks.
- Sealed diagnostic concurrency, consent withdrawal, grant expiry/rotation, malicious manifests,
  corrupt/expired/revoked mid-stream downloads, and browser complete/failure journeys.
- Upgrade/clean migration/recovery, complete application/role/security/browser regression and
  actual MinIO service verification. Accept ADR-048 only after unresolved details are verified.

No deletion, academic scoring, new production provider or release approval is enabled.


Current follow-on checks: `make lint test-unit test-export-jobs test-data-exports openapi-check`
passed the then-current 520 unit/contract, five tooling, 16 lifecycle and 15 existing export
cases, with unchanged generated contracts. Subsequent scoped-listing and closed worker-error
cases bring unit/contract coverage to 531; `make format typecheck test-unit` passes. Listing
rejects noncanonical/foreign/out-of-order keys and invalid times, bounds page consumption and
closes the generator. This is a prerequisite for cleanup, not an implemented cleanup policy.
The full async lifecycle remains uncommitted and unaccepted.


Cleanup/download progress: 23 lifecycle cases now pass. Bounded sweeps expire copies without
removing request accountability, preserve failed-cleanup metadata for retry, collect late orphan
uploads and ignore live/recent objects. Internal downloads verify owner/recent authentication,
frozen bytes and revocation before every emitted chunk, and fail closed on corrupt/expired copies.

A cleanup isolation review found that independent databases/test schemas can share a MinIO bucket.
Object prefixes are now HMAC-scoped by database name/search-path and lookup-key domain. Native/
Compose host aliases remain compatible; foreign namespaces/cursors are rejected before removal.
Scoped-listing and worker diagnostic tests bring unit/contract coverage to 533, confirmed by `make format migrate lint test-unit openapi-check`. Real MinIO verification now also lists only the test's own generation.

The lifecycle is still uncommitted and disabled at the HTTP/worker boundary. Remaining transport,
UI, scheduler/cursor persistence, operations/inventory and full acceptance work stays mandatory.


Disposable cursor handling now uses a bounded Redis GETRANGE, exact database-scoped keys, a
one-hour TTL and closed failure counts. Missing/expired/malformed/foreign state restarts the scan;
SQL remains the deletion authority. Thirteen deterministic cases cover resume, phase alternation,
finite retention, corrupt/oversized/foreign state and cache read/write outages.
`make format typecheck test-unit` passes 546 unit/contract and five tooling cases. Full native
regression is running; actual MinIO and browser/scheduler/transport verification remain separate.


Attachment response preparation (`apps/api/export_transfer.py`) now preserves exact Content-Length,
no-store, JSON type, nosniff and generated attachment names. It explicitly closes the synchronous
producer after client cancellation/send failure; incomplete or oversized bodies never emit a
successful final ASGI frame. Eight deterministic cases pass, including stalled downstream timeout.
`make format typecheck test-unit` passes 554 unit/contract plus five tooling cases.

Twenty-eight focused lifecycle cases pass, including four new consent/auth/deadline/cancellation
cases and actual local Redis TTL/resume/malformed-state replacement. A missing profile in the
withdrawal fixture and a mistaken helper return-type assertion were fixed; all 28 cases then passed.
The subsequent populated upgrade case passes: frozen legacy ciphertext/digest and pending requests survive two upgrade invocations; the upgraded pending request can complete asynchronously.

`make recovery-drill test-runtime-role` passes: isolated logical restore of 56 tables/272 rows in
280 ms, immutable/pgvector checks and restricted-role regression. The added job/generation tables
are empty in this older recovery fixture; this is not yet populated async recovery evidence.
`make security` passes Bandit, secret-boundary checks and both dependency audits. Bandit initially
rejected an application assert; an explicit runtime authorization guard now fails closed under
optimized Python too. No scanning suppression or bypass was added.

Resource gate still open: the ASGI deadline bounds downstream waits, but a shielded synchronous
provider read can delay cancellation. Per-socket read timeouts alone do not prove an absolute
whole-transfer bound against a stalled/dribbling source. Resolve and test that boundary before
registering routes, along with the separate hard-limited generation worker and web proxy.


Final focused `make format lint test-export-jobs` passed 29 cases, including populated upgrade
compatibility and real local Redis cursor storage. API contracts remain unchanged because the
transport helper is unregistered. The current lifecycle remains uncommitted and unaccepted.


Full native `make test` completed: its collected snapshot passed 546 unit/contract, five tooling
and 222 integration cases; two integration cases failed because localhost:9000 refused connection
(`test_private_minio_artifact_round_trip_and_owned_cleanup` and `test_local_storage_and_mailpit`).
No test was skipped or weakened. The later-added eight transport unit cases and six focused
integration cases passed separately, bringing current focused totals to 554 unit/contract and
29 lifecycle/upgrade/cursor cases. This does not establish a green full-stack run.


## Cancellable reader and isolated API progress

The synchronous-storage cancellation concern above now has a separate async reader implementation.
`services/export_reader.py` sends signed header-authenticated private local GETs through the existing
HTTPX transport, with no redirects/environment proxies/retries/client URL logging. It bounds
Content-Length and body allocation, rejects encodings, enforces a five-second total read deadline
and bounds shielded close to one second. The worker retains the synchronous MinIO adapter.

`make test-export-reader` passes 22 deterministic cases plus a real loopback TCP test. The latter
sends a continuously dribbling body and observes EOF/reset after the absolute deadline, proving
that arriving bytes do not keep the request alive. A TCP reset is a valid observed disconnect;
the initial test expected only EOF and was corrected to accept both. Actual MinIO signed reads
are added to the existing private object round-trip test but remain blocked natively by MinIO.

`prepare_async` uses the shared authenticated chunk decoder, verifies the whole digest before the
last chunk and refreshes owner/recent-auth/expiry between chunks. Async ASGI attachment tests cover
length/headers, corruption, disconnect, backpressure and cancellation during a provider wait.
The synchronous helper remains internal; learner transport uses the async response.

`make format typecheck test-unit` passed 590 unit/contract plus five tooling cases after dedicated
worker definitions were added. `make test-export-jobs test-data-exports` passed 35 lifecycle/API/
upgrade/cursor and 15 existing export cases before the additional inventory case. The API router is
registered only inside isolated tests, with deterministic storage injected. Tests cover closed owner
commands, receipts, status, correlation, attachment/frozen retry, expiry and old synchronous
`EXPORT_FILE_REQUIRED` compatibility. Generated application contracts remain unchanged until
activation. No public URL, secret query parameter, real data or external provider is used.

Worker definitions have explicit queue/soft/hard limits, closed error handling and resource cleanup.
Generation emits only closed state/status and the initiating correlation ID; cleanup returns only
counts, never its private cursor. Runtime registration/topology and a real hard-kill recovery test
remain pending. Deletion-preview inventory now counts jobs and disposable generations by owned
request, without grants/manifest data or deletion permission; its focused verification is running.


## Native worker process evidence

`make test-export-worker` passes five task-policy/error-boundary cases and a real CLI process test
on the M4 Mac. The test uses a generated Redis namespace, generated queue and an isolated synthetic
PostgreSQL schema. A provider intentionally ignores the soft timeout; Celery's hard deadline kills
the child, a replacement PID runs a probe, and the unpublished RUNNING job recovers through the
180-second lease and bounded backoff with a fresh generation. Production task limits remain
110/120 seconds; only this harness accelerates them to 0.5/1.5 seconds. The test removes only its
owned Redis keys and subprocess group; no database schema or developer data is reset.

The first embedded harness failed task registration. A real CLI reproduction then exposed the
pinned Billiard macOS spawn path: nested task registrations and Celery's fast trace registry were
not inherited. Importable shared export tasks plus child registry initialization fix this without
forcing fork or weakening timeout enforcement. The final CLI check passed in 9.25 seconds.
Native launch scripts/Compose activation still need the separate export consumer and one scheduler.

`make format lint test-export-jobs test-export-reader openapi-check` passes 36 lifecycle/API/
inventory cases, 22 reader contracts and the real TCP case; application contracts remain unchanged.
The real TCP check also verifies DEBUG logging exposes neither object paths nor authorization.
Source/dependency security passes with no known vulnerabilities. Full native regression is running
after these changes; the two unavailable-MinIO failures remain an expected but unwaived gate.


NFR-MNT-001 local resource correction: a broad native run passed 151 integration cases but had
86 fixture errors after PostgreSQL exhausted Docker's default 64 MiB `/dev/shm` and entered
recovery, plus the two known unavailable-MinIO failures. Compose now sets `shm_size: 512mb`.
`make services-db` recreated only the PostgreSQL container with its existing named volume intact;
inspection confirms a healthy service and 536870912-byte shared-memory ceiling. SQL timeouts,
acceptance thresholds and developer schemas remain unchanged. The serial rerun passes 590 unit/contract and 238 integration cases with zero setup errors;
its only two failures are the unavailable-MinIO cases. Actual storage acceptance remains open.

The real Uvicorn/API/middleware client-disconnect test passes: closing a partial attachment cancels
the in-flight async reader and closes its resources. Current focused lifecycle/API count is 37.


FR-ID-006/NFR-REL-002 recovery follow-up: the isolated logical drill now publishes a synthetic
async export before backup, requires nonempty job/generation records, verifies restored publication
guards and decrypts the restored manifest against in-memory synthetic encrypted objects. Frozen
bytes match; source/destination inventories remain unchanged. Native `make recovery-drill` passes
56 tables/285 rows in 262 ms with no cleanup failure. This is database/key compatibility evidence,
not object-storage backup, namespace remapping, production PITR or RPO/RTO acceptance.

The unwired web attachment helper passes exact-length, metadata, cancellation and deadline checks.
`make format lint test-tooling openapi-check` passes, including 21 tooling cases; application
contracts remain unchanged. ADR-048 and the complete async delivery slice remain unaccepted.

Recovery follow-up regression: `make format lint test-export-jobs test-unit` passes 40 focused
PostgreSQL cases, 590 unit/contract and 21 tooling cases. Three new cases prove read-only export
verification rejects corrupt ciphertext, missing objects and mismatched expected bytes.

Final follow-up `make format lint check-docs security-source` passes, including Gitleaks with no
findings. The previously failing pinned Go dependency URLs now answer HTTP 200; `make services`
has been restarted using the existing verified source and caches. Its MinIO build remains pending,
so the two actual-storage regression failures are not yet resolved or waived.


FR-ID-006/NFR-SEC-001/002 web gateway integration: owner export-job paths accept GET/POST;
export-file accepts GET only and rejects cross-site/same-site attachment requests. The attachment
uses the private cookie-derived Authorization header, requests identity encoding, rejects redirects
and keeps credentials out of URLs. Initial headers retain the eight-second deadline; successful
attachments move to the separate 300-second streaming deadline. Closed error mapping cancels the
unread upstream error body. Disconnects abort either phase. `make format lint test-tooling` passes
31 tooling cases, including ten new private-fetch/error/deadline cases. This supersedes the earlier
unwired-helper note; API registration and learner controls remain pending.


Snapshot sealing regression passes: after the export's repeatable-read snapshot is established,
the independent API commits the final diagnostic answer before export sections are read. The
result still contains the original 14 unreleased answers and no grades/mastery disclosure; retry
is byte-identical. A new request includes all 15 released results. `make format lint test-export-jobs
build` passes 41 focused PostgreSQL cases and the production web build. Final formatting/lint/types/
documentation/OpenAPI checks pass; generated application contracts remain unchanged.

`make security` passes after gateway integration: Bandit, secret-boundary checks and both dependency
audits report no findings. `make e2e-install` is running to restore the missing native browser
engines; `make services` remains live in the pinned MinIO source build. Neither pending process is
acceptance evidence, and the existing actual-storage/browser gates remain unwaived.


Attachment navigation failure handling (FR-ID-006, NFR-SEC-001/002): before a successful
attachment response starts, a closed upstream failure on an explicit navigation returns a
no-store 303 to the fixed local privacy page. Its query contains only an allowlisted error code,
never credentials, record identifiers, diagnostics or a return URL. The privacy page resolves
that code to a fixed accessible alert. Programmatic requests retain JSON/status errors;
cross-site/same-site rejection does not redirect. Mid-stream errors still abort the transfer and
cannot be converted into a successful file or a late redirect. Native attachment links must rely
on server Content-Disposition, without a `download` attribute that might save a redirected page.
`make format lint test-tooling build` passes 32 tooling cases and the production web build.
Real Next/API HTTP checks are running through `make test-export-gateway`; these do not require or
claim a browser-engine download journey. Learner queue/status controls and API activation remain
pending under ADR-048.

`make format lint test-export-gateway` passes both real Next/API HTTP cases in 6.8 seconds.
Navigation gets a fixed local redirect and rendered alert; programmatic errors stay JSON;
unsupported methods and same-site/cross-site requests are denied. These HTTP-client checks do
not assert native browser save/cancellation behavior or successful MinIO attachment delivery.


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

Operations evidence: `make test-operations` passes 19 contract/PostgreSQL cases, including real
queue-to-running-to-terminal-failure/retry transitions, inclusive 24-hour bounds, exclusion of
future finishes, exact alert thresholds/recovery and minimized output. The first broad unit run
caught omitted EXPORT_FAILED/EXPORT_STALLED values in the analytics alert schema; the schema was
updated without weakening its exact-match guard. Final `make format lint test-unit build
openapi-check` passes 593 unit/contract and 32 tooling cases plus generated contracts and production
web build. Browser assertions for the metrics were added but remain unexecuted pending engines.


FR-ID-006/FR-OPS-002/NFR-MNT-001 launch policy: `make worker-exports` now defines the dedicated
single-concurrency prefork consumer, prefetch multiplier 1, explicit exports queue and importable
shared tasks. It starts no Beat scheduler. Native and Compose ordinary workers explicitly consume
only operations/imports/messaging. The normal development launcher still starts only the existing
ordinary worker/scheduler; export Beat registration, automatic startup and owner routes remain
disabled pending the complete slice. The manual consumer command is not feature acceptance.

`make format lint test-export-worker` passes seven cases. The real subprocess test derives its
launch flags from `make -n worker-exports`, substituting only the isolated synthetic application,
queue/node identity and diagnostic verbosity. A non-cooperative provider is hard-killed, a new PID
runs, the database lease recovers, and a message on another generated queue remains unconsumed.
The test removes only its own Redis namespace after stopping its subprocess group. Production
110/120-second limits remain unchanged; the test fixture accelerates them to 0.5/1.5 seconds.

Launch follow-up `make format lint test-unit openapi-check` passes 594 unit/contract and
32 tooling cases; generated contracts match. The separate seven-case worker run includes real
hard-stop and foreign-queue isolation evidence. Automatic launch/scheduler, owner UI and full
storage/browser acceptance remain pending; no commit or promotion is claimed.


Candidate wiring for local synthetic acceptance (not promotion): the application now registers
owned export commands/status/attachments and the two scheduled tasks. `make dev` starts the
dedicated consumer alongside the existing sole scheduler; the application Compose profile includes
an export-worker with its own targeted health check. Ordinary workers retain exclusive selection
of operations/imports/messaging. Container smoke includes and preserves the prior running state
of the new worker. Generated contracts include the actual registered owner endpoints.

Learner controls use the generated client for explicit prepare/status/retry, retain ambiguous
command keys in memory, and save READY copies via a plain attachment link without a Blob. A
separate synthetic E2E fixture uses in-memory encrypted objects; no live storage/model/messaging
provider participates in those tests. The real Next/API HTTP journey now passes command/replay,
READY polling, exact-length frozen attachment and pre-response failure navigation (three cases).
The registered API's 41 focused PostgreSQL cases and seven worker cases pass. Browser journeys
were added but remain unexecuted while engine installation runs. ADR-048's prior disabled notes
are historical; its promotion/release gate is unchanged. No production deployment is authorized.


FR-OPS-002/NFR-MNT-001: each Compose worker now checks its explicit node identity and requires
that node's pong. A healthy export consumer cannot mask an unavailable ordinary worker (or vice
versa). Deterministic checks exercise both actual Compose probes with own, foreign, missing and
invalid replies. This corrects health reporting; queue separation and the sole scheduler remain
unchanged. Runtime container verification remains pending image completion.


Health and gateway follow-up: `make format lint test-export-worker` passes all 15 cases,
including both actual Compose probes rejecting foreign/missing/invalid replies and the real
hard-stop/lease-recovery case. `make format lint test-export-gateway` passes all three real
Next/API HTTP cases. Unauthenticated attachment requests must now return exactly 401
REAUTH_REQUIRED (or the corresponding fixed navigation redirect); a missing route/404 no longer
passes the regression. These are not native browser download or complete container acceptance.
Docker PostgreSQL, Redis, Mailpit and web are currently healthy; API/worker images, MinIO and
browser engines are still building/installing. No commit or main promotion is claimed.


FR-ID-006 interrupted-download acceptance: the isolated E2E process now offers per-generation
corruption/stall controls over its in-memory encrypted store and a bounded 700-event synthetic
history. Installation refuses any database search path other than the harness's random E2E
schema. Fixture routes are absent from application entry points, images and generated contracts;
the web gateway does not expose them. No real storage or external provider participates.
Four deterministic fixture checks pass within the 606-case unit suite. New browser journeys
require mid-stream corruption/cancellation to fail, release the reader and preserve a complete
frozen retry. They are added but not yet executed pending browser installation. The actual
Next/API HTTP suite additionally exercises the same faults independently of native browsers.


Fault transport result: `make format lint test-export-gateway` passes all three HTTP cases
(8.7 seconds), now including a multi-chunk synthetic export, corrupt second-chunk failure,
client timeout/disconnect during a stalled second read, observed reader closure and exact frozen
retry after each failure. This uses the real API/Next transport with fake storage. It does not
substitute for native browser save/cancel or MinIO verification. `make check-docs` passes.


NFR-COMP-001/NFR-MNT-001: add `make e2e-chromium-full`, an explicit supplementary command
using the installed pinned full Chromium in new headless mode. It retains both shards and all
assertions; normal CI and the three-engine acceptance requirement remain unchanged. This allows
real-browser progress during the separate headless-shell download, without restarting the live
installer or substituting an unpinned system browser. Execution evidence follows separately.


First full-Chromium shard: 13/14 tests passed, including native background-command recovery,
saving frozen attachments, user cancellation, corrupt second-chunk failure and successful retry.
The old administrator privacy-review test selected every export in the shared queue; concurrent
new export fixtures made its final assertion ambiguous. Scope its export/deletion locators to
the exact references returned by that learner's requests, retaining all permission/review/
download assertions. Both Chromium shards are being rerun; no complete browser pass is claimed.


Full pinned Chromium result: `make format lint e2e-chromium-full` passes both shards,
14 + 14 = 28 tests (25 browser journeys and three HTTP-only gateway cases). This includes
background-command lost acknowledgement, native attachment saves/frozen retry, cancellation,
corrupt second-chunk failure and reader closure, existing privacy review/holds, operations
metrics, narrow touch reflow and the existing learning/content/channel journeys. The ambiguous
admin locator failure is resolved using exact owned references; no assertions were removed.
`make security-source openapi-check` also passes: no secret leaks and matching generated contracts.
Firefox/WebKit, default headless-shell execution, native MinIO, full application containers and
hosted regression remain outstanding. This does not grant production or ADR-048 acceptance.


Native storage gate update: the pinned MinIO source build completed and its service is healthy.
`make seed` now passes both catalog and private storage initialization. `make test-export-storage`
passes all 59 cases, including real signed async MinIO reads, scope/listing, encrypted round trip,
anonymous denial and owned-object cleanup. The earlier unavailable-MinIO failures are not waived;
`make migrate test security` is running again with storage available. The new export worker has
started and its readiness is being checked. Browser installation remains live.


FR-ID-006/NFR-MNT-001 full Docker delivery evidence: `make smoke-export` passed through
the running Next/API/ordinary Beat/export-worker/MinIO topology. A fresh fictional account
receives its OTP only in local Mailpit; the probe searches only its own unpredictable recipient,
verifies via secure-cookie gateway flow, queues a request and waits at most 45 status reads.
The real scheduled worker published a 2,191-byte private export; exact length, own identifier,
no-store and frozen retry matched. The probe revokes only its session; normal retention handles
its synthetic request/copy. No credentials, OTP, identifier or contents are printed.

Add this journey to `make container-smoke`, retaining existing preservation of already-running
services. Two deterministic fake-transport tests verify bounded local behavior and reject a
changed retry file; the unit suite passes 608 cases. Full native integration remains in progress.
This proves local delivery, not production or long-history load acceptance.


### Native regression acceptance update — 9 October 2026

FR-ID-006, FR-OPS-002/003, NFR-SEC-001/002, NFR-REL-002 and NFR-MNT-001:
`make migrate test security` completed successfully with 606 unit/contract, 32 tooling and
245 integration cases; the later two smoke-probe cases passed in the 608-case unit run.
Actual MinIO checks now pass, resolving the earlier unavailable-storage failures. Bandit,
secret boundaries and Python/Node dependency audits pass. `make recovery-drill test-web-content`
also passes: 56 tables/285 rows restored in 256 ms, immutable/export guards verified, and
one isolated content-admin browser case. Object-storage recovery and production RPO/RTO
remain unverified. Evidence: `.local/async-export-complete-native-regression.log` and
`.local/async-export-final-recovery-ui.log`. Remaining browser matrix, container vulnerability
scan and hosted CI still gate promotion; ADR-048 remains proposed.
