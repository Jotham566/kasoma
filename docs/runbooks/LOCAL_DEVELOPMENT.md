# Local development and recovery

## Resume after a power interruption

Open Docker Desktop and wait for its engine to be ready. In the repository, inspect
`git status --short --branch` before changing checkout; preserve unfinished work.
Do not reset the database, remove volumes or regenerate an existing ignored `.env`.
A PostgreSQL crash recovery message alone is not a reason to restore over the database.

For the current local synthetic profile, run these steps in order:

```sh
make services
make migrate
make containers
docker compose --profile application up -d --wait --wait-timeout 90 api worker export-worker web
make container-smoke
docker compose --profile application ps --format 'table {{.Service}}	{{.State}}	{{.Health}}'
```

`make migrate` applies forward migrations from the checked-out source; confirm that
source is the intended local review candidate first. `make containers` rebuilds images
from that source. These commands preserve existing volumes. Do not run them concurrently
with a different checkout's migration or overwrite unfinished work to match main.
The fake smoke is synthetic and tests the owned export worker/storage path and bounded
request/model observations; it does not call an external model or messaging provider.
Do not run Gemini evaluation as part of recovery. Normal short-text scoring and staged
receipt-hold creation stay disabled unless separately authorized for the chosen profile.

Expect eight running healthy services. Review the UI at http://localhost:3000 and the
local mail viewer at http://localhost:8025. If a service fails, inspect only its bounded
local logs, fix that cause and repeat its health/smoke checks; do not paste secrets or
raw learner data into reports. This restart is not a production restore or PITR test.
Host-native Ollama is a separate optional interactive process; fake automated checks do
not require starting or contacting it. Do not reset synthetic users by rerunning seed
merely because the power failed.


Prerequisites: Git, Make, Python 3.9+ for the setup launcher, npm and Corepack,
Docker Desktop/Compose. `make setup` installs repository-local uv 0.12.18, Python
3.12.14 and Node 24.21.0, then Corepack's pinned pnpm 10.30.2 and locked dependencies.
Install Corepack 0.34.0 if it is missing. Initial downloads require internet;
runtime/test execution uses local services and fakes. No cloud account is required.

On macOS, if Docker Desktop is running but `make services` reports `docker: No such
file or directory`, add its installed CLI directory to this shell before running
the same repository commands:

```sh
export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"
docker info --format '{{.ServerVersion}}'
```

This changes only command discovery; it does not reset Docker or replace its context.

```sh
make setup
make services
make migrate
make seed
make dev
```

Open localhost port 3000. API readiness is `/api/v1/health` on port 8000;
`/api/v1/live` checks only the process. Mailpit is port 8025; MinIO console is 9001.
PostgreSQL uses host port 55432 to avoid an existing host database. Compose gives it a
512 MiB shared-memory ceiling; this is not an eager 512 MiB allocation. The Docker default
64 MiB was exhausted during local regression, causing shared-memory errors and a recovery
interval. Apply the configuration with `make services-db`; it recreates the container while
preserving the named database volume. Do not remove schemas/volumes or relax SQL timeouts to
hide resource failures. Run broad database suites serially on the 16 GB development host.
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
make test-web-identity # focused three-engine identity/consent/logout journeys
make test-web-mobile # focused 320-pixel synthetic touch journey; also included in e2e
make test-load-profile # deterministic load-runner isolation/measurement checks
make test-provider-fault-isolation # owned reads during a stalled fake grading call
make load-objective # optional full-size isolated synthetic HTTP load; creates/drops its own database
make load-history-mixed # optional 50-prior-answer histories and choice/numeric HTTP load
make security
make containers
make security-source
make security-containers
make container-smoke
```

The optional load commands accept only the local development PostgreSQL profile on
loopback port 55432. Each creates, migrates, seeds and removes its own randomly named
synthetic database; neither targets the review database or accepts a supplied HTTP URL.
Run them sequentially and await terminal cleanup. `load-history-mixed` prepares ten
five-question sessions for each of 500 active learners before timing 50 concurrent
choice/numeric journeys; preparation takes additional time. Both commands use fake
providers and make no inference or external delivery calls. A passing result requires
the unchanged latency/completion/format gates and successful cleanup. See
[baseline evidence](../implementation/E9_OBJECTIVE_LOAD_VERIFICATION.md) and
[history/mixed scope and evidence](../implementation/E9_HISTORY_MIXED_LOAD_VERIFICATION.md).

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
The fixture also publishes one synthetic asynchronous export, retains encrypted objects only in
memory, and verifies the restored manifest/keys reproduce the exact frozen bytes without modifying
restored rows. Nonempty job/generation records and their publication guards are checked. This does
not restore MinIO objects or authorize remapping a retired object namespace; the report explicitly
keeps `object_storage_recovery_verified` false.
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

## Synthetic reviewed rubrics

With `make setup services migrate seed` complete, a CONTENT_AUTHOR can select SHORT_TEXT in the
existing content editor, enter criteria/evidence/errors/prohibited inference and save a draft.
Review requires criterion points to sum to the item maximum and all existing curriculum/rights
metadata. Submit to a different ACADEMIC_REVIEWER with the complete checklist; second-review rules
still apply. Returned drafts may be corrected; approved edits require a new item/rubric version.
Use only original synthetic content. Approval does not place these items into learner sessions.

Run `make openapi openapi-check lint test build e2e security` for changes, including fresh/upgrade
migration tests and all three browser engines. See [rubric evidence](../implementation/E2_REVIEWED_RUBRICS_VERIFICATION.md).
Do not deploy a pre-rubric binary after storing SHORT_TEXT documents: it cannot parse them. Preserve
migration 0023 and protected evidence, disable new authoring in a compatible forward fix, and retain
the disabled learner assignment guard. Do not downgrade/drop reviewed rubric records.

## Synthetic model-call events

The existing fake rehearsal emits model.call for each dispatched pass/repair and model.rehearsal
for its final outcome. Correlate using the UUID, call_index and registered prompt version. A
CANDIDATE is unvalidated provider output; only the rehearsal outcome explains agreement/fallback,
and automatic scoring remains false. Tokens are provider-reported, not independently metered;
null values on failure mean unknown consumption. Do not sum null usage as zero or infer model cost.

Fingerprints use a new secret HMAC key for each rehearsal; the key is discarded and hashes cannot
be compared across rehearsals. Never add prompts, answers, context IDs, provider errors or arbitrary
model labels to these events. See [verification](../implementation/E8_MODEL_TELEMETRY_VERIFICATION.md).
Use `make test-unit lint security` for synthetic checks; do not run local or Gemini inference as
part of this workflow. Dashboard AI_USAGE remains unavailable pending durable aggregation.

Use `make test-reviewed-rubrics` for focused real-database rubric checks before the recovery drill;
CI runs the same focused check without replacing full regression or recovery.

For the October security refresh, the runtime Next.js pin is 16.3.8 with bounded Sharp/source-map-js
overrides. ADR-031's lint-only plugin/patch is unchanged and its five tooling checks pass. Use
`make deps-lock setup` then `make lint test build security` after dependency edits. See
[dependency verification](../implementation/E9_DEPENDENCY_REFRESH_2026_10_09.md).

`make build e2e-install test-web-content` runs the isolated staff editor test against deterministic
synthetic HTTP fixtures without PostgreSQL. Browser downloads use .local/browsers. This is a UI
state/serialization test, not API authorization or database acceptance; continue to run the full
`make test e2e` pipeline. The first native browser install lost its shared-cache lock; the isolated
cache avoids modifying that shared directory. On 9 October, Docker Desktop became available
(server 29.8.2). Its CLI was absent from the shell PATH; using the installed CLI directory above
allowed `make services` to start image downloads/builds. Database/browser acceptance still requires
successful migrations, seed and application assertions; daemon availability alone is insufficient.

For focused export/database work, `make services-db migrate test-data-exports` starts PostgreSQL
and Redis without waiting for the MinIO source build. It uses the same approved images, volumes
and loopback ports as `make services`. It does not replace `make services seed` or verify object
storage. The export reader batches ORM hydration while retaining ADR-028 synchronous limits and
privacy filters; see [projection verification](../implementation/E8_EXPORT_PROJECTION_VERIFICATION.md).

The 9 October native database retry passed migrations, focused rubric/export suites and the logical
recovery/restricted-login checks. Full `make test` still needs MinIO/Mailpit: a database-only stack
correctly fails the storage integration test. Do not treat `make services-db` as full setup.

Current native limitation: interrupted module downloads can still fail the MinIO build even with
Docker running. The 9 October source checksum passed, but four Go module downloads ended in
unexpected EOFs. Browser downloads also encountered timeout/connection resets. Preserve checksums,
pins and existing volumes when retrying; daemon/database availability does not establish complete
local service or browser acceptance.

MinIO builds now retain locked project-specific Go module/build caches and try interrupted module
downloads at most three times. Verification failure is terminal; source/compiler pins and checksum
checks remain mandatory. Retry with `make services migrate seed` when the network recovers, then
`make test` for the storage/Mailpit gate. No Docker volume reset is needed. See
[download recovery](../implementation/E0_MINIO_DOWNLOAD_RECOVERY.md). Cache reuse does not replace
verification and does not imply that a previously failed native service build has passed.

ADR-045 adds FLAG_HISTORY and DATA_REQUEST_REVIEW to exact-record hold registration. Use the
history row's own reference, or the reviewed request reference (there is no separate review UUID).
Ownership follows the flag reporter/request owner, not the staff actor. Normal parent triage can
continue; holds do not freeze entire accounts or permit later deletion. Use `make migrate test-legal-holds` for all existing/new exact-record regressions and the full CI gates for acceptance.
See [accountability evidence](../implementation/E8_ACCOUNTABILITY_HOLDS_VERIFICATION.md).


### Private export storage verification (delivery disabled)

After `make services migrate seed`, run `make test-export-storage` to verify ADR-047's format
through the local private MinIO boundary. The test writes only original synthetic bytes under
fresh random generation/object UUIDs, checks anonymous denial and removes only those exact
objects. It does not clear the bucket or use external storage. Missing MinIO is a failed
prerequisite, not a skipped test. See the [storage report](../implementation/E8_PRIVATE_EXPORT_STORAGE_VERIFICATION.md).

This adapter is not yet connected to a learner route or worker. Never invoke its exact-object
removal as a substitute for reviewed lease/expiry/orphan policy. ADR-048 remains a proposal;
large-history fulfillment and cleanup/download acceptance remain pending.


## Asynchronous attachment gateway preparation (ADR-048)

The web gateway recognizes owner export-job and export-file paths, but the corresponding API
router and worker scheduler are still disabled pending the complete slice. Do not treat a gateway
route or passing helper test as learner acceptance. `make test-tooling` exercises streamed lengths,
metadata, closed upstream errors, redirects and both initial/disconnect deadlines without external
services. The initial upstream budget is eight seconds; a successful attachment gets a separate
300-second whole-transfer budget. Cookie authorization stays server-side, with no token in the
attachment URL. `make test-export-jobs` exercises isolated API/database routes with fake storage.

`make test-export-gateway` starts the built Next application and isolated synthetic API to verify
attachment failure redirects, privacy alerts, programmatic errors, method restrictions and
cross-origin denial over real HTTP. Run `make build` first. It uses Playwright's HTTP client and
does not need browser binaries; complete attachment browser acceptance remains in the E2E gate.

Export operations use bounded durable job counts through the existing ADMIN snapshot. Configure
`OPS_EXPORT_FAILURE_THRESHOLD` (default 1) and `OPS_EXPORT_AGE_SECONDS` (default 300) for local
warnings; a snapshot at or above either threshold emits its closed warning. Pending age includes
automatic backoff and running work. Current terminal failures are counted by finish time in the
last 24 hours; explicit retry removes the job from that count. Investigate missing consumers,
storage availability and closed worker events without printing grants/manifests/object keys.
These alerts do not establish legal fulfillment deadlines. `make test-operations` tests SQL truth,
threshold boundaries/recovery, authorization and safe output; native browser checks remain in E2E.


### Dedicated export consumer preparation

`make worker-exports` defines the ADR-048 dedicated consumer: native prefork, concurrency 1,
prefetch 1, queue exports and hostname exports@host. It has no embedded scheduler. Do not use
`--pool=solo` for export generation because it does not enforce the required process hard stop.
The ordinary `make dev`/Compose worker selects operations/imports/messaging explicitly.
The manual export consumer is not automatically started yet, and the application does not yet
schedule export ticks or expose owner commands. Enable the complete topology only with the rest
of ADR-048 acceptance; preserve exactly one scheduler. `make test-export-worker` runs the same
launch recipe against its own synthetic app/schema/Redis namespace with accelerated timeouts,
verifies an unrelated queue stays untouched, and stops/cleans only the resources it created.


### Current candidate runtime (supersedes disabled-stage notes above)

The working branch now wires owner background-export controls and API routes. `make dev` starts
the normal worker with the only Beat scheduler and a separate `make worker-exports` consumer.
`docker compose --profile application up -d --build` starts API, ordinary/export workers, web and
local dependencies. The export worker health check targets only its own node. Do not run native
and Compose workers/schedulers together. The user has requested leaving the Docker application
running for visual review. Keep application services running between tests; `make container-smoke`
preserves their prior state. Rebuild affected images after code changes to refresh that UI.
Candidate wiring is for local synthetic review; ADR-048 acceptance and production release remain
unclaimed. Mailpit captures development email locally; use only synthetic identities.


FR-OPS-002/NFR-MNT-001: each Compose worker now checks its explicit node identity and requires
that node's pong. A healthy export consumer cannot mask an unavailable ordinary worker (or vice
versa). Deterministic checks exercise both actual Compose probes with own, foreign, missing and
invalid replies. This corrects health reporting; queue separation and the sole scheduler remain
unchanged. Runtime container verification remains pending image completion.


### Pinned full Chromium verification

`make e2e-chromium-full` runs both existing Chromium shards using Playwright's bundled
full Chromium in its supported new headless mode (`channel=chromium`). This is useful when
full Chromium is installed while its separate headless-shell download is still pending. It
runs the same tests, isolated API/database, fake providers and acceptance assertions. It does
not use an unpinned system browser or replace the required Firefox/WebKit matrix. Normal
`make e2e` and CI remain unchanged. The optional KASOMA_E2E_CHROMIUM_CHANNEL accepts only
`chromium` and only for the Chromium engine; invalid combinations fail configuration.


The learner UI now has shared navigation and a responsive home/recommendation layout. Review
at http://localhost:3000 after rebuilding the web image. Local visual evidence is retained in
`.local/ui-review`; synthetic notices remain visible. A healthy web container alone does not
establish API, worker or object-store availability.


Run the base `make seed` before assessment fixture commands: they require the synthetic
catalog. If MinIO is unavailable, catalog seeding may succeed while storage initialization fails;
record that failure and rerun `make seed` once storage is healthy. The plain assessment and hints
fixtures share synthetic staff contacts, so back-to-back first-time seeds may hit the normal
60-second OTP cooldown. Wait for that existing cooldown and retry the failed fixture command;
do not relax rate limits or reset developer data. Successful fixture commands are idempotent.


NFR-MNT-001 container build refinement: copy workspace manifests and dependency patches
before installing the frozen web lockfile, then copy application/package source. This preserves
pinned dependencies and runtime image behavior while allowing ordinary UI edits to reuse the
install layer. The previous Dockerfile copied all source before installation, causing repeated
network downloads on every local visual update. Build/cache evidence remains pending.


`make smoke-export` requires the running application Compose profile, healthy MinIO, initialized
private storage, fake model/messaging providers and local Mailpit. It creates one fictional
account/request, verifies its Mailpit OTP without displaying it, waits for real worker publication
and checks the frozen attachment through the web gateway. It signs out its own session afterward.
Its synthetic account/request are retained; normal copy expiry applies. It never resets a database
or deletes unrelated mail/storage. `make container-smoke` now includes this probe and preserves
services that were already running. This is a local synthetic runtime check, not a cloud test.


Container scans use `make security-containers` with a 30-minute per-image timeout so the
initial vulnerability database can download over a slow local connection. Override the
finite bound with `make security-containers TRIVY_TIMEOUT=45m` when needed. This only
changes the timeout; HIGH/CRITICAL failure, database updates and both image scans remain
mandatory. A download timeout is an incomplete scan, never a clean result.


For isolated native attachment diagnostics, run `KASOMA_E2E_BROWSER=firefox make
test-export-download` (or chromium/webkit). It runs the stall/corruption cases serially
and retains Playwright traces on failure under ignored `test-results/`. Select one
scenario with `EXPORT_FAULT=stall` or `EXPORT_FAULT=corrupt`. The synthetic fixture still
uses an isolated database and the real web/API gateway; no external providers run.
Traces contain synthetic authentication state: keep them local and do not commit them.
This focused command does not replace the full browser matrix.


`KASOMA_E2E_BROWSER=firefox make test-export-download-control` runs three plain
loopback HTTP attachment controls without starting Kasoma, PostgreSQL or a gateway.
Use chromium/webkit for comparison. The complete-transfer control verifies native
filename and exact saved bytes. The fault controls track connection closure and repeat
corruption on browser retries; retained traces contain only local synthetic traffic.
It is a diagnostic command, not a replacement for the application browser suite.

`make test-export-download-control-linux` runs those WebKit controls in the official
Playwright 1.58.2 Ubuntu Noble image pinned by manifest digest. It uses the host's
installed Playwright JavaScript package, a read-only filesystem, temporary output,
2 GiB/2 CPU limits and no external network. Only node_modules, the control tests and
their configuration are mounted; no environment file or application volume is exposed.
The image must be available locally (its initial pull requires registry access).
It uses the host architecture: on the M4 this is Linux ARM64, not hosted AMD64.
Its bundled Node 24.13.0 is a browser diagnostic runtime, not a replacement for the
repository's pinned application runtime. Hosted application acceptance remains required.

The export action checks recent-owner job status before starting the browser's native
attachment, with a ten-second client deadline and closed privacy-page errors for
unavailable, expired or unauthenticated requests. The file is never buffered into a
browser Blob. Status success does not authorize file access: the streaming endpoint
independently rechecks ownership, session and expiry. A later interrupted/failed native
transfer is retried through the same action while its frozen copy remains available.


`make test-firefox-native-download` diagnoses the pinned macOS Firefox's own download
manager via its built-in Marionette protocol. It requires `make e2e-install`, uses a
disposable profile and a loopback-only control server, denies external proxy traffic,
and removes only its own profile/process. It never uses a personal browser profile.
The raw stalled-server case currently fails because native cancellation does not close
the socket immediately; the application independently bounds storage reads. Native
manager corruption results are diagnostic, not Kasoma application acceptance.

The delivery service enforces its own five-second object-read deadline in addition
to the private adapter's bound. A client that delays disconnecting after cancellation
cannot leave a blocked object read active for the entire 300-second download budget.
Reader close remains bounded to one second; none of these changes extends export
availability, authentication or job-generation deadlines.


The normal Firefox export-corruption E2E case uses a bounded Python helper to drive
the same pinned browser's ordinary download manager. This avoids its Playwright
interceptor's independently reproduced missing failure notification. Continue using
`make e2e-firefox` or `KASOMA_E2E_BROWSER=firefox make test-export-download`; no
manual cookie copying or extra dependency is required. The helper receives only
validated synthetic cookies over stdin, requires the isolated fixture on port 18000,
and uses the actual privacy UI on port 13000. It denies external proxy traffic and
removes its owned profile/browser after success or failure. Never use personal profiles
or real data. Closed stage codes diagnose helper failures without exposing account
contents or credentials. Full application and hosted acceptance remain mandatory.

## Request timing aggregation candidate (ADR-049)

After `make services`, run `make test-request-metrics` for real SDK, fake-store
lifecycle and isolated local Redis checks. `make test-operations` covers the ADMIN
projection and denial paths. No production data or external telemetry destination is used.

The API owns one five-second collector thread; requests record only integer duration
in fixed OTel buckets. Local Redis holds at most 256 interval bodies, each at most
1024 bytes, with absolute expiry no later than five minutes from the start (and at
most five minutes of actual key lifetime within the one-second host/VM clock tolerance).
Collector freshness expires after 15 seconds. A corrupt or missing unexpired record
makes the aggregate unavailable. Capacity eviction is visible. Measurements are
best effort and can be lost during outages/process exits; they do not prove an SLO.

`OPS_REQUEST_P95_MS=500` and `OPS_REQUEST_MIN_SAMPLES=20` configure local alerts.
The p95 is a bucket interval: a threshold is alerted only when its lower bound proves
the breach. The ADMIN operations page requires explicit refresh and distinguishes
empty, unavailable, measured-zero and overflow states. No automatic external alerts
are sent. Disable collection and let the finite keys expire for rollback; do not flush
Redis. Native API/browser/backend/container checks pass; hosted acceptance remains pending.
`make smoke-request-metrics` checks fresh collection from the running API with only
loopback liveness traffic and scoped Redis reads. It is also part of `make container-smoke`.

Full browser runs retain failure traces in ignored `test-results/`. These contain
synthetic session data: keep them local, use fictional accounts and do not publish
raw traces/logs. Consent-success checks use an anchored positive sentence, avoiding
the otherwise matching paused-consent explanation.

## Hosted verification profile

CI sets `COMPOSE_FILE=docker-compose.yml:docker-compose.ci.yaml` to use the official,
digest-pinned Mailpit mirror. Run `make check-ci-profile` to validate that merge quietly
without changing any running service. Native Compose remains on its existing image.
The workflow has a 90-minute whole-job limit and a lock-keyed browser-binary cache;
all setup, migration, test, recovery, browser, security and container steps still run.
See [CI verification](../implementation/E9_CI_RUNTIME_VERIFICATION.md) for the observed
failures, artifact equality evidence and pending hosted gate.

### CI image-cache recovery

The hosted workflow uses a public Docker Hub cache on its disposable Linux runner
before starting services. `make ci-docker-config` merges the cache into the temporary
file specified by `CI_DOCKER_CONFIG`; it refuses ordinary local execution. The workflow
validates and installs that file and restarts only the hosted daemon. Do not run these
privileged workflow steps on the review machine. Local Compose and its eight services
remain unchanged. Cache misses fall back to Docker Hub and can still be throttled.
See [CI verification](../implementation/E9_CI_RUNTIME_VERIFICATION.md).

If hosted cache misses are throttled, maintainers can set repository Actions secrets
`DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` using a read-only Docker Hub token. The
workflow checks availability without printing values, uses the pinned official login
action and logs out afterward. Do not put these credentials in `.env`, Compose, source,
chat or browser variables. Fork runs without secrets continue anonymous public pulls.

### Durable grading storage preparation

`make test-grading-work` verifies the pure transition policy and PostgreSQL store in
isolated synthetic schemas, without model calls. `make migrate` applies additive
migration 0026; it does not enable short-text assignment or dispatch. Owned exports and
deletion previews include minimized work/history metadata. No worker should enqueue
or process learner short-text work until the remaining privacy, role and learner-path
[gates](../implementation/E4_DURABLE_GRADING_VERIFICATION.md) pass.

Migration 0027 adds exact `GRADING_HISTORY` holds. `make test-grading-work` covers the
independent administrator workflow and SQL preservation. `make build test-web-privacy`
runs the privacy journeys across Chromium, Firefox and WebKit, including the updated
record selector and incomplete-coverage wording. These commands use synthetic data.

`make test-short-text-eligibility` verifies the proposed ADR-050 calibration/audit
policy with synthetic report and approval IDs. It makes no model call and enables no
band or learner scoring. Use `make test-unit` for complete component regression; actual
academic reports, authorized persistence and worker publication remain separate gates.

`make test-grading-bands` verifies migration 0028's immutable calibration metadata,
row locking and sticky disablement using isolated synthetic schemas. No seed band is
created in the review application and no activation endpoint exists. `make test-runtime-role`
checks that the real restricted login can disable but cannot write approval metadata or
the activation timestamp. `make recovery-drill` includes unapproved synthetic band/history
rows in its isolated logical restore; this is not production PITR or academic acceptance.

### Publication/audit storage checks

`make test-grading-publications` exercises isolated synthetic grade publication,
atomic audit selection, rollback, replay and privacy controls using real PostgreSQL.
`make test-runtime-role` checks the actual restricted login. Run `make migrate` for
additive migrations 0030/0031; do not reset the developer database. This preparation
provides no activation command, production approval or learner short-text delivery.

### Candidate short-text flow verification

If the default Trivy database mirror stalls, use
`make security-containers TRIVY_DB_REPOSITORY=ghcr.io/aquasecurity/trivy-db:2`.
This is the scanner's alternative official database source; scan version, severity
threshold, failure exit code and finite timeout are unchanged. Progress bars are
suppressed in logs. Do not skip database refresh or ignore findings to pass a check.

`make test-short-text-flow` runs isolated PostgreSQL/API/worker cases, using actual
content review, encrypted answers, deterministic fake model results and fixture-only
report/safety authorities. Normal startup supplies neither authority, and
`SHORT_TEXT_ENABLED` defaults false. Do not enable actual learner scoring or substitute
plausible UUIDs/counts for real report approval. Draft migration 0032 remains on its
working branch until full acceptance; no developer-database reset is required.

The owned short-text feedback endpoint permits 120 reads per account per minute;
the web makes at most 12 automatic polls, three seconds apart, with one in flight.
Manual retry remains available. Rate limits never create a score or restart grading.

Finish `make build` before starting browser verification. Do not rebuild the native
web output while an E2E server is using it: replacing `.next` during a journey can
invalidate its route manifests. Docker builds use their own filesystem output.

The review stack can be kept running with the documented
`docker compose --profile application up -d --wait api worker export-worker web`.
`make container-smoke` restores the running/stopped state it found; start the review
stack first when it must remain available after the smoke check.


## Independent grading review candidate

Use `make test-grading-reviews` for strict contracts and isolated PostgreSQL review,
privacy, sampling and disablement cases. `make test-runtime-role` exercises the encrypted
flow and expert completion under a real temporary restricted login. `make test-web-short-text`
uses disposable synthetic schemas and FakeModelProvider across all three engines; it
includes the staff `/admin/grading` workspace, 320-pixel controls, accessibility,
pagination and lost-acknowledgement retry. Its screenshots are local artifacts only.
Do not run `make build` while the native browser server is using the same `.next` build.

The persistent stack retains normal short-text scoring disabled. A staff queue may be
empty until synthetic audit assignments exist; no fabricated reviews should be created
in the ordinary UI. Tests create their own authorized fixture and never call Ollama,
Gemini, email, messaging or cloud providers. Populated `make recovery-drill` verifies
review/counter data, original encrypted answer/result and immutable guards in disposable
owned databases. It is logical recovery, not production PITR or object-storage restore.

After interruption, inspect Git and `docker compose --profile application ps`; use
`make services` and the documented application profile start command to restore existing
containers/volumes. Never reset volumes to make checks pass. Preserve failed-run evidence
and rerun affected checks before reporting success.


Run native Playwright commands sequentially: their default `test-results` directory
is shared even when web-server ports differ. Starting the UI harness while a full
engine run is active can delete the other run's trace files during context closure.
This is a harness collision, not passing application evidence; preserve the failure
and rerun serially. Never rebuild `.next` while a native browser server uses it.


## Offline synthetic evaluation report comparison

`make eval-compare KASOMA_EVAL_BASELINE=/absolute/baseline.json KASOMA_EVAL_CANDIDATE=/absolute/candidate.json`
reads existing synthetic, payload-free short-text report-v1 files only. The command
makes no inference/provider call and imports no model adapter. It accepts at most
512 KiB per regular local file, rejects final-path symlinks/special files/duplicate
keys/unknown fields/inconsistent counters, and emits a closed error with exit 1 on
invalid or incomparable input. Paths, excerpts and exception diagnostics are withheld.
Only matching frozen benchmark/version/case count, task/output schema and metric policy
compare. Model/prompt/configuration differences are explicit closed changed-field names.

Report metadata includes exact model/adapter/runtime/quantization/context/sampling,
benchmark and schema versions, declared license/terms digests and hosted observed quota/
rate-limit counts. Local profiles follow specification 18; these declarations are not
verified academic, licensing or provider approvals. All planned cases remain in metric
denominators; low-confidence, invalid, failed, safety and unrun cases are separate.
Unavailable latency/usage stays null. Output contains only safe report IDs and aggregates,
not arbitrary model labels, raw answers, prompts or credentials. No output can activate
scoring. Genuine benchmark/report authority and actual local/Gemini evaluation remain
separately gated. Do not run Gemini evaluation without the owner's explicit request.


The report's SYNTHETIC_PAYLOAD_FREE marker is declared metadata; the comparison does
not perform or certify dataset sanitation. It cannot establish trusted benchmark/report
provenance or academic, licensing or processor approval. Actual evaluation must retain
its separate sanitizer and frozen academic authority gates.


## Local grading queue observation

`make test-grading-operations` checks contracts and real isolated PostgreSQL queue,
lease, neutral/fake-grade, independent review, 24-hour boundary, authorization and alert
states. `/admin/operations` shows aggregate grading work with no learner/attempt/band
identifiers. `OPS_GRADING_AGE_SECONDS` defaults to 60 (allowed 1–86400); it is a local
stale-work investigation threshold, not the eight-second AI feedback SLO. Expired leases
are counted without mutating work. Normal worker recovery remains responsible for them.
Processing fallback includes expected provider refusal and validation/budget fallback;
it is not an academic error rate. Pending audits can be sealed, and a historical
post-activation disabled-band count does not create a permanent alert. Model spend,
academic error rate, genuine approval and production telemetry remain separate gates.


## Runtime short-text resource ceilings

The worker snapshots `SHORT_TEXT_MAX_REQUESTS` (default 3, range 2–3),
`SHORT_TEXT_MAX_TOKENS` (default 16384, range 2–16384) and `SHORT_TEXT_TIMEOUT_MS`
(default 5000, range 1–5000) once per claimed job. These are shared by both independent
passes and the single optional repair; they cannot enlarge the previous hard envelope.
The dispatch wrapper and rehearsal use the same deadline. Very small ceilings can
prevent all dispatch or a second required pass: the saved attempt becomes neutral,
with no grade/mastery, and exact retries do not repeat work.

These server-only limits are not a new learner/day/fleet quota, a billed-provider budget,
a latency SLO or academic approval. Normal startup remains disabled without genuine
report/safety authority. Resource settings do not turn plausible approval UUIDs into
trusted configuration/report evidence. Future genuine evaluation/approval must cover its
actual model/prompt/configuration and relevant resource settings. No actual evaluation,
Ollama or Gemini inference is run by this change; tests use FakeModelProvider only.


### Local model observation verification

`make test-model-metrics` verifies the owned SDK and real Redis namespaces with only
synthetic fake-provider outcomes. `make smoke-model-metrics` sends one fixed fake
probe to the running ordinary worker and waits at most30 seconds for a new private
aggregate interval. `make container-smoke` includes this probe. No real inference,
learner data, cloud, email or messaging delivery is involved.

The ordinary Compose/native worker explicitly imports `apps.worker.model_metrics` and
sets `MODEL_OBSERVATION_ENABLED=true`. Export workers explicitly set false; API and
other process defaults are false. Only development/test worker roles initialize the
collector. Source/SDK metadata never enter Redis. Collection every five seconds is
best effort, with 15-second freshness and absolute five-minute expiry from the earliest
observed outcome, not retry time. A stale/failed collector is unavailable; costs and
unknown token totals remain unavailable. The ADMIN card explains capping/loss limits.
`OPS_MODEL_GATEWAY_ATTEMPTS_THRESHOLD` defaults100 (1–10,000) and warns on retained
observed volume; it neither rejects work nor represents a production budget policy.

After a power interruption, preserve volumes, run `make services`, then the documented
application-profile startup and `make container-smoke`; confirm all eight services are
healthy before relying on the dashboard. Never reset volumes to restore a metric.


### Terminal channel receipt holds (verified, creation disabled)

`make test-channel-receipt-holds` uses isolated synthetic schemas, including clean0034
and0033-upgrade/replay, SQL guards, clock/race cases and real signed local fake-delivery
opt-out. `make test-legal-holds test-whatsapp` protects existing behavior. Creation is
false by default in `.env.example`; tests explicitly opt in through typed settings.

Before enabling CHANNEL_RECEIPT_HOLDS_ENABLED, verify0034/0035 and deploy all API/worker
readers supporting both new kinds. The UI takes available types from the authorized
hold page. With the flag disabled, evidence stays readable/releasable. After new kinds
exist, rollback keeps the new reader/guards and disables creation; use a forward fix.
Never downgrade/drop holds or reset volumes. No real-data or legal approval is inferred.

Only already-minimized terminal owned receipts qualify. A pending message or unbound
sender is not made eligible by guessing ownership or clearing data solely to create a
hold. Do not freeze live STOP/unlink/code expiry. Other channel state and deletion
execution remain separately gated; see ADR-055 and its verification register.

The applied 0034 receipt guard has a json equality edge case on held menu no-ops.
Forward migration 0035 compares canonical JSONB rows without changing stored menu data or hold
metadata. Keep creation disabled through this upgrade; clean and existing-menu-hold
upgrade/replay tests must pass before activation. Do not edit/revert an applied migration.


### Legacy hold clock verification (verified)

`make test-hold-delete-clock` exercises actual wrappers with valid owned synthetic holds
created after a probe transaction begins, isolating timing on temporary rows without
disabling original append-only protection. Forward0036 replaces only DELETE clock
arguments; keep historical predicate semantics and all preservation evidence. Complete
clean/0035-upgrade, replay, existing holds, restricted-login, recovery/security and hosted
checks before promotion. This does not authorize or implement account erasure.

### Bounded ADMIN audit activity (verified synthetic scope)

Open `/admin/audit` from the staff workspace and explicitly refresh after synthetic
ADMIN sign-in. This shows the newest at most 10,000 audited actions in the last
24 hours, grouped into fixed categories; it does not expose individual records or
establish retention compliance. A cap warning means counts omit older matching
activity. No current result is shown after a failed refresh.

`make test-audit-activity` checks real role/rate/revocation, window/cap and SQL evidence
controls; `make test-web-audit test-web-content` covers real authenticated browser
access and isolated empty/capped/error UI harnesses. Migration 0037 adds an index
without rewriting evidence. Preserve the source audit rows/guards during rollback.

### Disposable hosted CI disk capacity

`make ci-storage-report` is read-only. `make ci-storage-check` is also read-only but
fails below the fixed 8 GiB phase budget. `make test-ci-storage` tests only synthetic
temporary directories and profile refusal. `make ci-runner-storage` is privileged
preparation for the disposable Ubuntu 24.04 X64 GitHub-hosted workflow only; it must
refuse the developer/self-hosted profile before mutation. Never sudo that command
locally or forge its context. It removes only the two versioned unused SDK roots
and requires 24 GiB afterward; it never prunes Docker or resets application volumes.
See [ADR-059](../decisions/ADR/059-disposable-ci-runner-storage.md) and
[verification](../implementation/E0_CI_STORAGE_VERIFICATION.md).

On a failed hosted capacity gate, retain the before/after numeric disk and Docker usage
diagnostics and fix that disposable job's profile. Do not disable browser/security
checks, lower product acceptance or delete developer test schemas by prefix.

### Minimized channel snapshots (ADR-057 bounded synthetic implementation)

Keep CHANNEL_PRESERVATION_ENABLED=false during the additive 0038/all-reader rollout.
This flag is separate from terminal original-receipt holds. The implementation is authorized
for synthetic development only; real-data/production processing and account erasure
remain separately gated. See
[verification](../implementation/E8_CHANNEL_PRESERVATION_VERIFICATION.md).

Use `make test-channel-preservation test-channel-clock` for the strict private format,
contracts, database upgrade/races/expiry, actual restricted logins and advancing-clock
regressions. Run `make build` before `make test-web-channel-preservation`; the latter
uses isolated synthetic schemas, explicit fake providers and three browser engines.
Do not rebuild native .next during an active browser run. `make recovery-drill` includes
bound ciphertext, disposal metadata and sequence-position recovery after operational
source removal. It creates/drops only its own generated synthetic databases; it is not
production PITR or object-storage recovery verification.

The ADMIN who independently claimed a pending DELETE request must recently sign in.
Open record holds, provide the actual source link UUID/revision and check the exact
current version before confirming an authorized finite decision. A conversation has no
independent source UUID. The resulting record reference is a new snapshot UUID; use
that UUID for additional decisions on the same snapshot. A stale source requires a
fresh check and affirmative confirmation. An uncertain capture response must retry the
same key/body; never silently recapture changing state.

Only approved minimized link/conversation fields are copied. No contacts, message
bodies, codes or tokens are retained by this mechanism. There is no payload viewer or
source-browsing endpoint. STOP barriers, unlink, withdrawal, normal source expiry and
shared grading remain independent. The worker removes ciphertext after the last exact
decision ends; immutable disposal/capture accountability follows the parent's existing
policy. Keep creation disabled on rollback while preserving readers, release, guards
and cleanup. Never drop evidence tables, reset volumes or reinterpret this subset as
full legal-hold coverage or permission to erase an account.

### Progress replay regression

`make test-progress` checks the frozen synthetic progress-rollup-v1 outputs,
request-local replay-work bound and existing consent/sealed-diagnostic/read-only
API cases. Every progress request builds a fresh replay context at its own explicit
time; no persistent/shared cache or environment flag is added. See
[verification](../implementation/E6_PROGRESS_REUSE_VERIFICATION.md).

### Shared select touch targets

`make test-web-select-targets` runs the existing synthetic narrow touch journey in
Chromium, Firefox and WebKit, requiring 44-pixel select targets, keyboard focus, axe
and 320-pixel reflow at normal and 200% text before completing saved practice.
`make test-web-content` includes the corresponding controlled staff editor checks.
See [verification](../implementation/E6_SELECT_TARGET_VERIFICATION.md); this does
not replace physical-device acceptance.

### Conversation mutation-version permissions

0038 assigns conversation versions through a noncycling sequence in a trigger. A
future separately reviewed channel-writing database role needs USAGE on that sequence
in addition to its narrowly scoped conversation writes. The snapshot-inspection role
does not mutate conversations or require that grant; the assessment role is not a
channel-writing role. Actual restricted capture/assessment tests do not establish a
production channel-worker role profile. Verify that distinct role and forward rollout
before any real-data deployment; do not broaden assessment or inspection privileges.

## ADR-060 additive export preservation candidate

`make test-export-recovery` checks read-only verification and damaged-byte/object
rejection for the original synthetic export fixture. The complete `make recovery-drill`
adds separately authorized exact receipt holds.

`make test-export-evidence-holds` exercises isolated synthetic schemas, exact owner
checks, original retry binding, populated 0038-to-head upgrade and an actual
restricted login. `make test-web-privacy` covers the three-engine operator controls;
its advertised-option test does not enable the server flag. Keep
EXPORT_EVIDENCE_HOLDS_ENABLED=false in the running review stack until acceptance.
This increment adds no maintenance routine or retirement schedule. No review-stack
purge, real data, inference or external delivery is needed or authorized. See
[verification](../implementation/E8_EXPORT_EVIDENCE_HOLDS_VERIFICATION.md).

## ADR-060 restricted SQL retirement candidate

`make test-export-retirement` uses owned isolated synthetic schemas and an actual
EXECUTE-only maintenance LOGIN. It creates historical synthetic exports through
normal fake identity/export flows and normal copy cleanup, then exercises due/hold/
privilege/scan/audit/race boundaries. Tests deliberately inject isolated malformed
fixtures and ownership damage; no review-stack purge or external provider runs.
`make migrate` installs 0041 default-disabled; it creates only a minimal NOLOGIN owner,
not a review-stack executor LOGIN. Keep export_retirement_state.enabled=false.
The routine independently rejects the normal public review scope even if that state
flag is altered. Runtime configuration/scheduling/health are separately verified in the operations
evidence below; they remain default-disabled and isolated-synthetic only.

Logical restore with --no-owner/--no-acl must leave execution refused until privileged
ownership/ACL repair and a fresh explicit isolated opt-in. The recovery drill verifies
that denial and disposes only its generated databases/owner roles. Do not equate this
with production backup acceptance. See [SQL evidence](../implementation/E8_EXPORT_RETIREMENT_VERIFICATION.md).

## ADR-060 isolated synthetic evidence maintenance

Requirements: FR-ID-006, FR-OPS-003, BR-010, NFR-SEC-002, NFR-MNT-001.
This candidate is restricted to owned `identity_test_<32 lowercase hex>` schemas or
public schemas in the generated retirement/recovery databases named by ADR-060.
It refuses ordinary review public. Never enable it for real data, account erasure,
the running review stack, or a database whose ownership/purpose is unconfirmed.
Use `make test-retirement-runtime` for automated isolated fake-provider verification.

The operator commands are `make retirement-provision`, `make retirement-enable`,
`make retirement-disable` and `make worker-retirement`. Set
`KASOMA_RETIREMENT_CONFIG` to a new ignored `.local` file and
`KASOMA_RETIREMENT_SCHEMA` to the exact existing owned synthetic schema for the first
three commands. Shared `DATABASE_URL` selects the local privileged setup connection;
never print it. Provisioning creates the restricted LOGIN and an exclusive 0600
configuration, with both private switches false; it refuses an existing role/file.
Do not retry provisioning by deleting roles or overwriting configuration. Resolve
rotation/recovery explicitly. A transaction failure may leave a refused, non-usable
configuration; preserve it for private diagnosis before another attempt.

Inspect/edit the private file locally without copying its secret URL into commands,
logs, source or client variables. To run in an approved isolated fixture, set its
`EXPORT_RETIREMENT_ENABLED` and `EXPORT_RETIREMENT_HOLDS_ENABLED` true. Invoke
`make retirement-enable` against that same privileged database/schema. It independently
checks the actual restricted LOGIN/profile before enabling persisted SQL state and
records a minimized configuration audit; it executes no batch. The private consumer
reads only this file, not shared `.env`. `make worker-retirement` consumes only
`privacy-maintenance`, with concurrency/prefetch one and no Beat. Native spawned
children restore only this app's registration and private settings; ordinary tasks
and shared credentials are excluded.

Optional scheduling belongs to a separately configured ordinary worker for that
same isolated fixture: `EXPORT_RETIREMENT_ENABLED=true`,
`EXPORT_EVIDENCE_HOLDS_ENABLED=true`, and the matching synthetic `DATABASE_URL`.
`EXPORT_RETIREMENT_INTERVAL_SECONDS` defaults 300 and is bounded 60–3600. Each
parameter-free message expires after one interval; do not run multiple Beat schedulers.
No scheduler is enabled by provisioning or by the private consumer command. The normal
Docker review `.env` keeps its switches false and needs no executor credential.

To stop: run `make retirement-disable` against the original matching privileged
scope; new-creation hold enablement is not required to disable. Set the private flag
false, stop its dedicated process and disable its isolated scheduler. Already-running
transactions finish/roll back independently; no force deletion or receipt tombstones
are introduced. Hold reads/releases and 24-hour copy cleanup remain independent.

ADMIN operations show due parent counts (capped at 10,000), scope/activation and
best-effort count-only observations. Exact holds, uncleared copies and dependencies
can prevent removals. Failure observations use fixed five-minute intervals and expire;
Redis loss must not trigger destructive retries or prove SQL failure. A failed task
can be retried through the same SQL capability; committed batches are replay-safe.
`RETIREMENT_FAILED` begins at one observed interval failure; `RETIREMENT_STALLED`
begins at twice the configured schedule interval without a database batch/activation.
Both require the scheduler, database switch and isolated scope. The dashboard grants
no enable/delete control. Durable minimized SQL audit remains transaction-atomic;
aggregate cache/UI observations are not an acceptance or compliance record.

See [complete bounded verification](../implementation/E8_EXPORT_RETIREMENT_OPERATIONS_VERIFICATION.md)
for exact results and limitations. Production/privacy authority, full preservation,
account erasure and finite disposal of other audit classes remain separate release gates.

### Synthetic lost-response interception controls

`make test-commit-interception` runs three-engine loopback reset/HTTP/missing-key
controls; `make test-web-whatsapp` runs the real local fake-channel journey in each
engine. The interception helper retries one ECONNRESET only for a UUID-keyed local
API mutation, retaining its exact body and headers. It never retries an HTTP error,
follows redirects or changes application/test retry policy. Persistent failure is
reported through a fixed diagnostic without request headers. The channel test still
confirms the first committed response before aborting it and verifies exact code/key
recovery. A failed hosted attempt remains failed until a complete corrected run passes.

### Feedback action stability

`make test-web-assessment` runs the resumed pointer/keyboard flow, withdrawal barrier
and delayed post-grade hint-response stability regression in all three engines.
Optional review hints render below feedback actions so loading cannot move their
pointer targets. The regression retains a real pointer click and the existing cold
question transfer budget. Failure-only diagnostics report capped endpoint-kind/status
counts and scalar focus/visibility state, without request IDs, payloads or credentials.
See [verification](../implementation/E3_REVIEW_ACTION_STABILITY_VERIFICATION.md).

## Verified bounded disposable load owner lifecycle

`make test-load-profile` runs deterministic contract checks without external calls.
`make test-load-role-cleanup` adds actual local PostgreSQL migration/cleanup and
privilege-refusal checks over exclusively created synthetic resources. The shared
`make load-objective` and `make load-history-mixed` lifecycle now requires absence
of its exact derived role before migration and removes only that role after its own
database is successfully dropped. The tool exclusively creates its role in a
transaction and confirms its OID; cleanup requires that same identity. An absence
check alone grants no ownership. A pre-existing, replaced, unsafe/shared or dependent role
is preserved and the run fails closed. Do not sweep existing orphan roles or use
DROP OWNED, revoke dependencies, or clean developer/application resources.
See [bounded verification](../implementation/E9_LOAD_ROLE_CLEANUP_VERIFICATION.md).
