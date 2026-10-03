# E8 local operations visibility verification

Date: 3 October 2026. Requirements: FR-OPS-002 (partial), NFR-OBS-001,
NFR-SEC-002 and NFR-MNT-001. Decision: [ADR-033](../decisions/ADR/033-local-operations-health.md).

## Scope

Read-only ADMIN snapshot/dashboard: dependency health, monitoring-worker heartbeat,
queued/stalled imports, recent failed imports and unresolved/high-priority flags. Counts
cap at 10,000 with a lower-bound indicator. Configurable thresholds produce allowlisted
structured alert metadata through a periodic local Celery sampler. No personal/domain
record IDs, source documents, report text or exception details are returned or logged.
Manual sampling cannot impersonate a live worker heartbeat. No database migration is added.

## Verification in progress

- `make openapi format lint test-unit typecheck`: 236 unit/contract and five tooling tests
  pass, along with lint/format/Python and TypeScript checks and contract generation.
- `make test-operations`: ten focused tests passed, covering exact boundaries/recovery,
  safe alert logs, role revocation, rate limits, queue/flag counts, unavailable queries,
  capped counts, heartbeat expiry and registered worker execution. A final rerun covers
  native/Compose heartbeat alias compatibility.
- All 19 browser journeys and dependency/security checks passed on the second run.
  The first browser run encountered host sleep (confirmed in macOS power logs); tests
  were rerun with command-scoped idle-sleep prevention and unchanged timeouts.
- The initial full integration run failed the heartbeat test, then its process stopped
  before reporting final results. Three new isolated regressions reproduced cross-app
  Celery settings reuse. Application-local registrations fix this for monitoring, imports
  and export expiry. All three regressions now pass in the 236-test unit suite.
  Fresh full database/container verification remains required.
- Docker again awaits its macOS administrator prompt after the prior process interruption.
  The final container smoke process also stopped before completion; it is not a pass.
- Initial failures: wrong ErrorEnvelope import corrected before generation; identical
  unit/integration test basenames caused pytest collection conflict, fixed by renaming
  the contract test. No existing acceptance tests were weakened.

## Changed components

Settings/environment example, operations contract/service/API, worker schedule, ADMIN
page/navigation/BFF, generated API client, manual/focused Make commands, isolated synthetic
browser provisioning, contract/integration/browser tests and required documentation.

## Remaining gates

The dashboard explicitly marks AI/messaging usage, grading-failure rates, latency,
mastery lag and WhatsApp failure instrumentation unavailable. Complete production
observability, independent outage detection/notification, deployment, restore and pilot
acceptance remain pending. No external providers, real learner data or model evaluation.
