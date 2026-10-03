# Current Sprint: legal-hold publication and E9 security maintenance

Record legal holds are committed as `ec53ac4`; publication is awaiting the refreshed
security gate and hosted CI. The development-tool advisory found on 3 October is
remediated locally on `codex/lint-security` under
[ADR-031](../decisions/ADR/031-lint-glob-security.md).

## Current evidence

FR-ID-006/BR-010: the legal-hold slice passed 337 Python tests, 17 browser tests and
22 final focused checks on 30 September. See [verification](E8_LEGAL_HOLDS_VERIFICATION.md).
NFR-MNT-001/NFR-SEC-001: dependency replacement now passes frozen setup, five actual-plugin
regressions, 223 Python unit/contract tests, lint/types, generated contracts, native build
and dependency/security audits. See [verification](E9_LINT_SECURITY_VERIFICATION.md).
No audit exclusions or lint rules were removed. Docker startup is blocked by the macOS
administrator prompt for privileged-port configuration. Local database/container checks
remain unavailable until that prompt is completed; hosted CI provides independent checks.

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
