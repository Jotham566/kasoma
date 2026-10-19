# Proposed erasure disposition manifest — ADR-061

Status: Proposed; no migration, executable manifest or execution authority.
Requirements: FR-ID-006, BR-010, FR-OPS-003, FR-GRD-003/004/005,
NFR-SEC-002 and NFR-MNT-001.
This is part of [ADR-061](../decisions/ADR/061-synthetic-account-erasure-proposal.md),
not an extension of the approvals for ADR-057 or ADR-060.

## Closed source baseline and action semantics

The baseline is public0042 at main `ebbf00c`; [the factual inventory](E8_ERASURE_SOURCE_INVENTORY.md)
provides every current column/type, FK and guard name. A separate read-only pg_constraint
query confirms all 69 primary keys below. No learner rows are inspected. Every source
below is covered by a proposed disposition; this does not mean every source is removable.
Any unknown table/column/key/payload version or inconsistent ownership blocks automatic
execution until assessed in a versioned manifest. The future executable policy must
validate schema/contract versions independently, not treat this Markdown as SQL input.

All-column actions refer to the exact column lists in the inventory, including nested
current-version JSON/ciphertext. No names are assumed to prove that a JSON value is
anonymous or independent of another person. Unsupported embedded/third-party content
is a blocker, never silently truncated or assigned to the learner by an FK alone.

| Code | Exact proposed row/field disposition and exception |
| --- | --- |
| K | Keep every column; no learner erasure of shared state. Only the explicit affected-band disablement in ADR-061 changes shared bands/history. No counter reset/decrement. |
| S | Keep every column and block automatic execution before closure for genuine subject staff provenance. Do not reassign actors, remove shared content or claim staff fulfillment. Overlapping original learner flag evidence is evaluated under F instead. |
| U | Set status=DISABLED at barrier and persist immutable database closed_at. Once preservation is established, set display_name=NULL and birth_date=NULL. Keep only id/status/created_at/closed_at while necessary lawful references exist; remove entire row after all such references/dependencies retire. This is personal linkage, not anonymous. |
| C | Revoke sessions/link codes at barrier; physically remove every owned row/column in bounded batches. No preservation of access_hash, refresh_hash, family, code_hash, link-code key or encrypted OTP contact/capability. Bound challenge ownership only; see T and the identifier-drain rule for unbound challenges. |
| I | Remove whole owned rows after any authorized exact non-capability snapshot. Login identifiers additionally wait for ADR-061's bounded pre-barrier OTP drain; never release a lookup while an old unbound challenge can register anew. A structurally required channel_link may retain id/user_id/sender_hash/revision/status/linked_at/opted_out_at/updated_at with external_identifier_encrypted=NULL and status STOPPED/UNLINKED as required by current state semantics; never retain a usable dispatch address. Delete this minimal ancestor when its last exact lawful dependency ends. |
| L | Delete every owned row/column unless an exact original hold or necessary approved-retention dependency requires it. Retain original held rows unmodified. Mutable projections use an exact encrypted snapshot before removal, not an operational freeze. No replacement learning aggregate. |
| M | Apply cancellation/privacy barriers immediately, then remove whole owned rows after exact preservation. Existing original terminal receipt holds keep only their already-minimized original receipt and required structural parents; new live evidence uses the explicit snapshot fields below. Never hold usable dispatch/resume capability. |
| R | Retain original consent evidence under the existing six-year closure/withdrawal anchor and exact holds; then remove whole row. No new contact collection or reset of historical consent times. |
| A | Keep only current original accountability schema under its existing classified deadline and exact holds, then remove whole row in dependency order. Request deadline is completion plus six calendar years; material audit uses closure/withdrawal; security audit uses 12 months. Do not invent a completion or classify unknown audit actions by convenience. ADR-060 still exclusively governs completed EXPORT rows. |
| F | Retain original flag, history and receipts until resolution plus 24 calendar months and applicable exact holds; then delete whole rows and now-unneeded context ancestors. Unresolved flags remain visibly pending; no fabricated resolution or changed staff provenance. |
| X | Drain the existing export/object cleanup lifecycle before closure; never remove a locator while retryable object cleanup is outstanding. This proposal does not shorten existing 24-hour access or declare a failed job fulfilled. |
| B | Keep encrypted body only while at least one exact active preservation decision covers it. Delete whole body after last release/expiry; metadata follows A, independently of original-source lifetime. |
| T | Do not derive account ownership from opaque hashes. Apply existing bounded global expiry independently: rate buckets at expires_at, sender barriers only under existing 30-day unreferenced-source conditions. Never delete a still-needed STOP/anti-abuse barrier or another learner's state. Unbound OTP challenges keep existing at-most-ten-minute verification expiry; a hash match alone grants no account-erasure ownership. |

## All69 table dispositions and actual primary keys

Subject means the server-derived verified request owner. All joins require consistent
ownership at every link; a cross-owner reference fails closed. Row actions are evaluated
under source/hold/worker locks, not copied from the advisory preview's capped counts.

| Table | Actual primary key | Action | Ownership / boundary |
| --- | --- | --- | --- |
| `alembic_version` | `version_num` | K | Shared control; no subject ownership |
| `assessment_grading_history` | `id` | L | attempt_id -> owned assessment_grading_work -> owned attempts |
| `assessment_grading_work` | `attempt_id` | L | attempt_id -> owned attempts |
| `assessment_outbox_events` | `id` | L | session_id -> owned assessment_sessions |
| `assessment_receipts` | `learner_id, key` | L | learner_id = subject |
| `assessment_sessions` | `id` | L | learner_id = subject |
| `attempts` | `id` | L | learner_id = subject |
| `audit_log` | `id` | A | Explicit material-action classification and exact target/actor ownership graph; unknown classification blocks |
| `auth_sessions` | `id` | C | user_id = subject only; unbound challenges use T rule |
| `channel_links` | `id` | I | user_id = subject |
| `channel_mutation_receipts` | `actor_id, key` | M | actor_id = subject, plus exact link revision/session ownership checks |
| `channel_preservation_bodies` | `snapshot_id` | B | snapshot_id -> owned channel_preservation_snapshots |
| `channel_preservation_disposals` | `snapshot_id` | A | snapshot_id -> owned channel_preservation_snapshots |
| `channel_preservation_snapshots` | `id` | A | request_id -> owned DELETE case; staff actor-on-other-case is S |
| `channel_senders` | `sender_hash` | T | Opaque shared key; no safe subject ownership from hash matching |
| `competencies` | `id` | K | Shared control; no subject ownership |
| `concepts` | `id` | K | Shared control; no subject ownership |
| `consent_records` | `id` | R | user_id = subject |
| `content_flag_history` | `id` | F | flag_id -> owned content_flags; initial own report is not staff activity |
| `content_flag_receipts` | `actor_id, key` | F | flag_id -> owned content_flags; initial own report is not staff activity |
| `content_flags` | `id` | F | reporter_id = subject; staff owner/triage-on-other-case is S |
| `content_import_jobs` | `id` | S | Subject staff role/author/reviewer/importer, or shared version dependency; review, not learner ownership |
| `content_mutation_receipts` | `actor_id, key` | S | Subject staff role/author/reviewer/importer, or shared version dependency; review, not learner ownership |
| `content_outbox_events` | `id` | S | Subject staff role/author/reviewer/importer, or shared version dependency; review, not learner ownership |
| `content_reviews` | `id` | S | Subject staff role/author/reviewer/importer, or shared version dependency; review, not learner ownership |
| `conversation_states` | `link_id` | M | actor_id = subject, plus exact link revision/session ownership checks |
| `data_exports` | `request_id` | X | request_id -> owned data_subject_requests |
| `data_request_receipts` | `actor_id, key` | A | request_id -> owned data_subject_requests; actor-on-other-case is S |
| `data_request_reviews` | `request_id` | A | request_id -> owned data_subject_requests; actor-on-other-case is S |
| `data_subject_requests` | `id` | A | user_id = subject |
| `export_retirement_state` | `singleton` | K | Shared control; no subject ownership |
| `grades` | `attempt_id` | L | attempt_id -> owned attempts |
| `grading_audit_assignments` | `id` | L | attempt_id -> owned grading_publications -> owned attempts |
| `grading_audit_reviews` | `id` | L | id -> owned grading_audit_assignments; reviewer-as-subject is S, not this predicate |
| `grading_band_history` | `id` | K | Shared control; no subject ownership |
| `grading_bands` | `id` | K | Shared control; no subject ownership |
| `grading_publication_counters` | `band_id` | K | Shared control; no subject ownership |
| `grading_publications` | `attempt_id` | L | attempt_id -> owned attempts |
| `grading_review_counters` | `band_id` | K | Shared control; no subject ownership |
| `hint_uses` | `id` | L | learner_id = subject |
| `identity_outbox_events` | `id` | L | user_id = subject; payload version must match current strict event schema |
| `identity_rate_buckets` | `key` | T | Opaque shared key; no safe subject ownership from hash matching |
| `inbound_messages` | `id` | M | actor_id = subject, plus exact link revision/session ownership checks |
| `item_mappings` | `item_version_id, competency_id` | S | Subject staff role/author/reviewer/importer, or shared version dependency; review, not learner ownership |
| `item_versions` | `id` | S | Subject staff role/author/reviewer/importer, or shared version dependency; review, not learner ownership |
| `items` | `id` | S | Subject staff role/author/reviewer/importer, or shared version dependency; review, not learner ownership |
| `learner_profiles` | `user_id` | I | user_id = subject |
| `learner_subjects` | `user_id, subject_id` | I | user_id = subject |
| `legal_hold_receipts` | `actor_id, key` | A | hold_id -> owned legal_holds; actor-on-other-case is S |
| `legal_holds` | `id` | A | request_id -> owned DELETE case; staff actor-on-other-case is S |
| `levels` | `id` | K | Shared control; no subject ownership |
| `link_codes` | `id` | C | user_id = subject only; unbound challenges use T rule |
| `mastery_estimate_history` | `id` | L | evidence_id -> owned mastery_evidence |
| `mastery_estimates` | `learner_id, concept_id, competency_id` | L | learner_id = subject |
| `mastery_evidence` | `id` | L | learner_id = subject |
| `otp_challenges` | `id` | C | user_id = subject only; unbound challenges use T rule |
| `outbound_messages` | `id` | M | actor_id = subject, plus exact link revision/session ownership checks |
| `personal_export_generations` | `id` | X | request_id -> owned data_subject_requests |
| `personal_export_jobs` | `request_id` | A | request_id -> owned data_subject_requests; actor-on-other-case is S |
| `reassessments` | `original_attempt_id` | L | original_attempt_id -> owned attempts, with owned session verified |
| `recommendation_snapshots` | `id` | L | learner_id = subject |
| `rubric_criteria` | `rubric_id, criterion_id` | S | Subject staff role/author/reviewer/importer, or shared version dependency; review, not learner ownership |
| `rubrics` | `id` | S | Subject staff role/author/reviewer/importer, or shared version dependency; review, not learner ownership |
| `session_items` | `id` | L | session_id -> owned assessment_sessions |
| `subjects` | `id` | K | Shared control; no subject ownership |
| `topics` | `id` | K | Shared control; no subject ownership |
| `user_identifiers` | `id` | I | user_id = subject |
| `user_roles` | `user_id, role` | S | Subject staff role/author/reviewer/importer, or shared version dependency; review, not learner ownership |
| `users` | `id` | U | id = subject |

## Exact preservation registry and encrypted allowlists

The registry allows exact subject-owned R/A/F originals under existing hold identities
where available and a new closed OWNED_SOURCE kind otherwise, plus exact immutable L rows. It adds exact
owned L sources not already covered by the 19 kinds, including sessions, session items,
receipts, hints, reassessments, recommendations and identity events. Existing original
hold meaning does not change. New source references for composite keys are opaque;
actor/key or learner/concept/competency components remain private and validated by a
fixed source-specific resolver, never caller-provided SQL. K/S/C/T/X are not new generic
hold targets. Missing/ambiguous excluded material is a visible preservation blocker.

Mutable U/I/L/M sources use only the following current-field allowlists, encrypted in
a separate preservation store. Binding/capture metadata holds case UUID, subject UUID,
source kind, opaque source reference, observed revision/version, snapshot UUID, capture
actor/time, decision and policy version. Original private key components remain in a restricted source-reference map for
independent SQL resolution; they never leave the resolver/API authorization boundary.
The encrypted binding repeats the opaque reference/version, not private retry keys.
Clear private key components after original-source resolution is no longer needed;
retained capture metadata never replaces a retired receipt-key ledger.
Neither hashes nor keys are exposed by ADMIN pages. Exact source versions must be
revalidated; source UUID alone is insufficient where mutation is possible.

| Source | Exact encrypted fields allowed | Mandatory exclusions |
| --- | --- | --- |
| users | id, status, display_name, birth_date, created_at; closed_at only if actually present in the implemented version | No credential or reconstructed historical profile |
| user_identifiers | id, user_id, type, normalized_value_encrypted, verified_at | lookup_hash; no authentication lookup consumer |
| learner_profiles | user_id, level_id | No other profile data inferred |
| learner_subjects | user_id, subject_id | No enrollment siblings |
| mastery_estimates | learner_id, concept_id, competency_id, snapshot | Only the exact current projection/version; no recomputed historical state |
| channel_links | id, user_id, sender_hash, external_identifier_encrypted, status, revision, linked_at, opted_out_at, updated_at | No link_codes, code material or resumable capability |
| conversation_states | link_id, actor_id, link_revision, session_id, expected_outbound_id, updated_at, expires_at, state_version | No authentication/resume consumer; references alone grant no access |
| inbound_messages | id, request_id, sender_hash, sender_encrypted, actor_id, command, status_reference, delivery_status, reply_reference, reply_encrypted, provider_at, received_at, available_at, processed_at, status, attempts, error_code | code_hash, message_hash, request_hash, raw provider webhook, signing material |
| outbound_messages | id, inbound_id, link_id, actor_id, recipient_hash, recipient_encrypted, template, provider_id, attempts, error_code, created_at, available_at, sent_at, status_at, link_revision, session_item_id, attempt_id, menu_topic_ids | No provider credential, send operation or generated plaintext body |
| channel_mutation_receipts | actor_id, created_at; opaque source reference binding identifies the exact receipt | key, request_hash in evidence payload; no indefinite retry-key replacement |

The U/I additions preserve existing profile/contact information **only after an exact
explicit preservation decision**. Together with the M contact/reply fields, they are
new personal-data preservation permissions requested by ADR-061, not previously granted
by ADR-057. Existing link/conversation minimized snapshot types remain available and
unchanged; an operator must explicitly choose the richer supported source and version.
Do not silently upgrade old decisions or preserve all revisions/accounts preemptively.

No plaintext payload-reading endpoint is proposed. A parsed learner reply may itself
contain arbitrary personal text or a user-entered secret; no sanitization guarantee
can be made. The capability must never unwrap it for logs, model calls, messaging,
analytics or UI. Encryption is not proof of anonymity or permission for real processing.

## Retained dependency closure and removal order

An exact retained root keeps the minimum referential and evidentiary ancestors required
by that root. The following closed dependency rules apply; do not recursively keep every
incoming child, the whole session or unrelated siblings:

- Retained grade/grading history/work/publication/audit/review or mastery evidence/history
  keeps its original attempt, the corresponding session item, session and disabled user
  reference as required. An assignment keeps its publication. A reassessment keeps its
  exact original attempt and reassessment session/item. Shared item/rubric versions remain K/S.
- Retained flag/history/receipt keeps the exact flag and its attempt, grade if present,
  corresponding session item/session and identity reference needed for the dispute.
  It does not retain every answer in that session or another learner's report.
- Retained original terminal outbound receipt keeps its inbound parent and only the
  link/session-item/attempt ancestors required by its actual FKs; retained links keep
  the sender barrier reference without a dispatch address. New encrypted live snapshots
  have no FK that forces the operational source/contact to stay alive.
- Retained case/review/receipt/hold/capture/job keeps only the necessary request, hold
  or snapshot metadata and user/actor references. A parent hold does not hold siblings
  or disposable exports. Preservation bodies follow exact active decisions, not A's
  six-year metadata period. Independent actors' references are not learner-owned data.
- A minimally retained session may clear diagnostic_result and recommendation_snapshot
  only if it is merely a structural ancestor, neither an exact held original nor needed
  as disputed evidence. Keep its other current fields until its last dependency ends.
  When that distinction is not proven, block the transformation; do not modify a hold.

Remove eligible leaves first, retaining blocked parents for later bounded passes.
Recheck precise dependencies each batch; expiry/release does not override another root's
longer lawful need. Newly discovered dependencies change eligibility, not policy.
The same rules govern due consent/flags/material audit and completed DELETE evidence
retirement. Remove the execution record and subject anchor last when all approved
accountability references are due and unheld. Do not retain erased source-ID lists.

## Exact audit classification proposed for this synthetic lane

This is an explicit classification choice requiring ADR-061 approval; the preview's
single category is not a legal classification engine. Preserve existing original fields
while their classified purpose applies. No wildcard-prefix acceptance or automatic
classification of newly added actions is permitted.

| Existing action codes | Proposed class / anchor |
| --- | --- |
| data_request.created, data_request.review_started, data_export.queued, data_export.completed | Material rights-workflow evidence; six years after that request's actual completion |
| legal_hold.created, legal_hold.released | Material preservation evidence; parent DELETE completion plus six years, with the exact active-decision custody exception in ADR-061 |
| data_request.queue_read, data_request.deletion_previewed, data_export.retrieved, legal_hold.queue_read, legal_hold.source_checked, legal_hold.export_sources_read | Confidential access/security audit; 12 months after created_at unless exact active investigation/hold |
| content.flag.created, content.flag.updated | Material support/triage evidence; closure/withdrawal plus six years, with its original flag context retained separately under F |
| content.flag.queue_read, content.flag.read, grading_review.queue_read, grading_review.read, grading_review.receipt_read | Confidential access/security audit; 12 months after created_at unless exact active investigation/hold |
| grading_review.completed | Material academic administrative evidence; closure/withdrawal plus six years; subject-as-staff is S and cannot be processed by this learner lane |
| content.created, content.edit, content.submit, content.review, content.retire; content_import.queued, content_import.completed, content_import.failed; staff.role.granted, staff.role.revoked | Material staff provenance; S blocks this automatic lane, rather than inventing staff closure or deleting shared content |
| data_request.export_retirement_batch, data_request.retirement_configuration | System security audit; 12 months after created_at under the existing ADR-060 classification boundary; not learner-owned rows |

An unrecognized action, missing lawful anchor, malformed deadline or unexplained actor/
target association blocks automatic classification-dependent removal and completion.
The new erasure authorization/closure/completion actions are material case evidence;
count-only worker batch/failure/configuration actions are 12-month security audit.
Implementation must fix their exact code enum and generated contracts before use.
Classifying a read as security audit does not delete an associated original request,
flag, review, hold or consent record before its separate obligation ends.

## Completion and uncovered environments

COMPLETED means all eligible subject operational/learning rows have been removed,
credentials and publication/dispatch barriers hold, and every remaining subject-linked
row has an exact classified lawful root/deadline or active specific preservation decision.
Verification must check the complete executable manifest without capped counts, not
merely observe an empty deletion queue. Do not report all personal data erased where
lawful exceptions remain. Case status explains completion subject to those obligations;
a pending/failed/unsupported case never gets a completion timestamp.

Known shared transient state is governed by T and disclosed as such; unbound or
third-party records are not silently attributed to the learner. An account with an
unresolved attribution/preservation/embedded-reference question remains BLOCKED.
Staff provenance and verified representative/closed-account support need subsequent
explicit policy and implementation; they remain gaps in the full MVP, not fulfillment
by rejection. Operational logs, external deliveries, production backup/checkpoint
handling, legal sufficiency and real-data/production release are separate outstanding
gates. The isolated synthetic recovery rehearsal cannot substitute for them.

## Proposal verification

The primary-key inventory and 69-table coverage assertion pass against the read-only
local 0042 catalog. `make check-docs` passes with 175 Markdown files/61 requirement IDs;
`make lint` passes, including Python/TypeScript formatting/type checks. These checks
verify proposal documentation only; no application acceptance, migration, destructive
execution, API/schema permission change or new retention behavior is claimed.

## Proposed0043 source extension — unapproved, ADR-067 candidate

The original69-table0042 baseline remains historical evidence. ADR-067 adds two shared
controls and13 columns, observed in the isolated0043 catalog described in the factual
inventory. A future closed manifest must cover71 tables and explicitly verify0043; a
0042-only executor must refuse the changed source. No executor is authorized here.

| Additional table | Actual primary key | Proposed action | Boundary |
| --- | --- | --- | --- |
| operations_configuration_versions | id | K | Global immutable numeric warning history; no learner/actor ownership |
| operations_configuration_state | id | K | Global current pointer and preserved namespace; no subject ownership |

Propose classifying exact action operations.configuration.changed as existing material
administrative staff evidence, closure/withdrawal plus six years and applicable exact
holds. It identifies the ADMIN actor and global configuration version; it must never be
removed merely because that staff member also has learner records. This exact addition
requires ADR-061 review/approval with the rest of the proposed classification; no wildcard
or inferred erasure, retention change or exception to staff provenance is authorized.
