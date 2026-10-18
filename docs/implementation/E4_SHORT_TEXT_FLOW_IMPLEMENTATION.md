# Short-text learner flow implementation

Started 18 October 2026. Requirements: FR-GRD-003/004/005, FR-MST-001, FR-ID-003/006,
NFR-SEC-002. Decision: [ADR-050 proposal](../decisions/ADR/050-short-text-pending-and-eligibility.md).

This is a work-in-progress checklist for the full approved learner path, not a feature
acceptance report. Academic calibration, reviewer qualification, genuine report authority
and production release retain their separate external gates.

- [x] Strict definitive rubric-result shape and evidence/feedback projection.
- [x] Encrypted answer/result persistence, pinned rubric/band and atomic submission receipt/work.
- [x] Synthetic selection/assignment eligibility; normal startup remains disabled.
- [x] Bounded fake dispatch outside locks and current authorization/content/band rechecks.
- [x] Synthetic grade/mastery/publication/audit atomic transaction; neutral fallback without score.
- [x] Owned pending/result retrieval, resume/history/polling and neutral learner action.
- [x] Diagnostic sealing; complete objective channel regression remains in progress.
- [ ] Independent blinded expert review, exact agreement and automatic sticky disablement.
- [ ] Owned exports, exact holds, retention inventory, restricted role and populated recovery.
- [ ] Concurrency/crash/withdrawal/retirement/disablement/encryption/three-engine acceptance.

Result contract evidence: `.local/rubric-result-contracts.log`; `make format lint test-unit
openapi-check` passes 808 unit/contract and 35 tooling cases. All new result tests are
synthetic; no model or learner dataset is accessed. The formatter is not called by
learner routes. No HTTP schema or SQL assignment guard changes at this stage.

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

## Browser and failure acceptance — 18 October 2026

`make format lint build test-web-short-text` passes nine executions across pinned
Chromium, Firefox and WebKit: pending-to-result polling/resume, 320-pixel neutral
fallback/lost acknowledgement/review request, and a sealed 15-question written
diagnostic. Axe checks pass; pending and mobile neutral captures were inspected under
`.local/ui-review`. An initial accessible-name failure was fixed by separating the
textarea label from its counter. The full existing browser regression then exposed
colliding report/hint React keys; distinct keys fix the duplicate report control, and
the unchanged regression is being rerun. These are engine checks, not physical-device,
approved-brand or academic acceptance.

Fourteen focused PostgreSQL cases pass, including duplicate workers, rollback after
publication and report withdrawal after the second pass. A later broker-failure case
initially counted the session-start receipt as an attempt receipt; the assertion now
targets the exact attempt. Final focused checks additionally exercise SQL rejection
when publication or mastery is omitted. No assertion was weakened to permit partial
publication or score-bearing fallback.

The isolated logical recovery fixture now includes an actual encrypted short-text
attempt/result and frozen owned export. The first extended restore passes (63 tables,
602 rows, 281 ms, no cleanup failures); an additional explicit restored decryption
check is under verification. It creates and drops only its generated disposable
databases. Production PITR/RPO/RTO and object-storage recovery remain unproved.

Source/dependency security checks pass. Full backend/browser regression, final recovery,
rebuilt-container smoke and current vulnerability-database scanning remain in progress.
The additive migration has been applied to the persistent review database during smoke
verification; no reset or deletion is used. Independent blinded expert review, rolling
disablement and genuine report/safety/model authorities remain mandatory before real
learner scoring; the normal runtime has none of those authorities and remains disabled.

Later focused verification passes 18 PostgreSQL/API cases, including account-bound
120/minute feedback reads, failed broker acknowledgement with exact receipt replay,
and SQL rejection of grade commits missing publication or mastery. `make test-unit`
passes 831 unit/contract and 35 tooling cases. Explicit restored decryption passes
with 63 tables/602 rows and a 1,510 ms local restore, with no cleanup failures.
The restricted-login integration also exercises a real encrypted model publication.

The full existing browser matrix passes 90 executions after the React-key fix. Its
subsequent short-text Firefox profile was invalidated by an overlapping native build
replacing `.next` route manifests; that is an orchestration failure, not a passing
run. Repeat browser verification against a finished, stable build before promotion.
The scanner's default database mirror stalled; its scan was stopped, and the same
Trivy version/thresholds are being retried using the alternative official GHCR source.

## Final local verification in progress

- `make e2e`: **99 passed** against the stable build (90 existing and nine new
  executions across all three engines). Log: `.local/short-text-stable-browser-matrix.log`.
- `make check-docs test-short-text-flow test-runtime-role`: **18 flow cases and the
  real restricted-login case pass**, including actual encrypted publication with
  runtime privileges. Log: `.local/short-text-final-flow-role.log`.
- `make format lint test-unit check-ci-profile`: **831 unit/contract and 35 tooling
  cases pass**, including grading queue routing and hard-limit assertions.
  Log: `.local/short-text-queue-checks.log`.
- `make migrate seed`, rebuilt images and `make container-smoke` pass. The latest
  queue-aware stack has all eight services healthy and verifies an owned worker-built
  export plus minimized metrics through the web/API. Logs:
  `.local/short-text-queue-images.log`, `.local/short-text-queue-container-smoke.log`.
- `make security security-source`, generated contracts and documentation checks pass.
  Logs: `.local/short-text-security.log`, `.local/short-text-final-contract-security.log`.
- Populated logical recovery with explicit restored decryption passes; log:
  `.local/short-text-final-verification.log`.

The broad backend run passes **307 integration cases** in 901.92 seconds; it was
collected before the final four flow cases and three queue contract cases, which pass
in the later focused and 831-case unit runs above. Log: `.local/short-text-full-backend.log`.
The current rebuilt-image vulnerability scan remains in progress while downloading
the fresh database. Commit/push the locally verified candidate for hosted verification;
promote only after the remaining checks pass.
No new main promotion, complete short-text feature or academic acceptance is claimed.
