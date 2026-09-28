# Current Sprint: E4 reviewed revision hints

Recommended practice is committed and pushed to main as `88dd880`.
[Hosted CI passed](https://github.com/Jotham566/kasoma/actions/runs/36398742634).
Its completed branch was deleted; `codex/e4-reviewed-hints` is the active local
implementation branch. The hint slice remains uncommitted for review.

## Current slice

FR-GRD-006, supporting FR-GRD-007, FR-MST-001/003, FR-CNT-001/004,
FR-ID-003, FR-OPS-001, NFR-SEC-002, NFR-ACC-001 and NFR-MNT-001.

Zero to three authored hints travel through independent content review. Revision
learners request progressive levels with durable usage and exact retry boundaries.
Submission freezes before-answer count/highest level into the immutable attempt and
mastery evidence; the existing independence formula applies without changing points.
Post-answer remediation preserves original evidence. Diagnostics always block hints.
Consent, ownership, current approved content and assignment eligibility are enforced.
Migration 0009 is additive and legacy evidence hashes remain replayable.

Decision: [ADR-022](../decisions/ADR/022-reviewed-hints.md).
Evidence and check status: [hint verification](E4_HINTS_VERIFICATION.md).
The changelog, API/data/content specifications, runbook and traceability accompany this slice.

## Next vertical slice

FR-GRD-008: unseen equivalent reassessment following remediation, with a pinned link
to the original attempt, equivalent approved skill/difficulty selection, separate
independent evidence and no original-grade rewrite. Read the applicable specification
and document selection/shortage semantics before implementation. The frozen expert
benchmark and Week 5 short-text gate remain parallel academic dependencies.

## Remaining external dependencies and release gates

- Named owners, kickoff date, delivery capacity and academic reviewer capacity.
- Exact NCDC mappings, real content rights, balanced inventory and expert benchmark.
- Approved privacy notices, verifiable guardian procedure, DPIA and legal approvals.
- Week 5 short-text benchmark gate remains; no model evaluation has been authorized.
- Week 8 production provider selection, production OTP/MFA and restricted DB roles.
- General progress/history UX, reviewed ranking calibration, multiple-choice/short-text,
  reassessment, flags, WhatsApp and operations remain further MVP work.
- Outbox dispatch and approved retention/anonymization jobs remain E8 work.
- Synthetic regression results do not authorize production or certify learning gain.

Prior evidence: [E0](E0_VERIFICATION.md), [E1](E1_VERIFICATION.md),
[E2](E2_VERIFICATION.md), [E3](E3_VERIFICATION.md), [E4 numeric](E4_VERIFICATION.md),
[E5 diagnostics](E5_VERIFICATION.md), [E5 recommendations](E5_RECOMMENDATIONS_VERIFICATION.md),
[traceability](REQUIREMENTS_TRACEABILITY.md).
