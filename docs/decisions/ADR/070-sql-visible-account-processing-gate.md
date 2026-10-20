# ADR-070: SQL-visible account processing coordination

Date:20 October2026 (Africa/Kampala)
Status: Accepted within delegated engineering discretion under approved ADR-061; verification pending
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

## Staff source mutation ordering —20 October2026

Extend the same shared subject gate to independent staff operations on an owned case
and flag. After authenticating/locking the staff actor, pre-read only the immutable
case user_id or flag reporter_id, acquire the subject's shared gate, then take/re-read
the case/flag row lock and apply the existing ownership/revision/claim checks. Do not
lock a case or flag first: closure takes the subject gate before source rows, and the
reverse order could deadlock preservation or allow late source evidence after the
barrier. Keep existing actor locks/rate limits/retry checks and all lawful hold rules.
No subject identity/contact/answer is added to a DTO. Immutable ownership is guaranteed
by existing SQL constraints/triggers; missing resources still return the existing404.

Apply this order to case claims and audited deletion previews, the shared legal-hold access path (including exact
channel capture) and staff flag detail/triage, including retry reads that append audit.
Queue reads have actor-only audit and no subject source mutation. This is coordination,
not post-closure custody permission or a new blanket refusal of preservation/release.
Future closure/preservation SQL still needs independent source/hold guards and bounded
post-completion custody. Do not infer those controls from a shared gate.

Test actual PostgreSQL wait state under an exclusive subject gate and independently
acquire the same case/flag row NOWAIT while the staff operation waits. Verify completion
after release, unrelated subject independence, unchanged audit/retry authorization and
normal flag/hold/channel regression. No custom sleep or trigger bypass establishes proof.


## Private plan gate amendment —20 October2026

The private SQL plan issuer also participates in the subject gate. After current
private principal/source/ADMIN checks, read the immutable case subject, try the shared
transaction gate using the independently verified installed public namespace OID,
then lock/recheck case, review and subject user rows. Never derive the key from the
private principal's pg_catalog search path or accept a subject/key parameter. Busy
returns a fixed denial before any plan/audit insert; no queued private call keeps case
locks ahead of closure. The shared gate remains held until the issuing transaction ends.

Under REPEATABLE READ, acquiring a gate alone cannot refresh a snapshot established
before concurrent closure. Lock the subject user row as well as the case/review; a row
changed since that snapshot causes a safe serialization conflict before plan writes.
This supplements the existing closed_at check and avoids issuing from an older identity
version after an exclusive processing transaction commits. No new closure authority is
introduced. Fresh capability v3 records the amended recipe; do not adopt or upgrade an
existing v1/v2 installation. Public0045 and the v2 fingerprint algorithm remain unchanged.
Verify actual private/public-key agreement, zero writes when busy, held-case contention before the call, unrelated subject independence and stale-snapshot refusal.
