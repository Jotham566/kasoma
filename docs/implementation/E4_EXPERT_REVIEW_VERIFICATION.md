# Independent grading review verification

18 October 2026. Candidate branch `codex/grading-expert-review`; FR-GRD-003/004/005,
FR-ID-003/006, NFR-SEC-002. [ADR-051](../decisions/ADR/051-blinded-review-and-release-unit-sampling.md)
is proposed for the disabled synthetic engineering path. Full acceptance is pending.

## Implemented boundary

Additive migration 0033 preserves original publication evidence, adds versioned
release-unit sampling and immutable independent completion/counters, and atomically
persists sticky rolling disablement. Reviewer/learner accounts lock in UUID order
before current authorization/consent and band acquisition. The worker reloads audit
state at every model pass and final publication. Staff cannot override grades/mastery.

The blinded API and responsive workspace show pinned question, exact response and
rubric only. No identity/model result/band/ordinal is projected. Explicit empty point
inputs, acknowledgement, critical classification, bounded queue pagination and immutable
lost-acknowledgement retry preserve independent scoring. Owned minimized export,
diagnostic sealing, review holds/inventory and correlated confidential-access audit are
included. The restricted database login has no role-table mutation permission.

## Executed evidence and remaining checks

- Focused contracts/integration: 32 pass, including competing reviewers, rollback,
  critical review between model passes, abandoned diagnostic sampling, current consent/
  role/recent-auth barriers, minimized correlated audit, 101 completed reviews with
  last-100 eviction/sticky disablement and populated repeatable 0032-to-0033 upgrade.
- Existing encrypted learner-flow/processor suite: 18 pass. An additional rerun includes
  an outside-provider assertion that consent withdrawal actually occurred; this prevents
  a malformed callback request from masquerading as a successful privacy barrier.
- Existing exact-record legal holds: 19 pass.
- Real restricted-login encrypted publication and independent completion: pass.
- New browser profile: 12 pass (four cases per Chromium/Firefox/WebKit), including
  desktop/mobile visual inspection, 320-pixel reflow, 48-pixel select controls, axe,
  BFF cursor/limit forwarding and exact retry. Full browser regression also passes
  90 existing executions plus these 12 new profile executions.
- 844 unit/contract and 35 tooling cases pass. Lint/format/types/generated contracts,
  source/dependency security and secret scan pass; no real data/provider calls.
- Rebuilt API/web images pass current HIGH/CRITICAL vulnerability scans. Additive
  `make migrate seed` and eight-service `make container-smoke` pass, including a real
  scheduled synthetic export through web/API/worker/private storage and scoped metrics.
  Persistent review stack now uses migration 0033; no reset/deletion was performed.
- Populated logical recovery: first extended run failed POPULATE_SYNTHETIC_SOURCE;
  the diagnostic retry passes with 65 tables/616 rows and 353 ms restore. The first
  cause is unresolved; retain the failure. A further unchanged-source repeat passes
  with 65 tables/616 rows, 1,085 ms restore and no cleanup failure. Failure
  diagnostics expose closed categories and repository-only basenames/line numbers,
  never exception messages, SQL or connection values.
- Full backend regression passes 324 integration cases (13 minutes), supplemented
  by the final 32 focused review cases and corrected 18-case encrypted-flow rerun.
  Final unit/security rerun passes. Exact-source hosted acceptance remains required
  before promotion; do not infer that result from earlier baselines.

An initial browser 404 exposed the missing web proxy allowlist; the strict route was
added and all browser profile cases rerun successfully. Early TypeScript/lint issues
were corrected without disabling checks. A new outside-provider withdrawal test initially
failed because SELF/affirmative:false is invalid; use WITHDRAW/affirmative:true and verify
subsequent learner access is denied. The older provider-callback test now uses that same
valid operation and verifies denial outside its exception-catching callback.
Existing persistent Docker services recovered
healthy after power loss without volume reset. Normal short-text scoring remains off.

## Release gaps

Genuine academic benchmark/calibration approval, reviewer qualification, sampling/window
approval, production safety/model providers, privacy/provider/pilot approval, destructive
retention approval and physical-device/PITR evidence remain in
[the release register](RELEASE_GATES.md). Synthetic agreement is not academic accuracy.


## Hosted promotion and clock follow-up

Complete [39150319607](https://github.com/Jotham566/kasoma/actions/runs/39150319607)
passes at `2164209`; source is on main and its merged branch is removed. Actual scoring
remains disabled. Subsequent native browser verification exposed millisecond host/VM
clock skew at the SQL nonfuture completion guard. The identical rollback-only review
failed nine of ten times before capping completion at database time; ten of ten succeed
after the cap, with no commit or weakened guard. A thirty-second ahead-clock integration
regression passes in the current 33-case review suite. Final follow-up acceptance is
tracked with [grading operations](E8_GRADING_OPERATIONS_VERIFICATION.md).
