# Older/diagnostic history objective load - candidate

Requirements: NFR-PERF-001/002, NFR-SCL-001, FR-DIAG-001–005,
FR-MST-001–005, NFR-SEC-002, NFR-MNT-001.
Decision: [ADR-066](../decisions/ADR/066-temporal-diagnostic-load-profile.md).
Status: final local tooling and all three sequential native profiles pass; own complete hosted acceptance pending.

## Profile boundary

make load-history-temporal adds the missing old/diagnostic fixture composition to
existing make load-objective and make load-history-mixed. All use generated isolated
owned databases/roles, original synthetic content, FakeModelProvider/fake messaging,
loopback HTTP,2,000 registered/500 active/50 concurrent learners and the unchanged
20-answer/s pacer, per-operation/per-format latency gates and request/workload deadlines.
No developer database/volume, supplied URL, real data, external provider or inference.

Content/accounts are created through the normal fixture workflow at an injected age
of94 days. Each learner has an independent historical IdentityService clock, completes
one normal15-item diagnostic at age91 days, then ten normal five-item sessions at
ages90,75,60,45,30,21,14,7,2,1 days. The existing30-day mastery half-life, repeated-item
windows, grades, role/consent policy and all immutable guards stay unchanged. These
ages are load composition, not approved academic values or retention policy.

At each date use normal OTP re-authentication and existing identity lookup. Refresh
families keep their fixed30-day lifetime; no auth lifetime or cooldown is weakened.
Only after every historical worker finishes, re-authenticate all active learners at
current real time. Timed API uses the real clock and current credentials. Never
UPDATE old immutable rows or mutate a shared concurrent identity clock.

Require sealed SAVED diagnostic receipts and15 answered/COMPLETED/nonempty frozen
results before historical revisions. Verify exact32500 prior attempts/grades,5500
completed sessions,500 distinct completed diagnostic owners and7500 diagnostic answers.
Every specified revision-age cohort must have2500 answers. After timed work require
35000 attempts/grades and6000 completed sessions. Existing strong/weak/inconsistent/
improving cohorts and guaranteed choice/numeric timed plans remain.

## Current verification

Initial make test-temporal-load passes69 controls in0.77s (14 new,55 existing load
controls); mypy passes203 source files. New controls cover independent chronological
clocks, each sealed diagnostic/completion, normal grade verification, subject-bound
plans, current authentication after historical preparation, exact age/diagnostic
composition and inherited production/remote/URL-options refusal before resources.
Mocks do not prove actual SQL, OTP behavior, performance or production scale.

The first full-size native make load-history-temporal is running in its own generated
database. Its process remains live; no restart, timeout/threshold relaxation or acceptance
is inferred. Final format/lint/types/contracts/build/unit/security, complete own hosted
regression and sequential original/recent profile rechecks remain pending. Capture all
terminal results including failed measurements and exact owned cleanup.

## Unchanged gates

Provider failures/latency, database/container resource attribution, daily soak, actual
academic inventory/benchmark, physical/branded/screen-reader acceptance, privacy/provider
and production deployment remain separate. This does not approve real scoring, support
access or erasure. Source29f1ddc object recovery and b5557a3 metric-loss each remain
pinned to their independent live hosted runs; they do not accept this newer load tooling.

## Final local engineering gates, measurement still live

make format and make lint openapi-check build test-unit test-temporal-load pass:
1,253 unit/contract,35 tooling,203 typed source files and69 focused load controls.
The502 integration cases are deselected by test-unit; three existing TestClient/
network-block warnings remain. make security security-source passes dependency and
source/secret checks. These are tooling controls, not a native performance result.
The new full-size process remains live and has not been restarted. Issue current
credentials after the complete historical pool joins, preserving token validity
through long setup and the normal fixed authentication-family expiry.

## Separate record-level administrative replay boundary

FR-MST-003's offline read-only reproduction exists, but authenticated learner-level
support replay is still absent. API contract section9 requires explicit support
permission and audit; the existing ADMIN audit page is deliberately aggregate-only.
Do not infer learner-record access from ADMIN status or add raw mastery snapshots
to operations. Any future support slice must resolve its exact case/scope permission,
independent authorization, audit and retention/export/hold controls before code.
This assessment changes no access policy and is not a request or grant of approval.

Final focused recheck after retaining independent mocked clock owners passes69
cases in0.92s. Documentation checks cover188 Markdown files/61 requirements and
whitespace. Runtime source is checkpointed locally while the original native
process remains live; no performance claim, main promotion or new hosted run is
inferred from this checkpoint. Earlier candidate remote heads remain unchanged.

## First complete native measurement

The original live make load-history-temporal completes PASSED with cleanup_failed
false. Runtime logic is represented by checkpoint8a4e09a; the measurement began
before that commit while its runtime code was unchanged, with test/documentation
refinement continuing separately. [Aggregate report](evidence/E9_TEMPORAL_HISTORY_LOAD_2026_10_19.json)
contains only closed measurement fields, without identifiers, records or raw errors.

All32500 historical attempts/grades,5500 historical sessions,500 completed91-day-old
diagnostics/7500 answers and ten2500-answer revision-age cohorts are verified before
HTTP. Timed work completes500 learners and7000 requests with zero errors,50 peak
in-flight,1250 choice/1250 numeric grades and exactly35000 final attempts/grades/
6000 completed sessions. The observed answer dispatch rate is19.988/s; lag p95 is
1.181ms. Timed duration125.405s, client/API CPU53.478s and peak RSS137461760 bytes.
Database/container resource attribution and production_acceptance remain false.

| Operation | Samples | p50 ms | p95 ms | p99 ms |
| --- | ---: | ---: | ---: | ---: |
| Profile | 500 | 4.142 | 206.360 | 235.246 |
| Session start | 500 | 13.393 | 410.622 | 959.979 |
| Next question | 2500 | 10.675 | 16.660 | 251.503 |
| Answer | 2500 | 20.187 | 28.829 | 84.493 |
| Numeric subset | 1250 | 20.189 | 29.137 | 82.107 |
| Choice subset | 1250 | 20.186 | 28.734 | 90.141 |
| Saved state | 500 | 9.893 | 14.731 | 19.619 |
| Progress | 500 | 12.803 | 18.105 | 40.762 |
| All HTTP | 7000 | 12.840 | 27.932 | 282.843 |

All original per-operation/per-format500ms p95 and deterministic feedback1500ms gates
pass; no workload, deadline, assertion or server limit is reduced. One scoped read-only
aggregate progress query occurs during the timed work, in addition to a catalog-only
statistics check. They expose no records and do not grant cleanup authority. The normal
Docker preview remains running; this is not an isolated production-host experiment.

The source still requires sequential original/recent profile rechecks and its own full
hosted regression. b5557a3's completed hosted39308594889 is separate acceptance for the
metric-loss fix, not acceptance of this newer runner. Object recovery remains live at
29f1ddc in39311093503. No main promotion of temporal tooling is inferred yet.

## Verified metric parent integration

Complete hosted39308594889 succeeds at b5557a3:1,180 unit/contract,502 integration,
35 tooling,114 full browser executions and all focused/engineering gates. Main
3cde8c23c9b43bcaa39e3bbe4821beaad2760623 is pushed and remote SHA/ancestry verified;
the owned merged metric-loss branch is removed locally/remotely. Integrating main
into this temporal candidate changes Markdown only relative to3b57714. Four
informational conflicts preserve both current acceptance and candidate histories.
The measured runtime remains unchanged; original/recent rechecks will use this tree.
Object source29f1ddc's own hosted39311093503 remains live and cannot accept this
newer load tooling. No academic/privacy/provider/erasure or production gate changes.

## Published candidate and sequential native baseline

Combined source687d86cdd06bf188f7aa2a725b5e0f19a7e5423b is pushed for own full
[39313955470](https://github.com/Jotham566/kasoma/actions/runs/39313955470), confirmed
in progress. Keep its remote runtime head unchanged; only local Markdown/aggregate
evidence follows. It includes the verified b5557a3 application tree and separately
pending object-recovery tooling; parent acceptance cannot accept these new tests.

After the temporal profile terminates with successful owned cleanup, make load-objective
load-history-mixed runs sequentially on this unchanged runtime tree. The original
[baseline recheck](evidence/E9_TEMPORAL_BASELINE_RECHECK_2026_10_19.json) passes:2000
registered/500 active,50 peak in-flight,7000 HTTP/zero errors,2500 attempts/grades,
500 completions and cleanup_failed false. START p95428.329ms,ANSWER p9529.174ms;
every original latency gate passes. The recent-history target is now live; this is
not a pass for that still-running target and the original process is not restarted.
No runtime change or weakening of thresholds, deadlines, pacing or auth policy.

Public provider-recovery documentation research is recorded separately; it changes
no code, dependency, provider choice, architecture approval or source CI head. It
cannot supply production backup/RPO/RTO or legal/transfer sign-off.

## Complete sequential original/recent rechecks

The same make load-objective load-history-mixed process exits0 after both commands
pass and both exact owned cleanups succeed. Neither native profile is restarted.
The [recent-history report](evidence/E9_TEMPORAL_RECENT_HISTORY_RECHECK_2026_10_19.json)
verifies25000 prior grades/5000 sessions,500 timed completions,7000 successful HTTP,
1250 numeric/1250 choice timed answers and27500 final grades/5500 completed sessions.

| Profile | Prior grades | Final grades | START p95 ms | ANSWER p95 ms | Errors | Cleanup failed |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Original objective | 0 | 2500 | 428.329 | 29.174 | 0 | false |
| Recent choice/numeric | 25000 | 27500 | 424.046 | 29.138 | 0 | false |
| Temporal/diagnostic | 32500 | 35000 | 410.622 | 28.829 | 0 | false |

All per-operation/per-format500ms p95 and1500ms deterministic-feedback gates pass
on unchanged runtime logic represented by687d86c. Recent numeric p9528.989ms and
choice29.630ms; START p99 remains1074.231ms, so this does not claim subsecond tails.
Recent mixed p9544.366ms, duration125.371s, CPU53.208s, peak RSS136151040 bytes,
observed answer dispatch19.992/s and lag p951.191ms. Database/container resource
attribution, provider failures/daily soak, real-deployment/production acceptance
remain unproved. Existing normal Docker services stay running.

The only changes after pushed source687d86c are local Markdown and aggregate evidence.
Local final image/security/service checks are now running; own full hosted39313955470
and object-recovery39311093503 remain live at their unchanged remote heads. None of
these native reports supplies academic/teacher approval or closes production gates.

Final make containers security-containers container-smoke exits0 on the frozen
candidate runtime after all native measurements. Rebuilt images pass high/critical
vulnerability and secret checks; owned private export/request/model/service smoke
passes. All8 normal Compose services are confirmed running/healthy again. No
volumes/cache/images or unrelated data are swept. Only Markdown/aggregate evidence
follows remote687d86c; own complete hosted acceptance remains pending.
