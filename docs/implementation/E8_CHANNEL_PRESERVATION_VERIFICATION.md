# ADR-057 bounded synthetic capture verification

Date: 19 October 2026. Candidate under verification, not application acceptance.
Requirements advanced: FR-ID-006, FR-WA-006, FR-OPS-003, BR-010, NFR-SEC-002,
NFR-MNT-001 and NFR-ACC-001; the advancing-clock correction also addresses FR-WA-002.
Follow [ADR-057](../decisions/ADR/057-minimized-channel-preservation-proposal.md),
[capture readiness](E8_CHANNEL_PRESERVATION_CAPTURE_READINESS.md) and the
[verified private format](E8_CHANNEL_PRESERVATION_FORMAT_VERIFICATION.md).

## Implemented candidate

- Additive 0038 assigns noncycling conversation mutation versions, preserves existing
  link revision rules and creates separate immutable metadata, disposable ciphertext
  and disposal receipts. No operational source FK can block STOP/unlink or expiry.
- Strict generated source/version/capture contracts, current independent recent-OTP
  claimant checks, exact owned source/version validation and shared read/write limits.
  Inspection uses JSON POST and returns only an opaque keyed version. Source queries
  avoid loading contact ciphertext. No source browsing or payload-reading API.
- Atomic finite capture, audit, outbox and exact retry receipts. Explicit rollback
  boundaries preserve rate accounting without committing partial capture/additional
  decisions/releases on IdentityError. New kinds use database wall clock.
- Independent SQL ownership/version/completeness/immutability guards; bounded cleanup
  excludes active decisions before LIMIT, skips locked evidence and prevents resurrection.
  It continues with creation disabled. Minimized metadata follows the existing parent
  request accountability policy; its expiry processor remains separately pending.
- Advisory owned inventory distinguishes evidence held only while a decision is active
  from retained accountability. Internal decisions/ciphertext remain excluded from
  ordinary learner export. Coverage remains incomplete and erasure execution false.
- Accessible exact-source checking and finite-decision controls with stale/re-auth/
  uncertain-response states, precise dropdown labels and the original receipt selector.
  Creation defaults false through CHANNEL_PRESERVATION_ENABLED; production remains
  unavailable under existing settings and release gates.

## Focused evidence

`make test-channel-preservation` passes 105 socket-disabled contract/format cases and,
at the last completed focused run, 34 integration cases including actual restricted
logins for both snapshot kinds. `make test-channel-clock` passes two advancing-clock
regressions, which fail before the correction. These runs cover:

- Current-role/re-auth/independent claim and owner denials, disabled capabilities,
  exact retry without recapture, same-time mutation versions and source reinsertion.
- Every capture flush boundary and late additional-decision/release rollback.
- Independent rejection of an unbound outbound reference in an owned conversation.
- Multiple decisions, exact database-clock expiry with a behind logical clock,
  disposal/reinsertion denial, hard 100-body batches and active-prefix starvation.
- A real uncommitted SQL decision locking evidence out of cleanup; capture/unlink
  concurrency, signed immediate STOP, shared objective grading while preserved,
  additive 0037 upgrade/replay and preservation of existing held records.
- Owned preview/export minimization and immutable evidence despite operational source
  cleanup. One initial inventory assertion conflated owned and staff-provenance rows;
  the corrected test retains both categories and passes.

The initial real-time browser journey passes in Chromium, Firefox and WebKit. It covers
link and conversation capture, exact key/body replay after a lost response, stale-state
recovery, signed STOP and release. Axe, keyboard source checking, 320-pixel reflow and
200%-text checks pass. Mobile screenshots were inspected. Additional desktop captures
and withdrawal coverage are included in the full regression. Its first batch exposed
a withdrawal assertion expecting UNLINKED after STOP (the existing STOPPED barrier
is preserved) and duplicate legal-hold landmark names when several request cards
coexist. The assertion follows the established state; each region now includes its
request identifier in its accessible name. Axe remains required without exclusions. The next browser run also caught an obsolete
exact selector-option inventory; it now includes both explicitly advertised snapshot
kinds. No permission or timeout was changed. The complete 108-execution browser run then
passed (32 ordinary journeys and four synthetic short-text journeys per engine),
plus three UI harness and three native WebKit download controls. Desktop screenshots
were inspected in each engine. Visual review exposed a native WebKit select of only
23 pixels despite CSS min-height; a new 44-pixel target assertion reproduced it.
Scoped menu styling preserves a visible arrow and the target-size test now also
runs at 200% text. The final focused journey passes in all three engines at normal and 200% text;
corrected WebKit desktop output was visually inspected.

The first browser attempts caught a missing test setup status refresh, an imprecise
wrapped-select label and an actual advancing-clock expiry defect in both conversation
creation and update. Explicit dropdown labels and one timestamp per exact 24-hour pair
correct these; no timeout or SQL invariant was relaxed. Previous fixed-clock fixture
acceptance does not establish real-time provider acceptance.

`make recovery-drill` passes with 68 tables/680 synthetic rows, 302-ms logical restore,
pgvector, frozen export and short-text evidence plus new bound snapshot decryption,
disposal receipts, sequence position and immutable guards after source removal.
The first two fixture attempts were rejected by existing claim ownership and OTP
cooldown. The fixture now reuses its exact current claimant context in memory; no
policy is loosened and no token is printed. This is not PITR, production RPO/RTO or
object-storage recovery acceptance.

The full local backend run passes 1,055 unit/contract and 35 tooling cases, and
411 of 412 integration cases. Its sole failure is the historical 0034 JSON-guard
upgrade fixture invoking the current conversation ORM before the new column exists.
The fixture now creates its terminal menu with original receipt columns, asserts
0034 explicitly, and retains the expected JSON-equality failure, held receipt replay
and two forward upgrades. The corrected 21-case receipt/restricted-login suite passes, including that upgrade.
A complete hosted run remains required before promotion.

Formatting, Python/TypeScript type checks, generated contracts and native builds pass.
Source/dependency/image security, populated recovery, additive migration and Docker
smoke pass. Complete hosted verification remains required before promotion. The additive
local migration and rebuilt service smoke pass, including asynchronous frozen export
and scoped live request metrics; all eight services are healthy on schema 0038,
with capture creation still false. Source/dependency/image scans report no findings
at their configured thresholds; the final scoped target-size image refresh and scan pass. No real provider,
real learner data or Gemini evaluation is used.

## Remaining boundary

This slice preserves only the approved minimized exact link/conversation versions.
Queued bodies, codes, sender barriers, actor/key receipts, logs, embedded references,
backups and full erasure coverage remain outside it. No raw-dispute legal sufficiency,
anonymous-data claim, real-data approval, academic/provider authority or production
release gate is supplied by this engineering evidence.

## Change inventory

- Runtime/configuration: Makefile, .env.example, settings and API route/proxy.
- Persistence: migration 0038, Alembic imports, channel evidence domain and
  conversation mutation version mapping.
- Services: exact capture/contracts, hold decisions, disposal, advisory inventory,
  recovery fixtures and the existing conversation clock correction.
- Web/contracts: capture and hold controls, preview policy label, scoped select styling,
  generated OpenAPI and TypeScript client.
- Tests: format/contracts, rollback/ownership/races, actual restricted logins, additive
  upgrade/SQL guards, recovery guards, advancing clock and browser journeys.
- Documentation: ADR-057 implementation details, data/API appendices, local runbook,
  readiness/verification, sprint, traceability, changelog and repository stage.

No architectural decision outside the approved ADR-057 boundary is introduced.
Next unblocked engineering slice: request-local reuse of identical skill estimates
for progress rollups under ADR-024 (FR-MST-004/005, NFR-PERF-001), preserving exact
DTO/hash/change semantics, consent and sealed-diagnostic filtering.
