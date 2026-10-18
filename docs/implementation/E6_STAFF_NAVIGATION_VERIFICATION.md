# Responsive staff navigation verification

18 October 2026. NFR-ACC-001, NFR-COMP-001; user-requested frontend refinement.
Implementation discretion under the existing UX specification and approved local UI
stack; no ADR, API, schema, permission or business-behavior change is required.

## Change

Staff links stay visible on desktop. At <=640 CSS pixels, a 48-pixel Workspace menu
button controls the same single navigation landmark with aria-expanded/aria-controls.
Closed links leave the accessibility/focus tree. Enter/Space operate the button;
following a link or changing routes resets it closed, with exact aria-current preserved.
The synthetic-only notice remains explicit, and sign-in has a >=44-pixel touch target.
System typography, local SVG/CSS and the existing green/paper visual language avoid
remote assets or extra dependencies. No menu interaction modifies review form state.

## Acceptance evidence

Final serial `make format lint build test-web-content e2e` passes: two UI harness
cases, 90 existing full-matrix executions and 12 encrypted learner/reviewer executions
across Chromium, Firefox and WebKit. The 200% text keyboard/navigation case passes.
`make openapi-check` confirms unchanged generated contracts. Desktop and open/closed
mobile screenshots were inspected under `.local/ui-review`; the compact header leaves
more space for the task without losing any destination.

Final rebuilt images pass eight-service health, scheduled synthetic export/private
storage/web smoke, scoped request metrics, current HIGH/CRITICAL container scans and
source scanning. The persistent review stack is updated and all eight services remain
healthy. No setup/dependency, migration, API or domain changes are needed for this slice;
backend evidence belongs to [the underlying expert review](E4_EXPERT_REVIEW_VERIFICATION.md).
Exact-source hosted verification remains required before promotion.
Physical-device, approved-brand, screen-reader and pilot usability acceptance remain
separate release gates. This change does not enable real grading or learner data.


## Failures retained and corrections

The first full run correctly failed the old 320-pixel expectation that staff links are
always visible. The existing journey now requires an initially closed menu, >=44-pixel
target, Enter activation and the same visible active destinations; desktop expectations
remain unchanged. A new 200% text check found real overflow from the review grid's
minimum content width. Scoped zero-minimum grid sizing and anywhere text wrapping keep
all content available without horizontal clipping; DOM inspection reports 320/320
viewport/content width after the correction.

A subsequent WebKit run reached successful rubric preview but failed context closure
with ENOENT for trace artifacts. A concurrent UI harness had cleaned the shared
`test-results` directory. No assertion or timeout was relaxed. All native Playwright
commands are now rerun serially, and the runbook records this shared-directory hazard.
Final acceptance must come from that serial run, not the interrupted artifact run.
