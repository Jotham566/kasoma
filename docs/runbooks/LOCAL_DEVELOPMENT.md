# Local development and recovery

Prerequisites: Git, Make, Python 3.9+ for the setup launcher, npm and Corepack,
Docker Desktop/Compose. `make setup` installs repository-local uv 0.12.18, Python
3.12.14 and Node 24.21.0, then Corepack's pinned pnpm 10.30.2 and locked dependencies.
Install Corepack 0.34.0 if it is missing. Initial downloads require internet;
runtime/test execution uses local services and fakes. No cloud account is required.

```sh
make setup
make services
make migrate
make seed
make dev
```

Open localhost port 3000. API readiness is `/api/v1/health` on port 8000;
`/api/v1/live` checks only the process. Mailpit is port 8025; MinIO console is 9001.
PostgreSQL uses host port 55432 to avoid an existing host database.
All published service ports bind to loopback. Do not expose these local services.
`make setup` creates a mode-0600 ignored `.env` with random local secrets and never
overwrites it. Existing credentials and data are preserved. No secret defaults
exist in application settings. Do not print `.env` or resolved Compose config.

`make smoke-dev` verifies startup and shuts down the native process group.
`make dev` supervises native web, API and worker; Ctrl-C stops them. Infrastructure
continues until `docker compose stop`. Do not delete volumes to resolve errors.
If a port is occupied, stop the conflicting development service deliberately.
API/worker can alternatively run through `docker compose --profile application
up -d --build` after migrations. Do not run those and native API/worker together.

## Verification

```sh
make lint
make typecheck
make test
make openapi-check
make build
# First browser installation only:
make e2e-install
make e2e
make security
make containers
make security-source
make security-containers
make container-smoke
```

`make test` runs socket-blocked unit/contracts first, then PostgreSQL/Redis
integration tests with only loopback sockets allowed. Missing services fail the
suite, not skip it. Migration tests use a unique `test_*` schema, preserving local
catalog data. The schema is retained for inspection; delete it only deliberately.
There is no previous-release snapshot for migration 0001. No destructive downgrade
or reset command is provided. Subsequent releases must test upgrade from the
previous migration and establish a rollback/restore plan.

The seed writes only the frozen S4/two-subject/six-topic catalog, idempotently.
`tests/fixtures/seed-scenarios.json` reserves synthetic graph, role, item, session
and trajectory cases for later slices. It does not create users, grant consent,
publish academic items or claim implemented learner journeys.

`make openapi` regenerates the schema/client; `make openapi-check` detects drift.
`make security` runs SAST, local secret-boundary checks and dependency audits;
audits download vulnerability metadata, never call model/messaging providers.
CI additionally scans container images and secrets. Branch protection and named
review owners must be configured by the repository owner; a workflow file alone
does not enforce them. Staging deployment awaits the Week 8 provider ADR.

## Local model boundary

For the optional native Mac runtime, run `make setup-ollama` (official 0.34.3
archive with pinned SHA-256), then `make ollama-serve` in a separate terminal.
`make ollama-check` probes availability without inference. Setup downloads no
weights, creates no cloud integration, and the serve target disables Ollama cloud.
Run Ollama natively on the M4/16 GB Mac. Host endpoint:
`http://localhost:11434/v1`; container endpoint:
`http://host.docker.internal:11434/v1`. Keep it bound locally. Start at 8k context
with a benchmark-selected Q4/Q5 4B–8B model; 12B is optional and 27B is unsupported.
No exact model is selected before licensing and frozen benchmark review.

The foundation includes a local connectivity probe and deterministic
`FakeModelProvider`; it does not perform inference, automatic grading or model
selection. `make eval-local`, `make eval-gemini-free` and `make eval-compare` fail
explicitly until the approved benchmark, full task/result schemas, sanitizer and
budgets are implemented. Never run Gemini as part of setup, tests or CI. The
opt-in flag does not authorize ordinary external provider startup.

## Production boundary

Foundation startup rejects APP_ENV=production. Real learner data remains blocked
pending identity/consent, encrypted identifiers, authorization, privacy/academic
release gates and the approved deployment provider. Console traces and structured
logs contain only allowlisted operational metadata; access logs are disabled.
The worker smoke task exercises plumbing only. Transactional outbox, domain retry,
idempotency and dead-letter handling arrive with the first persisted domain event.

The installed Next.js CLI generates apps/web/AGENTS.md and CLAUDE.md during
`next dev`; these are retained as framework guidance subordinate to root product
instructions. ESLint 9.39.5 is pinned for Next's React/import plugin compatibility;
ESLint 10 currently fails with those plugins. Track the upstream compatibility
upgrade; the development-tool deprecation is not a production-runtime exception.

## Identity and consent (E1)

Run `make setup migrate seed` after updating. Setup adds independent encryption and
lookup keys to ignored .env without printing or replacing existing keys. Keep these
keys with your local synthetic database; losing them prevents contact decryption.

Open `/onboarding`. Use an `example.invalid` email and retrieve its random OTP from
Mailpit at http://localhost:8025. Runtime codes are never logged or returned by an
API. Fake phone messages are available only inside injected test adapters; use email
for manual local walkthroughs. Automated Playwright starts its own isolated schema
and in-memory provider with deterministic test-only codes through scripts/e2e_api.py.
That script is never used by the development/production application entry point.

Use synthetic birth dates and names. Adult test profiles need their own declaration;
under-18 profiles need distinct guardian-contact verification and separate assent.
The development notice is explicitly not approved legal wording. Use Verify contact
again for sensitive actions after ten minutes, or Resume saved session when an
access credential expires. Refresh does not reset the recent-authentication clock.

The gateway allows same-origin local browser mutations only, retains credentials in
HttpOnly cookies, and accepts no arbitrary upstream route. Bearer API clients use
the generated identity contract. No active learning endpoints exist yet; future
assessment/channel services must call IdentityService.require_learning.

Migration 0002 is additive. Tests explicitly exercise 0001 -> 0002 and repeat
upgrade in independent schemas. No destructive downgrade is available. Expired OTP
and rate rows are pruned on OTP requests; long-term consent/audit and inactive-account
retention jobs remain release work, not an implied indefinite-retention policy.

## Staff content workflow (E2)

Run `make setup services migrate seed`. Migration 0003 adds content, normalized
mappings, role and audit tables. Seed adds six explicitly synthetic concepts/outcome
references and four competency labels, never approved question content.

First sign in a fictional `.invalid` email through `/onboarding` and local Mailpit.
Explicitly grant its role from the repository workspace:

```sh
make staff-role KASOMA_STAFF_EMAIL=author@example.invalid KASOMA_STAFF_ROLE=CONTENT_AUTHOR
make staff-role KASOMA_STAFF_EMAIL=reviewer@example.invalid KASOMA_STAFF_ROLE=ACADEMIC_REVIEWER
```

Each account must already be independently verified. The CLI refuses real-domain
addresses and non-development configuration. Names/addresses do not automatically
grant roles. Every action is audited. To revoke, repeat with
`KASOMA_STAFF_REVOKE=1`; the next protected request checks the new role state.
This is a synthetic bootstrap tool, not a production staff provisioning system.

Open `/admin/content` in separate browser profiles for author and reviewer. Create
a text-only single-choice draft with the synthetic catalog reference. Provide
rights evidence/conditions, answer, solution, remediation and competency weights
summing to one. Missing fields block submission with field-specific errors.
Approve only from a different verified reviewer; all fifteen checklist categories
must be checked. Mark disputed/high-risk work for two independent reviewers.
Returning a draft preserves comments. Retirement excludes new selection; creating
the next draft preserves the old version. Version conflicts require reloading.

The UI initially offers two options and preserves all existing API-authored options;
additional choices (up to eight) can be authored through the generated API contract.
The API rejects unknown privileged fields and requires revision and idempotency
headers for mutations. Mutation retries return the same version's current state.

No real NCDC mappings, source licenses, academic release approvals or production
eligibility are implied. Bulk import, media, other response formats, full curriculum
relations and learner attempt pinning remain subsequent slices. Never disable the
database guards to edit an approved payload or audit history. Application rollback
retains these additive tables; destructive downgrade has no automatic command.

## Synthetic assessment (E3)

After `make setup services migrate seed`, explicitly run `make seed-assessment`.
This creates 30 synthetic workflow fixtures (five per topic) using separate local
fixture author/reviewer identities and fake delivery. Repeating a completed seed
is a no-op. The labels exercise software only, not NCDC academic correctness;
they never count toward the 250-item release minimum.

Run `make dev`, create/consent a synthetic learner at `/onboarding`, and visit
`/revise`. The same session URL or the interrupted-session list resumes durable
progress on another authenticated browser. Answers save before navigation; a lost
acknowledgement can be retried safely. No tokens or answers are stored in browser
localStorage. Review the last saved feedback after reload, then continue.

`ASSESSMENT_SESSION_DAYS` and `ASSESSMENT_REPETITION_DAYS` default to seven days.
They control session expiry and recent-item exclusion, not data retention. If
inventory is insufficient, choose another topic; the service does not silently
repeat or shorten the plan. Retired questions block new serving/submission; end
that session to choose another topic. Historical grades retain their pinned version.
Mastery status is NOT_IMPLEMENTED until the later projection slice.

Migration 0004 is additive. Keep evidence tables if reverting application code;
never downgrade/drop learning evidence without a separate recovery plan.

## Numeric grading (E4)

Run `make migrate seed-numeric`. The explicit numeric seed creates five synthetic
workflow items in Physics / Electricity and Magnetism and is repeatable. It uses
fake messaging and separate fixture author/reviewer identities; it makes no claim
about academic inventory or curriculum correctness. Visit `/admin/content` as a
provisioned staff identity to author numeric rules, and `/revise` as a consented
synthetic learner to exercise the input and deterministic grade.

Each numeric item declares conversions (`canonical = input * factor + offset`),
absolute/relative tolerance, accepted forms and significant-figure policy. Boundary
comparison is inclusive, using exact rational arithmetic. Learners see allowed units,
formats and precision instructions, never expected values or tolerance specifications.
See [ADR-018](../decisions/ADR/018-numeric-grading.md) for bounds and conventions.

`make e2e` now starts isolated test servers on loopback ports 13000 (web) and 18000
(API). It retains separate synthetic database schemas and does not reuse the local
application on ports 3000/8000. `make container-smoke` restores the prior running/
stopped state of application services; it still refreshes them to the built images.

Migration 0005 is additive and preserves choice rows. Once numeric documents exist,
prefer a forward fix or retain numeric-aware readers during recovery. Pre-numeric
code cannot read new numeric documents; never delete evidence to enable rollback.

### MinIO image availability

`make services` builds the pinned MinIO release from official, checksum-verified
source because the original public image registry denies clean pulls. The initial
build downloads a pinned Go builder and verified upstream modules; Go is not needed
on the host. Compose caches subsequent builds. Keep existing data volumes when
updating. See [ADR-019](../decisions/ADR/019-minio-source-build.md).

## Synthetic diagnostic and mastery

Run `make migrate seed seed-diagnostic`, start with `make dev`, then sign in, record
synthetic consent, select a subject and open `/diagnostic`. The explicit fixture
command creates independently workflow-reviewed synthetic questions; they are not
NCDC-approved content and never count toward the release inventory. A new subject
diagnostic needs 15 eligible items and a STANDARD representative for each available
topic. Shortage is explicit; no immediate repeats or shortened plans are invented.

Starting again resumes the active subject diagnostic. Reloading after interrupted
submission reconciles saved server progress. Grades remain private until completion;
diagnostic worked solutions are always blocked. The results show score and confidence
per skill plus a first topic practice action. General adaptive ranking is later work.

`make test-unit` runs the deterministic suite without local services; `make test`
also runs integration against PostgreSQL/Redis/MinIO/Mailpit. `make replay-mastery`
reads and compares every stored current/history projection at its recorded timestamp
and configuration. It changes no records and prints only a count. An empty local
learning database reports zero; integration fixtures verify nonempty replay.

Migrations 0006/0007 are additive. Retain evidence and use a forward fix on failure.
Do not run old revision-only readers against new diagnostic records. The diagnostic
browser route and API must deploy together. Production startup remains blocked.

## Recommended practice (synthetic)

After `make migrate seed seed-diagnostic`, sign in with a synthetic consented profile
and open the home page. The next-activity card explains its target and offers five
questions or a diagnostic when evidence is sparse. The API supports 5–10 questions;
it returns insufficient content when the selected skill lacks the requested count.
`make seed-assessment` adds the existing choice fixtures for a larger local inventory.

`make replay-recommendations` verifies stored preview and committed-plan snapshots
without modifying data or calling a provider. Ranking uses the explicitly synthetic
configuration in [ADR-021](../decisions/ADR/021-recommended-practice.md); no real
curriculum priority or calibrated review schedule is implied. Forward-fix migration
0008 preserves historical sessions. Disable new recommended starts rather than
dropping learning or recommendation records during recovery.

## Synthetic reviewed hints

Run `make migrate seed seed-hints` to add reviewed synthetic choice inventory with
three authored hint levels. The hint fixture identity is distinct from earlier
fixtures; re-running does not edit published versions. Use the local staff workflow
to author/review successor versions when hints change. On revision questions, request
a hint before answering and reload to verify durable disclosure. After answering,
additional hints support review without changing the saved score or evidence.
Diagnostics never expose hints. `make replay-mastery replay-recommendations` verifies
stored evidence read-only; automated integration tests exercise nonempty histories.
Migration 0009 is additive; retain historical evidence and use forward fixes rather
than destructive downgrade. See [hint verification](../implementation/E4_HINTS_VERIFICATION.md).

## Synthetic unseen reassessment

Run `make migrate seed seed-reassessment` for additive migration 0010 and distinct
synthetic text scenarios across both subjects, three difficulty bands and two competency
mappings. These software fixtures are excluded from academic release counts. Re-running
preserves published versions; fixture staff use a separate deterministic identity namespace.

From revision feedback choose **Try an unseen reassessment**. Retry after a lost response
or use active sessions on another signed-in device. The one-item result is separate from
the original grade. A shortage is explicit; the selector never repeats a previously
served stable item. Retired targets cannot be served. Completed/expired links do not
mint new reassessments. `make replay-reassessments` checks frozen selection, hashes and
pinned content read-only; nonempty replay is exercised by integration tests.
Keep history and use forward fixes on rollback. See
[verification evidence](../implementation/E4_REASSESSMENT_VERIFICATION.md).

## Synthetic progress and session history

After consent and synthetic practice, open `/progress` for subject, topic and competency
estimates with confidence and mapped-skill coverage. `/history` lists resumable/reviewable
sessions and loads older records with an owned cursor. Dates display in Kampala.
Unfinished, abandoned and expired diagnostics contribute no visible progress evidence.
A completed diagnostic or practice contributes existing immutable evidence; opening these
pages creates no new learning evidence. Reload retries failed reads safely.
No new seed command or migration is required. Verify with `make test`, `make e2e`,
`make lint` and `make openapi-check`; see the
[progress verification report](../implementation/E6_PROGRESS_VERIFICATION.md).

## Synthetic learner flags and staff triage

Run `make migrate` for additive migrations 0011–0012. After saving a synthetic practice
answer, open **Report question or grade**. Diagnostic reporting uses the saved-question
selector without exposing scores. Comments are bounded, encrypted and never written
to browser storage. Retry preserves the same report; reload recovers recorded categories.

Provision a synthetic reviewer using the existing `make staff-role` workflow and open
`/admin/flags`. Inspect reports, claim them, set priority and resolve/dismiss with a
short internal resolution. Every read/decision is audited; authors cannot triage their
own content. Stale revisions require reload. Inspect the exact reported content version
through the content workspace; grades/mastery remain unchanged. Disputed successors
require two reviewers. Resolved flags record a 24-month retention due date; production
retention jobs and approved safeguarding procedures remain required before real data.
See [flag verification](../implementation/E8_FLAGS_VERIFICATION.md).

## Multiple-choice practice

Run `make migrate seed-multiple-choice`. This opt-in fixture adds five reviewed
synthetic multiple-choice items to Physics / Waves, Light and Sound. Enrol a synthetic
adult in Physics, record consent and select that topic at `/revise`. Select Alpha and
Gamma for full credit; a subset or superset earns zero. Reordering the same set does
not create a second attempt. Review content at `/admin/content`, choosing Multiple
choice, adding options and checking the complete key before independent review.
Migration 0013 preserves existing choice/numeric evidence. Deploy generated contracts
and compatible players together and recover through forward fixes after new content
exists. Neither this fixture nor migration authorizes production learner data.

`make e2e` runs two sequential Playwright shards per engine (Chromium, Firefox, WebKit), each with a fresh isolated migrated
schema and API. This keeps synthetic logins within the unchanged 20-per-hour peer
limit; it does not disable security controls. Every browser test runs once. The browser
fixture keeps diagnostic inventory in Mathematics, numeric items in Electricity and
Magnetism, and multiple-choice items in Waves, Light and Sound so selection is deterministic.

## Synthetic data-request intake

Run `make migrate` through additive migration 0015. Sign in with a synthetic identity,
then open `/privacy`; no profile or learning consent is required. Confirm Export or
Delete to record a pending request. Recent OTP verification (under ten minutes) is
required for creation; an active session suffices for owned status reads. A repeat
pending same-kind request returns its existing reference, including after a lost acknowledgement.
Learning withdrawal remains at `/onboarding` and does not remove privacy-request access.

Provision a different synthetic administrator using the existing `make staff-role`
workflow, then sign in and open `/admin/data-requests`. Queue reads and claims require
recent ADMIN access. Claiming starts review and creates an audit entry; it does not
export/delete data or change learning access. There is no completion button or external
notification. Requester identity is excluded from the queue. Operators must not represent
this development intake as completed processing or enroll real learners before fulfillment
and the privacy/legal gates pass. The six-year-after-completion policy is recorded;
export completion now records its deadline; six-year evidence expiry and complete legal-hold coverage
remain gated. The record-hold lifecycle below covers four target types.

Setup installs a pnpm Corepack shim in `.local/tools/bin`, ahead of global package
managers in repository commands. Nested Turborepo tasks therefore retain the pinned
package manager. If a global pnpm upgrade breaks nested commands, rerun `make setup`;
do not weaken version enforcement or change the approved packageManager pin.


## Synthetic owned exports

After intake, select Download export on `/privacy`. Verify OTP again if sign-in is
older than ten minutes. The JSON contains own account/released learning records and an
explicit exclusions manifest. Diagnostic results stay sealed until completion.
A lost response offers Retry download; reload also exposes the same encrypted snapshot.
The copy expires 24 hours after generation, including when workers are stopped.
An expired request cannot regenerate: submit a new explicit EXPORT request. COMPLETED
means made available, not proof that the user saved it. DELETE remains pending.

`make dev` and the Compose worker each embed one Celery Beat scheduler for a five-minute
cleanup task. Run only one scheduler for a local stack; do not run native and Compose
workers together. `make expire-exports` runs the same bounded sweep manually, removing
up to 100 expired copies. Repeat for a backlog. The sweep is idempotent and emits safe
correlation/aggregate metadata. A failed periodic invocation is retried at the next tick;
monitor worker failures and use the manual command to confirm recovery. Never remove
request/account/audit history to clear an export error. Artifact expiry is separate
from six-year accountability evidence retention and the approved 35-day backup policy.

EXPORT_LIMIT_REACHED leaves the request pending rather than returning a partial file.
Large-history fulfillment, exceptional disclosures, deletion/anonymization, full hold
coverage and evidence-expiry processors need further implementation and production acceptance.
No real learner data or provider calls are needed for this synthetic workflow.


## Synthetic deletion-impact review

Create a DELETE request from a synthetic learner account at `/privacy`. With a different
recently authenticated ADMIN, open `/admin/data-requests` and claim it. Select Preview
deletion impact; only that claimant can obtain the report. Expand Record counts and
retention with a pointer or keyboard. The report lists known linked sources, capped
counts and retention/review categories without learner identifiers, answers or comments.
A plus mark means a lower bound. Related staff categories overlap; do not sum the table
as a unique record total. Reload clears the observation; retry a failed preview explicitly.

The report always states that deletion is disabled. Incomplete legal-hold coverage remains an explicit
blocker even when the active registered count is zero. Preview does not revoke access, mutate consent, anonymize evidence
or complete a request. It emits a metadata audit event and uses ten previews/admin/minute;
failed queries/audits produce a generic error without returning a partial report.

Next work must expand record-hold coverage and implement deletion state, review the
precise erasure/anonymization migration with a recovery plan and run synthetic execution
checks. Do not remove immutable triggers or manually delete rows to work around blockers.
A production anonymization/re-identification review and the existing privacy/legal gates
remain required before real learner use. No external provider calls are required.

## Synthetic record-hold review

After `make migrate` (head 0016), use the same independent ADMIN claimant at
`/admin/data-requests`. On an in-review DELETE request select Manage record holds.
Choose Consent, Attempt, Content flag or Data request and supply an owned record UUID,
an opaque synthetic decision-reference UUID, an approved reason and a finite future
end date. The form accepts device-local time; displayed evidence uses Kampala time.
Confirm the authorized decision and create the hold. The default target is the DELETE
request itself, not the whole account. Never enter personal narratives or real learner data.

Use Release hold with a new authorized decision reference and affirmative confirmation.
Uncertain responses offer Retry hold operation with the original key/body; do not create
another hold to recover a lost acknowledgement. Reload holds discards the pending UI
operation and fetches authoritative metadata. Multiple explicit decisions remain separate.
An expired hold cannot be released again. Expiry is checked on access without a scheduled
job, and neither expiry nor release deletes underlying records or evidence.

Creating/releasing a hold clears the displayed deletion preview; fetch a fresh preview
for active counts. Zero active registered holds never establishes clearance: four record
types are supported and incomplete coverage stays explicit. Deletion remains disabled.
Request status stays IN_REVIEW. Hold details/events are internal and excluded from owner
exports. A hold on request evidence does not extend its disposable export-copy lifetime.

Troubleshooting: sign in again after stale OTP; only the current independent claimant
may act. Foreign record IDs return a generic not-found response. Wait after rate limits
(ten new writes or sixty reads/admin/minute). Do not bypass guards, mutate expiry, delete
hold evidence or downgrade migration 0016. Disable routes and use a reviewed forward fix.
Remaining work is expanded hold coverage, deletion execution state, reviewed transforms
and recovery, large-history exports and accountability-expiry processing.

For focused hold/preview regressions, use
`PYTEST_ADDOPTS='-k "legal_hold or deletion_preview"' make test`. The unfiltered
`make test` remains the full regression gate; use focused runs for subsequent narrow fixes.

## Dependency maintenance and lint compatibility

After a reviewed dependency change, run `make deps-lock` then `make setup` to refresh
and validate the frozen lock with the repository-pinned runtime. Avoid a global pnpm
installation with a different Node version. `make test-tooling` exercises the resolved
Next lint plugin; it also runs as part of `make test-unit` and `make test`.

ADR-031 scopes the tinyglobby alias to Next's lint plugin 16.3.6 and includes a pinned
helper patch disabling directory auto-expansion and preserving absolute patterns. Review
both at the next plugin update; do not copy the alias to other fast-glob consumers.
`make security` still audits all dependencies without advisory exclusions.

If Docker startup waits for a macOS administrator prompt, complete it locally. Do not
reset Docker, delete volumes, bypass privilege prompts or claim database/container checks
passed. Lint, type checks, unit tests and native builds can run while Docker is unavailable.

## Synthetic JSON draft imports

Use a provisioned CONTENT_AUTHOR and recent sign-in at `/admin/content/imports`.
Upload original synthetic JSON only, at most 64 KiB and 1–20 records, shaped as:

```json
{"format_version":"kasoma-draft-import-v1","synthetic":true,"records":[{"subject_id":"<catalog UUID>","change_reason":"Import original synthetic fixture","document":{"title":"Synthetic candidate","source":"Original synthetic author fixture","source_locator":"fixture:1","rights_status":"ORIGINAL_KASOMA","rights_evidence":"Original fixture without third-party material"}}]}
```

Use an actual subject UUID from content context. Additional supported draft fields use
the generated `DraftDocument` schema. Incomplete drafts can be edited before submission.
No binary, PDF, archive or media processing is enabled. The normal worker/beat consumes
`imports` every 30 seconds; `make process-imports` drains up to five due jobs manually.
Refresh owner status in the UI. Same-file retry after lost acknowledgement retains its
idempotency key during that page session. A new submission detects already-created owned
identical documents and reports duplicates. Editing a draft requires normal revision checks.

Transient failures retry at 60/120 seconds, then fail; role revocation or 24-hour expiry fails
immediately at processing. Terminal jobs clear candidate payloads. Keep the worker running
for expiry. Pause submission and worker polling for rollback, preserve evidence and deploy
a forward fix; migration 0017 does not provide a destructive downgrade. Raw payloads,
exception details and bearer tokens must never be logged. No import grants publication.

## Local operations monitoring

Use a provisioned ADMIN at `/admin/operations`, then **Refresh operations**. The snapshot
is manual-refresh, not a live guarantee; sampling time is displayed in Africa/Kampala.
Authentication/connection failures clear stale results. `make monitor-operations` samples
locally and emits active alert metadata, without refreshing the Celery heartbeat.
`make test-operations` exercises authorization, thresholds, recovery, minimization,
queue truth, worker heartbeat expiry and the actual registered monitoring task.

The normal Celery operations queue samples every 60 seconds, with a 180-second Redis
heartbeat TTL. Native/Compose host aliases share the database-name/search-path heartbeat
scope; API and worker must use the same identity lookup key and database/schema. A missing,
expired, malformed or future heartbeat is unavailable. A running monitor does not prove
all queues are consuming, so stalled-import alerts remain independent.

Server-side `.env` settings: `OPS_FAILED_IMPORT_THRESHOLD=1` (last 24 hours),
`OPS_IMPORT_AGE_SECONDS=300`, `OPS_FLAG_BACKLOG_THRESHOLD=20`. Limits are inclusive.
Any unresolved HIGH-priority flag or unavailable PostgreSQL/Redis dependency is critical;
missing heartbeat and configured backlog/failure breaches warn. These defaults are not
an approved safeguarding response policy or production SLO. Correct the underlying issue
and refresh; historical failed imports remain counted until their 24-hour window expires.

Investigate dependency/worker health first, preserve failed-job evidence and use the import
owner workflow to correct/resubmit drafts. Review flags through the existing authorized
triage workflow. Do not place report text, candidate documents or exception details in
operational logs. There is no external alert delivery and the sampler cannot log during its
own complete outage; independent production monitoring is still a release requirement.

## Local WhatsApp practice verification

Run `make migrate` for migration 0020 and `make test-whatsapp-practice` for signed synthetic
five-question flows across the three supported objective formats. Fixtures independently review
their synthetic questions, link a consented synthetic account and capture fake replies in memory.
No provider calls, real phone numbers or learner data are used. `make test-channel-assessment`
separately proves shared web/channel grading and mastery parity.

START shows enrolled topic choices; reply to the exact menu message with its displayed number.
Reply to each exact question using one option number, comma-separated multiple selections, or
`value | unit` as instructed. After feedback, CONTINUE requests the next question. A bare or stale
reply cannot answer another question. PROGRESS links to the authenticated web page. STOP/unlink
cancels delivery and clears channel state without removing submitted learning evidence.

The local API wakes the messaging queue after durable intake; `make process-messages` and periodic
worker draining remain recovery paths. Wake-up failures are minimized operational events; broker
outage does not undo intake. Rate limits still apply and latency/load acceptance remains pending.
Dynamic delivery rechecks current consent, enrollment, content approval and link revision.
See [conversation evidence](../implementation/E7_CONVERSATION_VERIFICATION.md) for exact results.

## Local channel operational visibility

After migration 0021, refresh `/admin/operations` as ADMIN to inspect incoming/outgoing queue
counts, oldest pending age, and recent received/created cohorts by current status. Counts cap at
10,000 and explicitly mark lower bounds. Follow `make process-messages` recovery only after checking
configuration/consent/STOP state; do not reset rows or erase attempts to clear an alert.

`OPS_CHANNEL_FAILURE_THRESHOLD` defaults to 1, `OPS_CHANNEL_QUEUE_AGE_SECONDS` to 60,
`OPS_CHANNEL_DISPATCH_P95_MS` to 1500 and `OPS_CHANNEL_DISPATCH_MIN_SAMPLES` to 20. Alerts use
inclusive boundaries; cancellation/rejection alone does not alert. Values are engineering defaults,
not production SLO approval. Local alerts do not notify external services.

Dispatch p95 uses nearest rank over at most the latest 1,000 eligible feedback send observations
in 24 hours. No samples means unavailable timing. It measures incoming durable receipt to local
fake transport acceptance; real learner delivery, HTTP/AI latency and agreed-load evidence require
separate tests. See [channel operations evidence](../implementation/E8_CHANNEL_OPERATIONS_VERIFICATION.md).

## Isolated synthetic recovery drill

Run `make recovery-drill` after `make setup services`. It creates fresh randomly named source and
destination databases on the standard local Compose PostgreSQL service, migrates and seeds original
synthetic evidence, performs pg_dump/pg_restore, verifies row parity/pgvector/immutable guards, and
cleans up only those databases. It never copies or overwrites your configured development database.
The report contains no raw records, tokens, credentials or subprocess diagnostics.

A failed command reports a fixed stage and any exact temporary database names it could not remove.
Inspect that specific run before cleanup; never drop by prefix, force active sessions or reset Docker
volumes. Temporary backup files are private and removed on exit. Native Docker must be available.
This is a logical local fixture drill, not 35-day production PITR or RPO/RTO acceptance. See
[ADR-042](../decisions/ADR/042-isolated-local-recovery-drill.md) and
[verification](../implementation/E9_RECOVERY_VERIFICATION.md).

## Browser engine matrix

`make e2e-install` installs the pinned Chromium, Firefox and WebKit engines. `make e2e-list`
checks the selected test inventory without launching browsers. `make e2e` runs all three engines
sequentially with isolated synthetic schemas per shard. Focused debugging uses
`make e2e-chromium`, `make e2e-firefox` or `make e2e-webkit`; do not run these concurrently on the
same loopback ports. Unknown `KASOMA_E2E_BROWSER` values fail before test execution.

The engine matrix does not replace branded current/previous-browser and physical Android/Safari
release checks. No real account, learner data or external messaging/model service is involved. See
[browser evidence](../implementation/E9_BROWSER_COVERAGE_VERIFICATION.md).

The assessment journey reports `cold_question_transfer` aggregate bytes and enforces the decimal
250 KB target from a fresh context. It includes all encoded response bodies/headers through initial
question rendering and network quiet; the fixture contains no question media. Do not substitute a
warm-cache measurement, skip failed measurements or raise the budget to make a run pass.

## Correlated API response-start timing

Each `api.request` operational event now includes integer `response_start_ms`, measured using a
monotonic clock from middleware entry to response headers. It excludes body/network delivery.
The trace also records response status and the same timing. Requests retain their UUID correlation
header, safe error envelope and no-store policy. No URL, query, credential, identity or payload
is logged. Worker events remain compatible without the optional timing field.

Use the event only for local investigation; aggregated REQUEST_LATENCY remains unavailable in
the ADMIN dashboard. Do not infer a latency/load SLO from one sample. See
[verification](../implementation/E8_REQUEST_TIMING_VERIFICATION.md).

## Restricted assessment database login test

Run `make test-runtime-role` with the local PostgreSQL service available. The integration fixture
creates an isolated synthetic schema and a random temporary login, exercises grading/mastery through
that login, checks denied operations and removes its exact grants/login afterward. A local test
administrator with role creation privilege is required. The generated credential is never printed.
Do not run this against production or real learner data. This is also included in `make test`.

Default application credentials remain unchanged; this is not a production provisioning command.
See [permission verification](../implementation/E9_RUNTIME_ROLE_VERIFICATION.md) for grant scope,
the item-version row-lock constraint and remaining production role/MFA gates.

## Learning-record holds

After `make migrate` applies 0022, the existing independent ADMIN DELETE-request claimant can
record an already authorized hold for a grade, mastery evidence or mastery history row. For a grade,
use the attempt reference; other kinds use their own record UUID. The hold covers only that row,
not its parents, children or an entire account. Never infer deletion clearance from a zero count.
Expiry/release does not remove immutable evidence. See
[verification](../implementation/E8_LEARNING_HOLDS_VERIFICATION.md) and
[ADR-043](../decisions/ADR/043-learning-record-holds.md).

## Expired authentication material

The operations worker/beat started by `make dev` runs kasoma.expire_identity every 60 seconds.
Each batch removes at most 100 already-expired OTP challenges and 100 expired rate buckets,
skipping locked rows. OTP requests no longer perform bulk deletion. Expired codes remain invalid
regardless of worker availability; active windows and account/consent/learning evidence remain.

Inspect identity.ephemeral_expiry status/count events and the existing worker heartbeat when
investigating cleanup. FAILED means the transaction rolled back and both committed counts are zero;
normal scheduled retries can continue. Do not print records, reset rate limits, delete by prefix or
clear tables to resolve a backlog. See
[verification](../implementation/E1_EPHEMERAL_EXPIRY_VERIFICATION.md).
