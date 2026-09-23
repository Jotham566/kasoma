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
