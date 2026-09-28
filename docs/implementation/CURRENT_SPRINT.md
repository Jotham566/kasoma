# Current Sprint: E4 unseen equivalent reassessment

Reviewed hints are committed and pushed to main as `3c0c3ba`; the completed branch
was deleted. [Hosted CI passed](https://github.com/Jotham566/kasoma/actions/runs/36401623871). The next slice
is local on `codex/e4-unseen-reassessment`, uncommitted for review.

## Current slice

FR-GRD-008, supporting FR-REV-003/005, FR-GRD-007, FR-MST-001/003,
FR-CNT-001/004, FR-ID-003, FR-OPS-001, NFR-SEC-002, NFR-ACC-001 and NFR-MNT-001.

Reviewed equivalent-version claims are preferred to same-primary-skill/difficulty
fallback. Selection excludes all previously served stable items, active reservations
and near-duplicate prompts. One reassessment links to each original revision attempt;
retries and cross-device discovery resume it. The shared player, grader and mastery
service produce separate independent evidence and preserve the original grade.
Migration 0010 is additive; replay checks frozen selection and content hashes.

Decision: [ADR-023](../decisions/ADR/023-unseen-reassessment.md).
Evidence and check status: [reassessment verification](E4_REASSESSMENT_VERIFICATION.md).
All 249 Python tests and 13 browser tests passed, alongside setup, migration, contracts,
lint/types, security and container checks. Changelog, API/data/content specifications,
runbook and traceability accompany the slice.

## Next vertical slice

FR-MST-004/005: consent-aware subject/topic/competency progress and recent session
history, aggregating immutable evidence with visible confidence and sparse-evidence
language. Preserve the Week 5 frozen expert benchmark and short-text gate as parallel
academic dependencies. Do not infer learning gain or misconception resolution from
synthetic regression results.

## Remaining dependencies and release gates

- Named owners, kickoff date, delivery and academic reviewer capacity.
- Exact NCDC mappings, content rights, balanced inventory, reviewed equivalent pairs
  and expert benchmark; semantic transfer validation and calibrated criterion thresholds.
- Approved privacy wording, verifiable guardian procedure, DPIA and legal approvals.
- Week 5 short-text benchmark and Week 8 production provider decision; no model
  evaluation, real learner data or cloud deployment is authorized by these local checks.
- General progress/history, multiple-choice/short-text, learner flags, WhatsApp and operations.
- Production OTP/MFA, restricted DB roles, outbox dispatch and retention/anonymization jobs.

Prior evidence: [hints](E4_HINTS_VERIFICATION.md), [recommendations](E5_RECOMMENDATIONS_VERIFICATION.md),
[diagnostics](E5_VERIFICATION.md), [traceability](REQUIREMENTS_TRACEABILITY.md).
