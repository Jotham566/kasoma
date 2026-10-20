# ADR-073: Frozen pre-install source catalog

Date:20 October2026 (Africa/Kampala)
Status: Accepted technical implementation under approved ADR-061; verification pending
Requirements: FR-ID-006, FR-OPS-003, BR-010, NFR-SEC-002, NFR-MNT-001

## Decision

Before installing any private erasure principal, compare the fresh public0045 catalog
with a versioned baseline reproduced from the approved migrations in another explicitly
created, exclusively owned fake-only source. Never learn or approve a baseline from an
existing developer/review database, from caller configuration or from the source being
accepted. The ordinary column/primary-key shape check is necessary but insufficient.

Canonicalize behavior-relevant catalog metadata under a fixed pg_catalog search path:
relations/attributes/defaults, constraints, indexes, internal and application triggers,
function bodies/interfaces/settings, ACL/default ACL, RLS/policies, rules, types, public
operator/index support, extension identities and relevant role/database controls. Exclude
physical storage/statistics, generated object OIDs, database names and login secrets.
Normalize role references only to independently observed database-owner/predefined-owner
identities and the exact database/public-schema ADR-060 retirement-owner derivation; additional roles/grants or changed behavior must fail. Internal FK trigger
names contain generated OIDs: compare their full semantic attributes and multiplicity
instead, retaining exact names for application triggers. No LIMIT truncates inspection.

Compute ordered category counts and SHA256 inside PostgreSQL. Only technical counts/
digests leave the server; no learner table rows, function bodies, secrets or ACL values
are returned by the verifier. The checked artifact is metadata, not a data preservation
copy. Emit a fixed unavailable error on mismatch. A live catalog cannot bless itself.
Four approved export-retirement function bodies contain that database-specific owner.
The generator freezes their code templates from the newly migrated source; the verifier
renders the checked expected templates with the exact derived owner and compares complete
live bodies inside PostgreSQL. Never replace/normalize live body strings: accepting a
placeholder in place of a real role literal would hide a changed predicate. An arbitrary
role prefix cannot become an owner label. The baseline also binds the frozen ordinary
migration helper code. These are code templates, never learner payload snapshots.

Baseline regeneration is an explicit repository command against a new owned source;
ordinary setup/startup/migrations never regenerate or install it.

This first guard applies before the privileged installer changes source functions,
constraints and grants. An installed-catalog/ACL fence, independent SQL revalidation,
ownership/payload/hold/export checks and permanent closure guards remain required before
any erasure. Do not call a matching pre-install digest full execution clearance. Fresh capability v4 records the new pre-install fence and reuses the v3 plan-gate SQL.
Existing v1/v2/v3 identities remain historical and fail the current API readiness contract; no existing installation is adopted.
Normal review/real data/production remain excluded and all activation flags stay false.

## Verification

Reproduce equal metadata across separate fresh resources and after synthetic row writes.
Reject body-only trigger/function changes, disabled triggers, lost FK/CHECK/index controls,
new grants/default privileges, RLS/policy/rule/type/operator changes and unexpected roles
without creating private principals. Preserve exact owned cleanup, clean migrations,
actual-login tests, API/version/processing gates and the complete engineering regression.
Do not infer erasure checkpoint recovery, legal/academic/provider approval or application
acceptance from this artifact or documentation checks.


ADR-073 raw safety stage: compare nine raw code/type and stored-expression
metadata categories before any PostgreSQL expression/definition deparser. This rejects
changed type I/O routines and unknown raw expressions before they could be invoked by
constant formatting. Render only the checked expected four dynamic code templates;
never normalize live code. Both stages return only counts/digests. Savepoint rollback
restores local settings on mismatch/query failure; success restores them explicitly.
The explicit fresh-migration generator can create the initial raw expectation, while
the runtime verifier must load it from the versioned artifact. The32 full metadata
categories are supplemented by these nine safety categories, not silently redefined.
Pinned PostgreSQL/vector core and the privileged creator/host remain trusted; this does
not claim protection from a hostile administrator controlling the engine or artifact.


The raw stage also covers trigger qualifiers, policy/rule expressions and partition
bounds before their full deparsers run. PostgreSQL16's get_const_expr calls a type's
output function; see the primary [PostgreSQL deparser source](https://github.com/postgres/postgres/blob/REL_16_STABLE/src/backend/utils/adt/ruleutils.c).
Reject changed raw trees or code/type interfaces before invoking those routines. This
supports the guard ordering, not a claim that a catalog hash secures a hostile engine.
