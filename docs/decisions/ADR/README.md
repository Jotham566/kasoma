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

- [ADR-036: Objective WhatsApp message format](036-whatsapp-objective-message-format.md)
  records bounded lossless questions and normalization into shared response schemas.

- [ADR-037: Channel-safe shared assessment operations](037-channel-assessment-provenance.md)
  records internal provenance, supported selection and cross-channel continuation constraints.

- [ADR-038: Bound local WhatsApp practice conversations](038-local-whatsapp-practice.md)
  records exact reply context, transient pointers, shared atomic learning and safe fake delivery.

- [ADR-039: Minimized local channel operations](039-local-channel-operations.md)
  records bounded queue cohorts, fake-dispatch sampling and operational thresholds.

- [ADR-040: Synthetic short-text candidate validation](040-short-text-candidate-validation.md)
  records strict offline rubric/evidence checks without learner scoring.

- [ADR-041: Budgeted synthetic dual-pass rehearsal](041-synthetic-short-text-rehearsal.md)
  records independent fake passes and bounded repair/request/token/deadline behavior.

- [ADR-042: Isolated synthetic recovery drill](042-isolated-local-recovery-drill.md)
  records owned temporary databases and verified logical recovery without developer data copies.

- [ADR-043: Individual learning-record holds](043-learning-record-holds.md)
  adds explicit grade, mastery evidence and mastery history preservation targets.

- [ADR-044: Version-pinned reviewed rubrics](044-reviewed-rubric-persistence.md)
  records normalized immutable rubric material and disabled short-text learner assignment.

- [ADR-045: Individual accountability-record holds](045-accountability-record-holds.md)
  adds exact immutable flag-history and data-request-review preservation targets.

- [ADR-046: Shared assessment content locks](046-shared-assessment-content-locks.md)
  permits concurrent immutable readers while excluding content writes and preserving eligibility.


- [ADR-047: Bounded private export artifact format](047-private-export-artifact-format.md)
  binds private encrypted chunks to their request/generation and keeps delivery disabled.


- [ADR-048: Asynchronous owned export delivery](048-asynchronous-owned-export-delivery.md)
  records the verified local asynchronous export lifecycle; production gates remain.

- [ADR-049: Bounded local request histograms](049-local-request-histograms.md)
  records verified local OTel aggregation, privacy and finite retention controls.

- [ADR-050: Short-text pending outcomes and eligibility](050-short-text-pending-and-eligibility.md)
  accepts the verified disabled synthetic path and retains actual learner-enablement gates.

- [ADR-051: Blinded review and release-unit sampling](051-blinded-review-and-release-unit-sampling.md)
  records verified independent review and audit coverage when diagnostic grades remain sealed.

- [ADR-052: Offline evaluation-report comparison](052-offline-evaluation-report-comparison.md)
  records verified payload-free synthetic report comparison without inference or approval.

- [ADR-053: Bounded grading operations](053-bounded-grading-operations.md)
  records verified durable queue observation without academic-error-rate claims.


- [ADR-054: Bounded worker model usage](054-bounded-worker-model-usage.md)
  records verified private local SDK counters, finite Redis aggregation and ADMIN visibility.


- [ADR-055: Terminal channel receipt holds](055-terminal-channel-receipt-holds.md)
  records verified original-record guards after message minimization, preserving opt-out.


- [ADR-056: Wall-clock hold DELETE guards](056-wall-clock-hold-delete-guards.md)
  records verified correction of four legacy evaluation clocks without granting erasure.

- [ADR-057: Minimized channel preservation snapshots](057-minimized-channel-preservation-proposal.md)
  has explicit bounded synthetic approval and complete hosted engineering verification
  at `0a8f674`; full coverage and production/erasure authority remain excluded.

- [ADR-058: Bounded ADMIN audit activity](058-bounded-admin-audit-activity.md)
  records aggregate-only audit navigation, finite sampling and no individual disclosure.

- [ADR-059: Disposable CI runner storage](059-disposable-ci-runner-storage.md)
  records fixed-SDK hosted-only preparation, capacity gates and diagnostics.

- [ADR-060: Completed export accountability retirement](060-completed-export-accountability-retirement-proposal.md)
  has explicit user approval for a default-disabled bounded synthetic retention slice;
  implementation verification and real-data/release approval remain separate.

- [ADR-061: Retention-aware synthetic learner account erasure](061-synthetic-account-erasure-proposal.md)
  has explicit human approval for bounded synthetic implementation, including0044 source
  coverage, exact disposition/profile/contact/reply preservation, restricted erasure,
  post-completion custody and affected-band disablement; verification remains pending.

- [ADR-062: Owned recent practice-day indicator](062-owned-practice-activity.md)
  records the approved roadmap's read-only consistency display, explicit Kampala
  calendar window and existing ownership/sealed-result rules; verification pending.

- [ADR-063: Bounded local OTP adapter observations](063-local-otp-dispatch-observations.md)
  records four payload-free, default-disabled API counters with finite local retention;
  adapter returns are not delivery/billing evidence. Verification is pending.

- [ADR-064: Known metric export loss windows](064-known-metric-export-loss-windows.md)
  records finite unavailable windows for existing request/model observations after
  failed exports, preserving payload codecs and no ledger/production claims.

- [ADR-065: Isolated database and private-object recovery](065-isolated-database-object-recovery.md)
  records a separate synthetic rehearsal restoring private temporary backups with source
  services stopped, exact storage namespace and exclusively owned disposable services.

- [ADR-066: Temporal diagnostic load profile](066-temporal-diagnostic-load-profile.md)
  records a fixed old-evidence/completed-diagnostic synthetic profile using independent
  clocks and normal OTP/domain processing, retaining all existing latency/isolation gates.

- [ADR-067: Versioned operational warning configuration](067-versioned-operational-warning-configuration.md)
  records an ADMIN/recent-auth closed numeric editor, atomic staff audit/version checks,
  original-command retries and explicit warning-only fallback. Verification pending.


- [ADR-068: Owned browser database services](068-owned-browser-database-services.md)
  records one bounded fresh PostgreSQL/pgvector service for the standard synthetic browser
  API, distinct ownership labels and exact-ID cleanup; verification pending.

- [ADR-069: Owned synthetic identity verification source](069-owned-erasure-identity-verification.md)

- [ADR-070: SQL-visible account processing coordination](070-sql-visible-account-processing-gate.md)

- [ADR-071: Isolated erasure SQL capability bootstrap](071-isolated-erasure-capability-bootstrap.md)

- [ADR-072: Private erasure authority and atomic barrier](072-private-erasure-authority-and-atomic-barrier.md)

- [ADR-073: Frozen pre-install source catalog](073-frozen-preinstall-source-catalog.md)
