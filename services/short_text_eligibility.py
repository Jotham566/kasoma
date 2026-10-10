"""Versioned calibration/audit policy; not approval authority or learner enablement."""

from datetime import datetime
from typing import Annotated, Final, Literal
from uuid import UUID

from pydantic import AwareDatetime, ConfigDict, Field, model_validator

from services.short_text_validation import StrictContract

POLICY_VERSION: Final = "short-text-calibration-v1"
AUDIT_WINDOW = 100
Version = Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")]
Count = Annotated[int, Field(ge=0, le=1_000_000_000)]


class FrozenContract(StrictContract):
    model_config = ConfigDict(frozen=True, revalidate_instances="always")


class GradingScope(FrozenContract):
    subject_id: UUID
    topic_id: UUID
    language: Literal["en"]
    model_version: Version
    prompt_version: Version
    configuration_version: Version


class CalibrationBand(FrozenContract):
    """Trusted report projection: its IDs must be resolved/authorized by persistence."""

    id: UUID
    scope: GradingScope
    policy_version: Literal["short-text-calibration-v1"] = POLICY_VERSION
    minimum_characters: int = Field(ge=1, le=2000)
    maximum_characters: int = Field(ge=1, le=2000)
    benchmark_id: UUID
    report_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    benchmark_cases: int = Field(ge=1, le=1_000_000_000)
    benchmark_within_tolerance: Count
    held_out_cases: int = Field(ge=1, le=1_000_000_000)
    held_out_exact: Count
    critical_errors: Count
    subgroup_review: Literal["PENDING", "APPROVED", "HARMFUL"]
    approval_id: UUID | None = None
    approved_at: AwareDatetime | None = None
    enabled: bool = False

    @model_validator(mode="after")
    def coherent(self) -> "CalibrationBand":
        if (
            self.minimum_characters > self.maximum_characters
            or self.benchmark_within_tolerance > self.benchmark_cases
            or self.held_out_exact > self.held_out_cases
            or (self.approval_id is None) != (self.approved_at is None)
        ):
            raise ValueError("Incoherent calibration evidence")
        return self


class AuditOutcome(FrozenContract):
    grade_id: UUID
    exact: bool
    critical_error: bool
    completed_at: AwareDatetime


class AuditState(FrozenContract):
    band_id: UUID
    returned_grades: Count
    assigned_audits: Count
    completed_audits: Count = 0
    # Durable disablement is sticky, even after the triggering audit leaves the window.
    disabled: bool = False
    recent: tuple[AuditOutcome, ...] = Field(default=(), max_length=AUDIT_WINDOW)

    @model_validator(mode="after")
    def coherent(self) -> "AuditState":
        if not self.completed_audits <= self.assigned_audits <= self.returned_grades or len(
            self.recent
        ) != min(self.completed_audits, AUDIT_WINDOW):
            raise ValueError("Incoherent audit counts")
        if len({row.grade_id for row in self.recent}) != len(self.recent):
            raise ValueError("Duplicate audit evidence")
        if any(
            a.completed_at > b.completed_at
            for a, b in zip(self.recent, self.recent[1:], strict=False)
        ):
            raise ValueError("Audit evidence must be ordered by completion")
        return self


Reason = Literal[
    "ELIGIBLE_CANDIDATE",
    "DISABLED",
    "UNAPPROVED",
    "SCOPE_MISMATCH",
    "LENGTH_MISMATCH",
    "BENCHMARK",
    "CALIBRATION",
    "SUBGROUP",
    "CRITICAL_ERROR",
    "AUDIT_COVERAGE",
    "AUDIT_AGREEMENT",
]


def audit_required(ordinal: int) -> bool:
    """Assign the first and every tenth subsequent return: ceil(N/10) in every prefix.

    Allocate ordinals and assignments atomically with publication under the band lock.
    Neither model prompts nor blinded expert review may reveal the sampling ordinal.
    """
    if type(ordinal) is not int or not 1 <= ordinal <= 1_000_000_000:
        raise ValueError("Invalid grading ordinal")
    return (ordinal - 1) % 10 == 0


def eligibility(
    band: CalibrationBand | None,
    *,
    scope: GradingScope,
    response_characters: int,
    audit: AuditState,
    now: datetime,
) -> Reason:
    """Return a necessary candidate gate, never a grade or authorization grant.

    The caller must load current approved evidence and audit state under a band lock,
    verify ownership/consent/content/detectors and dual-pass validation, and recheck
    immediately before atomic grade/mastery publication. No caller-supplied confidence
    can authorize scoring. No report, approval, enabled band or audit is created here.
    """
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("Eligibility clock must be timezone-aware")
    if type(response_characters) is not int or not 1 <= response_characters <= 2000:
        return "LENGTH_MISMATCH"
    scope = GradingScope.model_validate(scope)
    audit = AuditState.model_validate(audit)
    if band is None:
        return "UNAPPROVED"
    band = CalibrationBand.model_validate(band)
    if audit.band_id != band.id:
        raise ValueError("Audit evidence belongs to another band")
    if not band.enabled or audit.disabled:
        return "DISABLED"
    if band.approved_at is None or band.approved_at > now:
        return "UNAPPROVED"
    if band.scope != scope:
        return "SCOPE_MISMATCH"
    if not band.minimum_characters <= response_characters <= band.maximum_characters:
        return "LENGTH_MISMATCH"
    # Integer comparisons retain exact thresholds without rounding or float confidence.
    if band.benchmark_within_tolerance * 100 < band.benchmark_cases * 85:
        return "BENCHMARK"
    if band.held_out_exact * 10 < band.held_out_cases * 9:
        return "CALIBRATION"
    if band.subgroup_review != "APPROVED":
        return "SUBGROUP"
    if band.critical_errors or any(row.critical_error for row in audit.recent):
        return "CRITICAL_ERROR"
    if audit.assigned_audits < (audit.returned_grades + 9) // 10:
        return "AUDIT_COVERAGE"
    if any(row.completed_at > now for row in audit.recent):
        raise ValueError("Audit evidence cannot be from the future")
    if audit.recent and sum(row.exact for row in audit.recent) * 10 < len(audit.recent) * 9:
        return "AUDIT_AGREEMENT"
    return "ELIGIBLE_CANDIDATE"
