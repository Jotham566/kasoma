# ADR-076: Portable raw catalog Datum octets

Date: 20 October 2026 (Africa/Kampala)
Status: Accepted technical correction under approved ADR-061/073; verification pending
Requirements: FR-ID-006, BR-010, NFR-SEC-002, NFR-MNT-001

## Evidence and decision

Hosted39371164944 fails42 integration cases in catalog/bootstrap/plans. A controlled
fresh-source reproduction uses ARM64 and AMD64 variants from the same immutable
pgvector0.8.2/PostgreSQL16 image index, both server160014. All32 full categories match
the frozen artifact; only raw constraints differ. The existing guard accepts ARM64
and refuses AMD64. A known1000 constant emits232 on ARM64 and-24 on AMD64 for the
same byte. Both exact source containers are independently absent after cleanup.

PostgreSQL's [outDatum implementation](https://github.com/postgres/postgres/blob/REL_16_STABLE/src/backend/nodes/outfuncs.c)
prints each Datum byte through C char converted to int. Raw integer notation thus
depends on char signedness. This is not permission to ignore an unexplained catalog
difference, omit raw constraints, invoke deparsers early or learn a baseline from an
existing source.

The initial scalar SQL codec triggers disproportionate JIT compilation: a fresh
native EXPLAIN/ANALYZE measures1359.25 ms with JIT versus20.14 ms without, same
estimated cost1276734.46. Disable JIT only locally during the catalog snapshot and
restore its previous setting on success; savepoint rollback restores it on failure.
Keep the existing5-second statement/100-ms lock budgets. This is a catalog microcheck,
not a learner-load, provider or production performance acceptance result.

Canonicalize only decimal octets inside the exact constvalue array serialization
in the closed set of raw pg_node_tree fields. Values from-128 through255 map to their
unsigned eight-bit representation; preserve every octet, its order, declared length
and all surrounding tree text. Invalid octets must not compare equal to an approved
tree. Keep nulls, all other metadata and live function bodies unchanged. The four
approved owner-dependent code templates remain exact expected-body comparisons.

Perform this entirely inside PostgreSQL using fixed compiled SQL and a closed regex
parameter. No source rows, raw live trees, function bodies or credentials leave the
verifier. No custom type I/O or definition/expression deparser runs before all nine
raw categories match. The32 full categories still follow. No catalog DDL, temporary
function or caller-supplied SQL/field/pattern is introduced by the verifier.

Version the codec in a v2 pre-install artifact and fresh private capability v5.
Keep the historical v1 artifact/SQL recipe; refuse older private readiness versions
without adopting or upgrading an existing scope. Reproduce the new artifact explicitly
from approved migrations in a fresh owned fake-only source, then independently check
both image variants. Never relax a timeout/assertion or regenerate on ordinary startup.

## Acceptance and exclusions

Prove old AMD64 refusal, unsigned/signed equivalence with changed-byte/non-octet
rejection, unchanged full metadata, raw rejection before deparsers on same-length
constant drift, all existing metadata/ACL/role/body denials, actual private logins,
version refusal, clean/additive migrations and complete own engineering verification.
Cross-platform probes create only exact owned synthetic resources from approved
immutable variants; normal review images, services, SDKs, caches and volumes remain.

This corrects a reproducible representation defect, not erasure clearance. Full
installed SQL/ACL/payload/preservation/export guards, credential-consumer completion,
durable erasure/checkpoint recovery and external release gates remain. Activation
stays false; no normal review, real data or production permission is inferred.
