# Current sprint: verified checkpoint and preservation decision

Updated 19 October 2026. Earlier context is preserved in
[sprint history](SPRINT_HISTORY_2026_10_18.md) and the
[implementation checkpoint](IMPLEMENTATION_CHECKPOINT_2026_10_19.md).
This is not a completed MVP or production-release declaration.

## Verified source on main

Application source is `5d95f9d`; complete hosted
[39171302022](https://github.com/Jotham566/kasoma/actions/runs/39171302022) passes. The documentation-only closeout
preserves that exact application tree. All merged implementation/review branches are
removed locally/remotely. See [checkpoint](IMPLEMENTATION_CHECKPOINT_2026_10_19.md).

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
dependency/image security, rebuilt Docker smoke, 105 ordinary browser executions,
three UI harness/navigation cases and 31 full-Chromium executions. These are named
runs with overlapping cases. No real model or messaging provider is exercised.

The old standalone clock run 39167600610 fails on runner disk exhaustion after backend
and five browser batches; it is not accepted. Initial missing proxy/client/staging and
obsolete navigation expectations were caught and corrected. Failed/cancelled evidence
is retained; no timeout, authorization or academic threshold is relaxed.

## Next preservation decision

[ADR-057](../decisions/ADR/057-minimized-channel-preservation-proposal.md) proposes
bounded encrypted evidence for an exact owned link/conversation version, excluding
contacts, message bodies and authentication material. It compares version history,
sets finite lifecycle/access boundaries and defines atomic capture/race/recovery tests.
Explicit owner approval was requested under the source-of-truth change protocol and
is not recorded. No answer or elapsed time grants approval; dependent implementation
has not started. Full coverage, erasure/anonymization and accountability expiry remain
incomplete even if this first bounded proposal is approved.

## Review stack and remaining gates

All eight Compose services remain running healthy at http://localhost:3000;
Mailpit is http://localhost:8025. The preview is on schema 0037 with receipt
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
