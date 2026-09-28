# Current Sprint: E5 recommended practice

The diagnostic/mastery slice is committed and pushed to main as `b26ab75`.
[Hosted CI passed](https://github.com/Jotham566/kasoma/actions/runs/36396016478).
The completed diagnostic branch was deleted. The owner authorized committing and
pushing this verified recommended-practice slice to main, removing its completed
branch, and proceeding with hints.

## Current slice

FR-MST-006, FR-REV-001/006, supporting FR-REV-003/004/005, FR-ID-003,
FR-OPS-001, NFR-SEC-002, NFR-ACC-001 and NFR-MNT-001.

Synthetic versioned recommendation ranking considers every specification-05 factor,
redirects confident prerequisite gaps, respects sparse evidence, selects a supported
skill with enough eligible content and explains recommended practice. A home card
shows the target, reason, time estimate and diagnostic option. Recommended starts
freeze 5–10 assignments and ranking inputs atomically and reuse existing grading,
mastery, consent, idempotency, resume and outbox services.

Manual and recommended planning exclude other active reservations. Recommended
planning also excludes occupied revision topics to preserve the existing uniqueness
constraint, expiring stale reservations before a new start. Read-only replay verifies
preview and committed snapshots. Migration
0008 is additive; the production and academic gates remain closed.

Decision: [ADR-021](../decisions/ADR/021-recommended-practice.md).
Evidence: [recommended practice verification](E5_RECOMMENDATIONS_VERIFICATION.md).

## Next vertical slice

FR-GRD-006: reviewed revision hints, durable usage and hint level, and independence
weighting through the existing mastery engine. Diagnostic hints remain disabled.
Then implement FR-GRD-008 unseen equivalent reassessment. The frozen expert benchmark
and Week 5 short-text gate remain parallel academic dependencies, not waived gates.

## Remaining external dependencies and release gates

- Named owners, kickoff date, delivery capacity and academic reviewer capacity.
- Exact NCDC mappings, real content rights, balanced inventory and expert benchmark.
- Approved privacy notices, verifiable guardian procedure, DPIA and legal approvals.
- Week 5 short-text benchmark gate remains; no model evaluation has been authorized.
- Week 8 production provider selection, production OTP/MFA and restricted DB roles.
- General progress/history UX, reviewed ranking calibration, multiple-choice/short-text,
  hints/reassessment, flags, WhatsApp and operations remain further MVP work.
- Outbox dispatch and approved retention/anonymization jobs remain E8 work.
- Synthetic regression results do not authorize production or certify learning gain.

Prior evidence: [E0](E0_VERIFICATION.md), [E1](E1_VERIFICATION.md),
[E2](E2_VERIFICATION.md), [E3](E3_VERIFICATION.md), [E4](E4_VERIFICATION.md),
[traceability](REQUIREMENTS_TRACEABILITY.md).
