# Changelog

## Verified — bounded synthetic channel capture

- Add additive 0038 source/capture, finite disposal, generated contracts, advisory
  inventory and operator controls under ADR-057. Expanded 34 focused integration (including
  both actual restricted logins), 105 contract/format and 108 browser executions pass;
  complete hosted 39183714273 verifies source `0a8f674` with all 1,055 unit/contract,
  412 integration, 35 tooling and full security/recovery/image/service gates. Source
  is on main and its merged branch is removed. Creation stays disabled.
- Reproduce and correct the existing advancing-clock conversation expiry mismatch
  using one timestamp per exact 24-hour pair; both regression cases and the real-time
  conversation/capture browser journey pass. No database invariant is relaxed.
- Give each request hold region a distinct accessible name and enforce 44-pixel
  capture dropdown targets, including WebKit and 200% text. No accessibility exclusion
  or test timeout is added.

## Verified format — approved synthetic channel preservation

- Record the user's explicit bounded ADR-057 implementation approval. Real-data
  processing, account erasure and production privacy/release gates remain separate.
- Add a private, bounded, strict link/conversation evidence format with purpose- and
  snapshot-bound authenticated encryption, UTC canonicalization and closed diagnostics.
  No runtime capture, storage, endpoint, permission or retention change is enabled.
- Add 82 offline format/tampering/allowlist/binding cases and the prescribed
  `make test-channel-preservation-format` command. Full ADR-057 acceptance remains pending.
- Source `25b44b1` passes complete hosted [39176205670](https://github.com/Jotham566/kasoma/actions/runs/39176205670),
  all 1,022 unit/contract, 378 integration and 35 tooling cases, full browser/security/
  recovery/image/service gates. This is format acceptance only; capture is separate.
- Capture development exposes a real advancing-clock conversation expiry mismatch;
  the correction and new real-time coverage are now verified in `0a8f674`.

## Accepted engineering checkpoint — 19 October 2026

- Source 5d95f9d passes complete hosted [39171302022](https://github.com/Jotham566/kasoma/actions/runs/39171302022)
  and is on main with a documentation-only closeout. Merged branches are removed.
- Accept ADR-056/058/059 within their bounded engineering scope: wall-clock hold
  guards, aggregate ADMIN audit activity and disposable hosted storage safeguards.
  All 940 unit/contract, 378 integration, 35 tooling and full browser/security/restore/
  image/service checks pass. Historical failed/cancelled runs remain recorded below.
- Keep receipt creation and normal learner short-text delivery disabled. ADR-057
  remains an owner-review proposal; full preservation, erasure and real release gates
  remain incomplete. This acceptance supersedes older pending engineering status.

## Verified — disposable CI storage and navigation regression

- Preserve the failed hold-clock hosted run as failed disk-capacity evidence. Add
  ADR-059 hosted-only fixed SDK preparation, initial/phase capacity gates and read-only
  diagnostics; no local cleanup or reduction in application checks.
- Replace the obsolete absent-Audit navigation guard with its implemented exact target.
  All 105 browser executions, 22 storage safety and 940 unit/contract cases
  pass locally; corrected full-source hosted acceptance remains required.

## Verified — bounded ADMIN audit activity

- Implement the approved audit endpoint and navigation as fixed-category last-24-hour
  activity sampling under ADR-058, with live ADMIN checks, bounded reads and honest
  sample-cap reporting. No individual audit fields or extra support permission.
- Add an audit time-window index, strict generated contracts, real API/window/upgrade
  tests and accessible staff UI/browser coverage. Full local verification passes 918
  unit/contract, 35 tooling and 378 integration cases, restricted login, recovery,
  security and rebuilt Docker/browser smoke; complete hosted acceptance remains pending.

## Documentation — recovery and preservation review

- Record a nondestructive eight-service restart after a power interruption, preserving
  volumes and existing environment configuration, with fake-only smoke verification.
- Prepare ADR-057 for explicit owner review of bounded minimized link/conversation
  snapshots. No runtime behavior, new data retention or erasure authority is introduced.

## Verified — legacy hold DELETE clock

- Reproduce transaction-start time missing a later committed hold in all four legacy
  DELETE wrappers, using temporary probe rows while original evidence stays protected.
- Add forward migration 0036 to use database wall clock only in those wrappers, preserving the
  explicit historical predicate, source data, permissions, finite scope and independent
  immutable guards. Local verification passes 57 related integration cases, 918
  unit/contract and 35 tooling cases, restricted logins, populated recovery, security
  and rebuilt 0036 Docker smoke. Complete hosted acceptance remains pending.

## Verified — terminal channel receipt holds

- Preserve applied 0034 and add forward migration 0035 after a final real-menu regression catches
  PostgreSQL json equality failure on held no-op updates. Canonical JSONB comparison
  preserves menu order/core protection; clean and existing-hold upgrade/replay pass.
- Final 21-case receipt/clock/race/restricted-login verification passes alongside 918
  unit/contract,364 broad integration and 102 full browser executions. New creation
  remains disabled; the 0035 stack passes smoke/security/health with creation disabled. Complete hosted
  run 39165896953 passes at 397f562; it is on main and its merged branch is removed.

- Assess exact-record holds for already-minimized owned terminal inbound/outbound
  receipts under proposed ADR-055. Preserve normal callbacks, STOP/unlink and bounded
  unrelated cleanup, with database-clock guards and default-disabled staged creation.
  Live messages, links, conversations and usable code preservation remain unsupported.
  Add0034 guards, hold capabilities/UI, hold-aware cleanup and clean/upgrade/race/
  opt-out regressions. Initial 16-case receipt verification, existing holds/channels and
  restricted login/65-table/648-row recovery pass; final acceptance is in progress.

## Verified — bounded local model observations

- Add six private, attribute-free worker counters and bounded five-minute Redis
  aggregation under proposed ADR-054. Observe actual provider-port attempts after
  authorization; omitted usage stays unknown, explicit reported zero stays zero.
- Extend the ADMIN snapshot/dashboard with local attempt counts, known token
  subtotals, unavailable totals and a typed volume warning. No billing, fleet ledger,
  grading accuracy or quota enforcement claim. Only the ordinary development/test
  worker publishes freshness; fixed fake probes verify the running stack.
- Preserve the existing request histogram wire format while sharing its finite byte
  transport. Add SDK, real Redis, role/lifecycle, alert and accessible presentation
  regressions. Complete hosted run 39160113771 passes at `0c73c45`; the source is on main
  and its merged branch is removed. Learner scoring remains disabled.


## Verified — configurable per-job grading budgets

- Expose the existing shared request/token/deadline ceilings through typed server
  settings while preserving defaults and hard maxima of three requests, 16,384 tokens
  and five seconds. Both independent passes and the optional repair share one snapshot.
  The pre-dispatch deadline uses the same configured timeout.
- Verify stricter request, token and deadline exhaustion preserves the encrypted saved
  attempt, neutral no-score/no-mastery outcome and idempotent replay. No new quota
  policy, inference profile, approval, API, provider or persistence changes. Local
  verification passes 891 unit/contract, 21 flow and 33 review cases, restricted login,
  security, populated recovery and rebuilt image/service smoke; hosted acceptance
  passes at `f5f408e` in hosted run 39157127637. The source is on main and its merged
  branch is removed locally/remotely.

## Verified — grading queue operations

- Hosted run 39155326659 passes for `a357222`; promote to main and remove the merged
  grading-operations branch locally/remotely.
- Promote verified independent review, responsive navigation and offline report comparison
  through `17abb2d` to main after hosted runs 39150319607/39151730479 pass; remove all
  three merged source branches. Keep the current unmerged operations work separate.
- Fix host/VM completion-clock skew by capping at database time while retaining SQL
  guards. A rollback-only reproduction changes from nine failures in ten to ten successes.
  Await each diagnostic POST acknowledgement before checking its exact saved attempt.

- Propose ADR-053 and extend the existing ADMIN snapshot/dashboard with bounded
  grading queue/lease age, terminal outcomes, pending audits and post-activation
  disablement counts. Add a typed local stale-queue threshold and alert.
- Label GRADING_FAILED outcomes processing fallbacks because they include expected
  provider refusals and budget/validation outcomes. Do not infer academic error rate,
  model cost or an incident from those counts; existing unavailable metrics stay honest.
  Local verification passes 884 unit/contract and 333 broad integration cases, supplemented
  by 33 review/26 operational cases, restricted login, 104 browser executions, populated
  recovery and rebuilt image/security/smoke checks. Hosted acceptance remains pending.
  No grading policy, provider, persistence or retention changes.

## Work in progress — offline evaluation reports

- Propose ADR-052 and implement a strict payload-free synthetic short-text report
  contract and the required read-only `make eval-compare` command. Compare only matching
  frozen benchmark/schema/metric-policy references, include all planned cases in quality
  denominators and preserve unavailable usage. Reject ambiguous, oversized or private
  input and return closed errors. No inference, model/provider selection, approval or
  learner scoring is performed. Thirty-seven new cases, 881 total unit/contract and
  35 tooling cases, actual Make invocation, lint/contracts/security pass; hosted
  acceptance and actual benchmark/provider/evaluation gates remain open.

## Work in progress — staff mobile navigation

- Replace the always-expanded narrow-screen staff links with an explicit accessible
  workspace menu; retain visible desktop navigation and the current destination.
  Close the menu on navigation, keep sign-in touch-accessible and preserve the
  synthetic-data notice. No route permissions or learner workflows change.
- Verify keyboard disclosure, active links, navigation reset, 320-pixel reflow and
  reviewer-form state across browser engines before acceptance. Fix real 200% text
  overflow in the review grid using scoped wrapping and zero-minimum grid sizing;
  preserve content rather than clipping it. Record shared Playwright artifact collisions
  and require sequential native browser commands. Final serial acceptance passes 104
  browser executions, lint/build/contracts and rebuilt-image/service/security checks;
  exact-source hosted verification remains pending.

## Work in progress — independent grading review

- Implement ADR-051 candidate migration 0033, blinded academic-review API and responsive
  staff workspace. Validate every pinned criterion, calculate exact agreement in SQL,
  retain immutable completions and disable affected bands atomically on critical error
  or rolling agreement below 90%. Existing grades and mastery are never overridden.
- Preserve global publication ordinals and add versioned session/band sampling so
  permanently sealed diagnostic grades cannot consume released revision coverage.
- Add minimized owned exports, diagnostic sealing, exact review holds, deletion-impact
  inventory, correlated read/completion audit, restricted-login and populated recovery
  coverage. Recheck current consent, role and audit state at confidential access and
  each model pass/publication. Normal short-text scoring remains disabled.
- Verify the new accessible desktop/mobile journey across Chromium, Firefox and WebKit,
  including bounded pagination, explicit rubric inputs and exact retry after a lost
  acknowledgement. Thirty-two focused review cases, 844 unit/contract cases, restricted
  login, repeat populated recovery, 324 broad integration cases and rebuilt container
  checks pass. Exact-source hosted verification remains pending;
  see the expert-review verification register. No real academic approval is implied.

## Work in progress — short-text learner integration

- Promote disabled synthetic learner flow `853f80a` to main after complete hosted run
  39143803289 passes, including current container scans. Remove its merged branch.
  Restore the local review stack after a power interruption without resetting volumes.
  Actual learner scoring and the independent expert-review slice remain gated.

- Verify nine synthetic short-text browser journeys across Chromium, Firefox and
  WebKit, including mobile neutral fallback, review requests and sealed diagnostics.
  Fix the textarea accessible label and distinct report/hint React keys. Add duplicate
  worker, publication crash, revoked-report, broker failure and SQL atomicity coverage;
  extend isolated logical recovery with encrypted rubric evidence. Full regression and
  independent expert-review integration remain pending; normal scoring stays disabled.

- Route durable short-text work through the specified separate grading queue and
  retain periodic recovery after wake-up failure. Bound owned feedback reads and
  automatic client polling. Add a documented Trivy database-source override while
  preserving scanner version, freshness checks and HIGH/CRITICAL failure thresholds.

- Build the candidate encrypted submission/receipt/work flow, owned pending/fallback
  outcomes, finite-lease fake processor, atomic rubric grade/mastery/audit publication,
  schema/client changes, draft learner polling UI and diagnostic sealing coordination.
  Runtime enablement defaults false; genuine report/safety authorities remain unavailable.
  Ten intermediate PostgreSQL/API cases and 828 unit/contract plus 35 tooling cases pass;
  the full feature, audit review, browser, role and recovery gates remain under implementation.


- Begin the cohesive learner short-text flow with strict pinned rubric-result and
  partial-credit projection contracts. Revalidate exact answer evidence and reviewed
  feedback; reject inconsistent scores and hidden/unsupported fields. All 808
  unit/contract and 35 tooling cases pass with lint/types and unchanged HTTP contracts.
  Persistence, worker, ownership, polling/fallback and expert audit integration remain open.


- Add the publication/audit assignment ledger with band-locked ordinals, atomic sampling,
  immutable records, owned minimized exports, deletion inventory and exact-record holds.
  Generated contracts and staff hold controls include both types. Verification passes 12 focused SQL cases, 19 existing hold cases, restricted login,
  populated recovery, six browser executions, lint/types/contracts and rebuilt image
  scans. Full regression passes 780 unit/contract, 35 tooling and 291 integration cases;
  dependency security retry passes. Hosted publication acceptance remains required.
  Learner scoring, expert review and automatic disablement remain pending.

- Add immutable calibration-band metadata and exact transition history, disabled
  registration, locked snapshots and sticky disablement. Verify worker permissions
  allow disablement without approval/activation rights and extend populated recovery.
  No activation command or learner scoring is enabled. Full backend regression passes
  279 integration cases; a later reproduced topic-reparenting gap is closed with
  migration 0029's composite scope FK. Thirteen focused SQL cases, populated upgrade,
  restricted-login and recovery checks pass after that correction; hosted acceptance remains required.

- Add a versioned calibration/audit eligibility component with exact threshold counts,
  scope/version/length binding, approval-reference requirements, audit coverage and
  sticky-disablement checks. Propose a bounded rolling window and prefix-complete 10%
  audit selection under ADR-050; academic approval and durable/runtime integration remain
  required. No band or learner scoring is enabled by this component.
  Verification passes 780 unit/contract and 35 tooling tests, lint/types, generated
  contracts, source-secret and dependency/security checks.

- Define one-claim grading transitions with bounded queue/lease expiry and exact
  terminal replay. Interrupted claims fall back without resetting model-call budgets;
  late workers cannot publish. Durable persistence/worker wiring remains pending.

- Add a bounded authenticated answer envelope using the existing encryption interface,
  binding learner/attempt/assignment/item/rubric IDs and preserving exact answer text.
  Ciphertext replay, malformed data and provider diagnostics fail closed. Persistence
  and learner delivery remain disabled pending coordinated integration. All 730
  unit/contract and 35 tooling cases pass, with lint/types, contracts and secret scans.

- Reconcile readiness against existing assessment/mastery contracts and the mandatory
  beta expert-audit and automatic band-disablement rules. Scoring and learner selection
  remain disabled; this assessment provides no academic acceptance.

## Work in progress — hosted verification recovery

- Reproduce WebKit attachment timeouts in a network-isolated Linux control. Explicit
  HTML download intent passes complete/stalled/corrupt native transfers. Apply that
  intent to the background-export link; application error/retry acceptance is pending.
  Add bounded recent-owner status preflight and closed in-page errors after the
  attribute-only change failed signed-out notice regression; download authorization
  remains independent. Test unavailable status, no download and frozen recovery.
  Verification passes 90 native browser executions, three Linux transport controls,
  six final privacy executions, lint/types, contracts, source scanning and rebuilt
  container scans/smoke. Exact-head hosted acceptance remains required.

- Record the hosted Linux WebKit attachment failures after successful service/backend
  and Chromium/Firefox checks. Add a complete native-download loopback control with
  filename and exact-byte assertions; preserve mandatory application acceptance.

- Record continued PostgreSQL throttling after successful mirror configuration. Add
  optional, step-scoped Docker Hub authentication with a pinned official login action;
  preserve anonymous fork verification and automatic logout. Credentials remain external.

- Address the subsequent PostgreSQL pull throttle with a public Docker Hub cache
  configured only on disposable CI runners. Preserve daemon settings, validate before
  bounded restart, and test configuration merging and local-execution refusal.

- Address the observed 40-minute hosted timeout with a bounded 90-minute job and
  lock-keyed browser cache. Use the byte-identical official Mailpit mirror only in CI
  after Docker Hub throttled the runner. Every application/security check remains required.

## Work in progress — request aggregation

- Complete local acceptance: 259 integration cases, 666 unit/contract cases, 32 tooling
  checks, 90 browser executions, generated contracts, security scans/audits and both
  live container probes pass. Final-head hosted verification remains pending.

- Build/scan and refresh the local eight-service stack. Verify scheduled exports and
  real API-to-Redis metrics publication; add the bounded metrics probe to container smoke.
  Full backend/hosted acceptance remains pending.

- Verify all 90 native browser executions after strengthening consent/error selectors;
  operations display-state, mobile and accessibility checks pass. Full backend and
  container acceptance remain in progress.

- Trace and correct a browser-test consent race: the success substring also matched
  the paused-consent sentence. Anchor all 14 success assertions, preserving the actual
  consent gate. Scope export errors to main content to exclude Next's route announcer;
  retain synthetic browser traces only on failure.

- Wire API collection, minimized ADMIN snapshots, conservative sample-gated latency
  alerts and histogram-range presentation. Add typed thresholds, generated contracts
  and the alert event schema. Runtime/API/browser verification is in progress.

- Add bounded Redis interval retention and retry deduplication, corruption/freshness
  handling, and an owned background SDK collector with finite I/O/shutdown. Add
  local Redis and fake-store lifecycle tests; API/dashboard integration remains pending.

- Start an isolated, attribute-free OpenTelemetry histogram component with disabled
  exemplars, explicit resource metadata and honest percentile intervals. Add SDK and
  property tests and ADR-049 proposal. API wiring, Redis retention and dashboard
  integration remain pending; no runtime behavior changes yet.

- Add bounded canonical interval projection and fail-closed SDK/storage validation.
  Format/lint/types, 650 unit/contract cases, 32 tooling checks, OpenAPI comparison
  and source secret scanning pass. Runtime integration remains unverified.

## Work in progress — learner UI foundation

- Increase shared learner/staff navigation targets to 48px; retain the 44px acceptance minimum across browser bounding-box rounding. All 90 native browser executions pass.

- Correct the native macOS WebKit keyboard test to use Option-Tab for links, preserving skip-link/main-content focus assertions and ordinary Tab on other engines/platforms. All 30 native WebKit application cases pass after the correction.

- Style the content queue/editor and rubric/numeric fields consistently while retaining exact draft and independent-review semantics. Lint/types/build, mobile/axe/exact-save-reload and all 30 Chromium journeys pass; desktop/mobile captures reviewed.

- Apply shared presentation to operations, flags and synthetic imports; preserve unavailable metrics and explicit audited review controls. Lint/types/build and 30 Chromium cases pass; authenticated mobile/desktop captures reviewed.

- Add consistent staff workspace navigation for existing routes with active state, narrow-screen touch controls and unchanged server authorization. Lint/types/build, 30 Chromium journeys and the isolated editor check pass; desktop/mobile captures reviewed.

- Restyle privacy requests and WhatsApp linking for mobile, preserving explicit consent/re-authentication and retry controls; display link-code expiry explicitly in Kampala time. Lint/types/build and all 30 Chromium cases pass; mobile captures reviewed.

- Restyle confidence-aware progress and session history with responsive cards, explicit empty/auth recovery actions and consistent touch controls. Preserve server-derived estimates, diagnostic sealing and pagination; lint/types/build and 30 Chromium cases pass, with desktop/mobile screenshot review.

- Verify practice/diagnostic presentation with 30 Chromium cases and desktop/mobile screenshot review; verify the web dependency layer is cached after a source edit. Native MinIO and private storage initialization now work; all 59 storage checks pass, with full regression running.

- Separate web dependency installation from application source in the Docker build so UI-only changes can reuse the frozen dependency layer (NFR-MNT-001).

- Restyle practice/diagnostic questions and selected answers; share an accessible saved-answer progress indicator driven by server counts. Preserve scoring, hints, sealing and retry behavior; verification is in progress.

- Verify onboarding presentation and consent-gated diagnostic links in the 30-case Chromium suite; inspect desktop/mobile screenshots and refresh the running web container. Seed synthetic local learning fixtures while recording the still-unavailable storage initializer.

- Restyle onboarding fields/cards/actions, correct obsolete learning-availability copy and offer a diagnostic next step only when the server grants learning access. Guardian/consent/session semantics remain unchanged.

- Verify 30 full-Chromium cases with the new UI, 320/1280-pixel screenshot review, 200% text reflow, keyboard/axe checks and 175,609-byte cold question transfer. Web image rebuilt; remaining browser/pilot acceptance stays open.

- Introduce shared learner navigation, a keyboard skip link and a responsive home/recommendation presentation using existing authorized data. Preserve synthetic notices, consent and retry semantics; verification is in progress.

## Work in progress — asynchronous owned export lifecycle

- Verify Firefox corruption through the same pinned browser's ordinary download manager, with real privacy-page actions, native failure, closed reader, unchanged READY state and exact frozen retry. The case remains mandatory; all 90 native browser executions pass; final-head hosted acceptance remains pending.

- Enforce the five-second object-read deadline in the delivery service as well as the adapter. A stalled-adapter regression and all 42 focused export cases pass; Firefox cancellation, bounded cleanup and frozen retry now pass. Corruption acceptance remains open.

- Add a disposable-profile native Firefox download-manager diagnostic and bounded/redacted protocol checks; ordinary HTTP/1.1 corruption is rejected, while raw-server cancellation confirms delayed disconnects.

- Add standalone loopback attachment controls to distinguish browser automation failures from application transport. Chromium passes; Firefox reproduces both failures without Kasoma. No acceptance waiver.

- Add serial native export diagnostics with named failure/closure steps and retained local traces. Firefox cancellation/corruption failures reproduce; acceptance and main promotion remain gated.

- Document channel-preservation dependencies: terminal field clearing, STOP/unlink, relinking ownership and bounded expiry must remain compatible with any future hold mechanism. No retention or hold behavior changes.

- Pass updated-database HIGH/CRITICAL scans for both local API and web images after the bounded download-timeout adjustment.

- Audit export acceptance against concrete security, cleanup, large-history and interruption assertions; retain explicit browser/container/hosted promotion gates.

- Allow a finite configurable 30-minute container scan timeout after the default five-minute vulnerability database download timed out. Keep current database updates and HIGH/CRITICAL failure gates unchanged.

- Complete the native 245-case integration regression with real MinIO, dependency/security checks, populated logical recovery and isolated content-admin UI verification. Correct obsolete candidate registration comments; remaining browser/container/hosted gates still block promotion.

- Verify a complete owned export through the actual Docker scheduler, export worker, private MinIO and web gateway. Add the bounded fictional-account probe to container smoke; preserve running review services and hide private diagnostics.

- Record the next learner UI slice and its accessibility, responsive-layout, privacy and cold-transfer acceptance gates from the actual screens; implementation and visual acceptance remain pending.

- Verify both full pinned Chromium shards: 28 tests pass, including native export failure/cancellation/frozen retry, privacy review and operations metrics. Secret scanning and generated contracts pass; Firefox/WebKit/storage/container acceptance remains open.

- Scope administrator privacy-review browser assertions to the learner's exact request references so concurrent exports cannot make the test ambiguous. Native Chromium export cancellation/corruption journeys pass; full matrix verification continues.

- Add a documented full-Chromium headless test command using the pinned installed browser; retain the normal three-engine CI matrix and all assertions (NFR-COMP-001, NFR-MNT-001).

- Add isolated fake-store corruption/cancellation fixtures and frozen-retry acceptance journeys (FR-ID-006). Reject fixture installation outside random E2E schemas; native browser execution remains pending.

- Tighten the registered export gateway regression to require exact unauthenticated denial; 15 worker checks and three real gateway HTTP cases pass, along with lint, formatting and types.

- Target each Compose worker health probe to its own explicit node and require its pong, preventing another healthy consumer from masking failure (FR-OPS-002, NFR-MNT-001).
- Record the latest full regression: 594 unit/contract, 32 tooling and 243 integration passes; two unavailable-MinIO failures remain open. Candidate wiring is local and unaccepted. Earlier disabled-stage entries below are historical.

- Wire candidate owner routes, generated client, background prepare/status/retry/save controls, dedicated native/Compose worker and scheduler for local synthetic acceptance. Full promotion and browser/storage gates remain open.

- Add the dedicated `make worker-exports` launch policy and restrict ordinary workers to operations/imports/messaging. Verify the actual launch flags through synthetic hard-stop, process replacement and queue-isolation tests; automatic export scheduling remains disabled.

- Add capped export queue/failure/age metrics and configurable local warnings to the ADMIN operations view, with generated contracts and threshold/lifecycle tests (FR-OPS-002).

- Return failed attachment navigations to a fixed privacy-page alert using only closed error codes; preserve JSON errors for programmatic requests and abort incomplete transfers. Add actual Next/API HTTP checks.

- Verify a diagnostic completed during asynchronous generation cannot unseal an earlier snapshot; a later explicit request includes released grades. All 41 focused export integration cases pass.

- Populate the isolated logical recovery drill with a published synthetic export and verify restored guards, encrypted manifest and frozen bytes (FR-ID-006, NFR-REL-002). Object-storage recovery remains a separate gate.
- Connect the web gateway to exact-length streamed attachments with separate initial/transfer deadlines, closed errors and disconnect cancellation; 31 tooling cases pass. API registration and learner controls remain pending.

- Set local PostgreSQL shared memory to 512 MiB after the 64 MiB Docker default caused a full-regression outage (NFR-MNT-001). Preserve the existing volume and SQL timeouts; serial regression passes 238 integration cases with zero setup errors, while two unavailable-MinIO failures remain.

- Verify real CLI hard-stop/replacement and durable lease recovery with isolated synthetic fixtures. Use importable shared tasks and child initialization for the M4 macOS spawn path; preserve native process safety and ordinary worker limits.

- Add cancellable signed local object reads with total deadlines, shared chunk integrity checks and async attachment closure tests (FR-ID-006, NFR-SEC-001/002). Real loopback dribbling TCP cancellation passes.
- Test isolated owner queue/status/attachment routes, frozen retry, expiry and old synchronous `EXPORT_FILE_REQUIRED` compatibility. Define separate export tasks with hard-limit envelopes and minimized correlation logging; application activation remains gated.
- Include owned job/copy counts in advisory deletion inventory without exposing grants or enabling deletion.

- Prepare an exact-length attachment response with cancellation/closure tests; add consent-withdrawn privacy access, recent-auth expiry, transfer deadline and real Redis TTL tests. All routes remain disabled pending complete lifecycle acceptance.
- Add bounded database-scoped cleanup progress with a one-hour Redis TTL, safe restart on lost/malformed state and closed failure counts (FR-ID-006, FR-OPS-002, NFR-SEC-002). Thirteen deterministic cursor cases pass; scheduler/transport acceptance remains pending.

- Resolve the ADR-048 implementation contract and begin additive job/generation constraints and closed status types for FR-ID-006. No route or worker is enabled; the lifecycle remains unaccepted until the consuming implementation and acceptance tests pass.

## 9 October 2026 — verified private MinIO export adapter

- Reuse the approved local storage boundary for exact UUID-keyed encrypted chunks (FR-ID-006, NFR-SEC-001/002, NFR-MNT-001). Bound reads before allocation; verify lengths and always release responses.
- Add 24 fake-provider cases, an owned synthetic MinIO round trip/private-access test and `make test-export-storage`. Native MinIO remains unavailable; hosted CI 37962081120 passed 721 Python and 66 browser cases plus full recovery/security/container gates. Promoted `bb2f4eb` to main and removed its completed branch.
- Record ADR-048 as an unaccepted lifecycle proposal. No learner route, worker publication, new retention rule or cleanup policy is enabled.
- Record successful promotion of encoder `a485bb6` (657 Python/66 browser cases, CI 37949902270) and artifact format `8c08890` (696 Python/66 browser cases, CI 37950849215), with full recovery/security/container gates and branch cleanup.

## 9 October 2026 — verified private export artifact boundary

- Add ADR-047 and an internal authenticated chunk/manifest format for FR-ID-006 and NFR-SEC-001/002/MNT-001. Bind request, generation and ordinal; verify per-chunk and whole-file integrity before the final bytes.
- Bound plaintext chunks, ciphertext, total size and manifests; sanitize callback/cipher errors and close cancelled sources. Add fake-storage corruption, boundary, cancellation and projection round-trip tests.
- No learner route, worker publication, new provider or retention change. Existing synchronous caps remain unchanged; the artifact lifecycle is still pending.

## 9 October 2026 — verified incremental bounded export encoding

- Enforce the existing 2 MiB complete-envelope cap during allowlisted projection (FR-ID-006, NFR-SEC-001/002, NFR-MNT-001), stopping reads before an oversized history is fully hydrated.
- Bound collected encoding chunks to 16 KiB; retain exact row accounting, diagnostic sealing, atomic completion, encrypted retry compatibility and existing expiry. JSON member order may differ in new stored artifacts; v1 values/schema and old retry bytes remain unchanged.
- Add codec, exact-cap, cancellation, early-hydration and legacy retry tests. No new ADR, API, migration, provider or asynchronous large-history delivery. Acceptance is recorded in the export encoding report.

## 9 October 2026 — verified objective HTTP load baseline

- Add a local-only temporary-database profile for NFR-PERF-001/002 and NFR-SCL-001: 2,000 synthetic registrations, 500 active learners, 50 concurrent journeys, 288 original fixtures and paced objective answers.
- Report real HTTP percentiles, errors, completion, pacing and scoped resource evidence; preserve all application limits and strict latency gates.
- Add cleanup/isolation/metrics tests and strict typing. Runtime acceptance and broader history/provider/deployment scenarios remain pending.
- The initial run exposed 653 ms session-start p95 despite a 30 ms mixed p95. Require operation-specific latency gates and implement ADR-046 shared immutable-content locks plus focused topic selection; database concurrency/recheck tests pass, fresh load/full regression pending.
- Batch final plan eligibility/locking and bound manual candidate work. Final native baseline passes: 7,000 requests, zero errors, 500 sessions/2,500 grades, START p95 441 ms and answer p95 27 ms at 19.996 answer dispatches/s. Hosted CI 37933227560 passed 646 Python, 66 browser, five tooling and one isolated UI case plus full recovery/security/container gates; promoted `f2dbf8a` and removed its branch.

## 9 October 2026 — verified narrow learner journey

- Add NFR-ACC-001/NFR-COMP-001 coverage at 320 CSS pixels with touch enabled: onboarding, five-question practice, durable resume, feedback, progress and history.
- Check horizontal reflow, actual key touch-target dimensions and axe results; include the journey in all three existing engine runs and add `make test-web-mobile` for focused verification.
- Hosted CI 37925290651 passed 66 real-API browser executions, 621 Python, five tooling and one isolated UI case, plus full recovery/security/container gates. Promoted `83c6102` and removed its branch. This is emulated viewport evidence, not physical Android or branded Safari acceptance.

## 9 October 2026 — verified exact accountability-record holds

- Add FLAG_HISTORY and DATA_REQUEST_REVIEW under ADR-045 (FR-ID-006, BR-010, FR-OPS-003, NFR-SEC-002), using immutable parent ownership and exact primary-key references.
- Add migration 0024, strict generated contracts, administrator options and SQL DELETE protection; preserve normal triage, immutable evidence, finite decisions and disabled deletion.
- Hosted CI 37924489562 passed 621 Python, five tooling, 63 real-API browser and one isolated UI case, including migration/recovery, role/security and container smoke. Promoted `ce9d9f3` to main and removed its branch locally/remotely. Native focused cases pass; unavailable native storage remains separate.

## 9 October 2026 — verified MinIO download recovery

- Add at most three dependency-download attempts and terminal Go module verification after native network EOFs (NFR-MNT-001).
- Reuse locked module/build caches for the unchanged ADR-019 source/compiler/base pins; verify and compile within one build step.
- Hosted CI 37923437046 passed 615 Python, five tooling, 63 browser and one isolated UI test, actual service/seed, recovery, security scans and container smoke. Promoted `04de7ea` to main and removed its branch locally/remotely; native module downloads remain incomplete.

## 9 October 2026 — verified bounded export projection

Hosted CI [37918757085](https://github.com/Jotham566/kasoma/actions/runs/37918757085)
passed at `8c14590`: 427 unit/contract plus 184 integration tests (611 Python), five tooling tests,
63 real-API browser executions and one isolated editor test. Clean setup/migrations/seed, focused
rubric/role checks, lint/format/types/contracts/build, security/source/image scans and container smoke
passed. Recovery restored 54 tables/272 synthetic rows in 385 ms with pgvector/immutable guards and
no cleanup failures. Cold transfer was 191501/194260/193634 bytes, below 250000 for all engines.
The implementation is on main and its completed branch is removed locally and remotely.

- Native migrations, focused rubric/export tests, recovery, role and security checks pass. Full native integration has one unavailable-storage failure; MinIO/Playwright downloads encountered network interruptions.
- Record the asynchronous export design proposal and the next verified dependency-download resilience work; neither enables new learner scoring or large-history delivery.

## 9 October 2026 — bounded personal-export reads

- Replace retained ORM lookup collections with batched reads and owner-filtered SQL joins/subqueries (FR-ID-006, NFR-SEC-001/002, NFR-MNT-001).
- Preserve diagnostic sealing, exact related-row accounting, all-or-nothing synchronous limits and existing authorization/retention. No API, migration or architecture change.
- Add synthetic memory/batch, exact-cap and cursor-cleanup regressions plus focused database commands. Eight rubric and eleven focused export cases pass natively; full hosted acceptance is recorded above. Async large-history delivery is separate.

## 9 October 2026 — verified rubric, telemetry and dependency release

Hosted CI [37914864557](https://github.com/Jotham566/kasoma/actions/runs/37914864557)
passed at `ed7d7d5`: 427 unit/contract and 182 integration tests (609 Python total), five tooling
tests, 63 real-API browser journeys across Chromium/Firefox/WebKit and one isolated editor UI test.
Clean setup/migrations/seed, eight focused rubric cases, restricted-login verification,
lint/format/types/contracts/build, dependency/source/image security checks and container smoke all
passed. The isolated logical recovery restored 54 tables/272 synthetic rows in 455 ms and verified
pgvector/immutable guards; this is not production PITR/RPO/RTO evidence. Cold question transfers
were 191529/194251/193635 bytes, each below 250000. Commit `ed7d7d5` is on main; both completed
rubric/telemetry branches were deleted locally and remotely.

- Correct legacy JSON/JSONB rubric comparisons and remounted textarea label associations, with exact save/reload regressions.
- Patch runtime Next.js to 16.3.8 and affected Sharp/source-map-js to 0.35.5/1.2.2; retain ADR-031 lint tooling.
- Document the macOS Docker CLI PATH fix after daemon availability returned; native image builds/checks are still pending.
- Record FR-ID-006 large-history export readiness and the next bounded projection slice. No new architectural decision or learner-scoring enablement.

## 9 October 2026 — synthetic model-call telemetry

- Instrument the existing fake short-text rehearsal with correlated, closed per-call and outcome events (NFR-OBS-001, FR-OPS-002; AI gateway specification).
- Record bounded metadata, elapsed time and provider-reported usage; failures report unknown usage and omit provider diagnostics. Use disposable per-rehearsal HMAC fingerprints instead of stable answer hashes.
- Add privacy/schema/correlation/repair/failure tests. No live inference, learner scoring, cost estimate or aggregate dashboard acceptance is enabled.

## 9 October 2026 — reviewed rubric authoring

- Add version-pinned rubric/criterion persistence and independent short-text content review (FR-CNT-001–004, FR-GRD-003/004, NFR-SEC-002; ADR-044).
- Preserve legacy document hashes and request retries; require complete matching criteria before review and freeze normalized material with its item version.
- Add staff author/reviewer forms, generated contracts, SQL assignment exclusion and synthetic regression cases. Learner short-text delivery and model scoring remain disabled.
- Complete hosted acceptance is recorded below; learner scoring remains a separate gate.

## 9 October 2026 — verified holds, expiry and rubric context

- Promote `64394ac` after CI 37228984415: 587 Python (413 unit/contract, 174 integration), 60 browser and five tooling checks, clean migrations/recovery/security/container gates.
- This includes restricted-login permission verification, ADR-043 learning-record holds and bounded authentication expiry, also verified by CI 37228338121. Remove their four completed branches.
- The earlier missing users-row lock grant is fixed and verified. Production grants, full retention/erasure and academic grading approval remain open.

## 4 October 2026 — explicit synthetic rubric material

- Require criterion text, acceptable evidence, common errors and prohibited inferences in the offline short-text context (FR-GRD-003/004; specified rubric fields).
- Bound and redact criterion material, preserve explicit empty error/inference lists, and version both fake rehearsal prompts as v2.
- Add 13 context/privacy cases and verify both independent passes receive the complete rubric. Local 413 unit/contract checks pass; persistence, academic approval and learner scoring remain pending. No architecture or API change.

## 4 October 2026 — verified API timing

- Promote `74a4a8f` after CI 37226011029 passes 556 Python, 60 browser and five tooling checks, clean migration/recovery, security and container gates.
- Remove the completed request-timing branch; aggregated latency and load acceptance remain pending.

## 4 October 2026 — bounded ephemeral authentication expiry

- Move existing expired OTP/rate-bucket cleanup out of login requests into a bounded worker task every 60 seconds (FR-ID-001, security retention specification, NFR-OBS-001).
- Lock rate buckets before loading/refreshing them so concurrent cleanup cannot invalidate a request; skip locked rows and retain active windows.
- Add batch/boundary/concurrency/rollback/redaction tests and a closed count-only event schema. Preserve OTP validity, consent, sessions, learning and accountability evidence. No migration, provider or architectural change.

## 4 October 2026 — individual learning-record holds

- Extend FR-ID-006/BR-010 preservation to grades, mastery evidence and mastery history under ADR-043; keep independent recent-OTP ADMIN claim, finite exact-record decisions and immutable audit receipts.
- Add migration 0022 ownership/DELETE guards and generated API/client enums; clarify grade attempt references and seven supported types in the administrator UI.
- Add ownership, direct-SQL, release/expiry, immutable-evidence and export-boundary tests. Deletion remains disabled and hold coverage remains incomplete.

## 4 October 2026 — restricted assessment login verification

- Add a real temporary PostgreSQL login test for NFR-SEC-002: synthetic objective assessment and idempotent mastery recording with narrowly enumerated writes.
- Check schema changes, trigger bypass, evidence rewrites, role escalation and password-catalog reads are denied; remove only the generated role after each test.
- Add `make test-runtime-role` and update repository status/runbook. Local lint/types/contracts and 394 unit checks pass; native PostgreSQL is unavailable and hosted database acceptance is pending.
- Default application credentials remain unchanged; this is assessment-path verification, not production role provisioning or complete grant coverage. No architecture change.

## 4 October 2026 — verified recovery, browser engines and cold transfer

- Promote recovery `42a6e08` after CI 37223872075: 550 Python/20 browser/five tooling checks and a verified 52-table, 270-row synthetic restore with clean cleanup.
- Promote browser/transfer `96a16d0` after CI 37224172033: 550 Python/60 browser/five tooling checks, all security/container gates, and cold transfer of 191389–194127 bytes against 250000.
- Remove both completed branches. Production PITR/RPO/RTO, branded/mobile/browser-version and real-network gates remain open.

## 4 October 2026 — minimized API response-start timing

- Add monotonic response-start milliseconds to correlated API logs and spans (NFR-OBS-001/FR-OPS-002), including safe error paths.
- Extend the event schema additively; preserve worker events and omit URLs, query parameters, identities, credentials and payloads.
- Add six deterministic timing/redaction/compatibility cases. This is instrumentation, not aggregated p95 or load/SLO acceptance. No architectural decision changes.

## 4 October 2026 — browser engine regression matrix

- Add a cold-context first-question transfer assertion (NFR-BW-001), counting encoded bodies and headers against 250,000 bytes; runtime measurements remain pending.
- Extend `make e2e` to sequential Chromium, Firefox and WebKit runs with fresh synthetic fixtures per shard (NFR-COMP-001/NFR-ACC-001).
- Add prescribed engine install/list/focused commands and CI coverage; preserve all existing assertions. No application architecture change.
- Lint/types/contracts and three 20-case inventories pass; native execution fails at database setup, so 60 browser executions remain pending hosted verification. Branded/mobile/version coverage remains a release gate.

## 4 October 2026 — isolated synthetic recovery drill

- Add `make recovery-drill`, original synthetic assessment fixtures and a hosted CI recovery gate for NFR-REL-002.
- Restore only into a fresh database created by the drill; compare every table inventory, pgvector and selected immutable guards; never overwrite or copy the developer database.
- Fix the first hosted inventory check to use ORM table names, including `consent_records`; failed-run temporary database cleanup succeeded.
- Add ADR-042, 16 profile/cleanup contract cases and a runbook. Native database creation is unavailable; hosted restore acceptance and production PITR/RPO/RTO remain pending.

## 4 October 2026 — verified local channel operations

- Promote `34950b0` to main after full CI 37221185319: 479 Python, 20 browser and five tooling checks plus clean migrations, security scans and container smoke.
- Verify bounded ADMIN channel queues/status cohorts, sampled fake-feedback dispatch timing and configurable alerts (FR-OPS-002/004, NFR-OBS-001). Remove the completed branch.
- Synthetic fake acceptance timings do not establish production delivery or performance SLOs.

## 4 October 2026 — budgeted fake short-text rehearsal

- Add independent rubric passes, one global schema repair and bounded request/token/deadline handling through the existing ModelGateway (FR-GRD-003/004/005).
- Extend FakeModelProvider with deterministic candidate/exception fixtures; failures remain payload-free and agreement never enables learner scoring.
- Record ADR-041 and 15 new tests; local lint/types/contracts and 372 unit/contract plus five tooling checks pass. Hosted regression and academic/learner integration gates remain pending.

## 4 October 2026 — verified five-question WhatsApp conversations

- Promote `5063528` to main after full hosted CI 37220225176: 469 Python, 20 browser and five tooling checks plus clean migrations/security/container gates.
- Verify signed reply-bound practice, shared objective scoring/mastery, safe feedback, STOP/expiry, concurrent duplicate protection and broker-outage recovery.
- Remove the completed conversation branch. Production and academic acceptance remain gated.

## 4 October 2026 — synthetic short-text validation foundation

- Add strict version-pinned rubric candidate validation for FR-GRD-003/004/005, with 40 deterministic contract cases and ADR-040.
- Reject malformed/coerced output, unsupported evidence/context and caller safety flags; return candidates only, never learner scores.
- Local formatting/lint/types/contracts and 357 unit/contract plus five tooling checks pass. Academic calibration, gateway orchestration and learner integration remain pending.

## 3 October 2026 — verified local WhatsApp linking

- Add migration 0018, recent-auth/current-consent single-use codes and owner status/unlink (FR-WA-001/006).
- Add bounded signed durable webhook intake, atomic deduplication and immediate STOP barriers (FR-WA-004 foundation).
- Add transactional processing, fake delivery, bounded retries, configurable limits and transient expiry.
- Include owned channel records in exports and deletion previews; channel hold coverage remains pending.
- Add generated contracts, channel UI, local simulator, messaging worker and ADR-034.
- Commit `23da19c` passes full hosted CI: 395 Python, 20 browser and five tooling tests; setup/migrations/seed, lint/types/contracts/build and security/container gates pass.
- Record the native Docker interruption separately; no reset or weakened gate. Five-question practice and production messaging remain pending.

## 3 October 2026 — local operations visibility

- Publish bounded draft imports as `5bdd122` and remove the completed branch.
- Add ADMIN-only operational snapshots, bounded queue/flag counts, worker heartbeat and configurable threshold alerts (FR-OPS-002 partial).
- Add local periodic monitoring and safe alert logs; distinguish unavailable instrumentation from measured zeros. No external notification delivery.
- Fix cross-application Celery settings reuse with application-local task registration and regressions for monitoring/imports/export expiry.
- Record ADR-033, generated contracts, configuration/runbook and regression/browser coverage. Full hosted CI passes: 360 Python, 19 browser and five tooling tests plus all setup/migration/build/security/container gates.
- Publish `7218898` to main and remove the completed operations branch.


## 3 October 2026 — bounded synthetic draft imports

- Publish legal holds (`ec53ac4`) and lint security (`b766266`) to main after full hosted CI passed; remove completed branches.
- Add 1–20-record, 64 KiB synthetic JSON author imports (FR-CNT-001), source locators, owner-only status and draft links.
- Add migration 0017 and PostgreSQL-backed import commands, atomic draft creation, duplicate reporting, author rechecks and bounded retries/expiry.
- Preserve independent academic review, audit/outbox and synthetic-only eligibility. Add ADR-032, contracts, API/browser/worker tests and `make process-imports`.
- Add an explicit release-evidence register for missing academic, privacy and provider approvals.
- Docker recovered; all 347 Python, 18 browser and five tooling tests pass, alongside clean migrations/seed, lint/types/contracts/build, security scans and container smoke. Initial browser-selector failure was corrected; no final failed checks.

## 3 October 2026 — lint dependency security remediation

- Commit record legal holds as `ec53ac4` (FR-ID-006, BR-010); publication follows security verification.
- Remove the newly audited vulnerable braces dependency from Next lint tooling through
  a scoped tinyglobby override and pinned directory-discovery compatibility patch.
- Add actual-plugin glob/deep-pattern and lint-rule regressions to `make test-tooling`
  and `make test-unit`; add pinned-runtime `make deps-lock` for dependency maintenance.
- Record ADR-031; keep audit severity and all lint rules unchanged.
- Docker startup currently requires a macOS administrator prompt, blocking local
  database/container verification. Prior legal-hold integration/browser evidence is retained.

## 30 September 2026 — specific-record legal holds (local implementation)

- Deletion-impact preview committed and pushed to main as `6f7f210`; completed branch removed.
- Add recent-OTP independent ADMIN claimant controls for finite holds on owned consent,
  attempt, content-flag and data-request records, with opaque decision references.
- Add migration 0016, immutable scope, one-time release, atomic audit/outbox evidence,
  bounded read/write rates, retry receipts and active-hold DELETE guards.
- Add administrator create/list/release controls, generated contracts and SQL/API/browser
  tests for ownership, retries, expiry, rollback and preservation.
- Show active registered holds in the deletion preview while retaining incomplete-coverage
  and execution blockers. Exclude internal hold metadata/events from learner exports.
- Fix an initial-session-check race that could overwrite onboarding action errors; keep
  actions disabled until initialization settles and add a delayed-response browser regression.
- Record [ADR-030](docs/decisions/ADR/030-record-legal-holds.md), update sprint, traceability,
  API/data/runbook and [verification](docs/implementation/E8_LEGAL_HOLDS_VERIFICATION.md).
  This does not implement erasure, universal hold coverage or retention expiry.

## 29 September 2026 — deletion-impact preview (local implementation)

- Owned exports committed and pushed to main as `d20c344`; completed branch removed.
- Add a recent-OTP, independent-claimant ADMIN preview of linked record counts and
  retention/review categories for pending deletion requests, with audited access.
- Bound per-source counts, account for unbound login challenges and related staff
  provenance, and exclude another learner's bound guardian challenges from hash matching.
- Show unresolved legal-hold, erasure and anonymization gates explicitly. Preview does
  not decrypt personal records, revoke access, change data or authorize deletion.
- Add API/generated contracts, administrator UI and regression tests; no migration.
- Correct owner exports to decrypt the display name instead of returning its storage ciphertext;
  add a profiled-learner regression. Deletion previews still never decrypt personal data.
- Update [ADR-029](docs/decisions/ADR/029-deletion-impact-preview.md), sprint,
  traceability, API/data/runbook and [verification](docs/implementation/E8_DELETION_PREVIEW_VERIFICATION.md).

## 29 September 2026 — owned data exports (local implementation)

- Data-request intake committed and pushed to main as `68146b9`; completed branch removed.
- Add recent-OTP owner-only JSON exports with explicit field projections, diagnostic
  sealing, encrypted frozen retries, atomic completion and six-year retention deadlines.
- Add migration 0015, 24-hour download expiry, a bounded five-minute worker sweep and
  `make expire-exports`; expired copies are removed without deleting request evidence.
- Add learner download/retry UI, generated contracts and API/SQL/browser regressions.
- Record [ADR-028](docs/decisions/ADR/028-owned-data-exports.md) and update sprint,
  traceability, API/data/runbook and [verification](docs/implementation/E8_DATA_EXPORTS_VERIFICATION.md).
- Deletion/anonymization, large-history exports and accountability-retention/legal-hold
  processing remain pending; this does not establish production privacy acceptance.

## 29 September 2026 — data-request intake (local implementation)

- Multiple-choice support committed and pushed to main as `02f96bc`; completed branch removed.
- Add recent-OTP export/deletion request intake, owned status and safe acknowledgement,
  including after learning-consent withdrawal and before profile completion.
- Add an independent ADMIN review queue/claim, atomic audits/outbox, deduplicated retries,
  immutable evidence and explicit six-year-after-completion retention policy.
- Add migration 0014, generated contracts, learner/admin screens and regression tests.
- Forward request pagination through the web gateway and install repository-local Corepack
  shims so nested build tasks retain pinned pnpm despite unrelated global installations.
- Update ADR-027, API/data/runbook documentation, sprint and traceability; see
  [verification](docs/implementation/E8_DATA_REQUESTS_VERIFICATION.md). Fulfillment,
  completion evidence, deletion/anonymization and retention jobs remain pending.

## 28 September 2026 — deterministic multiple choice (local implementation)

- Flags/triage committed and pushed to main as `bd9dae3`; completed branch removed.
- Add reviewed multiple-choice keys, exact-set scoring and checkbox delivery through
  shared revision, diagnostic and reassessment paths. Preserve hint/evidence controls.
- Canonicalize selection order for idempotent retries; reject duplicate/unknown IDs.
- Add additive migration 0013, generated contracts, synthetic fixtures and tests.
- Run browser tests in two fresh isolated shards to retain the production OTP peer limit.
- Update ADR-026, API/data/runbook documentation, sprint and traceability; see
  [verification](docs/implementation/E4_MULTIPLE_CHOICE_VERIFICATION.md). Academic
  content approval, short-text benchmark and production deployment remain gated.

## 28 September 2026 — learner flags and triage (local implementation)

- Progress/history committed and pushed to main as `df855ab`; completed branch removed.
- Add owned attempt-bound reports, encrypted optional comments, safe receipt recovery,
  rate limits and exact retry handling across browser interruption/reload.
- Add reviewer/admin queue, independent self-assignment, priorities, revision-checked
  resolution/reopening and atomic audit/history/outbox records.
- Preserve grades, mastery and sealed diagnostics; require two reviewers for disputed
  successor content. Migrations 0011–0012 are additive and enforce the approved retention due date.
- Add ADR-025, generated contracts, tests, traceability and
  [verification](docs/implementation/E8_FLAGS_VERIFICATION.md). Production support,
  retention jobs, safeguarding/legal approval and academic calibration remain gated.

## 28 September 2026 — progress and session history (local implementation)

- Unseen reassessment committed and pushed to main as `73c1fba`; completed branch removed.
- Add consent-aware subject/topic/competency progress with evidence confidence, coverage
  and guarded recent-change text; unfinished diagnostic evidence remains sealed.
- Add owned, cursor-paginated session history with resume/review and Kampala timestamps.
- Add ADR-024, generated contracts, regression tests and documentation; no new migration.
- See [verification](docs/implementation/E6_PROGRESS_VERIFICATION.md). Academic calibration
  and production acceptance remain separate gates.

## 28 September 2026 — unseen reassessment (local implementation)

- Reviewed hints committed and pushed to main as `3c0c3ba`; hosted CI passed and completed branch removed.
- Add reviewed equivalent-version claims with independent review of both sides.
- Add one-item unseen reassessment, same-skill/difficulty fallback, conservative clone
  exclusion, durable source linkage and replayable selection evidence.
- Reuse the shared player/grader/mastery service; preserve the original result and
  record separate independent evidence with safe lifecycle events.
- Add migration 0010, generated contracts, synthetic fixtures and regression coverage.
- See [verification](docs/implementation/E4_REASSESSMENT_VERIFICATION.md). Academic
  transfer validity, calibrated resolution criteria and production gates remain pending.

## 28 September 2026 — reviewed revision hints (local implementation)

- Recommended practice merged to main as `88dd880`; hosted CI passed and its branch was removed.
- Add authored/reviewed progressive hints, durable disclosure and safe retry/resume.
- Freeze pre-answer usage and highest level for mastery independence weighting;
  post-answer remediation preserves original grading/evidence and diagnostics block hints.
- Add migration 0009, generated contracts, synthetic fixtures and API/browser tests.
- Require changelog, sprint, traceability and relevant verification/runbook updates
  alongside each implementation change in `AGENTS.md`.
- See [verification evidence](docs/implementation/E4_HINTS_VERIFICATION.md); production
  academic/privacy gates and unseen reassessment remain pending.

## E5 recommended practice (local synthetic verification)

- Versioned synthetic ranking, prerequisite redirection and immutable replay snapshots.
- Explained home recommendation and resumable 5–10-item recommended plans.
- Shared reservation exclusion for manual and adaptive practice.

- E2: synthetic single-choice authoring, independent review, version immutability,
  role checks and append-only content audit, with migration and browser/API tests.

- E1: local OTP identity, protected learner profiles, rotating sessions and separate
  guardian-consent/learner-assent flows with migration, contracts and tests.

Record meaningful repository and product changes here. A documentation baseline is not an application release.

## Unreleased

### Changed

- Moved product documents to `docs/product/` and the engineering pack to `docs/specifications/`.
- Renamed the software requirements document to `01_SRD.md` and updated references.
- Expanded root engineering instructions while preserving the approved source-of-truth hierarchy.

### Added

- E0 local runtime foundation, locked toolchains, health contract/client, migration,
  synthetic fixtures, provider boundaries, tests and initial CI (verification in current sprint).
- Phase 0 assessment and ADR-013 for delegated bootstrap choices.

- ADR navigation, current sprint and implementation traceability for all 61 SRD requirements.
- Workspace directory scaffolding, a safe environment example and a reserved Compose file.
- Make targets for documentation validation and explicit errors for pending runtime commands.

## 2026-09-22 — Initial specification baseline

- Product whitepaper, roadmap and engineering specification pack.
- README, contributor guidance, agent instructions, pull request template and Git/editor conventions.

### E3 first assessment slice

- Add consent-aware topic practice, approved version selection, immutable attempts,
  deterministic single-choice grades, solution gating and transactional result events.
- Add learner resume/retry UI, synthetic fixture command and ADR-016.
- E2 `b5cfd75` pushed to main; hosted CI passed and completed E1/E2 branches removed.

### E4 numeric grading and readiness

- Merge E3 `22773fd`, verify hosted CI and remove its completed branch.
- Resolve difficulty-label mapping and Week 5/6 sequencing in ADR-017 without
  changing published content or weakening quality gates.
- Add numeric authoring/review, safe learner input, exact rational grading,
  units/tolerance/precision policy, immutable response storage and regression tests.

## 28 September 2026 — diagnostic and initial mastery

- E4 numeric grading and the pinned MinIO source-build CI repair merged to main.
- Added synthetic resumable subject diagnostics with hidden in-session grades.
- Added immutable mastery evidence, baseline estimates/history and offline replay.
- Added generated contracts, browser results, migration and regression evidence.
- Full adaptive recommendation factors and academic calibration remain pending.

### Verified — shared assessment transactions (FR-WA-003/004)

- Extract internal actor-authorized start/serve/submit methods while preserving web contracts.
- Keep deterministic grading, mastery, receipts and outbox events in the caller transaction.
- Add rollback/committed-retry and current account/consent/enrollment/ownership regressions.
- Record ADR-035. Commit `50044d4` passed hosted CI 37149982356: 398 Python, 20 browser
  and five tooling tests, including clean migrations and security/container gates; published to main.

### In progress — objective channel formatting (FR-WA-002/003/005)

- Add explicit WHATSAPP suitability and bounded plain-text question rendering.
- Normalize numbered choice/multiple-choice and exact numeric replies into shared contracts.
- Record ADR-036 and add key-leakage, malformed-response, length and shared-grader regressions.
- Question/reply binding and the conversation worker remain pending.

### In progress — channel assessment provenance (FR-WA-002/003/004)

- Record ADR-037 and additive migration 0019 for immutable WHATSAPP attempt provenance.
- Filter supported questions before selection and validate complete five-item plans on continuation.
- Preserve WEB HTTP schemas and receipt hashes; separate internal WHATSAPP fingerprints.
- Add objective score/mastery parity, replay, current approval and database guard regressions.
- Webhook conversation and delivery integration remain pending.

### In progress — concise channel feedback (FR-WA-005)

- Extend ADR-036 with bounded shared-grade feedback and authenticated web solution links.
- Preserve complete academic instructions or use the web fallback; reject secret-bearing origins.
- Add format, length, continuation and link-safety regressions; delivery integration remains pending.

### 4 October 2026 — verified channel assessment foundation

- Publish `c0b5b55` to main after all hosted gates passed: 437 Python, 20 browser and five tooling
  tests, including six channel capability/parity regressions. Remove completed foundation branches.

### In progress — signed local five-question conversation (FR-WA-002–006)

- Record ADR-038; add migration 0020 for expiring link-revision-bound conversation pointers and
  encrypted transient structured replies. Bind numbered menus/answers to the exact sent question.
- Reuse shared atomic assessment operations; reconstruct approved question and grade references
  under current authorization before fake delivery. STOP/unlink clears the channel pointer.
- Add bounded local wake-up after durable intake, transport schemas, exports/inventory and complete
  synthetic flow, replay, withdrawal, STOP, rollback and expiry tests. Hosted verification pending.

- Align local channel instructions and development runbook with exact-reply practice controls.
- Recheck the requested channel on serving/submission so a WHATSAPP-only version cannot be
  answered through WEB simply by resuming its shared session.

### In progress — local channel operations (FR-OPS-002/004)

- Record ADR-039 and add operational indexes in migration 0021.
- Extend minimized ADMIN snapshots with bounded queue/status cohorts, oldest age and sampled
  local fake-dispatch p95; expose no-sample state and sample truncation explicitly.
- Add typed local thresholds, safe alert schema, generated contracts, dashboard and regression tests.
- No production messaging, external notifications or release latency acceptance is implied.

## 4 October 2026 — restricted-login row-lock correction

- Fix the NFR-SEC-002 test grant profile after CI 37227070209 exposed the attempt-hint guard's users-row lock requirement.
- Permit only the existing mutable display_name field; add explicit denied identity/status/birth-date writes and exact column-grant cleanup. Production credentials remain unchanged; rerun required.

FR-GRD-004/005 and NFR-SEC-002: internal `services/short_text_contracts.py` adds bounded
answer input and distinct pending/neutral outcomes, rejecting scores and hidden/provider
material. ADR-050 remains proposed; runtime routes, worker and privacy integration are
not implemented by these contracts. Verification passes: 699 unit/contract tests (33 new outcome/input cases), 35 tooling
checks, format/lint/types and generated-contract comparison. No HTTP schema changed.

FR-GRD-004/005 / NFR-SEC-002: migration 0026, grading-work models and transactional
storage are under verification. Commands have one claim, bounded expiry and immutable
transition snapshots. No learner/worker path is enabled. Use `make test-grading-work`;
privacy inventory/export/hold coverage and restricted-role checks remain integration gates.

Durable-store focused verification passes 24 cases (seven PostgreSQL, 17 transition),
including contention, rollback, expiry, publication consistency and owned/foreign
export projection. Work/history counts are in deletion inventory. Full backend
regression is running; exact-record holds and restricted-role extension still gate
runtime enablement. See `docs/implementation/E4_DURABLE_GRADING_VERIFICATION.md`.

FR-ID-006 / BR-010 / NFR-SEC-002: migration 0027 and the existing hold service now
support exact immutable grading-history records, preserving ownership and independent
review. The administrator selector/generated contracts include GRADING_HISTORY;
incomplete-coverage wording no longer reports a stale record count. Focused integration
and three-engine privacy verification are pending; learner grading remains disabled.

Durable grading/history local evidence: 26 focused cases and six privacy browser
executions pass across Chromium/Firefox/WebKit. Populated isolated recovery passes
(58 tables, 291 rows, 948 ms) with immutable grading snapshots. Container refresh and
both smoke probes pass. Bandit found a runtime assert in the earlier workflow helper;
explicit validation replaces it and Bandit passes. Full backend/final security checks
remain active; see `docs/implementation/E4_DURABLE_GRADING_VERIFICATION.md`.

Durable grading/history local gate now passes: full migration/backend run has 747
unit/contract, 35 tooling and 266 integration cases; two additional history-hold cases
and the extended restricted-login check pass separately. Six three-engine privacy
journeys, populated logical recovery, source/dependency checks, final rebuilt image
scans and eight-service smoke pass. Exact-head hosted acceptance remains required;
worker/learner/scoring integration is still disabled.
