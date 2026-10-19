# Current sprint: verified bounded preservation, progress and shared controls

Updated 19 October 2026. This is not a completed MVP or production-release declaration.
[Earlier sprint history](SPRINT_HISTORY_2026_10_18.md), the
[historical power-recovery checkpoint](IMPLEMENTATION_CHECKPOINT_2026_10_19.md) and
[the current checkpoint/file inventory](IMPLEMENTATION_CHECKPOINT_2026_10_19_PRESERVATION.md)
preserve the evidence and boundaries.

## Verified source on main

Application/test source `6d53541` passes complete hosted [39185423895](https://github.com/Jotham566/kasoma/actions/runs/39185423895) and is pushed to main
through Markdown-only merge `5de2ce5`. This documentation closeout preserves that
exact application/test/workflow tree. All three merged implementation branches are
removed locally/remotely. Capture source `0a8f674` passes complete hosted
[39183714273](https://github.com/Jotham566/kasoma/actions/runs/39183714273); progress
source `7148a1c` passes complete hosted [39184552472](https://github.com/Jotham566/kasoma/actions/runs/39184552472). Superseded progress run
39184146180 at `3291ef7` is cancelled, not a pass.

## Requirements and implementation

- FR-ID-001/005, NFR-ACC-001 and NFR-MNT-001: the
  [profile reverification visibility correction](E1_CONTACT_REVERIFY_VISIBILITY_VERIFICATION.md)
  removes an unrelated action from the signed-out form. The new regression fails
  before the presentation correction; lint/types/build pass afterward. Corrected
  three-engine verification now passes all nine identity executions, alongside
  1,092 unit/contract, 35 tooling, contracts and security. A public signed-out
  screenshot is recorded. Images build and the corrected Docker web preview is
  verified with all eight services healthy. Hosted `44ae9ad` acceptance is pending.

- FR-GRD-003/004/005, FR-MST-001/004/005, NFR-SEC-002 and NFR-MNT-001:
  [fake provider isolation](E9_PROVIDER_FAULT_ISOLATION_VERIFICATION.md) adds three
  bounded regressions for owned web reads during a stalled fake call and neutral
  publication after timeout/failure/fallback. Corrected focused cases, 1,092 unit/contract,
  35 tooling, lint/types/contracts and security pass. Full integration/hosted verification
  remains pending. Normal learner scoring remains off.

- NFR-PERF-001/002, NFR-SCL-001, FR-MST-004/005 and NFR-MNT-001: an independent
  synthetic history/mixed objective load profile is under verification while ADR-060
  awaits approval. It uses normal domain histories and real loopback HTTP without
  runtime changes. See [scope and evidence](E9_HISTORY_MIXED_LOAD_VERIFICATION.md).
  No load acceptance is claimed before the full-size command finishes.
  Final fixture coverage is deterministic by subject (144 choice/144 numeric);
  the earlier 293-item candidate correctly fails for missing numeric delivery despite
  zero HTTP errors and successful cleanup. Final source `6b06c53` passes the native
  profile: 7,000 HTTP requests, 1,250 timed answers per format, 27,500 total grades,
  zero errors and successful cleanup; START p95 432.085 ms, numeric answer 27.778 ms.
  The sequential original-baseline recheck also passes: 7,000 requests, zero errors,
  START p95 421.751 ms and successful cleanup. Hosted regression and main promotion
  remain pending; startup p99 and broader performance/release gaps remain.
  The local runbook and testing specification now describe the optional command,
  generated-database boundary and sequential execution.

- FR-ID-006, FR-WA-006, FR-OPS-003, BR-010, NFR-SEC-002 and NFR-MNT-001:
  approved ADR-057 exact owned encrypted link/conversation snapshots, additive 0038,
  independent API/SQL guards, atomic finite decisions, replay, disposal, inventory
  and accessible controls. Contacts, message bodies, codes and tokens are excluded.
  STOP/unlink/withdrawal and operational expiry remain independent. The advancing-clock
  conversation correction also addresses FR-WA-002. See
  [capture evidence](E8_CHANNEL_PRESERVATION_VERIFICATION.md).
- FR-MST-004/005, NFR-PERF-001 and NFR-MNT-001: request-local immutable estimate reuse
  under unchanged ADR-024. No shared cache, stored aggregate, math, API or consent
  change. Thirty-one frozen original summaries preserve hashes and nonnumeric fields;
  only the two floating-point oracle fields use machine-precision tolerance. See
  [progress evidence](E6_PROGRESS_REUSE_VERIFICATION.md).
- NFR-ACC-001/NFR-COMP-001/NFR-MNT-001: shared single-select appearance preserves
  native semantics and a visible arrow while correcting WebKit's 23-pixel menus.
  Three-engine 320-pixel touch/keyboard/axe journeys and normal/200%-text targets pass;
  staff controls also pass. See [select evidence](E6_SELECT_TARGET_VERIFICATION.md).

## Verification and retained failures

Latest complete hosted verification passes 1,074 unit/contract, 412 integration,
35 tooling and 108 browser executions (32 ordinary plus four fake short-text journeys
per engine), three UI harness and three native WebKit transport controls, actual
restricted logins, generated contracts, security/images and service smoke. Hosted
logical recovery verifies 68 tables/680 rows in 532 ms; local recovery records 302 ms.
These are synthetic engineering checks, not production PITR/RPO/RTO or academic approval.

The historical 0034 fixture is corrected without dropping JSON rejection, held replay
or two forward upgrades; its 21-case suite passes. The later local full backend run
passes 411/412 with a privileged temporary-role provisioning failure before application
checks. Its unchanged standalone recheck and both complete follow-up hosted suites
pass. Password diagnostics remain withheld; underlying local cause is unconfirmed.
The first broader progress browser run has one Firefox pointer click without a
follow-up request; unchanged rechecks and final local/hosted full matrices pass.
No timeout or permission is broadened. Original macOS/Linux math differs by at most
1.1102230246251565e-16; the portable oracle keeps all input hashes/other fields exact
and uses absolute 1e-15 only for mastery/confidence. No product threshold changes.

A 48-row/five-scope pure Linux probe records medians 29.959 ms before and 5.103 ms
after, 30 samples each; replay calls fall from 24 to eight. This excludes API/SQL and
hosted concurrency. Historical objective ANSWER p95 27.221 ms remains historical;
no current agreed-load or provider latency claim follows from either measurement.

## Running review stack and next boundary

All eight Docker services are healthy on 0038 at http://localhost:3000; existing
volumes are preserved. Capture and receipt creation remain false, and normal learner
short-text scoring remains disabled. Host-native Ollama was down after power recovery;
the pinned `make ollama-serve`, ready-state `make ollama-check` and API-container
connectivity probe now pass. No model download, inference, Gemini or external model/
messaging/cloud application call is made. Use fictional data only.

The next narrow design boundary is completed EXPORT-request evidence retirement at
its existing six-calendar-year deadline. Current immutable DELETE guards, key/receipt
expiry semantics, exact holds and object-purge proof require a separately reviewed ADR
before execution. Pending DELETE/snapshot parents have no invented completion or expiry.
The concrete [ADR-060 proposal](../decisions/ADR/060-completed-export-accountability-retirement-proposal.md)
now specifies the table allowlist, exact receipt/job holds, restricted maintenance
capability, cleanup prerequisites, finite retries and synthetic test sequence.
Approval is pending; this documentation increment implements no deletion path.
Complete main CI [39189901813](https://github.com/Jotham566/kasoma/actions/runs/39189901813)
also passes at the prior documentation closeout `f1bd1ad`.
Full preservation, erasure/anonymization and accountability processing remain incomplete.
Academic inventory/rights/benchmark/calibration, privacy/safeguarding and provider/budget
approvals, production recovery, physical/branded devices and pilot sign-offs remain
[release gates](RELEASE_GATES.md). No approval or completion is inferred from tests.
