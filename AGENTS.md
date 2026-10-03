# Kasoma Engineering Instructions

## Product identity

- Product name: Kasoma.
- The MVP must be completed within 12 weeks.
- Build only the approved MVP scope unless the user explicitly changes it.
- The product whitepaper describes the mature north-star product.
- The SRD and specification pack define the approved MVP implementation.

## Authoritative documents

Before planning or implementing work, read:

1. `docs/specifications/00_README_Source_of_Truth.md`
2. `docs/product/PRODUCT_WHITEPAPER.md`
3. `docs/product/PRODUCT_ROADMAP.md`
4. `docs/specifications/01_SRD.md`
5. The specification documents relevant to the task.

Use this authority order when documents disagree:

1. Approved ADRs
2. Security, privacy and safeguarding requirements
3. API contract and database constraints
4. SRD
5. QA acceptance and release specification
6. System architecture
7. Adaptive engine and AI specifications
8. UX and content-operation specifications
9. Product roadmap
10. Product whitepaper

The whitepaper is the product north star, but it does not automatically expand
the MVP scope.

## Mandatory workflow

Before changing code:

1. Identify the applicable requirement IDs.
2. Read the relevant specifications and accepted ADRs.
3. Inspect the current implementation and tests.
4. State assumptions where the documents do not decide something.
5. Do not silently invent requirements.
6. Implement the smallest complete change satisfying the requirement.
7. Add or update tests.
8. Update `CHANGELOG.md`, the current sprint, requirements traceability and relevant
   API/runbook/verification documentation alongside each implementation change.
9. Run the required quality checks.
10. Report the requirement IDs satisfied and any remaining gaps.

If documents conflict, stop and report the conflict. Do not choose silently.

## Scope and drift control

- Do not add features merely because they appear in the mature whitepaper.
- Do not alter accepted architecture without creating or updating an ADR.
- Do not replace approved technology without documenting the reason.
- Do not weaken privacy, safeguarding, academic or AI controls.
- Do not mark work complete unless its acceptance criteria pass.
- Do not use production or real learner data during development.

## AI development

- Automated tests use `FakeModelProvider`.
- Interactive local inference uses host-native Ollama.
- The supported machine is an M4 Mac Mini with 16 GB unified memory.
- The normal local model class is quantized 4B–8B.
- Gemini free-tier testing is manual and opt-in.
- Never send real learner, guardian, confidential or restricted data to
  Google AI Studio.
- Follow:
  - `docs/specifications/06_AI_RAG_and_Grading_Guardrails.md`
  - `docs/specifications/18_Ollama_and_Gemini_Evaluation_Profile.md`

## Definition of done

A task is complete only when:

- applicable acceptance criteria pass;
- tests have been added or updated;
- linting, formatting and type checks pass;
- migrations work from a clean database when applicable;
- API/schema changes are reflected in generated contracts;
- documentation and traceability are updated;
- no secrets or personal data are committed;
- the implementation remains within the approved MVP scope.

## Repository stage

E0–E4 foundation, identity/consent, content review and deterministic assessment
and the E5 synthetic diagnostic/mastery slice are merged. Synthetic recommended
practice, reviewed hints, unseen reassessment and E6 progress/history are merged.
Learner flags, independent staff triage and exact-set multiple-choice assessment are
merged. Data-request intake and administrator review are merged. Owned JSON exports,
completion evidence and 24-hour copy expiry are merged. A non-destructive administrator
deletion-impact preview is merged. Specific-record legal holds for consent, attempts,
content flags and data requests are merged. Bounded synthetic JSON draft imports, source
locators and atomic worker processing are verified. Deletion/anonymization, remaining
hold coverage, large-history fulfillment and accountability-retention processors remain pending.
Academic calibration and production deployment remain pending. See
`docs/implementation/CURRENT_SPRINT.md` and maintain the evidence register at
`docs/implementation/REQUIREMENTS_TRACEABILITY.md`. Accepted decisions remain
in `docs/specifications/13_ADR_and_Decision_Log.md`; new ADRs belong in
`docs/decisions/ADR/`. Do not claim application acceptance from documentation checks.

For documentation-only tasks, verify links and whitespace; application tests,
migrations and generated contracts apply when those components change.

## Standard commands

Prefer repository commands over improvised alternatives:

- `make setup`
- `make dev`
- `make test`
- `make lint`
- `make migrate`
- `make seed`
- `make openapi`
- `make e2e`
- `make security`
- `make eval-local`
- `make eval-gemini-free`

If a required command does not exist, implement it according to the repository
bootstrap specification rather than silently substituting an undocumented
workflow.

## Task completion report

At the end of every coding task, report:

- requirements addressed;
- files changed;
- tests and checks executed;
- results;
- architectural decisions made;
- unresolved risks or specification gaps;
- recommended next task.
