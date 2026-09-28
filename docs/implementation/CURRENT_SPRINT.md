# Current Sprint: E5 diagnostic and initial mastery

E0–E4 are on main. Numeric grading committed as `7d2c8ed`; the MinIO clean-setup
repair is `ee73741`. [Hosted CI passed](https://github.com/Jotham566/kasoma/actions/runs/36392615242).
The completed E4 branch was removed. The owner authorized committing and merging
this verified E5 slice to main, then removing its completed branch.

## Current slice

FR-DIAG-001–005, FR-MST-001–003/005, supporting FR-ID-003, FR-REV-002/005/006,
FR-GRD-007, FR-OPS-001, NFR-SEC-002, NFR-ACC-001 and NFR-MNT-001.

Subject diagnostics resume one active plan, sample 15 approved synthetic items,
cover available topics/competencies and adjust difficulty from prior answers.
Answers are acknowledged only after attempt, grade, mastery evidence and outbox
commit. No grade feedback or worked solutions leak during a diagnostic. Completion
freezes initial estimates with confidence and an explained first practice target.

Mastery follows specification 05 and ADR-017 exactly. Immutable per-attempt/skill
evidence includes original inputs and configuration; projections/history can be
replayed. Legacy grades reconcile only after current learner consent authorization.
Original grades remain unchanged. Numeric and choice grading share this path.

[ADR-019](../decisions/ADR/019-minio-source-build.md) repairs unavailable MinIO
images using official pinned source. [ADR-020](../decisions/ADR/020-diagnostic-mastery.md)
records the diagnostic/mastery decisions. Evidence: [E5 verification](E5_VERIFICATION.md).

## Next vertical slice

Implement the full versioned recommendation ranking (FR-MST-006) and recommended
5–10-item revision plans (FR-REV-001/006), including prerequisite redirection,
importance, recency, uncertainty and repetition factors. Preserve the current
baseline and teacher-calibration gate. Then add hint independence and unseen
reassessment to complete the Week 5 learning loop.

## Remaining external dependencies and release gates

- Named owners, kickoff date, delivery capacity and academic reviewer capacity.
- Exact NCDC mappings, real content rights, balanced inventory and expert benchmark.
- Approved privacy notices, verifiable guardian procedure, DPIA and legal approvals.
- Week 5 short-text benchmark gate remains; no model evaluation has been authorized.
- Week 8 production provider selection, production OTP/MFA and restricted DB roles.
- General progress/history UX, full adaptive ranking, multiple-choice/short-text,
  hints/reassessment, flags, WhatsApp and operations remain further MVP work.
- Outbox dispatch and approved retention/anonymization jobs remain E8 work.
- Synthetic regression results do not authorize production or certify learning gain.

Prior evidence: [E0](E0_VERIFICATION.md), [E1](E1_VERIFICATION.md),
[E2](E2_VERIFICATION.md), [E3](E3_VERIFICATION.md), [E4](E4_VERIFICATION.md),
[traceability](REQUIREMENTS_TRACEABILITY.md).
