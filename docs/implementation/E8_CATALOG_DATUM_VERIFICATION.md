# Portable catalog Datum verification

Requirements: FR-ID-006, BR-010, NFR-SEC-002, NFR-MNT-001.
Decision: [ADR-076](../decisions/ADR/076-portable-catalog-datum-octets.md).
Status: local engineering verified; complete own hosted acceptance pending.

## Reproduction and correction

Catalog source854afaa hosted39371164944 fails42 integration cases/552 pass;
LOGIN source4e5b2ab hosted39373055520 separately fails42/570. Both pass their
1,495 unit/contract and35 tooling checks; neither completes the remaining hosted
gates. Keep these failures and their original heads rather than rerunning them as
an explanation or inferring acceptance from local tests.

Two controlled fresh PostgreSQL160014 sources from the same approved immutable
image index reproduce v1 acceptance on ARM64 and rejection on AMD64. Only raw
constraints differ; all32 full metadata categories match. A known1000 literal
emits232 versus-24 for the same eight-bit value. This agrees with PostgreSQL's
[Datum serializer](https://github.com/postgres/postgres/blob/REL_16_STABLE/src/backend/nodes/outfuncs.c),
which prints C char values as integers. Normalized octets now match on both variants.
All existing full/native raw fingerprints, four approved code templates and ordinary
migration hashes remain identical to the historical v1 artifact.

The v2 artifact/private v5 recipe canonicalizes only constvalue octets in twelve
closed raw-tree fields, within PostgreSQL. Bits/order/declared length and surrounding
tree fields remain. Function bodies and all other metadata stay strict. Invalid
octets cannot compare equal to approved data. No live trees or source rows leave
the verifier, and no deparser runs until all nine raw categories match. The32 full
categories remain required. Historical v1 artifacts/SQL remain; no old installation
is adopted. This is a pre-install guard, not installed SQL/ACL/erasure clearance.

## Local gates and limitations

make update-erasure-catalog-baseline explicitly generates the artifact only from
standard migrations in a fresh owned fake-only source. Independent reproduction and
the actual guard pass. make erasure-catalog-portability checks both fixed immutable
ARM64/AMD64 manifests on the supported M4, including changed-constant refusal before
full deparsers, restored source, false activation, zero learners/jobs and exact cleanup.
It accepts no caller image/URL/scope and does not install erasure authority. CI now
runs native fresh reproduction/guard checks before its broader integration stage.

An EXPLAIN/ANALYZE microcheck finds1,359.25 ms with JIT versus20.14 ms without, at
the same estimated cost1,276,734.46. JIT is disabled locally for catalog inspection,
then its prior setting is restored on success or savepoint rollback. The5-second
statement and100-ms lock budgets are unchanged. Success/failure restoration tests
pass. These measurements do not prove learner/provider/production performance.

Local commands pass: make format/lint, erasure-catalog-baseline,
erasure-catalog-portability, test-erasure-catalog (28), test-erasure-plans (23),
test-erasure-fresh-scope (11), test-unit (1,502 unit/contract and35 tooling),
openapi-check, build, security and security-source. Strict typing covers230 Python
sources. The initial security scan flags five script assertions; explicit fixed-error
checks replace them, with no scanner suppression. Paired/script/security rechecks pass.
Generated contracts match; there is no public migration/dependency change. Standard
clean migrations run in every new source; additive regression remains required in CI.

make e2e passes123 executions:108 standard,12 short-text and three configuration.
Twelve browser IDs and18 captured native/probe IDs are independently absent; normal
native contexts also assert their exact cleanup. No older resources are swept.
[Aggregate evidence](evidence/catalog-datum-controlled-evidence.json) records only
technical counts/digests/variant identity and the controlled probe, never learner data.

Own complete hosted642-integration/role/recovery/image/service verification remains
pending. Normal review stays on0045, eight services healthy and erasure/retirement/
ordinary short-text activation disabled. Guardian consumption, closed staff revocation,
full installed-catalog/SQL/payload/preservation/export enforcement, durable removal
and external-checkpoint quarantine recovery remain. Academic/privacy/provider/device
and production release acceptance is not inferred from this correction.


## Frozen portable-catalog combined source

Exact9fece6ad03662eb6ba7f1a9b6f0d79037b364c0b is pushed on
codex/catalog-datum-portability for complete own hosted39378996412, confirmed live.
Preserve that remote head; only Markdown/aggregate evidence closeout follows its
runtime/test/Make/workflow tree. Local engineering and123 browser executions pass;
full native Linux642 integration, restricted-role, recovery, image/service and all
remaining hosted gates are still required. Main remains37be6e3 and its separate
follow-up39374776606 is not acceptance of this v5 correction. Catalog854afaa and
LOGIN4e5b2ab remain failed at their exact recorded runs; linked2c37d4d has its own
separate run39375073567. No failure is silently superseded by local or parent checks.
Normal review stays eight healthy services on0045, with erasure/retirement/normal
short-text disabled. Host-native Ollama connectivity passes without inference.
Next complete guardian-consumption/closed staff-revocation guards and the full
installed SQL/payload/preservation/export/erasure/checkpoint lifecycle. External
academic/privacy/provider/device/production acceptance remains genuine required work.


Linked parent39375073567 is now terminal FAILED at exact2c37d4d:1,501
unit/contract and35 tooling pass;42 integration fail/597 pass. Its catalog/
bootstrap/plan failures remain failures and later full-browser/security/image/
service acceptance is unexecuted. All three older catalog-dependent candidates
therefore retain failed hosted evidence; none is promoted or rerun as a substitute
for the corrected source's own complete39378996412 verification. The controlled
two-architecture reproduction/correction is local proof of the serialization defect,
not a claimed successful hosted result for any old head.


## Complete hosted portable-catalog/credential verification

Complete own hosted39378996412 is SUCCESS at exact
9fece6ad03662eb6ba7f1a9b6f0d79037b364c0b:1,502 unit/contract,642 integration,
35 tooling and123 full browser executions, plus every required setup/migration/seed,
independent fresh catalog, focused transport/assessment/staff, actual restricted-login,
quality/contracts/build/security/image/service gate. The conditional registry login
alone is legitimately skipped when optional credentials are absent; no engineering
stage is skipped. Logical recovery verifies74 tables/692 rows in633ms; stopped-source
PostgreSQL/MinIO verifies74/692/one42,084-byte ciphertext in381ms with integrity/fault/
immutable/dormant checks and empty cleanup. Production RPO/RTO and erasure checkpoint
recovery remain false. No new learner-load or physical/branded acceptance is inferred.

This accepts corrected unsigned raw Datum serialization, pre-install32+9 catalog
verification/private v5 provenance, retained-closed LOGIN guards and the actor/bound-
recipient LINK/GUARDIAN dispatch/cleanup guards at this combined source. Earlier
catalog854afaa/39371164944, LOGIN4e5b2ab/39373055520 and linked2c37d4d/39375073567
remain FAILED at their own exact heads; no failure is relabeled or rerun to hide it.
The current native two-architecture reproduction supplies the correction's separate
mechanism evidence. Only Markdown follows the verified runtime/test/Make/workflow
source on the prepared publication branch. Parent main37be6e3 follow-up39374776606
is separately SUCCESS and remote/main ancestry is checked before publication.

Consumer1597a68/39380895685 and principal4bf5a77/39383925992 remain separate live
candidates; neither is accepted by this run. No actual closure, new preservation,
retention, erasure, normal short-text or retirement activation occurs. Full installed
catalog/payload/ownership/hold/export clearance, permanent barriers, bounded durable
removal/checkpoint recovery and external release gates remain required.


Prepared publication also passes native make containers migrate container-smoke
security-containers on the verified runtime tree: worker/private-object export,
request/model telemetry and service smoke pass; image scans pass. All eight review
services are healthy on0045. Only Markdown closeout differs from exact9fece6a;
no extra application/test/Make/workflow change is accepted by this publication.
Main publishes this verified source; its new follow-up run requires separate status.
Consumer1597a68 and principal4bf5a77 remain unmerged until their own acceptance.
