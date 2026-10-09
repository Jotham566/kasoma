"""Pending/neutral short-text contracts; learner routes remain disabled (ADR-050)."""

from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from services.short_text_validation import StrictContract


class ShortTextResponse(StrictContract):
    type: Literal["SHORT_TEXT"]
    text: str = Field(min_length=1, max_length=2000, repr=False)

    @field_validator("text")
    @classmethod
    def nonblank_response(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("An answer is required")
        # Preserve exact evidence and whitespace; never rewrite the submitted answer.
        return value


class PendingShortTextGrade(StrictContract):
    attempt_id: UUID
    item_version_id: UUID
    status: Literal["PENDING"] = "PENDING"
    message_code: Literal["GRADE_PENDING"] = "GRADE_PENDING"
    mastery_update_status: Literal["NOT_APPLICABLE"] = "NOT_APPLICABLE"
    poll_url: str = ""

    @model_validator(mode="after")
    def owned_poll_target(self) -> "PendingShortTextGrade":
        # A relative, owned-grade route; never accept a provider-supplied redirect.
        expected = f"/api/v1/attempts/{self.attempt_id}/grade"
        if self.poll_url and self.poll_url != expected:
            raise ValueError("Poll target must match the attempt")
        self.poll_url = expected
        return self


class ObjectiveEquivalentFallback(StrictContract):
    kind: Literal["OBJECTIVE_EQUIVALENT"]
    session_id: UUID


class RequestReviewFallback(StrictContract):
    kind: Literal["REQUEST_REVIEW"]


Fallback = Annotated[
    ObjectiveEquivalentFallback | RequestReviewFallback, Field(discriminator="kind")
]


class LowConfidenceShortTextGrade(StrictContract):
    attempt_id: UUID
    item_version_id: UUID
    status: Literal["LOW_CONFIDENCE"] = "LOW_CONFIDENCE"
    message_code: Literal["GRADE_LOW_CONFIDENCE"] = "GRADE_LOW_CONFIDENCE"
    mastery_update_status: Literal["NOT_APPLICABLE"] = "NOT_APPLICABLE"
    fallback: Fallback


UnresolvedShortTextGrade = Annotated[
    PendingShortTextGrade | LowConfidenceShortTextGrade, Field(discriminator="status")
]
