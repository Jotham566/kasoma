# ADR-079: Independently reproduced installed catalog expectations

Date: 20 October 2026 (Africa/Kampala)
Status: Accepted technical implementation under approved ADR-061/071/072/073; implementation in progress; typed binding groundwork verified locally only
Requirements: FR-ID-006, FR-OPS-003, BR-010, NFR-SEC-002, NFR-MNT-001

## Decision

Complete the installed application-catalog fence before adding closure authority.
Use a fresh-only v7 recipe. Keep the public0045 model and all false execution flags.
Do not adopt v1-v6 installations or regenerate expectations during ordinary startup.
Keep the existing v2 pre-install guard and artifact unchanged.

Add one immutable private technical expectation field to control. It contains the
checked artifact identity, category counts/digests and exact expected code/expression
hashes rendered by the trusted creator from versioned templates and verified source
bindings. It contains no learner records, preservation bodies, contacts, credentials
or new secret. There is no update/reseal/relearn operation. The owner-only first
initializer accepts this field alongside the existing private fingerprint key; its
error handling continues withholding rejected rows and keys.

This separates expected data from checker code. Hash the complete expected body of
every instance-dependent function, including the catalog checker itself, from the
trusted compiler's definitions. Store those hashes in the immutable field. Compare
complete live bodies inside PostgreSQL before representing them with an approved
metadata marker. Never normalize or replace strings in live code. All ordinary
nonvariable bodies remain covered by the frozen full/raw catalog fingerprints.

The runtime SQL checker compares nine raw safety categories before invoking any
expression/definition deparser, then all32 approved metadata categories. Extend the
scope to public, the exact private capability/crypto namespaces and any unexpected
application namespace. Preserve role/database/ACL/default privileges, constraints,
indexes, triggers, types, operators and the other approved categories. Canonicalize
only technical object references using exact independently bound namespace/role
identities. An arbitrary name/prefix cannot become a trusted object or principal.

For the closed variable constraint/default expressions, freeze complete raw-tree
templates from the independent generator. Render their typed constants from verified
database/namespace/role OIDs and the installation nonce/names. Retain every octet,
declared length and surrounding tree text, including parser locations; use ADR-076's
unsigned-octet representation. Fresh v7 DDL renders dynamic numeric OID literals as
fixed-width decimal tokens, preserving parse locations across independently created
sources. Reject values outside the checked template's supported type/range; do not
relax the tree or learn an unfamiliar value/shape from a live source. No new raw-tree
location normalizer or deparser-before-raw exception is authorized.

## Generation and authority boundary

The explicit repository generator creates only registered invocation-owned fake-only
sources and approved migrations/DDL. Capture metadata before the control initializer
and public handoff, then roll back every private definition/role. Generation never
returns usable capability credentials or a ready installation. Check every compiled
body and typed expression binding before writing an artifact. Independently reproduce
the resulting artifact in another fresh source with different technical bindings,
including both approved ARM64/AMD64 variants. Never approve a baseline from a normal
review/developer source or from the installation being accepted.

Ordinary fresh installation loads the checked artifact, renders expectations without
observing live code as authority, initializes the immutable technical field and then
must pass its SQL fence before the existing sole metadata handoff. SQL scope identity
requires both principal and catalog predicates; private readiness/plan/version/expiry
therefore independently refuse drift before writes. Keep fixed qualified names,
bounded metadata queries, local JIT control and payload-free errors/results. No caller
supplies a baseline, actor/subject override, clock, namespace, expression or SQL.

The trusted creator, versioned artifact and pinned engine/extensions remain the
existing verification roots. This does not claim protection from a hostile privileged
host controlling them. Real-data/normal-review/production exclusions remain.

## Acceptance and remaining work

Prove fixed-width numeric semantics and exact raw constant rendering; independent
fresh reproduction with varied OIDs/nonces; full-body/private-checker tamper denial;
changed constraints, trigger/code/type/policy/rule/operator/ACL/role/namespace refusal;
raw failure before deparsers; immutable expectation/control denial through actual
logins; healthy plan/expiry and original temporary-shadow behavior; legacy refusal;
clean/additive public migrations and complete own engineering/hosted verification.

Installed catalog integrity alone does not validate learner payload versions or
ownership, exact preservation/holds, export drain or finite disposition. Those gates
and permanent closed-write guards still precede atomic durable authorization/closure,
bounded removal, checkpoint/quarantined recovery and DELETE completion. No erasure,
retention permission, real-data processing or release approval is introduced here.
