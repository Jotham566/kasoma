# ADR-018: Bounded deterministic numeric answers

Date: 23 September 2026
Status: Accepted within delegated implementation discretion
Owners: Engineering
Requirements: FR-GRD-002/005/007, FR-CNT-001/004/005, FR-REV-003, NFR-MNT-001

## Decision

Extend the existing reviewed-content and assessment path with NUMERIC. Existing
choice requests and stored grades remain compatible. Every numeric item explicitly
specifies its expected value, canonical unit, allowed unit conversions, absolute
and relative tolerance, significant-figure policy and accepted input forms. Reviewers
approve these values; the grader never infers them from question prose.

Use bounded decimal/scientific notation and integer fractions. Parse with exact
rational arithmetic, not binary floats or expression evaluation. Maximum input is
64 characters; decimal exponent magnitude is at most 12 and absolute value at most
10^12. Reject non-finite values, zero denominators, expressions, unsupported forms
and unknown units before saving an attempt. Unit labels are case-sensitive and
selected from the reviewed list; the empty label represents dimensionless values.
Conversions explicitly define canonical = value * factor + offset, with positive
factor. The canonical label must have factor 1 and offset 0. No global or inferred
unit-conversion catalogue is introduced.

Match when abs(converted - expected) <= max(absolute_tolerance,
relative_tolerance * abs(expected)). Boundaries are inclusive and relative tolerance
is in [0,1]. Tolerances are in canonical units and apply before any rounding; there
is no hidden rounding rule. Equivalent enabled representations have equal numeric
value. Scoring remains the explicitly authored ALL_OR_NOTHING policy.

Significant figures are either IGNORE or EXACT with a required count (1–12).
Count the entered mantissa's digits from its first nonzero digit, retaining trailing
zeros after a decimal point. Integers without a decimal point have trailing zeros
removed; scientific notation retains the mantissa's trailing zeros. For zero,
count decimal places (minimum one). Show this convention to authors and learners.
EXACT excludes fractions because their significant figures are ambiguous. Apply
precision to the entered quantity, before the unit conversion. Compare numeric
value and required precision independently; feedback does not invent reasoning.

Return only permitted forms, unit labels and precision instructions in learner
response_spec. Expected values, conversions and tolerances remain staff-only.
Store the original bounded numeric representation and selected unit in an immutable
response JSON column; retain existing choice columns/rows unchanged. Grades retain
the pinned content hash and numeric grader version, with safe structured feedback.
No answer text enters logs or analytics. Current consent, ownership, retirement,
idempotency and atomic attempt/grade/outbox rules continue to apply.

## Contracts, migration and exclusions

Add numeric alternatives to existing content/answer/player contracts and regenerate
the client. The web and API changes deploy together; old choice callers continue to
work. Migration 0005 adds nullable numeric-response storage and makes the legacy
choice column nullable only for numeric rows; database checks require exactly one
response representation and a numeric item for numeric answers. No backfill or
historical mutation. Roll back code while retaining new evidence; no destructive
downgrade. Before numeric documents are published, the additive migration remains compatible
with old choice code. Once numeric documents exist, prefer a forward fix or retain
numeric-aware readers while disabling affected routes. Stopping authoring alone
is insufficient to roll back to pre-numeric readers; never delete new evidence.

No symbolic algebra, natural-language number parsing, handwritten solutions, model
calls, partial-credit inference or new production providers. Publication remains
synthetic-only in development. This slice does not claim academic benchmark approval.

## Verification and approval

Test absolute/relative boundaries, zero/negative/scientific/fraction values, unit
factors and offsets, significant figures, hostile/oversized input, publication
validation, historical choice compatibility, replay/rollback and browser authoring
through numeric feedback. Add property tests for exact conversion equivalence.
The user authorized the next implementation and best-practice choices; no prior
ADR or academic answer is overridden.
