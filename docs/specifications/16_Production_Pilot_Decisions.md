# Kasoma Production-Pilot Decision Baseline

| Field | Value |
|---|---|
| Version | 1.2.0 |
| Status | Approved implementation defaults |
| Date | 22 September 2026 |
| Supersedes | P-001 through P-008 as open decisions |

## Purpose

This document records the decisions required to start implementation and prepare a safe production pilot. The decisions deliberately favour child safety, academic traceability and reversible delivery over convenience.

## Decision summary

| Area | Approved decision |
|---|---|
| Academic scope | Mathematics: Algebra and Functions; Geometry, Trigonometry and Measurement; Statistics and Probability. Physics: Mechanics and Energy; Waves, Light and Sound; Electricity and Magnetism. |
| Child consent | Under 18: verifiable parent/guardian consent **and** learner assent. Age 18+: learner consent. School approval alone is insufficient. |
| OTP | AWS SES email OTP baseline; Africa's Talking SMS OTP after Uganda delivery/privacy/commercial gate. Either verified route may authenticate. |
| Worker/queue | Celery 5.6.x with Redis transport, transactional outbox and idempotent jobs. |
| Managed Redis | Local Redis during development. Production Redis-compatible service selected with the cloud provider before beta. |
| Retention/governance | Explicit retention schedule; PDPO obligations, DPIA, processor register/contracts and cross-border assessment before real learner data. |
| Pilot | Closed alpha: 30–50 learners. Beta: 100–200 learners across 2–4 schools. Consent/assent, baseline, unseen reassessment, withdrawal and incident monitoring required. |
| Short-text grading | Dual independent rubric passes must agree; auto-score band must demonstrate ≥90% exact expert agreement. Otherwise low-confidence fallback. |
| Hosting | Cloud-neutral during development. AWS, Azure or GCP production provider/region selected by end of Week 8; 35-day PITR; RPO ≤24 h; RTO ≤8 h. |

## 1. Academic-scope rationale and implementation rule

The clusters maximize prerequisite coverage, scenario-based assessment and reuse across the accumulated O-Level curriculum. They are broad enough to test concept, interpretation, application and problem-solving while remaining feasible for 250–400 approved items.

The labels are product clusters, not a replacement for NCDC terminology. Before an item may be approved, academic reviewers must map it to the exact current NCDC learning outcome and syllabus reference. If a cluster contains insufficient valid content, reduce subtopic breadth; do not substitute another subject or add a seventh cluster without a roadmap change.

Recommended initial content allocation:

| Cluster | Minimum approved items | Target |
|---|---:|---:|
| Algebra and Functions | 40 | 55–65 |
| Geometry, Trigonometry and Measurement | 40 | 55–65 |
| Statistics and Probability | 30 | 40–50 |
| Mechanics and Energy | 40 | 55–65 |
| Waves, Light and Sound | 40 | 55–65 |
| Electricity and Magnetism | 40 | 55–65 |

Release requires at least 250 balanced items, not merely the sum of topic totals. The content matrix must also cover competency, difficulty and supported response formats.

## 2. Consent, assent and age assurance

The operational rule is intentionally conservative because Kasoma targets secondary-school learners and processes longitudinal learning profiles.

Implementation:

1. collect date of birth, not an easily bypassed `I am over 18` checkbox;
2. if under 18, collect a guardian's name, relationship and verified email or phone;
3. present guardian consent and learner assent separately in plain language;
4. record policy version, actor, verification method, timestamp and withdrawal state;
5. prohibit diagnostics, revision and WhatsApp linking until both are active;
6. allow withdrawal without school penalty;
7. re-consent after a material change in purposes, AI use, sharing or policy;
8. do not use behavioural profiling for advertising.

Legal/privacy approval remains a launch gate. This decision should be checked against Uganda's Data Protection and Privacy Act, 2019, its Regulations, the Children Act and current PDPO guidance before enrollment.

## 3. OTP and identity delivery

### Email

- AWS SES sends transactional OTP messages from a dedicated authenticated domain.
- OTPs contain no learning data and expire after 10 minutes.
- Configure SPF, DKIM and DMARC; monitor bounces/complaints.

### SMS

- Africa's Talking is the sole MVP SMS adapter.
- Production enablement requires test delivery to MTN Uganda and Airtel Uganda numbers.
- Gate: ≥95% delivered within two minutes across a representative test, no unexplained sensitive-data routing, approved sender identity/terms and acceptable unit economics.
- Failed SMS offers email OTP; do not silently send repeated billable messages.

### Abuse and budget

- maximum five verify attempts per OTP;
- resend cooldown at least 60 seconds;
- per-identifier, IP and device limits;
- daily anomaly alert and monthly SMS budget kill switch;
- generic responses prevent account enumeration.

## 4. Queue and background execution

Use Celery 5.6.x with Redis transport. Required patterns:

- transactional outbox is the authoritative job trigger;
- `acks_late` only for safely idempotent tasks;
- unique domain idempotency keys;
- bounded exponential retry for transient errors;
- hard/soft time limits;
- dead-letter/failure table visible to operators;
- separate queues for grading, messaging, imports and low-priority analytics;
- PostgreSQL stores job-relevant truth; Redis loss must not lose attempts or grades.

Pin the exact patch version in the lockfile and upgrade only through dependency review.

## 5. Retention and data governance

The controlling schedule is in the security specification. Key periods are:

- access logs: 90 days;
- raw provider webhook payloads: no more than 30 days;
- AI debug payloads: off by default; if approved, delete within 30 days;
- security audit logs: 12 months;
- support/content flags with learner data: 24 months after resolution;
- inactive learner accounts: review after 24 months, notify where possible, 30-day grace, then delete identifiers and anonymize permitted evidence;
- consent/assent, material audit and data-request evidence: six years after closure/completion;
- operational backups: 35 days.

Legal hold suspends deletion only for the specific records and period required. Aggregation is not automatically anonymization; re-identification risk must be assessed.

## 6. Pilot protocol

### Stage A — Closed alpha

- 30–50 Senior 4 learners;
- at least two schools where practical;
- supervised web sessions plus controlled WhatsApp linking;
- goal: usability, content defects, grading safety and operational readiness;
- no marketing claims about learning effectiveness.

### Stage B — Beta/outcomes evaluation

- 100–200 learners across 2–4 schools;
- baseline assessment before meaningful exposure;
- minimum two weeks of use inside the 12-week delivery window;
- unseen equivalent reassessment after intervention;
- seven-day delayed check where scheduling permits; 21-day follow-up may complete after MVP release;
- prespecified primary outcome: change in unseen equivalent-item performance;
- secondary outcomes: diagnostic completion, misconception resolution, calibration, return rate, support burden and cost per completed session.

### Participant protection

- school agreement plus individual consent/assent;
- participation voluntary and not tied to grades or school benefits;
- reasonable non-coercive reimbursement only for direct participation costs, if any;
- withdrawal process and contact;
- incident and safeguarding response ready before enrollment;
- accessibility/accommodation plan;
- no public learner rankings;
- results reported in aggregate with small-cell suppression.

If findings will be published, generalized as research or used beyond normal product improvement, obtain an independent research-ethics determination/approval before recruitment. Register hypotheses and analysis before inspecting outcome results.

## 7. Short-text grading release rule

The model's own confidence number is not trusted as calibration. A grade is automatically returned only if:

- two independent rubric evaluations agree on every criterion and total;
- all structural and evidence validators pass;
- no injection/safety/out-of-domain detector triggers;
- the relevant subject/topic/response-length confidence band has ≥90% exact agreement with expert scores on held-out benchmark data;
- no subgroup shows a material harmful error pattern;
- the feature flag enables that band.

All other responses use `LOW_CONFIDENCE`, with neutral wording and an objective equivalent item or human audit. Sample at least 10% of automatically returned short-text grades for blinded expert audit during the beta; automatically disable a band if rolling exact agreement falls below 90% or a critical error occurs.

## 8. Hosting and recovery

- Develop and test using Dockerized PostgreSQL/pgvector, Redis, MinIO and provider fakes; no cloud account is required.
- Select AWS, Azure or GCP by the end of Week 8 using cost, African/nearby region availability, latency from Uganda, security, processor terms, backup/recovery, AI-model availability and team-operability evidence.
- Keep API, web runtime, PostgreSQL, Redis-compatible service and object storage in one primary region unless an approved architecture/security reason requires otherwise.
- Use availability zones where the selected GA service/SKU supports them.
- Keep private networking/service endpoints where feasible for the pilot budget.
- Encrypt in transit and at rest; keys/secrets remain in managed secret storage.
- PostgreSQL PITR retention: 35 days.
- Maintain an encrypted recovery copy in an approved paired/secondary region.
- Run a restore exercise before beta and at least quarterly thereafter.
- If an AI deployment is unavailable in-region, send only minimized pseudonymous task content to an approved alternate region after updating the DPIA and processor/transfer records.

Any production region outside Uganda creates a cross-border transfer. Production use therefore depends on documented legal basis, contractual safeguards, processor review and disclosure to guardians/learners.

## 9. Remaining launch gates—not open product decisions

The decisions above are closed. The following are execution evidence that must still be produced:

- signed academic mapping approval for the six clusters;
- approved guardian consent, learner assent and privacy notices;
- PDPO registration/compliance evidence as applicable;
- completed DPIA and cross-border assessment;
- executed provider/processor agreements;
- SMS delivery and cost test report;
- frozen pilot protocol and school agreements;
- expert-scored grading benchmark and calibration report;
- approved production-cloud ADR, service-availability/cost confirmation and successful restore test.

Failure to meet a gate blocks the affected production capability; it does not silently reopen scope.

## References used for the decisions

- Uganda Data Protection and Privacy Office: [PDPO](https://pdpo.go.ug/)
- Uganda National Curriculum Development Centre: [NCDC curriculum resources](https://ncdc.go.ug/resource/)
- Microsoft: [Azure regions list](https://learn.microsoft.com/en-us/azure/reliability/regions-list)
- Celery: [official Celery documentation](https://docs.celeryq.dev/)
- AWS: [Amazon SES documentation](https://docs.aws.amazon.com/ses/)
- Africa's Talking: [SMS product](https://africastalking.com/sms)

Provider availability, prices and legal guidance can change. Recheck them at procurement/deployment; do not alter the functional decision without an ADR.

Google AI Studio free-tier evaluation is development evidence only and is not an approved production processor or production-model decision. A production choice still requires the Week 8 privacy, legal, regional, quality, reliability and cost review.
