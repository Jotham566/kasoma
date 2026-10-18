# Terminal channel receipt holds — candidate verification

18–19 October 2026. FR-ID-006, FR-WA-006, FR-OPS-003, BR-010, NFR-SEC-002, NFR-MNT-001.
See [ADR-055](../decisions/ADR/055-terminal-channel-receipt-holds.md) and
[readiness](E8_CHANNEL_RECEIPT_HOLD_READINESS.md). This candidate is not merged.

## Changes and limits

Migration 0034 extends exact original-record holds only to explicitly owned, already
minimized terminal inbound/outbound receipts. Queued/unbound/cross-owner messages,
links, conversations and usable authentication material remain unsupported. No new
snapshot, body copy, provider, personal-data category or blanket account hold.

Channel-lock serialization, SQL eligibility/owner validation, source DELETE/core-update
guards and database-clock checks protect against cleanup races and host skew. Existing
monotonic delivery callbacks remain allowed. Cleanup excludes held rows before LIMIT;
related FK dependencies remain and unrelated eligible rows continue to expire. Existing
finite release/expiry, independent fresh ADMIN claim, replay, audit and export boundaries
remain. Deletion preview continues to report incomplete coverage and disabled execution.

New creation defaults disabled through CHANNEL_RECEIPT_HOLDS_ENABLED. Existing hold
pages advertise supported kinds; UI options depend on that advertisement. Disablement
blocks creation/replay but keeps registered evidence readable/releasable. Enable only
after all API/worker readers support the new enum, preserving staged deployment safety.

## Executed evidence and pending gates

- `make format lint openapi-check`: passes for the initial implementation. Generated
  HoldInput/HoldView enums and HoldPage.supported_record_types match the API/client.
  Final static checks pass. The broad run passes 364 cases; later clock, restricted
  privacy-login and JSON guard/upgrade additions are verified separately.
- `make test-channel-receipt-holds`: initial 13 cases pass; expanded 16 cases pass including
  real signed LINK/practice/STOP/unlink and fake delivery barriers, actual advisory-lock
  cleanup contention, old-transaction DELETE, historical expiry, host/database clock
  cap, multiple holds, 101 unrelated receipts, direct SQL denial and0033 upgrade/replay.
  Both READ and FAILED callback paths pass. Final 21-case focused verification
  includes future-claim safe503, a distinct restricted privacy login, real held menu
  JSON no-op/callback/core-immutability, and0034-to0035 upgrade with exact hold replay.
- `make test-legal-holds test-whatsapp`:19 hold and34 channel cases pass. No existing
  type, guard, consent, sender barrier or code-expiry rule is weakened.
- `make test-unit`:918 Python unit/contract and 35 tooling cases pass, including explicit
  default-disabled capability checks. Broad PostgreSQL regression passes 364 cases; final focused supplements cover
  additions after collection. Complete hosted acceptance remains required.
- `make test-web-privacy`: the first expanded run catches 320-pixel/200% text form
  overflow. Scoped fieldset/control bounds and account-grid sizing fix it; all six
  three-engine journeys then pass, including advertised/disabled presentation and axe.
  Final readable-width/brand-control refinement passes six privacy journeys and
  two UI harness cases; the full90-journey matrix plus12 short-text cases also pass.
  The final copy explains resumption of normal retention only when no hold remains.
  An initial unlink fixture used the wrong HTTP route; it is corrected to the existing
  DELETE /channels/whatsapp/link contract and both real opt-out cases pass.
- `make test-runtime-role recovery-drill`: actual restricted login and populated logical
  restore pass. The drill now includes two original held channel receipts, independent
  request claim/decisions and restored source guards:65 tables/648 rows,357ms initially and 405 ms after the JSON correction,
  pgvector, immutable guards, encrypted short-text and frozen owned export verified.
  Production PITR/RPO/RTO and durable object recovery remain unverified.
- Source/dependency security and initial rebuilt-image scans/smoke pass. Persistent
 0034 and all eight rebuilt services pass smoke/health with new creation disabled.
 A final real menu regression exposes PostgreSQL json record-equality failure on
 no-op updates. Preserve applied 0034 and add forward migration 0035 using canonical JSONB
 comparison; fresh and upgrade/replay tests pass. Final 0035 rebuild, migration, eight-service health, fake worker/export/request
 smoke and application image security scans pass. Runtime API inspection confirms
 schema 0035 and new creation disabled. Hosted acceptance remains pending. No volume reset or row transform.

Local logs `.local/channel-receipt-hold-*.log`; original overflow trace is retained.
No real learner data or external model/Gemini/messaging/email/cloud calls are used.
These engineering tests do not establish a genuine legal decision or production
privacy/academic approval. Full preservation and erasure/anonymization remain open.
