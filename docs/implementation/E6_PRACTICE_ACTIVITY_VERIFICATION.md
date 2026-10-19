# Owned practice-day indicator — candidate verification

Requirements: FR-MST-004/005, FR-ID-003, FR-WA-003, NFR-SEC-002,
NFR-ACC-001, NFR-LOC-001 and NFR-MNT-001; approved roadmap 3.5.
Status: implementation candidate; not accepted or promoted.

## Requirement and decisions

The approved roadmap includes a simple streak or consistency indicator. Existing
Progress has no such display. [ADR-062](../decisions/ADR/062-owned-practice-activity.md)
records a read-only seven-Kampala-calendar-day count, including today, for the selected
subject. It preserves [ADR-024](../decisions/ADR/024-progress-history.md)'s access,
sealed diagnostics and absence of a stored streak/reward system. This ordinary MVP
display decision grants no new privacy/erasure permission and does not approve ADR-061.

Use the same explicit read timestamp and validated visible GRADED evidence already
loaded for progress. Distinct dates deduplicate mappings/attempts naturally. Include
wrong graded answers and all channels. Exclude pending grades and every incomplete
or abandoned/expired diagnostic. Original attempt dates determine the count even if
short-text results become available later. No extra SQL, replay, writes, cache or table.

The optional additive DTO supports older-server rollout; the new backend always emits
an object. Missing/unsupported data renders unavailable rather than zero. The modern
responsive card shows text, date range and a labelled meter using existing styles.
No rankings, notifications, penalties, public identity or academic-accuracy claim.

## Regression evidence and commands

Before implementation, new activity assertions fail in five integration cases with
missing practice_activity; 26 existing contract/history controls pass. This confirms
a missing approved MVP display rather than inferring it from a roadmap checkbox.
Initial implementation passes 54 focused cases. Expanded tests add normal OTP/grade
transactions across Kampala midnight, wrong-answer activity, selected-subject isolation
and explicit web/WhatsApp counts, alongside duplicate/date/DTO/sealed-result controls.

- `make test-progress`: expanded pure/rollup/replay, progress and shared channel suites;
  55 focused cases pass in 56.85s, including 14 actual PostgreSQL integration cases
  and 41 pure/rollup/replay cases; these are not 55 integration cases.
- `make openapi` regenerates the additive schema and TypeScript contracts.
- `make test-web-progress`: new standard three-engine progress journey target; covers
  empty/positive meter, incomplete diagnostics, older-response absence, offline retry,
  keyboard/axe and 320-pixel layout. The final three-engine run passes Chromium 13.2s, Firefox 15.8s and WebKit 13.5s.
  Screenshot review places the primary continuation action before the secondary
  activity card; a bounding-box assertion protects that order at 320 pixels.
  Initial unnamed-project screenshots collided; browserName now keeps three distinct
  images. The final Chromium positive screenshot is visually inspected; full physical/
  branded-browser review is not inferred.
- `make format`, `make lint openapi-check build` pass after final UI ordering.
  Generated contracts match. `make test-unit` passes 1,146 unit/contract and 35 tooling
  cases; the three existing deprecation/intentional network-denial warnings remain.
- `make security security-source` passes with no known dependency vulnerabilities
  or source leaks. `make containers security-containers container-smoke` passes;
  all services remain running. No migration or dependency change is introduced.
- The feature's own full hosted acceptance and combined-source load verification
  remain pending. Performance run 39286019222 at 58d598e cannot establish acceptance
  of this new activity/API/UI tree. Integrate the verified performance baseline before
  the final combined-source load/hosted run; do not replace its active branch head.

Native app/branded-browser review was unavailable because the Mac was locked. Existing
IAB/automated engines do not substitute for physical/branded browser acceptance. Keep
all normal Docker services running. No real data, inference, Gemini or external delivery.

## Verified performance baseline integrated

Main83f30cc publishes complete hosted39286019222's verified performance source58d598e
plus Markdown/aggregate closeout. Its merged branch is removed. That baseline is now
merged into the activity candidate; overlapping documentation and Make targets retain
both changes. The combined tree still requires its own targeted/load/hosted verification;
the earlier performance CI does not accept this API/UI feature. ADR-061 stays unapproved.

## Combined native checks before publication

After integrating main 83f30cc, `make test-progress test-fresh-session-response` passes
55 focused cases in 59.12s and 40 assessment integration cases in 158.43s. Seven channel
cases occur in both targets; these are 95 executions, not 95 distinct integration tests.
`make test-unit` passes 1,146 unit/contract and 35 tooling cases, with 484 integration
cases deselected. Quality/types/contracts/build, security/source/images and eight-service
container smoke pass. The combined progress journey passes Chromium 18.1s, Firefox 19.1s
and WebKit 16.1s, including real graded activity, sealed diagnostic exclusion, legacy
absence, offline retry, axe and narrow primary-action order. Native branded/physical
review remains separate. Both source-pinned load profiles and the feature's own full
hosted run are still required; no prior CI result substitutes for this combined tree.
