# Synthetic export retirement operations — candidate

Requirements: FR-ID-006, FR-OPS-002/003, BR-010, NFR-SEC-002, NFR-MNT-001;
operator presentation also supports NFR-ACC-001.

This implements step 3 of approved [ADR-060](../decisions/ADR/060-completed-export-accountability-retirement-proposal.md).
The [SQL kernel](E8_EXPORT_RETIREMENT_VERIFICATION.md) and
[exact preservation foundation](E8_EXPORT_EVIDENCE_HOLDS_VERIFICATION.md) have
separate complete hosted evidence. This candidate has not yet passed full acceptance.
The normal review stack remains disabled; no account erasure or real-data use is authorized.

## Implementation boundary

- A separately provisioned LOGIN has schema USAGE and EXECUTE on the parameter-free
  routine only. Actual authentication checks reject table/column privileges, memberships,
  elevated role attributes, unsafe ownership/search path and PUBLIC execution drift.
  Metadata checking materializes the target schema's table set before ACL evaluation;
  it never reads source rows. SQL remains the independent policy authority.
- An exclusively created owned 0600 file under ignored `.local` holds the private
  credential. Shared settings, API and ordinary worker never load it. Provisioning
  refuses existing roles/files. Fixed configuration audit events have no actor/source
  references. Disablement does not depend on the new-creation hold switch.
- The ordinary worker's optional scheduler publishes a parameter-free, expiring task
  to `privacy-maintenance` every 300 seconds (bounded 60–3600). Only a separate private
  consumer registers it: prefork, concurrency one, prefetch one, 12/15-second envelope,
  late acknowledgment and no result store. It runs no Beat or ordinary tasks.
- Both typed configurations default false. Scheduler enablement requires exact-hold
  support and an isolated synthetic scope. Private configuration and persisted SQL
  activation are independent. The ordinary review database's public schema is refused.
- Failed execution exposes a closed failure only. Count-only Redis observations expire
  within 300 seconds; failure counts use non-sliding five-minute buckets, capped at
  10,001. Scope keys derive from database/schema names, never learner identities.
  Observations are best effort, not deletion authority or durable audit evidence.
- The ADMIN operations route adds optional bounded counts, activation/scope status,
  database progress age and executor observations. Migration 0042 adds an additive
  due-export partial index. Due parent counts are not a promise of removability:
  exact holds, copies and dependencies are independently checked by SQL.
- Failure alerts require scheduled + database enabled + isolated scope. A failure in
  the retained interval alerts at one; no database progress alerts at twice the
  configured interval. Disabled review stacks do not generate retirement alarms.
  The accessible dashboard is read-only and states account deletion is disabled.

## Verification register

Local `make test-retirement-runtime` passes 25 cases in 32.89 seconds: 16 contract
and nine integration cases. These include actual EXECUTE-only authentication, damaged
capability refusal, private provisioning/activation/disablement, finite/scoped observations,
ADMIN authorization/redaction, a fresh native prefork consumer and populated0041-to0042
forward/repeated migration without evidence or activation changes. The ordinary queue's
message remains unconsumed. No eager-task or parent-only test substitutes for this proof.

`make setup` preserves existing `.env`; `make migrate seed recovery-drill` passes.
Logical recovery verifies 69 tables/686 rows in 345 ms, exact receipt holds, encrypted
stores, immutable guards and denied execution after stripped ownership, with no cleanup
failure. This does not prove object-storage recovery or production PITR/RPO/RTO.
`make test-unit` passes 1,112 unit/contract and 35 tooling checks. Lint/types/contracts,
build and security/dependency audits pass. Six focused operations/flag journeys pass
across Chromium/Firefox/WebKit, including authorization, count-only presentation,
320-pixel layout, 200% text and axe. Visual review shortens the maintenance heading to
avoid an orphaned final letter at enlarged text; the final broader browser run is pending.
The final `make test` passes all 1,112 unit/contract and 465 integration cases, with
35 tooling checks; native integration duration is 1,748.82 seconds. `make e2e` passes
96 ordinary plus 12 disabled fake short-text executions (108 total). The corrected
heading is visually reviewed at 320 pixels and 200% text. `make containers`, all eight
service health checks, `make security-source security-containers` and
`make container-smoke` pass. The review database is 0042 and its retirement state
is independently read false. Existing application volumes remain intact.

Application source is `94b40a66a99067f5c7b8bdc78f28569706554938`. Hosted
[39243195783](https://github.com/Jotham566/kasoma/actions/runs/39243195783) fails in
Chromium lost-response interception after 31 passing browser executions. All 1,112
unit/contract, 465 integration, 35 tooling, three staff UI and three native WebKit
transport checks pass first. Hosted recovery is 69 tables/686 rows in 643 ms.
Later browser engines, image/security/service gates do not run and are not accepted.
No main promotion occurs. A test-only correction and a new complete hosted run are
required; application, migration and contract code remain unchanged.
No inference or external delivery occurs.

Retained observations: after local engine recovery an initial 19-case run had one
closed failure during cold metadata validation; an unchanged diagnostic run passed all
19. Its underlying cause is unconfirmed. The candidate subsequently bounds catalog
ACL evaluation to the target schema; it does not increase the two-second SQL timeout
or weaken permission checks. Earlier setup errors occurred while PostgreSQL was stopped
and do not constitute application acceptance. Final results will be recorded here.


The fresh native consumer initially fails with `NotRegistered` in its spawned child;
parent-only registry and direct task assertions had passed. A first signal/import
attempt still fails and is not accepted. The final private AppLoader reconstructs the
registry on its explicit app before tracing, using only its private configuration;
no global shared task or ordinary credential is introduced. The final 24-case run and
expanded 25-case run pass cold with the same native prefork launch policy. Security
also initially flags a silent connection-disposal exception (Bandit B110); the final
path emits a fixed diagnostic without masking the committed batch or exposing SQL.
No scanner exemption, timeout increase or permission weakening is used.

## Files in this increment

- `.env.example`, `Makefile`, `AGENTS.md`, `CHANGELOG.md`.
- `apps/api/migrations/versions/0042_retirement_health_index.py`.
- `apps/worker/main.py`, `apps/worker/retirement.py`,
  `apps/worker/retirement_entrypoint.py`.
- `apps/web/app/admin/operations/page.tsx`.
- `services/config.py`, `services/export_retirement.py`,
  `services/export_retirement_access.py`, `services/export_retirement_cli.py`,
  `services/export_retirement_config.py`, `services/export_retirement_health.py`,
  `services/export_retirement_observations.py`, `services/operations.py`,
  `services/operations_contracts.py`.
- `packages/analytics-schema/operations-alert.schema.json`,
  `packages/api-client/openapi.json`, `packages/api-client/src/schema.d.ts`.
- `tests/contract/test_retirement_executor_contract.py`,
  `tests/integration/test_export_retirement_runtime.py`,
  `tests/fixtures/retirement_worker_app.py`, `tests/e2e/operations.spec.ts`.
- `docs/decisions/ADR/060-completed-export-accountability-retirement-proposal.md`;
  `docs/implementation/CURRENT_SPRINT.md`, `REQUIREMENTS_TRACEABILITY.md`,
  `E8_EXPORT_RETIREMENT_VERIFICATION.md` and this verification document;
  `docs/runbooks/LOCAL_DEVELOPMENT.md`;
  `docs/specifications/04_API_and_Integration_Contract.md`.

No new architectural decision changes ADR-060: private configuration, explicit
AppLoader and finite operational observations implement its accepted boundary.
Further Markdown closeout may update the release/checkpoint/decision registers;
application, test, migration, Makefile and workflow identity must remain at the
verified source when recording acceptance.


## Hosted interception failure and correction candidate

The failed request is the existing WhatsApp code POST's intercepted `route.fetch`.
The transport reports a socket reset with unknown commit status. The proxy generates
its own API correlation identity, so absence of the browser's request ID in API events
does not prove whether the write committed. The local full matrix passed.
The underlying hosted connection reset cause is unconfirmed. Raw harness failure
reports include temporary synthetic request headers; the correction withholds those
diagnostics. No real data or production credentials are involved.

FR-WA-001/004/006, NFR-MNT-001 and NFR-SEC-002: the new test helper permits only
loopback API POST/DELETE with a canonical UUID idempotency key, follows no redirect,
and retries at most one ECONNRESET using identical request body/headers. It does not
retry HTTP failures or the test itself. The original 201-before-abort, visible retry,
STOP and unlink assertions remain; the browser retry must now recover the exact
committed code and reuse the key, compared without printing either value. Production
and application retry behavior are unchanged.

A loopback server deliberately resets once, resets persistently, returns HTTP503,
or receives a missing-key attempt. Three-engine controls verify identical replay,
exactly two attempts for a reset, one for HTTP503, zero before invalid-key refusal,
and fixed diagnostic redaction. The first control fixture also counts automatic
favicon requests and correctly fails; its final listener counts only the committed
API path, keeping the exact attempt assertions intact. Native attachment targets
remain explicitly restricted to their original three tests, including the Linux
mount profile. `make test-commit-interception` and `make test-web-whatsapp` are the
prescribed focused commands; CI adds the former without omitting existing gates.
Full correction results will be recorded after execution.

Additional correction files: `tests/e2e/support/committed-intercept.ts`,
`tests/browser-control/committed-intercept.spec.ts`, `tests/e2e/whatsapp.spec.ts`,
`Makefile`, `.github/workflows/ci.yml`, changelog/sprint/traceability and the
local runbook/testing specification. No application or architectural change.

Correction-focused local checks pass: all 12 `make test-commit-interception` controls,
all three `make test-web-whatsapp` journeys, the original three native Linux attachment
controls, `make lint openapi-check build`, `make security security-source` and
1,112 unit/contract plus 35 tooling checks. Application/migration/contract source
remains byte-identical to `94b40a6`; the earlier complete 465-case native backend pass
is runtime evidence, not a claim of a new complete hosted run. The corrected full
browser matrix now passes all 108 executions. Corrected source
`b6aea35d653cd0f13e0aef301013d174c08e4c0f` fails complete hosted
[39249423592](https://github.com/Jotham566/kasoma/actions/runs/39249423592).
All backend/role/recovery and 12 interception controls pass, then a different WebKit
resumed-assessment transition fails after79 ordinary passes. Later gates do not run.
No main promotion or complete hosted acceptance is claimed. The
[layout correction](E3_REVIEW_ACTION_STABILITY_VERIFICATION.md) independently reproduces
and corrects a47.421875-pixel action shift from delayed review hints. Its exact
relationship to that unretained hosted pointer trace remains unconfirmed. Application
change is limited to feedback layout; backend/migrations/contracts remain unchanged. No main promotion occurs while hosted acceptance is absent.
