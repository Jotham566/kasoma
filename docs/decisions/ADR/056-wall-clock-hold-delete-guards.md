# ADR-056: Wall-clock evaluation of existing hold DELETE guards

Date: 19 October 2026
Status: Proposed; local reproduction and verification pass, hosted acceptance pending
Requirements: FR-ID-006, BR-010, NFR-SEC-002, NFR-MNT-001

## Scope and decision

ADR-030/043/045 require exact finite preservation. Four legacy DELETE wrappers pass
PostgreSQL current_timestamp (transaction start) to record_is_held. A deletion transaction
can begin before another transaction creates a hold and then miss that committed hold
when its later DELETE uses the older timestamp. Existing append-only guards still block
actual learning/accountability erasure; that independent protection must remain intact.

Evaluate those four DELETE wrappers at clock_timestamp instead. Keep the explicit
record_is_held(kind,target,at_time) predicate unchanged for historical/boundary queries.
Keep target kinds/ownership/locks, finite decisions, all authentication/authorization,
API/schema, source data, retention policy and append-only triggers unchanged. No deletion
processor, exception, data rewrite or additional preservation authority is introduced.
Channel receipts already use wall-clock checks under ADR-055 and remain unchanged.

Before changing a guard, reproduce its time boundary using the real trigger on an owned
temporary probe row carrying the real held record's UUID/column. This isolates the hold
wrapper without disabling any original append-only protection or deleting original
records. Create the valid owned hold in a second real database transaction after the
probe transaction begins. Its historical predicate must be false at transaction start
and true at current wall clock; the later DELETE must be denied by that wrapper.

## Acceptance and rollout

Cover generic id, grade attempt_id, request-review request_id and publication attempt_id
wrappers. Verify clean/0035-upgrade, exact existing hold replay, explicit point-in-time
predicate semantics, release/expiry scope and unchanged original immutable guards.
Re-run existing hold, actual restricted-login, populated recovery, security, migration
and Docker smoke checks; require complete hosted acceptance before main promotion.
No frontend behavior or model/provider call is changed. Production/privacy approval and
full preservation/erasure gates remain separate. Legacy clock-anomalous metadata and
future erasure clearance still require their own review; this fixes one measured boundary.

Forward migration only; preserve applied migrations and all registered evidence. A
rollback must retain protection and use a forward correction, never drop holds/guards.
