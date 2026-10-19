# Synthetic export retirement operations — candidate

Requirements: FR-ID-006, FR-OPS-003, BR-010, NFR-SEC-002, NFR-MNT-001;
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
Full backend, final browser matrix, container/image/service and hosted engineering gates
remain pending. No inference or external delivery occurs.

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
