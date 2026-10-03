# ADR-034: Consent-gated WhatsApp linking with durable message intake

Date: 3 October 2026
Status: Accepted within delegated MVP implementation discretion; local fake implementation verified
Requirements: FR-WA-001/004/006, FR-ID-003, FR-OPS-001/003/004, NFR-SEC-002, NFR-OBS-001

## Decision

Implement the required Meta-shaped signed webhook boundary using local synthetic fixtures
and a deterministic fake delivery adapter only. No cloud SDK, real number, provider account,
external delivery or new login method is enabled. Production remains blocked by existing gates.

Recent web authentication and the existing current-policy learning-consent gate are required
to issue a code. Codes contain 48 bits derived with the existing keyed digest from a random
row UUID, expire after five minutes and are single-use. Store a keyed code hash, never the
plaintext; deterministic recomputation supports same-key retry while the code remains valid.
Issuing a new code revokes prior unused codes. Limit new issues to five/hour/account and
link attempts to five/minute/sender. Expiry clears hashes; receipt metadata expires after
24 hours. Reusing a key after receipt expiry creates a fresh random row/code, never revives
an old code. Code strings and tokens are never logged.

Verify exact raw-byte HMAC-SHA256 before parsing, with a 64 KiB streaming cap. Bind the
configured synthetic business account and receiving phone ID. Retain only normalized sender
lookup/encrypted values, parsed command/status, timestamps, keyed payload/message hashes and
processing metadata. Ignore contact names, media URLs and unsupported free text. A unique
provider-message identity and canonical payload hash distinguish replay from conflicting reuse.
Acknowledge only after durable PostgreSQL intake; workers process asynchronously. Redis is
wake-up transport. Status callbacks use their provider ID/status/timestamp identity separately
from incoming message IDs and must not regress delivery state.

Links are unique per learner and per bound external sender (ACTIVE or STOPPED). STOP
retains ownership; only explicit web unlink releases the sender for another account. Never silently move an
active link, merge identities or attach a new login identifier. Reject collisions with another
account's verified phone. An owned status GET supplements the specified link-code POST and
link DELETE endpoints. Unlink carries the observed link UUID and revision and an actor/key-bound
receipt (24-hour retry window), so an old retry cannot unlink a newly established link.
The UUID prevents old retries from matching a new row after retention cleanup.
A compact sender table retains ordering barriers independently of a bound account. Web status, expiry and fake reply confirmation complete the local flow.

Serialize actor-sensitive work with identity's actor lock before the channel mutation lock;
recheck any pre-resolved sender/actor association after locking and retry if it changed.
For this initial bounded local channel, a single channel mutation lock orders receipt processing,
link/unlink, STOP and fake outbound delivery. No external request is made under that lock.
Every unique signed STOP conservatively establishes an immediate barrier, including late arrivals;
provider timestamp order cannot suppress an opt-out. Duplicate receipt replay is inert.
STOP/unlink establish a sender delivery barrier and cancel queued replies. A link code issued
before that barrier cannot reactivate the sender. The future practice slice must also end the
linked practice session. Existing consent/account/policy checks run at consumption and delivery;
withdrawal therefore blocks queued personal/learning replies without changing consent policy.

Only static neutral LINKED/STOPPED/HELP/LINK_REJECTED/UNSUPPORTED replies are enabled here,
with a 500-character ceiling. Outbound is feature-flagged, rate-limited and rechecked before
fake delivery; its receipt is idempotent by outbox ID. No proactive messaging is implemented.
Production delivery cannot inherit an unproven exactly-once claim from the deterministic fake.
Three transient executions maximum, 60/120-second backoff and visible terminal failures.

Clear transient encrypted recipients/code hashes on completion or expiry. Minimized inbound/
outbound transport receipts expire after 30 days; do not retain raw webhook bodies. Expired
codes are unusable even if cleanup is delayed. Unlinked records clear the encrypted identifier immediately and expire after 30 days,
following expiry of their transport receipts. STOPPED links remain bound account data under
the active-account retention baseline. Unreferenced sender ordering barriers expire after
30 days; ingress rejects events older than that horizon. Owned export projection and
deletion-impact inventory must include the new records before this slice is accepted. Existing record holds must not be represented as universal channel hold coverage.

## Boundary and verification

This slice implements linking/intake/opt-out, not five-question practice or grading. The next
slice must reuse the shared assessment/mastery services and complete FR-WA-002/003/005.
Verify signatures before parsing, streaming/body limits, current consent and minor gates,
code expiry/reuse, actor/sender conflicts, concurrent processing, replay/order barriers,
STOP/unlink/withdrawal before outbound, safe logs, rate limits, rollback, retention and owned
export/status access. Use clean migrations, generated contracts and fake-only browser/worker
journeys. Rollback disables ingress, code issue and workers while preserving link/evidence rows.
