# Requirements Traceability

Grading-operations candidate: FR-OPS-002, NFR-OBS-001, NFR-SEC-002 and NFR-ACC/COMP-001 add bounded
ADMIN queue/lease/terminal/pending-audit/disabled-band counts and a typed stale-age
alert under ADR-053. Actual encrypted synthetic transitions and authorization/boundary
checks pass: 26 operational and 33 review cases, 884 unit/contract plus 333 broad
integration cases, 104 browser executions, restricted login/recovery/security/containers.
See [grading evidence](E8_GRADING_OPERATIONS_VERIFICATION.md); hosted acceptance is
pending. Model usage and academic error rate remain unavailable.

Offline reports merged at `17abb2d`: FR-GRD-003/004, FR-OPS-002 and NFR-MNT-001 add a
strict versioned payload-free report reader/comparator and the required `make eval-compare`
command under ADR-052. Thirty-seven new cases, 881 total unit/contract and 35 tooling
cases, lint/types/contracts/security and actual Make invocation pass; see
[report evidence](E4_EVALUATION_REPORT_VERIFICATION.md). Complete hosted run 39151730479 passes. It does not run
inference, establish benchmark truth/approval or enable a learner grading band.

Staff mobile navigation merged at `17abb2d`: NFR-ACC-001/NFR-COMP-001 uses the existing
staff destinations with an explicit narrow-screen disclosure, keyboard activation,
active destination, >=44-pixel controls and close-on-navigation. Desktop navigation
remains visible. Lint/build/contracts, two UI harness and 102 three-engine executions,
including 200% text, pass; final rebuilt container/source checks pass. See
[navigation evidence](E6_STAFF_NAVIGATION_VERIFICATION.md). The complete later report-source hosted run passes; the navigation-only diagnostic save-ack race is retained and corrected in the active follow-up.

Independent review merged at `2164209`: FR-GRD-003/004/005, FR-ID-003/006 and NFR-SEC-002 are
addressed by migration 0033, `services/grading_reviews.py`, blinded staff routes/UI,
release-unit sampling, immutable complete-rubric reviews, sticky rolling disablement,
owned export/inventory/hold integration and per-pass processor rechecks. See
[expert-review verification](E4_EXPERT_REVIEW_VERIFICATION.md) for executed evidence
and complete hosted run 39150319607. The completion-clock cap is a separate active follow-up.
This does not replace academic/provider/privacy release
approval or enable ordinary learner short-text scoring.

Live implementation evidence for every requirement in the [SRD](../specifications/01_SRD.md). The [specification matrix](../specifications/14_Requirements_Traceability_Matrix.md) defines required coverage and evidence. Update this register with each implementation slice; completion requires passing acceptance evidence.

E0 through E6 synthetic learning and E8 learner-flag evidence is recorded below. Local synthetic journeys are not
production-pilot acceptance; delivery-provider and legal approval gates remain. See the [assessment](PHASE_0_ASSESSMENT.md).

| Requirement | Implementation | Tests / evidence | Status |
| --- | --- | --- | --- |
| FR-ID-001 | Email/phone OTP, purpose binding, five-attempt/ten-minute limits, per-contact/peer/device sends; initial UI check serializes sign-in actions | `tests/integration/test_identity.py`, `tests/e2e/identity.spec.ts` | Local implemented; SES/SMS production gates pending |
| FR-ID-002 | Verified identifier linking with uniqueness, encryption and keyed lookup; existing identities never auto-merge | API linking, collision and one-identity tests | Local implemented |
| FR-ID-003 | Birth date, adult consent, separately verified guardian evidence/learner assent, withdrawal, policy gate | Minor/adult API and browser tests; ownership, idempotency and policy-change tests | Local implemented, including channel issue/consume/delivery consent checks; approved wording remains pending |
| FR-ID-004 | Server-restricted S4 Mathematics/Physics profile and subject selection | Profile validation and browser journeys | Local implemented |
| FR-ID-005 | Opaque sessions, refresh rotation/reuse revocation, current/all logout | Expiry, family reuse and revocation API tests; browser logout | Local implemented |
| FR-ID-006 | Recent-OTP intake/review, encrypted bounded JSON and asynchronous private artifacts with 24-hour copy expiry; deletion preview and exact-record holds | [Export evidence](E8_DATA_EXPORTS_VERIFICATION.md); [hold evidence](E8_LEGAL_HOLDS_VERIFICATION.md); [review privacy candidate](E4_EXPERT_REVIEW_VERIFICATION.md) | Partial: intake/export/async delivery/expiry and advisory deletion preview merged; independent review privacy merged; erasure/anonymization, full hold coverage and accountability expiry pending |
| FR-DIAG-001 | Subject diagnostic start/resume; actor lock and partial unique index | Concurrent start and browser reload tests | Local synthetic implemented |
| FR-DIAG-002 | Versioned 15-item adaptive plan; database bounds 10–15 | Full choice/numeric diagnostics; client count override rejected | Local synthetic implemented; early stop intentionally not configured |
| FR-DIAG-003 | CORE first per available topic; competency coverage and response-dependent difficulty | Three-topic/two-competency coverage; strong/weak trajectories | Local synthetic implemented; academic inventory/mapping approval pending |
| FR-DIAG-004 | Atomic acknowledgement with attempt, grade, mastery and outbox; same-key replay | Lost acknowledgement browser retry, rollback and resume tests | Local implemented |
| FR-DIAG-005 | Frozen skill estimates, uncertainty and first explained topic practice recommendation | Completion API, browser result and recommendation link | Local synthetic implemented; current ranking is available through recommended practice |
| FR-REV-001 | `services/recommendations.py`, shared RECOMMENDED start, frozen plan snapshot | 5/10-item API flows, concurrent start, replay, browser lost-ack retry | Local synthetic implemented; academic calibration pending |
| FR-REV-002 | Topic-selected 5–10-item plans through shared assessment service | Assessment API and browser five-question journey | Local manual focus and synchronous mastery updates implemented |
| FR-REV-003 | Content-owned selector, S4/enrollment checks, current approval and retirement lock | Draft/retired/non-web inventory exclusion; identity subject checks | Local synthetic single/multiple-choice and numeric paths implemented |
| FR-REV-004 | Configurable seven-day served-item exclusion across versions; no silent shortage fallback | Completed plan cannot immediately repeat; insufficient-inventory API tests | Local implemented; reassessment enforces all-time unseen selection; academic ranking calibration pending |
| FR-REV-005 | Durable fixed assignments and answered history; active-plan lookup; lost-ack retry | Concurrent replay, separate browser resume and completion after reload | Local choice/numeric revision and diagnostic resume implemented |
| FR-REV-006 | Versioned reasons, home target/time card, per-item selection reasons and diagnostic action | API safe projection, sparse text, accessible browser practice | Local synthetic implemented |
| FR-GRD-001 | Pinned single-choice and canonical exact-set multiple-choice graders, reviewed keys and checkbox delivery | Exhaustive subset/permutation tests, publication/API/DB/retry/replay/diagnostic/reassessment and browser checks; [verification](E4_MULTIPLE_CHOICE_VERIFICATION.md) | Local deterministic implementation; synthetic evidence is not academic benchmark approval |
| FR-GRD-002 | Reviewed numeric contracts, exact rational grading, unit conversions, inclusive tolerances, precision and accepted forms | `tests/contract/test_numeric.py`, `tests/integration/test_numeric_workflow.py`, `tests/e2e/numeric.spec.ts` | Local deterministic implementation; synthetic regression/property cases are not expert academic benchmark approval |
| FR-GRD-003 | Version-pinned encrypted rubric grades, bounded fake dual-pass processor and disabled synthetic learner flow (ADR-050); independent review candidate (ADR-051) | Flow/API/SQL/role/browser/recovery tests; [review evidence](E4_EXPERT_REVIEW_VERIFICATION.md) | Synthetic learner path, independent review and offline reports merged after hosted acceptance; genuine calibration/provider/academic approval and actual scoring remain gated |
| FR-GRD-004 | Distinct pending/neutral outcomes, finite work leases and global request/time/token/repair budget; current consent/band checks and candidate atomic sticky review disablement | Rehearsal, worker rollback/revocation, pending/fallback/retry browser and review window tests | Disabled synthetic fallback and independent review merged after hosted verification; clock-skew follow-up under acceptance and actual scoring approval pending |
| FR-GRD-005 | Authored-feedback allowlists, exact pinned criterion evidence, encrypted result projection and owned rubric feedback; blinded independent review keeps model outcomes hidden | Strict candidate/result contracts, learner and reviewer browser/API cases | Synthetic learner feedback merged; real academic calibration and scoring approval pending |
| FR-GRD-006 | Reviewed versioned hints, append-only usage and frozen pre-answer count/highest level; independence weighting with unchanged points | `tests/contract/test_hint_contract.py`, `tests/integration/test_hints.py`, `tests/e2e/hints.spec.ts`; [verification](E4_HINTS_VERIFICATION.md) | Local synthetic verified (235 Python tests / 12 browser tests); production hint academic review pending |
| FR-GRD-007 | Owned submitted-attempt prerequisite for worked solution; safe learner DTO | Direct pre-attempt denial, IDOR and browser solution gate | Local revision gating and permanent diagnostic solution block implemented |
| FR-GRD-008 | Reviewed equivalence claims and same-primary-skill/difficulty fallback; all-time unseen/clone exclusion; one-item linked session with independent evidence | Reassessment unit/API/browser suites, migration 0010 and `make replay-reassessments`; [verification](E4_REASSESSMENT_VERIFICATION.md) | Local synthetic verified (249 Python tests / 13 browser tests); academic transfer validity and calibrated misconception-resolution criteria pending |
| FR-GRD-009 | Owned attempt/version-bound reporting, encrypted bounded comments, safe receipt recovery | Flag contract/API/browser suites; [verification](E8_FLAGS_VERIFICATION.md) | Local synthetic implementation; current consent and diagnostic sealing enforced |
| FR-MST-001 | Unique append-only attempt/skill evidence; synchronous deterministic grading; consented legacy reconciliation | Duplicate replay, rollback, immutable DB records and integration tests | Local deterministic path implemented |
| FR-MST-002 | Specified weighted prior, score, coverage/recency confidence and display state | Hand calculations, property tests and diagnostic UI | Local implemented |
| FR-MST-003 | Versioned configuration, original inputs, hashes, estimate history and offline replay | make replay-mastery; nonempty current/history replay integration tests | Local implemented; no authenticated admin replay UI yet |
| FR-MST-004 | Evidence-derived subject/topic/competency rollups, coverage, recent change and owned session history | Progress engine/API/browser tests; [verification](E6_PROGRESS_VERIFICATION.md) | Local synthetic implemented; academic aggregation calibration and large-history performance gates pending |
| FR-MST-005 | Confidence/coverage shown throughout progress; numeric mastery hidden below 0.25; unfinished diagnostic evidence excluded | Sparse/established engine tests, sealed diagnostic API/browser checks and axe/keyboard retry | Local diagnostic and general progress implemented; no absolute academic claims |
| FR-MST-006 | `services/recommendation_engine.py`, immutable inputs/configuration/plan snapshots; prerequisite graph from approved synthetic metadata | Factor direction, prerequisite redirection, cycle rejection, bounds, deterministic replay, API/browser flow | Local synthetic implemented; reviewed curriculum importance/graph, scenario metadata and teacher calibration remain release gates |
| FR-WA-001 | `services/whatsapp_linking.py`, migration 0018, owned web channel UI | [E7 evidence](E7_LINKING_READINESS.md); expiry/replay/concurrency, consent/minor and sender-collision tests | Local fake linking verified; production provider/pilot gates remain |
| FR-WA-002 | Shared five-item channel selection; reply-bound menus and conversation pointers | `test_channel_assessment.py`; [conversation evidence](E7_CONVERSATION_VERIFICATION.md) | Local signed five-question conversation verified; production gates remain |
| FR-WA-003 | Shared transactional graders/mastery with immutable channel provenance | [Foundation evidence](E7_SHARED_TRANSACTIONS_VERIFICATION.md); three-format database parity | Local internal and signed webhook parity verified |
| FR-WA-004 | Signed bounded intake, durable message-ID hashes, atomic replay/conflict handling, monotonic status callbacks | [E7 evidence](E7_LINKING_READINESS.md); signature, duplicate/conflict, callback and rollback tests | Local transport and answer/mastery replay invariants verified |
| FR-WA-005 | Bounded question/feedback formatters and authenticated web fallback | `test_whatsapp_format.py`, `test_whatsapp_feedback.py`; [conversation evidence](E7_CONVERSATION_VERIFICATION.md) | Formatting and authorized fake delivery verified; production pending |
| FR-WA-006 | Immediate STOP barrier, owner unlink, fake outbound rechecks | [E7 evidence](E7_LINKING_READINESS.md); STOP before worker/delivery, stale code and retry tests | Local opt-out and transient practice invalidation verified; learning evidence retained |
| FR-CNT-001 | `services/content.py`, strict draft DTO, staff editor; bounded JSON import API/UI and transactional worker | Content tests; import contract/API/browser regressions; [import evidence](E2_IMPORTS_VERIFICATION.md) | Partial: create/edit verified; structured synthetic JSON import verified; other formats and academic release pending |
| FR-CNT-002 | Role checks and immutable author ownership; self-review blocked even with both roles | API self-review denial; SQL review guard; disabled author approval in browser | Local implemented |
| FR-CNT-003 | Return, approval, high-risk/disputed second review, retirement and append-only reviews | Full API/browser workflow; two-reviewer and retired-selection tests | Local implemented with synthetic content |
| FR-CNT-004 | Immutable approved versions, explicit successor drafts, normalized frozen mappings and version-pinned reviewed rubrics | API mutation rejection; direct SQL history/mapping/attempt/rubric tests; retired-version grades/solutions remain unchanged | Choice/numeric provenance and ADR-044 rubric authoring verified; short-text learner attempt integration remains pending |
| FR-CNT-005 | Submission and approval revalidate rights, mappings, weights, answer, solution and remediation | Field-specific 409 tests; approval revalidates changed curriculum references | Local single/multiple-choice and numeric publication validation implemented; other formats and academic evidence pending |
| FR-CNT-006 | Reviewer/admin queue, independent claim, priority/status/resolution, immutable history and revision-checked retries | Triage API/browser, role/ownership, audit/rollback and disputed-successor tests | Local synthetic implementation; approved live support and retention jobs remain production gates |
| FR-OPS-001 | `services/observability.py`, `packages/analytics-schema/` | `tests/contract/test_foundation.py`, `tests/contract/test_identity_contract.py`, identity integration outbox assertions: safe operational and identity-event shape | Registration/consent, assessment, diagnostic start/completion and mastery-update events persist atomically; hint-use and reassessment lifecycle events also persist atomically; flag lifecycle events use the content outbox; data-request intake/review and export completion events also use the identity outbox; channel code/link/unlink/STOP events and safe correlated processing logs are implemented; remaining dispatch pending |
| FR-OPS-002 | ADMIN snapshot/dashboard, bounded imports/flags/channel/exports and response-start histograms; grading queue candidate | [Operations evidence](E8_OPERATIONS_VERIFICATION.md); [grading candidate](E8_GRADING_OPERATIONS_VERIFICATION.md); threshold/recovery, authorization, safe logs and browser checks | Partial: existing local visibility merged; grading queue/lease/fallback observation under acceptance; model spend, academic/technical error-rate distinctions, SMS/email/mastery/provider telemetry and production alerting remain pending |
| FR-OPS-003 | Atomic content/role audit, database history guards | Direct SQL audit rewrite rejection, role-action records and content events | Partial: content/local roles and flag read/triage audit; broader operations audit UI/retention pending |
| FR-OPS-004 | Typed channel attempt/outbound limits and feature flag; short-text per-rehearsal request/token/time/repair budget with finite lease/hard task bounds | [E7 evidence](E7_LINKING_READINESS.md); fake short-text orchestration/worker budget tests | Channel limits and fixed synthetic per-job budget verified; configurable runtime-wide model ceilings and production usage telemetry need assessment before additional policy |
| NFR-PERF-001 | Isolated objective HTTP load runner; ADR-046 shared content locks and batched eligibility | [Load profile evidence](E9_OBJECTIVE_LOAD_VERIFICATION.md) | Local baseline passes per-operation p95 (START 441 ms); hosted regression passes; representative deployment/history/provider acceptance pending |
| NFR-PERF-002 | Bounded local queue wake-up after durable channel intake | Wake-up contract tests; [conversation evidence](E7_CONVERSATION_VERIFICATION.md) | Implementation partial; measured p95 feedback latency gate pending |
| NFR-REL-001 | — | — | Not started |
| NFR-REL-002 | Isolated synthetic logical recovery command (ADR-042) | 16 safety cases; [recovery evidence](E9_RECOVERY_VERIFICATION.md) | Synthetic logical recovery verified in CI 37223872075; production PITR/RPO/RTO pending |
| NFR-SCL-001 | Synthetic 2,000-registration/500-active/50-concurrent objective load profile | [Load profile evidence](E9_OBJECTIVE_LOAD_VERIFICATION.md) | Local 7,000-request baseline passed with 500 sessions/2,500 grades and no errors; broader scale acceptance pending |
| NFR-SEC-001 | `services/config.py`, loopback Compose, generated ignored secrets | Fail-closed/redaction tests; source/dependency scans | Partial; production TLS/encryption pending |
| NFR-SEC-002 | Identity ownership, recent-auth/consent controls and staff content-role enforcement | Identity integration and cross-origin browser tests | Partial; content RBAC implemented; assessment consent/ownership guards verified; production MFA/role governance and future route integration pending |
| NFR-ACC-001 | `apps/web/app`, `packages/ui` | Playwright keyboard retry and axe scan | Shell, onboarding, staff review, assessment, diagnostic, progress/history and flag/triage axe/keyboard checks; remaining journey matrix pending |
| NFR-BW-001 | Cold-context first-question encoded transfer check, including headers/prefetch and no media exclusions for the synthetic fixture | Existing assessment E2E journey; [browser evidence](E9_BROWSER_COVERAGE_VERIFICATION.md) | Synthetic cold transfer verified across three engines: 191389–194127 bytes; media/mobile/latency release checks remain |
| NFR-COMP-001 | Full journey harness for isolated Chromium/Firefox/WebKit runs | [Browser matrix evidence](E9_BROWSER_COVERAGE_VERIFICATION.md), [narrow viewport regression](E9_MOBILE_REFLOW_VERIFICATION.md) | 66 browser executions, including 320-pixel touch journey, verified in CI 37925290651; branded/current-previous/physical mobile acceptance pending |
| NFR-OBS-001 | UUID web/API/worker correlation; console OTel; safe JSON logs; API response-start and synthetic model-call timing | Unit redaction and real worker propagation tests; [model telemetry evidence](E8_MODEL_TELEMETRY_VERIFICATION.md) | Minimized timing verified through hosted CI 37914864557; durable aggregation/domain tracing remains partial |
| NFR-MNT-001 | pnpm/Turbo + uv locks; Alembic; generated client; Make/CI | Setup, lint/types, migration tests, OpenAPI diff, web build/E2E | Full hosted synthetic regression evidence recorded per slice; release acceptance remains separately gated |
| NFR-LOC-001 | English shell; UTC storage/wire; progress/history dates in Africa/Kampala | Configuration and browser history checks | Progress/history presentation implemented; wider localization review pending |

FR-GRD-003/004/005 / FR-MST-001 / FR-ID-006: the 10 October
[short-text readiness update](E4_SHORT_TEXT_INTEGRATION_READINESS.md) records inspected
pending/neutral contract gaps and mandatory beta audit/automatic disablement controls.
This is design-readiness evidence only; learner short-text acceptance remains incomplete.

E4 numeric execution evidence: [verification report](E4_VERIFICATION.md).

NFR-MNT-001: [CI runtime/mirror remediation](E9_CI_RUNTIME_VERIFICATION.md) addresses
an observed whole-job timeout and registry throttling. The disposable-runner cache
configuration preserves existing settings and has isolated tooling regression tests. It does not waive any test
or constitute main/release acceptance; new exact-head hosted verification is required.

FR-ID-006 / NFR-COMP-001 / NFR-MNT-001: hosted run 38004530911 passed startup,
backend and Chromium/Firefox checks but failed three Linux WebKit attachments.
`tests/browser-control/download.spec.ts` adds a successful native attachment control
with exact filename/bytes. All three controls pass on macOS WebKit; Linux diagnosis
and full hosted acceptance remain pending. See [CI evidence](E9_CI_RUNTIME_VERIFICATION.md).

Linux ARM64 comparison reproduces the three control timeouts; explicit HTML download
intent passes the same filename/byte/cancellation/corruption checks. The background
export link adopts that intent, with application regression pending. The documented
`make test-export-download-control-linux` preserves a bounded, isolated reproduction.
The complete native browser matrix now passes 90 executions, including streamed fault
rejection, native frozen retry and recent-owner preflight errors. Rebuilt container
security/health/export/metrics smoke passes; final expired-notice privacy regression
passes all six executions with format/lint/types/build. Exact-head hosted acceptance
remains pending. No release gate is waived.

FR-OPS-002 / NFR-OBS-001 / NFR-SEC-002 / NFR-MNT-001 in progress:
[request aggregation](E8_REQUEST_AGGREGATION_VERIFICATION.md) adds an isolated OTel
histogram component and percentile/property tests under proposed ADR-049. Runtime
components now include bounded Redis expiry/deduplication and a background SDK collector.
Integration is under verification; REQUEST_LATENCY remains unavailable when collection
is absent/stale/invalid, and these requirements
remain partial. No application acceptance is inferred from the component.

E5 diagnostic/mastery evidence: [verification report](E5_VERIFICATION.md).

FR-GRD-003/004 / FR-MST-001 / NFR-SEC-001/002 / NFR-REL-002: migration 0028 and
`services/grading_band_store.py` add immutable global calibration metadata, locked
state and sticky disablement with exact history. Eleven focused PostgreSQL cases,
restricted disable-only worker permissions and populated recovery pass; full regression
passes 279 integration cases. Additive migration 0029 then closes a reproduced
topic-reparenting gap with a composite FK; 13 focused SQL cases, populated upgrade,
restricted login and recovery pass on that correction. Exact-head hosted verification
is pending. [Evidence and remaining runtime/approval gates](E4_BAND_STORAGE_VERIFICATION.md).

FR-GRD-003/004/005 / FR-MST-001 / NFR-SEC-002: the proposed ADR-050 eligibility
component binds calibration evidence and audit state to the exact band/scope/versions.
It rejects insufficient counts, missing approvals, harmful/pending subgroup review,
critical errors, incomplete audit coverage and rolling agreement below 90%.
[Verification and remaining runtime gates](E4_ELIGIBILITY_VERIFICATION.md). This is
not academic approval, durable automatic disablement or learner grading acceptance.
Component checks pass 780 unit/contract and 35 tooling cases, lint/types, generated
contracts and security scans; runtime and approval gates remain open.

E5 recommended practice: [verification report](E5_RECOMMENDATIONS_VERIFICATION.md).

E4 reviewed hints: [verification report](E4_HINTS_VERIFICATION.md).

E4 unseen reassessment: [verification report](E4_REASSESSMENT_VERIFICATION.md).

E6 progress and session history: [verification report](E6_PROGRESS_VERIFICATION.md).

E8 learner flags: [verification report](E8_FLAGS_VERIFICATION.md).

E8 record legal holds: [verification report](E8_LEGAL_HOLDS_VERIFICATION.md), covering
FR-ID-006, BR-010, FR-OPS-003, NFR-SEC-002, NFR-ACC-001 and NFR-MNT-001.
Partial coverage never authorizes account erasure.

E9 lint dependency security remediation (NFR-MNT-001/NFR-SEC-001):
[ADR-031](../decisions/ADR/031-lint-glob-security.md) and
[verification](E9_LINT_SECURITY_VERIFICATION.md). No application acceptance inferred.

### E7 verified local linking (FR-WA-001/004/006, FR-ID-003/006, FR-OPS-001/003/004)

Code `23da19c` and [E7 evidence](E7_LINKING_READINESS.md) record migration 0018, owner routes/UI,
signed durable intake, STOP barriers, transactional processing/fake delivery, expiry and owned
export/deletion inventory. Hosted CI passed 395 Python, 20 browser and five tooling tests plus
all setup/migration/lint/type/contract/build/security/container gates. Native Docker interruption
is recorded separately. FR-WA-002/003/005 practice/grading and production transport remain pending.

### Verified shared-service foundation (FR-WA-002/003/004)

ADR-035 and `tests/integration/test_assessment_transactions.py` cover the verified internal
transaction boundary needed for channel parity. Web behavior, schemas and receipt hashes remain
unchanged. Commit `50044d4` passed hosted CI 37149982356: 398 Python tests, 20 browser and
five tooling checks, including all three new database regressions and the complete release pipeline.
This is not evidence that WhatsApp practice or parity is implemented.

ADR-036 adds an independent channel-formatting boundary and contract regressions toward
FR-WA-002/003/005. This boundary neither chooses approved versions nor binds learner replies;
those integration gates and full channel parity remain pending.

ADR-037, migration 0019 and `tests/integration/test_channel_assessment.py` address internal
FR-WA-002/003/004, FR-CNT-004, FR-GRD-001/002 and FR-MST-001 channel capability/provenance.
The six added parity/database cases passed in CI 37217857047 for `c0b5b55`.
Conversation/reply binding, outbound practice and end-to-end parity remain separate gates.

FR-WA-005: `services/whatsapp_feedback.py` and `tests/contract/test_whatsapp_feedback.py` add
concise shared-grade projection, lossless-or-web fallback and safe local session links. Actual
channel feedback delivery remains pending conversation integration.

### E7 channel foundation verified; conversation in progress

Commit `c0b5b55` passed CI 37217857047 with 437 Python, 20 browser and five tooling checks plus
clean migrations, contracts, security and containers. This proves internal FR-WA-002/003/004 capability/parity. ADR-038, migration 0020,
`services/whatsapp_practice.py`, `whatsapp_render.py`, `whatsapp_wakeup.py` and
`tests/integration/test_whatsapp_practice.py` address signed end-to-end FR-WA-002/003/004/005/006
and transient FR-ID-006 inventory; those application acceptance gates remain pending.
NFR-PERF-002 has a bounded wake-up implementation, but measured p95 latency remains unverified.

Follow-up FR-CNT-004/FR-WA-003 regression rejects WEB serving/submission of WHATSAPP-only
versions, including direct database insertion, while preserving valid channel attempts.
The conversation suite adds pending hosted checks for accepted intake after a failed broker
wake-up and one attempt/mastery update for concurrent distinct replies to one question.

ADR-039, `services/channel_operations.py`, migration 0021 and the channel operations contract/
integration/browser checks address local FR-OPS-002/004 and NFR-OBS-001 visibility. New operational
acceptance is pending; counts and fake-dispatch timings do not establish NFR-PERF-002 or production
messaging/notification coverage. [Verification](E8_CHANNEL_OPERATIONS_VERIFICATION.md).

FR-GRD-003/004/005 offline validation: [E4 evidence](E4_SHORT_TEXT_VALIDATION_VERIFICATION.md).
Strict output, rubric/evidence/context checks are implemented; validated candidates never authorize
scores. Production eligibility, academic calibration and the learner vertical path remain pending.

### E7 final signed conversation acceptance

Commit `5063528` passed [CI 37220225176](https://github.com/Jotham566/kasoma/actions/runs/37220225176),
469 Python, 20 browser and five tooling checks with all setup/migration/build/security/container
gates. This supersedes the preceding conversation-pending notes for FR-WA-002/003/004/005/006
and FR-CNT-004. See [final evidence](E7_CONVERSATION_VERIFICATION.md). Production transport,
academic approval and measured latency/load remain pending.

FR-GRD-003/004/005 and NFR-SEC-002 rehearsal: [E4 evidence](E4_SHORT_TEXT_REHEARSAL_VERIFICATION.md)
covers 15 FakeModelProvider orchestration cases and bounded dual passes/repair. No scoring, model
inference, academic calibration, full gateway telemetry or learner fallback acceptance is claimed.

ADR-039 local channel operations acceptance is now verified for `34950b0` by
[CI 37221185319](https://github.com/Jotham566/kasoma/actions/runs/37221185319): 479 Python,
20 browser and five tooling checks plus clean migrations/security/container gates. This supersedes
the pending telemetry note above; remaining AI/HTTP/production metrics and release SLOs stay open.

NFR-REL-002/NFR-SEC-002/NFR-MNT-001 local recovery preparation: [E9 evidence](E9_RECOVERY_VERIFICATION.md).
Isolated source/destination backup/restore, row parity and immutable guards require hosted execution;
profile/cleanup contract tests alone do not establish recovery acceptance. Production PITR remains open.

ADR-041 fake orchestration is verified for `2ce14c3` by
[CI 37222368566](https://github.com/Jotham566/kasoma/actions/runs/37222368566): 534 Python,
20 browser and five tooling checks plus clean migrations/security/container gates. All automatic
learner scoring remains disabled. This supersedes earlier rehearsal-pending notes.

NFR-OBS-001/FR-OPS-002/NFR-SEC-002: [request timing evidence](E8_REQUEST_TIMING_VERIFICATION.md)
covers the additive privacy-safe response-start field and six contract cases. Aggregated latency,
full network timing and load/SLO acceptance remain pending; a log sample is not a percentile gate.

E9 final local acceptance: recovery `42a6e08` passed CI 37223872075 (550 Python/20 browser/five
tooling checks, 52-table/270-row logical restore). Browser/transfer `96a16d0` passed CI 37224172033
(550 Python/60 browser/five tooling checks, 191389–194127 response bytes). See the linked reports
for exact scope and limits; earlier pending entries are historical, not current acceptance status.

NFR-SEC-002 assessment database permission profile: [verification](E9_RUNTIME_ROLE_VERIFICATION.md).
The focused real-login integration test is implemented; hosted acceptance is pending. Local database
setup is unavailable. Production role provisioning and complete module grant coverage remain partial.

FR-ID-006/BR-010, FR-OPS-003 and NFR-SEC-002 learning-record holds:
[verification](E8_LEARNING_HOLDS_VERIFICATION.md), [ADR-043](../decisions/ADR/043-learning-record-holds.md).
Grade/mastery evidence/history ownership and guards are implemented with hosted acceptance pending;
full hold coverage and deletion remain incomplete.

FR-ID-001 and security §6 ephemeral OTP retention, supporting NFR-OBS-001:
[bounded expiry verification](E1_EPHEMERAL_EXPIRY_VERIFICATION.md). Scheduled cleanup and
rate-refresh locking are implemented; hosted acceptance is pending. Account/session/audit retention
and other privacy processors remain separate gaps.

NFR-OBS-001/FR-OPS-002 timing is verified at `74a4a8f` in hosted CI 37226011029: 556 Python,
60 browser and five tooling checks plus recovery, security and container gates. Main updated and
the completed branch removed. Aggregated p95/load evidence remains pending.

NFR-SEC-002 restricted-login follow-up: first hosted execution found a missing users-row locking
grant in the test profile. The narrow display_name update grant now enables the existing trigger;
identity/status/birth-date denial assertions remain. Acceptance is pending a complete rerun.

FR-GRD-003/004 criterion-material follow-up: the offline context now requires the specified
criterion text, acceptable evidence, common errors and prohibited inferences. Thirteen new
boundary/privacy cases pass locally; fake prompt versions are v2. See
[validation evidence](E4_SHORT_TEXT_VALIDATION_VERIFICATION.md). Persistence, academic approval,
calibrated enablement and the learner fallback path remain incomplete.

## 9 October 2026 verified rubric, telemetry and dependency slices

Hosted CI [37914864557](https://github.com/Jotham566/kasoma/actions/runs/37914864557)
passed at `ed7d7d5`: 427 unit/contract and 182 integration tests (609 Python total), five tooling
tests, 63 real-API browser journeys across Chromium/Firefox/WebKit and one isolated editor UI test.
Clean setup/migrations/seed, eight focused rubric cases, restricted-login verification,
lint/format/types/contracts/build, dependency/source/image security checks and container smoke all
passed. The isolated logical recovery restored 54 tables/272 synthetic rows in 455 ms and verified
pgvector/immutable guards; this is not production PITR/RPO/RTO evidence. Cold question transfers
were 191529/194251/193635 bytes, each below 250000. Commit `ed7d7d5` is on main; both completed
rubric/telemetry branches were deleted locally and remotely.

This supersedes earlier pending entries for restricted-login checks (NFR-SEC-002), bounded identity
expiry (FR-ID-001), learning-record holds (FR-ID-006/BR-010) and rubric context (FR-GRD-003/004).

FR-CNT-001/002/003/004, FR-GRD-003/004 and NFR-SEC-002:
[ADR-044](../decisions/ADR/044-reviewed-rubric-persistence.md) and
[rubric verification](E2_REVIEWED_RUBRICS_VERIFICATION.md). Migration 0023, shared contracts, content
service, staff editor/reviewer, generated API schemas, learner selection/SQL exclusion and staff
inventory are verified. Three contract cases, eight database cases and the new three-engine journey
cover the boundary; one isolated UI regression verifies save/reload. No academic or learner-scoring
acceptance is implied.

NFR-OBS-001/FR-OPS-002: [synthetic telemetry](E8_MODEL_TELEMETRY_VERIFICATION.md) connects
services/model_telemetry.py, short_text_orchestration.py and model-telemetry.schema.json to eleven
additional contract cases. Closed call/outcome events and disposable fingerprints are verified.
Durable aggregation, threshold alerts, production usage/cost and retention remain gaps.

NFR-MNT-001/security gate: [dependency verification](E9_DEPENDENCY_REFRESH_2026_10_09.md) records
patched runtime dependencies and complete source/container acceptance. Earlier JSON/JSONB and
textarea-label failures are corrected and retained in the rubric verification report.

FR-ID-006 next: [large-history export readiness](E8_LARGE_HISTORY_EXPORT_READINESS.md) maps the
existing bounded synchronous implementation to projection, async delivery and privacy/expiry gates.
This is assessment only; large-history fulfillment remains incomplete. Native Docker now responds,
but local migration/seed/application assertions await the approved image builds/browser downloads.

## Export projection acceptance and native recovery

FR-ID-006/NFR-SEC-001/002/NFR-MNT-001: services/data_export_projection.py and
tests/integration/test_data_exports.py verify batched ORM hydration, owned SQL reference/sealing
queries, exact row-cap accounting and cursor cleanup. See
[projection evidence](E8_EXPORT_PROJECTION_VERIFICATION.md).

Hosted CI [37918757085](https://github.com/Jotham566/kasoma/actions/runs/37918757085)
passed at `8c14590`: 427 unit/contract plus 184 integration tests (611 Python), five tooling tests,
63 real-API browser executions and one isolated editor test. Clean setup/migrations/seed, focused
rubric/role checks, lint/format/types/contracts/build, security/source/image scans and container smoke
passed. Recovery restored 54 tables/272 synthetic rows in 385 ms with pgvector/immutable guards and
no cleanup failures. Cold transfer was 191501/194260/193634 bytes, below 250000 for all engines.
The implementation is on main and its completed branch is removed locally and remotely.

Native Docker is available (29.8.2). The documented CLI PATH adjustment and
`make services-db migrate test-reviewed-rubrics test-data-exports` passed: PostgreSQL/Redis healthy,
eight rubric and eleven export cases verified. Full native `make lint test` passed 427 unit/contract
and 183 integration cases; its storage/Mailpit case failed because MinIO was not running. Separate
contract, recovery (54 tables/272 rows, 221 ms), restricted-role and security checks passed, with no
known vulnerabilities reported. This is not a full native acceptance pass.

The MinIO source download passed its checksum, but `go mod download` later failed with unexpected
EOFs in four module downloads. Native Playwright installed Chromium/FFmpeg; the headless-shell
transfer encountered timeout/connection resets and is retrying. No data or volumes were reset.

This supersedes earlier pending projection/native-database entries. Large-history delivery remains
incomplete; the readiness document is a proposal, not accepted asynchronous behavior. NFR-MNT-001
next covers bounded verified dependency-download recovery without replacing the MinIO source pin.

NFR-MNT-001 native setup resilience: infra/containers/minio.Dockerfile,
infra/containers/download-go-modules.sh and tests/contract/test_minio_download_recovery.py connect
bounded download retries and mandatory integrity verification to four deterministic subprocess
cases. [Verification](E0_MINIO_DOWNLOAD_RECOVERY.md): full hosted CI 37923437046 passed at `04de7ea`
(615 Python, 63 browser, one isolated UI and five tooling checks), including actual services and
security/container gates. Promoted to main; native image download remains incomplete. ADR-019 pins
and runtime behavior are unchanged; browser download recovery is a separate environment issue.

FR-ID-006/BR-010/FR-OPS-003/NFR-SEC-002 accountability hold coverage:
[ADR-045](../decisions/ADR/045-accountability-record-holds.md), migration 0024,
services/legal_holds.py and legal_hold_contracts.py, the administrator selector, generated API
contracts, expanded exact-record integration cases and the administrator browser journey.
[Verification](E8_ACCOUNTABILITY_HOLDS_VERIFICATION.md): 19 focused native cases and hosted CI
37924489562 pass (621 Python, 63 browser, one isolated UI, five tooling plus full security/container
gates). Promoted `ce9d9f3` to main and removed its branch. FLAG_HISTORY and
DATA_REQUEST_REVIEW add preservation only; incomplete coverage and disabled deletion remain.


FR-ID-006/NFR-SEC-001/002/NFR-MNT-001 incremental encoding: `services/data_export_encoding.py`,
`services/data_export_projection.py` and `services/data_exports.py` apply the existing full-envelope
byte cap before collecting the projected history. Codec and database cases cover exact byte counts,
Unicode/escaping, empty sections, early hydration stop, cancellation/cursor closure, all-or-nothing
completion and pre-existing frozen retry copies. [Verification](E8_EXPORT_ENCODING_VERIFICATION.md).
This does not enable asynchronous fulfillment or raise either synchronous limit.

ADR-046 objective load regression: hosted CI 37933227560 passed at `f2dbf8a` (646 Python,
66 real-API browser, five tooling, one isolated UI, full service/recovery/security/container checks).
Promoted to main and removed the branch. Representative deployment/history/provider acceptance
remains open; see the [load evidence](E9_OBJECTIVE_LOAD_VERIFICATION.md).


FR-ID-006/NFR-SEC-001/002/NFR-MNT-001 private artifact preparation: ADR-047,
`services/export_artifacts.py`, synthetic fake-storage contract cases and the owned projection
round-trip integration case. [Verification](E8_PRIVATE_EXPORT_ARTIFACT_VERIFICATION.md).
Delivery remains disabled pending the atomic job/storage/expiry/download lifecycle; existing
synchronous limits, authorization and retention remain unchanged.


FR-ID-006/NFR-SEC-001/002/NFR-MNT-001 private MinIO adapter: `services/export_storage.py`,
24 fake-provider cases and a real local-only owned-object integration case. Bounds apply before
reads and connections close on all paths. [Verification](E8_PRIVATE_EXPORT_STORAGE_VERIFICATION.md).
Native storage is unavailable; hosted actual-service CI 37962081120 passed at `bb2f4eb`, now on main. No runtime delivery
path or new retention decision is enabled; ADR-048 remains proposed.

Incremental encoding and private format hosted regression passed at `a485bb6` (CI 37949902270,
657 Python) and `8c08890` (CI 37950849215, 696 Python), each with 66 browser, five tooling, one
isolated UI and full service/recovery/security/container checks. Both are on main; completed
branches removed. This verifies their internal boundaries, not full asynchronous fulfillment.


FR-ID-006 async lifecycle work in progress: ADR-048 proposal, internal export job/status types
and additive migration 0025 are under implementation. No route/worker registration or completed
requirement is claimed. Queue/snapshot/publication/cleanup/download and acceptance tests must
travel together before this slice is committed or promoted.

Async export progress: [in-progress evidence](E8_ASYNC_EXPORT_VERIFICATION.md) records 23 isolated
PostgreSQL queue/claim/snapshot/publication/cleanup/download/failure cases and complete fake-storage
delivery of a 12,000-event synthetic history beyond both original caps. Fifteen existing export
regressions pass. Authenticated API/browser/worker integration remains incomplete; no requirement
is marked complete from these internal results.

FR-ID-006/FR-OPS-002/NFR-SEC-002 in-progress cleanup cursor: `services/export_cleanup_cursor.py`
and 13 deterministic contract cases enforce scoped keys, bounded reads, finite one-hour retention,
phase alternation and safe restart after invalid state/cache outages. Eight attachment transport
cases cover exact lengths, failure/cancellation and resource closure. The current 554 unit/contract
and five tooling checks pass. No scheduled worker or HTTP route is enabled by these helpers.


Migration 0025 clean-schema coverage and synthetic logical recovery pass (56 tables/272 rows,
280 ms); restricted-role regression and source/dependency security checks pass. Job/generation
recovery fixtures, absolute provider-read cancellation, enabled worker/API/proxy/UI acceptance
and actual scoped MinIO lifecycle verification remain outstanding under ADR-048.


FR-ID-006/NFR-SEC-001/002/NFR-OBS-001/NFR-MNT-001 async transport progress: the signed local
reader passes 22 deterministic plus one real TCP dribble/cancellation case; isolated API routes
and shared authenticated decoding pass ownership, frozen transfer, corruption/revocation and
expiry checks. 590 unit/contract, 35 focused lifecycle/API and 15 existing export cases pass.
Worker tasks have dedicated-queue envelopes and closed observability, but runtime registration,
hard-kill recovery, web proxy/UI, operations and complete acceptance are outstanding.
See [current evidence](E8_ASYNC_EXPORT_VERIFICATION.md); ADR-048 remains proposed.


FR-ID-006/FR-OPS-002/NFR-MNT-001 worker evidence: `make test-export-worker` passes five policy/
closed-error cases and an isolated real CLI hard-kill/replacement/lease-recovery case on macOS.
The test exposed and verified the fix for spawned task registration. No ordinary worker timeout,
provider, data or deletion permission changes. Actual application activation remains gated.


NFR-MNT-001 local resource correction: a broad native run passed 151 integration cases but had
86 fixture errors after PostgreSQL exhausted Docker's default 64 MiB `/dev/shm` and entered
recovery, plus the two known unavailable-MinIO failures. Compose now sets `shm_size: 512mb`.
`make services-db` recreated only the PostgreSQL container with its existing named volume intact;
inspection confirms a healthy service and 536870912-byte shared-memory ceiling. SQL timeouts,
acceptance thresholds and developer schemas remain unchanged. The serial rerun passes 590 unit/contract and 238 integration cases with zero setup errors;
its only two failures are the unavailable-MinIO cases. Actual storage acceptance remains open.

The real Uvicorn/API/middleware client-disconnect test passes: closing a partial attachment cancels
the in-flight async reader and closes its resources. Current focused lifecycle/API count is 37.


FR-ID-006/NFR-REL-002 recovery follow-up: the isolated logical drill now publishes a synthetic
async export before backup, requires nonempty job/generation records, verifies restored publication
guards and decrypts the restored manifest against in-memory synthetic encrypted objects. Frozen
bytes match; source/destination inventories remain unchanged. Native `make recovery-drill` passes
56 tables/285 rows in 262 ms with no cleanup failure. This is database/key compatibility evidence,
not object-storage backup, namespace remapping, production PITR or RPO/RTO acceptance.

The unwired web attachment helper passes exact-length, metadata, cancellation and deadline checks.
`make format lint test-tooling openapi-check` passes, including 21 tooling cases; application
contracts remain unchanged. ADR-048 and the complete async delivery slice remain unaccepted.

Recovery follow-up regression: `make format lint test-export-jobs test-unit` passes 40 focused
PostgreSQL cases, 590 unit/contract and 21 tooling cases. Three new cases prove read-only export
verification rejects corrupt ciphertext, missing objects and mismatched expected bytes.


FR-ID-006/NFR-SEC-001/002 web gateway integration: owner export-job paths accept GET/POST;
export-file accepts GET only and rejects cross-site/same-site attachment requests. The attachment
uses the private cookie-derived Authorization header, requests identity encoding, rejects redirects
and keeps credentials out of URLs. Initial headers retain the eight-second deadline; successful
attachments move to the separate 300-second streaming deadline. Closed error mapping cancels the
unread upstream error body. Disconnects abort either phase. `make format lint test-tooling` passes
31 tooling cases, including ten new private-fetch/error/deadline cases. This supersedes the earlier
unwired-helper note; API registration and learner controls remain pending.


Snapshot sealing regression passes: after the export's repeatable-read snapshot is established,
the independent API commits the final diagnostic answer before export sections are read. The
result still contains the original 14 unreleased answers and no grades/mastery disclosure; retry
is byte-identical. A new request includes all 15 released results. `make format lint test-export-jobs
build` passes 41 focused PostgreSQL cases and the production web build. Final formatting/lint/types/
documentation/OpenAPI checks pass; generated application contracts remain unchanged.


Attachment navigation failure handling (FR-ID-006, NFR-SEC-001/002): before a successful
attachment response starts, a closed upstream failure on an explicit navigation returns a
no-store 303 to the fixed local privacy page. Its query contains only an allowlisted error code,
never credentials, record identifiers, diagnostics or a return URL. The privacy page resolves
that code to a fixed accessible alert. Programmatic requests retain JSON/status errors;
cross-site/same-site rejection does not redirect. Mid-stream errors still abort the transfer and
cannot be converted into a successful file or a late redirect. Native attachment links must rely
on server Content-Disposition, without a `download` attribute that might save a redirected page.
`make format lint test-tooling build` passes 32 tooling cases and the production web build.
Real Next/API HTTP checks are running through `make test-export-gateway`; these do not require or
claim a browser-engine download journey. Learner queue/status controls and API activation remain
pending under ADR-048.

`make format lint test-export-gateway` passes both real Next/API HTTP cases in 6.8 seconds.
Navigation gets a fixed local redirect and rendered alert; programmatic errors stay JSON;
unsupported methods and same-site/cross-site requests are denied. These HTTP-client checks do
not assert native browser save/cancellation behavior or successful MinIO attachment delivery.


FR-OPS-002/003 export monitoring: the existing ADMIN-only operations endpoint now includes
bounded queued/running/current terminal-failure counts and oldest pending age from durable SQL.
Failure observations include only currently FAILED jobs with finished_at in the inclusive last
24 hours; future finishes are excluded. Explicit retry removes the failed observation and resets
pending age; automatic retry retains the original command age. No identifiers, grant fields,
manifest/object references or source data are returned. Counts reuse the 10,000 cap/at-least flag.
The generated contract and operations page include the metrics and unavailable-state wording.
Configurable local warning defaults are OPS_EXPORT_FAILURE_THRESHOLD=1 and
OPS_EXPORT_AGE_SECONDS=300 (bounded 1–10,000 and 60–86,400 respectively). These engineering
thresholds are not legal fulfillment deadlines or proof of delivery. ADR-048 remains proposed;
export API/worker activation and learner controls remain pending.

Operations evidence: `make test-operations` passes 19 contract/PostgreSQL cases, including real
queue-to-running-to-terminal-failure/retry transitions, inclusive 24-hour bounds, exclusion of
future finishes, exact alert thresholds/recovery and minimized output. The first broad unit run
caught omitted EXPORT_FAILED/EXPORT_STALLED values in the analytics alert schema; the schema was
updated without weakening its exact-match guard. Final `make format lint test-unit build
openapi-check` passes 593 unit/contract and 32 tooling cases plus generated contracts and production
web build. Browser assertions for the metrics were added but remain unexecuted pending engines.


FR-ID-006/FR-OPS-002/NFR-MNT-001 launch policy: `make worker-exports` now defines the dedicated
single-concurrency prefork consumer, prefetch multiplier 1, explicit exports queue and importable
shared tasks. It starts no Beat scheduler. Native and Compose ordinary workers explicitly consume
only operations/imports/messaging. The normal development launcher still starts only the existing
ordinary worker/scheduler; export Beat registration, automatic startup and owner routes remain
disabled pending the complete slice. The manual consumer command is not feature acceptance.

`make format lint test-export-worker` passes seven cases. The real subprocess test derives its
launch flags from `make -n worker-exports`, substituting only the isolated synthetic application,
queue/node identity and diagnostic verbosity. A non-cooperative provider is hard-killed, a new PID
runs, the database lease recovers, and a message on another generated queue remains unconsumed.
The test removes only its own Redis namespace after stopping its subprocess group. Production
110/120-second limits remain unchanged; the test fixture accelerates them to 0.5/1.5 seconds.

Launch follow-up `make format lint test-unit openapi-check` passes 594 unit/contract and
32 tooling cases; generated contracts match. The separate seven-case worker run includes real
hard-stop and foreign-queue isolation evidence. Automatic launch/scheduler, owner UI and full
storage/browser acceptance remain pending; no commit or promotion is claimed.


Candidate wiring for local synthetic acceptance (not promotion): the application now registers
owned export commands/status/attachments and the two scheduled tasks. `make dev` starts the
dedicated consumer alongside the existing sole scheduler; the application Compose profile includes
an export-worker with its own targeted health check. Ordinary workers retain exclusive selection
of operations/imports/messaging. Container smoke includes and preserves the prior running state
of the new worker. Generated contracts include the actual registered owner endpoints.

Learner controls use the generated client for explicit prepare/status/retry, retain ambiguous
command keys in memory, and save READY copies via a plain attachment link without a Blob. A
separate synthetic E2E fixture uses in-memory encrypted objects; no live storage/model/messaging
provider participates in those tests. The real Next/API HTTP journey now passes command/replay,
READY polling, exact-length frozen attachment and pre-response failure navigation (three cases).
The registered API's 41 focused PostgreSQL cases and seven worker cases pass. Browser journeys
were added but remain unexecuted while engine installation runs. ADR-048's prior disabled notes
are historical; its promotion/release gate is unchanged. No production deployment is authorized.


FR-OPS-002/NFR-MNT-001: each Compose worker now checks its explicit node identity and requires
that node's pong. A healthy export consumer cannot mask an unavailable ordinary worker (or vice
versa). Deterministic checks exercise both actual Compose probes with own, foreign, missing and
invalid replies. This corrects health reporting; queue separation and the sole scheduler remain
unchanged. Runtime container verification remains pending image completion.


Health and gateway follow-up: `make format lint test-export-worker` passes all 15 cases,
including both actual Compose probes rejecting foreign/missing/invalid replies and the real
hard-stop/lease-recovery case. `make format lint test-export-gateway` passes all three real
Next/API HTTP cases. Unauthenticated attachment requests must now return exactly 401
REAUTH_REQUIRED (or the corresponding fixed navigation redirect); a missing route/404 no longer
passes the regression. These are not native browser download or complete container acceptance.
Docker PostgreSQL, Redis, Mailpit and web are currently healthy; API/worker images, MinIO and
browser engines are still building/installing. No commit or main promotion is claimed.


FR-ID-006 interrupted-download acceptance: the isolated E2E process now offers per-generation
corruption/stall controls over its in-memory encrypted store and a bounded 700-event synthetic
history. Installation refuses any database search path other than the harness's random E2E
schema. Fixture routes are absent from application entry points, images and generated contracts;
the web gateway does not expose them. No real storage or external provider participates.
Four deterministic fixture checks pass within the 606-case unit suite. New browser journeys
require mid-stream corruption/cancellation to fail, release the reader and preserve a complete
frozen retry. They are added but not yet executed pending browser installation. The actual
Next/API HTTP suite additionally exercises the same faults independently of native browsers.


Fault transport result: `make format lint test-export-gateway` passes all three HTTP cases
(8.7 seconds), now including a multi-chunk synthetic export, corrupt second-chunk failure,
client timeout/disconnect during a stalled second read, observed reader closure and exact frozen
retry after each failure. This uses the real API/Next transport with fake storage. It does not
substitute for native browser save/cancel or MinIO verification. `make check-docs` passes.


NFR-COMP-001/NFR-MNT-001: add `make e2e-chromium-full`, an explicit supplementary command
using the installed pinned full Chromium in new headless mode. It retains both shards and all
assertions; normal CI and the three-engine acceptance requirement remain unchanged. This allows
real-browser progress during the separate headless-shell download, without restarting the live
installer or substituting an unpinned system browser. Execution evidence follows separately.


First full-Chromium shard: 13/14 tests passed, including native background-command recovery,
saving frozen attachments, user cancellation, corrupt second-chunk failure and successful retry.
The old administrator privacy-review test selected every export in the shared queue; concurrent
new export fixtures made its final assertion ambiguous. Scope its export/deletion locators to
the exact references returned by that learner's requests, retaining all permission/review/
download assertions. Both Chromium shards are being rerun; no complete browser pass is claimed.


Full pinned Chromium result: `make format lint e2e-chromium-full` passes both shards,
14 + 14 = 28 tests (25 browser journeys and three HTTP-only gateway cases). This includes
background-command lost acknowledgement, native attachment saves/frozen retry, cancellation,
corrupt second-chunk failure and reader closure, existing privacy review/holds, operations
metrics, narrow touch reflow and the existing learning/content/channel journeys. The ambiguous
admin locator failure is resolved using exact owned references; no assertions were removed.
`make security-source openapi-check` also passes: no secret leaks and matching generated contracts.
Firefox/WebKit, default headless-shell execution, native MinIO, full application containers and
hosted regression remain outstanding. This does not grant production or ADR-048 acceptance.


Learner UI next-slice readiness: [review and acceptance plan](E6_LEARNER_UI_READINESS.md)
identifies the existing functional screens and the remaining shared navigation/home/recommendation
work for FR-REV-006 and NFR-ACC-001/BW-001/COMP-001. No visual acceptance or new feature is claimed.


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


Native storage gate update: the pinned MinIO source build completed and its service is healthy.
`make seed` now passes both catalog and private storage initialization. `make test-export-storage`
passes all 59 cases, including real signed async MinIO reads, scope/listing, encrypted round trip,
anonymous denial and owned-object cleanup. The earlier unavailable-MinIO failures are not waived;
`make migrate test security` is running again with storage available. The new export worker has
started and its readiness is being checked. Browser installation remains live.


FR-ID-006/NFR-MNT-001 full Docker delivery evidence: `make smoke-export` passed through
the running Next/API/ordinary Beat/export-worker/MinIO topology. A fresh fictional account
receives its OTP only in local Mailpit; the probe searches only its own unpredictable recipient,
verifies via secure-cookie gateway flow, queues a request and waits at most 45 status reads.
The real scheduled worker published a 2,191-byte private export; exact length, own identifier,
no-store and frozen retry matched. The probe revokes only its session; normal retention handles
its synthetic request/copy. No credentials, OTP, identifier or contents are printed.

Add this journey to `make container-smoke`, retaining existing preservation of already-running
services. Two deterministic fake-transport tests verify bounded local behavior and reject a
changed retry file; the unit suite passes 608 cases. Full native integration remains in progress.
This proves local delivery, not production or long-history load acceptance.


### Native regression acceptance update — 9 October 2026

FR-ID-006, FR-OPS-002/003, NFR-SEC-001/002, NFR-REL-002 and NFR-MNT-001:
`make migrate test security` completed successfully with 606 unit/contract, 32 tooling and
245 integration cases; the later two smoke-probe cases passed in the 608-case unit run.
Actual MinIO checks now pass, resolving the earlier unavailable-storage failures. Bandit,
secret boundaries and Python/Node dependency audits pass. `make recovery-drill test-web-content`
also passes: 56 tables/285 rows restored in 256 ms, immutable/export guards verified, and
one isolated content-admin browser case. Object-storage recovery and production RPO/RTO
remain unverified. Evidence: `.local/async-export-complete-native-regression.log` and
`.local/async-export-final-recovery-ui.log`. Remaining browser matrix, container vulnerability
scan and hosted CI still gate promotion; ADR-048 remains proposed.


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


NFR-SEC-001/NFR-MNT-001 scan environment update: the native Trivy database download
exceeded its default five-minute deadline before scanning either image. The pinned CLI
confirms a `--timeout` duration option. `make security-containers` now supplies a configurable
30-minute per-image bound; database freshness, severity and failure rules are unchanged.
A retry is running. The initial run is recorded as incomplete, not clean.


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


FR-ID-006 promotion coverage audit: inspected explicit assertions for revoked publication,
12,000-event complete exports, late orphan cleanup, storage failure/retry, cross-owner reads,
mid-read cancellation/corruption and privacy access after consent withdrawal. The export
verification document records exact tests and remaining scope. Hosted/browser/container
acceptance remains pending; this review does not mark ADR-048 or the MVP accepted.


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


Native container security result: `make security-containers` completed successfully for both
`kasoma-api` and `kasoma-web` with the updated vulnerability database and no HIGH/CRITICAL
findings. Evidence: `.local/async-export-container-security-retry.log`. The initial attempt
failed before scanning due to the database-download deadline; extending only the finite
timeout resolved it. This closes the local image-scan gate, not hosted/latest-head browser
acceptance or production security approval.


Latest UI container verification: `make container-smoke` passes with all eight services healthy
and an actual scheduled owned export through web/API/Beat/export-worker/MinIO. The 2,191-byte
synthetic JSON copy has an exact-length frozen retry; the smoke session is revoked afterward.
Existing services remain running. Evidence: `.local/final-ui-container-smoke.log`.
The completed UI follow-ups are now queued for one final-head hosted run; the earlier candidate
run is superseded, not treated as passed. Main/ADR acceptance still requires the final run.


FR-ID-006/FR-WA-006/BR-010 readiness: [channel preservation assessment](E8_CHANNEL_HOLD_READINESS.md)
records concrete ownership, message disposal, STOP/unlink and relinking constraints from existing
code and database guards. It defines required ADR decisions and acceptance tests, not an accepted
implementation or legal decision. Current retention and incomplete-hold warnings remain unchanged.


FR-ID-006 / NFR-COMP-001 candidate acceptance update (9 October): two native
Firefox attachment cases fail in both the full first shard and focused serial reproduction.
Cancellation reader closure and corruption download completion remain unresolved; Chromium evidence
does not satisfy this gate. See [export verification](E8_ASYNC_EXPORT_VERIFICATION.md).

A plain HTTP native-download control reproduces both failures in pinned Firefox,
while Chromium passes. This narrows diagnosis; it does not establish Firefox acceptance
or replace the real-gateway requirement. The standalone diagnostic command starts no
application/database services.

NFR-ACC-001 / NFR-COMP-001: native WebKit export fault cases pass; its first-shard
keyboard test required macOS Option-Tab for links. The corrected test retains skip-link
and main-content focus assertions; all 30 native WebKit application cases pass; Firefox remains open.

FR-ID-006 / NFR-SEC-001 / NFR-COMP-001: delivery enforces a five-second object-read
bound independently of the storage adapter. The stalled-adapter integration regression
passes with all 42 focused export cases; Firefox stall/cancel/frozen retry now passes.
Raw native-manager corruption controls narrow the remaining automation discrepancy
but do not establish application acceptance. See export verification.

FR-ID-006 / NFR-COMP-001: the mandatory real-application Firefox corruption case
passes through the pinned browser's ordinary download manager, verifying rejection,
reader closure, READY state and byte-count/SHA-256-identical native retry. The driver
changes only that case's automation boundary; no requirement or failure is skipped.
Full Firefox and hosted final-head acceptance remain required.

NFR-ACC-001 / NFR-COMP-001: shared learner/staff navigation minimum height is now
48px, leaving margin above the unchanged 44px acceptance threshold after Firefox
reported fractional bounding-box values at an exactly 44px height. Full matrix pending.
The complete timeout-fix integration/security run passes 246 integration cases.

Final native follow-up evidence: all 90 browser executions pass (30 Chromium,
30 Firefox, 30 WebKit), including the mandatory real-gateway export faults and
48px navigation. All 246 integration cases/security checks and the later 625-case
unit plus 32-tooling run pass. Rebuilt eight-service smoke and API/web image scans
pass. Hosted final-head verification and ADR-048 promotion remain pending.

FR-GRD-004/005 and NFR-SEC-002: internal `services/short_text_contracts.py` adds bounded
answer input and distinct pending/neutral outcomes, rejecting scores and hidden/provider
material. ADR-050 remains proposed; runtime routes, worker and privacy integration are
not implemented by these contracts. Verification passes: 699 unit/contract tests (33 new outcome/input cases), 35 tooling
checks, format/lint/types and generated-contract comparison. No HTTP schema changed.

NFR-MNT-001: CI cache configuration passed remotely in run 37993094065, but PostgreSQL
pull throttling persisted. Optional read-only registry authentication is prepared; hosted
acceptance remains open. See [CI evidence](E9_CI_RUNTIME_VERIFICATION.md).

NFR-SEC-002 / FR-GRD-003 / FR-ID-006: `services/short_text_answers.py` implements the
bounded authenticated answer format proposed by ADR-050. Synthetic real-crypto tests
cover exact Unicode/escape preservation, cross-record replay, tampering, wrong keys,
bounds and closed errors. Verification passes: 730 unit/contract cases (31 new
answer-protection cases), 35 tooling checks, formatting/lint/types, generated-contract
comparison and source secret scanning. No database/API path is enabled;
exports and new workflow-record hold/retention coverage remain required before integration.

FR-GRD-003/004/005 and NFR-SEC-002: `services/short_text_workflow.py` adds the proposed
one-claim transition policy, inclusive queue/lease expiry, clock/state validation and
immutable terminal replay. A crashed claim cannot reset the global model-call budget.
Verification passes: `make format lint test-unit openapi-check security-source`,
including 747 unit/contract cases (17 new transitions) and 35 tooling checks. Log:
`.local/short-text-workflow-checks.log`. This is a transition component only; durable SQL locking,
worker wiring, eligibility, grade/mastery publication and privacy coverage are unimplemented.

FR-GRD-004/005 / NFR-SEC-002: migration 0026, grading-work models and transactional
storage are under verification. Commands have one claim, bounded expiry and immutable
transition snapshots. No learner/worker path is enabled. Use `make test-grading-work`;
privacy inventory/export/hold coverage and restricted-role checks remain integration gates.

Durable-store focused verification passes 24 cases (seven PostgreSQL, 17 transition),
including contention, rollback, expiry, publication consistency and owned/foreign
export projection. Work/history counts are in deletion inventory. Full backend
regression is running; exact-record holds and restricted-role extension still gate
runtime enablement. See `docs/implementation/E4_DURABLE_GRADING_VERIFICATION.md`.

NFR-SEC-001/002: the durable-work restricted-login extension passes independently:
queue, claim and neutral completion work with bounded grants; history mutation,
command deletion, schema changes and immutable attempt-ID edits are rejected. Source
secret scanning and generated-contract comparison pass. Full backend run remains live;
new history hold coverage and worker/publication integration are still pending.

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

## Publication and audit assignment preparation — 10 October 2026

FR-GRD-003/004, FR-MST-001, FR-ID-006 and NFR-SEC-002: migrations 0030/0031
add a band-locked publication ordinal, atomic minimum-10% audit assignment, immutable
records and exact publication/assignment holds. Owned exports omit calibration IDs,
ordinals and sampling flags; deletion inventory includes both personal record types.
The generated hold contract and staff selector include the new types. These are
format-independent storage controls tested with valid synthetic objective grades;
learner short-text scoring remains disabled. Grade/mastery integration, blinded expert
review, rolling audit outcomes and automatic disablement remain required.

Initial eight PostgreSQL cases pass after correcting a test-only projection import.
Additional negative and restricted-login checks are running. Full regression, populated
recovery and browser acceptance remain required; no completion or promotion is claimed.
See [publication verification](E4_PUBLICATION_VERIFICATION.md).

Verification update: `make test-grading-publications` passes 10 PostgreSQL cases;
`make test-legal-holds` passes 19 existing preservation cases; the real restricted-login
case passes with INSERT-only publication/assignment rights and guarded counter UPDATE.
It denies record rewriting/deletion and band activation/approval changes. Formatting,
lint/types and generated contracts pass. The isolated populated recovery now compares
63 tables / 302 rows, restores in 282 ms and verifies publication/assignment/counter
immutability, with no cleanup failures. Its synthetic owner-only band transition is
restricted to the generated recovery-source database name and is not academic evidence.
Full backend and three-engine privacy regressions are running; acceptance remains open.

Diagnostic disclosure follow-up: all 11 focused publication cases pass, including a
complete 15-question diagnostic proving publication/audit records remain absent from
owned exports until completion. The first privacy-browser run used a stale production
web build and failed the new option-list assertion (one pass, one failure). No assertion
was weakened; `make build test-web-privacy` is rerunning against the rebuilt source.
The full backend run began before this final diagnostic test was added; its evidence
must be read alongside the 11-case focused result, not claimed as an exact final-tree run.

Rebuilt browser acceptance: `make build test-web-privacy` passes all six executions
across Chromium, Firefox and WebKit, including the new hold selector and unchanged
ownership/retry/export protections. Final `make lint openapi-check` also passes.
The earlier stale-build failure is resolved. Full backend/security regression and
rebuilt-container checks remain live; no commit or main promotion is claimed yet.

Final focused checks pass 12 publication cases and 13 band cases, including foreign
scope/replay rejection and populated upgrade counter backfill. Rebuilt container scans,
eight-service export/metrics smoke and source checks pass. Full backend/security
regression remains running; the [publication report](E4_PUBLICATION_VERIFICATION.md)
consolidates final evidence and the resolved initial test/browser failures.

## 18 October 2026 acceptance reconciliation

FR-ID-006 / FR-OPS-002 / NFR-OBS-001 / NFR-MNT-001: main is `46a0f8a`, with
complete hosted runs 38033307073 and 38034913518 passing. ADR-048/049 now record
local synthetic acceptance. Completed export, timing and earlier short-text branches
are removed; the current grading branch retains the unpublished audit-ledger work.
FR-GRD-003/004 / FR-MST-001 / FR-ID-006: publication tests pass as recorded in the
[verification report](E4_PUBLICATION_VERIFICATION.md). Full regression passes 780
unit/contract, 35 tooling and 291 integration cases; 12 final publication and 13 band
cases cover later assertions. The security retry passes after a PyPI timeout.
No learner short-text grading, academic approval or production acceptance is inferred.

## Learner short-text flow in progress — 18 October 2026

Requirements: FR-GRD-003/004/005, FR-MST-001 and FR-ID-006. The next cohesive
slice connects encrypted submission, bounded worker execution, authorized outcomes,
mastery, audit and learner resume/poll/fallback. Current rubric results now have a strict
partial-credit contract with matching rubric/item version, unique criteria, coherent
score/totals, finite confidence and minimized representations. Candidate projection
rechecks answer evidence and authored feedback. This formatter grants no eligibility,
publication or disclosure authority. Its evidence excerpts require encrypted persistence
and current owner authorization before learner projection.

`make format lint test-unit openapi-check` passes 808 unit/contract and 35 tooling
checks. The 28 new result cases reject forged evidence/feedback, invalid/mismatched
rubrics, duplicate criteria, inconsistent scores and unsupported fields. HTTP schemas,
assignment guards and learner delivery remain unchanged at this intermediate point.
No short-text feature completion is claimed; see the flow implementation checklist.

## Cohesive short-text candidate under verification — 18 October 2026

FR-GRD-003/004/005, FR-MST-001, FR-ID-003/006 and NFR-SEC-002: the working
branch now includes draft migration 0032, encrypted result storage/projection, pinned
assignment bands, atomic encrypted attempt/receipt/work submission, owned pending and
neutral result retrieval, and a finite-lease processor. The processor releases locks
for model work, rechecks current consent/content/report/band before each dispatch and
publication, and commits grade/mastery/audit together. The default report and safety
authorities are unavailable, runtime enablement defaults false, and only deterministic
fake providers are implemented in this candidate. No real report or safety approval
has been created. Trusted isolated fixtures supply synthetic authorities for tests.

The intermediate API/worker suites pass 10 cases, including a complete synthetic
pending-to-grade-to-mastery/audit/export path and before-second-pass withdrawal,
disablement and lease-expiry barriers. The result encryption suite passes 828 unit/
contract and 35 tooling cases. Existing rubric/band checks pass after fixing an ORM
foreign-key registration regression; the reproduced objective failure is retained in
`.local/short-text-objective-regression.log` and its passing test remains in the suite.

Newer additions (diagnostic terminal/sealing coordination, queue wake-up/scheduler,
learner pending/poll/fallback UI and reassessment guards) are under verification.
Migration 0032 has only run in isolated test schemas; the persistent Docker review
stack remains on the verified 0031 images. Full regressions, database grants/recovery,
independent blinded expert audit/rolling disablement and browser acceptance remain
required. No learner-flow completion or main promotion is claimed.

18 October verification follow-up: nine synthetic short-text browser executions pass
across Chromium/Firefox/WebKit, including 320-pixel neutral review, exact retry and
sealed diagnostic. Fourteen focused PostgreSQL cases prove duplicate claims cannot
restart model budgets, publication rollback preserves no partial grade/audit/mastery,
and revoked report authority after pass two prevents scoring. Broker-failure/SQL-atomicity
extensions and complete regressions are under verification. Source/dependency security
passes; the recovery fixture now includes encrypted rubric results (initial restore:
63 tables/602 rows/281 ms). Explicit restored decryption, final container checks and
full acceptance remain pending. See [current evidence](E4_SHORT_TEXT_FLOW_IMPLEMENTATION.md).

Final local follow-up: the stable complete browser command passes 99 executions;
18 flow cases, actual restricted-login publication, 831 unit/contract and 35 tooling
cases, lint/types, contracts, source/dependency security, populated encrypted recovery
and the rebuilt eight-service export/metrics smoke all pass. Grading uses its separate
queue and polling has server/client bounds. Broad backend and current container scans
remain in progress; expert review/rolling disablement and real learner enablement
remain unimplemented. Exact logs and limits are in the linked current evidence.

The broad backend run is now terminal: 307 integration cases pass in 901.92 seconds.
Its earlier collection is supplemented by the final 18-case flow and 831-case unit
runs above. Container vulnerability-database download and hosted verification still
gate promotion. This is verified disabled synthetic engineering, not MVP acceptance.

## Independent expert-review candidate — 18 October 2026

FR-GRD-003/004/005, FR-ID-003/006 and NFR-SEC-002: the next branch proposes ADR-051
and begins draft migration 0033 plus blinded review contracts. It addresses the
unimplemented completed-review/rolling-disablement path and adds release-unit sampling
to cover diagnostics that remain sealed. No application acceptance is claimed; tests,
staff/runtime wiring, exact holds, export/inventory and recovery remain pending. See
[readiness](E4_EXPERT_REVIEW_READINESS.md).

18 October recovery/promotion update: disabled learner-flow commit `853f80a` passes the
complete hosted run [39143803289](https://github.com/Jotham566/kasoma/actions/runs/39143803289)
including rebuilt-image security and container smoke. It is promoted to main and the
merged branch removed. Local scan interruption is not a local pass. The next review
branch remains uncommitted/unverified after its initial 20 contract/SQL cases; no
complete grading, real-data or MVP acceptance is claimed.
