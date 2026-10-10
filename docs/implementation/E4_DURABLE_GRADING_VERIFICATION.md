# Durable grading work — integration preparation

Date: 10 October 2026. Requirements: FR-GRD-003/004/005, FR-ID-006, NFR-SEC-002,
NFR-MNT-001. ADR-050 remains proposed; short-text learner delivery remains disabled.

## Implemented boundary

Migration 0026 adds a grading command/current-state table and exact immutable transition
history. Ownership derives from the referenced immutable attempt. Queue replay preserves
the original command and correlation; concurrent workers lock and skip claimed rows.
One claim lasts at most 30 seconds and cannot exceed the five-minute queue deadline.
Expiry returns a neutral outcome, never another inference budget. SQL prevents lease
renewal, terminal rewriting, history mutation and grade/work publication disagreement.

The store has no model provider, public route or scheduling registration. Its enqueue
method is an internal substrate: the future assessment service must validate response
format, eligibility, ownership and consent before calling it in the attempt transaction.
The migration does not change existing short-text assignment or response-format guards.

Owned exports add allowlisted grading_work and grading_history groups, with attempt,
status and timestamps; history also includes record ID and revision. Correlation IDs,
claim tokens, internal reasons and whole snapshots are excluded. Existing diagnostic
sealing applies. Deletion-impact previews count both tables under learning-evidence
anonymization review. This does not enable erasure or change approved retention rules.

## Evidence

`make format lint test-grading-work` passes 24 cases: 17 transition cases and seven
actual PostgreSQL integration cases. Fixtures migrate from foundation through head in
isolated synthetic schemas, preserving existing migrations and guards. Integration
coverage includes two competing claim transactions, queue replay, rollback of work and
history, expiry/late-worker rejection, SQL mutation denial, deferred atomic-publication
failure, owned projection and foreign-owner exclusion.

The substrate tests use valid synthetic ungraded objective attempts, without disabling
any trigger. They prove durable work behavior independently of short-text enablement;
they do not prove learner short-text submission, model grading or academic accuracy.

Logs: `.local/grading-work-store-checks.log` and `.local/grading-work-privacy-checks.log`.
`make migrate test` is running; full backend acceptance is pending. OpenAPI comparison and source-secret checks pass. The extended `make test-runtime-role`
also passes through a real restricted login: enqueue, claim and neutral completion
create three exact history rows without schema privileges. Work deletion and history
rewrites remain denied. FOR UPDATE requires UPDATE privilege on an attempt column;
only immutable `attempts.id` is granted, and the existing trigger rejects actual edits.
The temporary role is removed and its password is absent from captured output. Log:
`.local/grading-work-runtime-role.log`. Recovery and hosted verification remain open.

## Required integration gates

- Exact-record legal holds for immutable transition evidence and defined preservation
  of the current projection; approved retention processor integration.
- Maintain the verified restricted-role boundary when adding worker/publication behavior.
- Atomic encrypted attempt, command and idempotency receipt persistence through the
  actual consent-gated assessment service.
- Worker dispatch only after claim commit; post-inference consent/content/band checks;
  bounded model execution and claim-expiry reconciliation after worker termination.
- Academic eligibility/audit controls and grade/mastery publication in one transaction;
  neutral fallback creates no grade or mastery evidence.
- Learner submission/polling/resume/history and an executable equivalent/review path,
  with generated contracts and browser acceptance.

No live inference, Gemini, real learner data or production provider is used.

## Grading-history holds in verification

Migration 0027 adds exact GRADING_HISTORY holds through the existing independent ADMIN
request-review path. Both API and SQL verify record ownership; deletion checks the
hold, and immutable history still cannot be edited or erased after release. A held
queued snapshot does not stop a later claim/neutral transition. The administrator
selector exposes the type; stale seven-type limitation wording is replaced with an
accurate incomplete-coverage statement. Existing hold types remain available.
Use `make test-grading-work` for transition/storage/hold checks and `make test-web-privacy`
for all three browser engines' privacy journeys. Verification is in progress.

## Latest local verification

- `make format lint test-grading-work`: 26 cases pass, including both new history-hold
  cases (exact replay, cross-owner/wrong-staff denial, continued workflow, immutable
  held snapshot and release without erasure permission).
- `make migrate build test-web-privacy`: both migrations apply; the web build and six
  privacy executions pass (two each in Chromium, Firefox and WebKit). These check the
  selector and existing owned export/review flows, not a learner short-text journey.
- `make recovery-drill`: 58 tables/291 rows restored in 948 ms with no cleanup failures.
  The fixture contains an ungraded synthetic attempt, neutral grading work and three
  exact transitions; whole-table hashes match, restored immutability rejects changes,
  pgvector and frozen export checks pass. Object-storage restore and production RPO/RTO
  remain unverified. Only drill-created databases were backed up/restored/removed.
- `make containers container-smoke`: the review stack refreshed and all eight services
  pass health, scheduled export/frozen retry and request-metrics checks. A subsequent
  source-only runtime-assert correction is pending inclusion in the next image refresh.
- A Bandit failure identified a runtime assert in the earlier transition component.
  It is replaced with explicit validation; Bandit and local secret checks now pass.
  The final dependency audit and full backend regression are still running.

Logs: `.local/grading-history-hold-integration.log`,
`.local/grading-history-privacy-browsers.log`, `.local/grading-work-recovery.log`,
`.local/grading-history-container-refresh.log`, `.local/grading-history-final-quality.log`.
These results do not enable learner/model execution or constitute academic acceptance.

Final `make format lint test-unit openapi-check security` passes: 747 unit/contract
cases, 35 tooling checks, formatting/types, generated contracts, Bandit and Python/
JavaScript dependency audits with no known vulnerabilities. Full native integration
and hosted regression remain in progress. A final image rebuild/scan/smoke is running
to include the explicit-validation correction in the local containers.

## Completed local gate

The full `make migrate test` run passes: 747 unit/contract cases, 35 tooling checks
and 266 integration cases in 715.62 seconds. It was collected before the two new
history-hold cases and restricted-role extension; those pass in the separate 26-case
focused run and restricted-login run described above. The post-correction unit/security
run also passes. This preserves the evidence boundaries rather than counting unrun
cases into the broad regression.

Final `make containers security-containers container-smoke` passes after including the
explicit-validation fix: rebuilt API/web images have no HIGH/CRITICAL findings, all
eight services are healthy, and scheduled export/frozen retry plus live metrics probes
pass. Source secret scanning passes. Logs: `.local/grading-work-full-backend.log`,
`.local/grading-history-final-containers.log`, `.local/grading-history-secret-scan.log`.
The local slice is ready to commit; exact-head hosted acceptance remains pending.
No worker, learner assignment, model scoring, deletion or production enablement is claimed.
