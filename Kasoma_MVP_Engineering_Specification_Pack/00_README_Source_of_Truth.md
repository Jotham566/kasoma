# Kasoma MVP Engineering Specification Pack

| Field | Value |
|---|---|
| Pack version | 1.3.0 |
| Date | 22 September 2026 |
| Delivery horizon | 12-week MVP |
| Product | Kasoma |
| Status | Implementation baseline |

## Purpose

This pack gives human engineers and coding LLMs enough product, technical and quality context to implement Kasoma's MVP without inventing scope or silently changing product behaviour.

## Authority order

When documents conflict, use this order:

1. Approved Architecture Decision Records (ADRs)
2. Security, privacy and safeguarding requirements
3. API contract and database constraints
4. Software Requirements Document (SRD)
5. QA acceptance and release specification
6. System architecture
7. Adaptive engine and AI specifications
8. UX and content-operation specifications
9. Product roadmap
10. Product whitepaper

The whitepaper describes the mature north star. It does **not** authorize post-MVP features. The roadmap defines what belongs in the 12-week MVP. The SRD turns that scope into testable behaviour.

## Documents

| File | Purpose |
|---|---|
| `01_Software_Requirements_Document.md` | Functional and non-functional requirements with acceptance criteria |
| `02_System_Architecture.md` | Chosen stack, boundaries, runtime topology and cross-cutting design |
| `03_Domain_and_Data_Model.md` | Entities, states, invariants, database model and event vocabulary |
| `04_API_and_Integration_Contract.md` | REST conventions, endpoints, payloads, errors and WhatsApp integration |
| `05_Adaptive_Mastery_Engine.md` | Diagnostic, mastery update, recommendation and reassessment algorithms |
| `06_AI_RAG_and_Grading_Guardrails.md` | Permitted AI use, retrieval, grading, prompts, confidence and evaluation |
| `07_Content_Operations_and_Academic_QA.md` | Content schema, rights, workflow and publication rules |
| `08_UX_Flows_and_Accessibility.md` | Screen flows, states, low-bandwidth behaviour and accessibility |
| `09_Security_Privacy_and_Safeguarding.md` | Threat controls, minor safety, consent, retention and incident handling |
| `10_Testing_Acceptance_and_Release.md` | Test strategy, traceability, quality gates and release criteria |
| `11_Implementation_Backlog.md` | Ordered epics, vertical slices, dependencies and 12-week delivery plan |
| `12_Coding_LLM_Operating_Contract.md` | Mandatory working protocol for an autonomous coding model |
| `13_ADR_and_Decision_Log.md` | Initial architectural decisions and change-control template |
| `14_Requirements_Traceability_Matrix.md` | Links requirements to components, APIs and tests |
| `15_Repository_Bootstrap_and_Environment.md` | Local setup, configuration, CI and initial repository contract |
| `16_Production_Pilot_Decisions.md` | Resolved academic, consent, provider, retention, pilot, grading and hosting decisions |
| `17_Local_Development_and_Provider_Portability.md` | Zero-cost local AI workflow, provider adapters and production-selection gate |
| `18_Ollama_and_Gemini_Evaluation_Profile.md` | M4 Mac Mini Ollama profile and privacy-safe Gemini free-tier evaluation lane |

## Immutable MVP boundaries

- Senior 4 only.
- Mathematics and Physics only.
- Three topic clusters per subject, chosen and frozen in Week 1.
- 250–400 approved items; release minimum is 250 with adequate coverage.
- Web is the full learner experience.
- WhatsApp supports linked-account short practice, not feature parity.
- Supported responses: single choice, multiple choice where academically valid, numeric and bounded short text.
- Rules-based mastery engine v1.
- Deterministic grading first; bounded model assistance only where specified.
- No teacher/parent portals, simulations, Snap & Learn, native mobile apps, full Exam Mode, fine-tuning, advanced knowledge tracing or unreviewed generated questions.

## Change protocol

The implementation agent must not reinterpret requirements to make them easier. If a requirement is contradictory, missing or infeasible:

1. stop work on the affected slice;
2. create an `OPEN-QUESTION` or ADR proposal;
3. describe options, trade-offs and affected requirement IDs;
4. continue only on unaffected work;
5. obtain human approval before changing scope, security, data or learner-visible behaviour.

## Definition of implementation ready

A work item is ready only when it has:

- linked requirement IDs;
- expected learner/admin behaviour;
- API/data impact;
- acceptance tests;
- security/privacy considerations;
- analytics events;
- explicit exclusions.
