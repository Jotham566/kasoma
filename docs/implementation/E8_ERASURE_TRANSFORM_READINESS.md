# Account erasure transform — readiness assessment

Status: assessment only. No execution, transform, migration or new approval.
Requirements: FR-ID-006, BR-010, FR-OPS-003, NFR-SEC-002 and NFR-MNT-001.
This records the next substantive privacy implementation boundary after the current
[load-tool lifecycle](E9_LOAD_ROLE_CLEANUP_VERIFICATION.md) is verified and published.

## Observed implementation

The [deletion preview](../../services/deletion_preview.py) requires the independent,
recently authenticated ADMIN claimant of a pending DELETE request. It returns bounded
relational counts in nine retention/review categories. It always reports
execution_enabled=false and includes LEGAL_HOLD_COVERAGE_INCOMPLETE,
ERASURE_PROCESSOR_UNAVAILABLE and ANONYMIZATION_REVIEW_REQUIRED. Active holds and staff
provenance can add further blockers. Zero counts do not clear these requirements.

[Identity migration0002](../../apps/api/migrations/versions/0002_identity.py) permits
ACTIVE/DISABLED users. The current [request contract](../../services/data_request_contracts.py)
exposes QUEUED/IN_REVIEW/COMPLETED, with no erasure execution contract. The
[hold contract](../../services/legal_hold_contracts.py) supports19 exact target kinds;
that count is not proof of coverage over every source in the preview or embedded
references. Existing SQL immutability and ownership constraints remain authoritative.

[ADR-029](../decisions/ADR/029-deletion-impact-preview.md) requires deletion execution
state, an exact reviewed transform and recovery plan before destruction. It explicitly
rejects treating changed user IDs as evidence of anonymity.
[ADR-030](../decisions/ADR/030-record-legal-holds.md) preserves existing immutable guards;
a hold's expiry is not permission to erase or anonymize the original record.
[ADR-057](../decisions/ADR/057-minimized-channel-preservation-proposal.md) authorizes only
its minimized exact channel snapshots, excluding contacts, codes and message bodies.
[ADR-060](../decisions/ADR/060-completed-export-accountability-retirement-proposal.md)
explicitly excludes account erasure and pending DELETE completion. Its four-table
EXPORT capability cannot be reused as general deletion authority.

## Verified relational dependency boundary

A schema-only inspection of the healthy local public0042 schema finds39 direct
foreign keys from36 tables to users, all with PostgreSQL NO ACTION deletion behavior.
No learner rows, payloads or credentials are selected. This is a direct-reference
observation, not a complete graph or embedded-reference/hold clearance.

In particular, consent_records.user_id and data_subject_requests.user_id retain
references to users, alongside request-review actors, legal-hold actors, author/reviewer
provenance and learning records. Removing login identifiers alone cannot reconcile
these references; blindly deleting the user would conflict with both foreign keys and
lawfully retained evidence. The exact proposal must resolve how minimized retained
subject references and staff provenance survive until their approved deadlines.
This assessment chooses neither a retained user stub nor rewritten subject links,
and does not label either approach anonymous.

## Full schema and shared academic state inspection

Schema metadata at main `ebbf00c`/0042 contains 69 tables, 488 columns, 120 foreign keys
and 97 non-internal triggers. The inventory selects catalog structure and migration
metadata only, not learner rows. The [versioned source inventory](E8_ERASURE_SOURCE_INVENTORY.md) records every column,
foreign-key definition, CHECK name and non-internal trigger name/function. A second
read-only catalog inspection matches the original snapshot field-for-field. This is
not a reviewed erasure manifest or permission to mutate any of those sources.

The [publication counter guards](../../apps/api/migrations/versions/0030_grading_audit_assignments.py)
prohibit resetting lifetime publication/audit counts. The
[expert review guards](../../apps/api/migrations/versions/0033_expert_grading_reviews.py)
use immutable completion ordinals and the latest 100 completed expert reviews per band
for sticky below 90%-agreement/critical-error disablement. Those are shared academic
controls, not disposable per-learner projections. Erasing a learner's review rows could
change a subsequent rolling window even if foreign-key deletion were permitted.

The proposal must therefore resolve deletion's effect on shared calibration authority:
retain the approved monotonic counters, preserve or explicitly fail closed on affected
quality authority, and never silently improve an active band's agreement by removing
reviews. A new source-unlinked projection would itself need a defined field/retention
policy and re-identification review; it cannot simply be called anonymous. No option,
new retained dataset, counter reset or grading-policy change is chosen here.

This adds FR-GRD-003/004/005 to the affected requirements for the forthcoming proposal,
under [ADR-051](../decisions/ADR/051-blinded-review-and-release-unit-sampling.md).
It does not authorize deletion of the original learner, grade or review records.

## Verified authorization and ownership gaps

The [hold service](../../services/legal_holds.py) requires a pending DELETE case and
its original independent ADMIN claimant. Its access check rejects completed requests
with REQUEST_COMPLETED. Therefore existing lawful post-closure retention cannot simply
reuse a completed case for new preservation decisions or release operations. The
proposal must resolve custody before enabling DELETE completion; it must not silently
extend ADMIN permissions, reassign the original claim or fabricate another completion
clock. Current holds require a finite future expiry, not a fixed approved maximum term.

The [preview inventory](../../services/deletion_preview.py) deliberately counts both
owned flag histories/receipts and staff actor links, with overlap. A learner's original
report can therefore also appear in STAFF_PROVENANCE_REVIEW. That category alone cannot
establish staff activity or justify excluding the entire account from fulfillment.
Conversely a real author/reviewer/ADMIN relationship must not be treated as ownership
of the other learners' records it touches.

The same preview includes unbound OTP challenges by a matching identifier hash.
The actual otp_challenges schema has no created_at field. A future transform cannot
infer creation time, historical ownership or safe deletion from that advisory match;
OTP expiry and bound user ownership need separate treatment. Shared channel sender
barriers similarly need provenance, not an opaque-hash match alone.

No new policy or authority is inferred from these gaps. They constrain the exact
execution proposal and its negative/race tests; they do not justify weakening controls.

## Required assessment before an execution proposal

| Boundary | Exact evidence needed |
| --- | --- |
| Owned learning and identity records | Table/column/FK/trigger inventory, explicit per-record REMOVE/RETAIN/TRANSFORM rule, ownership predicate and dependency order; no blanket cascade or guard bypass |
| Legally retained material | Preserve approved consent/material-audit, resolved-flag and request-accountability schedules; do not invent closure, resolution or request-completion dates |
| Preservation | Map each proposed affected source to its applicable exact hold/snapshot and independent SQL check, including ownership/hold/worker races; document remaining uncovered sources |
| Immediate processing stop | Define the authorized point for session revocation, consent/assent processing barriers and channel cancellation without freezing usable credentials or overriding STOP/unlink |
| Anonymity | Review the exact retained fields, free-text/encrypted bodies, timestamps and embedded references; a different UUID or deleted encryption key alone proves no anonymous aggregate |
| Staff provenance | Separate learner-owned information from author/reviewer/support/ADMIN records concerning other people; no automatic actor reassignment or shared-content deletion |
| Execution lifecycle | Design explicit authorization, durable stages, finite batches, replay/crash recovery, completion conditions and independent restricted database authority within a proposed bounded synthetic lane |
| Copies and external retention | Account for existing export copies, unbound sender history, shared buckets, operational logs and backups; do not claim relational cleanup proves their erasure or introduce production providers before the Week8 decision |

The next concrete deliverable is an exact transform/preservation/recovery ADR proposal
based on this source inventory, with clearly separated unresolved policy decisions.
Do not implement irreversible transforms merely to make the preview's blockers disappear.
The human must approve the concrete affected data and preservation boundary under the
[operating contract](../specifications/12_Coding_LLM_Operating_Contract.md) and
[release gates](RELEASE_GATES.md) before destructive implementation. The previous bounded
synthetic approvals cannot be extended silently. Production privacy/legal approval,
academic/provider authority and pilot sign-off remain separate gates.

This assessment chooses no new status, retained aggregate, retention period, provider,
public API or architecture. It does not narrow the full FR-ID-006/BR-010 obligation to
the currently working export or preview journeys.
