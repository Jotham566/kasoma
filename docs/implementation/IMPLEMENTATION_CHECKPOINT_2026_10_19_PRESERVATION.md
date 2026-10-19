# Approved synthetic preservation and progress checkpoint — 19 October 2026

This report records verified local and complete hosted engineering.
It is not a completed MVP, production approval or account-erasure authorization.
The user's ADR-057 approval applies only to the specified synthetic implementation.

## Sources and scope

- `0a8f674`: exact finite encrypted owned link/conversation-version snapshots,
  additive 0038, independent API/SQL guards, cleanup, advisory inventory and operator UI.
  Requirements: FR-ID-006, FR-WA-006, FR-OPS-003, BR-010, NFR-SEC-002, NFR-MNT-001.
  The conversation clock correction also addresses FR-WA-002.
- `7148a1c`: request-local progress replay reuse under unchanged ADR-024;
  FR-MST-004/005, NFR-PERF-001 and NFR-MNT-001. No shared cache, math or API change.
- `6d53541`: shared native single-select target correction;
  NFR-ACC-001/NFR-COMP-001/NFR-MNT-001. No custom dropdown or permission change.

All three complete hosted runs pass: capture
[39183714273](https://github.com/Jotham566/kasoma/actions/runs/39183714273), progress
[39184552472](https://github.com/Jotham566/kasoma/actions/runs/39184552472), and latest source [39185423895](https://github.com/Jotham566/kasoma/actions/runs/39185423895). Verified application/test/workflow source
`6d53541` is pushed to main through Markdown-only merge `5de2ce5`. All three merged
implementation branches are removed locally/remotely; this closeout changes only
Markdown. No code, test, contract, dependency or workflow differs from that tested source.

## Executed checks and results

| Area | Executed commands / result |
| --- | --- |
| Complete hosted | Latest [39185423895](https://github.com/Jotham566/kasoma/actions/runs/39185423895): 1,074 unit/contract, 412 integration, 35 tooling, 108 browser executions, all UI/transport/recovery/security/image/service gates pass. Latest logical recovery: 68 tables/680 rows, 532 ms. |
| Capture/SQL | `make test-channel-preservation`: 105 format/contracts and 34 integration cases pass, including both actual restricted logins, rollback, race, active-decision and disposal boundaries. `make test-channel-clock`: two advancing-clock red/green regressions pass. |
| Upgrade correction | `make test-channel-receipt-holds`: 21 cases pass after correcting the historical 0034 fixture to use its original columns; JSON rejection, exact held replay and two forward upgrades are preserved. |
| Progress | `make test-progress`: 31 cases pass (six engine, 19 reuse and six API), including current consent, sealed diagnostics, owned evidence, fresh reads and exact nonnumeric/hash outputs. |
| Broader backend | 1,074 unit/contract and 35 tooling cases pass. The local `make test` integration run exits with 411 passes and one temporary privileged test-role provisioning failure before application checks. The standalone `make test-runtime-role` recheck passes. Underlying transient cause remains unconfirmed; generated-password diagnostics remain withheld. |
| Browser/UI | Final `make e2e` on `6d53541` passes 108 executions: 32 ordinary and four fake short-text journeys per engine. Three UI harness and three native WebKit download controls pass. Three focused capture journeys and three shared-selector touch journeys cover axe/keyboard, 320-pixel reflow and 200% text. |
| Recovery | `make recovery-drill`: 68 tables/680 synthetic rows, 302-ms logical restore; encrypted bound snapshots after operational source removal, finite disposal, sequence position and immutable guards pass. No production PITR/RPO/RTO or object recovery claim. |
| Quality/security | `make format lint openapi-check build`, `make security security-source`, and `make containers security-containers` pass. Python/TypeScript types, generated contracts, secret/dependency and configured HIGH/CRITICAL image gates pass. |
| Live review | Additive `make migrate`, Compose refresh and `make container-smoke` pass, including async frozen export and safe request/model metrics. All eight services are healthy on 0038 at http://localhost:3000. Capture/receipt creation and normal learner short-text scoring remain disabled. Existing volumes are preserved. |
| Host model runtime | `make ollama-check` initially reports the host server unavailable after power recovery. The pinned `make ollama-serve` restarts it on loopback; the ready-state native check and API-container connectivity probe pass. No inference, model download or external fallback occurs. |

The pure Linux progress probe compares all 31 original/optimized summaries exactly
on that platform. Original macOS/Linux floating-point drift is at most
1.1102230246251565e-16; only mastery/confidence oracle comparisons use absolute
1e-15, with no relative tolerance. Input hashes and other fields remain exact.
No domain threshold changes. A 48-row/five-scope probe, 30 samples each, measures
pure-rollup medians 29.959 ms before and 5.103 ms after; replay calls fall from 24
to eight. This excludes API/SQL/concurrency and does not establish hosted load p95.

The first broader progress browser run has one existing Firefox cross-device
Next-question click with no follow-up request; the unchanged Firefox recheck and
final full 108-execution run pass. Its cause is unconfirmed. Initial capture browser
setup/label/clock errors, stale option inventory, duplicate landmarks, 23-pixel WebKit
menus, nonportable float hashes and the old-schema fixture failure are preserved in
[the capture](E8_CHANNEL_PRESERVATION_VERIFICATION.md),
[progress](E6_PROGRESS_REUSE_VERIFICATION.md) and
[select](E6_SELECT_TARGET_VERIFICATION.md) evidence. No timeout or permission is broadened.

## Decisions and remaining work

No architectural decision beyond the user's approved ADR-057 is introduced. Existing
ADR-024 formulas, confidence/display/change rules and sealed-diagnostic boundaries
remain unchanged. Snapshot evidence is minimized, independently encrypted and bound
to exact request/owner/source/version; it cannot resume, grade or send. STOP/unlink,
withdrawal and normal operational expiry remain independent of preservation.

Full preservation coverage, erasure/anonymization and accountability expiry remain
incomplete. Real-data privacy/safeguarding authority, academic inventory/rights/
benchmark/calibration, Week 8 production provider/budgets, production PITR/RPO/RTO,
physical/branded-device evidence and pilot sign-offs remain separate
[release gates](RELEASE_GATES.md). Synthetic engineering cannot supply these approvals.
Recommended next boundary: prepare the exact remaining preservation/retention and
erasure transform for review before destructive execution; do not infer it from
ADR-057's bounded approval. Continue only independently authorized MVP work meanwhile.

## Next retention design boundary

The next narrow review target is already-completed EXPORT-request accountability
evidence. `data_subject_requests` already has completed_at and retention_due_at,
with the exact six-calendar-year relationship enforced in SQL. Pending DELETE
requests, including all current snapshot parents, have no invented completion or
expiry and remain ineligible. No account/learning erasure follows from this scope.

Before adding deletion execution, resolve an owner-reviewed ADR covering retained
intake key/receipt behavior after expiry, narrowly authorized exceptions to current
immutable DELETE guards, exact child-row/hold locking, and object-purge proof before
discarding export-generation locators. Existing ADR-045 explicitly says release or
expiry does not bypass immutable guards or authorize deletion. ADR-057's synthetic
snapshot approval does not supply this separate execution authority. Existing generic
audit evidence also follows its own schedule; request completion cannot silently be
substituted for account closure/withdrawal. This is readiness, not an implementation
or a newly accepted policy.

## Files created or changed

Repository-relative inventory from `9c98a55` through the current main and Markdown
closeout, including this report. Builds, screenshots, test fixtures created at runtime
and local logs remain ignored.

- `.env.example`
- `AGENTS.md`
- `CHANGELOG.md`
- `Makefile`
- `apps/api/data_requests.py`
- `apps/api/migrations/env.py`
- `apps/api/migrations/versions/0038_channel_preservation.py`
- `apps/web/app/api/v1/[...path]/route.ts`
- `apps/web/app/globals.css`
- `apps/web/app/privacy/channel-preservation.tsx`
- `apps/web/app/privacy/deletion-impact.tsx`
- `apps/web/app/privacy/legal-holds.tsx`
- `docs/decisions/ADR/057-minimized-channel-preservation-proposal.md`
- `docs/decisions/ADR/README.md`
- `docs/implementation/CURRENT_SPRINT.md`
- `docs/implementation/E6_PROGRESS_REUSE_VERIFICATION.md`
- `docs/implementation/E6_PROGRESS_VERIFICATION.md`
- `docs/implementation/E6_SELECT_TARGET_VERIFICATION.md`
- `docs/implementation/E8_CHANNEL_PRESERVATION_CAPTURE_READINESS.md`
- `docs/implementation/E8_CHANNEL_PRESERVATION_FORMAT_VERIFICATION.md`
- `docs/implementation/E8_CHANNEL_PRESERVATION_VERIFICATION.md`
- `docs/implementation/IMPLEMENTATION_CHECKPOINT_2026_10_19.md`
- `docs/implementation/IMPLEMENTATION_CHECKPOINT_2026_10_19_PRESERVATION.md`
- `docs/implementation/RELEASE_GATES.md`
- `docs/implementation/REQUIREMENTS_TRACEABILITY.md`
- `docs/runbooks/LOCAL_DEVELOPMENT.md`
- `docs/specifications/03_Domain_and_Data_Model.md`
- `docs/specifications/04_API_and_Integration_Contract.md`
- `docs/specifications/13_ADR_and_Decision_Log.md`
- `packages/api-client/openapi.json`
- `packages/api-client/src/schema.d.ts`
- `scripts/e2e_api.py`
- `scripts/recovery_channel_preservation.py`
- `scripts/recovery_channel_receipts.py`
- `scripts/recovery_drill.py`
- `scripts/recovery_fixture.py`
- `services/channel_preservation.py`
- `services/channel_preservation_contracts.py`
- `services/config.py`
- `services/data_request_contracts.py`
- `services/deletion_preview.py`
- `services/domain/channel_preservation.py`
- `services/domain/messaging.py`
- `services/legal_hold_contracts.py`
- `services/legal_holds.py`
- `services/progress.py`
- `services/progress_engine.py`
- `services/whatsapp_practice.py`
- `services/whatsapp_retention.py`
- `tests/contract/progress_reuse_fixtures.py`
- `tests/contract/test_channel_clock.py`
- `tests/contract/test_channel_preservation_contracts.py`
- `tests/contract/test_progress_reuse.py`
- `tests/contract/test_recovery_channel_preservation.py`
- `tests/e2e/channel-preservation.spec.ts`
- `tests/e2e/content-editor.ui.spec.ts`
- `tests/e2e/data-requests.spec.ts`
- `tests/e2e/mobile-reflow.spec.ts`
- `tests/fixtures/progress-rollup-v1-reuse-baseline.json`
- `tests/integration/test_channel_preservation.py`
- `tests/integration/test_channel_preservation_runtime_role.py`
- `tests/integration/test_channel_preservation_sql.py`
- `tests/integration/test_channel_receipt_holds.py`
- `tests/integration/test_progress.py`
