# Kasoma Testing, Acceptance and Release Specification

| Field | Value |
|---|---|
| Version | 1.2.0 |
| Quality model | Risk-based, requirement-traceable |

## 1. Test layers

| Layer | Focus |
|---|---|
| Unit | domain rules, formulas, validators, permissions |
| Property-based | mastery bounds/monotonicity, numeric grading, idempotency |
| Component | UI states and accessibility |
| Repository integration | constraints, transactions, migrations |
| API integration | auth, ownership, state transitions, errors |
| Contract | OpenAPI client, analytics events, model schemas, WhatsApp payloads |
| E2E | learner/admin journeys across deployed stack |
| Academic benchmark | grading, content and recommendation validity |
| Performance | pilot concurrency, answer feedback and imports |
| Security | authorization, abuse, injection, secrets and dependencies |
| Resilience | provider timeouts, duplicate webhooks, worker retry/dead letter |

## 2. Minimum automated gates

Every pull request:

- formatting/lint;
- TypeScript and Python type checks;
- unit/property tests;
- migration validation;
- API schema generation/diff;
- security/dependency/secret scans;
- affected contract tests.

Main/staging:

- integration tests with PostgreSQL/Redis;
- full E2E critical paths;
- accessibility scan plus manual keyboard smoke test;
- deterministic grading benchmark;
- AI grading benchmark when prompts/model/config change;
- container build and vulnerability scan.

Normal PR/main CI uses deterministic provider fakes and makes no external model calls. Local-model benchmark runs use host-native Ollama on the M4 Mac Mini. Gemini free-tier compatibility/quality runs are manual, opt-in and execute only after the benchmark sanitizer proves the fixture contains no personal, learner, confidential or restricted data. They never gate ordinary CI. Paid hosted-model tests remain in a separately approved, budget-capped `external-eval` workflow.

## 3. Critical acceptance suites

### Identity/consent

- OTP expires, is single-use and rate-limited.
- Unknown/existing identifier has indistinguishable request response.
- learner cannot bypass required consent;
- token rotation/revocation works;
- learner A cannot access learner B resources.

### Content

- draft/retired content never served;
- author cannot self-approve;
- approved version immutable;
- missing rights/rubric/mapping blocks publication;
- historical attempt keeps exact version.

### Attempts/grading

- duplicate submission yields one attempt/grade/evidence;
- numeric tolerance/unit boundaries pass;
- answer keys never appear before submission;
- low-confidence model grade follows fallback;
- grade override is additive/audited;
- solution blocked before attempt.

### Mastery/recommendation

- estimate remains within `[0,1]`;
- correct independent evidence raises estimate more than hinted evidence;
- older evidence contributes less;
- sparse evidence shows uncertainty;
- prerequisite weakness redirects recommendation;
- replay produces identical output for identical versioned inputs.

### WhatsApp

- invalid signatures rejected;
- duplicate/out-of-order messages do not duplicate progress;
- expired/reused link code rejected;
- opt-out prevents proactive messages;
- WhatsApp and web produce equal grade/mastery for same attempt.

## 4. Academic benchmark gates

- Objective/numeric exact score accuracy ≥95%.
- Supported short-text expert agreement ≥85% within approved tolerance.
- All six topic clusters represented.
- Critical factual/rubric defects: zero open.
- Recommendation sample reviewed and accepted by subject reviewers.
- Equivalent items independently reviewed for transfer validity.

Benchmark changes require academic approval and versioning. Never modify expected scores solely to make the system pass.

## 5. Performance test profile

MVP target profile:

- 50 concurrent active learners;
- burst of 20 answer submissions/second for a short period;
- 500 daily active learners;
- 250–400 content items and representative mastery evidence;
- delayed/failed model provider and WhatsApp provider scenarios.

Targets follow NFRs in the SRD. Tests report p50/p95/p99, errors and resource use. AI provider latency is reported separately.

## 6. Test data

- Use synthetic identities and original fixture questions.
- No production PII in test/CI.
- Seeded learner trajectories cover strong, weak, sparse, inconsistent and hint-dependent cases.
- Fixtures include all response types, difficulty bands, statuses and channel constraints.
- Clock and randomness are injectable for deterministic tests.

## 7. Defect severity

| Severity | Examples | Release effect |
|---|---|---|
| S1 | data exposure, safeguarding risk, wrong answer key at scale, mastery corruption | block/rollback |
| S2 | broken critical journey, major grading error, WhatsApp duplicates | block unless fixed |
| S3 | limited noncritical defect/workaround | explicit acceptance |
| S4 | cosmetic/minor copy | backlog |

## 8. Release candidate checklist

- All MVP requirement IDs have test/evidence or approved exception.
- Zero open S1/S2 defects.
- Minimum approved content and balanced coverage met.
- Academic benchmark and model evaluation pass.
- Migrations tested forward and rollback/mitigation documented.
- Security scans and manual authorization smoke test pass.
- Monitoring, alerts, dashboards and runbooks active.
- Backup restoration tested.
- Feature flags and kill switches verified.
- WhatsApp templates/webhook configuration verified.
- Support, safeguarding and content-correction rehearsals complete.
- Known limitations published internally.
- Product, technical, academic and safeguarding owners sign off.

## 9. Release and rollback

- Deploy staging, run smoke/E2E, then production with gradual exposure.
- Separate code deployment from feature enablement.
- Roll back code when safe; use feature flags to disable AI grading/WhatsApp/new engine version.
- Never roll back a destructive migration without a tested data plan.
- If content is defective, withdraw the item independently of code deploy.
- If mastery evidence is corrupted, stop processing, identify affected evidence and replay from immutable grades after correction.

## 10. Post-release validation

Within 24 hours review errors, feedback latency, duplicate rate, grade fallbacks, content flags, AI cost and mastery lag. Within the pilot window review diagnostic completion, recommended-session completion, unseen reassessment gain and learner/teacher feedback.
