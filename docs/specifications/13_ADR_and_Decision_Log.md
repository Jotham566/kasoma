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
