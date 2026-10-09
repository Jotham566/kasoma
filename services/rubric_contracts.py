"""Bounded authored rubric material shared by content and synthetic model rehearsal."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Identifier = Annotated[str, Field(pattern=r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")]
RubricText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]


class RubricContract(BaseModel):
    model_config = ConfigDict(
        extra="forbid", strict=True, allow_inf_nan=False, hide_input_in_errors=True
    )


class RubricCriterion(RubricContract):
    criterion_id: Identifier
    maximum_points: int = Field(ge=1, le=100)
    criterion_text: RubricText = Field(repr=False)
    acceptable_evidence: list[RubricText] = Field(min_length=1, max_length=10, repr=False)
    common_errors: list[RubricText] = Field(max_length=10, repr=False)
    prohibited_inferences: list[RubricText] = Field(max_length=10, repr=False)


class RubricDraft(RubricContract):
    criteria: list[RubricCriterion] = Field(min_length=1, max_length=20, repr=False)

    @model_validator(mode="after")
    def unique_criteria(self) -> "RubricDraft":
        ids = [criterion.criterion_id for criterion in self.criteria]
        if len(ids) != len(set(ids)):
            raise ValueError("Rubric criterion IDs must be unique")
        return self
