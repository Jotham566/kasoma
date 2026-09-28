"""First authored response format; no hand-written browser DTOs."""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field, StringConstraints

from services.identity_contracts import Contract
from services.numeric import NumericSpec

Text = Annotated[str, Field(max_length=4000)]
Reason = Annotated[str, Field(min_length=1, max_length=500)]
Rights = Literal[
    "ORIGINAL_KASOMA",
    "LICENSED",
    "PUBLIC_DOMAIN_CONFIRMED",
    "PERMISSION_CONFIRMED",
    "REFERENCE_ONLY_NO_REPRODUCTION",
    "UNKNOWN_BLOCKED",
]
ChecklistKey = Literal[
    "curriculum",
    "competency_difficulty",
    "factual_accuracy",
    "clarity",
    "answer_rubric",
    "units_precision",
    "partial_credit",
    "worked_solution",
    "feedback",
    "equivalence",
    "language_age",
    "accessibility",
    "rights",
    "channel",
    "safety",
]
CHECKLIST = {
    "curriculum",
    "competency_difficulty",
    "factual_accuracy",
    "clarity",
    "answer_rubric",
    "units_precision",
    "partial_credit",
    "worked_solution",
    "feedback",
    "equivalence",
    "language_age",
    "accessibility",
    "rights",
    "channel",
    "safety",
}


class Choice(Contract):
    id: str = Field(pattern=r"^[A-Z]$", max_length=1)
    text: Text


class Mapping(Contract):
    competency_id: UUID
    weight: float = Field(gt=0, le=1, allow_inf_nan=False)


class DraftDocument(Contract):
    title: str = Field(default="", max_length=160)
    topic_id: UUID | None = None
    concept_id: UUID | None = None
    competency_mappings: list[Mapping] = Field(default_factory=list, max_length=4)
    learning_outcome_reference: str = Field(default="", max_length=300)
    difficulty: Literal["FOUNDATIONAL", "STANDARD", "CHALLENGING"] = "FOUNDATIONAL"
    expected_seconds: int = Field(default=60, ge=10, le=3600)
    response_type: Literal["SINGLE_CHOICE", "NUMERIC"] = "SINGLE_CHOICE"
    channel_suitability: list[Literal["WEB", "WHATSAPP"]] = Field(
        default=["WEB"], min_length=1, max_length=2
    )
    prompt: Text = ""
    choices: list[Choice] = Field(default_factory=list, max_length=8)
    numeric_spec: NumericSpec | None = None
    correct_choice_id: str = Field(default="", max_length=1)
    maximum_points: int = Field(default=1, ge=1, le=20)
    partial_credit: Literal["ALL_OR_NOTHING"] = "ALL_OR_NOTHING"
    hints: list[
        Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]
    ] = Field(default_factory=list, max_length=3)
    worked_solution: Text = ""
    remediation: Text = ""
    prerequisite_concept_ids: list[UUID] = Field(default_factory=list, max_length=20)
    source: str = Field(default="", max_length=500)
    rights_status: Rights = "UNKNOWN_BLOCKED"
    rights_evidence: str = Field(default="", max_length=1000)
    rights_conditions: str = Field(default="", max_length=1000)
    high_risk: bool = False


class CreateDraft(Contract):
    subject_id: UUID
    document: DraftDocument
    change_reason: Reason
    source_version_id: UUID | None = None


class EditDraft(Contract):
    expected_revision: int = Field(ge=1)
    document: DraftDocument
    change_reason: Reason


class Transition(Contract):
    expected_revision: int = Field(ge=1)
    reason: Reason


class ReviewInput(Transition):
    decision: Literal["APPROVE", "RETURN"]
    checklist: list[ChecklistKey] = Field(default_factory=list, max_length=15)
    require_second_review: bool = False


class VersionView(Contract):
    id: UUID
    item_id: UUID
    subject_id: UUID
    author_id: UUID
    version: int
    revision: int
    status: str
    document: DraftDocument
    requires_second_review: bool
    synthetic: Literal[True] = True
    production_eligible: Literal[False] = False
    approval_count: int
    created_at: datetime
    updated_at: datetime


class VersionPage(Contract):
    data: list[VersionView]
    next_cursor: UUID | None


class CatalogEntry(Contract):
    id: UUID
    name: str
    parent_id: UUID | None = None
    syllabus_reference: str | None = None


class ContentContext(Contract):
    actor_id: UUID
    roles: list[str]
    subjects: list[CatalogEntry]
    topics: list[CatalogEntry]
    concepts: list[CatalogEntry]
    competencies: list[CatalogEntry]
    checklist: list[str]


class ReviewView(Contract):
    reviewer_id: UUID
    decision: str
    reason: str
    checklist: list[str]
    created_at: datetime


class FieldError(Contract):
    field: str
    message: str


class APIError(Contract):
    code: str
    message: str
    request_id: UUID
    field_errors: list[FieldError]


class ErrorEnvelope(Contract):
    error: APIError
