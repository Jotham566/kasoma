# Requirements Traceability

Live implementation evidence for every requirement in the [SRD](../specifications/01_SRD.md). The [specification matrix](../specifications/14_Requirements_Traceability_Matrix.md) defines required coverage and evidence. Update this register with each implementation slice; completion requires passing acceptance evidence.

E0 through E6 synthetic learning and E8 learner-flag evidence is recorded below. Local synthetic journeys are not
production-pilot acceptance; delivery-provider and legal approval gates remain. See the [assessment](PHASE_0_ASSESSMENT.md).

| Requirement | Implementation | Tests / evidence | Status |
| --- | --- | --- | --- |
| FR-ID-001 | Email/phone OTP, purpose binding, five-attempt/ten-minute limits, per-contact/peer/device sends; initial UI check serializes sign-in actions | `tests/integration/test_identity.py`, `tests/e2e/identity.spec.ts` | Local implemented; SES/SMS production gates pending |
| FR-ID-002 | Verified identifier linking with uniqueness, encryption and keyed lookup; existing identities never auto-merge | API linking, collision and one-identity tests | Local implemented |
| FR-ID-003 | Birth date, adult consent, separately verified guardian evidence/learner assent, withdrawal, policy gate | Minor/adult API and browser tests; ownership, idempotency and policy-change tests | Local implemented; approved wording and WhatsApp integration pending; diagnostic and revision routes enforce current consent |
| FR-ID-004 | Server-restricted S4 Mathematics/Physics profile and subject selection | Profile validation and browser journeys | Local implemented |
| FR-ID-005 | Opaque sessions, refresh rotation/reuse revocation, current/all logout | Expiry, family reuse and revocation API tests; browser logout | Local implemented |
| FR-ID-006 | Recent-OTP intake/review and owned allowlisted JSON export; encrypted retries, atomic completion, six-year deadline and 24-hour copy expiry | Contract/API/SQL/browser tests; [intake](E8_DATA_REQUESTS_VERIFICATION.md), [export verification](E8_DATA_EXPORTS_VERIFICATION.md) | Partial: intake/export/expiry and deletion preview merged; specific-record hold lifecycle local ([verification](E8_LEGAL_HOLDS_VERIFICATION.md)); erasure/anonymization, full hold coverage, large-history fulfillment and accountability expiry pending |
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
| FR-GRD-003 | — | — | Not started |
| FR-GRD-004 | — | — | Not started |
| FR-GRD-005 | Typed deterministic correct/missing elements and authored remediation | API score/feedback and browser correct/incorrect journey | Choice and numeric correct/missing feedback implemented; rubric feedback pending |
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
| FR-WA-001 | — | — | Not started |
| FR-WA-002 | — | — | Not started |
| FR-WA-003 | — | — | Not started |
| FR-WA-004 | — | — | Not started |
| FR-WA-005 | — | — | Not started |
| FR-WA-006 | — | — | Not started |
| FR-CNT-001 | `services/content.py`, strict draft DTO, staff editor | Content API/schema/browser tests | Partial: single-choice, multiple-choice and numeric create/edit complete; import and other formats pending |
| FR-CNT-002 | Role checks and immutable author ownership; self-review blocked even with both roles | API self-review denial; SQL review guard; disabled author approval in browser | Local implemented |
| FR-CNT-003 | Return, approval, high-risk/disputed second review, retirement and append-only reviews | Full API/browser workflow; two-reviewer and retired-selection tests | Local implemented with synthetic content |
| FR-CNT-004 | Immutable approved versions, explicit successor drafts and normalized frozen mappings | API mutation rejection; direct SQL history/mapping/attempt tests; retired-version grades/solutions remain unchanged | Partial: choice/numeric attempts and grades pin immutable versions/hash; migration preserves legacy choice rows; rubric pinning pending |
| FR-CNT-005 | Submission and approval revalidate rights, mappings, weights, answer, solution and remediation | Field-specific 409 tests; approval revalidates changed curriculum references | Local single/multiple-choice and numeric publication validation implemented; other formats and academic evidence pending |
| FR-CNT-006 | Reviewer/admin queue, independent claim, priority/status/resolution, immutable history and revision-checked retries | Triage API/browser, role/ownership, audit/rollback and disputed-successor tests | Local synthetic implementation; approved live support and retention jobs remain production gates |
| FR-OPS-001 | `services/observability.py`, `packages/analytics-schema/` | `tests/contract/test_foundation.py`, `tests/contract/test_identity_contract.py`, identity integration outbox assertions: safe operational and identity-event shape | Registration/consent, assessment, diagnostic start/completion and mastery-update events persist atomically; hint-use and reassessment lifecycle events also persist atomically; flag lifecycle events use the content outbox; data-request intake/review and export completion events also use the identity outbox; other learner events and dispatch pending |
| FR-OPS-002 | `services/health.py`, API health shell and worker smoke | Health success/degraded tests; real Redis/Celery test | Partial; alerts/dashboards pending |
| FR-OPS-003 | Atomic content/role audit, database history guards | Direct SQL audit rewrite rejection, role-action records and content events | Partial: content/local roles and flag read/triage audit; broader operations audit UI/retention pending |
| FR-OPS-004 | — | — | Not started |
| NFR-PERF-001 | — | — | Not started |
| NFR-PERF-002 | — | — | Not started |
| NFR-REL-001 | — | — | Not started |
| NFR-REL-002 | — | — | Not started |
| NFR-SCL-001 | — | — | Not started |
| NFR-SEC-001 | `services/config.py`, loopback Compose, generated ignored secrets | Fail-closed/redaction tests; source/dependency scans | Partial; production TLS/encryption pending |
| NFR-SEC-002 | Identity ownership, recent-auth/consent controls and staff content-role enforcement | Identity integration and cross-origin browser tests | Partial; content RBAC implemented; assessment consent/ownership guards verified; production MFA/role governance and future route integration pending |
| NFR-ACC-001 | `apps/web/app`, `packages/ui` | Playwright keyboard retry and axe scan | Shell, onboarding, staff review, assessment, diagnostic, progress/history and flag/triage axe/keyboard checks; remaining journey matrix pending |
| NFR-BW-001 | — | — | Not started |
| NFR-COMP-001 | Next.js shell | Chromium browser test | Partial; cross-browser learner matrix pending |
| NFR-OBS-001 | UUID web/API/worker correlation; console OTel; safe JSON logs | Unit redaction and real worker propagation tests | Foundation verified; authenticated/domain traces pending |
| NFR-MNT-001 | pnpm/Turbo + uv locks; Alembic; generated client; Make/CI | Setup, lint/types, migration tests, OpenAPI diff, web build/E2E | E0–E5 hosted CI and E6 progress local checks recorded in verification reports |
| NFR-LOC-001 | English shell; UTC storage/wire; progress/history dates in Africa/Kampala | Configuration and browser history checks | Progress/history presentation implemented; wider localization review pending |

E4 numeric execution evidence: [verification report](E4_VERIFICATION.md).

E5 diagnostic/mastery evidence: [verification report](E5_VERIFICATION.md).

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
