# Current sprint: approved synthetic preservation implementation

Updated 19 October 2026. Earlier context is preserved in
[sprint history](SPRINT_HISTORY_2026_10_18.md) and the
[implementation checkpoint](IMPLEMENTATION_CHECKPOINT_2026_10_19.md).
This is not a completed MVP or production-release declaration.

## Verified source on main

Application source is `25b44b1`; complete hosted
[39176205670](https://github.com/Jotham566/kasoma/actions/runs/39176205670) passes. The documentation-only closeout
preserves that exact application tree. The format branch is merged; its merged branch
is removed locally/remotely. The active capture branch remains separate. Earlier
checkpoint: [5d95f9d](IMPLEMENTATION_CHECKPOINT_2026_10_19.md).

Terminal receipt source 397f562 also passes complete hosted 39165896953. Receipt
creation remains false; live-state preservation and erasure remain incomplete.

Earlier merged checkpoints:

- `0c73c45`: bounded private local model observations, truthful unknown usage and
  ADMIN visibility; [hosted 39160113771](https://github.com/Jotham566/kasoma/actions/runs/39160113771)
  and [model evidence](E8_MODEL_USAGE_VERIFICATION.md) pass under ADR-054.
- `f5f408e`: typed existing per-job request/token/time ceilings;
  [hosted 39157127637](https://github.com/Jotham566/kasoma/actions/runs/39157127637)
  and [budget evidence](E4_RUNTIME_BUDGET_VERIFICATION.md) pass.
- `a357222`: bounded grading operations and database-clock review completion cap;
  [hosted 39155326659](https://github.com/Jotham566/kasoma/actions/runs/39155326659)
  and [grading evidence](E8_GRADING_OPERATIONS_VERIFICATION.md) pass.
- Independent blinded review, rolling controls, staff navigation and offline report
  comparison are merged; genuine reviewer/model/academic approval remains separate.

## Verified integrated changes

Source `5d95f9d` passes every step of the complete hosted pipeline, including actual
24/8 GiB capacity checks, full backend/browser suites, security/images and service smoke.

- ADR-056: four legacy DELETE wrappers evaluate holds at wall clock, preserving
  historical predicates and original immutable guards. Five focused cases plus
  related suites pass; [clock evidence](E8_HOLD_DELETE_CLOCK_VERIFICATION.md).
- ADR-058: fixed-category ADMIN audit activity, newest-10,000 cap, strict generated
  contract and time-window index; [audit evidence](E8_AUDIT_ACTIVITY_VERIFICATION.md).
  No individual audit field, new learner support permission or retention change.
- ADR-059: hosted-only fixed SDK preparation, capacity gates and diagnostics after
  runner disk exhaustion; [CI evidence](E0_CI_STORAGE_VERIFICATION.md). No developer
  SDK cleanup, Docker prune or application-volume reset.

Local verification passes 940 unit/contract, 35 tooling and 378 integration cases,
actual restricted logins, 65-table/648-row populated logical recovery (287 ms), source/
dependency/image security, rebuilt Docker smoke, 105 browser executions,
three UI harness/navigation cases and 31 full-Chromium executions. These are named
runs with overlapping cases. No real model or messaging provider is exercised.

The old standalone clock run 39167600610 fails on runner disk exhaustion after backend
and five browser batches; it is not accepted. Initial missing proxy/client/staging and
obsolete navigation expectations were caught and corrected. Failed/cancelled evidence
is retained; no timeout, authorization or academic threshold is relaxed.

## Current preservation increment

[ADR-057](../decisions/ADR/057-minimized-channel-preservation-proposal.md) defines
bounded encrypted evidence for an exact owned link/conversation version, excluding
contacts, message bodies and authentication material. It compares version history,
sets finite lifecycle/access boundaries and defines atomic capture/race/recovery tests.
On 19 October the user explicitly approved this bounded synthetic implementation.
Real-data processing and erasure were excluded in the approval request and remain
unauthorized. The first increment is an offline strict evidence format and independently
derived Fernet encryption bound to snapshot/request/owner/source/revision/version.
All 82 focused socket-disabled, 1,022 unit/contract, 378 integration and 35 tooling cases
pass locally, alongside lint/type/generated-contract/security/image/service checks.
Complete hosted 39176205670 passes at `25b44b1`. See
[increment verification](E8_CHANNEL_PRESERVATION_FORMAT_VERIFICATION.md).
Capture candidate on `codex/channel-preservation-capture` adds additive 0038, opaque
exact source versions, independent SQL guards, atomic finite decisions/disposal,
generated contracts, preview inventory and operator controls. Initial 27 integration
cases were extended to 34 (including both actual restricted-login paths); 105 focused
format/contract and two advancing-clock cases pass. Initial three-engine browser
journeys pass. Populated logical recovery passes 68 tables/680 rows in 302 ms,
including encrypted snapshots and disposal/sequence state after source removal.
The full 1,055-unit/contract and 35-tooling suites pass; integration finishes with
411 passes and one historical-schema fixture failure. Its correction preserves
the 0034 JSON guard and forward-upgrade assertions. All 108 browser executions,
three UI harness and three native transport checks pass; final scoped dropdown
target-size correction passes the capture journey in all three engines. Security,
recovery, migration and Docker smoke pass. The corrected 21-case receipt/restricted-login suite passes, including the
historical upgrade. Complete hosted acceptance remains required. See
[capture verification](E8_CHANNEL_PRESERVATION_VERIFICATION.md).
Format source `25b44b1` is on main with documentation closeout `9c98a55`; its merged
branch is removed. The running Docker UI is upgraded additively to 0038; migration and service smoke
pass with all eight services healthy. Capture remains disabled.
Full coverage, erasure/anonymization and accountability expiry remain incomplete.

The separate capture candidate is under implementation. Its real-time browser path
exposes an existing clock defect: conversation updated_at and exact 24-hour expiry used
different clock reads. Two deterministic advancing-clock cases reproduce it. A fix
using one instant and new browser/role/capture coverage are under separate verification;
no real-time conversation or full capture acceptance is inferred from this format gate.

## Review stack and remaining gates

All eight Compose services remain running healthy at http://localhost:3000;
Mailpit is http://localhost:8025. The preview is on schema 0038 with capture and receipt
creation false and normal learner short-text scoring disabled. Existing volumes are
retained. See [nondestructive local recovery](../runbooks/LOCAL_DEVELOPMENT.md).
Native Playwright runs are serial; do not rebuild native .next during an active server.
Docker builds have a separate filesystem. Use fictional data only.

Recent screenshots of learner home, practice, progress and audit were visually reviewed;
large-text audit spacing was improved and reverified. Full Chromium is additional
engineering evidence, not physical-device or all branded-browser acceptance.

Genuine academic inventory/rights/benchmark/calibration, privacy/DPIA/PDPO and guardian
procedures, Week 8 production provider/budget approval, complete preservation and
reviewed erasure authority, production PITR/RPO/RTO and pilot/device sign-offs remain in
[release gates](RELEASE_GATES.md) and [traceability](REQUIREMENTS_TRACEABILITY.md).
Gemini remains manual and explicitly opt-in; it was not run. No production cloud
application dependency is introduced. Historical objective ANSWER p95 27.221 ms is
recorded accurately; no current-source/provider/long-history performance is inferred.

## Next unblocked slice: progress replay reuse

Capture source `0a8f674` is pushed on its dedicated branch; complete hosted
[39183714273](https://github.com/Jotham566/kasoma/actions/runs/39183714273) is in progress.
Main remains the verified format source. The merged format branch and the temporary
owned capture stash are removed; the active capture and child progress branches
remain until their exact-source gates pass and main promotion is complete.

`codex/progress-rollup-reuse` addresses FR-MST-004/005 and NFR-PERF-001 within ADR-024.
All 31 frozen legacy summaries and 1,074 unit/contract cases pass. The
pure dense overlapping-scope case reuses eight distinct skill replays instead of
24, with no shared cache, data/API/math or authorization changes. Fresh-read API,
browser and broad/hosted verification are pending; see
[verification](E6_PROGRESS_REUSE_VERIFICATION.md).
