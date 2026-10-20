# ADR-071: Isolated erasure SQL capability bootstrap

Date:20 October2026 (Africa/Kampala)
Status: Accepted technical implementation within delegated discretion under approved ADR-061; implementation and verification in progress
Requirements: FR-ID-006, BR-010, FR-OPS-003, NFR-SEC-002, NFR-MNT-001

## Decision

The approved ADR-061 capability must never be installed by normal application startup,
an environment flag, a request body or an ordinary Alembic upgrade of the review database.
Use a separately versioned, forward-only privileged installer inside a newly created
owned local synthetic PostgreSQL source. The normal source remains on its ordinary
Alembic revision with dormant erasure controls. This changes neither approved erasure
scope nor any retention/preservation permission.

Issue a process-local source proof before migrations. Bind its exact owned container,
label, loopback port, database and public-namespace OIDs, factory nonce and active lifetime.
A one-use registered issuance ticket prevents metadata-only adoption; the issued object
is itself registered, immutable and not reconstructible by copying fields. Existing
relations/functions/namespaces refuse issuance. Revalidate the live resource and catalog
identity before installation. The trusted bootstrap process and Docker administrator are
privileged operators, not an application authorization boundary; independent SQL guards
must enforce runtime scope after installation. A proof alone grants no SQL execution.

Create exclusively, without adoption, three capability-specific roles: a NOLOGIN owner,
a separate authorizer login and an EXECUTE-only maintenance login. Grant no membership,
superuser, role/database creation, replication, inheritance or RLS bypass. Only the
owner receives narrow table privileges needed by implemented functions. Ordinary
identity/assessment permissions for the authorizer require explicit reviewed grants;
it does not gain source CRUD merely from installation. Maintenance receives only the
closed implemented entrypoints. Verify with actual logins, not SET ROLE alone.

Use an immutable private control schema for source/role OIDs, original source nonce,
installation policy/version, false activation defaults and a purpose-specific random
plan-fingerprint key. Keep it inaccessible to both logins. It is shared capability
metadata (K), not a learner/source-key ledger; no new personal-data retention is added.
Freeze and independently check this additional namespace as well as the complete
application source manifest before authorization or closure. No unknown private table,
function, grant or source revision is accepted merely because a schema name matches.

For standard SQL HMAC, install PostgreSQL's bundled pgcrypto1.3 extension only in a new
private crypto namespace of this owned source. Use its bytea HMAC-SHA256 function with
qualified identifiers. Revoke PUBLIC function execution and grant only the required
HMAC overload to the NOLOGIN owner. This avoids a custom cryptographic implementation;
it adds no cloud/provider dependency and does not replace authenticated preservation
encryption. Normal migrations, review startup and automated model behavior are unchanged.
Existing pgcrypto installations/namespaces/roles are not adopted.

The explicit installer may replace the dormant state guard in its owned source with
an owner/OID/nonce-bound bootstrap guard and constraint, atomically in one transaction.
This is a forward capability migration, not a trigger-disabling switch or bypass GUC.
At this stage creation/execution checks remain false, plan/job writes and closed_at
remain forbidden, and the only login entrypoint is minimized disabled readiness.
Subsequent functions must independently recheck actual session principal, scope,
current case/claimant/OTP, version-bound plan, source/payload/hold/export drain and phase.
Nonblocking exclusive ADR-070 coordination is mandatory for closure. No early phase may
claim the first authorization/closure slice or fulfill a DELETE request.

## Verification and remaining work

Prove fresh issuance, clone/expired/nonlocal/non-fake/populated-source denials and exact
resource cleanup. Prove actual authorizer/maintenance principal flags, no owner membership,
no source/control reads, source DML, role assumption, direct closure or plan/job creation.
Prove private key/PUBLIC boundaries, namespace/OID/replacement and installation replay
refusal, SQL error sanitization and atomic failure. Run normal browser/resource regressions
because the factory is shared. Never clean another invocation's resources or SDK/cache.

Complete the server plan, authorization, permanent processing stop, durable continuation,
full preservation/removal/retirement and recovery acceptance from ADR-061. These remain
required work. This technical decision grants no normal-review, real-data, production,
representative/staff support, provider or release permission and changes no deadline.


## Local disabled-bootstrap evidence

The implemented disabled stage passes11 native/contract fresh-source/capability cases,
1,487 unit/contract,110 resource controls and123 browser executions, plus quality,
contracts/build and security. Actual source inventory is75 tables/561 columns including
the private K table. The PostgreSQL key-error probe observes a fixed server error in
both-stream capture without the rejected key or generated credentials; rollback and
retry pass. No first-slice, full source/hold/ACL clearance, SQL authorization/closure,
erasure or complete hosted acceptance is inferred. Follow the exact evidence register.
