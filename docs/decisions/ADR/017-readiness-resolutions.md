# ADR-017: Resolve implementation readiness questions

Date: 23 September 2026
Status: Accepted within the owner's instruction to resolve pending implementation work
Owners: Engineering; academic and release sign-off remain with their named functions
Requirements: FR-MST-001/003/006, FR-GRD-003/004, release planning

## Context and decision

The owner requested resolution of pending items before the next implementation.
Resolve E3-01 without rewriting published content or changing grading semantics:
content difficulty FOUNDATIONAL maps to engine FOUNDATIONAL; STANDARD maps to CORE;
CHALLENGING maps to STRETCH. Name the mapping `content-difficulty-v1`. Preserve current
API values and immutable historical documents. E5 must record this mapping version
with the engine configuration when producing evidence. The weighting values stay
exactly as specification 05 defines; calibration and academic approval remain gates.
No mastery computation is implemented by this documentation decision.

Resolve E0-01 by preserving the stricter Week 5 quality gate: begin the supported
short-text grading vertical path and its frozen-benchmark evaluation during Weeks
3–5, alongside deterministic work. Week 6 hardens and broadens only already-gated
formats and completes content tooling. Week 2 still requires the teacher-scored
benchmark. This corrects the backlog's sequencing conflict; it does not move the
Week 5 gate, lower 85% agreement, remove dual-pass/calibrated 90% automatic-score
controls, or authorize any external model evaluation. Capacity/owners must be
confirmed at kickoff, and a missed gate remains a delivery risk, never a waived gate.

## Alternatives and consequences

Renaming stored difficulty labels would create unnecessary content/API migration.
Moving the short-text gate to Week 6 would relax the approved roadmap. Both are
rejected. The 12-week boundary and all release thresholds remain unchanged.

Legal notices, academic content/rights sign-off, reviewer recruitment, named owners,
kickoff date and the Week 8 provider decision cannot be manufactured in code. Keep
those as explicit external dependencies; synthetic implementation may continue.

## Approval and verification

This implements the user's explicit instruction to resolve pending work, within
existing scope and safeguards. No legal, academic or provider approval is inferred.
Documentation-link/whitespace checks apply. The difficulty adapter and its replay
checks are acceptance work for the E5 implementation.
