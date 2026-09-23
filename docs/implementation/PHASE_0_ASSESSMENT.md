# Phase 0 assessment — 23 September 2026

Read-only assessment completed before implementation. Baseline: commit
`0ceef70`; working tree clean. Read AGENTS.md, both product documents, all 19
specification documents, every tracked configuration/script and the live register.
No application, runtime manifests, migrations, application tests or CI existed.
Compose was empty and runtime Make targets deliberately failed. Documentation
checks passed (29 documents, all 61 SRD requirements represented).

## Scope and gap analysis

The approved outcome is the S4 Mathematics/Physics learning loop across six frozen
clusters, with 250–400 independently approved items. Web is complete; WhatsApp is
linked five-question practice. No mature-product portals, simulations, photo
solving, native applications, full Exam Mode or advanced knowledge tracing.

| Weeks | Requirements / work | Dependencies and acceptance gates |
| --- | --- | --- |
| 1 | E0: NFR-MNT-001, NFR-OBS-001; security/operations foundations | Locked setup; healthy web/API/DB/Redis; generated client; clean migration; correlated worker; fake-only tests; CI |
| 2 | FR-ID-001–005, FR-CNT-001–005, FR-OPS-003 | OTP abuse controls, consent/assent, ownership/RBAC, immutable independent approval; 60 reviewed items |
| 3 | FR-REV-003, FR-GRD-001–002/005, FR-MST-001, FR-OPS-001 | Approved item → immutable attempt → deterministic grade/outbox; idempotency; 100 items |
| 4 | FR-DIAG-001–005, FR-MST-002–003 | 10–15 items, coverage, resume, initial estimates; 125 items |
| 5 | FR-REV-001–006, FR-GRD-006–009, FR-MST-004–006 | Complete adaptive loop, reason, gated solutions, unseen reassessment; 150 items |
| 6 | FR-GRD-003–005, FR-CNT-001/006, FR-OPS-004 | Frozen expert benchmark, dual-pass calibrated grading, fallback; 190 items |
| 7–8 | FR-WA-001–006, FR-ID-006, FR-OPS-001–004; NFR-ACC/BW/COMP/LOC | Shared services, replay/signature/STOP tests, export/deletion, all capabilities; ≥250 balanced items; alpha |
| 9 | NFR-PERF-001–002, NFR-SCL-001, NFR-SEC-001–002, NFR-REL-001–002 | 50 concurrent learners, resilience/security scans, provider ADR, restore evidence |
| 10–12 | All requirement acceptance and release evidence | Beta, unseen reassessment, calibration, support/safeguarding rehearsal, zero S1/S2, owner sign-offs |

All rows initially lack code and application evidence. Full per-ID status remains
in REQUIREMENTS_TRACEABILITY.md. Relative weeks are binding; a calendar kickoff,
workstream owners and team capacity have not been recorded. Do not invent them.

## Critical path and safeguards

Schema and independently approved content → deterministic assessment → immutable
evidence → mastery/recommendation → reassessment → channel reuse. Academic mapping,
rights clearance, expert scoring and content throughput are human dependencies.
Only synthetic fixtures may be seeded; fixtures are not academic release evidence.

Under-18 guardian consent plus learner assent precedes learning and linking. No
learner data before privacy notices, DPIA, PDPO obligations, processor agreements
and cross-border review are approved. Deny access by default; redact secrets and
answers; enforce independent publication and deterministic grading. Production
provider selection is due by Week 8 under D-014; SES/SMS decisions do not authorize
cloud calls during bootstrap. Backups require 35-day PITR and a tested restore.

## Differences and open question

D-014 supersedes Azure hosting and managed-Redis defaults; D-009 retains Celery
5.6.x. The frozen clusters supersede roadmap wording about selecting topics.
Existing ADRs stay canonical in specification 13, linked from the ADR index.

OPEN-QUESTION E0-01: roadmap Week 5 requires ≥85% short-text expert agreement,
whereas backlog Week 6 implements short-text grading. No decision resolves the
milestone mismatch. Before planning that affected slice, Product/Academic must
choose earlier benchmark/implementation capacity or explicitly revise the gate.
Recommendation: establish the benchmark early and resolve capacity at Week 2;
never silently move or weaken the gate. Foundation and deterministic work continue.

## First vertical slice and implementation discretion

Web health shell → generated OpenAPI TypeScript client → FastAPI safe dependency
health → PostgreSQL/Redis; worker smoke task propagates the same correlation ID.
Add the approved pnpm/Turborepo layout, Python 3.12/uv lock, Compose infrastructure,
Alembic baseline, local-only seed foundation, provider contracts/fakes, typed
configuration, observability and checks. No authenticated learner endpoints yet.

Use uv under specification 15's explicit bootstrap discretion. Keep all credentials
in ignored local files with no source defaults. Automated tests block external
network calls; no model evaluation runs as part of this task. Ollama stays native
with explicit local endpoints. Bootstrap must refuse production startup until
production controls exist. Health is an operational extension to the API contract,
recorded with the bootstrap decision. Acceptance evidence must distinguish local
checks from a hosted CI run and report missing tools without claiming completion.
