# Current sprint: export acceptance and learner UI completion

Updated 9 October 2026. Main remains `bb2f4eb`. Export candidate `c08341b` and UI follow-ups
through `be42dbd` are complete locally on `codex/async-personal-exports`. They are being pushed
together for final-head hosted CI, superseding candidate run 37979693427 without claiming it
passed. Native container scanning and the latest full-stack export smoke now pass. All data is
synthetic; no production, academic or MVP completion is claimed.

## Local review stack

All eight Compose services are running and healthy: web, API, ordinary worker, dedicated export
worker, PostgreSQL/pgvector, Redis, private MinIO and Mailpit. Keep them running for user review.

- UI: http://localhost:3000
- Local email capture: http://localhost:8025
- Use fictional details only; real learner/guardian data is prohibited.
- Synthetic choice, numeric, diagnostic, hints, multiple-choice and reassessment fixtures are seeded.
- `make seed` now passes catalog and private storage initialization.

Earlier MinIO download failures are resolved. The live browser installer completed pinned Chromium
and its headless shell and is downloading Firefox; WebKit follows. Do not restart a live download
because output is quiet. See the [local runbook](../runbooks/LOCAL_DEVELOPMENT.md).

## Candidate export slice

Requirements: FR-ID-006, FR-OPS-002/003, NFR-SEC-001/002, NFR-OBS-001 and NFR-MNT-001.
[ADR-048](../decisions/ADR/048-asynchronous-owned-export-delivery.md) remains proposed until its
full acceptance gates pass. Candidate API, learner controls and scheduler/worker wiring are
active locally; do not promote unverified work to main.

Implemented: recent-owner queue/status/frozen download, additive job/generation constraints,
consistent bounded projection, authorization rechecks, encrypted publication, bounded cleanup,
separate hard-limited worker, exact-length cancellable transport, native browser downloads and
minimized operational metrics. Existing synchronous exports remain compatible. This does not
enable deletion or change legal accountability retention.

Current evidence:

- 608 unit/contract and 32 tooling cases pass; lint, formatting and types pass.
- 59 storage cases pass, including actual signed MinIO reads, private-access denial and owned cleanup.
- 41 focused lifecycle/API cases and 15 worker checks pass, including real process hard-stop/recovery.
- Complete native `make migrate test security` passes: 606 unit/contract cases, 32 tooling cases
  and 245 integration cases, including the previously unavailable real MinIO checks. Two later
  smoke-probe unit cases also pass in the separate 608-case unit run. Dependency/security checks pass.
- Full pinned Chromium passes 30 cases across both shards, including native cancellation/corruption,
  frozen retry, privacy review and operational metrics. Firefox/WebKit and hosted regression remain open.
- Populated synthetic logical recovery passes again (56 tables/285 rows, 256 ms); object-storage restore
  and production PITR/RPO/RTO are explicitly unverified.
- `make container-smoke` passes both eight-service health and a real scheduled export through
  Next/API/Beat/export-worker/MinIO, with exact-length frozen retry and scoped session logout.
- Source secret scanning and generated OpenAPI/client checks pass.

Full chronology and evidence boundaries: [export verification](E8_ASYNC_EXPORT_VERIFICATION.md).
The isolated content-admin browser check also passes. Container vulnerability scanning now passes for API and web with no HIGH/CRITICAL findings.
The initial five-minute database-download timeout was resolved by the configurable 30-minute bound.
Before promotion: finish the remaining browser matrix, container security and hosted CI; resolve any failures, then record ADR status and promotion evidence.

## Learner UI work

Requirements: FR-ID-001/003/004/005, FR-DIAG-004/005, FR-REV-005/006, FR-GRD-006,
FR-MST-004/005 and NFR-ACC-001/BW-001/COMP-001/LOC-001/MNT-001.

The running web now includes shared learner navigation and keyboard skip access, a responsive
home/recommendation layout, onboarding cards/fields and consent-gated diagnostic navigation,
and clearer practice/diagnostic questions with a server-derived saved-answer progress bar.
Synthetic notices and existing consent, scoring, hint/solution, sealing and replay rules remain.
Staff routes remain separate. No external assets, fonts, analytics or provider dependencies were added.

Thirty Chromium cases pass, including 320/1280-pixel home/onboarding checks, 200% text reflow,
44-pixel navigation targets, keyboard/axe, existing learning journeys and saved-progress assertions.
Desktop/mobile captures were inspected and retained under `.local/ui-review`. The current web image
is deployed locally; source-only rebuilds reuse the frozen dependency layer. This is not physical-
device, screen-reader, approved-brand or pilot acceptance.

Progress/history presentation passes lint/types/build and all 30 Chromium cases, including
320-pixel reflow, touch targets, owned paging and sealed diagnostic resume. Screenshots were
inspected without clipping; its rebuilt local web is healthy.
Privacy/channel presentation passes lint/types/build and all 30 Chromium cases, including mobile
privacy axe/reflow, frozen export retry, channel STOP/unlink and Kampala expiry. Captures reviewed.
Shared staff navigation passes lint/types/build, 30 Chromium journeys, isolated editor and
source/contract checks. Desktop/mobile captures reviewed; the rebuilt web image is available.
Operations/flags/import presentation passes lint/types/build and 30 Chromium journeys;
authenticated operations captures reviewed at desktop and 320 pixels.
Content editor presentation passes lint/types/build, mobile/axe/exact-save-reload and all
30 Chromium journeys. Captures reviewed; human usability acceptance remains open.
Next UI work: final learner action hierarchy and supported-device acceptance;
review action hierarchy and supported-device usability. Keep API state authoritative, sparse-evidence
wording accurate and the 250,000-byte cold-question transfer gate unchanged.
[Plan and evidence](E6_LEARNER_UI_READINESS.md).

## Verified main baseline

Main `bb2f4eb` passed hosted CI 37962081120 for the private storage adapter: 721 Python cases,
66 browser executions and the full recovery/security/container pipeline. Its completed branch was
removed. Earlier merged evidence includes [incremental exports](E8_EXPORT_ENCODING_VERIFICATION.md),
[encrypted artifact format](E8_PRIVATE_EXPORT_ARTIFACT_VERIFICATION.md),
[objective load](E9_OBJECTIVE_LOAD_VERIFICATION.md), [mobile reflow](E9_MOBILE_REFLOW_VERIFICATION.md),
[reviewed rubrics](E2_REVIEWED_RUBRICS_VERIFICATION.md) and
[accountability holds](E8_ACCOUNTABILITY_HOLDS_VERIFICATION.md).
See [requirements traceability](REQUIREMENTS_TRACEABILITY.md) for the complete historical register.

## Remaining MVP and release gates

Learner short-text integration/fallback and academic calibration, aggregate telemetry, complete
hold coverage, deletion/anonymization and accountability-retention processors remain incomplete.
Do not expand into mature whitepaper features or silently reduce these requirements.

The [release register](RELEASE_GATES.md) retains external gates: kickoff/capacity, approved academic
mappings/rights/inventory/benchmark, privacy and safeguarding approval, Week 8 providers, production
security/operations, PITR/RPO/RTO, supported devices and pilot sign-offs. Synthetic tests are not
substitutes. No kickoff date or delivery-week acceptance is inferred from engineering progress.
