# Current Sprint: E4 deterministic multiple choice

Flags/triage is committed and pushed to main as `bd9dae3`; the completed branch was
removed. [Hosted main CI](https://github.com/Jotham566/kasoma/actions/runs/36411128242).
This next slice is local on `codex/multiple-choice`, uncommitted for review.

## Current slice

FR-GRD-001, supporting FR-GRD-005/007, FR-CNT-001/003/004/005, FR-REV-003/005,
FR-DIAG-004, FR-MST-001/003, NFR-SEC-002, NFR-ACC-001 and NFR-MNT-001.
Reviewed nonempty answer sets, exact deterministic scoring, canonical retry/storage,
checkbox players and compatible immutable evidence through additive migration 0013.
Decision: [ADR-026](../decisions/ADR/026-multiple-choice.md).
All 294 Python tests and 16 browser tests pass; setup, migrations, contracts, lint/types,
security and container checks pass. Hosted main CI is still running at the final check.
Check status and limitations: [multiple-choice verification](E4_MULTIPLE_CHOICE_VERIFICATION.md).

## Next vertical slice

FR-ID-006: consent-aware learner export/deletion request intake, safe acknowledgement,
owned status and auditable staff processing workflow, following the approved retention
policy. Establish the exact deletion/retention boundary before implementing destructive
processing. Expert short-text benchmark and Week 8 provider gates remain unchanged.

## Remaining dependencies and release gates

- Named owners, kickoff date, delivery and academic reviewer capacity.
- Exact NCDC mappings, content rights, balanced inventory, reviewed equivalent pairs
  and expert benchmark; semantic transfer validation and calibrated criterion thresholds.
- Approved privacy wording, verifiable guardian procedure, DPIA and legal approvals.
- Week 5 short-text benchmark and Week 8 production provider decision; no model
  evaluation, real learner data or cloud deployment is authorized by these local checks.
- Short-text, WhatsApp and remaining operations.
- Production OTP/MFA, restricted DB roles, outbox dispatch and retention/anonymization jobs.

Prior evidence: [reassessment](E4_REASSESSMENT_VERIFICATION.md),
[hints](E4_HINTS_VERIFICATION.md), [recommendations](E5_RECOMMENDATIONS_VERIFICATION.md),
[diagnostics](E5_VERIFICATION.md), [traceability](REQUIREMENTS_TRACEABILITY.md).
