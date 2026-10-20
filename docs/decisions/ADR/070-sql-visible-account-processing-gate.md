# ADR-070: SQL-visible account processing coordination

Date:20 October2026 (Africa/Kampala)
Status: Accepted within delegated engineering discretion under approved ADR-061; complete local/hosted engineering verification, closure and production gates remain pending
Requirements: FR-ID-003/005/006, FR-GRD-003/004, FR-WA-006, FR-OPS-003,
BR-010, NFR-SEC-002, NFR-MNT-001

## Context

Existing account serialization uses an HMAC key derived from the identity lookup
secret. A separately restricted SQL erasure owner must not receive that secret merely
to coordinate closure. Ordinary ACTIVE checks without a compatible lock leave a
check/commit race. Short-text authorization currently ends its transaction before
calling the model, leaving a dispatch interval after the check. ADR-050 deliberately
releases database locks before inference; keeping a row transaction or the existing
exclusive account lock across the provider would stall consent withdrawal and ordinary
work. Replacing the HMAC locks would change existing concurrency guarantees.

## Decision

Preserve every existing HMAC lock and its domain ordering. Introduce an explicit
lock_user wrapper that acquires that same lock, then a transaction-scoped **shared**
PostgreSQL advisory gate. Its server-computed64-bit key is
hashtextextended('kasoma.account-processing.v1:' || schema_oid::text || ':' || subject_uuid::text,0)
bitwise-OR the signed64-bit minimum. The result is always negative, disjoint from
the existing nonnegative60-bit HMAC lock space.
The normal caller derives schema_oid from its current schema; the future fixed-search-path
SQL owner must use its independently verified installed namespace OID, never its own
pg_catalog search path or a caller-supplied namespace. PostgreSQL also scopes advisory
locks by database. The same UUID in another owned schema must not be blocked.
This is a coordination key, never a credential or authorization proof. Collisions can
serialize unrelated work but cannot grant access. Use typed UUID bindings and fixed SQL;
never accept a caller-selected key or SQL expression through an endpoint.

Use the wrapper at existing account-lock sites: authentication, existing-user LOGIN,
refresh, staff provisioning, assessment/internal actor authorization, channel command/
delivery, grading/review and export coordination. Refresh cached user state after
acquiring the gate before deciding authority. Rate/identifier/global-channel keys
retain their original lock method. No additional user lock is acquired after an
identifier lock for an existing identity; existing fresh-verification rejection stays.

The future ADR-061 SQL closure capability will take the **exclusive** gate before its
case/source mutations. It must use nonblocking pg_try_advisory_xact_lock and safe
conflict/retry handling, never queue an exclusive waiter behind an in-flight session
whose short authorization transaction may acquire another shared gate;
this ADR adds no executor or permission to close an identity. That capability must
independently validate scope, current claimant/authentication, plan/source/preservation,
export drain and permanent closure, with SQL guards on later protected writes. A shared
lock alone is not an ACTIVE check, clearance, checkpoint or preservation mechanism.

For each already-authorized synthetic short-text provider call, use a dedicated pooled
connection holding a session-scoped shared advisory gate. Acquire it before the fresh
short authorization transaction, commit the acquisition transaction, and retain it only
through that provider call. Release the gate before returning the connection. On an
uncertain acquisition or failed release, invalidate the owned connection so a pooled
session cannot keep a hidden lock. A busy exclusive gate rejects dispatch immediately;
existing total request/token/time budgets remain, and final publication independently
rechecks its transaction authority. Do not widen the provider whitelist or enable scoring.

This is a narrow amendment to ADR-050's no-database-lock inference rule: the single
account privacy advisory gate is held during dispatch; **no row locks, HMAC account
lock, content/band lock or open transaction spans the model call**. Shared coordination
allows ordinary consent withdrawal, STOP and other already-authorized operations to
proceed; its exclusive closure peer cannot cross an in-flight dispatch. One extra
connection is bounded by existing worker/provider concurrency and call budgets.
Process/connection loss releases session locks. This synthetic FakeModelProvider lane
does not prove cancellation of remote production inference after process loss; that
remains part of provider/release acceptance. No cloud or real model call is introduced.

## Scope and alternatives

Rejected: pass the identity lookup secret to SQL; replace existing lock keys; hold an
exclusive account/row transaction across inference; rely only on a pre-dispatch check.
This change coordinates the already-approved closure design without changing data use,
retention, preservation, account ownership, academic authority or production permission.
The normal review database has no erasure capability and stays disabled. There is no
new feature, general lock endpoint, payload projection, deletion or completion path.
Unbound LOGIN issuance/drain, post-closure neutral/outbox behavior and independent SQL
write guards still require the full ADR-061 lifecycle implementation and tests.

## Verification and rollback

Prove real access/refresh/LOGIN operations wait at the shared SQL gate and recheck a
committed disablement. Pin the SQL key agreement. During fake model dispatch prove an
exclusive transaction cannot acquire the gate while the holding connection is idle
outside a transaction; prove release after success/provider failure and invalidation
on uncertain cleanup. Retain existing withdrawal, band revocation, budget, single-use,
worker/replay, channel STOP, export, restricted-login, browser and recovery checks.
Publish native and exact-source full hosted results separately. Do not infer closure
or erasure acceptance from these prerequisite tests. Roll back only before activation;
removing a coordination barrier after erasure enablement requires a forward safety
repair preserving closed identities and accepted work.
