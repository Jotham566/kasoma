# Implementation checkpoint after power recovery — 19 October 2026

This is an engineering checkpoint, not a completed MVP or production release.
The [current sprint](CURRENT_SPRINT.md) and [traceability register](REQUIREMENTS_TRACEABILITY.md)
remain the live status sources. All work uses synthetic fixtures and deterministic fake
providers; no external model, Gemini, messaging, email or cloud application call is made.
Existing local volumes and unrelated work are preserved.

## Requirements and implementation

| Area | Requirements addressed | Implementation and evidence |
| --- | --- | --- |
| Grading operations | FR-OPS-002, NFR-OBS-001, NFR-SEC-002, NFR-ACC-001 | Bounded queue/lease/outcome/audit counts and stale alerts; database-clock review completion cap. [Verification](E8_GRADING_OPERATIONS_VERIFICATION.md), ADR-053. |
| Existing runtime budgets | FR-OPS-004, FR-GRD-004, NFR-SEC-002, NFR-MNT-001 | Typed existing request/token/time ceilings and shared budget enforcement; no new daily/fleet policy. [Verification](E4_RUNTIME_BUDGET_VERIFICATION.md). |
| Local model observations | FR-OPS-002, NFR-OBS-001, NFR-SEC-002, NFR-ACC-001, NFR-MNT-001 | Six attribute-free worker counters, bounded private Redis intervals, truthful unknown usage, ADMIN card and fixed fake probe. [Verification](E8_MODEL_USAGE_VERIFICATION.md), ADR-054. |
| Terminal channel receipt holds | FR-ID-006, FR-WA-006, FR-OPS-003, BR-010, NFR-SEC-002, NFR-MNT-001 | Exact owned cleared terminal receipts, SQL guards, legal callbacks, hold-aware cleanup, staged capabilities/UI and additive JSON correction. [Verification](E8_CHANNEL_RECEIPT_HOLD_VERIFICATION.md), ADR-055. |
| Legacy hold clock | FR-ID-006, BR-010, NFR-SEC-002, NFR-MNT-001 | Four DELETE wrappers evaluate current wall clock; historical predicate and source immutable guards remain. [Verification](E8_HOLD_DELETE_CLOCK_VERIFICATION.md), ADR-056. |
| ADMIN audit activity | FR-OPS-003, NFR-SEC-002, NFR-ACC-001, NFR-PERF-001, NFR-MNT-001 | Fixed-category newest-10,000 sample, strict generated contract, index, live ADMIN/rate checks and accessible UI. No individual audit disclosure. [Verification](E8_AUDIT_ACTIVITY_VERIFICATION.md), ADR-058. |
| CI capacity/recovery docs | NFR-MNT-001 | Hosted-only fixed SDK preparation, capacity gates and diagnostics; nondestructive local restart procedure. [Verification](E0_CI_STORAGE_VERIFICATION.md), ADR-059. |

NFR-PERF-001 is supported by bounded/indexed reads; no new current-source 500 ms
acceptance is claimed. Traceability now correctly links the historical objective
feedback measurement rather than implying none exists. That historical baseline is
not a new benchmark or provider/long-history acceptance.

## Verification and source status

Already merged source checkpoints a357222, f5f408e, 0c73c45 and 397f562 pass complete
hosted runs 39155326659, 39157127637, 39160113771 and 39165896953 respectively.
Their merged implementation branches are removed locally/remotely.

Application source 5d95f9d passes complete hosted run
[39171302022](https://github.com/Jotham566/kasoma/actions/runs/39171302022).
The whole pipeline passes; main contains that source plus a documentation-only
closeout, and all merged branches are removed. The old standalone clock
run 39167600610 is failed disk-capacity evidence, not accepted application evidence.
The incomplete first audit push and superseded audit run are cancelled, not passes.

Executed local commands include `make format lint openapi-check build`, `make test`,
focused hold/channel/publication/audit suites, `make test-runtime-role recovery-drill
security security-source`, `make containers migrate container-smoke security-containers`,
`make test-web-audit test-web-content e2e e2e-chromium-full`, and `make test-ci-storage
test-unit ci-storage-check check-ci-profile check-docs`. Final local results: 940
unit/contract, 35 tooling, 378 integration, 105 ordinary browser executions, three UI
harness/navigation cases and 31 full-Chromium executions pass. This aggregates named
runs, not unique test cases. Recovery verifies 65 tables/648 rows in 287 ms, pgvector,
immutable/encrypted/frozen-export evidence and the restored audit index, without
cleanup failures. Source/dependency and API/web image scans report no HIGH/CRITICAL
findings. Hosted-only real SDK preparation and later capacity gates pass in the complete run.

Resolved failures remain recorded: wrong client-factory call, missing GET proxy
allowlist entry, initial narrow large-text spacing, omitted service staging, obsolete
absent-Audit navigation assertions, and runner disk exhaustion. No assertion was
changed to grant unauthorized access; no timeout/academic threshold/retention gate was
relaxed. Follow-up commits use normal hooks and pushes; no force push or history rewrite.

All eight local Docker services are running healthy on schema 0037; the audit
page is served at http://localhost:3000/admin/audit. Receipt-hold creation stays false;
normal learner short-text delivery stays disabled. Local visual evidence and logs remain
ignored in .local. Production PITR/object recovery and physical/branded device acceptance
are not inferred from local synthetic or browser-engine results.

## Decisions and next gate

ADRs 053/054/055 record accepted local engineering. ADRs 056/058/059 are accepted after complete
corrected-source hosted acceptance. [ADR-057](../decisions/ADR/057-minimized-channel-preservation-proposal.md)
is only a concrete owner-review proposal. Approval was requested and is not recorded;
no snapshot implementation or new retention meaning is authorized by elapsed time.
The source-of-truth protocol requires human approval before changing security/data
meaning; existing original-row guards cannot silently become live-state snapshots.

The exact next proposed slice is encrypted minimized evidence for an owned exact link
revision or conversation version, preserving STOP/unlink/expiry, excluding contacts,
message bodies and authentication material, with independent recent-ADMIN authorization,
atomic capture, finite release/expiry, strict contracts and synthetic race/recovery tests.
Implement only after the proposal is approved/revised. Full preservation coverage,
erasure/anonymization and accountability expiry remain incomplete. Genuine academic
inventory/rights/benchmark/calibration, privacy/safeguarding/provider decisions, production
PITR/RPO/RTO, supported-device evidence and pilot sign-offs remain in
[release gates](RELEASE_GATES.md). These cannot be fabricated by automated tests.

## Files created or changed

Repository-relative inventory from the pre-checkpoint source 17abb2d through verified source
5d95f9d; 112 files. This report is the additional closeout document.

- `.env.example`
- `.github/workflows/ci.yml`
- `AGENTS.md`
- `CHANGELOG.md`
- `Makefile`
- `apps/api/migrations/versions/0034_channel_receipt_holds.py`
- `apps/api/migrations/versions/0035_channel_receipt_json_guard.py`
- `apps/api/migrations/versions/0036_hold_delete_wall_clock.py`
- `apps/api/migrations/versions/0037_audit_activity_index.py`
- `apps/api/operations.py`
- `apps/web/app/admin/audit/page.tsx`
- `apps/web/app/admin/navigation.tsx`
- `apps/web/app/admin/operations/page.tsx`
- `apps/web/app/api/v1/[...path]/route.ts`
- `apps/web/app/globals.css`
- `apps/web/app/privacy/legal-holds.tsx`
- `apps/worker/model_metrics.py`
- `docker-compose.yml`
- `docs/decisions/ADR/051-blinded-review-and-release-unit-sampling.md`
- `docs/decisions/ADR/052-offline-evaluation-report-comparison.md`
- `docs/decisions/ADR/053-bounded-grading-operations.md`
- `docs/decisions/ADR/054-bounded-worker-model-usage.md`
- `docs/decisions/ADR/055-terminal-channel-receipt-holds.md`
- `docs/decisions/ADR/056-wall-clock-hold-delete-guards.md`
- `docs/decisions/ADR/057-minimized-channel-preservation-proposal.md`
- `docs/decisions/ADR/058-bounded-admin-audit-activity.md`
- `docs/decisions/ADR/059-disposable-ci-runner-storage.md`
- `docs/decisions/ADR/README.md`
- `docs/implementation/CURRENT_SPRINT.md`
- `docs/implementation/E0_CI_STORAGE_VERIFICATION.md`
- `docs/implementation/E4_EVALUATION_REPORT_READINESS.md`
- `docs/implementation/E4_EVALUATION_REPORT_VERIFICATION.md`
- `docs/implementation/E4_EXPERT_REVIEW_READINESS.md`
- `docs/implementation/E4_EXPERT_REVIEW_VERIFICATION.md`
- `docs/implementation/E4_RUNTIME_BUDGET_READINESS.md`
- `docs/implementation/E4_RUNTIME_BUDGET_VERIFICATION.md`
- `docs/implementation/E6_STAFF_NAVIGATION_VERIFICATION.md`
- `docs/implementation/E8_AUDIT_ACTIVITY_READINESS.md`
- `docs/implementation/E8_AUDIT_ACTIVITY_VERIFICATION.md`
- `docs/implementation/E8_CHANNEL_HOLD_READINESS.md`
- `docs/implementation/E8_CHANNEL_RECEIPT_HOLD_READINESS.md`
- `docs/implementation/E8_CHANNEL_RECEIPT_HOLD_VERIFICATION.md`
- `docs/implementation/E8_GRADING_OPERATIONS_READINESS.md`
- `docs/implementation/E8_GRADING_OPERATIONS_VERIFICATION.md`
- `docs/implementation/E8_HOLD_DELETE_CLOCK_READINESS.md`
- `docs/implementation/E8_HOLD_DELETE_CLOCK_VERIFICATION.md`
- `docs/implementation/E8_MODEL_TELEMETRY_VERIFICATION.md`
- `docs/implementation/E8_MODEL_USAGE_READINESS.md`
- `docs/implementation/E8_MODEL_USAGE_VERIFICATION.md`
- `docs/implementation/RELEASE_GATES.md`
- `docs/implementation/REQUIREMENTS_TRACEABILITY.md`
- `docs/implementation/SPRINT_HISTORY_2026_10_18.md`
- `docs/runbooks/LOCAL_DEVELOPMENT.md`
- `docs/specifications/03_Domain_and_Data_Model.md`
- `docs/specifications/04_API_and_Integration_Contract.md`
- `docs/specifications/06_AI_RAG_and_Grading_Guardrails.md`
- `docs/specifications/13_ADR_and_Decision_Log.md`
- `packages/analytics-schema/operations-alert.schema.json`
- `packages/api-client/openapi.json`
- `packages/api-client/src/schema.d.ts`
- `pyproject.toml`
- `scripts/ci_runner_storage.py`
- `scripts/container_smoke.py`
- `scripts/dev.py`
- `scripts/e2e_api.py`
- `scripts/model_metrics_smoke.py`
- `scripts/recovery_channel_receipts.py`
- `scripts/recovery_drill.py`
- `scripts/recovery_fixture.py`
- `services/audit_activity.py`
- `services/config.py`
- `services/deletion_preview.py`
- `services/grading_operations.py`
- `services/grading_reviews.py`
- `services/legal_hold_contracts.py`
- `services/legal_holds.py`
- `services/metric_interval_store.py`
- `services/metric_reader.py`
- `services/model_metric_collector.py`
- `services/model_metric_store.py`
- `services/model_metrics.py`
- `services/model_telemetry.py`
- `services/observed_model_gateway.py`
- `services/operations.py`
- `services/operations_contracts.py`
- `services/request_metrics_collector.py`
- `services/request_metrics_store.py`
- `services/short_text_processor.py`
- `services/whatsapp_retention.py`
- `tests/contract/test_ci_runner_storage.py`
- `tests/contract/test_legal_hold_contracts.py`
- `tests/contract/test_model_metrics.py`
- `tests/contract/test_model_telemetry.py`
- `tests/contract/test_operations_contract.py`
- `tests/contract/test_short_text_orchestration.py`
- `tests/e2e/audit.spec.ts`
- `tests/e2e/audit.ui.spec.ts`
- `tests/e2e/content-editor.ui.spec.ts`
- `tests/e2e/data-requests.spec.ts`
- `tests/e2e/flags.spec.ts`
- `tests/e2e/learner-home.spec.ts`
- `tests/e2e/operations.spec.ts`
- `tests/e2e/short-text.spec.ts`
- `tests/integration/test_audit_activity.py`
- `tests/integration/test_channel_receipt_holds.py`
- `tests/integration/test_channel_receipt_runtime_role.py`
- `tests/integration/test_grading_operations.py`
- `tests/integration/test_grading_reviews.py`
- `tests/integration/test_hold_delete_clock.py`
- `tests/integration/test_model_metric_store.py`
- `tests/integration/test_operations.py`
- `tests/integration/test_short_text_processing.py`
