# ADR-015: First content review vertical slice

Date: 23 September 2026
Status: Accepted within delegated implementation discretion
Owners: Engineering
Requirements: FR-CNT-001–005, FR-OPS-003, NFR-SEC-002, NFR-MNT-001

## Decision and scope

Implement ADR-006 with immutable published versions and independent review. This
first path supports text-only single-choice items: draft, edit, submit, return,
approve, retire and create a corrected new version. Import, other response formats,
media, equivalence authoring and learner flags remain their scheduled slices. This
is partial FR-CNT-001/004, not removal of the remaining MVP requirements.

Use normalized curriculum concept/competency and version mapping tables. Seed only
explicit synthetic concept/outcome references; they make no NCDC mapping claim.
Every local item is marked synthetic and excluded from production eligibility.
Local APPROVED status tests workflow mechanics, never academic release counts.

The API follows the specified mutation paths. Add GET /admin/items with UUID cursor
pagination, GET /admin/item-versions/{id}/reviews for decision history,
and GET /admin/content-context for authorized queue/editor metadata.
POST /admin/items accepts an optional source_version_id to create the next version
of the same item. Only its original author can edit or clone it in this slice.
No author reassignment endpoint exists. Request bodies reject role/author/status
injection. Admin retirement does not imply reviewer or author permission.

Edits and transitions require expected_revision and Idempotency-Key. Item-row locks
serialize versions; replay keys are scoped to actor and request digest. Replay
returns the same version's current state after authorization, never duplicates.
Versions freeze during review. Returned versions re-enter DRAFT with recorded
comments. High-risk/disputed work requires two distinct independent approvals;
reviewer escalation persists through corrections and copied versions. Every review
checks the fifteen approved checklist categories before approval. Self-review is
forbidden even for users holding both author and reviewer roles.

Validate curriculum membership, weights, rights evidence, single-choice answer,
worked solution and remediation at submit and again at approval. Missing publication
fields return safe field names with 409, without echoing their contents.

Append audit and a safe content outbox event in the same transaction. Database
triggers prohibit audit/review rewriting, version deletion, and changes to approved
payloads/mappings; retirement changes availability only. There are no learner content
read endpoints yet. The later assessment slice must pin versions and use the approved
content selector and shared consent authorization.

## Staff bootstrap and security

Persist roles separately from learner-controlled profiles. Staff grants/revocations
are local CLI operations over already verified example.invalid identities and are
audited. No email automatically grants roles; no public role-management route exists.
Every admin request authenticates and rechecks roles. Mutations require recent OTP.
Production remains disabled, including until staff MFA/role governance is implemented.
The existing same-origin cookie gateway forwards only explicitly listed staff routes.

## Alternatives and consequences

A generic JSON editor or full import pipeline would obscure the first review journey.
Start with labeled single-choice fields and a reviewer checklist. Normalized mapping
columns enable later selection; bounded prompt/answer structures remain versioned JSON.
No runtime package or infrastructure provider changes are needed.

## Migration, rollback and approval

Migration 0003 is additive after identity. Triggers are schema-local for isolated tests.
Test upgrades, repeated seeds, concurrent edits, role denial and direct SQL mutation
attempts. Roll back application code while retaining tables; destructive downgrade
requires a separate approved recovery plan. The user authorized this next vertical
slice and discretionary implementation choices; no accepted architectural or academic
policy is replaced. Academic reviewers still own real curriculum/answer truth.
