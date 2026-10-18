"""Authenticated answer-bearing grade storage with a quote-free scoring summary."""

from typing import Literal
from uuid import UUID

from pydantic import Field

from services.rubric_grade_contracts import RubricGradeView
from services.short_text_answers import AnswerBinding, AnswerCipher
from services.short_text_validation import Identifier, StrictContract

MAX_RESULT_BYTES = 131_072
MAX_RESULT_CIPHERTEXT = 196_608


class GradeProtectionError(RuntimeError):
    """Fixed diagnostics only; never include answer, result, ciphertext or keys."""


class ResultBinding(StrictContract):
    answer: AnswerBinding = Field(repr=False)
    band_id: UUID


class GradeEnvelope(StrictContract):
    format: Literal["kasoma-rubric-grade-v1"] = "kasoma-rubric-grade-v1"
    binding: ResultBinding = Field(repr=False)
    grade: RubricGradeView = Field(repr=False)


class StoredRubricGrade(StrictContract):
    """Only ciphertext contains feedback, excerpts and misconception labels.

    The remaining fields support SQL point/rubric/band consistency and mastery.
    They are still confidential learning data, never public operational telemetry.
    """

    format: Literal["kasoma-rubric-grade-v1"] = "kasoma-rubric-grade-v1"
    status: Literal["GRADED"] = "GRADED"
    method: Literal["RUBRIC_MODEL"] = "RUBRIC_MODEL"
    attempt_id: UUID
    item_version_id: UUID
    rubric_version_id: UUID
    band_id: UUID
    score: float = Field(ge=0, le=1)
    points_awarded: int = Field(ge=0, le=20)
    points_possible: int = Field(ge=1, le=20)
    confidence: float = Field(ge=0, le=1)
    hint_count: int = Field(ge=0, le=3)
    highest_hint_level: int = Field(ge=0, le=3)
    grader_version: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
    mastery_update_status: Literal["NOT_IMPLEMENTED", "COMPLETED"]
    criterion_points: dict[Identifier, int] = Field(min_length=1, max_length=20)
    ciphertext: str = Field(min_length=1, max_length=MAX_RESULT_CIPHERTEXT, repr=False)


def stored_projection(
    grade: RubricGradeView, binding: ResultBinding, ciphertext: str
) -> StoredRubricGrade:
    if (grade.attempt_id, grade.item_version_id, grade.rubric_version_id) != (
        binding.answer.attempt_id,
        binding.answer.item_version_id,
        binding.answer.rubric_version_id,
    ) or not ciphertext.isascii():
        raise ValueError("Invalid result binding")
    return StoredRubricGrade.model_validate(
        grade.model_dump(exclude={"criterion_results", "detected_misconception_ids", "feedback"})
        | {
            "band_id": binding.band_id,
            "criterion_points": {
                row.criterion_id: row.points_awarded for row in grade.criterion_results
            },
            "ciphertext": ciphertext,
        }
    )


def protect_result(
    grade: RubricGradeView, binding: ResultBinding, cipher: AnswerCipher
) -> StoredRubricGrade:
    """No persistence or grading authorization; caller owns the publication transaction."""
    try:
        checked = GradeEnvelope.model_validate_json(
            GradeEnvelope(binding=binding, grade=grade).model_dump_json()
        )
        raw = checked.model_dump_json()
        if len(raw.encode("utf-8")) > MAX_RESULT_BYTES:
            raise ValueError("Result exceeds storage bounds")
        ciphertext = cipher.encrypt(raw)
        return stored_projection(checked.grade, checked.binding, ciphertext)
    except Exception:
        raise GradeProtectionError("RUBRIC_GRADE_WRITE_FAILED") from None


def reveal_result(
    stored: StoredRubricGrade, binding: ResultBinding, cipher: AnswerCipher
) -> RubricGradeView:
    """Authenticate binding and summary before returning confidential result material."""
    try:
        stored = StoredRubricGrade.model_validate_json(stored.model_dump_json())
        binding = ResultBinding.model_validate_json(binding.model_dump_json())
        if not stored.ciphertext.isascii():
            raise ValueError("Invalid ciphertext")
        raw = cipher.decrypt(stored.ciphertext)
        if len(raw.encode("utf-8")) > MAX_RESULT_BYTES:
            raise ValueError("Result exceeds storage bounds")
        envelope = GradeEnvelope.model_validate_json(raw)
        if (
            envelope.binding != binding
            or envelope.model_dump_json() != raw
            or stored_projection(envelope.grade, binding, stored.ciphertext) != stored
        ):
            raise ValueError("Invalid result binding")
        return envelope.grade
    except Exception:
        raise GradeProtectionError("RUBRIC_GRADE_READ_FAILED") from None
