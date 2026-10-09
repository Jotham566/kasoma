# Learner UI completion readiness

Reviewed 9 October 2026. This is an implementation plan, not UI acceptance evidence.
The active export slice must retain its own acceptance gates. This review prepares the next
user-requested UI work while native dependency installations continue.

## Authority and scope

Use the [SRD](../specifications/01_SRD.md), [UX specification](../specifications/08_UX_Flows_and_Accessibility.md),
[security controls](../specifications/09_Security_Privacy_and_Safeguarding.md) and
[release tests](../specifications/10_Testing_Acceptance_and_Release.md).
The [roadmap](../product/PRODUCT_ROADMAP.md) places working learner flows in Weeks 3–5,
responsive feature completion in Weeks 6–8 and pilot refinement in Weeks 9–12. These are relative
milestones; a kickoff date is still missing from the [release register](RELEASE_GATES.md).

Requirements: FR-REV-006, FR-ID-003/004/005, FR-DIAG-005, FR-MST-004/005,
NFR-ACC-001, NFR-BW-001, NFR-COMP-001, NFR-LOC-001 and NFR-MNT-001.
No new API, database, provider, grading algorithm or product capability is needed for the first slice.
Existing Next.js, Tailwind and packages/ui remain the approved implementation stack.

## Observed implementation

- `apps/web/app/layout.tsx` supplies document language and metadata but no shared navigation.
- `apps/web/app/globals.css` defines basic colors, font and focus behavior; packages/ui currently
  exposes only a live status component. Buttons, fields, cards and spacing are repeated per screen.
- Home offers functional route links, server-readiness feedback and RecommendationCard. The
  recommendation already uses authorized server data, subject selection, explained next action,
  estimated duration, consent/identity/content error states and an in-memory command retry key.
- Onboarding, diagnostics, revision, hints, progress/history and privacy/channel screens exist.
  These are functional implementations, not complete visual-design or pilot acceptance.
- LearningDashboard already hides mastery below the confidence threshold and reports coverage,
  uncertainty and Kampala dates. Presentation work must preserve those conditions exactly.
- Real browser checks cover keyboard/axe behavior, lost acknowledgements, consent and diagnostic
  sealing. The 320-pixel touch journey checks reflow and key 44-pixel targets. Physical devices,
  branded browsers, screen-reader review and pilot usability remain separate release gates.

## Exact first vertical slice

Deliver consistent learner navigation plus a redesigned home and recommendation card, using the
existing APIs and routes. Keep the implementation independently reviewable from subsequent page
redesigns. Introduce only the shared primitives actually consumed by these screens.

Learner destinations remain Home, Revise, Progress, History and Profile/Settings; the existing
onboarding route supplies profile/sign-in functionality. Keep privacy and channel access easy to
find. Staff navigation remains a separate workspace; do not add teacher/parent portals, rankings,
Exam Mode or unavailable features. Avoid duplicate landmarks and confusing duplicate link names.

Use the repository's current restrained green/neutral palette as the initial visual direction,
with consistent type scale, spacing, borders and primary/secondary actions. This is implementation
discretion, not an approved brand identity. Use local system fonts and CSS; no remote font, image,
analytics or icon-provider calls. Existing synthetic-data notices and pending consent approval
must remain truthful; polished presentation does not authorize real-learner use.

The next useful activity must be prominent. Show only the server's recommendation and duration;
never manufacture progress, streaks, achievements or academic claims. Preserve explicit refresh,
profile/consent recovery and unavailable-content states. Do not prefetch private assessment data
or add a second set of analytics events for the same actions. Navigation must not discard an
unconfirmed command or falsely acknowledge an answer; current server resume/retry semantics apply.

## Acceptance for that slice

1. Anonymous, consent-blocked, content-unavailable and authorized recommendation states remain
   distinguishable, actionable and free of fabricated learner data.
2. Existing recommendation start/replay and subject-binding journeys pass against the real API.
3. Keyboard traversal, visible focus, skip navigation and active destination are usable; semantic
   headings/landmarks are unique. Axe passes, followed by an explicit manual keyboard check.
4. Layout reflows at 320 CSS pixels; primary touch controls meet the existing 44-pixel target.
   Enlarged text and reduced-motion preferences do not hide controls or obstruct the next action.
5. Existing three-engine learner regression passes. The first-question cold transfer remains
   below 250,000 bytes with the same measurement and exclusions; do not relax it for styling.
6. Lint, formatting, types, production build, security-source and contract checks pass. Record
   actual viewport screenshots and review layout before claiming visual completion.
7. Rebuild the local web container and keep the review stack running at localhost:3000.
   Update changelog, sprint and requirement evidence with measured results and remaining limits.

No migration is expected. If implementation discovers a missing backend contract, handle it as
an explicit follow-on requirement rather than inventing data in the UI.

## Subsequent UI sequence

- Apply the same navigation/control foundation to onboarding and consent, retaining all age,
  guardian, verification, withdrawal and session-security behavior.
- Complete diagnostic and practice presentation, feedback/hints/solution hierarchy, retry and
  session summary states; preserve diagnostic sealing and immutable answers.
- Complete confidence-aware progress/history and profile/privacy/channel screens, including
  empty, loading, error, stale and recovery states.
- Bring content, review, imports, flags and operations workspaces to a consistent staff layout.
  Audit presentation must depend on the approved audit capability, not fabricated records.
- Run supported-browser/device and assistive-technology review with representative approved
  content when available; incorporate pilot feedback before release sign-off.

The UI sequence does not mark pending short-text grading, retention/deletion, academic content,
provider selection, privacy approval or operational release work complete.


Learner UI foundation candidate (FR-REV-006, NFR-ACC-001/BW-001/COMP-001): shared learner
navigation and skip link, consistent home/recommendation styling and explicit synthetic-preview
notice now use existing routes and API state. Shared navigation replaces redundant progress/history
menus; staff routes retain their separate workspace. Navigation prefetch is disabled. No backend,
consent, grade, mastery or retention behavior changes. New 320/1280-pixel, enlarged-text, keyboard,
axe and anonymous-state browser checks accompany the existing authenticated recommendation suite.
Build/lint/types passed before the new tests; full regression and screenshot review are pending.


Learner UI foundation verification: `make format lint build e2e-chromium-full` passes all
30 tests (15 per shard), including both new 320/1280-pixel home checks, 200% text reflow,
44-pixel navigation targets, keyboard skip/focus, active destinations, staff separation, axe,
and the existing authenticated recommendation/learning/privacy/channel journeys. Cold first-
question transfer is 175,609 bytes against the unchanged 250,000-byte ceiling. Desktop and
320-pixel screenshots were inspected with no clipping; local copies are under `.local/ui-review`.
The web container rebuild succeeded. This is Chromium engineering evidence, not full browser,
physical-device, screen-reader, academic, brand or pilot acceptance. Subsequent page design
and the remaining export acceptance gates are still open. No new ADR or API/migration is needed.


Onboarding presentation candidate (FR-ID-001/003/004/005, NFR-ACC-001/COMP-001): apply
consistent field/button/card styling and remove obsolete claims that learning and diagnostics
are unimplemented. When the server reports learning_allowed, offer the existing diagnostic
route as a next action. Preserve separate guardian verification/assent, withdrawal, OTP limits,
session security and synthetic notices. Browser and screenshot verification is in progress.

Local runtime update: API and ordinary worker images built and both containers are healthy.
Web, PostgreSQL, Redis and Mailpit remain healthy. Fictional email sign-in codes are available
only through local Mailpit at localhost:8025. MinIO and the dependent export worker remain
pending; do not equate partial stack health with complete export acceptance.


Onboarding result: `make format lint build e2e-chromium-full` passed 30 cases; after adding
explicit consent-gated next-action and onboarding reflow/screenshot assertions, `make format
lint e2e-chromium-full` again passed 30 cases. Desktop and 320-pixel onboarding screenshots
were inspected and retained under `.local/ui-review`. The rebuilt web container is healthy.
Existing adult/minor/guardian, withdrawal, cookie and retry protections continue to pass.

Local review setup: an initial assessment seed failed because the developer catalog was empty.
`make seed` populated S4/two subjects/six clusters; its storage-init step still fails because
MinIO is unavailable. Standard assessment/numeric/diagnostic/reassessment/multiple-choice seeds
then passed. The consecutive hints seed hit the existing shared fixture OTP cooldown; retrying
`make seed-hints` after the cooldown passed without weakening authentication limits. All fixtures
are synthetic and excluded from academic release counts. API, ordinary worker, web, PostgreSQL,
Redis and Mailpit are healthy; storage/export-worker and other browser engines remain pending.


Practice/diagnostic presentation candidate (FR-DIAG-004, FR-REV-005/006, FR-GRD-006,
NFR-ACC-001/BW-001/COMP-001): apply consistent question cards, selected answer controls and
primary submit actions. Shared SavedProgress displays only the server's saved-answer count,
never mastery or a diagnostic score. Preserve hint/solution gating, immutable submissions and
same-key retries. Browser assertions cover saved progress after acknowledgements, and captures
cover desktop/mobile questions. Verification is running; no acceptance claim yet.


NFR-MNT-001 container build refinement: copy workspace manifests and dependency patches
before installing the frozen web lockfile, then copy application/package source. This preserves
pinned dependencies and runtime image behavior while allowing ordinary UI edits to reuse the
install layer. The previous Dockerfile copied all source before installation, causing repeated
network downloads on every local visual update. Build/cache evidence remains pending.


Practice/diagnostic result: `make format lint build e2e-chromium-full` passes 30 cases after
the final spacing/button corrections. Native saved-progress values are checked against server
acknowledgements, including lost-response recovery; keyboard/axe/320-pixel journeys still pass.
Desktop practice/diagnostic and mobile practice screenshots were inspected. The rebuilt web
image now reuses the frozen dependency-install layer (`CACHED`) after a source-only change;
its latest container is healthy. No grading, consent or diagnostic disclosure rules changed.


### Progress and history presentation candidate — 9 October 2026

FR-MST-004/005, NFR-ACC-001/COMP-001/LOC-001/MNT-001: progress now uses responsive
subject/topic/competency cards with explicit evidence labels and the existing confidence-gated
mastery display. History uses consistent session cards and touch controls; empty history links
to the existing diagnostic. Authentication/consent blocks offer profile recovery. Private session
links disable prefetch. Server selection, paging, diagnostic sealing, confidence thresholds and
Kampala timestamps are unchanged. Browser checks now include 320-pixel progress/history reflow,
active navigation, history touch targets and screenshots. Lint/build/browser verification is
running; this entry is not acceptance. No API/migration change or new ADR is needed.


Progress/history verification: `make format lint build e2e-chromium-full` passes all 30
Chromium cases (15 per shard), including sparse-evidence suppression, offline recovery,
owned pagination, diagnostic sealing/resume, 320-pixel reflow and 44-pixel history controls.
Desktop progress and mobile progress/history captures were inspected with no clipping.
Evidence: `.local/progress-history-ui-checks.log` and `.local/ui-review/`. The web image
build passed and the restarted local web is healthy. No API, migration or ADR change. Remaining
engines, physical-device/screen-reader and pilot acceptance are still open.


### Privacy and channel presentation candidate — 9 October 2026

FR-ID-006, FR-WA-001/006 and NFR-ACC-001/COMP-001/LOC-001/MNT-001: apply the existing
card/control styles to privacy requests and channel linking, wrap long request references,
keep export actions usable at 320 pixels and remove duplicate learner Home links. Preserve
owner/re-authentication, ambiguous-command retries, explicit status checks, deletion-pending
wording and fake-only delivery. Link-code expiry now explicitly uses Africa/Kampala and a
semantic time element instead of the browser's local timezone. Browser checks include
320-pixel privacy/channel layout, privacy axe and the displayed expiry timestamp.
Verification is running. No API, migration, provider or architectural decision changes.


Privacy/channel result: `make format lint build e2e-chromium-full` passes all 30 Chromium
cases (15 per shard), including mobile privacy axe, 320-pixel request-reference/control
reflow, background frozen export, lost command recovery and channel STOP/unlink. Link-code
time is checked against the server expiry in Africa/Kampala. Privacy/channel mobile captures
were inspected without clipping. Source/contract/doc checks pass. Evidence:
`.local/privacy-channel-ui-checks.log` and `.local/privacy-channel-contract-checks.log`.
Other browser engines and real-device/pilot acceptance remain open.


### Staff navigation candidate — 9 October 2026

FR-CNT-001/003/006, FR-OPS-002, FR-ID-006 and NFR-ACC-001/SEC-002/MNT-001:
add one shared staff header with links to existing content/review, imports, flags, privacy
review and operations routes. Active destination and 44-pixel controls support narrow screens.
No staff role is inferred from navigation; each existing API continues to enforce access.
No Audit link is invented while a dedicated audit screen remains absent. Learner navigation
stays separate. Browser checks cover narrow/wide header reflow, active destination, axe and
unauthorized operational denial. Verification is running; no API, migration or ADR change.


Staff navigation verification: `make format lint build e2e-chromium-full test-web-content`
passes 30 Chromium journey cases plus the isolated rubric-editor case. Narrow/wide captures
were inspected without clipping. Active navigation, 44-pixel targets, axe and anonymous
operations denial pass. Source secret, generated contract and documentation checks pass.
The rebuilt web image is ready for local review. Evidence: `.local/staff-navigation-checks.log`,
`.local/staff-navigation-source-checks.log` and `.local/ui-review/staff-*.png`. No new ADR
or API/migration change. Full browser/pilot acceptance and remaining staff page design are open.


### Staff operational screens candidate — 9 October 2026

FR-OPS-002, FR-CNT-001/006 and NFR-ACC-001/COMP-001/MNT-001: apply shared control
and card presentation to operations, flag triage and synthetic imports. Group service health,
alerts and workloads into named regions; keep metric tables bounded at narrow widths.
No metrics are invented and missing data remains explicitly unavailable. Explicit refresh,
review/claim/retry, role checks and draft-only import behavior are unchanged. Operations
checks now include authenticated desktop/mobile captures, 320-pixel reflow and axe.
Verification is running; no new API, migration or ADR.


Staff operations result: `make format lint build e2e-chromium-full` passes 30 Chromium
journeys, including independent flag triage, bounded draft import and authenticated operations
at 320 pixels. Desktop/mobile operations captures were inspected without clipping; missing
heartbeat and unmeasured instrumentation remain explicit. Source, contract and documentation
checks pass. Web image rebuilt. Evidence: `.local/staff-operations-ui-checks.log`,
`.local/staff-operations-source-checks.log` and `.local/ui-review/operations-*.png`.
No API, migration or architecture changes; other engines/pilot gates remain open.


### Content editor presentation candidate — 9 October 2026

FR-CNT-001/003/005 and NFR-ACC-001/COMP-001/MNT-001: style the existing content/review
queue, staff preview, author fields and rubric/numeric controls consistently. Fieldsets have
bounded width and a named draft form; save remains explicit. No document/schema, review,
rights, eligibility or versioning behavior changes. The isolated controlled-rubric test adds
desktop/mobile captures, 320-pixel reflow and axe before verifying exact save/reload.
Verification is running. No API, migration or architectural decision changes.


Content editor result: `make format lint build test-web-content e2e-chromium-full` passes
the isolated mobile/axe/exact-rubric-save/reload test and all 30 Chromium journeys.
Desktop/mobile captures were inspected without clipping; the long authoring form still needs
human usability acceptance. Source/contract/doc checks pass. The web image built successfully.
Evidence: `.local/content-editor-ui-checks.log`, `.local/content-editor-source-checks.log`
and `.local/ui-review/content-editor-*.png`. No academic eligibility or publication change;
no API/migration or ADR change. Remaining browser/pilot gates stay open.
