# Changelog

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
