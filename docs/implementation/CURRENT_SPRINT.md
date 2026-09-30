# Current Sprint: E8 deletion-impact preview

Owned exports are committed and pushed to main as `d20c344`; completed branch removed.
[Hosted export CI passed](https://github.com/Jotham566/kasoma/actions/runs/36529147185).
This next slice is local on `codex/deletion-readiness`, uncommitted for review.

## Current slice

FR-ID-006/BR-010 (deletion review prerequisite), supporting FR-OPS-003, NFR-SEC-002,
NFR-ACC-001 and NFR-MNT-001. An independent ADMIN claimant can inspect bounded counts
and retention/review categories for a pending DELETE request. Recent authentication,
claim ownership, read audits and rate limits are enforced. No personal payload is read
or decrypted. Execution is structurally disabled and unresolved safeguards are explicit.
Decision: [ADR-029](../decisions/ADR/029-deletion-impact-preview.md).
All 321 Python tests and 17 browser tests pass, plus setup, migration/seed, generated
contracts, lint/types, security scans and final container smoke.
Check status: [deletion-preview verification](E8_DELETION_PREVIEW_VERIFICATION.md).

## Next vertical slice

Implement specific-record, time-bounded legal-hold lifecycle and deletion execution state.
Then review the exact erasure/anonymization migration and recovery plan, reconciling
immutable learning, content and accountability evidence before destructive execution.
The preview is not approval to erase, a clearance of legal holds or proof of anonymity.
Large-history export and six-year evidence expiry remain explicit gaps.

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
