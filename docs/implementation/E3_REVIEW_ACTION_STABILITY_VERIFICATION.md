# Stable feedback actions during delayed hint loading — verified

## Complete hosted engineering verification — 19 October 2026

[Run 39256037485, attempt 2](https://github.com/Jotham566/kasoma/actions/runs/39256037485/attempts/2)
passes completely at `d8fc0310120fb0b6366f193fdb6aec5f4c799255`. Its application,
tests, contracts, Makefile and workflow match `e33ec69`; later changes are Markdown only.
Verified results: 1,112 unit/contract, 465 integration, 35 tooling and 111 full browser
executions (99 ordinary plus 12 disabled fake short-text), nine focused assessment,
12 interception controls, three staff UI and three native WebKit transport controls.
Setup/migration/seed, actual restricted logins, lint/types/contracts/build,
security/dependency/source/image checks and container smoke all pass. Logical recovery
verifies 69 tables/686 rows in 465 ms, with no cleanup failure and denied execution
after stripped ownership. Object-storage recovery and production RPO/RTO are not proved.

This verifies ADR-060's bounded synthetic executor operations, the guarded test
interception helper and stable feedback actions. It does not complete FR-ID-006/BR-010,
full preservation, account erasure, real-data authority or the MVP release gates.
The eight-service Docker review stack is healthy on 0042 with retirement false;
normal learner short-text scoring remains disabled. No new architecture is adopted.
The next assessed implementation is the bounded disposable load-role lifecycle.

The owner explicitly authorized public repository visibility. GitHub confirms PUBLIC;
current-source and all 125 locally available commit secret scans pass. Earlier billing
refusals and browser failures remain historical failures. The following earlier stage
notes preserve their then-current status; this complete run supersedes their pending
engineering acceptance without retrospectively converting failures into passes.

Requirements: NFR-ACC-001, FR-REV-005, FR-GRD-006, NFR-MNT-001.
No grading, selection, consent, API, storage or architecture change.

## Evidence and change

[Hosted39249423592](https://github.com/Jotham566/kasoma/actions/runs/39249423592)
at `b6aea35` passes all backend/role/recovery checks, all 12 interception controls,
Chromium and Firefox browser shards. WebKit's first shard fails in the existing
cross-context resumed-practice journey, waiting for Question3 after a pointer Next
activation. Seventy-nine ordinary browser executions pass first; the last WebKit
shard, fake short-text journeys and later security/image/service gates do not run.
This failed complete run is not accepted or promoted. The earlier WhatsApp intercepted
transport failure does not recur there. The exact cause of this WebKit failure cannot
be established from its retained console alone.

A deterministic delayed-hints regression reproduces a real layout issue independently:
after an objective answer is saved, asynchronously loaded review hints are inserted
above the action buttons. In Chromium, delivering the held real hint response moves
Next by 47.421875 CSS pixels. The new test fails against the original application:
two existing assessment cases pass and the new stability assertion fails. No timing
threshold or successful test expectation is relaxed.

Move the existing post-grade `Hints` component below the feedback action buttons.
Hint contents, permissions, review-only semantics, pre-answer weighting and manual
reveal behavior remain unchanged. Optional asynchronous loading can no longer displace
Next, solution or reassessment buttons. Keep the original resumed-context pointer
clicks and keyboard answer submission; do not substitute synthetic click dispatch,
force clicks or blanket retries. The regression releases the held real response,
checks less than one-pixel action movement, then requires a real pointer click to
reach Question2. Existing pointer/touch and hint/solution journeys remain active.

The resumed journey also uses the guarded single-reset commit helper for its original
lost-answer-response interception and explicitly checks key reuse. On failure it
prints only capped endpoint-kind/status counts and scalar UI focus/visibility state;
no URL, source/session/attempt identifiers, answers, tokens, cookies or payloads are
copied into replacement diagnostics. These are test-only diagnostics.

## Verification boundary

`make test-web-assessment` runs all three assessment cases in Chromium, Firefox and
WebKit. CI adds this focused gate after services/seed and before the long backend
suite; the complete browser matrix remains required. The added case increases the
ordinary matrix from96 to99, for111 including the existing12 fake short-text journeys.
The red run fails the new assertion with47.421875-pixel movement, while its two
existing cases pass. After the layout change, all nine focused cases pass:
Chromium18.5s, Firefox20.7s and WebKit18.2s. `make lint openapi-check build` passes.
Final local `make e2e` passes111 executions:99 ordinary and12 disabled fake
short-text journeys, with original bandwidth, pointer/touch and axe assertions retained.
`make containers`, `make security-source security-containers` and `make container-smoke`
pass; all eight Docker services are healthy on0042 and persisted retirement remains
false. The review UI includes the updated feedback layout.

Exact source `e33ec6966220bbddd24f11ce8a641e959ebd2983` is pushed to the verification
branch. [Hosted39255125288](https://github.com/Jotham566/kasoma/actions/runs/39255125288)
is refused before any job steps: GitHub's annotation reports failed account payments
or an insufficient spending limit. This is not an application test result. No complete
hosted acceptance or main promotion occurs. The owning account must restore Actions
capacity before a fresh complete run; no billing change, gate bypass or new spending
is performed by the agent. The owner has been asked once for that external action.
Earlier complete native backend evidence remains separate; its source has no backend,
migration or contract change in this correction. No production or academic acceptance.

Files: `apps/web/app/revise/page.tsx`, `tests/e2e/assessment.spec.ts`, `Makefile`,
`.github/workflows/ci.yml`, changelog/sprint/traceability, the local runbook/testing
specification and this verification record. The privacy operations candidate retains
its [separate evidence](E8_EXPORT_RETIREMENT_OPERATIONS_VERIFICATION.md).

## Frozen identity/UI source12c6b60 — complete local browser and recovery results

The default-cache complete matrix passes123 browser executions:108 standard,12
short-text and three configuration. Twelve owned standard/configuration PostgreSQL
containers have empty cleanup reports and independently confirmed exact-ID absence.
The separate short-text runner retains its existing schema scope; no cleanup of
older developer schemas/roles/caches occurs. Recovery passes71 tables/691 rows318ms
logically and71/691/one42,084-byte ciphertext163ms with actual MinIO, stopped source
services, fault/immutable guards, denied stripped retirement and empty cleanup.
Actual restricted-login verification passes. Production RPO/RTO remains false.

Full own hosted39337786063 remains in progress at exact12c6b60d3a76a82c5e10ee15fc51122f4a130fcb.
Only Markdown closeout follows that runtime/test/Make/workflow tree. Earlier missing
browser/native-cache failures remain failed and are not application acceptance.

Separately, verified foundation source2966bab is published through main64e1f72ee10a3ed39a344525f49b9252341224b6
after complete hosted39334774152. Its configuration, erasure-foundation and browser
branches are proven merged and removed locally/remotely. A remote deletion response
reported ref errors, but independent ls-remote and fetch/prune confirm all three
remote refs absent; no unmerged source is discarded. The main follow-up39339512181
remains live. Docker is8/8 healthy on0044, with the locally verified viewport preview
36cb6e9 and retirement/normal short-text disabled. Host-native Ollama connectivity
is restored without inference. Account closure, erasure and DELETE fulfillment remain
unimplemented; approved ADR-061's SQL barrier/resumable job is the next vertical slice.
