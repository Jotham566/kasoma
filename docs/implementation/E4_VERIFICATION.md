# E4 numeric grading verification

Date: 23 September 2026. Local synthetic evidence only.
E3 was committed as `22773fd`, fast-forwarded and pushed to main; its branch was
deleted and [hosted CI passed](https://github.com/Jotham566/kasoma/actions/runs/35906564261).
The user authorized committing and pushing this slice on 28 September 2026.

## Pre-commit recheck — 28 September 2026

Lint, formatting, Python/TypeScript types, documentation checks, all 120
unit/contract/property tests and generated-contract checks passed again.
Integration tests and the Docker-based source scan could not run because Docker
Desktop was stopped and startup awaited macOS administrator authentication.
The complete 23 September evidence below remains the last local integration,
browser and container run; hosted CI must independently verify this commit.

## Requirements and implementation

FR-GRD-002 adds deterministic numeric grading with exact rational parsing,
reviewed unit factors/offsets, inclusive absolute/relative tolerances, enabled input
forms and explicit significant figures. FR-GRD-005/007 preserve pinned rules and
structured feedback. FR-CNT-001/004/005 extend authoring, independent review and
immutable content versions; FR-REV-003 adds the numeric learner input. Supporting
NFR-SEC-002, NFR-ACC-001 and NFR-MNT-001 retain safe DTOs, keyboard/accessibility
checks and generated typed contracts. This does not complete every criterion in
these broader requirements.

Migration 0005 preserves choice attempts and grades, adds bounded numeric responses
and requires exactly one representation matching the assigned item. No model calls,
real data, cloud providers or production delivery adapters were used.

## Files

- Numeric contracts and grading: `services/numeric.py`, `services/grading.py`,
  `services/content_contracts.py`, `services/content.py`,
  `services/assessment_contracts.py`, `services/assessment.py`,
  `services/domain/assessment.py`, `apps/api/migrations/versions/0005_numeric.py`.
- Web: `apps/web/app/admin/content/{editor.tsx,numeric-fields.tsx,page.tsx}` and
  `apps/web/app/revise/page.tsx`.
- Generated contracts: `packages/api-client/openapi.json`,
  `packages/api-client/src/schema.d.ts`.
- Tests: `tests/contract/test_numeric.py`,
  `tests/integration/test_numeric_workflow.py`, `tests/integration/conftest.py`,
  `tests/e2e/numeric.spec.ts`.
- Local tooling: `Makefile`, `scripts/assessment_fixtures.py`,
  `scripts/e2e_api.py`, `playwright.config.ts`, `scripts/container_smoke.py`.
- Documentation: `AGENTS.md`, `README.md`, `CHANGELOG.md`, ADR-017/018 and ADR index,
  decision log, adaptive engine specification, implementation backlog, current
  sprint, traceability, Phase 0 assessment, E3 verification, this report and local
  development runbook.

## Executed checks

| Commands | Result |
| --- | --- |
| `make setup services migrate seed seed-numeric` | Passed with pinned runtimes, migration 0005 and synthetic fixtures; repeated numeric seed is safe. |
| `make format lint typecheck` | Passed Python/TypeScript lint, formatting, type checks, documentation links and whitespace. |
| `make openapi openapi-check build` | Generated contracts current; production web build passed. |
| `make test` | 120 unit/contract/property tests and 38 integration tests passed. Includes clean migrations and populated 0004→0005 upgrade with preserved choice evidence. |
| `make e2e` | All 9 browser tests passed, including numeric author/reviewer/learner flow, malformed input, precision, units, resume, keyboard submission and axe checks. |
| `make security security-source` | Bandit, secret checks, Python/JS dependency audits and source scan passed. |
| `make containers security-containers container-smoke` | Container build, HIGH/CRITICAL vulnerability gates and API/database/Redis/worker/web smoke passed. Previously running application services preserved. |

Failures caught and fixed: duplicate pytest module names; JSON `null` incorrectly
used instead of SQL NULL for legacy choice responses; browser servers colliding
with an existing local stack; exact label selector including select option text.
All affected checks passed on rerun. The existing Starlette/httpx test-client
deprecation warning remains; it does not fail the pinned test stack. Browser servers now bind dedicated loopback
ports 13000/18000. No Gemini or interactive inference evaluation was run.

## Decisions and remaining gates

[ADR-017](../decisions/ADR/017-readiness-resolutions.md) resolves the content/engine
difficulty-label mismatch with a versioned mapping for E5 and preserves the stricter
Week 5 short-text benchmark gate by advancing its first implementation.
[ADR-018](../decisions/ADR/018-numeric-grading.md) records numeric semantics,
compatibility, bounds, security and forward-fix constraints. Neither changes
approved engine weights or authorizes academic/production use.

Academic benchmark approval, exact curriculum mappings, rights evidence, named
owners, privacy approvals and production provider decisions remain external gates.
Numeric software tests do not certify the teacher-agreement target. Multiple choice,
short text, diagnostic/mastery, hints and other MVP slices remain pending.

Next: a resumable diagnostic with 10–15 approved items, coverage constraints, no
hints/solutions, versioned difficulty mapping and immutable initial mastery evidence.
See [current sprint](CURRENT_SPRINT.md) and [traceability](REQUIREMENTS_TRACEABILITY.md).

### Main CI artifact repair — 28 September 2026

E4 committed and pushed as `7d2c8ed`. Hosted run 36391189987 failed before tests
because the pinned MinIO image returned unauthorized. Docker startup was subsequently
completed locally. All 38 existing integration tests and the source scan passed
again. ADR-019 retains MinIO but builds official immutable, archive-checksummed
release source. The source build, Compose readiness and private bucket setup passed.
This fixes clean CI setup without registry credentials or a new storage provider.
