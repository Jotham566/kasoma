# Terminal channel receipt hold readiness

18 October 2026. FR-ID-006, FR-WA-006, FR-OPS-003, BR-010, NFR-SEC-002, NFR-MNT-001.

Read the authoritative index/SRD, security retention schedule, production decisions,
ADR-030/043/045, channel readiness, current hold/messaging migrations, services and
synthetic tests before this assessment. Existing holds protect exact original rows;
channel retention clears usable data before its bounded 30-day terminal cleanup.
The persistent stack has additive0034 with new creation disabled. A menu JSON
comparison regression requires forward migration 0035; isolated clean/upgrade tests pass and
final rebuild/migration/security/smoke verification passes with creation disabled.
Hosted acceptance remains pending.

The smallest safe extension is exact holds on owned already-minimized terminal inbound
and outbound receipts. It does not require copying contact details/answers, preserving
usable codes or freezing active conversations/links. See proposed
[ADR-055](../decisions/ADR/055-terminal-channel-receipt-holds.md). Callbacks may advance
only their existing delivery lifecycle; core receipt fields remain protected.

Implementation sequence:

1. Additive 0034 enum/ownership/terminal-state validation and channel DELETE/core-update
   guards; preserve existing hold types/replay and live channel constraints.
2. Existing hold service/UI/contracts: explicit terminal-receipt choices, channel lock,
   database-clock cap and no body exposure. Keep queued/unbound targets unsupported.
3. Ordinary retention: active-hold exclusion before bounded selection, dependencies and
   unrelated cleanup progress, exact expiry/release and multiple-hold behavior.
4. Synthetic real PostgreSQL API/direct-SQL/transition/race/upgrade tests, restricted
   login, export/preview boundaries and existing STOP/unlink/conversation regression.
5. Generated contracts, UI/axe/reflow, lint/types, clean migrations, populated recovery,
   security, rebuilt Docker stack and hosted verification before main promotion.

No erasure, anonymization, new payload snapshot or real-data processing is authorized by
this engineering slice. Broader preservation, accountability expiry, privacy/legal and
production release gates remain open. No claim of complete MVP or hold coverage.
