# Kasoma Repository Bootstrap and Environment Contract

| Field | Value |
|---|---|
| Version | 1.3.0 |
| Purpose | Make the first coding session reproducible and bounded |

## 1. Required local tooling

- Node.js current LTS pinned in repository;
- pnpm pinned through Corepack;
- Python 3.12 pinned;
- Python dependency/virtual-environment tool selected and locked in ADR or initial bootstrap;
- Docker and Compose for PostgreSQL/Redis/local object-storage substitute;
- Makefile or task runner exposing stable developer commands.

No global tool version should be assumed silently. Pin versions and commit lockfiles.

## 2. Standard commands

The repository shall provide equivalents of:

```text
make setup          # install dependencies and hooks
make dev            # start web, API, worker and dependencies
make test           # required unit/integration suite
make lint           # formatting/lint/type checks
make migrate        # apply local migrations
make seed           # synthetic development fixtures
make openapi        # generate/check OpenAPI and TS client
make e2e            # critical browser journeys
make security       # local security/secret/dependency checks
```

Commands must fail clearly when prerequisites or configuration are missing.

## 3. Environment variables

Use `.env.example` with safe placeholders. Required categories:

```text
APP_ENV
APP_PUBLIC_URL
API_PUBLIC_URL
DATABASE_URL
REDIS_URL
OBJECT_STORAGE_ENDPOINT
OBJECT_STORAGE_CONTAINER
OBJECT_STORAGE_ACCESS_KEY
OBJECT_STORAGE_SECRET_KEY
JWT_SIGNING_KEY / managed key reference
TOKEN_ISSUER
OTP_PROVIDER
OTP_EMAIL_PROVIDER
OTP_SMS_PROVIDER=africas_talking
OTP_SMS_MONTHLY_BUDGET
OTP_EMAIL_FROM
OTP_SMS_SENDER
AI_PROVIDER
AI_ENDPOINT
AI_API_KEY
AI_GRADING_MODEL
AI_EMBEDDING_MODEL
WHATSAPP_APP_SECRET
WHATSAPP_ACCESS_TOKEN
WHATSAPP_PHONE_NUMBER_ID
WHATSAPP_VERIFY_TOKEN
CLOUD_PROVIDER=<selected-by-week-8-adr>
CLOUD_PRIMARY_REGION=<selected-by-week-8-adr>
CLOUD_RECOVERY_REGION=<selected-by-week-8-adr>
OTEL_EXPORTER_OTLP_ENDPOINT
ERROR_REPORTING_DSN
```

Exact names may be refined before code depends on them. Secrets never receive defaults and never enter client-side `NEXT_PUBLIC_*` variables.

## 4. Configuration model

- Validate configuration at process startup using typed settings.
- Separate environment secrets from versioned product configuration.
- Version mastery weights, confidence thresholds, content coverage and prompt templates in database/config artifacts.
- Fail closed in production when signatures, token keys or consent configuration are absent.
- Development-only insecure adapters must refuse to start when `APP_ENV=production`.

## 5. Local services

Compose should provide:

- PostgreSQL with pgvector extension available;
- Redis;
- object-storage substitute if needed;
- host-native Ollama on the 16 GB M4 Mac Mini (preferred over running Ollama inside Docker on macOS), or an optional vLLM shared endpoint;
- optional mail/SMS capture adapter;
- API and worker health dependencies.

AI, OTP and WhatsApp interfaces require deterministic fake adapters for automated tests. Tests must not call paid/external providers.

Default local values:

```text
MODEL_PROVIDER=fake              # automated tests
MODEL_PROVIDER=local             # interactive developer profile
MODEL_API_STYLE=openai_compatible
MODEL_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL_ALIAS=local-quality
GEMINI_EVAL_MODEL=<versioned-model-alias>
GEMINI_API_KEY=<secret-no-default>
ALLOW_GOOGLE_FREE_TIER_EVAL=false
GEMINI_EVAL_MAX_REQUESTS=100
GEMINI_EVAL_MAX_INPUT_TOKENS=<explicit-ceiling>
OBJECT_STORAGE_PROVIDER=minio
EMAIL_PROVIDER=mailpit
SMS_PROVIDER=fake
WHATSAPP_PROVIDER=fake
ALLOW_EXTERNAL_API_CALLS=false
```

The application must refuse to start an `external-eval` or `production` provider while `ALLOW_EXTERNAL_API_CALLS=false`.

Run Ollama directly on macOS so it can use Apple acceleration. Dockerized API/worker processes connect to `http://host.docker.internal:11434/v1`; host processes use `http://localhost:11434/v1`. `ALLOW_GOOGLE_FREE_TIER_EVAL=true` enables only the named evaluation command and does not relax `ALLOW_EXTERNAL_API_CALLS` for any other service.

## 6. Seed data

`make seed` creates:

- S4, Mathematics and Physics;
- synthetic topic/concept/competency graph;
- users for learner, author, reviewer and admin roles;
- original synthetic items for each supported response type/status;
- example diagnostic/revision session;
- mastery trajectories for UI states.

Seeds must be deterministic, safe to reset locally and clearly non-production.

## 7. CI stages

1. dependency install/cache;
2. lint/format/type checks;
3. unit/property tests;
4. database migration from empty and previous release snapshot;
5. integration/contract tests;
6. OpenAPI generation diff;
7. web build and component accessibility checks;
8. security/secret/dependency scan;
9. container build;
10. staging deploy/E2E on protected branches.

Ordinary CI ends before any external-model call. `gemini-free-eval` is a manual developer workflow with a sanitizer, request/token ceilings and no CI requirement. A separate manually triggered `external-eval` workflow may use short-lived secrets and a hard budget/request ceiling.

## 8. Initial repository acceptance

Bootstrap is done only when:

- a new developer can set up from README without tribal knowledge;
- health endpoint reports API/database/Redis dependency state safely;
- web consumes generated API client;
- one migration applies cleanly;
- tests run without external provider credentials;
- correlation ID appears across web request, API log and worker test;
- CI passes from a clean clone;
- no real academic or personal data is present.
