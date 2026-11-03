# E1 identity and consent verification

## Workspace reconciliation — 3 November 2026

Reconcile the local onboarding correction from snapshot `46a0f8a` onto upstream
`1afed82` on `reconcile/local-onboarding`. Preserve upstream OTP observation,
identity coordination, signed-out reverification visibility and browser assertions.
Regenerate contracts from the current API rather than restoring older generated
files. The original workspace is retained in a named local Git stash; ignored
environment and runtime files remain local. No database migration or ADR is added.

The earlier Windows verification below describes the original local correction,
not acceptance of this combined source. Current combined-source checks:

- Ten focused auth-options/identity contract cases pass. Windows' event loop needs
  the repository's loopback allowlist (`--allow-hosts=localhost,127.0.0.1,::1`);
  the first default socket-disabled invocation failed before API execution.
- Focused Ruff lint/format, ESLint for onboarding/gateway and browser tests,
  Linux-target Python type checks, all three workspace
  TypeScript checks, production Next.js build, focused Prettier, repeated
  OpenAPI/client generation, local
  secret boundaries and Git whitespace checks pass.
- Documentation checks pass for 211 Markdown files and all 61 requirements using
  Python UTF-8 mode. The Make-based contract wrapper cannot run without Windows
  `make`; repeated direct generation confirms identical contract bytes.
- Docker's Linux engine is unavailable. Database integration and real-API browser
  acceptance were not rerun; historical walkthroughs do not establish combined-source
  acceptance. The Windows-default mypy target also reports the unchanged upstream
  Unix-only `os.getuid` call; the supported Linux target passes.

## Local onboarding correction — 18 October 2026

FR-ID-001–005 / NFR-ACC-001: clarify shared registration/sign-in and make local
delivery guidance reflect backend configuration. Add a minimized public auth-options
contract and allowlisted gateway route, explicit email entry/Mailpit access, setup
steps, visible Senior 4 level, resend cooldown, verification errors and missing-subject
guidance. Guardian and identifier-link forms use the same local email instructions.
ADR-014's verification, session, enumeration and age/consent controls remain in place.

Validation on the Windows development machine:

- Ten focused Python contract cases pass (delivery configuration and identity
  contracts); seven PostgreSQL identity integration cases pass in isolated schemas.
- Six focused Chromium browser cases pass across the identity and learner-home
  suites, covering delivery guidance, invalid phone/email entry, incorrect-code
  recovery, adult profile/consent/withdrawal/logout, distinct guardian consent and
  assent, offline retry, CSRF, axe, and navigation/reflow at 320/1280 pixels.
  Five passed on the first focused run; the adult case passed after correcting its
  alert locator to exclude Next's empty announcement element.
- The shared all-feature browser fixture bootstrap exceeded its normal startup
  timeout on this machine. The focused run used an ignored local launcher with
  an independent schema, the same migrations/API/identity service and deterministic
  fake messaging, plus only the base catalog. No developer schemas were reset.
- Live collaborative-browser walkthrough against normal Mailpit delivery verifies
  new account creation, code capture, profile saving, adult consent, logout,
  incorrect-code feedback and returning sign-in with saved profile/consent.
  The refreshed development stylesheet also passes a 320-pixel reflow check.
- Production Next build, TypeScript checks, focused ESLint, Ruff and mypy checks
  pass. OpenAPI/client generation and drift checks pass. Documentation links and
  whitespace were checked directly because this workspace has no Git metadata;
  Git-based repository checks cannot run here.

No database migration or new architecture decision is required. Local SMS remains
an inaccessible in-memory test adapter, and the web form directs users to email.
No real SMS/provider delivery, production acceptance, or new personal-data fields
are claimed. Next acceptance remains the existing academic/provider release gates.

Date: 23 September 2026. Branch: `codex/e1-identity-consent`.
Foundation `4faf65a` passed [hosted CI](https://github.com/Jotham566/kasoma/actions/runs/35889650630),
was fast-forwarded to main and pushed, and its branch was deleted locally/remotely.
E1 was subsequently committed as `9dfe726`, fast-forwarded to main and pushed
at the owner's request. [Hosted CI passed](https://github.com/Jotham566/kasoma/actions/runs/35896298632).

## Scope and evidence

FR-ID-001–005 and supporting security, accessibility, typed-contract and registration
analytics requirements. Local synthetic delivery only. FR-ID-006 remains E8.
See [traceability](REQUIREMENTS_TRACEABILITY.md) and [ADR-014](../decisions/ADR/014-identity-consent.md).

- API tests: encrypted identifiers, generic OTP requests, five-attempt limit,
  ten-minute expiry, single-use concurrent verification, per-device/peer throttles,
  contact linking and collision rejection, profile selection, adult birthday boundary,
  minor guardian binding and separate assent, policy changes, withdrawal, idempotency,
  re-authentication, session expiry, refresh reuse and revocation, ownership and log safety.
- Migration tests create independent schemas, apply 0001, seed, apply 0002 twice,
  and exercise the actual PostgreSQL constraints. No developer tables are truncated.
- Four browser tests passed: shell, adult onboarding/withdrawal/logout, minor guardian
  consent plus assent, cross-origin rejection and interrupted-request retry. Browser
  checks also cover HttpOnly/SameSite cookies, no token JSON/browser storage, and axe.
- Setup, migration, seed, formatting, type checks, OpenAPI generation/drift and build
  passed. Final expanded evidence is recorded below.

## Failures found and corrected

- A test encryption-key fixture had the wrong decoded length; fixed the fixture.
- Alembic could discover the public version table through search_path and skip fresh
  schema migrations. It now pins its version table to current_schema().
- Initial CSRF origin comparison used Next's internal hostname; compare the browser
  origin to the actual request host and restrict local hostnames instead.
- Cryptography 48.0.1 failed vulnerability audit; upgraded the resolved dependency
  to patched 50.0.1. No advisory suppression added.
- Replaced an assert in authorization code with an explicit runtime failure.
- Secret scanning identified a deterministic encoded test key; the fixture now
  visibly derives its key from a synthetic test string, without scanner exclusions.
  Scanner diagnostics now retain redaction while showing finding locations.
- Renamed a contract test module to avoid pytest's same-basename import collision.

## Remaining limits

The synthetic notice is not legally approved wording. Contact OTP proves possession,
not legal guardianship or age. Pilot procedures and legal review remain mandatory.
No real SES/SMS integration, staff authorization/MFA, export/deletion processing,
production key rotation, retention scheduler or analytics dispatcher is delivered.
Future learning/WhatsApp endpoints must use the tested consent guard. No assessment
is claimed complete merely because the profile reports its consent readiness.

The Week 5/6 short-text benchmark sequence conflict remains outside this slice.
The next slice is content roles, independent review and publication constraints.

## Final command results

| Command | Result |
|---|---|
| `make setup` | Passed; existing local keys preserved, missing keys generated without output |
| `make migrate seed` | Passed; additive 0002 and repeatable catalog/storage seed |
| `make format lint` | Passed; Ruff, mypy, ESLint, Prettier, TypeScript and docs |
| `make test` | 39 passed: 29 unit/property/contract and 10 integration |
| `make openapi openapi-check` | Generated schema and TypeScript agree |
| `make build e2e` | Production web build and all four browser tests passed |
| `make security` | Bandit, boundary checks, pip and pnpm audits passed; no known vulnerabilities |
| `make security-source` | Gitleaks passed; no leaks, no suppressions |
| `make containers` | API, worker and web built |
| `make security-containers` | API/web scans passed with zero HIGH/CRITICAL findings; worker uses same Python image |
| `make container-smoke` | API, dependencies, worker and web healthy; app containers stopped afterward |

[Main CI](https://github.com/Jotham566/kasoma/actions/runs/35890229157) also passed
after the foundation merge. E1 was subsequently committed and pushed; its hosted CI also passed. The Starlette TestClient deprecation warning and intentional blocked-socket
warnings remain non-failing toolchain notices.

No external model, SMS, email or cloud service was called. Dependency downloads and
public vulnerability metadata checks were used. No real learner data was used.
Infrastructure remains running locally; isolated synthetic test schemas are retained
for debugging. No user database was truncated or reset.

## Files changed

- [.env.example](../../.env.example)
- [AGENTS.md](../../AGENTS.md)
- [CHANGELOG.md](../../CHANGELOG.md)
- [README.md](../../README.md)
- [apps/api/identity.py](../../apps/api/identity.py)
- [apps/api/main.py](../../apps/api/main.py)
- [apps/api/migrations/env.py](../../apps/api/migrations/env.py)
- [apps/api/migrations/versions/0002_identity.py](../../apps/api/migrations/versions/0002_identity.py)
- [apps/web/app/api/v1/[...path]/route.ts](../../apps/web/app/api/v1/[...path]/route.ts)
- [apps/web/app/development-notice/page.tsx](../../apps/web/app/development-notice/page.tsx)
- [apps/web/app/onboarding/page.tsx](../../apps/web/app/onboarding/page.tsx)
- [apps/web/app/page.tsx](../../apps/web/app/page.tsx)
- [docs/decisions/ADR/014-identity-consent.md](../../docs/decisions/ADR/014-identity-consent.md)
- [docs/decisions/ADR/README.md](../../docs/decisions/ADR/README.md)
- [docs/implementation/CURRENT_SPRINT.md](../../docs/implementation/CURRENT_SPRINT.md)
- [docs/implementation/E0_VERIFICATION.md](../../docs/implementation/E0_VERIFICATION.md)
- [docs/implementation/E1_VERIFICATION.md](../../docs/implementation/E1_VERIFICATION.md)
- [docs/implementation/REQUIREMENTS_TRACEABILITY.md](../../docs/implementation/REQUIREMENTS_TRACEABILITY.md)
- [docs/runbooks/LOCAL_DEVELOPMENT.md](../../docs/runbooks/LOCAL_DEVELOPMENT.md)
- [docs/specifications/13_ADR_and_Decision_Log.md](../../docs/specifications/13_ADR_and_Decision_Log.md)
- [packages/analytics-schema/identity-event.schema.json](../../packages/analytics-schema/identity-event.schema.json)
- [packages/api-client/openapi.json](../../packages/api-client/openapi.json)
- [packages/api-client/src/index.ts](../../packages/api-client/src/index.ts)
- [packages/api-client/src/schema.d.ts](../../packages/api-client/src/schema.d.ts)
- [playwright.config.ts](../../playwright.config.ts)
- [pyproject.toml](../../pyproject.toml)
- [scripts/e2e_api.py](../../scripts/e2e_api.py)
- [scripts/scan_source.py](../../scripts/scan_source.py)
- [scripts/setup.py](../../scripts/setup.py)
- [services/config.py](../../services/config.py)
- [services/domain/identity.py](../../services/domain/identity.py)
- [services/identity.py](../../services/identity.py)
- [services/identity_contracts.py](../../services/identity_contracts.py)
- [tests/conftest.py](../../tests/conftest.py)
- [tests/contract/test_identity_contract.py](../../tests/contract/test_identity_contract.py)
- [tests/e2e/identity.spec.ts](../../tests/e2e/identity.spec.ts)
- [tests/integration/test_identity.py](../../tests/integration/test_identity.py)
- [uv.lock](../../uv.lock)
