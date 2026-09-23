# Requirements Traceability

Live implementation evidence for every requirement in the [SRD](../specifications/01_SRD.md). The [specification matrix](../specifications/14_Requirements_Traceability_Matrix.md) defines required coverage and evidence. Update this register with each implementation slice; completion requires passing acceptance evidence.

E0 foundation evidence is recorded below. Partial foundation support is not full
MVP acceptance. All learner requirements remain unimplemented; synthetic fixtures
are not academic or learner-journey evidence. See the [assessment](PHASE_0_ASSESSMENT.md).

| Requirement | Implementation | Tests / evidence | Status |
| --- | --- | --- | --- |
| FR-ID-001 | — | — | Not started |
| FR-ID-002 | — | — | Not started |
| FR-ID-003 | — | — | Not started |
| FR-ID-004 | — | — | Not started |
| FR-ID-005 | — | — | Not started |
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
| FR-CNT-001 | — | — | Not started |
| FR-CNT-002 | — | — | Not started |
| FR-CNT-003 | — | — | Not started |
| FR-CNT-004 | — | — | Not started |
| FR-CNT-005 | — | — | Not started |
| FR-CNT-006 | — | — | Not started |
| FR-OPS-001 | `services/observability.py`, `packages/analytics-schema/` | `tests/contract/test_foundation.py`: safe operational-event shape | Foundation only; learner analytics pending |
| FR-OPS-002 | `services/health.py`, API health shell and worker smoke | Health success/degraded tests; real Redis/Celery test | Partial; alerts/dashboards pending |
| FR-OPS-003 | — | — | Not started |
| FR-OPS-004 | — | — | Not started |
| NFR-PERF-001 | — | — | Not started |
| NFR-PERF-002 | — | — | Not started |
| NFR-REL-001 | — | — | Not started |
| NFR-REL-002 | — | — | Not started |
| NFR-SCL-001 | — | — | Not started |
| NFR-SEC-001 | `services/config.py`, loopback Compose, generated ignored secrets | Fail-closed/redaction tests; source/dependency scans | Partial; production TLS/encryption pending |
| NFR-SEC-002 | No learner/admin routes; production startup rejected | Unavailable routes and production config rejection tests | Foundation only; ownership/RBAC pending |
| NFR-ACC-001 | `apps/web/app`, `packages/ui` | Playwright keyboard retry and axe scan | Shell verified; learner journeys pending |
| NFR-BW-001 | — | — | Not started |
| NFR-COMP-001 | Next.js shell | Chromium browser test | Partial; cross-browser learner matrix pending |
| NFR-OBS-001 | UUID web/API/worker correlation; console OTel; safe JSON logs | Unit redaction and real worker propagation tests | Foundation verified; authenticated/domain traces pending |
| NFR-MNT-001 | pnpm/Turbo + uv locks; Alembic; generated client; Make/CI | Setup, lint/types, 24 Python tests, OpenAPI diff, web build/E2E | Foundation verified locally, including containers and fresh source; hosted CI pending |
| NFR-LOC-001 | English shell; UTC database connections/Celery | Configuration inspected; no learner timestamps yet | Foundation only; Kampala presentation pending |
