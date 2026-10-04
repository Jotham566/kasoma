# Kasoma

An adaptive revision and mastery platform for Uganda's competency-based secondary education.

Kasoma's planned learning loop is **Diagnose → Recommend → Practice → Explain → Reassess → Update mastery**. The MVP focuses on Senior 4 Mathematics and Physics, with a full web experience and linked-account short practice through WhatsApp.

## Repository status

The local synthetic implementation includes identity/consent, independent content review, choice/
multiple-choice/numeric assessment, diagnostic/mastery, recommended practice, hints/reassessment,
progress/history, content flags/triage, bounded JSON imports, data-request exports/expiry, deletion
previews and specific-record legal holds. Linked five-question WhatsApp practice uses the shared
grading/mastery service with fake transport, signed durable intake and STOP barriers.

ADMIN operations includes channel queue/status and fake-dispatch timing. Offline short-text
candidate validation and budgeted dual-pass rehearsal are implemented; learner short-text scoring
is disabled. An isolated synthetic logical restore and 60 Chromium/Firefox/WebKit journey
executions pass; cold first-question transfer is below 250,000 bytes in those fixtures.

These are engineering results, not academic or production acceptance. Erasure/anonymization,
remaining holds/retention/large-history work, full short-text learner integration, load/latency,
academic benchmarks/content approval, privacy/provider decisions and pilot release gates remain.
Use the [current sprint](docs/implementation/CURRENT_SPRINT.md),
[requirements evidence](docs/implementation/REQUIREMENTS_TRACEABILITY.md) and
[release register](docs/implementation/RELEASE_GATES.md) for exact commits, checks and limitations.

## Local setup

Install Git, Make, Python 3.9+ (setup launcher), npm, Corepack 0.34.0 and Docker
Desktop with Compose. Start Docker Desktop, then:

```sh
make setup
make services
make migrate
make seed
make dev
```

Setup pins Python 3.12.14, uv 0.12.18, Node 24.21.0 and pnpm 10.30.2 locally,
installs locked dependencies and generates ignored local credentials. Existing
`.env` and database state are preserved. Web: localhost:3000; API: localhost:8000;
Mailpit: localhost:8025; MinIO console: localhost:9001.

Run `make lint typecheck test openapi-check build`, then `make e2e-install` and
`make e2e security containers recovery-drill`. Missing dependencies fail clearly. The runbook
covers native Ollama, safe shutdown, migrations, CI and deferred evaluation gates.

## Documentation

| Document | Purpose |
| --- | --- |
| [Product whitepaper](docs/product/PRODUCT_WHITEPAPER.md) | Long-term product vision |
| [Product roadmap](docs/product/PRODUCT_ROADMAP.md) | Scope and delivery plan for the 12-week MVP |
| [Engineering specification index](docs/specifications/00_README_Source_of_Truth.md) | Specification inventory, authority order and fixed MVP boundaries |
| [Implementation backlog](docs/specifications/11_Implementation_Backlog.md) | Ordered implementation slices |
| [Coding agent operating contract](docs/specifications/12_Coding_LLM_Operating_Contract.md) | Required engineering workflow |
| [Architecture decisions](docs/specifications/13_ADR_and_Decision_Log.md) | Architectural decisions and change control |
| [Repository bootstrap contract](docs/specifications/15_Repository_Bootstrap_and_Environment.md) | Requirements for the development environment and CI |
| [Current sprint](docs/implementation/CURRENT_SPRINT.md) | Completed preparation, next slice and open differences |
| [Implementation traceability](docs/implementation/REQUIREMENTS_TRACEABILITY.md) | Implementation and test evidence for every SRD requirement |
| [ADR index](docs/decisions/ADR/README.md) | Existing decisions and location for new proposals |
| [Changelog](CHANGELOG.md) | Repository and product change history |

## Repository layout

```text
AGENTS.md                 Engineering instructions and specification navigation
docs/product/             Product roadmap and whitepaper
docs/specifications/      Authoritative engineering specification pack
docs/decisions/ADR/        ADR index and future decision records
docs/implementation/      Current sprint and live requirements evidence
apps/                     Web, API and worker entry points
services/                 Shared Python services and domain modules
packages/                 Shared packages and generated client
infra/                    Local containers; production deployment deferred
tests/                    Unit, contract, integration and browser tests
scripts/                  Repository maintenance and validation tools
```

Implementation directories contain the foundation components. Their presence does
not establish acceptance of learner functionality. Documentation checks remain
available with `make check-docs` and are distinct from application tests.

Keep credentials, real learner data, production exports and restricted academic
material out of Git. `.env.example` leaves secrets empty and disables external
calls. Automated tests use deterministic providers; local runtime requires no
cloud account. Production startup and model evaluations remain gated.

## Approved architecture

The [system architecture](docs/specifications/02_System_Architecture.md) specifies a modular monolith with asynchronous workers:

- Next.js, React and TypeScript for the web application.
- FastAPI, Pydantic, SQLAlchemy and Alembic for the Python API and persistence.
- PostgreSQL for authoritative data; Redis and Celery for background work.
- Provider interfaces for AI, messaging and object storage, with local or deterministic fake adapters for development and tests.
- A pnpm/Turborepo monorepo using the reserved directories above.

These decisions govern the foundation and subsequent slices. See [CONTRIBUTING.md](CONTRIBUTING.md) for the change and review workflow.

## Local identity slice

After setup/migrations/seed, open `/onboarding` for synthetic registration and
consent. Email codes are captured in local Mailpit; phone tests use an injected
fake adapter. No real provider delivery or real learner enrollment is enabled.
See [E1 verification](docs/implementation/E1_VERIFICATION.md) and
[ADR-014](docs/decisions/ADR/014-identity-consent.md).

## Staff content workflow

The content workflow at `/admin/content` supports single-choice, multiple-choice and numeric
drafts, independent review, corrections, approval and retirement. Synthetic mappings and
workflow approvals do not count as academically approved production content.
See [E2 verification](docs/implementation/E2_VERIFICATION.md) and the
[local development runbook](docs/runbooks/LOCAL_DEVELOPMENT.md) for role provisioning.

### Synthetic topic practice

After `make setup services migrate seed`, run `make seed-assessment` explicitly
to create 30 synthetic workflow fixtures through the author/reviewer service.
Run `make dev`, complete a synthetic profile and consent at `/onboarding`, then
open `/revise`. Only five-question topic practice is exposed in the UI; the API
accepts 5–10 when inventory permits. Resulting mastery estimates describe synthetic software fixtures, not an academic content release. See [current sprint](docs/implementation/CURRENT_SPRINT.md).

For numeric development fixtures, run `make seed-numeric` after migrations. This
adds five synthetic numeric items to Physics / Electricity and Magnetism. They
exercise software rules only and do not count as academic release content.
Units, inclusive tolerances, accepted forms and precision are explicitly reviewed;
see [ADR-018](docs/decisions/ADR/018-numeric-grading.md).

The synthetic diagnostic and initial mastery slice is available locally; see
[E5 verification](docs/implementation/E5_VERIFICATION.md). Run `make seed-diagnostic`
for workflow fixtures and open `/diagnostic`. `make replay-mastery` verifies stored
projections without changing data. Neither command certifies academic quality.

For multiple-choice fixtures, run `make seed-multiple-choice` after migrations.
This creates five independently reviewed synthetic items in Physics / Waves, Light
and Sound. Practice uses checkboxes and exact-set scoring: all correct options and
no others earn full credit. No partial or negative marking is inferred. See
[ADR-026](docs/decisions/ADR/026-multiple-choice.md).

Data requests are at `/privacy`, with administrator intake review at
`/admin/data-requests`. Requesting export/deletion and checking status do not require
learning consent. Intake requires recent sign-in. This local slice records pending
requests. Owners can download bounded JSON exports after recent sign-in; retry copies
expire after 24 hours. Deletion processing remains pending. See
[ADR-028](docs/decisions/ADR/028-owned-data-exports.md).


For a pending DELETE request, its independent administrator claimant can preview
linked record counts and retention requirements at `/admin/data-requests`. The preview
is audited and cannot enable deletion or revoke access. Specific-record holds cover consent, attempts, content flags and data requests. Remaining hold
coverage, erasure execution and anonymization review remain pending. See [ADR-029](docs/decisions/ADR/029-deletion-impact-preview.md).
