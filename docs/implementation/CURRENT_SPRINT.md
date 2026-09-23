# Current Sprint

## E0 — repository bootstrap and engineering foundation

Phase 0 complete. E0 local foundation implemented and verified. Hosted CI awaits
the foundation branch push; no full learner/MVP acceptance is claimed.
No calendar kickoff date or named delivery owners have been supplied. The horizon
remains 12 weeks; see [Phase 0 assessment](PHASE_0_ASSESSMENT.md) for the requirement
mapping, dependency chain, risks and first slice.

## Implemented

- Approved pnpm/Turborepo monorepo; Python 3.12.14/uv 0.12.18 and Node 24.21.0/
  Corepack 0.34.0/pnpm 10.30.2; committed lockfiles.
- Next.js 16.3.6 shell consuming generated OpenAPI client, FastAPI and Celery 5.6.3.
- PostgreSQL 16/pgvector, Redis, MinIO (official Quay distribution), Mailpit.
- Typed local-only settings, generated ignored secrets, explicit production denial.
- Alembic migration 0001, deterministic S4/two-subject/six-topic catalog seed,
  versioned synthetic scenario fixture inventory and private local storage bucket.
- Correlation IDs, safe structured logs and local OpenTelemetry console traces.
- Fake model/messaging and queue contracts, local email/storage adapters, native
  Ollama connectivity probe; no inference or external communication performed.
- Make commands, local pre-commit hook, initial GitHub Actions CI, SAST/dependency/
  secret/container scan commands, browser accessibility test and local runbook.
- [ADR-013](../decisions/ADR/013-bootstrap-foundation.md) records delegated choices;
  existing ADRs are linked and unchanged in substance.

## Verification evidence — 23 September 2026

- `make setup`: passed and rerun idempotently, preserving .env.
- `make services`: all four infrastructure services healthy.
- `make migrate`: initial empty local database upgrade passed.
- `make seed`: catalog and private bucket passed; repeated catalog seed unchanged.
- `make lint`, `make typecheck`: Python/TypeScript, Ruff/Prettier and docs passed.
- `make test`: 21 unit/property/contract cases and 3 integration cases passed.
  Integration covers isolated migration/repeated upgrade and seed, Redis readiness,
  local Mailpit/MinIO, and a real Celery worker preserving the request correlation.
- `make openapi-check`: generated schema/client matched.
- `make build`: production web build passed.
- `make e2e`: Chromium shell, keyboard retry and axe accessibility passed.
- `make security`: Bandit, local source boundary checks, pip and pnpm audits passed;
  final dependency audit reported no known vulnerabilities.
- `make security-source`: Gitleaks scanned Git-eligible source, no leaks.
- `make containers`, `make container-smoke`: final Alpine API/worker and standalone
  web images built and passed dependency/worker/web readiness.
- `make security-containers`: Trivy 0.74.0 passed strict HIGH/CRITICAL scans for both
  runtime images, without ignores or lowered severity.
- `make setup-ollama`, `make ollama-check`: official native 0.34.3 archive SHA-256
  verified; host and container-to-host probes passed, no model weights or inference.
- `make smoke-dev`: prescribed native development command passed.
- Fresh source/environment/volumes: setup, lint/types, OpenAPI, build, migration,
  seed, 24 Python tests and browser accessibility test passed. This was an isolated
  source copy of uncommitted work, not a hosted GitHub Actions claim.
- Hosted GitHub Actions is pending the foundation branch push; commit and push
  were subsequently authorized by the repository owner.

Initial failures were fixed: Make's local-tool resolution, format/type findings,
MinIO Docker Hub distribution, occupied PostgreSQL port (use 55432), Turborepo audit
findings, and Celery's reserved correlation header. First integration run preceded
healthy infrastructure; rerun passed. Starlette emits a test-client deprecation
warning; socket-guard warnings in tests are expected assertions of blocked calls.

## Boundaries and next slice

This is not application or pilot acceptance. Full user/content/session/mastery
seeding awaits those domain schemas; current scenarios are non-publishable fixtures.
Outbox/retry/dead-letter behaviour begins with persisted domain events, not the
smoke task. No learner feature or real-data use is enabled.

After all E0 checks pass, next slice: verified identity with fake OTP delivery,
server-enforced consent/assent state and protected `/me` (FR-ID-001–004,
NFR-SEC-002), followed by independent content approval. Do not start it in this
bootstrap change.

OPEN-QUESTION E0-01 remains: Week 5 short-text benchmark gate versus Week 6
implementation in the backlog. Resolve before the affected slice; do not weaken
the gate. Production provider, legal/privacy, academic and pilot approvals remain
mandatory future evidence. CI branch protection, reviewer ownership and staging
deployment require repository/Week 8 configuration, not a local claim of success.

The complete command evidence, fixed failures and file inventory are in
[E0 verification](E0_VERIFICATION.md). Runtime app processes and the temporary
Ollama server were stopped after verification; local infrastructure remains
available. The isolated verification stack is stopped and its synthetic volumes
are retained. No existing host database or unrelated service was changed.
