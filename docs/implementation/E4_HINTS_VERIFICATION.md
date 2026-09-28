# E4 reviewed hints verification

Date: 28 September 2026. Synthetic local development only.

Recommended practice was committed and pushed to main as `88dd880`.
[Hosted CI passed](https://github.com/Jotham566/kasoma/actions/runs/36398742634);
the completed recommendation branch was removed. This next slice is on the active
local `codex/e4-reviewed-hints` branch at verification. It was subsequently committed
and pushed to main as `3c0c3ba`; that completed branch was removed.

## Requirements and decision

FR-GRD-006: independently reviewed progressive revision hints, append-only disclosure,
exact retry/resume, frozen count/highest level and independence weighting. Supporting
FR-GRD-007, FR-MST-001/003, FR-CNT-001/004, FR-ID-003, FR-OPS-001, NFR-SEC-002,
NFR-ACC-001 and NFR-MNT-001: solution gating, immutable/replayable evidence, consent,
authorization, safe outbox counters, generated contracts and accessible browser flows.

[ADR-022](../decisions/ADR/022-reviewed-hints.md) preserves immutable submitted attempts:
pre-answer disclosure uses the session assignment, post-answer remediation uses the
attempt, and only pre-answer usage changes independence weight. Points remain unchanged.
Reviewed documents contain at most three hints. Diagnostics never expose hints.
Migration 0009 adds usage/receipt linkage and integrity guards. Old published documents
are unchanged, and absent legacy highest-level metadata retains its original hash.

## Verification

All applicable local checks passed on the final implementation.

| Command | Result |
| --- | --- |
| `make setup migrate seed seed-hints` | Passed with pinned tools and preserved local environment; additive 0009 and synthetic reviewed hint fixtures applied. |
| `make format lint` | Passed Python/TypeScript lint/types, formatting, documentation links and whitespace checks. |
| `make test` | 174 unit/contract/property tests and 61 integration tests passed (235 total). |
| `make openapi openapi-check build` | Generated API/client match and production web build passed. |
| `make e2e` | All 12 browser tests passed, including authored/reviewed hints, lost-response retry, pre/post-answer resume, keyboard and axe. |
| `make replay-mastery replay-recommendations` | Passed read-only with zero projections/snapshots in default local DB; integration exercises nonempty replay including hinted and legacy evidence. |
| `make security security-source` | Bandit, secret-boundary/Gitleaks and Python/JavaScript dependency audits passed. |
| `make containers security-containers container-smoke` | Images built; HIGH/CRITICAL vulnerability gates and API/database/Redis/worker/web smoke passed. |

Tests cover content bounds, client metadata rejection, unchanged correctness/points,
independence calculation, legacy hashes, choice/numeric submission, exact hint retries,
concurrent disclosure/answer and duplicate delivery, rollback, ownership/consent,
unserved/future items, retirement, diagnostic denial, SQL history/count guards and
post-answer immutability. Integration fixtures run migrations from a clean isolated
schema through head and repeat the upgrade without discarding previous evidence.

Failures corrected during development: duplicate pytest module naming, lint/typing,
a SQL count-guard subquery returning multiple columns, a retired-content assertion
expecting 409 instead of the existing 404 contract, and a browser pagination race.
Pagination tests now await the loaded state before requesting another page.
No unresolved check failure remains. No check was disabled or acceptance gate relaxed. Existing non-failing warnings include
Starlette/httpx deprecation, deliberate socket blocking, pnpm's ignored dependency
build script and Trivy's Alpine EOL-list warning. No production or academic acceptance
is claimed.

Ignored local logs: `.local/hints-final-regression.log`, `.local/hints-browser.log`,
`.local/hints-contract.log`, `.local/hints-foundation.log`, `.local/hints-containers.log`
and `.local/hints-final-docs.log`.

## Change inventory

- API/domain: `services/hints.py`, `services/assessment.py`, assessment/content contracts,
  `services/domain/assessment.py`, `services/mastery.py`, `services/mastery_engine.py`,
  `apps/api/assessment.py`, migration `0009_reviewed_hints.py`.
- Web: staff content editor/review page, revision page and new `revise/hints.tsx`, API proxy.
- Contracts: generated `packages/api-client/openapi.json` and `src/schema.d.ts`,
  `packages/analytics-schema/assessment-event.schema.json`.
- Tests: new contract/integration/browser hint suites, assessment contract assertions,
  staff content review assertions and numeric/content browser pagination synchronization.
- Fixtures/tooling: `Makefile` (`seed-hints`), `scripts/assessment_fixtures.py`,
  `scripts/e2e_api.py` (independently reviewed synthetic hint inventory).
- Documentation: `AGENTS.md`, `README.md`, `CHANGELOG.md`, current sprint, traceability,
  local runbook, data/API/content specifications, ADR-022 and indexes, prior recommendation
  verification and this report.

## Limits and next task

Synthetic tests do not certify hint quality or academic calibration. Production hints
still require the existing independent academic and rights review. No real learner data,
model inference, external messaging, Gemini evaluation, cloud provider or mature-product
scope was introduced. Dependency vulnerability checks access package advisories only.
No production deployment is enabled. The next slice is FR-GRD-008 unseen equivalent
reassessment, preserving the original grade and recording new independent evidence.
Week 5 benchmark and Week 8 provider decisions remain release prerequisites.

Hosted CI for main `3c0c3ba`: [passed](https://github.com/Jotham566/kasoma/actions/runs/36401623871).
