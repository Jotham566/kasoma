# Architecture Decision Records

Accepted ADR-001 through ADR-012 and the existing decision register remain in the [canonical decision log](../../specifications/13_ADR_and_Decision_Log.md). Read that log before proposing a change; do not duplicate accepted decision bodies here.

Create new records in this directory as `NNN-short-title.md`, starting at `013` after checking the decision log for newer IDs. Use the template in the canonical decision log, mark proposals as proposed, and record approval before treating them as accepted. Add links to new records to this index and the decision log.

This directory location follows the user-requested repository organization. It does not change the accepted runtime architecture or product scope.

- [ADR-013: Bootstrap implementation choices](013-bootstrap-foundation.md)

- [ADR-014: Local identity and consent](014-identity-consent.md)

- [ADR-015: First content review vertical slice](015-content-review.md)

- [ADR-016: First assessment and deterministic choice slice](016-assessment-choice.md)

- [ADR-017: Implementation readiness resolutions](017-readiness-resolutions.md)
- [ADR-018: Bounded deterministic numeric answers](018-numeric-grading.md)

- [ADR-019: Local MinIO source build](019-minio-source-build.md)

- [ADR-020: Diagnostic and initial mastery](020-diagnostic-mastery.md)

- [ADR-021: Synthetic recommended practice and replay](021-recommended-practice.md)

- [ADR-022: Reviewed hints and immutable independence evidence](022-reviewed-hints.md)
  records reviewed disclosure, retry boundaries and frozen independence metadata.

- [ADR-023: Unseen equivalent reassessment](023-unseen-reassessment.md)
  records reviewed claims, unseen selection, immutable linkage and independent evidence.

- [ADR-024: Evidence-derived progress and history](024-progress-history.md)
  records confidence-aware aggregation, sealed diagnostics and owned cursor pagination.

- [ADR-025: Learner flags and independent triage](025-learner-flags.md)
  records report privacy, immutable linkage, audit/retry controls and disputed review.

- [ADR-026: Exact-set deterministic multiple choice](026-multiple-choice.md)
  records canonical sets, all-or-nothing grading and compatible immutable evidence.

- [ADR-027: Minimized data-request intake](027-data-request-intake.md)
  records rights access, verification, independent review and the fulfillment boundary.

- [ADR-028: Owned bounded data exports](028-owned-data-exports.md)
  records explicit disclosure, encrypted retries, completion and copy expiry.

- [ADR-029: Minimized deletion-impact preview](029-deletion-impact-preview.md)
  records non-destructive review, bounded counts, audit and explicit execution blockers.

- [ADR-030: Specific-record legal holds](030-record-legal-holds.md)
  records finite record preservation, independent review, immutable evidence and partial coverage.

- [ADR-031: Remove vulnerable lint-only glob dependency](031-lint-glob-security.md)
  records the scoped dependency replacement and directory-discovery compatibility tests.

- [ADR-032: Bounded asynchronous draft imports](032-bounded-draft-imports.md)
  records synthetic JSON limits, author rechecks, transactional retries and independent review.

- [ADR-033: Local operational health and threshold alerts](033-local-operations-health.md)
  records minimized ADMIN snapshots, monitoring heartbeats and local alert defaults.

- [ADR-034: Consent-gated WhatsApp linking](034-whatsapp-linking.md)
  records bounded signed intake, fake delivery, STOP barriers, retries and transient retention.

- [ADR-035: Shared assessment transactions](035-shared-assessment-transactions.md)
  records internal actor authorization and atomic reuse of existing grading/mastery operations.
