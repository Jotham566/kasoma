"""FR-GRD-009 / FR-CNT-006 strict report and triage boundaries."""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field, StringConstraints, model_validator

from services.identity_contracts import Contract

Category = Literal[
    "QUESTION_ERROR", "GRADE_DISPUTE", "UNCLEAR", "ACCESSIBILITY", "UNSAFE_CONTENT", "OTHER"
]
Status = Literal["OPEN", "IN_REVIEW", "RESOLVED", "DISMISSED"]
Priority = Literal["NORMAL", "HIGH"]
Comment = Annotated[str, StringConstraints(strip_whitespace=True, max_length=1000)]


class FlagInput(Contract):
    category: Category
    comment: Comment = ""


class FlagReceipt(Contract):
    id: UUID
    category: Category
    created_at: datetime


class FlagUpdate(Contract):
    expected_revision: int = Field(ge=1)
    status: Literal["IN_REVIEW", "RESOLVED", "DISMISSED"]
    priority: Priority
    claim: bool = False
    resolution: Comment = ""

    @model_validator(mode="after")
    def resolution_required(self) -> "FlagUpdate":
        if self.status in {"RESOLVED", "DISMISSED"} and not self.resolution:
            raise ValueError("Terminal decisions require a resolution")
        if self.status == "IN_REVIEW" and self.resolution:
            raise ValueError("Resolution is recorded only for terminal decisions")
        return self


class FlagSummary(Contract):
    id: UUID
    item_id: UUID
    item_version_id: UUID
    category: Category
    priority: Priority
    status: Status
    owner_id: UUID | None
    revision: int
    created_at: datetime
    updated_at: datetime


class FlagHistoryView(Contract):
    actor_id: UUID
    revision: int
    status: Status
    priority: Priority
    owner_id: UUID | None
    created_at: datetime


class FlagDetail(FlagSummary):
    comment: str
    resolution: str
    resolved_at: datetime | None
    retention_due_at: datetime | None
    history: list[FlagHistoryView]


class FlagPage(Contract):
    data: list[FlagSummary]
    next_cursor: UUID | None
