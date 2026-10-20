# Synthetic erasure pre-install catalog verification

Requirements: FR-ID-006, FR-OPS-003, BR-010, NFR-SEC-002, NFR-MNT-001.
Decision: [ADR-073](../decisions/ADR/073-frozen-preinstall-source-catalog.md).
Status: local candidate; full own hosted acceptance remains pending.

## Boundary

The versioned public 0045 baseline is reproduced only from standard migrations in
an exclusively created fake-only source. The installer compares nine raw safety
categories before 32 full metadata categories and before creating any private role,
schema or key. A source cannot approve itself. Exact expected code templates cover
four database-specific retirement-owner literals; live bodies are never normalized.
Fresh private capability v4 records this prerequisite and reuses v3 SQL. Older
capabilities are refused by the current API readiness contract, without adoption.

This is a pre-install metadata fence. It does not implement installed SQL/ACL
revalidation, payload/hold/export clearance, closure, removal, DELETE completion,
erasure checkpoint recovery or production permission. Normal review remains 0045
with erasure, retirement and ordinary learner short text disabled.

## Local evidence

The body-only closure-guard regression initially fails because the previous installer
accepts the changed function (one failure/six passes). The final nine-stage source
passes 25 catalog cases, 22 private-plan cases and 11 fresh-scope/bootstrap cases.
The catalog cases include two independently created equal baselines, synthetic row
writes, connection-setting restoration and 18 metadata mutation classes. A statement
observer proves body drift is rejected before the full deparser stage. Actual native
contexts assert exact owned-container absence after successful cleanup.

make erasure-catalog-baseline and make lint pass with 228 strictly typed Python
sources. make test-unit passes 1,495 unit/contract and 35 tooling cases. Generated
OpenAPI/client comparison and build pass. The first final security scan flags three
subprocess findings in the new generator. The generator now uses the existing bounded,
fixed-error command helper; baseline reproduction, lint, dependency security and source
security rechecks pass. No scanner suppression is added. Full browser and own hosted
results are not inferred from these checks.

## Interrupted run and exact owner-authorized cleanup

The preceding nine-stage native run loses its process after five contract cases and
one native progress marker. It has no terminal result and is not a pass. The later
complete 25/22/11 execution is a separate recheck, not a correction of that history.

The interruption also leaves synthetic PostgreSQL container
91c93448d8156695319097ff17e29cc9094e7265cb530d84bcbc809619559eff without its
original in-process creation receipt. Labels alone do not establish cleanup ownership.
The owner explicitly approves removal of this exact full ID. It is re-inspected for
that identity, its original synthetic invocation label, 512 MiB limit and no persistent
mounts before removal; a separate full-ID inventory confirms absence. This grants no
authority over other orphaned resources, volumes, images or SDK caches.

All eight normal review services are independently healthy after recovery and
make container-smoke passes. Host-native Ollama is restarted with the repository
command; make ollama-check passes without inference. No model or messaging evaluation
is performed. Production recovery and physical/branded-device acceptance remain open.
