# E2 bounded draft-import verification

Date: 3 October 2026. Requirements: FR-CNT-001/002/004/005; bounded portions of
FR-OPS-001/002/003, NFR-SEC-002 and NFR-MNT-001.

## Implemented boundary

[ADR-032](../decisions/ADR/032-bounded-draft-imports.md) defines original synthetic JSON
imports only. 64 KiB streaming limit precedes parsing; 1–20 strict draft candidates
require provenance/source locators and valid supplied taxonomy. Imports create drafts,
never approve content. Existing independent review and rights controls remain required.
PostgreSQL stores command/retry truth. Workers recheck current author permissions and
atomically create normal draft/audit/outbox records. Duplicates report the author's
existing version. Three executions maximum, 60/120-second backoff, 24-hour payload expiry,
terminal payload removal and minimized owner-only statuses limit retained data.

## Verification

- `make openapi format test-unit lint`: passed 227 Python contract/unit tests, five
  actual-plugin tooling regressions, lint/format/Python and TypeScript checks.
- `make format lint openapi-check build security`: lint/types/contracts, web build and
  security/dependency checks passed after correcting browser-test formatting.
- Integration tests exercise ownership, exact replay/conflicts, taxonomy rejection,
  concurrent processing, duplicate exclusion, independent publication, rollback/retries,
  expired payloads, revoked author permissions and append-only database guards.
- Browser test covers invalid JSON, lost acknowledgement retry, owner status recovery,
  accessibility and opening a draft with source locator. Its isolated synthetic server
  drains the same worker processor; production Celery registration has a contract test.
- Docker recovered; `make services migrate seed test` passed all 347 Python tests
  (227 unit/contract and 120 integration), including clean isolated migrations and reruns.
- `make e2e`: all 18 browser tests passed. The initial import journey failed on an exact
  label selector for a prefilled textarea; its accessibility snapshot confirmed the correct
  value. The test now locates the textbox by accessible role/name and passes.
- `make security-source containers security-containers container-smoke process-imports`:
  source scan, image builds/scans, actual container API/Redis/worker/web smoke and bounded
  manual drain passed. Containers were rebuilt and rescanned after the final web-proxy
  streaming limit. Both API and proxy bound upload bytes before full-body buffering.
- Existing upstream Starlette/httpx deprecation and intentional socket-guard warnings
  remain; no failed final acceptance checks. No external model/messaging calls occurred.

## Files and decisions

API router/body limiter/main; content/import contracts/services/domain; additive migration
0017; Celery registration; source locator editor, import page and BFF; generated clients;
manual processor command, synthetic browser harness; import contract/integration/browser
tests; deletion-preview staff provenance inventory; ADR-032 and associated changelog,
sprint, traceability, API/data/content-operations/runbook documentation.

## Remaining gaps

No arbitrary-file extraction, model calls, external delivery or real content/data.
Academic mapping/rights approvals and calibration are separate release gates. Failed jobs
can be resubmitted with a new key after correction; the original job remains immutable.
Retention of minimal administrative evidence and all destructive processors still require
the previously documented implementation/review. Stopping workers delays expiry; operations
must monitor worker availability. These checks do not establish production-pilot acceptance.
