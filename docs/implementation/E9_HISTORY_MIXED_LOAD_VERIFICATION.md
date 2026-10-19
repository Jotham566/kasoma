# E9 synthetic history and mixed objective HTTP load

Requirements: NFR-PERF-001/002, NFR-SCL-001, supporting FR-MST-004/005 and NFR-MNT-001.
Status: final-source native profiles and complete hosted regression pass at `6b06c53`.
This is bounded local engineering evidence, not full performance/release acceptance.

## Scope and assumptions

The testing specification requires representative mastery histories and numeric
workloads beyond the earlier empty-history choice baseline. `make load-history-mixed`
extends the existing isolated local harness without changing application behavior,
limits, database pools, content selection, authentication, grading or mastery math.
The existing `make load-objective` command retains its empty-history workload.
No new architectural decision is required for an additional synthetic test profile.

This fixed engineering fixture uses 2,000 registered learners and 500 active learners
with both MVP subjects selected. Each active learner completes ten five-question
sessions through normal domain transactions before the timed run: 25,000 prior
attempts/grades and 5,000 completed sessions in total. History traverses the selected
subject's topic clusters. Four answer trajectories exercise strong, weak, alternating
and improving evidence, with each trajectory represented in both subjects. These
are synthetic test patterns, not academic judgments or an approved population model.
Fifty recent answers per learner is a disclosed engineering assumption, not a new
retention limit or proof of long-lived, decayed or diagnostic-history performance.

Fixture preparation uses at most eight threads, outside HTTP timing, with the existing
pool and real domain transactions. Normal refresh-token rotation before each history
and after setup avoids expired preparation tokens; token lifetimes, OTP cooldowns and
the application clock are unchanged. Credentials remain in memory and out of reports.
Only the runner's original choice/numeric fixtures have a solver; other formats fail
closed. There are 288 original reviewed fixtures: 144 choice in Mathematics and 144
numeric in Physics, using the existing combined fixture switches. This guarantees
both formats without relying on random UUID ordering in a mostly-choice pool.
Synthetic review contributes nothing to academic release inventory.

## Timed workload and gates

Reuse 50 concurrent journeys, the 20-answer/second pacer, six operations, five timed
answers per learner, 300-second workload deadline and ten-second client timeout.
Mathematics and Physics plans are bound independently to their authenticated learner;
Physics targets Electricity and Magnetism with numeric questions selected by the
unchanged engine. The run must observe both SINGLE_CHOICE and NUMERIC submissions.
Every timed answer must score one with its mastery update completed.

Verify exact pre-run counts and final totals: 27,500 attempts/grades and 5,500 completed
sessions, with 500 timed completions and no HTTP errors. Report p50/p95/p99 for each
operation, aggregate and response format; enforce the existing 500-ms p95 gate for
every operation and each observed format, plus the 1,500-ms deterministic feedback
gate. A rare slow numeric subset cannot hide behind fast choice submissions. Report
actual dispatch rate/lag and scoped API/client CPU and peak RSS; database/container
resource use remains explicitly unmeasured. Do not infer production acceptance.

The original generated-database boundary, migrations, loopback HTTP, fake providers,
closed errors and cleanup ownership remain unchanged. Never target the running review
database, change existing volumes or accept a supplied target URL. The command drops
only its own successfully created disposable database and fails on cleanup failure.

## Verification record

- All 37 load-profile contract cases pass in `make test-unit`, including mixed
  plan binding/format payloads via MockTransport, unsupported-format refusal, trajectory
  patterns and independent numeric latency gating. Existing isolation, error minimization,
  pacing and cleanup tests remain.
- The first type check identifies an insufficiently narrowed response-body value;
  explicit local narrowing fixes it. Subsequent Python and TypeScript type checks pass.
- The first full-size command fails at SYNTHETIC_HISTORY with successful cleanup,
  before timed HTTP. Inspection finds immediate repeated OTP logins conflict with
  cooldown; use normal credential refresh instead of weakening the limit. Closed,
  allowlisted domain diagnostics are added without exception payloads. A format check
  also rejects one overlong comment; the comment is shortened before final lint.
- `make lint test-unit openapi-check` passes: 1,092 unit/contract and 35 tooling
  cases, lint/format, Python/TypeScript types and unchanged generated contracts.
  `make security` passes, including secret-boundary checks and both dependency audits.
- The second command at `21ccb9b` with 293 items completes 7,000 HTTP requests,
  500 timed sessions and exactly 27,500 attempts/grades with zero HTTP errors and
  successful cleanup, but correctly fails format coverage: all 2,500 timed answers
  are SINGLE_CHOICE. START p95 is 465.507 ms and mixed p95 27.784 ms; these do not
  supply numeric acceptance. The [aggregate failed report](evidence/E9_HISTORY_MIXED_MISSED_NUMERIC_2026_10_19.json)
  confirms the small numeric pool can be missed.
  Final fixture source `6b06c53` replaces it with the guaranteed 144/144 split;
  its separate full-size native run passes below. Superseded hosted
  39217608868 is cancelled, not passed; final-source hosted 39217860618 passes.
  This record is not application or performance acceptance from documentation checks.

## Final-source native result — 19 October 2026

`make load-history-mixed` passes at runner source `6b06c53`: 2,000 registered learners,
288 reviewed synthetic fixtures, 25,000 verified prior attempts/grades in 5,000 completed
sessions, followed by 500 timed five-question sessions. All 7,000 HTTP requests succeed;
final totals are exactly 27,500 attempts/grades and 5,500 completed sessions. Maximum
in-flight HTTP reaches 50. All 1,250 numeric and 1,250 choice timed answers score one
with completed mastery updates. The owned temporary database is removed successfully.

| Operation | Samples | p50 ms | p95 ms | p99 ms |
| --- | ---: | ---: | ---: | ---: |
| Profile | 500 | 4.298 | 218.707 | 252.972 |
| Session start | 500 | 14.167 | 432.085 | 975.166 |
| Next question | 2,500 | 10.720 | 15.865 | 323.636 |
| Objective answer | 2,500 | 19.723 | 27.487 | 74.974 |
| Numeric answer subset | 1,250 | 19.727 | 27.778 | 107.760 |
| Choice answer subset | 1,250 | 19.718 | 27.178 | 72.815 |
| Saved state | 500 | 10.364 | 13.333 | 18.176 |
| Progress | 500 | 11.960 | 17.079 | 23.802 |
| All HTTP | 7,000 | 12.909 | 26.986 | 288.525 |

The unchanged per-operation and per-format p95 gates pass. Actual answer dispatch
averages 19.992/s against the 20/s target; lag p95 is 2.161 ms. Timed duration is
125.404 seconds, client/API CPU 52.239 seconds and peak RSS including fixture setup
136,396,800 bytes. Database/container resource use remains unmeasured. Existing review
services stay running; two read-only progress checks observe counts during this run.
No latency adjustment, suppressed sample, widened pool/timeout or external call occurs.
See the [aggregate final report](evidence/E9_HISTORY_MIXED_LOCAL_2026_10_19.json).
Session-start p99 remains close to one second and is retained as a risk signal.
The original empty-history baseline also passes sequentially at the same runner
source: 7,000 requests, zero errors, 2,500 attempts/grades, 500 completed sessions,
peak 50 in-flight HTTP and successful cleanup. START p95 is 421.751 ms, answer p95
26.430 ms and progress p95 11.795 ms. History counts are exactly zero. Timed duration
is 125.414 seconds, dispatch 19.987/s, lag p95 2.164 ms, client/API CPU 50.664 seconds
and peak RSS including setup 137,134,080 bytes. START p99 is 1,115.791 ms; retain the
tail-latency risk. See the [baseline report](evidence/E9_OBJECTIVE_LOAD_LOCAL_2026_10_19.json).
These sequential runs are not a controlled causal comparison of history cost.

Native verification is complete for these two fixed profiles. Complete hosted source
regression [39217860618](https://github.com/Jotham566/kasoma/actions/runs/39217860618)
passes at `6b06c5308f11d74dae465da5388f8bd8ada1639f`. No destructive retention approval
is inferred.

## Complete hosted regression and publication boundary

All 1,092 unit/contract, 412 integration and 35 tooling cases pass, including actual
restricted-role checks. Browser acceptance includes 96 ordinary plus 12 disabled
fake short-text executions (108 total), three staff UI harness cases and three native
WebKit attachment controls. Setup, clean migrations, seed, generated contracts,
lint/format/types, builds, source/container security and service/export/request/model
smoke all pass. Optional registry authentication is skipped because no credential is
configured; no application acceptance check is skipped.

Synthetic logical recovery verifies 68 tables/680 rows in 361 ms, pgvector, immutable
guards and encrypted evidence. It is not production PITR/RPO/RTO or object-storage
recovery. Cold question transfer is 178,022 bytes Chromium, 178,396 Firefox and
177,998 WebKit, each below 250,000 bytes with 19 resources/nine scripts. These are
media-free synthetic journeys, not physical-device or branded-browser acceptance.

Documentation closeout changes only Markdown and aggregate JSON reports after this
verified source. Verify that code, tests, Makefile and workflows remain identical to
`6b06c53` when publishing; preserve the passing and failed native reports separately.

Publication is verified through main commit `6ebdf71`; the owned merged load branch
is removed locally and remotely. The first normal local branch deletion refuses
because its tracking branch still points at the earlier source. Verify ancestry in
both local and remote main, remove only that stale local tracking association, then
use normal deletion. No unmerged work is discarded. Provider-isolation and profile-UI
candidates retain their own live CI and are not accepted by this load result.

## Files in this increment

- `scripts/objective_load.py`, `tests/contract/test_objective_load.py`, `Makefile`.
- `AGENTS.md`, `README.md`, `CHANGELOG.md`.
- `docs/implementation/CURRENT_SPRINT.md`, `REQUIREMENTS_TRACEABILITY.md`,
  `E9_HISTORY_MIXED_LOAD_VERIFICATION.md`, `E9_OBJECTIVE_LOAD_VERIFICATION.md`,
  `RELEASE_GATES.md` (all in `docs/implementation/`).
- `docs/runbooks/LOCAL_DEVELOPMENT.md` and
  `docs/specifications/10_Testing_Acceptance_and_Release.md`.
- Three aggregate JSON reports in `docs/implementation/evidence/`:
  `E9_HISTORY_MIXED_LOCAL_2026_10_19.json`,
  `E9_HISTORY_MIXED_MISSED_NUMERIC_2026_10_19.json` and
  `E9_OBJECTIVE_LOAD_LOCAL_2026_10_19.json`.

Remaining scope includes older/decayed and diagnostic histories, additional response
formats, model/messaging delay/failure scenarios, database resource measurements,
daily soak, deployed networking and all external release approvals. This increment
does not resolve ADR-060's pending deletion authorization.
