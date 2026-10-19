"""FR-MST-004/005 learner-safe aggregate and history views."""

from datetime import date, datetime, timedelta
from typing import Literal, Self
from uuid import UUID

from pydantic import Field, model_validator

from services.identity_contracts import Contract
from services.mastery_engine import DisplayState


class ProgressSummary(Contract):
    id: UUID
    name: str
    mastery: float | None = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    display_state: DisplayState
    evidence_count: int = Field(ge=0)
    assessed_skill_count: int = Field(ge=0)
    mapped_skill_count: int = Field(ge=0)
    last_evidence_at: datetime | None
    change: Literal["NOT_ENOUGH_EVIDENCE", "HIGHER", "LOWER", "UNCHANGED"]
    input_hash: str


class ProgressAction(Contract):
    kind: Literal["CONTINUE_DIAGNOSTIC", "START_DIAGNOSTIC", "OPEN_RECOMMENDATIONS"]
    session_id: UUID | None = None
    label: str


class PracticeActivity(Contract):
    """Distinct dates with eligible graded practice in the selected subject."""

    days_practised: int = Field(ge=0, le=7, strict=True)
    window_start: date
    window_end: date
    window_days: Literal[7] = 7
    time_zone: Literal["Africa/Kampala"] = "Africa/Kampala"
    version: Literal["practice-days-v1"] = "practice-days-v1"

    @model_validator(mode="after")
    def complete_calendar_window(self) -> Self:
        if self.window_end - self.window_start != timedelta(days=6):
            raise ValueError("Practice activity requires seven inclusive calendar dates")
        return self


class ProgressView(Contract):
    subject: ProgressSummary
    topics: list[ProgressSummary]
    competencies: list[ProgressSummary]
    next_action: ProgressAction
    practice_activity: PracticeActivity | None = None
    calculated_at: datetime
    algorithm_version: Literal["weighted-evidence-v1"] = "weighted-evidence-v1"
    aggregation_version: Literal["progress-rollup-v1"] = "progress-rollup-v1"
    synthetic: Literal[True] = True


class SessionHistoryEntry(Contract):
    id: UUID
    subject_id: UUID
    subject: str
    topic: str | None
    kind: Literal["REVISION", "DIAGNOSTIC", "REASSESSMENT"]
    status: Literal["ACTIVE", "COMPLETED", "ABANDONED", "EXPIRED"]
    started_at: datetime
    completed_at: datetime | None
    item_count: int
    answered_count: int
    original_session_id: UUID | None = None


class SessionHistoryPage(Contract):
    data: list[SessionHistoryEntry]
    next_cursor: str | None
