# Changelog

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
