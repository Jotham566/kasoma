# E6 request-local progress replay reuse

Date: 19 October 2026. Candidate, not application acceptance.
Requirements: FR-MST-004/005, NFR-PERF-001, NFR-MNT-001.

## Comprehension and boundary

[ADR-024](../decisions/ADR/024-progress-history.md) and specification 05 remain
unchanged. Progress currently replays identical skill evidence independently for
subject, topic and competency rollups, including before/after change comparisons.
Reuse an immutable estimate only within one authorized read at its single explicit
calculation timestamp. Do not add a shared cache, stored aggregate, query limit,
new DTO, migration, algorithm version or academic threshold.

The existing API authorization, current consent, subject filter and completed-only
diagnostic evidence query remain authoritative. A subsequent read must create a
fresh context, including after consent/evidence/time changes. The pure context
copies its input grouping and never owns a database connection or learner identity.
Corrupt, conflicting and future evidence must continue to fail closed.

Affected components: progress engine/context and the existing progress service;
contract/operation-count and API isolation tests; Makefile, sprint, traceability,
changelog and this verification record. No unresolved specification conflict or new
architectural decision is identified. Existing mutable summary DTOs must not be shared.

## Planned evidence

Freeze complete legacy summary fingerprints before changing the engine, across empty,
prior, sparse, dense, duplicate, mixed mapping and decayed evidence. Compare exact
summaries, input hashes and latest-attempt change semantics across overlapping scopes.
Verify repeated requests/timestamps/input mutation cannot reuse stale results and that
identical skill/evidence/time replays occur only once within a request. Run existing
progress authorization/sealed-diagnostic/read-only and browser checks, broader quality
and hosted verification. Timing is local engineering evidence, not an agreed hosted
MVP-load or academic acceptance claim.

## Initial results

Before engine changes, 31 full-summary SHA-256 fingerprints were frozen from source
`0a8f674` in `tests/fixtures/progress-rollup-v1-reuse-baseline.json`. Seven scenarios
cover 31 scopes, including different scope-specific latest attempts. The first
unit run passes the seven legacy fingerprint cases and fails the 12 new reuse cases
because the context is not implemented. After implementation, all 19 new cases and
all 1,074 unit/contract plus 35 tooling cases pass. No expected fingerprint changes.

`make test-progress` passes all 31 focused cases: six existing engine cases, 19 new
replay cases and six PostgreSQL API cases. The API spy confirms each request computes
its own estimates, without duplicate identical skill replay, and repeated reads
remain fresh. Consent/subject/learner isolation, evidence read-only behavior and
completed-only diagnostic visibility still pass.

The dense four-skill, five-scope case requires 24 legacy replays (current/before
across overlapping scopes), versus eight distinct request-local replays. Repeating
all scopes in that same context requires no additional skill replay. Complete DTO
fingerprints, evidence hashes, recency, confidence and change states remain identical.
The context copies input grouping; returned mutable summary changes cannot poison
subsequent results. Corrupt/future/conflicting inputs still reject on repeated calls.

Full backend/browser, image/service, security and complete hosted checks remain in
progress. No complete MVP, hosted latency or academic acceptance is inferred.
