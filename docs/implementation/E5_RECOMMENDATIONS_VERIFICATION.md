# E5 recommended practice verification

Date: 28 September 2026. Synthetic local development only.

The preceding diagnostic/mastery work is committed and pushed to main as `b26ab75`.
[Hosted CI passed](https://github.com/Jotham566/kasoma/actions/runs/36396016478).
Its completed branch was deleted. The owner subsequently authorized committing and
pushing this verified slice to main and removing its completed branch. The final
pre-commit lint, types, generated-contract and source-secret checks passed again.

## Requirements and implementation

FR-MST-006 and FR-REV-001/006: versioned multiplication of gap, academic importance,
uncertainty, spacing, prerequisite readiness, recent repetition and availability;
deterministic tie breaks; confident prerequisite redirection; 5–10-item skill plans;
learner reasons and a home card with estimated duration. Sparse evidence offers a
diagnostic without asserting weakness. Each assignment records its selection reason.

Supporting FR-ID-003, FR-REV-003/004/005, FR-OPS-001, NFR-SEC-002, NFR-ACC-001 and
NFR-MNT-001: current consent/subject authorization, content revalidation, durable
idempotency/resume, atomic session.started events, safe generated API projection,
keyboard and accessibility coverage. Manual selection now shares active-reservation
exclusion. Recommended plans also avoid occupied manual topics.

[ADR-021](../decisions/ADR/021-recommended-practice.md) documents delegated synthetic
ranking defaults, safe previews and persisted replay inputs. Migration 0008 adds an
immutable snapshot store and frozen session snapshot without rewriting old evidence.
Read-only replay checks stored inputs against both preview and session results.

## Verification

All applicable local checks passed on the final implementation:

| Command | Result |
| --- | --- |
| `make setup migrate seed seed-diagnostic` | Passed; migration 0008 applied additively and synthetic fixtures remained idempotent. |
| `make format lint` | Passed formatting, Python/TypeScript lint/types, documentation and whitespace checks. |
| `make test` | 163 unit/contract/property tests and 54 integration tests passed (217 total). Integration exercises clean-schema and upgrade migrations. |
| `make openapi openapi-check build` | Generated contracts match and production web build passed. |
| `make e2e` | All 11 browser tests passed, including recommendation reason/time, sparse diagnostic link, lost start acknowledgement, retry, saved-answer resume, keyboard and axe checks. |
| `make replay-recommendations` | Read-only command passed with zero snapshots in the default local database; integration replays nonempty preview and committed snapshots. |
| `make security security-source` | Bandit, secret-boundary/Gitleaks, Python and JavaScript dependency audits passed. |
| `make containers security-containers container-smoke` | Final images built; HIGH/CRITICAL vulnerability gates and API/database/Redis/worker/web smoke passed. |

The new tests cover ranking direction for all factors, prerequisite thresholds and
transitive redirection, unavailable prerequisites, cycle rejection, stable replay,
neutral unknown prerequisites, factor bounds, item mapping/diversity/exposure,
5/10-item plans, preview deduplication, immutable records, concurrent start, consent,
subject authorization, invalid client input, withdrawn inventory, active reservations,
manual/adaptive coexistence and expired manual-slot recovery. Existing diagnostics,
choice/numeric grading, content and identity suites remain green.

Failures corrected during verification: Python formatting/type errors; an incorrectly
isolated factor-test fixture; generated identity-client error narrowing and React lint;
missing subject-query forwarding in the web proxy; a test retirement request missing
its required idempotency header. Review also found and fixed active/expired manual
session uniqueness conflicts. No checks were disabled or acceptance gates relaxed.
Only the existing non-failing Starlette/httpx and deliberate socket-block warnings
remain. No unresolved implementation-check failure remains.

Local logs are ignored development artifacts: `.local/recommendations-expiry-verification.log`,
`.local/recommendations-final-verification.log`, `.local/recommendations-expiry-containers.log`,
`.local/recommendations-browser-recheck.log` and `.local/recommendations-final-docs.log`.

## Files

- Domain/API: `services/recommendation_engine.py`, `services/recommendations.py`,
  `services/assessment.py`, `services/assessment_contracts.py`,
  `services/domain/assessment.py`, `apps/api/assessment.py`, migration 0008.
- Web/contracts: `apps/web/app/recommendation-card.tsx`, `apps/web/app/page.tsx`,
  the web API proxy, generated `packages/api-client/openapi.json` and `src/schema.d.ts`.
- Tests: `tests/contract/test_recommendation_engine.py`,
  `tests/integration/test_recommendations.py`, `tests/e2e/recommendations.spec.ts`,
  `tests/e2e/health.spec.ts` (scope the readiness assertion with the second status region).
- Tooling/docs: `scripts/replay_recommendations.py`, `Makefile`, `AGENTS.md`, `README.md`,
  `CHANGELOG.md`, ADR-021/indexes, current sprint, traceability, local runbook and this report.

## Limits and next task

No real learner data, model inference, Gemini evaluation, production provider,
calibration change or mature-product feature was introduced. Neutral importance and
seven-day review timing are explicit synthetic configuration, not academic judgment.
Reviewed curriculum graph/importance administration, richer reviewed scenario metadata,
teacher sanity review and mastery calibration remain release prerequisites. Prompt
hash is only the current text-fixture scenario proxy. Preview may change before start;
the committed session reason and snapshot are authoritative.

Hints, unseen reassessment, general progress/history, short-text benchmark/guardrails,
WhatsApp and operations remain further MVP work. Next: reviewed revision hints and
independence evidence (FR-GRD-006), then unseen reassessment (FR-GRD-008). Keep the
Week 5 short-text benchmark and Week 8 provider gates intact.
