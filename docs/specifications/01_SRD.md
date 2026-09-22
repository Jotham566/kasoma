# Kasoma Software Requirements Document

| Field | Value |
|---|---|
| Version | 1.1.0 |
| Status | MVP implementation baseline |
| Scope | 12-week MVP |

## 1. System objective

Kasoma shall help Senior 4 learners diagnose weaknesses in selected Mathematics and Physics topics, receive a recommended revision activity, practise with accurate feedback, complete an unseen equivalent reassessment and maintain one mastery profile across web and WhatsApp.

## 2. Actors

| Actor | Capabilities in MVP |
|---|---|
| Learner | Register, consent, diagnose, practise, receive feedback, view progress, link WhatsApp |
| Guardian | Provide recorded consent where the configured age policy requires it |
| Content author | Create/import and edit draft academic items |
| Academic reviewer | Review, approve, return or retire academic items |
| Administrator | Manage roles, configuration, support, audit and operational reporting |
| WhatsApp user | Link an existing learner identity and complete supported short sessions |
| System worker | Run asynchronous grading, embedding, notification and analytics jobs |

## 3. Functional requirements

### 3.1 Identity, consent and profiles

| ID | Requirement | Acceptance condition |
|---|---|---|
| FR-ID-001 | The system shall support registration using an email address or mobile number through a verified one-time code. | An unverified address/number cannot create an active learner session. |
| FR-ID-002 | The system shall create one user identity that may hold multiple verified login identifiers. | Adding a phone to an email-created account does not create a second learner. |
| FR-ID-003 | The system shall record date of birth, consent basis, consent timestamp and policy version. Every learner under 18 requires verifiable parent/guardian consent plus separate learner assent; learners 18+ consent for themselves. | An under-18 learner cannot begin diagnostics, revision or WhatsApp linking until both current guardian consent and learner assent are recorded. |
| FR-ID-004 | The learner shall select Senior 4 and one or both available subjects. | No non-MVP level or subject appears as selectable. |
| FR-ID-005 | The system shall support logout from the current device and revocation of all sessions. | Revoked tokens fail on the next protected request. |
| FR-ID-006 | The learner shall request export or deletion of personal data. | Request is recorded, acknowledged and auditable; processing follows the retention policy. |

### 3.2 Diagnostics

| ID | Requirement | Acceptance condition |
|---|---|---|
| FR-DIAG-001 | A learner shall start one active diagnostic per subject. | Reopening resumes the same incomplete attempt instead of duplicating it. |
| FR-DIAG-002 | A diagnostic shall normally contain 10–15 approved items and may adapt within this limit. | Completion cannot exceed 15 scored items without an explicit configuration change. |
| FR-DIAG-003 | Selection shall cover the configured topic clusters and at least two competency types where inventory permits. | The result contains evidence by topic and competency, not only a total mark. |
| FR-DIAG-004 | The system shall save every answer before navigation proceeds. | Network interruption after acknowledgement does not lose the answer. |
| FR-DIAG-005 | Completion shall create initial mastery estimates, uncertainty and a first recommendation. | The result endpoint returns all three. |

### 3.3 Adaptive revision sessions

| ID | Requirement | Acceptance condition |
|---|---|---|
| FR-REV-001 | The learner shall start a recommended session of 5–10 items. | Session plan records why each initial item was selected. |
| FR-REV-002 | The learner may instead choose an available topic. | Manual choice changes session focus but does not disable mastery updates. |
| FR-REV-003 | Only approved, active items matching the learner's level and subject may be served. | Repository and API tests prevent draft/retired/cross-level items. |
| FR-REV-004 | The service shall avoid immediate item repetition unless explicitly performing a retry. | Previously answered item IDs are excluded using configurable windows. |
| FR-REV-005 | A learner shall resume an interrupted session on another web device. | The next unanswered item and prior responses are preserved. |
| FR-REV-006 | Each recommendation shall expose a learner-readable reason. | UI never shows a recommended session without a reason string. |

### 3.4 Answering, grading and feedback

| ID | Requirement | Acceptance condition |
|---|---|---|
| FR-GRD-001 | The system shall grade single-choice and approved multiple-choice items deterministically. | Result exactly matches the versioned answer key. |
| FR-GRD-002 | Numeric grading shall support units, tolerance, significant-figure policy and accepted equivalent forms defined by the item. | Benchmark cases pass, including boundary values. |
| FR-GRD-003 | Bounded short-text grading shall return score, rubric evidence, confidence and method. | No short-text grade is stored without a rubric version. |
| FR-GRD-004 | Low-confidence automated grading shall not present a definitive unsupported judgment. | It uses the configured fallback: retry, simplified item, or review flag. |
| FR-GRD-005 | Feedback shall identify correct elements, missing elements and a next action where the rubric supports them. | Response is structurally validated before display. |
| FR-GRD-006 | Hints shall be recorded and reduce independence weighting. | Mastery event includes hint count and highest hint level used. |
| FR-GRD-007 | Worked solutions shall be unavailable until an attempt is submitted, except accessibility/admin overrides. | Direct solution endpoint fails before an attempt. |
| FR-GRD-008 | The system shall provide an approved reassessment item after remediation where inventory allows. | Reassessment uses an equivalent-item relationship or same skill/difficulty band, not the same item. |
| FR-GRD-009 | Learners shall flag a question or grade. | Flag includes item/version, attempt, category and optional comment. |

### 3.5 Mastery and progress

| ID | Requirement | Acceptance condition |
|---|---|---|
| FR-MST-001 | Every scored attempt shall create immutable evidence used to update affected skill estimates. | Reprocessing the same attempt is idempotent. |
| FR-MST-002 | Mastery shall include score and confidence/uncertainty. | The API never returns a mastery percentage without confidence metadata. |
| FR-MST-003 | The system shall retain the reason and inputs for each mastery update. | Admin audit can reproduce the calculation from stored evidence and algorithm version. |
| FR-MST-004 | The learner shall view mastery by subject, topic and competency. | UI aggregates only from visible, valid estimates. |
| FR-MST-005 | Progress shall avoid absolute claims when evidence is sparse. | Low-confidence UI uses `Not enough evidence` or `Developing estimate`. |
| FR-MST-006 | The recommendation engine shall consider weakness, importance, prerequisites, recency, uncertainty and repetition. | Unit tests demonstrate every factor changes ranking in the intended direction. |

### 3.6 WhatsApp

| ID | Requirement | Acceptance condition |
|---|---|---|
| FR-WA-001 | A learner shall link WhatsApp using a short-lived one-time code generated after web authentication. | Code is single-use, expires and cannot link to two users. |
| FR-WA-002 | The learner shall start/continue a five-question supported revision session. | Unsupported image/complex response items are excluded. |
| FR-WA-003 | WhatsApp attempts shall use the same grading and mastery services as web. | The same answer produces the same score and mastery evidence. |
| FR-WA-004 | Duplicate/out-of-order webhook delivery shall not duplicate answers or mastery updates. | Idempotency tests pass using provider message IDs. |
| FR-WA-005 | Feedback shall be concise and include a web link when detail is unsuitable for chat. | Message templates meet configured length limits. |
| FR-WA-006 | The learner shall send a stop command to end the session or opt out of proactive messages. | Opt-out state takes effect before the next outbound message. |

### 3.7 Content administration

| ID | Requirement | Acceptance condition |
|---|---|---|
| FR-CNT-001 | Authors shall create and import draft items conforming to the content schema. | Invalid or incomplete records cannot enter review. |
| FR-CNT-002 | Authors cannot approve their own items. | Role and separation-of-duty tests pass. |
| FR-CNT-003 | Reviewers shall approve, return with comments or retire content. | Every transition records actor, time, reason and content version. |
| FR-CNT-004 | Published attempts shall retain the exact item/rubric version used. | Later edits do not change historical scores or displayed audit records. |
| FR-CNT-005 | The system shall block publication without rights status, curriculum mapping, answer/rubric and explanation. | Publish API returns field-specific validation errors. |
| FR-CNT-006 | Admins shall view and triage learner flags. | Status, owner and resolution are auditable. |

### 3.8 Operations and analytics

| ID | Requirement | Acceptance condition |
|---|---|---|
| FR-OPS-001 | The system shall emit versioned analytics events for registration, diagnostic, sessions, attempts, feedback, reassessment and channel linking. | Contract tests validate required properties and prohibit sensitive free text. |
| FR-OPS-002 | Operators shall see service health, grading failures, content flags, AI usage and queue failures. | Alerts fire under simulated threshold breaches. |
| FR-OPS-003 | Critical administrative actions shall be audited. | Audit records are append-only to application actors. |
| FR-OPS-004 | AI and messaging operations shall enforce configurable usage limits. | Requests above the limit fail safely without corrupting the session. |

## 4. Non-functional requirements

| ID | Requirement | Target |
|---|---|---|
| NFR-PERF-001 | API latency | p95 < 500 ms for non-AI reads/writes under agreed MVP load |
| NFR-PERF-002 | Answer feedback | p95 < 1.5 s deterministic; p95 < 8 s AI-assisted |
| NFR-REL-001 | Availability | ≥99.5% monthly during pilot, excluding announced maintenance |
| NFR-REL-002 | Data durability | Managed database backup; RPO ≤24 h, RTO ≤8 h for MVP |
| NFR-SCL-001 | Pilot scale | 2,000 registered, 500 daily active and 50 concurrent learners without redesign |
| NFR-SEC-001 | Transport/storage | TLS in transit; managed encryption at rest; secrets outside source control |
| NFR-SEC-002 | Authorization | Deny by default; server-enforced RBAC; ownership checks on learner data |
| NFR-ACC-001 | Accessibility | WCAG 2.2 AA for core learner journeys where practicable; keyboard and screen-reader support |
| NFR-BW-001 | Low bandwidth | Core question page initial compressed transfer target ≤250 KB excluding question media |
| NFR-COMP-001 | Browser support | Current and previous major Chrome/Edge/Firefox; Android Chrome primary; graceful Safari support |
| NFR-OBS-001 | Traceability | Correlation ID across web/API/worker; structured logs without secrets or answer text by default |
| NFR-MNT-001 | Maintainability | Typed contracts, migrations, automated tests and documented local setup required |
| NFR-LOC-001 | Locale/time | English MVP; UTC storage; Africa/Kampala presentation default |

## 5. Business rules

- BR-001: A content item has one immutable version per publication; edits create a new version.
- BR-002: Only `APPROVED` content versions may be delivered.
- BR-003: A submitted answer cannot be edited; another submission becomes a new attempt.
- BR-004: An attempt affects mastery at most once.
- BR-005: Diagnostic hints and worked solutions are disabled.
- BR-006: Revision hints are permitted and recorded.
- BR-007: Mastery is evidence, not a certified grade.
- BR-008: WhatsApp never creates an unverified learner identity implicitly.
- BR-009: AI-generated candidate content remains `DRAFT` until independent academic approval.
- BR-010: Deleting a learner removes or anonymizes personal linkage while preserving permitted aggregate evidence.

## 6. Out of scope

Any capability listed in the roadmap's explicit exclusions is out of scope. The implementation must not create partial hidden versions of excluded capabilities unless required as a general reusable primitive and recorded in an ADR.
