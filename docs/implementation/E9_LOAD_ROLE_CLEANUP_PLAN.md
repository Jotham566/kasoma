# Next slice: disposable load role lifecycle

Status: implementation candidate; focused checks pass, complete verification pending.
Requirements: NFR-MNT-001, NFR-SEC-002; supports repeatable NFR-PERF-001/002 and
NFR-SCL-001 verification without adding a product feature or performance claim.

## Existing implementation and gap

The load harness in `scripts/objective_load.py` creates only its own generated
`kasoma_load_<32 hex>` database, rejects supplied application targets, runs migrations,
uses fake providers and closes its server/engines before dropping that database.
Both existing objective profiles share this lifecycle. Tests already prove name,
endpoint, creation-failure and database-drop boundaries.

Migration0041 now installs a cluster-level derived NOLOGIN owner. Dropping its database
does not drop that PostgreSQL role. The recovery drill explicitly handles this derived
role after dropping only its fresh databases, but the load harness does not yet do so.
Repeated fresh load runs can therefore leave unused maintenance roles. This is a
bounded tool-resource cleanup gap, not permission to purge application data or roles.

## Assessed implementation boundary

1. Keep the current local-only validator, generated database naming, provider choices,
   HTTP profiles, latency thresholds and server-stop-before-drop rules unchanged.
2. Derive only `owner_name(database, "public")` for the invocation's generated
   database. Before migrations, require that exact role to be absent using a bounded
   catalog lookup. If it already exists, refuse migration and preserve the role;
   creating a fresh database alone does not prove ownership of a pre-existing role.
   Exclusively CREATE that role in a transaction and record its OID before successful
   commit; absence alone cannot prove creation ownership. A concurrent creator makes
   this creation fail without conferring cleanup authority. After successful drop of
   the invocation-created database, inspect only that derived role using a bounded
   lookup rather than enumeration.
3. If absent, finish successfully. If present, require the same confirmed OID and
   the expected non-login,
   non-elevated attributes and no memberships before attempting normal restrictive
   DROP ROLE. Do not alter attributes, revoke dependencies, use DROP OWNED or sweep
   matching role names. PostgreSQL dependency refusal remains effective.
4. Preserve the role if database cleanup fails or its creation/commit was unconfirmed. Treat
   role cleanup refusal/failure as `cleanup_failed=true` and overall failure, using
   the existing closed diagnostics. Never mask the original processing failure or
   claim a successful load when owned cleanup fails.
5. Do not touch existing review databases, retained debugging schemas, shared roles,
   application volumes, SDKs or caches. No production role lifecycle is introduced.

## Acceptance gates

- Preserve existing negative tests with explicit absent-role mocks where needed.
- Cover a pre-existing exact role (refuse before migration and preserve it),
  role absent/created by migration, database-drop failure, unsafe/shared role refusal
  and role-drop failure. Cover a separate creator racing the absence check and a
  replacement with the same name but a different OID. Assert exact SQL targets/order
  and withheld diagnostic text.
- Run an actual isolated fresh migration that creates the derived role, stop before
  learner fixture creation, and verify database/role cleanup. Use only an invocation's
  freshly created resources; no cleanup of existing orphan roles is authorized.
- Run prescribed lint/types/security, relevant tests and complete hosted engineering
  gates. Add a focused Make target if absent. Update changelog, sprint, traceability,
  runbook and verification evidence alongside implementation.

This follows the existing recovery lifecycle under
[ADR-060](../decisions/ADR/060-completed-export-accountability-retirement-proposal.md)
and preserves [ADR-046](../decisions/ADR/046-shared-assessment-content-locks.md).
No new architectural decision, performance acceptance, erasure or real-data authority
is proposed. Further aged/diagnostic/provider/soak load profiles remain separate work.

## Readiness refinement during hosted verification

Inspection of `install_v1` confirms that migration 0041 can reuse an existing derived
role when its attributes pass validation. The load invocation must therefore record
absence before migration, rather than infer exclusive lifecycle ownership from its
fresh database name. This adds an acceptance case within the existing bounded cleanup
plan; it grants no authority over pre-existing roles. Implementation still follows
current candidate promotion. That promotion is now published through main `226ecf3`;
the operations branch is removed locally/remotely. The load-role implementation remains
a separate candidate.

The initial absence-only candidate at `4614bd3` is not accepted: a deterministic
actual two-connection regression creates a role after its absence SELECT and proves
that candidate incorrectly removes it. Exclusive transactional creation and an exact
OID recheck correct the ownership boundary. This remains local tooling under the
existing naming/installer decision; no production capability or new ADR is introduced.
