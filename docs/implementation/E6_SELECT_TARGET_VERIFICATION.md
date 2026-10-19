# Shared select touch-target correction

Date: 19 October 2026. Candidate, not application acceptance.
Requirements: NFR-ACC-001, NFR-COMP-001, NFR-MNT-001.

## Comprehension and boundary

Specification 08 requires usable 44-by-44 touch targets where feasible and keyboard
operation. Existing shared ui-input/ui-select controls specify minimum heights, but
native WebKit menu rendering can ignore them. ADR-057's focused form correction
proves appearance styling can preserve a visible arrow while honoring target size.
Extend that same styling to shared single-select controls; preserve native semantics,
options, labels, focus, disabled state and existing form actions. Do not restyle
multi-select/listbox controls or introduce a custom JavaScript dropdown.

Read root/web AGENTS, installed Next CSS guidance and specification 08; inspect shared
styles and the existing narrow mobile/assessment/privacy journeys. No data, API,
authorization, runtime/dependency or architectural decision changes are required.
No unresolved contradiction is identified. Existing global shared-control styles
remain in the root stylesheet and are verified through a production build.

## Verification plan

Extend the existing synthetic 320-pixel touch journey to require both practice menu
controls, check width/height and keyboard focus at normal and 200% text, verify reflow
and axe, then complete the existing saved-learning journey. Run it in Chromium,
Firefox and WebKit with the prescribed target. Freeze screenshots and visually inspect
each engine. Add the same target-size assertion for the controlled staff editor in
its existing UI harness. Run lint/types/build, applicable broader browser/security/
image/service and hosted checks. Physical devices and branded browsers remain separate.

## Local results

Before CSS changes, Chromium and Firefox each pass the extended journey; WebKit
fails the actual height assertion with 23 pixels. After the shared single-select
rule replaces the form-only rule, `make test-web-select-targets test-web-content`
passes three full touch journeys and all three staff UI harness cases. Both practice
selectors retain keyboard focus and targets at least 44 by 44 at normal and 200%
text, with axe/reflow and the existing complete saved-learning journey unchanged.
Staff editor controls also meet the target at both text scales without horizontal
overflow, and controlled rubric save/reload still passes.

Three-engine 200% screenshots were visually inspected. Native closed menus can
truncate long selected labels at the narrowest enlarged view; their full options
remain available through the native picker and accessibility tree. No tiny-font or
custom JavaScript substitute is introduced. Multi-select/listbox styles are excluded.
Lint, formatting, Python/TypeScript checks, generated-contract agreement and the
production build pass. Final image/security/service and complete hosted checks
remain required before main promotion. No backend code or migration changes here;
the parent source's broad backend run continues independently.
