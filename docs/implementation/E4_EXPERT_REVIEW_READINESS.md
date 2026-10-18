# Independent grading review readiness

Historical readiness assessment before implementation. The slice is now merged after
hosted verification; see [current evidence](E4_EXPERT_REVIEW_VERIFICATION.md). Present-tense inventory below
records the assessment baseline and does not override CURRENT_SPRINT.md or acceptance.

18 October 2026. Requirements: FR-GRD-003/004/005, FR-ID-003/006, NFR-SEC-002.
Current learner-flow candidate: `853f80a`; hosted run
[39143803289](https://github.com/Jotham566/kasoma/actions/runs/39143803289).
The hosted run passes and `853f80a` is promoted to main. No actual learner scoring is enabled.

The next complete slice must let an independently authorized academic reviewer inspect
the pinned synthetic answer/rubric without learner identity, model points/confidence/
feedback, sampling ordinal, prior audit outcomes or band identifiers. Submission must
validate every rubric criterion, preserve immutable reviewer provenance and calculate
exact agreement server-side. Review never rewrites the original grade or mastery.

Current code stores publications and audit assignments only. The processor correctly
uses zero completed audits rather than treating pending assignments as correct. It
cannot yet read completed reviews or enforce automatic rolling disablement. Existing
band locks and sticky disablement are the transaction boundary to reuse. Reviewer role
alone is not evidence of real academic qualification; production qualification and
approval remain external gates.

New personal records need owned minimized exports with diagnostic sealing, inventory,
exact-record holds, restricted-login tests and populated recovery before runtime wiring.
Keep answer text solely in its existing encrypted attempt and derive review projections
after current authorization. Staff identities, request keys and comparison internals
must not appear in learner projections or operational logs.

## Sampling edge case to resolve in this slice

The current global publication counter includes internal grades from sealed diagnostics.
An abandoned diagnostic may never release those grades. If it consumes a sampled global
ordinal, the following revision grades can be available without a sampled grade among
that released subset. A ten-percent global persisted-grade sample alone therefore does
not prove ten-percent coverage of actually released learner grades. This is an
implementation gap before enablement, not permission to lower the requirement.

Propose retaining existing immutable global ordinals and their sample, while additionally
sampling the first and every tenth automatic publication within each session/band. A
revision exposes publication prefixes; a diagnostic exposes its whole completed result
or none. Sampling both boundaries preserves coverage of those release units. Record a
new audit-policy version, relax exact sample-count equality only to allow additional
audits, and never rewrite prior publications. Verify interleaved abandoned diagnostics,
multiple sessions/bands, neutral outcomes, concurrency and counter rollback.

## Implementation sequence and acceptance

1. Record [ADR-051](../decisions/ADR/051-blinded-review-and-release-unit-sampling.md)
   and strict blinded-task/review contracts; preserve fail-closed runtime defaults.
2. Add review persistence, exact points/independence checks, completion order and a
   band-locked rolling window. Any critical error or exact agreement below 90% must
   persist sticky disablement in the same transaction.
3. Add owned export, inventory and exact holds before staff/runtime disclosure.
4. Add bounded independent staff review API/UI, current consent and role checks,
   immutable idempotent completion and safe conflict handling.
   Use the existing Kasoma visual system with clear queue/task/form hierarchy,
   responsive cards, accessible typography, generous spacing and touch targets,
   and explicit saving/empty/error states. Inspect desktop/mobile captures; visual
   appeal does not replace blinded-data, accessibility or browser acceptance.
5. Recheck actual audit state before every model pass and grade publication; verify
   review/publication races, fallback without score/mastery and all existing journeys.
6. Run clean/upgrade migration, role, populated recovery, complete backend/browser,
   generated-contract, security and container checks. Academic calibration, real safety
   detectors/providers and production approval remain separate gates.

No schema or application change is made by this readiness document.
