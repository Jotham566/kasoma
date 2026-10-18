"""Blinded independent-review contracts; no model comparisons in staff projections."""

from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, Field, model_validator

from services.rubric_contracts import RubricCriterion
from services.short_text_validation import Identifier, StrictContract

CriticalError = Literal["NONE", "ACADEMIC_INTEGRITY", "SAFEGUARDING", "PRIVACY"]


class BlindedReviewTask(StrictContract):
    id: UUID
    item_version_id: UUID
    rubric_version_id: UUID
    prompt: str = Field(repr=False)
    response: str = Field(min_length=1, max_length=2000, repr=False)
    criteria: list[RubricCriterion] = Field(min_length=1, max_length=20, repr=False)

    @model_validator(mode="after")
    def pinned_rubric(self) -> "BlindedReviewTask":
        ids = [row.criterion_id for row in self.criteria]
        if self.rubric_version_id != self.item_version_id or len(ids) != len(set(ids)):
            raise ValueError("Pinned unique review criteria required")
        if sum(row.maximum_points for row in self.criteria) > 20:
            raise ValueError("Bounded reviewed item required")
        return self


class ReviewPoints(StrictContract):
    criterion_id: Identifier
    points_awarded: int = Field(ge=0, le=20)


class AuditReviewInput(StrictContract):
    criterion_points: list[ReviewPoints] = Field(min_length=1, max_length=20)
    critical_error: CriticalError
    affirmative: Literal[True]

    @model_validator(mode="after")
    def unique_criteria(self) -> "AuditReviewInput":
        ids = [row.criterion_id for row in self.criterion_points]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate review criterion")
        return self


class AuditReviewReceipt(StrictContract):
    id: UUID
    status: Literal["COMPLETED"] = "COMPLETED"
    completed_at: AwareDatetime


class AuditQueueEntry(StrictContract):
    id: UUID


class AuditQueuePage(StrictContract):
    data: list[AuditQueueEntry] = Field(max_length=50)
    next_cursor: UUID | None
