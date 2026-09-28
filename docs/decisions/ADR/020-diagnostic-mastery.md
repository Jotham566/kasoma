# ADR-020: Synthetic diagnostic and initial mastery evidence

Date: 28 September 2026
Status: Accepted within delegated implementation discretion
Requirements: FR-DIAG-001–005, FR-MST-001–003/005, FR-OPS-001, NFR-SEC-002

Use the existing assessment/grading transaction and consent/ownership lock. Add a
DIAGNOSTIC session kind and nullable topic for a subject-wide plan; retain existing
REVISION defaults and contracts. A partial unique index permits one active diagnostic
per learner/subject. Pin 15 as the initial maximum-length diagnostic configuration;
there is no invented early-stop confidence threshold. Choose one STANDARD (CORE)
item per available topic first. Then prefer under-covered competencies and the least
confident skill, using foundational items after weak responses and challenging
application/interpretation items after strong responses where inventory permits.
Fallback stays within approved eligible content. Stable IDs resolve ties. Pin served
assignments; exclude recent item identities across versions. Insufficient content
fails explicitly instead of silently repeating or falling below ten items.

Diagnostic answers use the same immutable attempt and grade storage, but return a
separate SAVED acknowledgement. No scores or corrective feedback are exposed during
the diagnostic through session, replay or grade routes. Worked solutions remain
blocked for diagnostic attempts even after completion. Completion exposes a frozen
initial result with skill estimates, confidence and a first evidence-seeking practice
recommendation; full adaptive revision, reassessment and progress UX remain later work.

The mastery module owns additive evidence/projection/history writes. Deterministic
grades update mastery synchronously in the same transaction. Immutable evidence
records contain original grade/mapping inputs, all effective weights, the complete
versioned baseline configuration and input hashes. Use specification 05 unchanged,
including ADR-017's content-difficulty-v1 mapping. Repeated delivery creates no extra
evidence. A pure replay function verifies derived fields before calculation; database
uniqueness and append-only triggers enforce durability. Current consent is required
before lazily reconciling legacy grades; historical grade snapshots remain unchanged.

All academic fixtures and rankings remain synthetic. Neutral curriculum importance
is only a software-fixture default, not an academic judgment. Teacher calibration,
real curriculum configuration, recommendation approval and release gates remain open.
No production enablement, cloud provider, model evaluation or real data is introduced.

Migration is additive with forward-fix rollback: retain new learning evidence and
numeric/diagnostic-aware readers. Do not destructively downgrade or serve diagnostic
records through older revision-only code. Test concurrency, consent withdrawal,
IDOR, answer leakage, rollback, immutable records, replay and browser resume.

Evidence includes a normalization timestamp and reason code; projection snapshots
retain exact attempt IDs for historical replay. Completion records a hash of the
initial recommendation inputs alongside algorithm/configuration versions. Candidate
discovery does not lock the entire inventory; the chosen version is locked and
revalidated by the shared delivery/submission boundary. Migrations 0006/0007 preserve
existing data; 0007 tightens integrity after the first local 0006 application.

Diagnostic selection also excludes unserved items reserved in other unexpired active
plans, preventing a parallel practice plan from revealing feedback for a diagnostic
question. Abandoned/expired unserved reservations do not block inventory.
