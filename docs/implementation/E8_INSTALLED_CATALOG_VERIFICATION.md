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
