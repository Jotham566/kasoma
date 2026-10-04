# E8 local channel operations verification

Status: local/synthetic application verified; release performance and production gates remain.
Requirements: FR-OPS-002/004, NFR-OBS-001, NFR-SEC-002; contributes instrumentation toward NFR-PERF-002.
Decision: [ADR-039](../decisions/ADR/039-local-channel-operations.md).

The existing ADMIN/rate-gated snapshot and sampler now derive capped message queue/status cohorts,
oldest age and bounded fake-feedback dispatch p95 from PostgreSQL. Optional channel fields preserve
existing response compatibility. Migration 0021 adds indexes only. No identities or free text enter
snapshots/alerts. No observations returns null timing and query failure remains unavailable.

## Checks

- Pure tests: empty/zero/rounding/nearest-rank/capped timing, exact thresholds, minimum samples,
  recovery, rejection/cancellation non-alerting, typed configuration and alert schema coverage.
- Database tests: inclusive 24-hour cohort bounds, stale pending age, latest-sample cap, real
  authorization and minimized projection. Use `make test-channel-operations`.
- Browser: refreshed channel panel, honest empty timing, existing access/network and axe checks.
- Required: setup/clean migrations/seed, full test suites, generated contracts, lint/types/build,
  security audits/scans and container smoke before promotion.

An initial duplicate test-module basename caused collection failure; the contract module was
renamed to the repository's distinct naming convention. No test was removed or weakened.
Local Docker remains unavailable; database acceptance must come from hosted clean-schema checks.

## Limits

Recent status counts refer to receipt/creation cohorts, not the time of later status changes.
Dispatch timing measures durable receipt to fake transport acceptance, not delivery to a learner.
At most 1,000 latest observations are sampled; the response identifies truncation. Configured alerts
use engineering defaults and do not grant release/SLO acceptance. AI/SMS/email usage, pre-intake
signature failures, HTTP latency, mastery lag and external production alerting remain separate gaps.

## Local execution before hosted verification

`make format lint openapi-check test-unit` passed 317 unit/contract and five tooling tests.
`make openapi` regenerated shared contracts; the contract comparison passes. `make security` passed
Bandit, local secret checks and Python/JavaScript dependency audits. `make migrate` and all three
focused database cases failed because local PostgreSQL refuses connections; none reached an
application assertion. These are failed native attempts, not migration or telemetry acceptance.

A later native probe also found the Docker CLI symlink target under Docker.app absent. The
repository does not repair or replace that host installation; hosted checks remain the database
verification path. Existing local database errors are preserved as failed attempts.

## Final hosted acceptance

Commit `34950b0` passed [CI 37221185319](https://github.com/Jotham566/kasoma/actions/runs/37221185319):
317 unit/contract and 162 integration tests (479 Python total), 20 browser and five tooling checks.
Setup, clean migrations/seed, lint/types/contracts/build, security audits/source/image scans and
container smoke all passed. Main now contains the slice and its completed branch was removed.
This supersedes pre-hosted pending notes but does not erase the failed native setup attempts.
