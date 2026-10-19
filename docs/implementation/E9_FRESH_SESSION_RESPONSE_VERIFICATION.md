# Fresh revision response — verification candidate

Requirements: NFR-PERF-001/002, FR-REV-001/002/005/006, FR-GRD-008,
FR-WA-003, NFR-MNT-001 and NFR-SEC-002.
Status: candidate; full application/hosted acceptance and new load evidence pending.

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
  integration suites. The initial focused-only command results above are not a claim
  that the expanded command or full suite has passed.
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
  vulnerabilities and source Gitleaks reports no leaks. Image/service checks are
  in progress; hosted regression and new load evidence remain pending.
- Re-run both standard native load profiles sequentially after other checks finish.
  Retain every failure and unchanged per-operation thresholds; do not claim that two
  fewer queries fix the previously unexplained START p95 variance.

The original corrected-source history miss at 559.306ms remains failed. The previously
passing 448.045ms recheck is not acceptance of this candidate. Full agreed-load/provider/
soak/production acceptance and genuine academic/privacy/safeguarding gates remain open.
Normal Docker services remain running on 0042, with review retirement false.
