# E6 request-local progress replay reuse

Date: 19 October 2026. Synthetic engineering verified at `7148a1c`; complete
hosted [39184552472](https://github.com/Jotham566/kasoma/actions/runs/39184552472) passes. It is merged to main with verified descendant `6d53541`; no full MVP acceptance.
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

Freeze complete legacy summaries before changing the engine, across empty,
prior, sparse, dense, duplicate, mixed mapping and decayed evidence. Compare exact
summaries, input hashes and latest-attempt change semantics across overlapping scopes.
Verify repeated requests/timestamps/input mutation cannot reuse stale results and that
identical skill/evidence/time replays occur only once within a request. Run existing
progress authorization/sealed-diagnostic/read-only and browser checks, broader quality
and hosted verification. Timing is local engineering evidence, not an agreed hosted
MVP-load or academic acceptance claim.

## Initial results

Legacy full-summary fingerprints were frozen before engine changes from source
`0a8f674`; the portable oracle later re-executes that same original source and stores
all 31 complete summaries in `tests/fixtures/progress-rollup-v1-reuse-baseline.json`. Seven scenarios
cover 31 scopes, including different scope-specific latest attempts. The first
unit run passes the seven legacy summary cases and fails the 12 new reuse cases
because the context is not implemented. After implementation, all 19 new cases and
all 1,074 unit/contract plus 35 tooling cases pass. No input-hash or nonnumeric expected-field changes.

`make test-progress` passes all 31 focused cases: six existing engine cases, 19 new
replay cases and six PostgreSQL API cases. The API spy confirms each request computes
its own estimates, without duplicate identical skill replay, and repeated reads
remain fresh. Consent/subject/learner isolation, evidence read-only behavior and
completed-only diagnostic visibility still pass.

The dense four-skill, five-scope case requires 24 legacy replays (current/before
across overlapping scopes), versus eight distinct request-local replays. Repeating
all scopes in that same context requires no additional skill replay. Complete DTO fields (with machine-precision numeric tolerance), evidence hashes, recency, confidence and change states remain identical.
The context copies input grouping; returned mutable summary changes cannot poison
subsequent results. Corrupt/future/conflicting inputs still reject on repeated calls.

Complete hosted [39184552472](https://github.com/Jotham566/kasoma/actions/runs/39184552472) passes every gate: 1,074 unit/contract, 412 integration,
35 tooling, 108 browser executions, UI/transport, recovery, security/images and
service smoke. Hosted logical restore verifies 68 tables/680 rows in 613 ms.
No complete MVP, agreed-load hosted latency or academic acceptance is inferred.

## Cross-platform fixture correction

The first portability probe finds 15 mismatched full-DTO hashes between native macOS
and the Linux application image. Replaying the unchanged original `0a8f674` engine
inside that image reproduces exactly the optimized outputs for all 31 summaries.
The original engine itself differs from macOS by at most 1.1102230246251565e-16 in
mastery/confidence (platform libm rounding), so a full-float JSON hash is not a valid
portable oracle. The fixture now stores the original complete summaries; hashes,
labels, counts, IDs and timestamps compare exactly, while only mastery/confidence
use absolute 1e-15 tolerance with zero relative tolerance. No product threshold,
formula, expected input hash or eligibility decision changes. The initial fingerprint
probe is failed portability evidence, not an implementation-equivalence failure.

A Linux application-image probe compares the original source and optimized results
exactly within that platform and confirms all nonnumeric frozen fields match. On
48 synthetic evidence rows across five overlapping scopes, 30 samples per variant
measure median pure-rollup time 29.959 ms before and 5.103 ms with request-local
reuse. These timings include fresh grouping/cache construction but exclude API,
authentication, SQL and hosted concurrency; they do not establish NFR-PERF-001's
full agreed-load p95. No provider or learner data is involved.

The first broader browser run passes both Chromium batches and 15/16 in its first
Firefox batch. The existing cross-device assessment journey observes a Next question
click without a subsequent API request. Its unchanged full Firefox recheck passes
both 16-case batches. The trace and failure remain recorded; no timeout, assertion
or product code is changed to mask it. Subsequent complete WebKit/short-text and
hosted matrices pass; the intermittent pointer-event cause is unconfirmed.

The broader local integration run passes 411/412; its sole failure occurs while
provisioning the privileged temporary database test role, before application checks.
The wrapper withholds server diagnostics to protect the generated password. A
standalone unchanged `make test-runtime-role` recheck passes in 12.90 seconds, and
the complete clean hosted run passes all 412 integration cases. No grant, permission
assertion or timeout is broadened. The underlying local fixture cause is unconfirmed.
The final complete local `make e2e` on descendant `6d53541` also passes all 108
executions, including the shared-selector styling follow-up.

Latest descendant `6d53541` also passes complete hosted [39185423895](https://github.com/Jotham566/kasoma/actions/runs/39185423895). It is pushed to main;
both follow-up branches are removed locally/remotely. Subsequent commits are
Markdown-only and preserve that exact application/test tree.
