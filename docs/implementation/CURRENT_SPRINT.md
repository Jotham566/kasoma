# Current Sprint: E6 progress and session history

Unseen reassessment is committed and pushed to main as `73c1fba`; the completed
branch was deleted. [Hosted main CI passed](https://github.com/Jotham566/kasoma/actions/runs/36404562915).
The next slice is local on `codex/e6-progress-history`, uncommitted for review.

## Current slice

FR-MST-004/005, supporting FR-MST-002/003, FR-ID-003, FR-REV-005, NFR-SEC-002,
NFR-ACC-001, NFR-LOC-001 and NFR-MNT-001.

Progress summarizes subject/topic/competency estimates from immutable eligible evidence,
with confidence, mapped-skill coverage and guarded recent change. Unfinished, abandoned
and expired diagnostic evidence stays sealed. History provides owned cursor pagination,
Kampala timestamps and existing session resume/review. Reads do not mutate learning
records. No migration is required.

Decision: [ADR-024](../decisions/ADR/024-progress-history.md).
Evidence and check status: [progress verification](E6_PROGRESS_VERIFICATION.md).
Changelog, API contract, runbook and traceability accompany the slice.

## Next vertical slice

FR-GRD-009/FR-CNT-006: learner flags for owned questions/grades, immutable item/version/
attempt linkage, safe optional comments and auditable staff triage. Preserve the Week 5
frozen expert benchmark and short-text gate as academic dependencies. Do not infer
learning gain or misconception resolution from synthetic regression results.

## Remaining dependencies and release gates

- Named owners, kickoff date, delivery and academic reviewer capacity.
- Exact NCDC mappings, content rights, balanced inventory, reviewed equivalent pairs
  and expert benchmark; semantic transfer validation and calibrated criterion thresholds.
- Approved privacy wording, verifiable guardian procedure, DPIA and legal approvals.
- Week 5 short-text benchmark and Week 8 production provider decision; no model
  evaluation, real learner data or cloud deployment is authorized by these local checks.
- Multiple-choice/short-text, learner flags, WhatsApp and operations.
- Production OTP/MFA, restricted DB roles, outbox dispatch and retention/anonymization jobs.

Prior evidence: [reassessment](E4_REASSESSMENT_VERIFICATION.md),
[hints](E4_HINTS_VERIFICATION.md), [recommendations](E5_RECOMMENDATIONS_VERIFICATION.md),
[diagnostics](E5_VERIFICATION.md), [traceability](REQUIREMENTS_TRACEABILITY.md).
