# E9 synthetic provider fault isolation

Requirements: FR-GRD-003/004/005, FR-MST-001/004/005, NFR-SEC-002, NFR-MNT-001;
supports NFR-REL-001 and the provider-failure test profile without proving availability.
Status: corrected focused cases and local quality checks pass; full integration and
hosted acceptance pending.

## Approved boundary and test design

[ADR-050](../decisions/ADR/050-short-text-pending-and-eligibility.md) requires model
work outside database locks and neutral outcomes without mastery on failure.
[ADR-054](../decisions/ADR/054-bounded-worker-model-usage.md) requires unchanged
provider behavior and minimized observations. No architectural or runtime change is
proposed here: add regression coverage through the existing disabled synthetic flow.

`make test-provider-fault-isolation` uses an isolated migrated test schema, ordinary
authorized API paths and FakeModelProvider. An event holds one authorized fake call
while 50 web-read tasks are scheduled across a pool of up to 50 reader threads.
These are one learner's owned pending poll, progress and session-history reads, not
50 distinct active learners or a measured peak of 50 simultaneous HTTP requests.
All reads must finish while the provider remains held. Pending polling is stable,
progress has no provisional mastery evidence and history shows the saved answer.

After release, three cases exercise timeout, unavailable-provider exception and
ordinary fake fallback. Each must dispatch exactly once, persist LOW_CONFIDENCE,
preserve exact-key submission replay and never create a definitive grade, mastery
evidence, publication or audit assignment. Neither response nor logs may contain the
synthetic diagnostic canary. A second processor pass must not redispatch terminal work.
The original review-stack settings and learner-delivery gate remain untouched.

The eight-second read wait is a finite deadlock guard, not the 500-ms API target.
The fifteen-second fake barrier is a test cleanup ceiling, not an increased runtime
provider timeout. Release the provider before waiting for reader shutdown even on
assertion failure. No SDK interruption, provider latency, network delivery, academic
accuracy, availability percentage or full load acceptance follows from these tests.

## Evidence

The first focused execution passes all three cases in 11.86 seconds. The existing
Starlette/httpx deprecation warning remains; no dependency is replaced. A follow-up
cleanup correction moves barrier release before executor shutdown so a failing
isolation assertion cannot wait for the artificial provider ceiling before cleanup.
The corrected focused run passes all three cases in 11.32 seconds. `make format lint
test-provider-fault-isolation test-unit openapi-check` passes: the three integration
cases, 1,092 unit/contract cases, 35 tooling checks, formatting, Python/TypeScript
types and unchanged generated contracts. `make security` passes, including secret
boundaries and both dependency audits. Full integration/hosted acceptance is pending;
unit-only execution explicitly deselects the 415 integration cases.

The parent [mixed-history load increment](E9_HISTORY_MIXED_LOAD_VERIFICATION.md)
already passes native load but still awaits its separate hosted promotion. Keep the
two increments and their exact source evidence distinct. Delayed/failed WhatsApp
transport, mixed-provider workload, older/diagnostic histories, database resource
measurement and external academic/privacy/provider/release gates remain open.
ADR-060 approval remains pending; this test work grants no deletion authority.
