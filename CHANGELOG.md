# Changelog

## 29 September 2026 — deletion-impact preview (local implementation)

- Owned exports committed and pushed to main as `d20c344`; completed branch removed.
- Add a recent-OTP, independent-claimant ADMIN preview of linked record counts and
  retention/review categories for pending deletion requests, with audited access.
- Bound per-source counts, account for unbound login challenges and related staff
  provenance, and exclude another learner's bound guardian challenges from hash matching.
- Show unresolved legal-hold, erasure and anonymization gates explicitly. Preview does
  not decrypt personal records, revoke access, change data or authorize deletion.
- Add API/generated contracts, administrator UI and regression tests; no migration.
- Correct owner exports to decrypt the display name instead of returning its storage ciphertext;
  add a profiled-learner regression. Deletion previews still never decrypt personal data.
- Update [ADR-029](docs/decisions/ADR/029-deletion-impact-preview.md), sprint,
  traceability, API/data/runbook and [verification](docs/implementation/E8_DELETION_PREVIEW_VERIFICATION.md).

## 29 September 2026 — owned data exports (local implementation)

- Data-request intake committed and pushed to main as `68146b9`; completed branch removed.
- Add recent-OTP owner-only JSON exports with explicit field projections, diagnostic
  sealing, encrypted frozen retries, atomic completion and six-year retention deadlines.
- Add migration 0015, 24-hour download expiry, a bounded five-minute worker sweep and
  `make expire-exports`; expired copies are removed without deleting request evidence.
- Add learner download/retry UI, generated contracts and API/SQL/browser regressions.
- Record [ADR-028](docs/decisions/ADR/028-owned-data-exports.md) and update sprint,
  traceability, API/data/runbook and [verification](docs/implementation/E8_DATA_EXPORTS_VERIFICATION.md).
- Deletion/anonymization, large-history exports and accountability-retention/legal-hold
  processing remain pending; this does not establish production privacy acceptance.

## 29 September 2026 — data-request intake (local implementation)

- Multiple-choice support committed and pushed to main as `02f96bc`; completed branch removed.
- Add recent-OTP export/deletion request intake, owned status and safe acknowledgement,
  including after learning-consent withdrawal and before profile completion.
- Add an independent ADMIN review queue/claim, atomic audits/outbox, deduplicated retries,
  immutable evidence and explicit six-year-after-completion retention policy.
- Add migration 0014, generated contracts, learner/admin screens and regression tests.
- Forward request pagination through the web gateway and install repository-local Corepack
  shims so nested build tasks retain pinned pnpm despite unrelated global installations.
- Update ADR-027, API/data/runbook documentation, sprint and traceability; see
  [verification](docs/implementation/E8_DATA_REQUESTS_VERIFICATION.md). Fulfillment,
  completion evidence, deletion/anonymization and retention jobs remain pending.

## 28 September 2026 — deterministic multiple choice (local implementation)

- Flags/triage committed and pushed to main as `bd9dae3`; completed branch removed.
- Add reviewed multiple-choice keys, exact-set scoring and checkbox delivery through
  shared revision, diagnostic and reassessment paths. Preserve hint/evidence controls.
- Canonicalize selection order for idempotent retries; reject duplicate/unknown IDs.
- Add additive migration 0013, generated contracts, synthetic fixtures and tests.
- Run browser tests in two fresh isolated shards to retain the production OTP peer limit.
- Update ADR-026, API/data/runbook documentation, sprint and traceability; see
  [verification](docs/implementation/E4_MULTIPLE_CHOICE_VERIFICATION.md). Academic
  content approval, short-text benchmark and production deployment remain gated.

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
