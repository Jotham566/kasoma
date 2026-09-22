# Kasoma Requirements Traceability Matrix

| Field | Value |
|---|---|
| Version | 1.0.0 |
| Purpose | Prevent requirements from disappearing between specification, code and tests |

## Traceability matrix

| Requirement group | Owning module | Primary API/UI | Mandatory test evidence | Release owner |
|---|---|---|---|---|
| FR-ID-001–002 | Identity | `/auth/otp/*`, registration | OTP, deduplication, enumeration, rate-limit integration tests | Technical/Security |
| FR-ID-003 | Identity | consent flow, `/me/consents` | consent block and policy-version E2E | Safeguarding |
| FR-ID-004–006 | Identity | profile/settings | subject constraints, revocation, data-request tests | Product/Privacy |
| FR-DIAG-001–005 | Assessment/Mastery | diagnostic flow | planner limits, coverage, resume, result E2E | Product/Academic |
| FR-REV-001–006 | Assessment/Mastery | revision flow | selection constraints, resume, reason tests | Product/Academic |
| FR-GRD-001–002 | Grading | attempt submission | frozen deterministic benchmark | Academic/QA |
| FR-GRD-003–005 | Grading/AI | pending/feedback UI | expert benchmark, schema and fallback tests | Academic/AI |
| FR-GRD-006–009 | Assessment/Content | hint/solution/flag | state, weighting, access and audit tests | Product/Academic |
| FR-MST-001–003 | Mastery | event worker/admin audit | idempotency, replay and reproduction tests | Data/QA |
| FR-MST-004–006 | Mastery/Web | progress/recommendation | display-state E2E and ranking property tests | Product/Data |
| FR-WA-001–006 | Messaging | link/webhook/chat | signature, duplicate, parity, opt-out tests | Technical/Product |
| FR-CNT-001–006 | Content | admin content/review | workflow, rights, immutability, self-review tests | Academic |
| FR-OPS-001–004 | Analytics/Admin | dashboards/events/config | schema, alert, audit and limit tests | Operations/Security |
| NFR-PERF-* | Platform | all | staged load test report | Technical |
| NFR-REL-* | Platform | deploy/backup | availability monitoring and restore drill | Operations |
| NFR-SEC-* | All | all | threat-model checklist and security suite | Security |
| NFR-ACC-* | Web | core journeys | automated scan + manual keyboard/screen reader smoke | Design/QA |
| NFR-BW-* | Web | learner question flow | bundle/network profile | Frontend |
| NFR-OBS-* | Platform | logs/traces/dashboards | correlation/redaction tests | Operations |

## Story traceability rule

Every story and pull request must list:

```text
Requirements implemented:
Requirements partially affected:
Acceptance tests added/updated:
Security/privacy controls:
Analytics events:
Documentation/ADR:
```

No requirement is marked complete because a UI exists. Completion requires domain enforcement and passing evidence.

## MVP release evidence register

Maintain during delivery:

| Requirement ID | Code component | Test ID/link | Evidence/result | Owner | Status |
|---|---|---|---|---|---|
| Example: FR-GRD-001 | `grading.choice` | `test_choice_grading.py` | CI run / benchmark | QA | Not started |

The implementation agent may generate this register from test metadata, but owners must review it before release.

## Deferred-feature contamination check

At the end of each sprint, search code, migrations, navigation and feature flags for:

- teacher/parent portals;
- simulations;
- photo/handwriting solving;
- voice;
- full Exam Mode;
- native apps;
- advanced knowledge tracing;
- fine-tuning pipelines;
- learner-facing unreviewed generation.

Any occurrence must be justified as a generic primitive or removed. A disabled half-built feature still creates maintenance and drift risk.
