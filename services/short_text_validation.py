"""Offline candidate validation only; no learner scoring or model execution (ADR-040)."""

import json
from typing import Annotated, Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    model_validator,
)

from services.rubric_contracts import RubricCriterion

Identifier = Annotated[str, Field(pattern=r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")]
Text = Annotated[str, Field(min_length=1, max_length=2000)]
Points = Annotated[int, Field(ge=0, le=100)]


class StrictContract(BaseModel):
    model_config = ConfigDict(
        extra="forbid", strict=True, allow_inf_nan=False, hide_input_in_errors=True
    )


class SyntheticRubricContext(StrictContract):
    """Trusted fixture context; it conveys no academic approval or production eligibility."""

    classification: Literal["synthetic"] = "synthetic"
    rubric_version_id: UUID
    item_version_id: UUID
    maximum_points: int = Field(ge=1, le=100)
    criteria: list[RubricCriterion] = Field(min_length=1, max_length=20, repr=False)
    misconception_ids: list[Identifier] = Field(max_length=50)
    correct_elements: list[Text] = Field(max_length=20, repr=False)
    missing_elements: list[Text] = Field(max_length=20, repr=False)
    next_actions: list[Text] = Field(min_length=1, max_length=20, repr=False)

    @model_validator(mode="after")
    def coherent_rubric(self) -> "SyntheticRubricContext":
        ids = [criterion.criterion_id for criterion in self.criteria]
        if len(ids) != len(set(ids)):
            raise ValueError("Rubric criterion IDs must be unique")
        if sum(criterion.maximum_points for criterion in self.criteria) != self.maximum_points:
            raise ValueError("Rubric maxima must sum to item maximum")
        if len(self.misconception_ids) != len(set(self.misconception_ids)):
            raise ValueError("Misconception IDs must be unique")
        return self


class CriterionResult(StrictContract):
    criterion_id: Identifier
    points_awarded: Points
    evidence_excerpt: str = Field(max_length=2000, repr=False)
    justification_code: Literal["SUPPORTED", "MISSING", "CONTRADICTED"]


class CandidateFeedback(StrictContract):
    correct_elements: list[Text] = Field(max_length=20, repr=False)
    missing_elements: list[Text] = Field(max_length=20, repr=False)
    next_action: Text = Field(repr=False)


class ShortTextCandidate(StrictContract):
    criterion_results: list[CriterionResult] = Field(min_length=1, max_length=20, repr=False)
    total_points: Points
    confidence: float = Field(ge=0, le=1)
    detected_misconception_ids: list[Identifier] = Field(max_length=50)
    feedback: CandidateFeedback = Field(repr=False)


Reason = Literal[
    "SCHEMA_INVALID", "RUBRIC_MISMATCH", "EVIDENCE_INVALID", "CONTEXT_INVALID", "FLAGGED"
]


class ValidationResult(StrictContract):
    status: Literal["VALIDATED_CANDIDATE", "LOW_CONFIDENCE"]
    reason: Reason | None = None
    candidate: ShortTextCandidate | None = Field(default=None, repr=False)


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("Duplicate JSON field")
        value[key] = item
    return value


def reject_constant(value: str) -> None:
    raise ValueError("Non-finite JSON number")


def fallback(reason: Reason) -> ValidationResult:
    return ValidationResult(status="LOW_CONFIDENCE", reason=reason)


def validate_candidate(
    raw: str, *, context: SyntheticRubricContext, response: str, flagged: bool
) -> ValidationResult:
    """Reject malformed/unsupported output without echoing it or its validation errors.

    Exact excerpts and exact authored feedback are intentionally conservative. Caller must
    supply safety/injection/domain flags; this function is not an injection detector. Even a
    validated candidate is never a definitive grade, regardless of its claimed confidence.
    """
    if flagged:
        return fallback("FLAGGED")
    if not response.strip() or len(response) > 2000 or len(raw) > 16384:
        return fallback("SCHEMA_INVALID")
    try:
        candidate = ShortTextCandidate.model_validate(
            json.loads(raw, object_pairs_hook=unique_object, parse_constant=reject_constant)
        )
    except (ValueError, ValidationError, RecursionError):
        return fallback("SCHEMA_INVALID")
    maxima = {criterion.criterion_id: criterion.maximum_points for criterion in context.criteria}
    ids = [criterion.criterion_id for criterion in candidate.criterion_results]
    if len(ids) != len(set(ids)) or set(ids) != set(maxima):
        return fallback("RUBRIC_MISMATCH")
    if (
        any(item.points_awarded > maxima[item.criterion_id] for item in candidate.criterion_results)
        or sum(item.points_awarded for item in candidate.criterion_results)
        != candidate.total_points
        or candidate.total_points > context.maximum_points
    ):
        return fallback("RUBRIC_MISMATCH")
    for item in candidate.criterion_results:
        excerpt = item.evidence_excerpt
        if excerpt and (not excerpt.strip() or excerpt not in response):
            return fallback("EVIDENCE_INVALID")
        if item.points_awarded and (not excerpt.strip() or item.justification_code != "SUPPORTED"):
            return fallback("EVIDENCE_INVALID")
        if item.justification_code == "CONTRADICTED" and not excerpt.strip():
            return fallback("EVIDENCE_INVALID")
    misconceptions = candidate.detected_misconception_ids
    feedback = candidate.feedback
    if (
        len(misconceptions) != len(set(misconceptions))
        or not set(misconceptions).issubset(context.misconception_ids)
        or not set(feedback.correct_elements).issubset(context.correct_elements)
        or not set(feedback.missing_elements).issubset(context.missing_elements)
        or feedback.next_action not in context.next_actions
    ):
        return fallback("CONTEXT_INVALID")
    return ValidationResult(status="VALIDATED_CANDIDATE", candidate=candidate)
