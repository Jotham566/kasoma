# E9 isolated objective HTTP load profile

Requirements: NFR-PERF-001, NFR-PERF-002, NFR-SCL-001. Local objective baseline passes;
full hosted regression passes; broader performance acceptance remains pending.

`make load-objective` creates a fresh randomly named local database, applies the repository
migrations and seeds original synthetic content. Only the standard development PostgreSQL profile
on loopback port 55432 is accepted. There is no supplied application URL, database-name override,
production mode or external provider. A failed CREATE never grants cleanup ownership. Cleanup
drops only the generated database successfully created by this invocation; no force-disconnect,
configured database reset or volume removal occurs. Failed cleanup makes the run fail.

The profile creates 2,000 synthetic verified learners and 288 independently reviewed original
software fixtures across six topic clusters. Five hundred consenting adult synthetic learners run
five-question objective sessions through real loopback HTTP, with at most 50 active journeys.
An answer pacer targets 20 dispatches/second and does not deliberately catch up after delays.
Record achieved dispatch rate and lateness rather than treating the target as measured throughput.
Each successful answer must receive the expected deterministic score and completed mastery update.
Final checks require 500 completed sessions and exactly 2,500 attempts/grades.

Preparation runs the existing domain workflows outside the timed interval. Timed operations include
profile reads, session creation, question retrieval, submission, saved state and progress. HTTP timing
includes response-body receipt and local transport; it excludes client pacing waits. Report nearest-rank
p50/p95/p99 per operation and overall, errors, completion counts, maximum simultaneous HTTP requests,
elapsed time, combined client/API CPU time and process peak RSS including fixture setup. Database
container resource use is explicitly not measured. Existing application limits, database pool and
observability remain unchanged; there is no latency adjustment or suppressed failed sample.

The command fails unless all learners complete without errors, peak in-flight HTTP reaches 50,
every non-AI operation and the aggregate p95 are below 500 ms, and objective-answer p95 below
1,500 ms. A fast frequent operation cannot hide a slower route. It uses a finite
300-second timed-workload deadline and ten-second client request timeout. These harness limits are
not application configuration changes or revised acceptance thresholds. Output contains aggregate
metrics and closed stage names, never bearer tokens, identities, answers, request URLs or exception
payloads. Default application telemetry remains enabled and minimized.

Run `make test-load-profile` for deterministic isolation/cleanup, percentile, HTTP-error minimization
and pacing checks; all requests there use httpx MockTransport. The script is included in strict mypy.
The harness itself changes no runtime API, schema, retention or provider decision. New temporary
fixture databases use the already tested local-only boundary from the recovery drill. The measured
assessment optimization is separately governed by [ADR-046](../decisions/ADR/046-shared-assessment-content-locks.md).

This is an objective engineering baseline, not full performance or scale acceptance. It compresses
500 active learners into one run rather than a 24-hour soak, begins with empty learning histories,
uses one objective response format, and omits delayed/failed model or messaging providers. Shared
host/database resources, representative long histories, numeric workloads, deployed network and
provider scenarios must be measured separately. Synthetic review is not academic approval.

Initial `make format test-load-profile typecheck` passed 16 deterministic cases and strict type
checks. The first full-size native run completed 7,000 HTTP requests, 500 sessions and 2,500 grades
with zero errors and successful cleanup. Mixed API p95 was 30.115 ms and answer p95 29.219 ms, but
START p95 was 652.530 ms. Its initial aggregate-only PASSED label is not accepted as requirement
evidence: the per-operation gate now rejects that result. No threshold was relaxed.

ADR-046 replaces exclusive immutable-content read locks with FOR SHARE (still conflicting with
non-key retirement updates), and manual topic practice queries only its selected topic. The
content eligibility and final locked refresh remain authoritative. `make format lint test-load-profile
test-assessment-locks` passed 18 harness cases and four PostgreSQL lock/filter regressions. The final full-size run and hosted regression results are recorded below.

## Final native objective baseline — 9 October 2026

The bounded-topic change alone still measured START p95 523.881 ms and correctly failed.
ADR-046 now also batches the final version lock/eligibility check for the selected plan in the
content boundary, preserving its original order and rejecting every missing/foreign/retired or
short-text reference. Six PostgreSQL regressions verify concurrent readers, exclusive writers,
non-key retirement exclusion, stale eligibility, batch order/bounds/ownership and topic filtering.
The reviewed-rubric suite additionally exercises batch short-text rejection.

The final pacer compensates for normal timer jitter while skipping missed intervals rather than
releasing a catch-up burst. Nineteen deterministic harness tests pass, including both cases and
the rule that a slow operation cannot hide in mixed latency. The final full-size native run passed
with the unchanged application pool, timeouts and observability. The test ran on the supported M4
Mac Mini while unrelated dependency downloads remained active; deployed performance is separate.

| Operation | Samples | p50 ms | p95 ms | p99 ms |
| --- | ---: | ---: | ---: | ---: |
| Profile | 500 | 4.020 | 223.107 | 258.647 |
| Session start | 500 | 12.284 | 440.633 | 1039.280 |
| Next question | 2500 | 10.773 | 15.755 | 235.470 |
| Objective answer | 2500 | 19.587 | 27.221 | 64.172 |
| Saved state | 500 | 8.475 | 10.887 | 13.329 |
| Progress | 500 | 9.107 | 11.323 | 14.782 |
| All HTTP | 7000 | 12.015 | 26.580 | 275.163 |

All 500 sessions completed, with exactly 2,500 attempts and grades, zero measured errors and no
cleanup failure. Maximum in-flight HTTP was 50. Actual answer dispatch averaged 19.996/s against
the 20/s target; dispatch-lag p95 was 2.179 ms. Timed duration was 125.375 seconds; combined API/client
CPU was 50.522 seconds and peak process RSS, including setup, 138,395,648 bytes. Database/container
resources were not measured. [Machine-readable aggregate report](evidence/E9_OBJECTIVE_LOAD_LOCAL_2026_10_09.json).

The startup p99 remains about one second despite passing p95; retain it as a tuning/risk signal.
This finite local result does not close the representative-history, numeric/provider, soak, resource
and production release gates described above.

`make format lint test` passed 450 unit/contract and 195 integration cases, including the new
concurrency checks, reviewed-rubric batch exclusion and restricted assessment-role regression.
Only `test_local_storage_and_mailpit` failed because the native MinIO service remains unavailable.
`make openapi-check build security` passed, with no known Python/JavaScript vulnerabilities.
`make migrate recovery-drill` passed (54 tables/272 rows, 238 ms restore, pgvector/immutable guards,
no cleanup failures). Documentation links/whitespace pass. The native environment failure is not treated as a full native pass.


## Hosted regression and promotion

Hosted CI [37933227560](https://github.com/Jotham566/kasoma/actions/runs/37933227560)
passed at `f2dbf8a`: 450 unit/contract and 196 integration cases (646 Python), five tooling,
66 real-API browser executions and one isolated UI case. Setup, migrations, seed, lint/format/types,
contracts, build, role/security/source/image checks and container smoke passed. Isolated recovery
restored 54 tables/272 rows in 452 ms with pgvector and immutable guards and no cleanup failures.
Cold question transfers were 191532/194232/193633 bytes, below 250000 in every engine.
The commit is on main; its branch was removed locally/remotely. This CI verifies regression,
not a production rerun of the native load measurements above.
