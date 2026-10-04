# ADR-037: Channel-safe shared assessment operations

Date: 4 October 2026
Status: Accepted within delegated MVP implementation discretion; base implementation verified; follow-up delivery work in progress
Requirements: FR-WA-002/003/004, FR-CNT-004, FR-GRD-001/002, FR-MST-001

## Decision

Add a trusted internal channel argument to the shared assessment transaction methods. Public
HTTP contracts and wrappers remain WEB-only. Channel workers must authenticate and bind the
linked actor before invoking these methods; the argument is not an authentication mechanism.
Keep WEB receipt fingerprints unchanged; namespace WHATSAPP fingerprints to prevent an operation
from replaying a receipt with different provenance.

WHATSAPP start accepts explicitly selected topic practice of exactly five items. Apply approved
version eligibility, repetition exclusions and ADR-036 capability checks before selection. An
existing five-item revision session can continue across channels only if every assigned version
is currently approved and channel-suitable. Do not silently replace assignments, start a second
active plan or shorten an unsuitable plan. Diagnostics, reassessments and recommended-plan starts
remain web operations. Recheck suitability before serving or accepting an answer on either channel. A WHATSAPP-only
version must not become WEB-eligible merely because its session is shared. Owned post-grade
results remain accessible through the existing protected web results/solution flow.

Migration 0019 permits immutable attempts with WEB or WHATSAPP provenance and adds a database
insert guard for five-item revision assignments explicitly marked WHATSAPP-suitable. Existing
attempt immutability, assignment ownership, approval and response-format guards remain intact;
no historical evidence is rewritten. Both paths use the same grader and mastery reconciliation.

## Verification and boundary

Test five-item web/channel score and mastery-evidence parity using independently reviewed synthetic
versions and equivalent consented actors. Test cross-channel receipt conflicts, unsupported content,
non-five-item plans, retired versions and direct database provenance guards. Exercise clean migrations
and existing web regressions. This dependency does not enable webhook-driven learning; conversation
state, exact reply binding, delivery, STOP/session integration and end-to-end parity remain pending.
