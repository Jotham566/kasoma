# ADR-051: Blinded expert review and release-unit audit coverage

Date: 18 October 2026
Status: Accepted for disabled synthetic engineering; actual scoring remains gated
Requirements: FR-GRD-003/004/005, FR-ID-003/006, NFR-SEC-002

## Context

Production-pilot decision 16 requires independent blinded audit of at least ten percent
of automatically returned short-text grades and sticky disablement below 90% rolling
exact agreement or on any critical error. Publication storage currently assigns audits
at global ordinals 1, 11, 21. Internal diagnostic grades can remain sealed permanently;
their global sample does not guarantee coverage of the subset actually made available.
Completed expert review, blinded access and runtime rolling state are unimplemented.

## Proposed decision

Keep immutable global ordinals and their existing sample. For new model publications,
also sample ordinal 1 and each tenth subsequent publication within its session/band.
Persist the new audit-policy version and session ordinal; do not rewrite old evidence.
Counters permit additional assignments while preserving the global minimum and
assigned <= published bound. Objective storage fixtures retain their existing policy.

This covers revision publication prefixes and whole completed diagnostic release units,
including interleaved abandoned diagnostics. It may require more than ten percent
review, particularly short sessions; it does not claim random representativeness.
The academic lead must approve the versioned sampling/window policy before actual beta.

Expert task projection omits learner identity, model results, ordinals and previous
reviews. Require current academic-reviewer authorization independent of the learner
and item author. Validate the complete pinned rubric point set and closed critical-error
classification. Store one immutable completed expert review per assignment with exact
reviewer/request provenance; determine agreement from stored criterion points, never a
reviewer's declaration that the model was correct. Duplicate same-input completion is
idempotent and conflicting completion fails safely. No grade override is implied.

Before confidential projection or completion, lock reviewer and learner accounts in
stable UUID order and recheck current authentication/roles/consent. Role revocation
already uses the reviewer account lock. Take the band lock afterwards, matching worker
ordering; do not grant role-table write privileges merely to obtain row locks.

Complete reviews and any disablement under the same refreshed exclusive band lock used
by publication. Order the latest 100 completed reviews deterministically; pending
assignments do not count as completed. Preserve aggregate completion counts through
future permitted retention, and recheck current audit state before dispatch/publication.
Later good outcomes never re-enable a disabled band.

Completion uses the earlier of the current domain clock and PostgreSQL clock_timestamp()
under the existing band lock. This preserves frozen test clocks and the SQL nonfuture
constraint while tolerating a host clock slightly ahead of Docker. It does not weaken
authorization, assignment/band/prior-completion lower bounds or the database guard.

New review records require minimized owned export, sealed diagnostic handling,
deletion-impact inventory, exact-record holds, restricted-role verification and
populated logical recovery. Keep answers in their original encrypted record. No new
indefinite retention, destructive transform or real learner processing is authorized.

## Acceptance and alternatives

Verify independence/IDOR, blinded output, complete integer rubric points, exact agreement,
critical and below-threshold disablement, deterministic window bounds, duplicate and
concurrent completion, publication races, rollback, sampling under interleaved sealed
diagnostics, privacy/hold coverage and the complete learner/browser regression.

Counting pending assignments as correct hides missing evidence. Sampling only persisted
global ordinals fails the release-subset case. Rewriting old ordinals destroys immutable
evidence. These alternatives are rejected. Keeping the normal application disabled is
mandatory until the complete integration and genuine external approval gates pass.

Sources: [readiness assessment](../../implementation/E4_EXPERT_REVIEW_READINESS.md),
[ADR-050](050-short-text-pending-and-eligibility.md),
[AI controls](../../specifications/06_AI_RAG_and_Grading_Guardrails.md),
[production rules](../../specifications/16_Production_Pilot_Decisions.md).


## Verified acceptance and follow-up

Source `2164209` passes complete hosted run
[39150319607](https://github.com/Jotham566/kasoma/actions/runs/39150319607) and is on
main. A later native run exposed host/VM completion-clock skew; the database-time cap
and ahead-clock regression above are a follow-up under verification, without relaxing
SQL guards. Genuine academic/sampling/provider/production approvals remain missing.


## Completion-clock follow-up accepted

The later database-clock completion cap passes complete hosted
[39155326659](https://github.com/Jotham566/kasoma/actions/runs/39155326659) at
`a357222`, which is on main. This supersedes the pending-follow-up status above;
SQL guards and the disabled synthetic/real-approval boundary remain unchanged.
