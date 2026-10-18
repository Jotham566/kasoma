# Current sprint: grading operations and acceptance

Updated 18 October 2026. This file supersedes the preserved
[historical checkpoints](SPRINT_HISTORY_2026_10_18.md).

## Verified main

Main/origin main is `17abb2d`. All merged source branches are removed locally/remotely.
Only the active unmerged `codex/grading-operations` branch remains.

- `2164209`: independent blinded expert review, versioned released-session sampling,
  immutable exact rubric completion and sticky rolling disablement pass complete hosted
  [39150319607](https://github.com/Jotham566/kasoma/actions/runs/39150319607).
- `3775ae1` / `17abb2d`: responsive staff navigation and payload-free offline report
  comparison pass complete hosted
  [39151730479](https://github.com/Jotham566/kasoma/actions/runs/39151730479).
  This includes the ancestor UI and preserves all genuine approval gates.
- The earlier navigation-only run 39151218081 failed a diagnostic test that read before
  POST acknowledgement. The active follow-up now binds its assertion to the actual
  successful save receipt, retaining sealing checks. It is not reported as a passing run.

Normal learner short-text scoring remains disabled. Synthetic report/role fixtures and
matching fake passes are not academic, safeguarding, licensing or provider approval.

## Active vertical slice

FR-OPS-002, NFR-OBS-001, NFR-SEC-002: add bounded ADMIN grading queue/lease age,
terminal/processing-fallback counts, pending audits and post-activation disablement,
with a typed local stale-queue alert. See
[readiness](E8_GRADING_OPERATIONS_READINESS.md),
[ADR-053](../decisions/ADR/053-bounded-grading-operations.md) and
[verification](E8_GRADING_OPERATIONS_VERIFICATION.md).

GRADING_FAILED includes expected provider refusal, budget and validation fallback.
It is labeled processing fallback and does not establish academic error rate or an
incident. AI usage/error-rate metrics stay unavailable. No schema migration, provider,
retention or learner policy changes.

A broader browser run exposed an independent review-clock issue: a host clock slightly
ahead of Docker failed the SQL nonfuture guard. The active source caps completion at
database time under existing locks without weakening SQL constraints. Rollback-only
reproduction changes from nine failures in ten to ten successes; a thirty-second
ahead-clock regression passes in the 33-case focused review suite.

## Current acceptance

- 26 focused operational contract/API/PostgreSQL cases pass, including actual encrypted
  queue/claim/expiry/neutral/fake-grade/review transitions and exact 24-hour boundaries.
- Lint/types/generated contracts and 884 unit/contract cases pass. The first broad unit
  run caught an omitted analytics-alert enum; schema alignment is fixed and the strict
  test is retained. Broad backend passes 333 integration cases; the clock cap is
  additionally covered by the final 33-case review suite and restricted-login rerun.
- 90 existing browser executions pass. An initial short-text profile had a delayed
  diagnostic and review HTTP 500; clock/root-cause evidence is retained. A later profile
  passes all 12 cases. Final acknowledgement-bound full serial acceptance passes
  104 executions including 200% text and the shared staff layout correction.
- Source/dependency security and populated logical recovery pass (65 tables/616 rows,
  322 ms initially, then 290 ms after the clock cap). Final clock-aware recovery,
  rebuilt images/smoke/security and restricted login pass. Exact-source hosted acceptance
  remains required before promotion; do not infer it from prior runs.

## Review stack and safeguards

All eight Compose services remain running: web, API, worker/Beat, export worker,
PostgreSQL/pgvector, Redis, private MinIO and Mailpit. Candidate operational images are
running, including the completion-clock cap. Final scans/smoke pass. No volumes are reset.

- UI: http://localhost:3000
- Local email capture: http://localhost:8025
- Fictional details only. No real learner/guardian data or external model/provider calls.
- Run native Playwright commands sequentially (shared test-results); do not rebuild the
  native .next while a browser server uses it. Docker builds use their own filesystem.

## Remaining work

Do not claim the full MVP complete. Genuine academic inventory/benchmark/calibration,
report/safety/model authority, privacy/DPIA/PDPO/provider/pilot approval, full preservation
coverage, deletion/anonymization/retention execution and production PITR/device evidence
remain in [the release register](RELEASE_GATES.md) and
[requirements traceability](REQUIREMENTS_TRACEABILITY.md).

Next safe engineering assessment: FR-OPS-004 configurable model usage ceilings across
runtime dispatches. Inspect the existing per-rehearsal request/token/time budget and
rate-bucket expiry before proposing additional controls; do not infer missing limits or
production approval. Actual model evaluation remains separately gated and Gemini is
not to be run without the owner's explicit request.
