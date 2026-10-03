# E7 local linking verification and next-slice readiness

Verified 3 October 2026. Code commit: `23da19c`.
Requirements: FR-WA-001; bounded FR-WA-004/006, FR-ID-003/006, FR-OPS-001/003/004,
NFR-SEC-002, NFR-OBS-001 and NFR-MNT-001.
Decision: [ADR-034](../decisions/ADR/034-whatsapp-linking.md).

## Implemented local slice

Recent web authentication and current adult or guardian-plus-assent consent permit a five-minute,
single-use code. Codes are stored only as keyed hashes. Signed synthetic Meta-shaped messages
establish one owned link asynchronously. Code, sender and verified-phone collisions are rejected;
no webhook creates a user or login identifier. Owned web status and fake delivery confirm linking.

Raw-byte HMAC verification precedes strict JSON parsing, with a 64 KiB streaming cap and twenty
messages per batch. Configured synthetic business/phone identifiers must match. Acknowledgement
follows durable receipt; exact replay is inert and conflicting ID reuse rolls back the batch.
Every unique STOP creates an immediate delivery barrier, even before worker processing. STOP
retains ownership; explicit unlink clears the encrypted identifier and releases the sender.
Unlink binds the link UUID/revision and actor-bound idempotency receipt so stale retries cannot
undo a new link, including after retention cleanup.

Workers recheck current account/consent/ownership, roll back partial linking on transient failure,
and retry at most three times with 60/120-second delays. Fake delivery is feature-flagged and
rate-limited; recipient-bound status callbacks cannot regress delivery/read evidence. Terminal
processing clears transient encrypted recipients and codes. Bounded cleanup expires code hashes
at five minutes, code/mutation receipts at 24 hours and transport/unlinked records at 30 days.
Owned exports and advisory deletion inventory include channel records without exposing unbound
sender history. Channel legal-hold coverage and account erasure remain pending.

## Executed verification

[Hosted CI 37148246698](https://github.com/Jotham566/kasoma/actions/runs/37148246698)
passed the exact code commit on Ubuntu 24.04:

- `make setup`, services, clean migrations and seed.
- `make lint test openapi-check build`: 257 unit/contract and 138 integration tests (395 Python),
  five tooling tests, Python/TypeScript types, formatting, lint, generated contracts and web build.
- `make e2e security containers`: 20 browser journeys including signed local linking, lost
  acknowledgement recovery, STOP, unlink retry and accessibility; dependency audits and images.
- `make security-source security-containers container-smoke`: secret/image scans and API,
  PostgreSQL/Redis, worker and web smoke checks.

Focused coverage comprises 20 channel contracts and 14 PostgreSQL integration tests. It covers
minor/current-policy/withdrawal/recent-auth gates, code expiry/reuse/rates/concurrency, SQL code/
ownership guards, duplicate/conflicting batches, STOP before delivery, sender/verified-phone
collisions, fresh post-STOP linking, recipient-bound status progression, rollback/retry/final
failure, safe correlated logs, expiry and owned export/inventory. All providers are deterministic
fakes. No real learner data, external model/messaging/cloud calls or Gemini evaluation occurred.

## Local interruption and limitations

Earlier native full (384-test), expanded linking, browser and container runs passed. Docker
Desktop stopped during the final image rebuild; the concurrent final database run consequently
reported 56 passes, 3 failures and 79 setup errors. The focused rerun passed 20 offline contracts
but could not create its 14 database fixtures. Normal restart did not restore the engine. No data
was reset and those interrupted runs are not passing evidence. Full hosted CI above independently
verified the final snapshot, including the last correlation-log adjustment.

This verifies local linking/intake/opt-out only. FR-WA-002/003/005 five-question practice, shared
assessment parity, approved academic inventory, real provider configuration and pilot release
remain pending. No production or complete-MVP acceptance is claimed. See [release gates](RELEASE_GATES.md).

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
