# ADR-023: Unseen equivalent reassessment

Date: 28 September 2026
Status: Accepted within delegated implementation discretion
Requirements: FR-GRD-008, FR-REV-003/005, FR-MST-001/003, FR-CNT-001/004, FR-ID-003, FR-OPS-001

## Context and decision

Use the specified REASSESSMENT session kind with exactly one item, linked immutably
to an owned submitted REVISION attempt. The original deterministic feedback includes
remediation; the learner explicitly requests reassessment from that feedback. Do not
claim the learner read or understood it. Diagnostics and reassessment chains cannot
start this flow. One reassessment per original attempt supports different-key retries
and cross-device resume, including completed/expired results, without farming repeats.

Optional versioned `equivalents` claims contain a target version ID and reviewed
confidence. Claims undergo the existing independent publication workflow; reviewers
cannot author either side. Both versions must share primary concept/competency and
difficulty, and pass duplicate exclusion. Claims are directional metadata but selection
recognizes either direction and pins the claim-bearing version and approval evidence.
No mutation of existing published versions or automatic equivalence claims.

Prefer a reviewed EQUIVALENT claim, then same primary concept/competency and difficulty
as allowed by specification 05. Primary competency is highest mapping weight, then
stable competency ID. Require current approved synthetic S4 web content. Exclude the
same stable item, every previously served stable item across all time, active plan
reservations and near-duplicates of previously served prompts. No shortage fallback
to a repeated or less constrained item. Return REASSESSMENT_UNAVAILABLE without writes.

Version `reassessment-v1` uses Unicode-normalized lowercase word tokens, numeric-value
masking, sequence similarity >=0.85 or token Jaccard >=0.80 as conservative duplicate
rejection. These deterministic text-only software safeguards do not certify semantic
transfer; independent academic review and the frozen benchmark remain release gates.
Rank reviewed claims first, then stable version ID. Freeze eligible candidate summaries,
content hashes, relationship provenance, versioned configuration and selected ID/hash
for read-only replay. Retain elapsed seconds from original submission to selection;
completion time remains on the session/attempt for later outcome analysis.

Reuse the shared question player, grading, evidence and consent transaction. Independent
reassessment hides hints before submission (the existing hint service allows REVISION
only); worked solutions remain gated by submission. No score rewrites or claims of
misconception resolution: approved misconception tags and calibrated criterion thresholds
are not yet available. Display the new result as separate evidence, with a return link
to the original revision. Preserve manual 5–10-item session bounds.

## Security, API and migration

Add POST/GET /attempts/{attempt_id}/reassessment for start/resume. POST requires an
idempotency key. GET returns an existing linked session only. Existing session routes
serve, answer, abandon and resume it; active-session discovery includes reassessment.
Safe learner metadata contains original attempt/session linkage, never relationship
confidence, answer pattern or candidate internals. Current consent/subject/ownership
and content approval apply at every relevant read/write; retired content is never served.

Migration 0010 widens the session-kind constraint without rewriting history and adds
an append-only binding with ownership/version guards and one-item assignment checks.
Scope the existing active-topic uniqueness to REVISION so a child reassessment can
coexist with its parent. Transactional reassessment.started/completed events reuse
safe IDs; no raw answers, prompts or contacts in logs. Keep evidence on rollback and
use forward fixes. No providers, generated questions, grading calibration, portals
or mature-product scope are added.

## Verification

Test explicit preference/fallback, primary-skill/difficulty matching, text/value clones,
all-time unseen identities, reservations, shortage, publication/review controls,
concurrent/idempotent starts and answers, expiry, consent/IDOR, retirement, atomic
rollback, immutable bindings, legacy migrations, replay and browser retry/resume/axe.
