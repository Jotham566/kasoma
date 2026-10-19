# Stable feedback actions during delayed hint loading — candidate

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
