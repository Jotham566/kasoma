# Current Sprint: E8 data-request intake

Multiple-choice support is committed and pushed to main as `02f96bc`; its completed
branch was removed. [Hosted main CI](https://github.com/Jotham566/kasoma/actions/runs/36487637477).
This next slice is local on `codex/data-requests`, uncommitted for review.

## Current slice

FR-ID-006 (intake/review portion), supporting FR-OPS-001/003, NFR-SEC-002,
NFR-ACC-001 and NFR-MNT-001. Requests require recent OTP, not learning consent.
Owned pending status, safe retry and independent ADMIN review are auditable and atomic.
Migration 0014 is additive. Export/deletion fulfillment is not implemented or represented
as complete. Decision: [ADR-027](../decisions/ADR/027-data-request-intake.md).
All 305 Python tests and 17 browser tests pass. Setup, migration, generated contracts,
lint/types, security and container checks pass. Hosted main CI is still running at the final check.
Check status: [data-request verification](E8_DATA_REQUESTS_VERIFICATION.md).

## Next vertical slice

Continue FR-ID-006 with an owned machine-readable export and safe retrieval/completion
workflow, excluding authentication secrets, third-party evidence and assessment keys.
Then implement deletion/anonymization with early session/channel revocation, specific
legal holds and observable retention jobs through a narrow reviewed processor.
Resolve the export content/retention boundary before implementing fulfillment.

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
