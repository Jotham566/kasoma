# Current Sprint: E4 guarded short-text preparation

Updated 4 October 2026. Main is `34950b0`. Completed conversation and channel operations branches
have been removed. All work remains synthetic/local; no production model or messaging is enabled.

## Latest verified slices

- Five-question signed WhatsApp practice (`5063528`): [CI 37220225176](https://github.com/Jotham566/kasoma/actions/runs/37220225176),
  469 Python, 20 browser and five tooling checks. Reply binding, shared score/mastery parity,
  concurrency/replay, STOP/expiry, broker recovery and reviewed channel suitability pass.
  [Conversation evidence](E7_CONVERSATION_VERIFICATION.md).
- Minimized ADMIN channel operations (`34950b0`): [CI 37221185319](https://github.com/Jotham566/kasoma/actions/runs/37221185319),
  479 Python, 20 browser and five tooling checks. Queue/status cohorts, bounded fake-dispatch p95
  and threshold alerts pass. [Operations evidence](E8_CHANNEL_OPERATIONS_VERIFICATION.md).

Both runs passed setup, clean migrations/seed, lint/types/contracts/build, security scans and
container smoke. Native PostgreSQL checks failed before assertions; Docker.app is unavailable.
Hosted acceptance does not claim that the local Docker installation has recovered.

## Active implementation

- ADR-040 strict rubric candidate validation (`3b74f5b`): 40 new fixture cases, 357 local unit/contract
  and five tooling checks with lint/types/contracts/security. Hosted verification is running.
  [Validation evidence](E4_SHORT_TEXT_VALIDATION_VERIFICATION.md).
- ADR-041 adds independent fake passes, one global schema repair and bounded request/token/deadline
  accounting through ModelGateway. Fifteen additional tests pass; 372 local unit/contract and five
  tooling checks with lint/types/contracts/security. No candidate becomes a learner score.
  [Rehearsal evidence](E4_SHORT_TEXT_REHEARSAL_VERIFICATION.md).

Finish exact-commit hosted verification and publish verified work. Next: approved rubric/context
loading and neutral learner fallback/persistence, while preserving the calibration enablement gate.
Gateway telemetry, injection/domain detectors and live adapter enforcement remain required.

## Other MVP gates

Measure feedback latency under the approved load; functional tests and fake-dispatch samples alone
do not establish NFR-PERF-002. Continue remaining telemetry/usage controls. Prepare the concrete
deletion/anonymization transform and tested recovery plan before seeking destructive-execution
approval. Remaining hold coverage, large-history export and accountability expiry remain gaps.

The [release register](RELEASE_GATES.md) records missing owner evidence: kickoff/capacity, exact
NCDC mappings, rights and approved inventory, expert benchmark/calibration, privacy/guardian/DPIA,
Week 8 provider decision, production OTP/MFA, restricted roles, restore/load and pilot sign-offs.
No synthetic test, elapsed time or implementation ADR substitutes for those approvals.

See [requirements traceability](REQUIREMENTS_TRACEABILITY.md) for the complete evidence map.
