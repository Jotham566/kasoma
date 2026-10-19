# ADR-066: Older evidence and completed diagnostics in the objective load profile

Date: 19 October 2026
Status: Accepted within delegated synthetic test engineering; local tooling checks pass, native/hosted verification pending
Requirements: NFR-PERF-001/002, NFR-SCL-001, FR-DIAG-001–005, FR-MST-001–005,
NFR-SEC-002, NFR-MNT-001

## Decision and existing boundaries

Add a separate fixed temporal-history profile to the existing generated-database load
runner. Preserve the original objective and recent-history commands, exclusive owned
role/database lifecycle, 2,000 registered/500 active/50 concurrent learners, 20-answer/s
pacer, 7,000 timed requests, per-operation/per-format p95 thresholds, deadlines, normal
server limits and fake providers. No application, public API, migration or engine policy
changes. Do not age immutable rows using UPDATE or disable a trigger.

Create original fixture content/accounts at a fixed historical anchor, 94 days before
setup. For each active learner, use an independent injected identity clock and normal
OTP authentication to complete one 15-question diagnostic 91 days before the anchor's
present time. Use the existing diagnostic selector, sealed answer receipts and normal
completion/mastery path; no hand-built diagnostic grade or fabricated result. Require
all 15 saved answers and a completed, nonempty frozen diagnostic result.

Create ten normal five-question revision sessions at ages 90,75,60,45,30,21,14,7,2,1 days.
Keep the existing strong/weak/inconsistent/improving synthetic trajectories and guaranteed
Mathematics choice/Physics numeric fixture split. Dates are fixture distribution only,
not new academic truth, decay weights or retention policy. Current configured 30-day
half-life remains unchanged. Content approval must precede historical attempts.

Each learner uses a separate clock closure; never mutate a shared concurrent identity
clock. Re-authenticate normally at each date and at current real time for timed HTTP.
Do not extend session expiry/refresh families or bypass OTP cooldown. Authenticated
subjects, content eligibility, ownership, immutable grades and synchronous mastery remain
normal domain decisions. Timed API uses the unmodified real clock and current credentials.

Before timing verify exact 32,500 prior attempts/grades,5,500 completed sessions,500
completed diagnostics/7,500 diagnostic answers and the fixed age cohorts. After 500 timed
sessions require35,000 attempts/grades and6,000 completed sessions. Report diagnostic
and age composition explicitly; do not count fixture preparation as measured API work.
No unfinished diagnostic evidence may leak into any learner projection.

## Acceptance and exclusions

Test chronological isolated clocks, actual OTP re-authentication, every normal diagnostic
receipt/completion, exact counts/age cohorts, unsupported responses, no mutable record
rewrites, inherited unsafe-profile/cleanup refusal and unchanged independent latency
checks. Execute a real full-sized profile, then the original/recent profiles sequentially
when source changes could affect them. Preserve failed measurements and cleanup evidence.
Require full own hosted regression before main promotion. Mocks do not prove performance.

This fills one representative-history gap. Provider failure/timing, database/container
resource attribution, daily soak, real academic review, deployment latency and production
acceptance remain separate. No support access, erasure authority, real data, model call,
new provider, runtime tuning or reduced gate is introduced.
