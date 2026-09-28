"""Learner-safe, explicitly projected assessment contracts."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from services.content_contracts import Choice
from services.identity_contracts import Contract
from services.numeric import NumericForm


class StartRevision(Contract):
    subject_id: UUID
    mode: Literal["TOPIC"] = "TOPIC"
    topic_id: UUID
    desired_item_count: int = Field(default=5, ge=5, le=10)
    channel: Literal["WEB"] = "WEB"


class ChoiceResponse(Contract):
    type: Literal["SINGLE_CHOICE"] = "SINGLE_CHOICE"
    choice_id: str = Field(pattern=r"^[A-Z]$", max_length=1)


class NumericResponse(Contract):
    type: Literal["NUMERIC"]
    value: str = Field(min_length=1, max_length=64)
    unit: str = Field(default="", max_length=24)


class SubmitAnswer(Contract):
    session_item_id: UUID
    response: ChoiceResponse | NumericResponse


class Feedback(Contract):
    correct_elements: list[str]
    missing_elements: list[str]
    next_action: str


class GradeView(Contract):
    attempt_id: UUID
    item_version_id: UUID
    status: Literal["GRADED"] = "GRADED"
    score: float
    points_awarded: int
    points_possible: int
    confidence: float = Field(default=1.0, ge=1, le=1)
    method: Literal["DETERMINISTIC"] = "DETERMINISTIC"
    grader_version: str
    feedback: Feedback
    mastery_update_status: Literal["NOT_IMPLEMENTED", "COMPLETED"] = "NOT_IMPLEMENTED"


class AnsweredItem(Contract):
    session_item_id: UUID
    position: int
    grade: GradeView


class SessionView(Contract):
    id: UUID
    subject_id: UUID
    topic_id: UUID
    status: Literal["ACTIVE", "COMPLETED", "ABANDONED", "EXPIRED"]
    item_count: int
    answered_count: int
    recommendation_reason: str
    plan_version: str
    expires_at: datetime
    answers: list[AnsweredItem]
    synthetic: Literal[True] = True


class PromptBlock(Contract):
    type: Literal["text"] = "text"
    content: str


class ResponseSpec(Contract):
    type: Literal["SINGLE_CHOICE"] = "SINGLE_CHOICE"
    choices: list[Choice]


class NumericResponseSpec(Contract):
    type: Literal["NUMERIC"] = "NUMERIC"
    unit_options: list[str]
    accepted_forms: list[NumericForm]
    significant_figures_policy: Literal["IGNORE", "EXACT"]
    significant_figures: int | None
    input_mode: Literal["text"] = "text"


class LearnerItem(Contract):
    session_item_id: UUID
    item_version_id: UUID
    position: int
    prompt_blocks: list[PromptBlock]
    response_spec: ResponseSpec | NumericResponseSpec
    maximum_points: int
    selection_reason: str


class SolutionView(Contract):
    attempt_id: UUID
    item_version_id: UUID
    worked_solution: str


class TopicView(Contract):
    id: UUID
    name: str


class StartDiagnostic(Contract):
    subject_id: UUID
    channel: Literal["WEB"] = "WEB"


class DiagnosticReceipt(Contract):
    attempt_id: UUID
    status: Literal["SAVED"] = "SAVED"
    message: str = "Answer saved. Results are available after the diagnostic."


class SkillSummary(Contract):
    topic_id: UUID
    topic: str
    concept_id: UUID
    competency_id: UUID
    competency: str
    mastery: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    display_state: str
    evidence_count: int


class InitialRecommendation(Contract):
    topic_id: UUID | None
    reason_code: Literal["GATHER_MORE_EVIDENCE", "PRACTISE_SUPPORTED_GAP", "CONTENT_UNAVAILABLE"]
    learner_text: str


class DiagnosticResult(Contract):
    skills: list[SkillSummary]
    recommendation: InitialRecommendation
    calculated_at: datetime
    algorithm_version: str
    configuration_version: str
    input_hash: str


class DiagnosticView(Contract):
    id: UUID
    subject_id: UUID
    status: Literal["ACTIVE", "COMPLETED", "ABANDONED", "EXPIRED"]
    item_count: int
    answered_count: int
    plan_version: str
    expires_at: datetime
    result: DiagnosticResult | None
    synthetic: Literal[True] = True
