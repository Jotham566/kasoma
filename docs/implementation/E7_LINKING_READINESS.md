# E7 linking and message-intake implementation readiness

Date: 3 October 2026. Status: implementation under final verification; no acceptance claimed.
Requirements: FR-WA-001/004/006, FR-ID-003, FR-OPS-001/003/004,
NFR-SEC-002, NFR-OBS-001 and NFR-MNT-001.

## Intended first vertical slice

Authenticated web learner requests a short-lived one-time code only after the existing
profile/consent gate passes. A signed synthetic Meta-shaped inbound message consumes the
code asynchronously and establishes a unique owned channel link. Both channels receive
confirmation through local state/fake delivery. Web unlink and incoming STOP prevent
subsequent queued delivery. No account is created or silently merged by a webhook.

The following slice adds START/CONTINUE and five-question objective practice through
existing assessment/grading/mastery services, with HELP/PROGRESS and concise authored
feedback. The first slice must not be labelled complete WhatsApp support: FR-WA-002/003/005
remain pending until the shared learning journey and parity/replay tests pass.

## Existing implementation and dependencies

- Identity authenticates opaque sessions, requires recent sign-in for sensitive changes,
  encrypts identifiers, uses keyed lookups and serializes actor mutations.
- `IdentityService.profile` checks the active policy and guardian-plus-assent/adult-self
  declarations. Recheck this gate at code issue, consumption and outbound processing.
- Assessment currently authorizes a web bearer. Channel integration must introduce a
  trusted authenticated-actor entry point with the same consent/enrollment checks,
  never a fabricated bearer or separate grading/mastery implementation.
- PostgreSQL-backed commands, bounded retry handling, Celery queues and operation alerts
  now have reusable patterns. Redis remains disposable; progress/deduplication lives in SQL.
- The current fake messaging provider needs durable idempotent delivery evidence for this
  path. Test fakes must not make any external call. Production Meta credentials, account
  registration and real message delivery remain outside the authorized development profile.

## Contract and data work

Use the specified link-code POST, webhook GET/POST and link DELETE routes. Add an owned
status read for the web confirmation only through an ADR and generated contracts.
Use the specified channel_links, link_codes, inbound_messages, conversation_states and
outbound_messages entities as needed by the vertical slice; avoid speculative tables.
Enforce sender/link uniqueness, code single-use/expiry and provider-message uniqueness
in SQL as well as services. Sensitive identifiers are encrypted with keyed lookup indexes.
Code material, webhook bodies and contacts never enter logs or client configuration.

A bounded raw-body reader must precede parsing. Verify the SHA-256 signature against the
exact received bytes, then parse only supported fields. Ignore provider contact-profile
names and media URLs. Bind the configured business account/phone identifiers, and reject
conflicting reuse of a provider message ID. Record minimized durable receipt state before
acknowledgement; actual linking and replies execute asynchronously.

Link issuance/consumption, unlink, STOP, consent withdrawal, retries and outbound sending
need consistent locks and a defined ordering barrier so stale deliveries cannot relink an
account or bypass opt-out. Check collisions with another account's verified identifiers;
never silently merge or transfer an active link. Do not make the link a new login method.
Include new owned records in export projection and deletion-impact inventory, and document
expiry/retention instead of introducing indefinite raw webhook storage.

## Decisions to record with implementation

Record an ADR before schema/API changes: exact code lifetime/entropy and retry behavior,
rate/attempt limits, sender normalization, allowed signed fixture schema, event ordering,
STOP/unlink barriers, bounded job retries, outgoing-message limit and fake delivery receipt
semantics. These are engineering choices within MVP discretion; none approves a provider,
minor-consent policy, academic content or real-data processing.

## Acceptance evidence required

- Expired/consumed codes, concurrent claims, actor/sender collisions and generic denials.
- Missing profile/consent, minor consent combinations, changed policy and withdrawal races.
- Signature verification before parsing; malformed/chunked/oversized payload rejection;
  configured business identity checks; duplicate/conflicting/out-of-order message IDs.
- Crash/retry atomicity, no duplicate links/replies, current outbound consent/opt-out checks,
  STOP/unlink before pending delivery, delivery-status progression and safe dead-letter state.
- Owned status/export boundaries, encrypted identifiers and logs without bodies or codes.
- Web code expiry/retry/status/unlink flow and accessibility; fake-only webhook/worker flow.
- Clean migrations, generated contracts, standard quality checks and required documentation.

## Initial boundary evidence (superseded by the checkpoint below)

`services/whatsapp_ingress.py` verifies exact raw-byte SHA-256 signatures with constant-time
comparison before JSON parsing. It rejects missing configuration, invalid signatures,
empty/oversized bodies, duplicate JSON fields, non-finite numbers and invalid encoding.
`tests/contract/test_whatsapp_ingress.py` includes tampering, parser-order and size-boundary
regressions using a public synthetic fixture key. `make format test-unit lint` passes
249 unit/contract tests and five tooling tests. At that initial checkpoint no HTTP route or domain action was exposed.
The later checkpoint below records the implemented transport and domain path.

## Sources and limitations

Binding repository sources: [SRD](../specifications/01_SRD.md),
[API contract](../specifications/04_API_and_Integration_Contract.md),
[data model](../specifications/03_Domain_and_Data_Model.md),
[security](../specifications/09_Security_Privacy_and_Safeguarding.md),
[UX](../specifications/08_UX_Flows_and_Accessibility.md) and
[QA](../specifications/10_Testing_Acceptance_and_Release.md).

Meta's [payload reference](https://www.postman.com/meta/whatsapp-business-platform/folder/vzaxn16/webhook-payload-reference)
provides the envelope and delivery-status structure. Meta's archived
[SDK webhook reference](https://whatsapp.github.io/WhatsApp-Nodejs-SDK/api-reference/webhooks/start/)
documents verification challenge and signature checks; no archived SDK will be installed.
Direct current developer-document fetches were rate-limited during inspection; this is
not evidence of current production integration acceptance. No provider API, real sender,
model, messaging service or production learner data was used in this assessment.

## Implementation checkpoint — 3 October 2026

Additive migration 0018 and owner code/status/unlink routes are implemented. Unlink binds the
observed link UUID and revision to its idempotency receipt, including after retention cleanup.
Signed Meta-shaped intake binds the synthetic destination and acknowledges only durable rows.
Every unique STOP establishes a barrier at intake; even unbound subsequent HELP cannot bypass it.
Asynchronous processing and fake delivery recheck current consent/account/ownership, use bounded
retries and erase transient encrypted recipients on termination. No external provider is enabled.

Owned export and deletion-preview inventory include channel records; unbound sender history is
excluded from account disclosure. Channel legal holds remain a separate pending coverage gap.
The retention processor bounds cleanup batches and clears expired code hashes, 24-hour code/
mutation receipts, expired pending jobs and 30-day transport/unlinked records.

`make services migrate seed` passed locally (Docker recovered without a reset). `make test-whatsapp`
passed 24 tests: 13 signature contracts and 11 PostgreSQL integration tests, including clean schema
migration, consent/minor/policy/recent-auth, code rate/replay/concurrency, SQL ownership/code guards,
atomic conflicting-message rollback, STOP before processing, delivery withdrawal/retry, worker
rollback, transient expiry and owned export/inventory. `make format typecheck` passed.
The web UI, generated contracts, worker schedule and browser journey are now implemented but
full-suite, browser, security and container verification remain pending. This checkpoint does not
claim FR-WA acceptance or production readiness.

## Local operation and rollback

`make setup` generates missing local signing/challenge secrets without printing them. Only fake
WhatsApp transport and synthetic business/phone IDs are accepted. Keep `WHATSAPP_OUTBOUND_ENABLED`
false unless testing local fake receipt delivery. `/channels/whatsapp` exposes owned code/status/
unlink; the API webhook is not forwarded by the browser proxy. `make process-messages` drains a
bounded batch using the same processor as the ten-second Celery messaging queue schedule.
Automated integration/browser fixtures sign their own synthetic messages and make no external calls.

Stop messaging workers and disable the channel entry points for rollback; preserve migration rows
and apply a forward fix. Never downgrade/delete evidence or reset volumes to repair this slice.
No cloud adapter, real phone number, Gemini call or academic practice is enabled by these commands.

For a manual synthetic fixture, run `make dev`, obtain a code on `/channels/whatsapp`, then
set `KASOMA_WHATSAPP_TEXT` to `LINK <code>` for `make simulate-whatsapp`. The command signs a
single local message using a fixed synthetic sender; it prints neither the code nor secrets.
Use `HELP` or `STOP` for subsequent commands and refresh owned status in the web UI. The same
fixed sender cannot link to two accounts; explicitly unlink before testing a different account.
`WHATSAPP_OUTBOUND_PER_MINUTE` (default 10) and `WHATSAPP_LINK_ATTEMPTS_PER_MINUTE` (default 5)
configure bounded local usage limits. Never enter a real learner number or data.

Subsequent adversarial checks passed for sender/verified-phone collisions, post-STOP relinking,
recipient-bound monotonic status callbacks, final processing failure and configurable usage limits.
The latest unit suite passes 257 tests plus five tooling tests; the expanded linking integration
suite passes 14 tests. Initial full regressions passed 384 Python tests; final regressions now
include the added cases (395 total). Dependency audits and source secret scanning passed.
Final browser/container results are still pending and must be recorded before publication.

## Next slice assessment — shared five-question practice

Read-only inspection confirms that `AssessmentService.start`, `next_item` and `submit` currently
open their own transactions and authorize web tokens; `StartRevision.channel` currently permits
WEB only. The next slice must extract shared transaction-scoped actor-authorized operations,
retaining actor locks, current account/consent/enrollment checks, content eligibility, idempotent
attempt receipts, deterministic graders and atomic mastery/event updates. The channel worker
will call those operations within its receipt transaction, never fabricate a learner token.

Add expiring conversation/session pointers and supported-content selection for five-question
sessions. Commands START/CONTINUE/PROGRESS/HELP/STOP must remain explicit. Structured answers need
an unambiguous question/reply reference so delayed messages cannot answer the next question.
Outbound templates must reconstruct minimal approved question/grade references under current
consent, ownership and STOP checks, rather than persist arbitrary learner message bodies.
Record these choices in the next ADR and prove web/channel score and mastery parity before
marking FR-WA-002/003/004/005/006 complete. No academic inventory or production approval is implied.

Final verification interruption: Docker Desktop's engine stopped during the final image rebuild.
The concurrent database run then reported connection-refused/setup errors (56 integration tests
passed before/around the interruption; 3 failed and 79 errored). The focused correlation rerun
passed 20 offline contracts but all 14 database fixtures were unavailable. These runs are not
acceptance evidence. Normal Docker restart did not restore its engine; no volumes were reset.
Earlier full 384-test, expanded 14-integration, 20-browser and container-smoke runs passed;
final lint/types/contracts passed. Hosted CI must verify the exact committed snapshot before
promotion to main. The last code adjustment propagates inbound correlation IDs into safe worker
logs and labels webhook requests WHATSAPP; it still needs database execution in the final snapshot.
