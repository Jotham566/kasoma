# Current sprint: verified model observations and terminal receipt follow-up

Updated 18 October 2026. Earlier checkpoints remain in
[the preserved history](SPRINT_HISTORY_2026_10_18.md).

## Verified application source

Application source on main is `0c73c45`; documentation-only checkpoints may follow it.
Complete hosted [39160113771](https://github.com/Jotham566/kasoma/actions/runs/39160113771)
passes. All merged implementation branches are removed locally/remotely.

- `0c73c45`: bounded local worker model counters, truthful unknown usage, private
  five-minute Redis intervals, ADMIN snapshot/card and fake worker smoke. See
  [model verification](E8_MODEL_USAGE_VERIFICATION.md) and accepted ADR-054.
- `f5f408e`: configurable existing three-request/16,384-token/five-second envelope;
  [hosted39157127637](https://github.com/Jotham566/kasoma/actions/runs/39157127637)
  and [runtime evidence](E4_RUNTIME_BUDGET_VERIFICATION.md) pass.
- `a357222`: bounded grading queue/lease/outcome/audit visibility and database-clock
  review completion cap; [hosted39155326659](https://github.com/Jotham566/kasoma/actions/runs/39155326659)
  and [grading evidence](E8_GRADING_OPERATIONS_VERIFICATION.md) pass.
- Earlier independent review, staff navigation and offline report comparison remain
  verified through2164209/17abb2d and hosted39150319607/39151730479.

Local model-slice evidence includes916 unit/contract and35 tooling cases,345 broad
integration cases plus two later dispatch-boundary cases,110 browser executions across
serial runs, restricted login, source/dependency/image security and populated logical
restore. Full hosted acceptance is separate evidence, not inferred from local checks.

## Active unmerged work

`codex/channel-receipt-holds` is the next engineering slice, not merged application
behavior. FR-ID-006, FR-WA-006, FR-OPS-003, BR-010, NFR-SEC-002 and NFR-MNT-001:
assess exact original-record holds on owned terminal receipts only after transient
material has been cleared. Preserve STOP/unlink, delivery lifecycle and unrelated
bounded cleanup. New creation must default disabled for staged reader compatibility.
See [channel readiness](E8_CHANNEL_HOLD_READINESS.md); live-state preservation still
requires a separately recorded design. Do not claim full hold coverage or erasure.

## Review stack and remaining gates

All eight Compose services are kept running for review at http://localhost:3000;
Mailpit is http://localhost:8025. Existing volumes are retained. Local candidate UI
visibility alone does not establish main or production acceptance. Use fictional data.
Native Playwright commands run sequentially; do not rebuild native .next during a
browser server run. Docker builds have a separate filesystem.

Normal learner short-text scoring stays disabled. Synthetic fixtures/fake agreement
are not academic, legal, safeguarding, licensing or provider approval. Gemini remains
manual and owner opt-in; no external provider or real learner data is used here.

The MVP is not complete. Genuine inventory/benchmark/calibration, privacy/DPIA/PDPO,
provider/pilot approvals, full preservation, erasure/anonymization/accountability expiry,
production PITR/RPO/RTO and branded/physical-device evidence remain in
[release gates](RELEASE_GATES.md) and [requirements traceability](REQUIREMENTS_TRACEABILITY.md).
