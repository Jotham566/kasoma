# Current Sprint: E3 first assessment slice

E0 (`4faf65a`), E1 (`9dfe726`) and E2 (`b5cfd75`) are on main and passed hosted CI.
Completed E1/E2 branches have been removed locally; origin contains only main.
E3 is active on `codex/e3-assessment`, uncommitted for review.
See [E3 verification and file inventory](E3_VERIFICATION.md).

## Current slice

FR-REV-002–005, FR-GRD-001/005/007, FR-CNT-004 and FR-OPS-001; supporting
FR-ID-003, NFR-SEC-002, NFR-ACC-001 and NFR-MNT-001.

A consented S4 learner selects a topic, starts/resumes five-question practice,
receives only approved synthetic single-choice versions, submits immutable answers,
receives deterministic feedback and reads the pinned worked solution after submission.
Retries are idempotent; attempt, grade and outbox record commit atomically.
The API supports 5–10 items and reports insufficient inventory without shrinking plans.
No recommendation/mastery claim is made. See [ADR-016](../decisions/ADR/016-assessment-choice.md).

## Next vertical slice

E3/E4 numeric items and deterministic grading: approved unit/tolerance/equivalence
contracts, content editor and question input, immutable result evidence and boundary
benchmarks. Then implement the 10–15-item diagnostic and initial mastery projection.

## Remaining release gates and questions

- Real academic mapping, rights review and sufficient independently reviewed content.
- Approved consent/assent notices and guardian verification procedures.
- Production providers, staff MFA, role governance and restricted database roles.
- Mastery evidence/projections, outbox dispatch and retention/anonymization jobs.
- Diagnostic, recommended practice, hints, numeric/multiple-choice/short-text grading,
  reassessment, flags, progress and WhatsApp remain scheduled work.
- E0-01: roadmap Week 5 short-text benchmark versus backlog Week 6 implementation.
- E3-01: content difficulty STANDARD/CHALLENGING versus engine CORE/STRETCH; resolve
  before adaptive weighting. The current choice grader does not use difficulty.
- No calendar kickoff or named delivery owners supplied; horizon remains 12 weeks.

Prior evidence: [E0](E0_VERIFICATION.md), [E1](E1_VERIFICATION.md),
[E2](E2_VERIFICATION.md), [Phase 0](PHASE_0_ASSESSMENT.md),
[traceability](REQUIREMENTS_TRACEABILITY.md).
