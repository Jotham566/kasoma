# Legacy hold DELETE clock verification — candidate

19 October 2026. FR-ID-006, BR-010, NFR-SEC-002, NFR-MNT-001.
[ADR-056](../decisions/ADR/056-wall-clock-hold-delete-guards.md) and
[readiness](E8_HOLD_DELETE_CLOCK_READINESS.md) define this narrow slice.

All four legacy wrappers reproduce the missed-hold boundary before the change:
a valid owned hold commits after the deleting transaction begins, the historical
predicate is false at transaction start and true at wall clock, but the wrapper
allows its temporary probe row DELETE. No original learning/accountability row is
deleted and no source append-only trigger is disabled. The failed reproduction is
retained locally; it is not reported as passing application acceptance.

Forward migration 0036 replaces only the four DELETE-wrapper clock arguments with
clock_timestamp. The explicit historical predicate and all ownership, target,
authentication, finite release/expiry, retention and append-only protections remain.
Four focused cases then pass. Each verifies denied probe DELETE while held, allowed
probe deletion after an independently valid release, and continued denied DELETE of
the original source row. No source-row/data transform or erasure authority.

Local verification passes:

- `make format lint openapi-check test-hold-delete-clock test-legal-holds
  test-grading-publications test-channel-receipt-holds`: 57 integration cases,
  including clean/0035 upgrade, repeated upgrade and exact prior hold replay.
- `make test-unit test-runtime-role recovery-drill security security-source`: 918
  unit/contract cases, 35 tooling cases, the actual restricted assessment login,
  dependency/source security and isolated 65-table/648-row logical recovery (299 ms).
  The receipt suite also exercises the actual restricted privacy login.
- `make containers migrate container-smoke security-containers` and application
  service restart: all eight services healthy, running API schema 0036, receipt
  creation disabled; owned asynchronous export/frozen retry, request aggregation and
  deterministic fake model observation pass. API/web scans report no HIGH/CRITICAL
  findings. Existing volumes are retained.

Complete exact-source hosted acceptance remains required before main promotion.
No frontend or provider-call behavior changes; this slice does not infer browser
acceptance from static checks. Prior receipt UI acceptance remains separate evidence.

Logs: `.local/hold-delete-clock-*.log`. Broader preservation, legacy clock-anomalous
metadata and future erasure clearance remain separately required. The MVP and actual
learner/academic/privacy/provider production approvals are not complete.

## Hosted gate failure

Run [39167600610](https://github.com/Jotham566/kasoma/actions/runs/39167600610) at
978ab30 passes 918 unit/contract and 373 integration cases plus five browser batches,
then the disposable runner runs out of disk. The pipeline fails and this source is
not promoted. [ADR-059](../decisions/ADR/059-disposable-ci-runner-storage.md) records
the capacity correction; require a complete corrected-source run before acceptance.
