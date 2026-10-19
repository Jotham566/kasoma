# Fresh revision response — verification candidate

Requirements: NFR-PERF-001/002, FR-REV-001/002/005/006, FR-GRD-008,
FR-WA-003, NFR-MNT-001 and NFR-SEC-002.
Status: bounded synthetic engineering verified by complete hosted 39286019222 at 58d598e.

## Change and boundary

A newly created REVISION in the shared locked start transaction has neither attempts
nor a reassessment link. The old response builder nevertheless selects both. The
candidate uses one shared SessionView constructor with an empty answer list for only
that transaction's new revision; receipt retries and active-plan resumes still read
current committed evidence through the ordinary view path. Reassessment provenance
reads and grade serialization remain unchanged. The original final flush, receipt,
outbox, content locks, consent/role checks and transaction/commit owner remain intact.

This implements the existing [ADR-046](../decisions/ADR/046-shared-assessment-content-locks.md)
performance direction within unchanged ADR-021/023/035 behavior. No new ADR, API/schema,
cache, warm-up, provider, grading policy, timeout or latency threshold is introduced.
It does not implement or approve proposed ADR-061. The proposal branch is the parent
of this independent performance branch so its reviewable documents remain available;
no erasure code, permission, migration or runtime activation accompanies this change.

## Meaningful regression evidence

Before runtime edits, corrected API-contract assertions yield three failed/one passed
focused tests: TOPIC/WEB, RECOMMENDED/WEB and TOPIC/WHATSAPP each perform exactly the
two empty response SELECTs. Existing-answer resume already passes. An initial test
expected 201 rather than the existing 200 answer status; that test error was corrected
before recording this baseline. The tests inspect only statement-shape labels, never
parameters, answers or identifiers.

After the candidate, all four focused tests pass in 13.66s. Each fresh complete serialized
response equals an independent committed database view. Both same-key and new-key
resumes still perform the two reads and recover the full view. The HTTP answer/resume
regression preserves the exact submitted grade and answer count, rather than incorrectly
returning an empty fresh response. The standalone topic-required validation order is
preserved. Broader transaction, consent, channel, reassessment and lock suites follow.

## Commands and outstanding checks

- `make test-fresh-session-response`: now includes the four focused cases and existing
  assessment, recommendation, reassessment, shared-transaction, content-lock and channel
  integration suites. The initial focused-only result is separate from the expanded 40-case pass below.
  Neither is a claim of a complete 483-case native integration run.
- Expanded `make test-fresh-session-response`: 40 integration cases pass in 165.05s,
  including transactions/rollback, authorization/consent, recommendation/reassessment,
  content-lock races and channel grading/mastery parity.
- `make format`, `make lint openapi-check build` pass; generated contracts are unchanged.
  `make test-unit` passes 1,130 unit/contract cases and 35 tooling cases. Existing three
  unit warnings remain (TestClient deprecation and two intentional network denials).
- `make test-web-assessment`: nine browser executions pass, three per engine:
  Chromium 20.2s, Firefox 23.2s and WebKit 19.3s. These are the focused journeys, not a new
  complete 111-execution browser or branded/physical-device acceptance claim.
- `make security security-source` passes: dependency audits report no known
  vulnerabilities and source Gitleaks reports no leaks. Image/service checks also pass; full hosted regression remains pending.
- Both standard native load profiles pass sequentially after other checks finish.
  Retain every failure and unchanged per-operation thresholds; do not claim that two
  fewer queries fix the previously unexplained START p95 variance.

The original corrected-source history miss at 559.306ms remains failed. The previously
passing 448.045ms recheck is not acceptance of this candidate. Full agreed-load/provider/
soak/production acceptance and genuine academic/privacy/safeguarding gates remain open.
Normal Docker services remain running on 0042, with review retirement false.

## Native candidate source and first load result

Application/test/Make source `58d598eb77196d28844f156165488175e26a1dcb` is committed
and pushed. Complete hosted 39286019222 now passes at that exact source; see acceptance below. Main 4377da5 publishes only the
checked Proposed ADR-061/readiness/inventory documents; its runtime tree is unchanged
from the previously verified main baseline. The merged proposal branch is removed.
No erasure implementation approval has arrived.

`make containers security-containers container-smoke` passes; rebuilt API/worker/web
services are healthy. Standard native `make load-objective` passes: 7,000 HTTP requests,
zero errors, 500 completed learners/2,500 grades, 50 peak concurrent requests and successful
owned cleanup. START p95/p99 is 408.061/922.495ms; ANSWER p95 is 27.248ms; target 20 answers/s
(observed 19.992/s). Database resources are not measured. The source-pinned
[aggregate report](evidence/E9_FRESH_RESPONSE_OBJECTIVE_LOCAL_2026_10_19_58d598e.json)
contains no learner/source identifiers or payloads. The history result below completes this pair of native observations;
these runs do not explain prior variance or complete NFR-PERF-001 release acceptance.

## Mixed-history result and review runtime

Standard `make load-history-mixed` passes at the same runtime source, with 25,000 prior
grades and 27,500 final grades/5,500 completed sessions. All 7,000 HTTP requests succeed;
500 learners complete, peak concurrency is 50 and owned cleanup succeeds. START
p95/p99 is 422.913/924.864ms. Numeric/choice ANSWER p95 is 27.610/28.092ms, with 1,250 timed
answers per format. Target 20 answers/s is observed at 19.998/s. The source-pinned
[aggregate report](evidence/E9_FRESH_RESPONSE_HISTORY_MIXED_LOCAL_2026_10_19_58d598e.json)
retains the exact scope and database_resources_measured=false/production_acceptance=false.
No recheck or threshold/warm-up change was used for this candidate pair.

Read-only SHA-256 comparison of services/assessment.py in the rebuilt API, worker and
export-worker matches the local candidate: f9b8795780909bd20f31b470ffa448109d4fba43d264096037e3bf015a5d4959.
All eight services remain healthy; schema 0042/review retirement false are preserved.
Only Markdown and aggregate JSON closeout follows runtime/test/Make source 58d598e.
Do not push a replacement branch head while its exact hosted verification is running.
Promote runtime to main and remove its branch only after full hosted verification;
the proposal on main remains unapproved independently of these engineering checks.

## Complete hosted acceptance — 19 October 2026

[39286019222](https://github.com/Jotham566/kasoma/actions/runs/39286019222) completes
successfully at exact application/test/Make source 58d598eb77196d28844f156165488175e26a1dcb.
It passes 1,130 unit/contract, 483 integration (1,530.77s), 35 tooling and 111 full browser
executions, plus nine focused assessment, 12 transport controls, three staff UI, three
native WebKit, eight reviewed-rubric and one actual restricted-runtime-role checks.
Setup/migration/seed, lint/types/contracts/build, dependency/source/image security and
container/service smoke all pass. The optional registry-authentication step is skipped
when credentials are unavailable, as configured; no required gate is skipped.

Logical recovery verifies 69 tables/686 rows in 477ms, with no cleanup failures and
stripped-retirement execution denied. This is isolated synthetic logical recovery,
not object-storage recovery, production PITR/RPO/RTO or real-data authorization.
Only Markdown/aggregate JSON closeout follows this verified runtime/test/Make tree.
The separate practice-day API/UI candidate is not covered by this CI. ADR-061 remains
Proposed and unapproved. Native results remain observations, with the prior 559.306ms
history miss and unexplained variance retained; broad provider/deployment/soak and
production/academic/privacy release acceptance remain open.
