# ADR-078: Installed erasure principal and grant fence

Date: 20 October 2026 (Africa/Kampala)
Status: Accepted technical implementation under approved ADR-061/071/072; engineering accepted after complete own hosted39383925992 at exact4bf5a77347af725cdb05853392f73e14c6e68fef
Requirements: FR-ID-006, FR-OPS-003, BR-010, NFR-SEC-002, NFR-MNT-001

Add a fresh-only v6 recipe with a closed SQL principal/ACL predicate called by
scope_identity_ok. Therefore readiness, plan issuance/versioning and bounded plan
expiry independently refuse missing or extra privileges before source writes.
Compile expectations from the versioned grant recipe and manifest, never observed
live ACLs. Pin the fresh creator, owner, authorizer and maintenance OIDs. Compare
complete explicit grant tuples (object/subobject, grantee, grantor, privilege and
grant option) affecting those new principals; reject PUBLIC source-table/column
grants and unexpected private-schema/function/type access. Keep exact role flags,
membership prohibition and the two LOGIN roles' fixed global settings. Refuse
unexpected default privileges and persistent objects owned by these principals.

Use raw pg_catalog fields and fixed builtin type signatures; no expression deparser,
application rows, key/body export, new secret or live-derived baseline. Preserve the
existing PUBLIC database CONNECT/TEMP and controlled temporary-table shadow test;
temporary objects grant no ordinary source access. Retain the original checked
pre-install catalog and public0045 source identity. v1-v5 remain immutable historical
recipes and are not silently upgraded or accepted as the current private capability.

This is the installed principal-separation component, not full installed public/private
code/catalog verification or clearance. Unrelated existing-role grants, all source
payload/ownership/hold/preservation/export checks and permanent closure write guards
still require their full fences before atomic authorization/closure. No job, closure,
erasure or DELETE completion is enabled; normal review and real data remain excluded.

Prove actual LOGIN denials after extra/lost table/column/schema/function/type rights,
grant options, role settings/flags/membership/defaults or persistent ownership drift;
no plan/expiry/audit mutation on refusal. Healthy controls and existing temporary
shadowing must pass. All tests use invocation-owned fake-only fresh sources.
