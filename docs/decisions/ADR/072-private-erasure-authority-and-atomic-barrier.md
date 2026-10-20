# ADR-072: Private erasure authority and atomic authorization/barrier

Date:20 October2026 (Africa/Kampala)
Status: Accepted technical implementation within approved ADR-061; implementation/verification in progress
Requirements: FR-ID-003/005/006, FR-OPS-003, BR-010, NFR-SEC-002, NFR-MNT-001

## Decision

Keep the ADR-071 authorizer login separate from the ordinary API database login and
maintenance login. It is an EXECUTE-only private service capability, not an ordinary
identity/assessment login. Do not grant it source-table CRUD, owner membership or a
learner lookup API. Ordinary SQL-login possession must not authorize erasure. Maintenance
may process only already-authorized durable job identities and bounded transient cleanup.

The API authenticates the bearer token and current ADMIN/recent-OTP/case claim through
its ordinary identity service. Copy only the authenticated session UUID and the source's
server-observed database/namespace/nonce binding, then end that transaction before using
the private authorizer connection. No request body supplies a session, actor, subject,
namespace, clock or database URL. SQL independently rechecks the actual session principal,
source binding, current session/access/refresh expiry and revocation, active ADMIN user,
independence, pending verified DELETE request and exact current claimant. Lock the relevant
current authority rows while accepting a command. PostgreSQL clock is authoritative.

Ending the ordinary authentication transaction before the private call avoids holding
an account/row lock while a second connection tries to recheck that same authority.
SQL revalidation prevents the gap from grandfathering a revoked role/session. This is
delegation by the separately protected server capability, not trust in a client UUID.
Compromise of that privileged credential is an administrative incident: keep it private,
rotate/revoke it, and fail closed. This decision does not claim protection from a hostile
application process or privileged database/Docker administrator who controls those secrets.
No identity lookup/JWT signing key is shared with the SQL owner; no custom MAC protocol
or per-user database-role system is introduced.

Issue case-only database-clock plans through that private principal. An issued plan may
report explicit execution-disabled/verification-incomplete blockers while implementation
or switches prevent authorization. It never converts a source fingerprint or advisory
counts into erasure clearance. Plans expire within ten minutes; maintenance cleanup is
bounded and uses database time, not a caller cutoff. The owner may write only the exact
server-generated plan and seal its version once. All source predicates come from the
closed versioned registry, not request-selected SQL/tables/columns.

The version seal folds every owned source row in primary-key order using private SQL
HMAC-SHA256, bound to source/subject/current plan identity and manifest. Include all
owned transient plans; normalize only this plan's self-referential version field.
Issue the plan/read audit before computing the seal. Its subsequent version update
changes no other plan field. Later authority/source changes require a new reviewed
plan. Do not silently omit all audit or lifecycle evidence to avoid stale-plan conflicts.
No source body, credentials, private key or source-ID list leaves PostgreSQL.

When complete authorization is implemented, acceptance and the initial permanent
closure barrier commit in one transaction. AUTHORIZED may be an internal transition;
there is no separately accepted job stranded behind an expired original plan before
closure. Nonblocking exclusive ADR-070 acquisition, complete source/payload/hold/export
checks and current authority all precede acceptance. A busy/stale/unsupported attempt
commits neither a job nor closure. Once the barrier commits, the same durable job resumes
preservation/removal/verification; later failure cannot reopen the identity. Exact retries
recheck current API authority and the already-accepted immutable command binding.
This does not permit completion before all ADR-061 acceptance gates pass.

## Versioning and scope

The staged disabled v1 bootstrap remains historical. Extend the fresh-install recipe
with explicit private capability version v2 for plan issuance and bounded plan expiry;
never adopt or silently upgrade an existing v1 namespace/roles. The ordinary public
0045 structural baseline remains separately identified. Normal migrations/startup do
not install this capability. Default erasure creation/execution remain false, and all
normal-review, real-data, production, provider, support and release exclusions remain.
No new preservation or retention permission is created.

Exact new action data_request.erasure_plan_read is security/access evidence, twelve
months after created_at subject to exact holds; it targets its owned case. Exact action
data_request.erasure_plan_expiry_batch is system security evidence with the same class;
it targets the installation nonce and carries count-only metadata, not a removed-plan
ID list. These implement ADR-061's already-approved new erasure access/batch vocabulary.
They do not reset a case deadline or authorize retiring associated originals.

## Verification

Use actual private/ordinary/maintenance logins; reject unauthenticated, non-ADMIN,
revoked/rotated/expired/future sessions, self review, wrong claimant/kind/completed case,
wrong source and direct source/control writes. Prove server-generated clocks/seals,
current-plan self-write reconciliation, unrelated-subject stability, large-history
nontruncation, stale-source/plan rejection and bounded database-clock expiry. Verify
no public plan/actor/subject override or error/log body leakage.

Full source/private catalog/ACL integrity, payload/hold/export drain, permanent closed
write barriers, actor/role/OTP/refresh/channel/model/export races, restart/recovery and
complete preservation/removal/retirement remain mandatory before actual closure or
DELETE fulfillment. A blocked issued plan is not completion of that vertical slice.


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
