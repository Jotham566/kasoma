# Kasoma Coding LLM Operating Contract

| Field | Value |
|---|---|
| Version | 1.2.0 |
| Applies to | Any coding model or autonomous engineering agent |

## 1. Mission

Implement the Kasoma MVP exactly as specified, in small testable vertical slices, while preserving academic integrity, child safety, data security and the fixed 12-week scope.

## 2. Read order before coding

1. `00_README_Source_of_Truth.md`
2. Product roadmap and product whitepaper
3. `01_SRD.md`
4. `09_Security_Privacy_and_Safeguarding.md`
5. `02_System_Architecture.md`
6. `03_Domain_and_Data_Model.md`
7. `04_API_and_Integration_Contract.md`
8. `05_Adaptive_Mastery_Engine.md`
9. `06_AI_RAG_and_Grading_Guardrails.md`
10. `07_Content_Operations_and_Academic_QA.md`
11. `08_UX_Flows_and_Accessibility.md`
12. `10_Testing_Acceptance_and_Release.md`
13. `11_Implementation_Backlog.md`
14. `13_ADR_and_Decision_Log.md`
15. `14_Requirements_Traceability_Matrix.md`

Before implementation, produce a short comprehension report listing:

- MVP objective;
- immutable boundaries;
- selected stack;
- current vertical slice;
- applicable requirement IDs;
- unresolved contradictions/questions;
- intended files/components and tests.

Do not write code until contradictions affecting the slice are resolved.

## 3. Non-negotiable behaviours

- Do not add excluded features.
- Do not change the stack, module boundaries, public API or schema without an ADR.
- Do not invent curriculum, answer keys, rubrics, rights or safety policy.
- Do not publish generated content.
- Do not use an LLM where a deterministic grader is specified.
- Do not duplicate assessment/mastery logic in web or WhatsApp adapters.
- Do not weaken tests to make code pass.
- Do not introduce paid/cloud API calls into local startup, automated tests or ordinary CI.
- Do not import a cloud SDK into domain modules; use provider interfaces and adapters.
- Do not log secrets, tokens, direct identifiers or raw learner answers by default.
- Do not perform destructive migrations without explicit human approval and a recovery plan.
- Do not silently fix requirement ambiguity by choosing the easiest behaviour.

## 4. Work protocol for every slice

### Step 1 — Inspect

Read relevant docs and existing code, migrations, tests and ADRs. Check whether the working tree contains unrelated user changes and preserve them.

### Step 2 — Plan

State:

- requirement IDs;
- intended user outcome;
- implementation boundary;
- data/API changes;
- threat/privacy considerations;
- tests;
- excluded adjacent work.

### Step 3 — Contract first

Update or confirm domain types, API schema, database constraints and event schema before UI plumbing. Generate clients from OpenAPI.

### Step 4 — Implement vertically

Deliver the smallest end-to-end path through UI/adapter, API, domain, persistence, events and tests. Avoid broad infrastructure that no active requirement needs.

### Step 5 — Verify

Run targeted tests first, then required broader checks. Confirm authorization, error/offline states, idempotency, observability and acceptance criteria.

### Step 6 — Report

Provide:

- completed requirement IDs;
- files and migrations changed;
- tests run/results;
- screenshots or API examples when useful;
- security/privacy impact;
- remaining risks/open questions;
- next unblocked slice.

## 5. When to stop and ask

Create an `OPEN-QUESTION` and pause the affected work when:

- two authoritative documents conflict;
- curriculum or grading truth is missing;
- rights status is unknown;
- a change affects minors' consent, privacy or safeguarding;
- a requirement needs a new external provider or credential;
- database migration may destroy/irreversibly transform data;
- public API behaviour must break;
- schedule requires removing a release gate;
- the solution would add a deferred feature.

The question must include options, recommendation, trade-offs, requirement IDs and what can continue safely meanwhile.

## 6. Definition of done for code

- requirement acceptance criteria pass;
- domain rules are server enforced;
- migrations are reviewed and reversible/mitigated;
- API/OpenAPI and generated client agree;
- unit, integration and relevant E2E tests pass;
- accessibility and low-bandwidth states are handled;
- analytics and operational signals exist;
- secrets and PII are absent from logs/fixtures;
- documentation/ADR updated;
- no excluded capability was introduced.

## 7. Branch/commit guidance

- One coherent change per branch/PR.
- Reference requirement/story IDs in title and description.
- Separate mechanical refactors from behaviour changes.
- Never commit credentials, production exports, copyrighted source PDFs or generated build artifacts.
- Migrations and contract changes travel with the consuming implementation.

## 8. Initial bootstrap instruction

The first coding session should stop after producing:

1. repository/workspace skeleton;
2. local development environment;
3. CI checks;
4. FastAPI health endpoint and OpenAPI generation;
5. Next.js shell consuming the health endpoint;
6. PostgreSQL/Redis connectivity abstractions;
7. first migration framework;
8. observability/correlation-ID skeleton;
9. test harnesses;
10. ADR-001 through ADR-005 copied/linked into repository docs.

## External model test boundary

A coding agent may run `make eval-local` without approval. It must not run `make eval-gemini-free` unless the explicit opt-in flag is set, the sanitizer passes, and `GEMINI_API_KEY` is available through the local secret environment. It must never place real learner data, production extracts, direct identifiers, guardian/contact data, unpublished proprietary material or restricted content in a Google free-tier request. Failed sanitation is a hard stop, not a warning.
11. fake/local provider profiles demonstrating zero-cost startup and tests.

It must not begin learner features until this foundation is verified.

## 9. Paste-ready initiation prompt

```text
You are the implementation agent for Kasoma. Treat the supplied Kasoma Product Whitepaper, Product Roadmap and Engineering Specification Pack as the authoritative source set. Read every document in the order defined by 12_Coding_LLM_Operating_Contract.md before modifying code.

Begin with the currently assigned backlog slice only. First return a comprehension report covering the MVP objective, immutable scope, architecture, applicable requirement IDs, acceptance tests, affected components, security/privacy considerations, explicit exclusions and any contradictions. Do not code until the report shows no unresolved blocker.

Follow contract-first vertical delivery. Do not invent academic content, expand scope, weaken quality gates, duplicate business logic or change architectural decisions without an ADR approved by the human owner. After implementation, report requirement traceability, files/migrations changed, tests executed, results, known risks and the next unblocked slice.
```
