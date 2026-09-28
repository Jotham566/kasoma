# Changelog

## 28 September 2026 — learner flags and triage (local implementation)

- Progress/history committed and pushed to main as `df855ab`; completed branch removed.
- Add owned attempt-bound reports, encrypted optional comments, safe receipt recovery,
  rate limits and exact retry handling across browser interruption/reload.
- Add reviewer/admin queue, independent self-assignment, priorities, revision-checked
  resolution/reopening and atomic audit/history/outbox records.
- Preserve grades, mastery and sealed diagnostics; require two reviewers for disputed
  successor content. Migrations 0011–0012 are additive and enforce the approved retention due date.
- Add ADR-025, generated contracts, tests, traceability and
  [verification](docs/implementation/E8_FLAGS_VERIFICATION.md). Production support,
  retention jobs, safeguarding/legal approval and academic calibration remain gated.

## 28 September 2026 — progress and session history (local implementation)

- Unseen reassessment committed and pushed to main as `73c1fba`; completed branch removed.
- Add consent-aware subject/topic/competency progress with evidence confidence, coverage
  and guarded recent-change text; unfinished diagnostic evidence remains sealed.
- Add owned, cursor-paginated session history with resume/review and Kampala timestamps.
- Add ADR-024, generated contracts, regression tests and documentation; no new migration.
- See [verification](docs/implementation/E6_PROGRESS_VERIFICATION.md). Academic calibration
  and production acceptance remain separate gates.

## 28 September 2026 — unseen reassessment (local implementation)

- Reviewed hints committed and pushed to main as `3c0c3ba`; hosted CI passed and completed branch removed.
- Add reviewed equivalent-version claims with independent review of both sides.
- Add one-item unseen reassessment, same-skill/difficulty fallback, conservative clone
  exclusion, durable source linkage and replayable selection evidence.
- Reuse the shared player/grader/mastery service; preserve the original result and
  record separate independent evidence with safe lifecycle events.
- Add migration 0010, generated contracts, synthetic fixtures and regression coverage.
- See [verification](docs/implementation/E4_REASSESSMENT_VERIFICATION.md). Academic
  transfer validity, calibrated resolution criteria and production gates remain pending.

## 28 September 2026 — reviewed revision hints (local implementation)

- Recommended practice merged to main as `88dd880`; hosted CI passed and its branch was removed.
- Add authored/reviewed progressive hints, durable disclosure and safe retry/resume.
- Freeze pre-answer usage and highest level for mastery independence weighting;
  post-answer remediation preserves original grading/evidence and diagnostics block hints.
- Add migration 0009, generated contracts, synthetic fixtures and API/browser tests.
- Require changelog, sprint, traceability and relevant verification/runbook updates
  alongside each implementation change in `AGENTS.md`.
- See [verification evidence](docs/implementation/E4_HINTS_VERIFICATION.md); production
  academic/privacy gates and unseen reassessment remain pending.

## E5 recommended practice (local synthetic verification)

- Versioned synthetic ranking, prerequisite redirection and immutable replay snapshots.
- Explained home recommendation and resumable 5–10-item recommended plans.
- Shared reservation exclusion for manual and adaptive practice.

- E2: synthetic single-choice authoring, independent review, version immutability,
  role checks and append-only content audit, with migration and browser/API tests.

- E1: local OTP identity, protected learner profiles, rotating sessions and separate
  guardian-consent/learner-assent flows with migration, contracts and tests.

Record meaningful repository and product changes here. A documentation baseline is not an application release.

## Unreleased

### Changed

- Moved product documents to `docs/product/` and the engineering pack to `docs/specifications/`.
- Renamed the software requirements document to `01_SRD.md` and updated references.
- Expanded root engineering instructions while preserving the approved source-of-truth hierarchy.

### Added

- E0 local runtime foundation, locked toolchains, health contract/client, migration,
  synthetic fixtures, provider boundaries, tests and initial CI (verification in current sprint).
- Phase 0 assessment and ADR-013 for delegated bootstrap choices.

- ADR navigation, current sprint and implementation traceability for all 61 SRD requirements.
- Workspace directory scaffolding, a safe environment example and a reserved Compose file.
- Make targets for documentation validation and explicit errors for pending runtime commands.

## 2026-09-22 — Initial specification baseline

- Product whitepaper, roadmap and engineering specification pack.
- README, contributor guidance, agent instructions, pull request template and Git/editor conventions.

### E3 first assessment slice

- Add consent-aware topic practice, approved version selection, immutable attempts,
  deterministic single-choice grades, solution gating and transactional result events.
- Add learner resume/retry UI, synthetic fixture command and ADR-016.
- E2 `b5cfd75` pushed to main; hosted CI passed and completed E1/E2 branches removed.

### E4 numeric grading and readiness

- Merge E3 `22773fd`, verify hosted CI and remove its completed branch.
- Resolve difficulty-label mapping and Week 5/6 sequencing in ADR-017 without
  changing published content or weakening quality gates.
- Add numeric authoring/review, safe learner input, exact rational grading,
  units/tolerance/precision policy, immutable response storage and regression tests.

## 28 September 2026 — diagnostic and initial mastery

- E4 numeric grading and the pinned MinIO source-build CI repair merged to main.
- Added synthetic resumable subject diagnostics with hidden in-session grades.
- Added immutable mastery evidence, baseline estimates/history and offline replay.
- Added generated contracts, browser results, migration and regression evidence.
- Full adaptive recommendation factors and academic calibration remain pending.
