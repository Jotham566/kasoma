# Current sprint: legacy hold-clock verification

Updated 19 October 2026. Earlier checkpoints remain in
[the preserved history](SPRINT_HISTORY_2026_10_18.md).

## Verified application source

Application source on main is `0c73c45`; documentation-only checkpoints may follow it.
Complete hosted [39160113771](https://github.com/Jotham566/kasoma/actions/runs/39160113771)
passes. All merged implementation branches are removed locally/remotely.

- `0c73c45`: bounded local worker model counters, truthful unknown usage, private
  five-minute Redis intervals, ADMIN snapshot/card and fake worker smoke. See
  [model verification](E8_MODEL_USAGE_VERIFICATION.md) and accepted ADR-054.
- `f5f408e`: configurable existing three-request/16,384-token/five-second envelope;
  [hosted 39157127637](https://github.com/Jotham566/kasoma/actions/runs/39157127637)
  and [runtime evidence](E4_RUNTIME_BUDGET_VERIFICATION.md) pass.
- `a357222`: bounded grading queue/lease/outcome/audit visibility and database-clock
  review completion cap; [hosted 39155326659](https://github.com/Jotham566/kasoma/actions/runs/39155326659)
  and [grading evidence](E8_GRADING_OPERATIONS_VERIFICATION.md) pass.
- Earlier independent review, staff navigation and offline report comparison remain
  verified through 2164209/17abb2d and hosted 39150319607/39151730479.

Local model-slice evidence includes 916 unit/contract and 35 tooling cases, 345 broad
integration cases plus two later dispatch-boundary cases, 110 browser executions across
serial runs, restricted login, source/dependency/image security and populated logical
restore. Full hosted acceptance is separate evidence, not inferred from local checks.

## Active unmerged hold-clock slice

`codex/hold-delete-clock`: FR-ID-006, BR-010, NFR-SEC-002 and NFR-MNT-001.
[ADR-056](../decisions/ADR/056-wall-clock-hold-delete-guards.md),
[readiness](E8_HOLD_DELETE_CLOCK_READINESS.md) and
[verification](E8_HOLD_DELETE_CLOCK_VERIFICATION.md) cover the measured boundary.
All four legacy wrappers reproduce a missed hold committed after transaction start;
forward migration 0036 changes only DELETE evaluation time. Four focused cases pass after the
fix; the upgrade/replay supplement and related suites total 57 passing cases.
918 unit/contract and 35 tooling cases, restricted logins, security, populated recovery
and rebuilt 0036 image/service smoke pass. Complete hosted acceptance remains pending.
Original append-only protections remain; no original row is erased for reproduction.

## Underlying receipt candidate

`397f562` is pushed on `codex/channel-receipt-holds` for hosted run 39165896953.
Its 21 focused receipt/clock/race/JSON-upgrade and privacy-login cases,918 unit/contract,
364 broad integration plus final supplements,102 full browser executions, final privacy
reflow and recovery/security/image/service checks pass locally. The stack is on 0036
with creation disabled. This candidate remains unmerged until hosted acceptance.

## Receipt scope and continuing safeguards

See [ADR-055](../decisions/ADR/055-terminal-channel-receipt-holds.md),
[receipt readiness](E8_CHANNEL_RECEIPT_HOLD_READINESS.md) and
[verification](E8_CHANNEL_RECEIPT_HOLD_VERIFICATION.md). Source guards, hold-aware
cleanup, staged capabilities/UI and synthetic recovery are implemented. Final 21-case
receipt/clock/race/JSON-upgrade and restricted privacy-login verification passes;918 unit/contract,
364 broad integration and 102 full browser executions pass with final focused
supplements. Applied0034 is preserved; forward migration 0035 fixes a reproduced held-menu JSON no-op
comparison. Final 0035 images/migration/service checks pass with creation disabled; hosted
acceptance remains pending.


The receipt candidate addresses FR-ID-006, FR-WA-006, FR-OPS-003, BR-010,
NFR-SEC-002 and NFR-MNT-001 with exact original-record holds on owned terminal
receipts only after transient material is cleared. STOP/unlink, delivery lifecycle
and unrelated bounded cleanup remain operational. Creation defaults disabled for
staged reader compatibility. See [channel readiness](E8_CHANNEL_HOLD_READINESS.md);
live-state preservation still requires a separately recorded design. Full hold
coverage and erasure are not complete.

## Next preservation decision

[ADR-057](../decisions/ADR/057-minimized-channel-preservation-proposal.md) is a concrete
proposal, not implementation: bounded encrypted evidence for an exact owned link or
conversation version, excluding contact/message/authentication material. It compares
continuous version history, defines ownership, atomic capture, finite retention and
access/rollout tests, and leaves full coverage/erasure disabled. Explicit owner approval
has been requested under the source-of-truth change protocol; no reply is approval.
Unaffected verification continues. A nondestructive post-power-interruption procedure
is now recorded in [local recovery](../runbooks/LOCAL_DEVELOPMENT.md).

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
