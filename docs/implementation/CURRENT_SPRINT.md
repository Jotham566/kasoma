# Current Sprint: E8 learner flags and independent triage

Progress/history is committed and pushed to main as `df855ab`; the completed branch
was deleted. [Hosted main CI passed](https://github.com/Jotham566/kasoma/actions/runs/36407232098). This next slice is local on `codex/learner-flags`, uncommitted for review.

## Current slice

FR-GRD-009/FR-CNT-006, supporting FR-CNT-003/004, FR-ID-003, FR-OPS-001/003,
NFR-SEC-002, NFR-ACC-001 and NFR-MNT-001.

Learners report owned submitted questions/grades; staff inspect, claim, prioritize and
resolve flags with immutable source linkage, encrypted text, revision checks and audited
history. Diagnostic feedback remains sealed and no learning evidence is changed.
Disputed successor content requires two independent reviewers. Migrations 0011–0012 are additive.

Decision: [ADR-025](../decisions/ADR/025-learner-flags.md).
Evidence and check status: [flag verification](E8_FLAGS_VERIFICATION.md).
All 280 Python tests and 15 browser tests pass; setup, migrations, contracts, lint/types,
security and final container checks pass. Production gates remain below.

## Next vertical slice

Complete FR-GRD-001 deterministic multiple-choice support through reviewed content,
shared assessment, exact grading and tests. Preserve the expert short-text benchmark
and Week 8 provider gates; synthetic validation does not certify academic truth.

## Remaining dependencies and release gates

- Named owners, kickoff date, delivery and academic reviewer capacity.
- Exact NCDC mappings, content rights, balanced inventory, reviewed equivalent pairs
  and expert benchmark; semantic transfer validation and calibrated criterion thresholds.
- Approved privacy wording, verifiable guardian procedure, DPIA and legal approvals.
- Week 5 short-text benchmark and Week 8 production provider decision; no model
  evaluation, real learner data or cloud deployment is authorized by these local checks.
- Multiple-choice/short-text, WhatsApp and remaining operations.
- Production OTP/MFA, restricted DB roles, outbox dispatch and retention/anonymization jobs.

Prior evidence: [reassessment](E4_REASSESSMENT_VERIFICATION.md),
[hints](E4_HINTS_VERIFICATION.md), [recommendations](E5_RECOMMENDATIONS_VERIFICATION.md),
[diagnostics](E5_VERIFICATION.md), [traceability](REQUIREMENTS_TRACEABILITY.md).
