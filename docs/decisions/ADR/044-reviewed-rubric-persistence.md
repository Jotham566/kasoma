# ADR-044: Version-pinned reviewed rubrics with learner delivery disabled

Date: 4 October 2026
Status: Accepted within delegated implementation discretion
Requirements: FR-CNT-001/002/003/004, FR-GRD-003/004, NFR-SEC-002

Add SHORT_TEXT as a synthetic content-authoring/review format, without enabling learner assignment,
attempt submission, model grading or mastery. Reuse independent author/reviewer separation,
rights/curriculum checks, complete review checklist, second-review escalation, revision/idempotency
and immutable approved versions. Academic inventory/calibration/production approval remain gates.

An optional DraftDocument.rubric contains explicit unique criteria, point values, criterion text,
acceptable evidence, common errors and prohibited inferences. Short-text review requires a rubric
whose maxima sum to the item maximum, CRITERION_SUM partial-credit semantics and no objective
answer key. Other formats reject a rubric and preserve ALL_OR_NOTHING. Existing requests without
a rubric serialize exactly as before, preserving canonical hashes and idempotency receipts.

Migration 0023 adds normalized rubrics and rubric_criteria. A rubric's immutable ID is its owning
item-version UUID, making the one-to-one version pin explicit without independently mutable rubric
versions. The item version supplies the sequential version number and approval lifecycle. Criteria
use (rubric_id, criterion_id) keys and stable positions. Normalized rows are derived from the same
canonical authored document used by content hashing/reviews; SQL requires exact agreement before
review/approval. They can change only while the owning version is DRAFT. Approved edits require a
new item/rubric version. Existing rows are not rewritten.

Both service selectors and a database assignment guard reject SHORT_TEXT while learner integration
is unavailable. The author UI says review-only. Content approval alone never enables scoring; the
future eligibility/calibration decision must explicitly replace this disabled boundary and add a
pending/neutral learner path. Existing objective WEB/WhatsApp grading remains unchanged.

Rubric bodies are content-author/reviewer data, not learner-visible responses. Staff-provenance
inventory includes the new rows; learner exports keep their existing hidden-rubric exclusion.
No new model/provider call, retention deadline, real learner data or academic truth is introduced.
Synthetic fixture resource ceilings remain engineering limits, not academic eligibility approval.

Verify fresh/upgrade migrations, complete validation, exact normalized storage, independent review,
SQL immutability/projection checks, idempotent retries, version copying, excluded learner selection
and browser author/reviewer controls. Rollback disables short-text authoring routes/options while
retaining protected evidence, then uses a forward fix; no destructive downgrade is permitted.

After storing SHORT_TEXT documents, a binary predating this contract cannot parse those documents.
Do not roll back to a pre-rubric binary. Disable new authoring in a compatible forward fix while
preserving the schema, reviewed evidence and assignment guard.
