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
PATH="$PWD/.local/runtime/node_modules/node/bin:$PATH" corepack pnpm exec playwright install chromium
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
