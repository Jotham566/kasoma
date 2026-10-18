# Channel preservation and retention readiness

Reviewed 9 October 2026. Requirements: FR-ID-006, FR-WA-006, FR-OPS-003,
NFR-SEC-002 and BR-010. This is a source inspection and implementation dependency
assessment, not a preservation decision or permission to process real data.

## Existing authority

Follow [privacy and retention](../specifications/09_Security_Privacy_and_Safeguarding.md),
[ADR-030](../decisions/ADR/030-record-legal-holds.md),
[ADR-043](../decisions/ADR/043-learning-record-holds.md),
[ADR-045](../decisions/ADR/045-accountability-record-holds.md) and the
[release gates](RELEASE_GATES.md). Existing finite, independently authorized,
recent-OTP administrator holds remain exact-record controls. They are not blanket
account preservation or deletion clearance. The deletion preview must continue to
report incomplete coverage and disabled execution.

## Observed implementation and consequences

| Record/path | Current behavior | Constraint on the next implementation |
| --- | --- | --- |
| `inbound_messages` | Actor can be unknown at intake and is resolved during processing. Terminal state clears sender ciphertext, link-code hash and reply ciphertext. Migration 0018 requires sender/code clearing; conversation changes add reply minimization. | Do not attribute an unbound sender to an account using a guessed association. A whole-row freeze cannot safely block processing or expiry. Never recreate already cleared payloads. |
| `outbound_messages` | Leaving PENDING clears recipient ciphertext. STOP, unlink and 24-hour expiry cancel pending messages. Delivery status may advance after sending. | Preservation must not authorize transmission, prevent opt-out or keep an operational recipient address usable. Test callbacks and cancellation while evidence is preserved. |
| `channel_links` | One row per user; an unlinked row may later represent a new sender/revision. UNLINKED requires a cleared external identifier. | A hold must identify the historical evidence/revision it preserves rather than silently following a new linkage or preventing unlinking. |
| `conversation_states` | Session continuation is mutable, expires after 24 hours and is removed on unlink/STOP paths. | A preservation mechanism must not reactivate a conversation or interfere with answer binding and expiry. |
| `link_codes` | One-time material expires, is consumed/revoked and is cleared/deleted in bounded batches. | Never preserve a usable authentication capability as an operational exception. Any accountability evidence needs an explicit minimized definition. |
| Sender and mutation receipts | Sender key is a hash; receipts have composite actor/key identity. Unbound sender history is intentionally absent from owned deletion inventory. | Do not invent a UUID target or broaden a learner's ownership based on a shared sender hash. |
| `whatsapp_retention.expire` | Bounded cleanup runs under the channel lock: 24-hour transient expiry, then 30-day terminal message/link cleanup with dependency checks. | Legal preservation must be consulted without letting one held row starve unrelated expiry, extend transmission lifetime or deadlock account/channel operations. |

Source paths inspected: `services/domain/messaging.py`, `services/whatsapp_processing.py`,
`services/whatsapp_intake.py`, `services/whatsapp_linking.py`,
`services/whatsapp_retention.py`, `services/legal_holds.py`,
`services/deletion_preview.py` and migration `0018_whatsapp_linking.py`.

## Required design before code

A new ADR must distinguish preserved evidence from mutable operational state, define the
exact record/revision and ownership at preservation time, and specify which minimized
fields can be retained and for how long. Compare a separate encrypted preservation
snapshot with versioned immutable channel evidence; neither is accepted by this document.
Existing raw-message disposal and STOP/unlink guarantees must remain effective. Do not
silently replace ADR-030's record guards with a different preservation meaning.

The ADR must specify atomic capture, authorization, lock order, idempotency, expiry/release,
retention after a preservation decision ends, export/disclosure boundaries and recovery.
No unbounded copies, indefinite metadata, public download, automatic legal determination
or hidden production enablement. The ordinary user export must not disclose internal
investigation material merely because a preservation record exists.

## Acceptance required for a complete slice

- Independent recent-OTP administrator claimant and exact requester ownership; cross-owner,
  missing, unbound and ambiguous/relinked targets fail closed.
- Exact decision/body/key replay and finite expiry/release; no credential or record body in logs.
- STOP, unlink, withdrawal and code expiry remain effective while preservation is active.
- No preserved artifact can be reused to send a message, authenticate or resume a session.
- Race tests for processing/cancellation/callbacks/relinking and preservation capture; approved
  account-before-channel lock ordering must not deadlock.
- Held evidence survives bounded ordinary cleanup, while unrelated records still expire.
- Release/expiry follows the approved underlying retention policy rather than granting arbitrary
  deletion or retaining duplicates indefinitely.
- Owned inventory, safe export, strict generated contracts, operator UI, audit and alerts reflect
  the new evidence without claiming complete deletion readiness.
- Additive clean/upgrade migration, populated restore and regression across existing holds and
  five-question channel journeys. No destructive migration without its separately required approval.

Pending full coverage also includes other personal-data logs, embedded references and backups.
This channel assessment does not close those gaps or enable the account-erasure processor.


## Pre-erasure clock review

Terminal receipt DELETE/cleanup uses database wall clock under ADR-055. Legacy
held-record guards still use transaction-start time; review long-transaction boundaries
before enabling any future erasure processor. Existing append-only protections remain,
account erasure is disabled and this terminal subset does not claim universal clearance.
