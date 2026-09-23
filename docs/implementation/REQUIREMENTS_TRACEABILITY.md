# Requirements Traceability

Live implementation evidence for every requirement in the [SRD](../specifications/01_SRD.md). The [specification matrix](../specifications/14_Requirements_Traceability_Matrix.md) defines required coverage and evidence. Update this register with each implementation slice; completion requires passing acceptance evidence.

E0, E1 and E2 evidence is recorded below. Local synthetic journeys are not
production-pilot acceptance; delivery-provider and legal approval gates remain. See the [assessment](PHASE_0_ASSESSMENT.md).

| Requirement | Implementation | Tests / evidence | Status |
| --- | --- | --- | --- |
| FR-ID-001 | Email/phone OTP, purpose binding, five-attempt/ten-minute limits, per-contact/peer/device sends | `tests/integration/test_identity.py`, `tests/e2e/identity.spec.ts` | Local implemented; SES/SMS production gates pending |
| FR-ID-002 | Verified identifier linking with uniqueness, encryption and keyed lookup; existing identities never auto-merge | API linking, collision and one-identity tests | Local implemented |
| FR-ID-003 | Birth date, adult consent, separately verified guardian evidence/learner assent, withdrawal, policy gate | Minor/adult API and browser tests; ownership, idempotency and policy-change tests | Local implemented; approved wording and downstream learning-route integration pending |
| FR-ID-004 | Server-restricted S4 Mathematics/Physics profile and subject selection | Profile validation and browser journeys | Local implemented |
| FR-ID-005 | Opaque sessions, refresh rotation/reuse revocation, current/all logout | Expiry, family reuse and revocation API tests; browser logout | Local implemented |
| FR-ID-006 | — | — | Not started |
| FR-DIAG-001 | — | — | Not started |
| FR-DIAG-002 | — | — | Not started |
| FR-DIAG-003 | — | — | Not started |
| FR-DIAG-004 | — | — | Not started |
| FR-DIAG-005 | — | — | Not started |
| FR-REV-001 | — | — | Not started |
| FR-REV-002 | — | — | Not started |
| FR-REV-003 | — | — | Not started |
| FR-REV-004 | — | — | Not started |
| FR-REV-005 | — | — | Not started |
| FR-REV-006 | — | — | Not started |
| FR-GRD-001 | — | — | Not started |
| FR-GRD-002 | — | — | Not started |
| FR-GRD-003 | — | — | Not started |
| FR-GRD-004 | — | — | Not started |
| FR-GRD-005 | — | — | Not started |
| FR-GRD-006 | — | — | Not started |
| FR-GRD-007 | — | — | Not started |
| FR-GRD-008 | — | — | Not started |
| FR-GRD-009 | — | — | Not started |
| FR-MST-001 | — | — | Not started |
| FR-MST-002 | — | — | Not started |
| FR-MST-003 | — | — | Not started |
| FR-MST-004 | — | — | Not started |
| FR-MST-005 | — | — | Not started |
| FR-MST-006 | — | — | Not started |
| FR-WA-001 | — | — | Not started |
| FR-WA-002 | — | — | Not started |
| FR-WA-003 | — | — | Not started |
| FR-WA-004 | — | — | Not started |
| FR-WA-005 | — | — | Not started |
| FR-WA-006 | — | — | Not started |
| FR-CNT-001 | `services/content.py`, strict draft DTO, staff editor | Content API/schema/browser tests | Partial: single-choice create/edit complete; import and other response formats pending |
| FR-CNT-002 | Role checks and immutable author ownership; self-review blocked even with both roles | API self-review denial; SQL review guard; disabled author approval in browser | Local implemented |
| FR-CNT-003 | Return, approval, high-risk/disputed second review, retirement and append-only reviews | Full API/browser workflow; two-reviewer and retired-selection tests | Local implemented with synthetic content |
| FR-CNT-004 | Immutable approved versions, explicit successor drafts and normalized frozen mappings | API mutation rejection; direct SQL history/mapping tests | Partial: published content immutable; attempt/rubric pinning awaits assessment/grading |
| FR-CNT-005 | Submission and approval revalidate rights, mappings, weights, answer, solution and remediation | Field-specific 409 tests; approval revalidates changed curriculum references | Local single-choice path implemented; other formats and academic evidence pending |
| FR-CNT-006 | — | — | Not started |
| FR-OPS-001 | `services/observability.py`, `packages/analytics-schema/` | `tests/contract/test_foundation.py`, `tests/contract/test_identity_contract.py`, identity integration outbox assertions: safe operational and identity-event shape | Registration/identity/consent outbox events implemented; other learner analytics and dispatch pending |
| FR-OPS-002 | `services/health.py`, API health shell and worker smoke | Health success/degraded tests; real Redis/Celery test | Partial; alerts/dashboards pending |
| FR-OPS-003 | Atomic content/role audit, database history guards | Direct SQL audit rewrite rejection, role-action records and content events | Partial: content and local role actions; operations audit UI/retention pending |
| FR-OPS-004 | — | — | Not started |
| NFR-PERF-001 | — | — | Not started |
| NFR-PERF-002 | — | — | Not started |
| NFR-REL-001 | — | — | Not started |
| NFR-REL-002 | — | — | Not started |
| NFR-SCL-001 | — | — | Not started |
| NFR-SEC-001 | `services/config.py`, loopback Compose, generated ignored secrets | Fail-closed/redaction tests; source/dependency scans | Partial; production TLS/encryption pending |
| NFR-SEC-002 | Identity ownership, recent-auth/consent controls and staff content-role enforcement | Identity integration and cross-origin browser tests | Partial; content RBAC implemented; production MFA/role governance and downstream learning guards pending |
| NFR-ACC-001 | `apps/web/app`, `packages/ui` | Playwright keyboard retry and axe scan | Shell, onboarding and staff review axe/keyboard checks; assessment journeys pending |
| NFR-BW-001 | — | — | Not started |
| NFR-COMP-001 | Next.js shell | Chromium browser test | Partial; cross-browser learner matrix pending |
| NFR-OBS-001 | UUID web/API/worker correlation; console OTel; safe JSON logs | Unit redaction and real worker propagation tests | Foundation verified; authenticated/domain traces pending |
| NFR-MNT-001 | pnpm/Turbo + uv locks; Alembic; generated client; Make/CI | Setup, lint/types, migration tests, OpenAPI diff, web build/E2E | E0/E1 hosted CI passed; E2 verification tracked separately |
| NFR-LOC-001 | English shell; UTC database connections/Celery | Configuration inspected; no learner timestamps yet | Foundation only; Kampala presentation pending |
