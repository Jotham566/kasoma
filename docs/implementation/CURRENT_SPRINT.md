# Current Sprint: E8 owned data exports

Data-request intake is committed and pushed to main as `68146b9`; its completed
branch was removed. [Hosted main CI passed](https://github.com/Jotham566/kasoma/actions/runs/36523648234).
This next slice is local on `codex/data-exports`, uncommitted for review.

## Current slice

FR-ID-006 export/completion portion, supporting FR-OPS-001/003, NFR-SEC-001/002,
NFR-OBS-001, NFR-ACC-001 and NFR-MNT-001. Recently authenticated owners may download
explicitly projected JSON without learning consent. Encrypted snapshots support frozen
retries for 24 hours; completion evidence records a six-calendar-year retention deadline.
Migration 0015 guards both lifecycles. A bounded worker sweeps expired copies every five
minutes; downloads reject expiry even without cleanup. No public URLs or staff retrieval.
Decision: [ADR-028](../decisions/ADR/028-owned-data-exports.md).
All 315 Python tests and 17 browser tests pass. Setup, migrations, generated contracts,
lint/types, security scans and final container smoke pass.
Check status: [export verification](E8_DATA_EXPORTS_VERIFICATION.md).

## Next vertical slice

Implement the narrow deletion/anonymization workflow for FR-ID-006: early session/channel
revocation, preserved minimized accountability evidence, scoped legal holds and resumable
processing. Reconcile immutable learning/content history in an ADR before changing those
constraints. Large-history export and six-year evidence expiry remain explicit gaps.

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
