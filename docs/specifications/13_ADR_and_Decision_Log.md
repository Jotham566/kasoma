# Kasoma Architecture Decision Record and Decision Log

| Field | Value |
|---|---|
| Version | 1.3.0 |
| Status | Initial decisions accepted for MVP baseline |

## ADR template

```markdown
# ADR-NNN: Title
Date:
Status: Proposed | Accepted | Superseded | Rejected
Owners:
Requirement IDs:

## Context
## Decision
## Alternatives considered
## Consequences
## Security/privacy/academic impact
## Migration or rollback
## Approval
```

## ADR-001: Modular monolith

**Status:** Accepted\
**Decision:** Build one FastAPI application organized into domain modules plus asynchronous worker, rather than microservices.\
**Reason:** 12-week delivery, shared transactions and small team.\
**Consequence:** Module ownership is enforced in code; extraction is deferred until measured need.

## ADR-002: Next.js and FastAPI

**Status:** Accepted\
**Decision:** Next.js/TypeScript for web and FastAPI/Python for API/AI/data logic.\
**Reason:** Strong mobile web ecosystem, typed client generation and Python grading/ML tooling.\
**Consequence:** OpenAPI is the interface boundary; business logic remains server-side.

## ADR-003: PostgreSQL source of truth

**Status:** Accepted\
**Decision:** PostgreSQL stores operational truth; Redis is cache/queue only; object storage holds media.\
**Reason:** Transactions and auditability are central to learning evidence.\
**Consequence:** Mastery can be rebuilt from immutable grades/evidence.

## ADR-004: Interpretable mastery model v1

**Status:** Accepted\
**Decision:** Use versioned weighted evidence rather than IRT/BKT/DKT for MVP.\
**Reason:** Sparse initial data, explainability and testability.\
**Consequence:** Configuration is treated as hypothesis and evaluated against unseen items.

## ADR-005: Deterministic grading first

**Status:** Accepted\
**Decision:** Objective/numeric grading is deterministic; model grading is limited to approved bounded short-text rubrics.\
**Reason:** Trust and reproducibility.\
**Consequence:** Low-confidence model cases use safe fallback.

## ADR-006: Versioned approved content

**Status:** Accepted\
**Decision:** Approved item versions are immutable and historical attempts pin exact versions.\
**Reason:** Reproducible grading and corrections.\
**Consequence:** Edits create a new version and require review.

## ADR-007: Shared channel services

**Status:** Accepted\
**Decision:** Web and WhatsApp use identical assessment, grading and mastery application services.\
**Reason:** Prevent inconsistent learner state and duplicated logic.\
**Consequence:** WhatsApp remains an adapter with constrained rendering/state.

## ADR-008: Provider-neutral AI and messaging adapters

**Status:** Accepted\
**Decision:** AI, object storage, email, SMS and messaging use internal interfaces. Development uses fake/local implementations. Production providers are selected through a later ADR. Meta WhatsApp remains the required external production channel adapter.\
**Reason:** Testability, zero-cost development, cost control and portability.\
**Consequence:** Provider-specific payloads remain in adapter modules.

## ADR-009: Transactional outbox

**Status:** Accepted\
**Decision:** Use a database outbox for mastery, analytics and message-triggering domain events.\
**Reason:** Avoid saved attempts with missing downstream processing.\
**Consequence:** Worker lag is monitored and handlers are idempotent.

## ADR-010: Web-first PWA behaviour, no native app

**Status:** Accepted\
**Decision:** Deliver responsive web with resilient session behaviour; no native mobile application or full offline synchronization in MVP.\
**Reason:** coverage within 12 weeks.\
**Consequence:** offline work is limited to safe recovery/retry, not extended unsynchronized assessment.

## Product/technical decision log

| ID | Date | Decision | Owner | Affected requirements |
|---|---|---|---|---|
| D-001 | 22 Sep 2026 | Product name is Kasoma | Product | all |
| D-002 | 22 Sep 2026 | MVP deadline is 12 weeks | Product | backlog/release |
| D-003 | 22 Sep 2026 | MVP is S4 Mathematics and Physics, three topic clusters each | Product/Academic | FR-DIAG, FR-REV, FR-CNT |
| D-004 | 22 Sep 2026 | Web is complete; WhatsApp is focused short practice | Product | FR-WA-* |
| D-005 | 22 Sep 2026 | 250 approved items is the minimum; 400 is the upper target | Academic | FR-CNT, release gate |

## Resolved production-pilot decisions

| ID | Resolution | Owner | Reopen only if |
|---|---|---|---|
| P-001 | Freeze Mathematics clusters as **Algebra and Functions**, **Geometry, Trigonometry and Measurement**, and **Statistics and Probability**. Freeze Physics clusters as **Mechanics and Energy**, **Waves, Light and Sound**, and **Electricity and Magnetism**. Exact NCDC learning-outcome mappings remain an academic content task, not a scope change. | Academic/Product | NCDC mapping review finds a material coverage error before item authoring |
| P-002 | Treat every learner under 18 as a child. Require verifiable parent/guardian consent and separate learner assent before diagnostics, revision, WhatsApp linking or outcome research. Learners 18+ consent for themselves. No passive school-only consent. | Safeguarding/Legal | Ugandan counsel or PDPO supplies contrary binding guidance |
| P-003 | Use **AWS SES email OTP as the guaranteed baseline**; use **Africa's Talking SMS for Ugandan phone OTP** after sender/commercial approval and delivery testing. A learner may use either verified route. Enforce per-identifier/IP/device limits and a monthly SMS budget kill switch. No automatic second SMS vendor in MVP. | Technical/Product | pre-production MTN/Airtel delivery is below 95% within two minutes or vendor terms fail privacy review |
| P-004 | Use **Celery 5.6.x with Redis transport** and the transactional outbox. Use local Redis for development; select a generally available managed Redis-compatible production service with the Week 8 cloud ADR. PostgreSQL remains the source of truth; queue jobs are idempotent. | Technical | production candidate fails availability, durability or load gates |
| P-005 | Adopt the retention schedule in `09_Security_Privacy_and_Safeguarding.md`; register the company/system with Uganda's PDPO as applicable, complete a DPIA and data-flow register, sign processor agreements, and approve cross-border safeguards before real learner data. | Privacy/Legal | counsel/PDPO or contractual obligations require a different period |
| P-006 | Run a 30–50 learner closed alpha followed by a 100–200 learner beta across 2–4 schools. Use guardian consent/learner assent, baseline and unseen-equivalent reassessment, predefined metrics, withdrawal without penalty and incident monitoring. Obtain independent ethics determination before any generalizable research/publication; otherwise clearly limit claims to product evaluation. | Product/Safeguarding/Academic | schools, ethics review or safeguarding assessment changes cohort/design |
| P-007 | Enable automatic short-text grading only when two independent rubric passes agree exactly, schema/rubric checks pass, no injection/safety flag occurs, and calibrated validation predicts **≥90% exact expert-score agreement** for that confidence band. Otherwise use `LOW_CONFIDENCE` and objective reassessment/human audit. The overall supported short-text benchmark remains ≥85%. | Academic/AI | calibration data supports a safer threshold change approved through ADR |
| P-008 | Keep development cloud-neutral and select **AWS, Azure or GCP** by the end of Week 8 using the approved provider matrix. Production requires zone/multi-zone resilience where feasible, 35-day point-in-time backups, encrypted approved-region recovery, RPO 24 hours and RTO 8 hours. Complete cross-border assessment and processor contracts before beta. | Technical/Security/Privacy | provider evidence changes materially after approval |

These decisions are implementation defaults, not substitutes for Ugandan legal advice, NCDC academic validation or provider contracting.

## Newly accepted decisions

| ID | Date | Decision | Owner | Affected requirements |
|---|---|---|---|---|
| D-006 | 22 Sep 2026 | Freeze the six MVP academic clusters listed in P-001 | Academic/Product | FR-DIAG, FR-REV, FR-CNT |
| D-007 | 22 Sep 2026 | Under-18 guardian consent plus learner assent | Safeguarding/Legal | FR-ID-003 |
| D-008 | 22 Sep 2026 | Email OTP baseline; Africa's Talking SMS after delivery/privacy gate | Technical/Product | FR-ID-001–002 |
| D-009 | 22 Sep 2026 | Celery 5.6.x and Azure Managed Redis | Technical | **Partially superseded by D-014: Celery retained; production Redis provider deferred** |
| D-010 | 22 Sep 2026 | Adopt explicit retention, DPIA, PDPO and cross-border controls | Privacy/Legal | NFR-SEC, FR-ID-006 |
| D-011 | 22 Sep 2026 | Two-stage 30–50/100–200 learner pilot | Product/Academic | release evidence |
| D-012 | 22 Sep 2026 | Dual-pass, calibrated ≥90% gate for automatic short-text scores | Academic/AI | FR-GRD-003–004 |
| D-013 | 22 Sep 2026 | Azure South Africa North primary region | Technical/Security | **Superseded by D-014** |
| D-014 | 22 Sep 2026 | Keep AWS, Azure and GCP eligible; select provider/region by end of Week 8 using documented evidence | Technical/Security/Privacy | NFR-REL, NFR-SEC |
| D-015 | 22 Sep 2026 | Local-first zero-paid-API development with fake providers in CI and local open models for AI work | Technical/AI | architecture, testing, bootstrap |
| D-016 | 22 Sep 2026 | Use host-native Ollama on the 16 GB M4 Mac Mini; default to a benchmark-selected 4B–8B quantized model, with 12B as an optional stretch profile | Technical/AI | architecture, testing, bootstrap |
| D-017 | 22 Sep 2026 | Use Google AI Studio free-tier Gemini only for opt-in tests over synthetic or approved de-identified fixtures; never send real learner or confidential data | Technical/AI/Privacy | AI guardrails, testing |

## ADR-011: Local-first, cloud-neutral development

**Status:** Accepted\
**Decision:** Run the complete application locally using open-source infrastructure and provider fakes. Use Ollama/llama.cpp for developer inference and vLLM for shared-GPU inference. No ordinary test or CI path may call a paid API. Cloud providers remain adapter/deployment choices until the Week 8 production ADR.\

## ADR-012: M4 Ollama baseline and sanitized Gemini free evaluation

**Status:** Accepted.\
**Decision:** Run Ollama natively on the M4 Mac Mini with 16 GB unified memory and use a quantized 4B–8B model as the supported baseline. Keep 12B quantized models optional and exclude 27B-class models from the required workflow. Add a manual `gemini-free-eval` adapter for high-capability comparison, restricted to synthetic or formally approved de-identified fixtures.\
**Consequence:** Everyday work remains local and reproducible. Gemini can expose quality gaps without API spend, but free-tier data-use terms prevent it from processing real learner or confidential data and its changing project quotas cannot be a CI dependency.
**Reason:** Reduce development cost, enable offline/reproducible testing and avoid premature vendor lock-in.\
**Consequences:** The team must maintain provider contracts, frozen evaluation sets and a deliberate hosted-model compatibility run before production. Local-model quality cannot be treated as production evidence.

## Bootstrap implementation records

- [ADR-013: Bootstrap implementation choices](../decisions/ADR/013-bootstrap-foundation.md)
  records delegated tooling, health-contract and migration-foundation choices;
  no accepted architecture or learner behaviour is replaced.

- [ADR-014: Local identity and consent](../decisions/ADR/014-identity-consent.md)
  records implementation choices for the approved E1 identity and consent contracts.

- [ADR-015: First content review vertical slice](../decisions/ADR/015-content-review.md)
  records the approved workflow implementation and explicit remaining content scope.

- [ADR-016: First assessment and deterministic choice slice](../decisions/ADR/016-assessment-choice.md)
  records consent-aware topic practice, immutable grading and explicit remaining scope.

- [ADR-017: Implementation readiness resolutions](../decisions/ADR/017-readiness-resolutions.md)
  resolves E0-01/E3-01 while preserving existing values and release gates.
- [ADR-018: Bounded deterministic numeric answers](../decisions/ADR/018-numeric-grading.md)
  records reviewed numeric contracts, exact grading semantics and migration controls.

- [ADR-019: Local MinIO source build](../decisions/ADR/019-minio-source-build.md)
  repairs clean setup after the pinned public image became unavailable.

- [ADR-020: Diagnostic and initial mastery](../decisions/ADR/020-diagnostic-mastery.md)
  records synthetic diagnostics, sealed results, synchronous evidence and replay.

- [ADR-021: Synthetic recommended practice and replay](../decisions/ADR/021-recommended-practice.md)
  records ranking inputs, prerequisite redirection and immutable recommended plans.

- [ADR-022: Reviewed hints and immutable independence evidence](../decisions/ADR/022-reviewed-hints.md)
  records reviewed disclosure, retry boundaries and frozen independence metadata.

- [ADR-023: Unseen equivalent reassessment](../decisions/ADR/023-unseen-reassessment.md)
  records reviewed claims, unseen selection, immutable linkage and independent evidence.

- [ADR-024: Evidence-derived progress and history](../decisions/ADR/024-progress-history.md)
  records confidence-aware aggregation, sealed diagnostics and owned cursor pagination.

- [ADR-025: Learner flags and independent triage](../decisions/ADR/025-learner-flags.md)
  records report privacy, immutable linkage, audit/retry controls and disputed review.

- [ADR-026: Exact-set deterministic multiple choice](../decisions/ADR/026-multiple-choice.md)
  records canonical sets, all-or-nothing grading and compatible immutable evidence.

- [ADR-027: Minimized data-request intake](../decisions/ADR/027-data-request-intake.md)
  records rights access, verification, independent review and the fulfillment boundary.

- [ADR-028: Owned bounded data exports](../decisions/ADR/028-owned-data-exports.md)

- [ADR-029: Minimized deletion-impact preview](../decisions/ADR/029-deletion-impact-preview.md)

- [ADR-030: Specific-record legal holds](../decisions/ADR/030-record-legal-holds.md)
  records finite record preservation, independent review, immutable evidence and partial coverage.

- [ADR-031: Remove vulnerable lint-only glob dependency](../decisions/ADR/031-lint-glob-security.md)
  records the scoped dependency replacement and directory-discovery compatibility tests.

- [ADR-032: Bounded asynchronous draft imports](../decisions/ADR/032-bounded-draft-imports.md)
  records synthetic JSON limits, author rechecks, transactional retries and independent review.

- [ADR-033: Local operational health and threshold alerts](../decisions/ADR/033-local-operations-health.md)
  records minimized ADMIN snapshots, monitoring heartbeats and local alert defaults.

### ADR-034 — local WhatsApp linking and durable intake

See [ADR-034](../decisions/ADR/034-whatsapp-linking.md). Defines consent/recent-auth code issue,
owner/sender uniqueness, exact-byte signature verification, atomic intake, STOP/unlink barriers,
actor-before-channel lock ordering, fake-only replies, bounded retries and transient expiry.
Local implementation is verified under [E7 evidence](../implementation/E7_LINKING_READINESS.md);
academic practice and production transport remain pending.

### ADR-035 — shared transaction-scoped assessment

See [ADR-035](../decisions/ADR/035-shared-assessment-transactions.md). Internal actor-authorized
start/serve/submit operations preserve web contracts and existing grading/mastery behavior while
allowing the next channel slice to commit receipts and learning evidence atomically. Commit
`50044d4` and database regressions passed hosted CI 37149982356; no WhatsApp grading is enabled
by the refactor alone.

### ADR-036 — bounded objective message format

See [ADR-036](../decisions/ADR/036-whatsapp-objective-message-format.md). Independently reviewed
WHATSAPP suitability, plain-text and length checks precede selection. Numbered choice and exact
numeric replies normalize to existing response schemas. The conversation layer must bind replies
to the exact question before invoking the parser; no grading or practice is enabled here alone.

### ADR-037 — channel assessment provenance

See [ADR-037](../decisions/ADR/037-channel-assessment-provenance.md). Trusted internal channel
operations reuse grading/mastery and enforce five-item approved channel capability. Public API
contracts remain WEB-only; migration 0019 preserves immutable evidence with explicit provenance.
Commit `c0b5b55` passed CI 37217857047; the foundation alone does not enable webhook-driven practice.

### ADR-038 — local five-question conversations

See [ADR-038](../decisions/ADR/038-local-whatsapp-practice.md). START/CONTINUE use explicit topic
menus and five-item shared revision sessions. Replies bind to the exact sent menu/question;
STOP/unlink invalidates transient pointers. Approved references are rendered under current access,
with bounded encrypted intake and a local queue wake-up. Commit `5063528` passed full hosted
CI 37220225176 (469 Python, 20 browser and five tooling checks); production gates remain.

### ADR-039 — minimized channel operations

See [ADR-039](../decisions/ADR/039-local-channel-operations.md). Extend ADMIN operations with
bounded channel cohorts/queue age and sampled fake-dispatch timing. Typed local thresholds use
existing safe alert logging. No learner delivery, load/SLO, cloud or production claim is implied.

### ADR-040 — synthetic short-text candidate validation

See [ADR-040](../decisions/ADR/040-short-text-candidate-validation.md). Strict rubric/evidence/context
validation rejects unsupported candidate output without learner scoring. Independent passes,
repair, academic calibration and learner fallback remain required integration gates.

### ADR-041 — budgeted synthetic dual-pass rehearsal

See [ADR-041](../decisions/ADR/041-synthetic-short-text-rehearsal.md). The shared gateway gains
additive structured task/ceiling fields and deterministic fixtures. Independent passes, one global
schema repair and fail-closed budgets produce internal candidates only; automatic scoring stays off.

### ADR-042 — isolated synthetic recovery drill

See [ADR-042](../decisions/ADR/042-isolated-local-recovery-drill.md). A local-only command creates
its own source/destination databases, verifies restored synthetic evidence and cleans up only
owned temporary databases. No developer-database overwrite, production PITR or RPO/RTO claim.

### ADR-043 — individual learning-record holds

See [ADR-043](../decisions/ADR/043-learning-record-holds.md). Extend the partial hold registry to
grades, mastery evidence and mastery history with exact ownership and row locks. Grade references
use attempt_id. Existing immutability and independent authorization remain; deletion stays disabled.

### ADR-044 — version-pinned reviewed rubrics

See [ADR-044](../decisions/ADR/044-reviewed-rubric-persistence.md). Synthetic SHORT_TEXT authoring
reuses independent content review. Rubric IDs equal immutable item-version IDs; normalized criteria
must match the reviewed document and cannot change outside DRAFT. Learner assignment stays disabled;
academic calibration and pending/fallback integration are separate gates.

### ADR-045 — individual accountability-record holds

See [ADR-045](../decisions/ADR/045-accountability-record-holds.md). FLAG_HISTORY and
DATA_REQUEST_REVIEW extend exact preservation to existing immutable rows owned through their
parent flag/request. Review targets use request_id. Normal parent workflows, independent authorized
claimant controls, privacy and immutable evidence remain; deletion stays disabled.

### ADR-046 — shared assessment content locks

See [ADR-046](../decisions/ADR/046-shared-assessment-content-locks.md). Assessment content reads
use shared row locks that still exclude retirement/writes; manual topic selection avoids unrelated
topic enumeration. Existing content eligibility, grading, transaction and channel boundaries remain.
The objective load baseline checks operation-specific latency rather than hiding slow routes in an aggregate.


### ADR-047 — bounded private export artifact format

See [ADR-047](../decisions/ADR/047-private-export-artifact-format.md). A bounded internal format
binds encrypted chunks to their request/generation/ordinal, with trusted manifest sizes/digests.
This is preparation for FR-ID-006 large-history delivery; no route, publication, storage lifecycle,
retention policy or existing synchronous export limit changes. Delivery remains disabled.

### ADR-048 — asynchronous owned export delivery (proposed)

See [ADR-048](../decisions/ADR/048-asynchronous-owned-export-delivery.md).
Local lifecycle/transport verification is recorded; final-head hosted acceptance and
promotion remain pending. This proposal does not authorize deletion or change retention.

### ADR-049 — bounded local request histograms

See [ADR-049](../decisions/ADR/049-local-request-histograms.md). Accepted for local
synthetic implementation at 46a0f8a after hosted 38034913518; production approval
remains gated. Attribute-free API response-start histograms and bounded Redis
projection are merged; they do not measure complete-response latency or release SLOs.

### ADR-050 — short-text pending outcomes and eligibility

See [ADR-050](../decisions/ADR/050-short-text-pending-and-eligibility.md). Disabled
synthetic learner flow passes hosted 39143803289 at 853f80a and is merged. Genuine
academic/calibration/privacy/provider approval and normal learner enablement remain gated.

### ADR-051 — blinded review and release-unit sampling

See [ADR-051](../decisions/ADR/051-blinded-review-and-release-unit-sampling.md).
Disabled synthetic independent review/rolling controls pass hosted 39150319607 at
2164209; the later database-clock completion cap passes 39155326659 at a357222.
These engineering decisions do not approve real reviewers, calibration or scoring bands.

### ADR-052 — offline evaluation report comparison

See [ADR-052](../decisions/ADR/052-offline-evaluation-report-comparison.md). Payload-free
synthetic report comparison passes hosted 39151730479 at 17abb2d and is merged.
No inference call, academic truth, sanitation, license or real evaluation approval follows.

### ADR-053 — bounded grading operations

See [ADR-053](../decisions/ADR/053-bounded-grading-operations.md). Bounded ADMIN
queue/lease/outcome/audit visibility and local stale-age alerts pass hosted run
39155326659 at `a357222`. Processing fallback does not establish academic error rate.

### ADR-054 — bounded worker model usage

See [ADR-054](../decisions/ADR/054-bounded-worker-model-usage.md). Six private local
SDK counters, bounded Redis aggregation and ADMIN visibility pass complete hosted
run 39160113771 at `0c73c45` and are merged.
No learner content, billing authority, complete fleet accounting or quota policy.


### ADR-055 — exact terminal channel receipt holds

See [ADR-055](../decisions/ADR/055-terminal-channel-receipt-holds.md). Extend existing
exact-record holds only to owned already-minimized terminal receipts. New creation
stays disabled for staged rollout; live-state preservation and full coverage stay open.
Source 397f562 passes complete hosted run 39165896953 and is merged.


### ADR-056 — wall-clock hold DELETE evaluation

See [ADR-056](../decisions/ADR/056-wall-clock-hold-delete-guards.md). Four legacy
wrappers must observe a committed hold when DELETE executes, even if its transaction
began earlier. Historical queries, source evidence and immutable guards remain unchanged.

## ADR-057: Minimized channel preservation snapshots

**Status:** Explicit user approval for bounded synthetic implementation on 19 October;
complete bounded engineering verification at `0a8f674`, hosted 39183714273. See
[ADR-057](../decisions/ADR/057-minimized-channel-preservation-proposal.md).
Bounded encrypted link/conversation-version evidence is independent of mutable
operational state. Approval covers the specified source identities, allowed fields
and finite lifecycle in synthetic development. The capture/lifecycle/API/UI increment is verified with creation default-disabled;
real-data processing, raw-body preservation, full coverage and erasure remain excluded.

## ADR-058: Bounded ADMIN audit activity

**Status:** Accepted for bounded synthetic ADMIN activity; complete hosted 39171302022
passes at 5d95f9d. See
[ADR-058](../decisions/ADR/058-bounded-admin-audit-activity.md). Implement the approved
audit endpoint/navigation as a bounded fixed-category ADMIN aggregate, preserving
individual-record support boundaries, immutable evidence and finite sample reporting.

## ADR-059: Disposable CI runner storage

**Status:** Accepted for the disposable hosted profile; complete hosted 39171302022
passes at 5d95f9d. See
[ADR-059](../decisions/ADR/059-disposable-ci-runner-storage.md). A measured runner
disk failure motivates hosted-only fixed SDK preparation, capacity checks and
diagnostics. No local/application data cleanup or acceptance reduction is permitted.

ADR-056 is also accepted through the same complete integrated run at 5d95f9d. The
older standalone disk-exhaustion run remains failed; no real-data/erasure approval.

## ADR-060: Completed export accountability retirement

**Status:** Approved by explicit user response on 19 October 2026 for bounded
synthetic implementation only. See
[ADR-060](../decisions/ADR/060-completed-export-accountability-retirement-proposal.md).
The approved bounded synthetic slice covers due completed EXPORT accountability,
two exact hold targets, restricted SQL execution and finite retry semantics. No
real-data processing, account-erasure or production activation is granted.
Implementation acceptance requires the decision’s migration, role and test gates.

ADR-060 preservation and SQL kernel sources `be2735e` and `e5d3d98` pass complete
hosted39232307831/39234377840 respectively. The latter passes456 integration and108
browser executions. Executor operations now pass complete hosted39256037485 attempt2
at `d8fc031`: 1,112 unit/contract, 465 integration, 35 tooling and 111 browser
executions, focused controls and all engineering gates. Review state stays false.
These are bounded synthetic engineering results, not real-data/erasure or release approval.

## ADR-061: Retention-aware synthetic learner account erasure

**Status:** Explicit human approval recorded20 October2026 for bounded synthetic implementation
and isolated tests, including the0044 source addendum; engineering acceptance pending. See
[ADR-061](../decisions/ADR/061-synthetic-account-erasure-proposal.md) and its
[71-table disposition manifest including0043/0044 addendum](../implementation/E8_ERASURE_DISPOSITION_PROPOSAL.md).
The proposal explicitly resolves the data-model replacement-identity ambiguity through
eligible row removal, retains lawful exact evidence and proposes restricted finite
execution, richer encrypted preservation and post-completion custody. These are new
choices, not extensions of ADR-057/060. No real-data/production authority is inferred.

## ADR-062: Owned recent practice-day indicator

**Status:** Accepted within the user's approved MVP implementation discretion;
engineering verification pending. See
[ADR-062](../decisions/ADR/062-owned-practice-activity.md). Roadmap3.5's simple
consistency indicator is a read-only count of visible graded-practice dates in the
selected subject's last seven Kampala calendar days. No stored streak/reward system,
new authorization, retention class or change to mastery/diagnostic sealing. This is
independent of unapproved ADR-061 and grants no real-data/production authority.

## ADR-063 - bounded local OTP adapter observations

[ADR-063](../decisions/ADR/063-local-otp-dispatch-observations.md) records the approved
MVP's local messaging-observation extension: four static API email/SMS return/failure
counters, no payload/identifier dimensions, an app-local observer and existing finite
Redis transport. Default-disabled; development/test only. ADMIN DTO/UI and inclusive
local warning are additive; no authentication, quota, production provider, retention
policy or billing/delivery authority changes. Implementation verification is pending.

## ADR-064 - known metric export loss windows

[ADR-064](../decisions/ADR/064-known-metric-export-loss-windows.md) corrects the
existing request/model collectors' fresh-zero behavior after known export loss. One
finite namespace marker blocks reads atomically while counts continue within their
original expiry. Successful empty collection cannot hide the unknown window. This
preserves API/payload schemas, authorization, provider/learner outcomes and scopes.
Candidate verification is separate from ADR-063 and production release acceptance.

## ADR-065 - isolated database and private-object recovery

[ADR-065](../decisions/ADR/065-isolated-database-object-recovery.md) extends local
recovery preparation with a separate generated PostgreSQL/MinIO rehearsal. It restores
private database/ciphertext backups after stopping the owned source, preserving exact
storage scope and existing integrity/retirement controls. No developer data/volumes,
production provider, retention/erasure policy or production recovery claim changes.
Own local/hosted acceptance is recorded separately from ADR-042's logical evidence.

## ADR-066 - older and diagnostic objective load composition

[ADR-066](../decisions/ADR/066-temporal-diagnostic-load-profile.md) adds a separate
fixed synthetic older-evidence/completed-diagnostic load profile with independent
historical clocks and normal OTP re-authentication. Original/recent commands, schema,
application behavior, secrecy/consent/immutable guards and latency/deadline gates stay
unchanged. Native and own hosted verification are separate requirements; no production,
academic, support-access, real-data or erasure authority is inferred.

## ADR-067: Versioned operational warning configuration

Accepted within delegated engineering discretion; implementation verification pending.
[Record](../decisions/ADR/067-versioned-operational-warning-configuration.md): the
approved configuration route edits existing warning thresholds only, using immutable
versions, ADMIN/recent OTP, exact retry authority and atomic existing staff audit.
It grants no processing/retention/provider/academic or activation authority.


## ADR-068: Fresh owned browser database services

Accepted within delegated local engineering discretion; verification pending.
[Record](../decisions/ADR/068-owned-browser-database-services.md): browser fixtures use
one fresh approved-image PostgreSQL service with bounded tmpfs/memory, loopback/private
credentials and exact returned-ID/label cleanup. Normal services/data and application
contracts/deadlines stay unchanged; no shared developer resource cleanup is authorized.

## ADR-069: Owned synthetic identity verification source

Status: Accepted within delegated engineering discretion; verification pending.
[Record](../decisions/ADR/069-owned-erasure-identity-verification.md): reuse the exact-ID,
distinct-label local fixture for the closed ADR-061 identity test target. Fresh fake
source only; no review data, executor, erasure or application policy change.

## ADR-070: SQL-visible account processing coordination

Status: Accepted within delegated engineering discretion; verification pending.
[Record](../decisions/ADR/070-sql-visible-account-processing-gate.md): preserve existing
account HMAC locks and add shared SQL-visible coordination with a narrow idle-session
model-dispatch gate. This amends ADR-050's blanket inference-lock rule without keeping
row locks/transactions across inference or adding provider/erasure authority.


## ADR-071: Isolated erasure SQL capability bootstrap

[Record](../decisions/ADR/071-isolated-erasure-capability-bootstrap.md): technical
implementation under approved ADR-061. Use registered pre-migration fresh-source proof,
exclusive NOLOGIN/authorizer/maintenance roles and a private versioned SQL control/crypto
namespace. Normal migrations/startup cannot install it; creation/execution remain false.
No new privacy, retention, cloud/provider or real-data permission. Verification and the
complete SQL authorization/closure/preservation/removal workflow remain in progress.


## ADR-072: Private erasure authority and atomic barrier

[Record](../decisions/ADR/072-private-erasure-authority-and-atomic-barrier.md): keep
private authorizer/maintenance credentials separate from ordinary API SQL authority.
Recheck current authenticated ADMIN case ownership in SQL, issue database-clock sealed
plans, and ultimately commit authorization plus permanent closure atomically. No
identity signing/lookup key sharing, client actor/subject/clock input or new privacy
permission. Implementation and complete first-slice verification remain in progress.

## ADR-073: Frozen pre-install source catalog

[Record](../decisions/ADR/073-frozen-preinstall-source-catalog.md): compare a new source's
behavior/privilege catalog against metadata reproduced only from approved migrations in
an independently owned fake-only source. Never approve the live source as its own baseline.
No source rows, credentials, erasure activation or new preservation/retention authority.
Installed-catalog/SQL/payload/hold clearance and full execution remain required work.


## ADR-074: Closed-identity credential dispatch

[Record](../decisions/ADR/074-closed-identity-credential-dispatch.md): coordinate retained
LOGIN bindings before rate/identifier work, reject closed credential mutations and
hold only an idle shared subject gate through bound OTP dispatch. Keep generic responses,
actual provider-only observations, exact newly created challenge cleanup and unchanged
active reuse protection. No closure, hash-based attribution or execution authority.


## ADR-075: Linked credential dispatch gates

[Record](../decisions/ADR/075-linked-credential-dispatch-gates.md): protect authenticated
actor and known recipient with at most two shared subject gates on one owned connection.
Recheck current recent authority and exact binding before LINK/GUARDIAN dispatch, without
opposing account HMAC locks. Exact pending cleanup respects committed closure and consumed
evidence. No new data attribution, retention, erasure activation or public DTO.


## ADR-076: Portable raw catalog Datum octets

[Record](../decisions/ADR/076-portable-catalog-datum-octets.md): preserve the exact
eight-bit values of signed/unsigned raw Datum serialization on the approved ARM64/
AMD64 image variants. Keep all surrounding trees, live code bodies and32 full
metadata categories strict. Versioned v2 artifact/private v5 provenance, independent
fresh reproduction and raw-before-deparser denials remain required. No erasure
activation, live-source baseline learning or new data permission.


## ADR-077: Closed consent consumer guards

[Record](../decisions/ADR/077-closed-consent-consumer-guards.md): coordinate known
guardian recipients before challenge locks; recheck exact binding/closure before
consumption/evidence. Preserve replay and withdrawal. Refuse closed local role
mutations while keeping temporary-disable revocation. No execution or SQL acceptance.


## ADR-078: Installed erasure principal fence

[Record](../decisions/ADR/078-installed-erasure-principal-fence.md): fresh v6 adds
fixed raw-catalog grant/role/ownership expectations to SQL scope identity. Refuse
drift before private readiness/plan/expiry work. Preserve existing temporary-table
behavior; no live ACL learning, public migration, activation or full erasure clearance.
