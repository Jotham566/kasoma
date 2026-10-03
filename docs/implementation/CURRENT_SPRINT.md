# Current Sprint: E8 specific-record legal holds

Deletion-impact preview is committed and pushed to main as `6f7f210`; completed branch
`codex/deletion-readiness` removed. [Hosted CI passed](https://github.com/Jotham566/kasoma/actions/runs/36726790587). The next slice is local on `codex/legal-holds`,
uncommitted for review.

## Current slice

FR-ID-006/BR-010 preservation prerequisite, supporting FR-OPS-003, NFR-SEC-002,
NFR-ACC-001 and NFR-MNT-001. The independent recent-OTP ADMIN claimant can create,
list and release finite holds on individual owned consent, attempt, content-flag and
data-request records. Metadata, receipts, audits and safe outbox events are atomic;
SQL checks enforce ownership and immutability, with active-hold DELETE guards.
The preview reports active registered holds and explicitly incomplete coverage.
Deletion remains disabled. Decision: [ADR-030](../decisions/ADR/030-record-legal-holds.md).
All 337 Python tests and 17 browser tests pass, followed by 22 focused checks for the
final inventory correction. Setup, lint/types, contracts, build, security and final
container smoke pass. See [legal-hold verification](E8_LEGAL_HOLDS_VERIFICATION.md).
The browser run includes the related FR-ID-001 initial-session-check race correction.

## Next vertical slice

Implement the deletion execution state and expand hold coverage for the exact deletion
plan. Review the erasure/anonymization transform, constraints and recovery plan before
any destructive execution. Reconcile immutable learning, content and accountability
records, embedded references, logs, backups and representative requests.
Zero active registered holds is not clearance. Large-history exports and six-year
evidence expiry remain explicit gaps; production privacy approval is independent.

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
