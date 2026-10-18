"""Definitive rubric result shape; creation is not publication authorization."""

from math import isclose
from typing import Literal
from uuid import UUID

from pydantic import Field, model_validator

from services.short_text_validation import (
    CandidateFeedback,
    CriterionResult,
    Identifier,
    StrictContract,
)


class RubricGradeView(StrictContract):
    attempt_id: UUID
    item_version_id: UUID
    rubric_version_id: UUID
    status: Literal["GRADED"] = "GRADED"
    method: Literal["RUBRIC_MODEL"] = "RUBRIC_MODEL"
    score: float = Field(ge=0, le=1)
    points_awarded: int = Field(ge=0, le=20)
    points_possible: int = Field(ge=1, le=20)
    confidence: float = Field(ge=0, le=1)
    hint_count: int = Field(default=0, ge=0, le=3)
    highest_hint_level: int = Field(default=0, ge=0, le=3)
    grader_version: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
    criterion_results: list[CriterionResult] = Field(min_length=1, max_length=20, repr=False)
    detected_misconception_ids: list[Identifier] = Field(max_length=50)
    feedback: CandidateFeedback = Field(repr=False)
    mastery_update_status: Literal["NOT_IMPLEMENTED", "COMPLETED"] = "NOT_IMPLEMENTED"

    @model_validator(mode="after")
    def coherent_result(self) -> "RubricGradeView":
        if self.rubric_version_id != self.item_version_id:
            raise ValueError("Rubric must match its pinned item version")
        ids = [row.criterion_id for row in self.criterion_results]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate rubric criterion")
        if (
            self.points_awarded > self.points_possible
            or sum(row.points_awarded for row in self.criterion_results) != self.points_awarded
            or not isclose(
                self.score, self.points_awarded / self.points_possible, rel_tol=0, abs_tol=1e-12
            )
        ):
            raise ValueError("Incoherent rubric points")
        if len(set(self.detected_misconception_ids)) != len(self.detected_misconception_ids):
            raise ValueError("Duplicate misconception")
        if self.highest_hint_level > self.hint_count:
            raise ValueError("Incoherent hint usage")
        return self
