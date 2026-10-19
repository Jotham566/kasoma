# E9 synthetic history and mixed objective HTTP load

Requirements: NFR-PERF-001/002, NFR-SCL-001, supporting FR-MST-004/005 and NFR-MNT-001.
Status: implementation under verification; no performance acceptance yet.

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
closed. There are 288 original reviewed choice fixtures and five reviewed numeric
fixtures. Synthetic review contributes nothing to academic release inventory.

## Timed workload and gates

Reuse 50 concurrent journeys, the 20-answer/second pacer, six operations, five timed
answers per learner, 300-second workload deadline and ten-second client timeout.
Mathematics and Physics plans are bound independently to their authenticated learner;
Physics targets Electricity and Magnetism so numeric questions can be selected by the
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
- The corrected full-size native load and hosted verification are pending.
  This record is not application or performance acceptance from documentation checks.

Remaining scope includes older/decayed and diagnostic histories, additional response
formats, model/messaging delay/failure scenarios, database resource measurements,
daily soak, deployed networking and all external release approvals. This increment
does not resolve ADR-060's pending deletion authorization.
