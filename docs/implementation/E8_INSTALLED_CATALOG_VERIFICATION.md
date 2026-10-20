# Installed catalog expectations — implementation in progress

Requirements: FR-ID-006/FR-OPS-003, BR-010, NFR-SEC-002, NFR-MNT-001.
Decision: [ADR-079](../decisions/ADR/079-installed-catalog-expectations.md).

## Current implementation and limits

services/erasure_catalog_bindings.py renders exact expected raw-tree constants from
closed technical bindings. Ten explicit expression keys cover five int4 constraints,
one owner/executor constraint, one nonce constraint and three namespace/procedure
defaults (the owner/executor field contains two slots). The registry has ten fields
and eleven slots: six single constraints including nonce, one double constraint and
three defaults. No caller-selected table, expression or SQL is introduced. Actual
function bodies are never normalized. All nonbound bytes, declared lengths, types,
locations and surrounding raw-tree structure remain exact. Unknown/missing/duplicate
bindings, changed types/widths or unsupported OID ranges fail closed.

Fresh profile OIDs must fit the checked positive int4 representation. Fixed-width
decimal SQL tokens will keep parser positions stable in v7 DDL. Text slots retain
the exact four-byte varlena header and fixed width; nonce slots retain16 UUID bytes.
Only expected templates are rendered. The runtime verifier will load independently
reproduced templates; it must never freeze from the installation being accepted.

The v7 checker, artifact generator, immutable private expectation field and SQL
scope interlock are NOT implemented yet. Current private runtime remains v6.
No public/private schema, route/DTO, activation, custody, role permission, data
retention or provider changes. This does not establish installed-catalog clearance,
closure, erasure, checkpoint recovery, complete MVP or release acceptance.

## Actual evidence and retained failures

A fresh two-source metadata probe uses approved migrations/private v6 with fake-only
settings. One source consumes an invocation-owned temporary OID before installation;
the temporary table closes with its owned connection. Role OIDs/nonces differ. Both
sources verify fixed-width decimal expressions equal10/16384 and retain integer type.
Each exposes only fresh technical metadata (14 constraints/six defaults), never
learner rows, credentials or fingerprint keys; both exact containers clean successfully.
Ignored probe data has0600 mode. No normal-review or older schema/role/cache cleanup.

An initial formatting run fails four long SQL literals, corrected by splitting them.
Initial pytest collection fails because contract/integration modules share a basename.
Rename only the new contract module; no cache deletion, assertion or timeout change.
The prescribed make test-erasure-catalog-bindings passes12 cases:11 contract and one
native test using two independently created/cleaned sources. All ten frozen expressions
reproduce the second source exactly with changed OIDs, namespace names and nonce;
integer contracts also prove only bound octets change and parser locations remain.

make format lint test-erasure-catalog-bindings test-unit openapi-check build security
security-source passes:12 focused,1,513 unit/contract,35 tooling,232 typed files,
format/lint, generated contract equality, web build and security/dependency/source
checks.677 integration is collection only, not a full local integration pass.
No new browser claim is made from this groundwork. The root normal preview stays
healthy on0045 with erasure disabled. Full v7 native/matrix/own hosted/recovery/role/
image/service and application acceptance remain required after integration.

## Files and exact next implementation

Created the typed binding module, tests/contract/test_erasure_catalog_binding_contract.py,
tests/integration/test_erasure_catalog_bindings.py, ADR-079 and this report. Makefile
adds the prescribed target. Changelog, current sprint, traceability and decision
indexes are updated. Public API/contracts, migrations and dependencies are unchanged.

Next implement the trusted metadata-only fresh preparation path that rolls back
before initialization/handoff, independently reproduce the frozen installed artifact,
compile complete expected bodies and typed expressions from verified bindings, then
add the immutable expectation field and raw-before-full SQL checker/interlock. Test
its own body, code/constraint/type/trigger/policy/rule/operator/ACL/namespace drift
and actual private-principal refusals before any plan/expiry write. Full payload/
ownership/hold/preservation/export checks still precede atomic durable closure,
permanent write guards, bounded removal and checkpoint/quarantined restore.


## ADR-079 rollback-only preparation and independent metadata compiler

FR-ID-006/FR-OPS-003, BR-010 and NFR-SEC-002/MNT-001: the trusted offline
preparation path accepts only an actual registered FreshErasureScope, follows the
ordinary pre-install fences and creates private definitions inside one transaction.
It clears the temporary password GUC, captures technical metadata before generating
a fingerprint key or initializing control, then rolls back on normal return, error
or interruption. It returns no initialized capability, credentials or ready scope.
No callback, source URL, SQL or baseline is accepted from an application user.

The expected-code compiler hashes complete trusted repository definitions and the
four existing frozen public bodies. A PostgreSQL comparison checks all14 complete
v6 bodies before metadata observation; a replaced scope-identity body is rejected.
The metadata compiler covers all application namespaces with exact private technical
aliases, nine raw safety categories followed by32 full categories, and typed exact
expression hashes. Independent fresh preparations with changed OIDs/nonces reproduce
all category counts/digests. An initial function-ACL digest difference is retained:
the fixed technical function-signature reference had not been aliased. Correcting
that specific reference makes both stages reproduce; live code is never normalized.

A strict v7 artifact envelope pins the migration and trusted recipe source digests,
closed category/expression sets and exact recipe identity. Missing or changed files
fail rather than regenerating/adopting a baseline. No frozen v7 artifact is written,
no ordinary installer loads this envelope yet, and the private runtime remains v6.
The SQL checker, immutable expectation field, generator CLI/architecture matrix and
runtime raw-before-deparser interlock remain unimplemented. Producer reproduction
is not installed-catalog clearance, payload/hold/export validation, closure/erasure,
checkpoint recovery or production/MVP acceptance.


## Preparation checkpoint — local engineering results

Commands: make format lint; make test-erasure-installed-queries
(test envelope plus native reproduction/body refusal); make test-erasure-catalog-preparation;
make test-erasure-fresh-scope test-erasure-principals test-erasure-catalog-bindings;
make test-erasure-plans; make test-unit openapi-check build security security-source;
make erasure-catalog-baseline recovery-drill recovery-objects; make check-docs.
The six focused targets pass86 cases (9+9+11+21+12+24), including changed-code
rejection and normal/error/interruption rollback with exact-ID absence. Unit/contract
passes1,526; tooling35; typing236 files. Public generated contracts/build remain equal.
682 integration is collection only; no complete native integration or new browser
pass is claimed. Own full hosted verification remains required for this source.

Retain the initial mypy Literal default failure and correction, initial three
B608 static-SQL construction findings and their correction to psycopg composables.
The final format/lint, direct native reproduction/preparation/plan tests, secret,
dependency and source scans pass without adding scan exclusions. Earlier query/ACL
failures remain recorded; they are not application acceptance. No timeout/assertion
relaxation, external provider call or older resource cleanup occurs.

The fresh unchanged v2 pre-install catalog reproduces32 metadata/nine raw categories.
Logical recovery verifies74 tables/692 rows in341ms. Actual stopped-source database/
MinIO recovery verifies74/692/one42,084-byte ciphertext in144ms, integrity/fault/
immutable/dormant guards and cleanup[]. Production RPO/RTO remainsfalse; this is not
closure checkpoint recovery. Every fresh native source asserts exact cleanup; the
owner-approved orphan91c93448 is independently absent. The normal review remains
8/8healthy on0045 and no private installation/activation is performed there.

Created scripts/erasure_catalog_code.py, erasure_installed_queries.py and
 erasure_installed_profile.py; services/erasure_installed_profile.py; three contract
modules and two native modules. Changed the privileged installer, Makefile and mypy/
security scan scope, plus changelog/sprint/traceability/AGENTS/ADR verification records.
No public migration, dependency, DTO, runtime version or model/messaging change.
The accepted ADR-079 design remains unchanged. Next implement the v7-only private
field and raw-before-full SQL checker, independent artifact generator/matrix and
scope interlock before any closure authority; the current preparation is not that gate.


## Catalog preparation publication after complete own acceptance

FR-ID-006/FR-OPS-003/BR-010 and NFR-SEC-002/MNT-001: exactaf02686ee77064783c5ea8352b2899134da3a987
passes complete own [39393189109](https://github.com/Jotham566/kasoma/actions/runs/39393189109):
1,526 unit/contract,682 integration (2236.48s),35 tooling and123 full browser executions,
plus every required setup/migration/seed/focused/role/quality/contracts/build/security/
image/service gate. Logical74-table/692-row recovery573ms; actual stopped-source
PostgreSQL/MinIO74/692/one42,084-byte ciphertext316ms, fault/immutable/dormant guards
and empty cleanup. Production RPO/RTO remains false. Optional registry authentication
alone is legitimately skipped. Mainf8a2afb follow-up39395023461 also succeeds.

Publication merges this accepted preparation source with main's Markdown-only
closeout; all non-Markdown files equal exactaf02686. This accepts rolled-back fresh
preparation and typed expected metadata only. Separate v7 installed interlock and
ADR-080 TEMP type correction remain local candidates requiring their own full CI.
No closure, removal, DELETE completion or production acceptance is inferred. Existing
failures remain failures. Review services stay healthy on0045 with erasure disabled.
