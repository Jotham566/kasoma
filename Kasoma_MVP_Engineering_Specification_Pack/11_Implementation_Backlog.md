# Kasoma 12-Week Implementation Backlog

| Field | Value |
|---|---|
| Version | 1.1.0 |
| Delivery style | Vertical slices with weekly demonstrable software |

## 1. Delivery rules

- Each story links requirement IDs and acceptance tests.
- Complete one thin end-to-end path before broadening.
- Content, engineering, AI and pilot work run concurrently.
- No feature is done without telemetry, errors, authorization and tests.
- If schedule slips, reduce topic/item breadth or short-text formats—not safety or academic quality.

## 2. Epics

| Epic | Outcome | Principal requirements |
|---|---|---|
| E0 Foundation | reproducible repo, environments and CI | NFR-MNT-001, NFR-OBS-001 |
| E1 Identity/consent | verified learner with safe access | FR-ID-* |
| E2 Curriculum/content | approved versioned content | FR-CNT-* |
| E3 Assessment | diagnostic and revision session | FR-DIAG-*, FR-REV-* |
| E4 Grading/feedback | trusted marking and remediation | FR-GRD-* |
| E5 Mastery/recommendation | explainable adaptive loop | FR-MST-* |
| E6 Progress UX | learner can understand state/action | FR-MST-004/005 |
| E7 WhatsApp | shared short-practice channel | FR-WA-* |
| E8 Operations | monitoring, flags, support and data requests | FR-OPS-*, FR-ID-006 |
| E9 Hardening/pilot | safe evidence-backed release | all release gates |

## 3. Weekly plan

### Week 1 — Foundation and frozen contracts

- monorepo, local containers, CI and environments;
- code owners, branch/PR rules and ADR folder;
- OpenAPI skeleton and generated client;
- database migration baseline;
- observability skeleton;
- load the six frozen clusters: Mathematics—Algebra and Functions; Geometry, Trigonometry and Measurement; Statistics and Probability. Physics—Mechanics and Energy; Waves, Light and Sound; Electricity and Magnetism;
- map each cluster to exact NCDC learning outcomes before item approval;
- first 30–40 reviewed items in staging.

**Demo:** health check, web/API build, first approved fixture rendered from database.

### Week 2 — Identity and content workflow

- OTP request/verify, tokens and learner profile;
- under-18 guardian-consent plus learner-assent gate;
- email OTP baseline and Africa's Talking SMS delivery spike with budget/rate-limit controls;
- RBAC and audit foundation;
- author create/edit/submit and reviewer approve/return;
- rights/publication validators;
- cumulative 60 approved items.

**Demo:** verified learner plus independently approved item; access-control tests.

### Week 3 — Assessment vertical slice

- create session, assign approved item, submit choice/numeric answer;
- idempotency and deterministic grade;
- basic learner question UI and feedback;
- attempt/grade/outbox model;
- cumulative 100 items.

**Demo:** complete one question end-to-end with stored grade and event.

### Week 4 — Diagnostic

- diagnostic planner and 10–15-item constraint;
- interruption/resume;
- initial mastery evidence and estimate;
- diagnostic results UI;
- analytics events;
- cumulative 125 items.

**Demo:** full subject diagnostic yielding initial estimates.

### Week 5 — Adaptive revision

- recommendation ranking and explanation;
- 5–10-item revision sessions;
- hints, authored remediation, worked solution gating;
- equivalent reassessment;
- progress page v1;
- cumulative 150 items.

**Gate:** complete Diagnose → Recommend → Practice → Explain → Reassess → Update loop.

### Week 6 — Short-text grading and content tooling

- rubric-grading gateway and schema validation;
- dual-pass agreement, calibrated ≥90% auto-score gate, fallback and feature flag;
- frozen benchmark execution;
- bulk import validation and content flags;
- cumulative 190 items.

**Demo:** supported short response plus safe low-confidence case.

### Week 7 — WhatsApp foundation

- provider webhook verification/idempotency;
- link-code flow and conversation state;
- START/CONTINUE/HELP/STOP;
- supported item rendering/answer parsing;
- shared assessment services;
- cumulative 220 items.

**Demo:** linked WhatsApp user completes one graded item reflected on web.

### Week 8 — Feature complete / closed alpha

- five-question WhatsApp session;
- learner history and progress polish;
- offline/retry states;
- admin flag triage and operational dashboards;
- accessibility pass;
- cumulative ≥250 items;
- 30–50 learner closed alpha.

**Gate:** all MVP requirements implemented behind production-ready controls.

### Week 9 — Quality and performance

- defect fixes from alpha;
- grading regression and mastery replay;
- load/resilience/security testing;
- cost controls and caching;
- content balance and second-pass review;
- target 300 items if quality capacity permits.

### Week 10 — Real-world beta

- 100–200 learner beta;
- baseline collection and support operation;
- production monitoring and content incident flow;
- daily defect/academic triage.

### Week 11 — Release candidate

- unseen/delayed reassessment analysis;
- calibration and subgroup review;
- backup restore and incident tabletop;
- content/code freeze except blockers;
- support and runbook sign-off.

### Week 12 — MVP release

- final release checklist;
- staged production exposure;
- launch monitoring;
- known limitations and evidence report;
- post-MVP decision review.

## 4. Critical dependency chain

```text
Topic/schema freeze
  -> approved content
  -> assessment delivery
  -> grading
  -> mastery evidence
  -> recommendation
  -> remediation/reassessment
  -> progress and WhatsApp reuse
```

WhatsApp must reuse completed domain APIs; it must not create a second assessment implementation.

## 5. Story template

```markdown
### [ID] Imperative title
Requirements: FR-...
User outcome:
In scope:
Out of scope:
API/data changes:
Security/privacy:
Analytics:
Acceptance tests:
Dependencies:
Definition of done:
```

## 6. Stop-the-line conditions

Pause affected delivery for:

- unclear content rights;
- disagreement on correct answer/rubric;
- cross-user access or consent bypass;
- duplicate/corrupt mastery evidence;
- model grading below gate;
- requirements conflict requiring product choice.

Record the issue; do not hide it behind a fallback that changes learner behaviour.
