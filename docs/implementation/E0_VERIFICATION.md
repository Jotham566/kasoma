# E0 verification and change inventory

Date: 23 September 2026. Baseline: `0ceef70`. Local verification completed before commit and push. The repository owner
subsequently authorized publishing the foundation branch.

## Requirement scope

NFR-MNT-001 and NFR-OBS-001 receive the local foundation. FR-OPS-001/002,
NFR-SEC-001/002, NFR-ACC-001, NFR-COMP-001 and NFR-LOC-001 receive supporting
primitives only. Full SRD acceptance remains in the live traceability register.
No learner feature, production deployment or academic acceptance is claimed.

## Checks

| Command / evidence | Result |
| --- | --- |
| `make setup` (repeated) | Pass; pins and locks honored; existing environment retained |
| Fresh Git-eligible source copy with new environment and new Compose volumes | Setup, lint/types, OpenAPI, build, migrations, seed, Python tests and browser test passed |
| `make services` | PostgreSQL/pgvector, Redis, MinIO and Mailpit healthy |
| `make migrate`, `make seed` | Pass from empty local database; repeated migration/seed idempotent |
| `make lint`, `make typecheck`, `make check-docs` | Pass; Ruff, mypy, ESLint, Prettier, TypeScript, links/61-ID coverage/whitespace |
| `make test` | 21 unit/property/contract tests and 3 integration tests passed |
| `make openapi-check` | No generated OpenAPI/client drift |
| `make build`, `make e2e` | Web production build, keyboard retry and axe scan passed; standalone local start verified |
| `make smoke-dev` | Native web/API/worker startup and live dependency health passed |
| `make containers` | API, worker and standalone web images built |
| `make container-smoke` | Pass: final web/API/worker readiness |
| `make security` | SAST and source boundary checks passed; pip/pnpm audits: no known vulnerabilities |
| `make security-source` | Gitleaks: no source leaks |
| `make security-containers` | Pass: Trivy 0.74.0, both runtime images; strict HIGH/CRITICAL gate, no exclusions |
| `make setup-ollama`, `make ollama-check` and container-to-host probe | Official native 0.34.3 SHA-256 verified; both probes passed; no weights/inference |
| Hosted GitHub Actions | Pending foundation branch push; publication authorized |

Normal tests block network sockets; integration allows loopback only. Browser
requests are restricted to local hosts. Integration includes a real Redis/Celery
worker, local Mailpit delivery, private MinIO bucket, pgvector and isolated
migration/repeated-seed checks. No external model, email, messaging or cloud
service invocation took place. Public package/image/vulnerability metadata
and development-runtime downloads were used for setup and security checks.

## Resolved failures and remaining limits

Resolved: local Make executable lookup; lint/type issues; MinIO Docker Hub access
(use official Quay); occupied port 5432 (use 55432); Turborepo advisories; Celery's
reserved correlation header (use dedicated transport header); transient package
download failures; Debian base CVEs (Alpine); bundled npm CVEs (minimal standalone
web runtime). The scan threshold was not lowered and no CVE was suppressed.

ESLint 9 is development-only and currently needed for the pinned Next React/import
plugins; version 10 fails their API compatibility. Track an upstream upgrade.
Starlette's httpx TestClient deprecation is non-blocking. Real user/content/session/
mastery seeds, outbox retries/dead letters, all four full ModelGateway result
contracts and academic evaluation commands belong to their subsequent domain
slices; their fixture/provider foundations are not those implementations.

Production startup remains explicitly blocked. Legal/privacy/content/benchmark
and Week 8 hosting gates remain outstanding. The Week 5 versus Week 6 short-text
milestone conflict is OPEN-QUESTION E0-01 in the Phase 0 assessment. Named owners,
calendar kickoff, GitHub branch protection and hosted CI evidence remain pending.

## Architectural decisions

ADR-013 records uv, health extensions, catalog-first migration/seeding and minimal
local containers under delegated bootstrap discretion. ADR-001–012 remain intact.
The first delivered vertical slice is web → generated health client → API →
PostgreSQL/Redis with worker correlation. Next: fake OTP → verified identity →
consent/assent enforcement → protected profile; independent content approval follows.

## Files created or changed

This inventory excludes generated build caches, ignored credentials, downloaded
tools and local scan logs. Unchanged original scaffolding is preserved.

- [.dockerignore](../../.dockerignore)
- [.env.example](../../.env.example)
- [.githooks/pre-commit](../../.githooks/pre-commit)
- [.github/workflows/ci.yml](../../.github/workflows/ci.yml)
- [.node-version](../../.node-version)
- [.npmrc](../../.npmrc)
- [.prettierignore](../../.prettierignore)
- [.python-version](../../.python-version)
- [AGENTS.md](../../AGENTS.md)
- [CHANGELOG.md](../../CHANGELOG.md)
- [CONTRIBUTING.md](../../CONTRIBUTING.md)
- [Makefile](../../Makefile)
- [README.md](../../README.md)
- [apps/__init__.py](../../apps/__init__.py)
- [apps/api/__init__.py](../../apps/api/__init__.py)
- [apps/api/alembic.ini](../../apps/api/alembic.ini)
- [apps/api/main.py](../../apps/api/main.py)
- [apps/api/migrations/env.py](../../apps/api/migrations/env.py)
- [apps/api/migrations/versions/0001_curriculum_foundation.py](../../apps/api/migrations/versions/0001_curriculum_foundation.py)
- [apps/web/AGENTS.md](../../apps/web/AGENTS.md)
- [apps/web/CLAUDE.md](../../apps/web/CLAUDE.md)
- [apps/web/app/config.ts](../../apps/web/app/config.ts)
- [apps/web/app/error.tsx](../../apps/web/app/error.tsx)
- [apps/web/app/globals.css](../../apps/web/app/globals.css)
- [apps/web/app/layout.tsx](../../apps/web/app/layout.tsx)
- [apps/web/app/loading.tsx](../../apps/web/app/loading.tsx)
- [apps/web/app/page.tsx](../../apps/web/app/page.tsx)
- [apps/web/next-env.d.ts](../../apps/web/next-env.d.ts)
- [apps/web/next.config.ts](../../apps/web/next.config.ts)
- [apps/web/package.json](../../apps/web/package.json)
- [apps/web/postcss.config.mjs](../../apps/web/postcss.config.mjs)
- [apps/web/tsconfig.json](../../apps/web/tsconfig.json)
- [apps/worker/__init__.py](../../apps/worker/__init__.py)
- [apps/worker/entrypoint.py](../../apps/worker/entrypoint.py)
- [apps/worker/main.py](../../apps/worker/main.py)
- [docker-compose.yml](../../docker-compose.yml)
- [docs/decisions/ADR/013-bootstrap-foundation.md](../../docs/decisions/ADR/013-bootstrap-foundation.md)
- [docs/decisions/ADR/README.md](../../docs/decisions/ADR/README.md)
- [docs/implementation/CURRENT_SPRINT.md](../../docs/implementation/CURRENT_SPRINT.md)
- [docs/implementation/E0_VERIFICATION.md](../../docs/implementation/E0_VERIFICATION.md)
- [docs/implementation/PHASE_0_ASSESSMENT.md](../../docs/implementation/PHASE_0_ASSESSMENT.md)
- [docs/implementation/REQUIREMENTS_TRACEABILITY.md](../../docs/implementation/REQUIREMENTS_TRACEABILITY.md)
- [docs/runbooks/LOCAL_DEVELOPMENT.md](../../docs/runbooks/LOCAL_DEVELOPMENT.md)
- [docs/specifications/13_ADR_and_Decision_Log.md](../../docs/specifications/13_ADR_and_Decision_Log.md)
- [eslint.config.mjs](../../eslint.config.mjs)
- [infra/containers/python.Dockerfile](../../infra/containers/python.Dockerfile)
- [infra/containers/web.Dockerfile](../../infra/containers/web.Dockerfile)
- [package.json](../../package.json)
- [packages/analytics-schema/foundation-event.schema.json](../../packages/analytics-schema/foundation-event.schema.json)
- [packages/api-client/openapi.json](../../packages/api-client/openapi.json)
- [packages/api-client/package.json](../../packages/api-client/package.json)
- [packages/api-client/src/index.ts](../../packages/api-client/src/index.ts)
- [packages/api-client/src/schema.d.ts](../../packages/api-client/src/schema.d.ts)
- [packages/api-client/tsconfig.json](../../packages/api-client/tsconfig.json)
- [packages/config/tsconfig.json](../../packages/config/tsconfig.json)
- [packages/ui/package.json](../../packages/ui/package.json)
- [packages/ui/src/index.tsx](../../packages/ui/src/index.tsx)
- [packages/ui/tsconfig.json](../../packages/ui/tsconfig.json)
- [playwright.config.ts](../../playwright.config.ts)
- [pnpm-lock.yaml](../../pnpm-lock.yaml)
- [pnpm-workspace.yaml](../../pnpm-workspace.yaml)
- [pyproject.toml](../../pyproject.toml)
- [scripts/check_contract.py](../../scripts/check_contract.py)
- [scripts/check_docs.py](../../scripts/check_docs.py)
- [scripts/check_secrets.py](../../scripts/check_secrets.py)
- [scripts/container_smoke.py](../../scripts/container_smoke.py)
- [scripts/dev.py](../../scripts/dev.py)
- [scripts/ollama_check.py](../../scripts/ollama_check.py)
- [scripts/openapi.py](../../scripts/openapi.py)
- [scripts/scan_source.py](../../scripts/scan_source.py)
- [scripts/setup.py](../../scripts/setup.py)
- [scripts/setup_ollama.py](../../scripts/setup_ollama.py)
- [scripts/smoke_dev.py](../../scripts/smoke_dev.py)
- [scripts/start_web.mjs](../../scripts/start_web.mjs)
- [scripts/storage_init.py](../../scripts/storage_init.py)
- [services/__init__.py](../../services/__init__.py)
- [services/config.py](../../services/config.py)
- [services/database.py](../../services/database.py)
- [services/domain/__init__.py](../../services/domain/__init__.py)
- [services/domain/curriculum.py](../../services/domain/curriculum.py)
- [services/health.py](../../services/health.py)
- [services/jobs.py](../../services/jobs.py)
- [services/observability.py](../../services/observability.py)
- [services/providers.py](../../services/providers.py)
- [services/seed.py](../../services/seed.py)
- [tests/conftest.py](../../tests/conftest.py)
- [tests/contract/test_foundation.py](../../tests/contract/test_foundation.py)
- [tests/e2e/health.spec.ts](../../tests/e2e/health.spec.ts)
- [tests/fixtures/seed-scenarios.json](../../tests/fixtures/seed-scenarios.json)
- [tests/integration/test_services.py](../../tests/integration/test_services.py)
- [turbo.json](../../turbo.json)
- [uv.lock](../../uv.lock)
