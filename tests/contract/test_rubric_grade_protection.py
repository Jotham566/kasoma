"""FR-GRD-003 / FR-ID-006: confidential result binding, tamper detection and bounds."""

import json
from uuid import UUID, uuid4

import pytest
from cryptography.fernet import Fernet

from services.rubric_grade_contracts import RubricGradeView
from services.rubric_grade_protection import (
    MAX_RESULT_CIPHERTEXT,
    GradeProtectionError,
    ResultBinding,
    protect_result,
    reveal_result,
)
from services.short_text_answers import AnswerBinding
from tests.contract.test_rubric_grade_projection import context as context_fixture
from tests.contract.test_rubric_grade_projection import material as material_fixture
from tests.contract.test_rubric_grade_projection import output as output_fixture
from tests.contract.test_rubric_grade_projection import project

context = context_fixture
material = material_fixture
output = output_fixture


class Cipher:
    def __init__(self):
        self.fernet = Fernet(Fernet.generate_key())

    def encrypt(self, raw):
        return self.fernet.encrypt(raw.encode()).decode()

    def decrypt(self, raw):
        return self.fernet.decrypt(raw.encode()).decode()


@pytest.fixture
def protected(material):
    grade = project(material)
    binding = ResultBinding(
        answer=AnswerBinding(
            learner_id=UUID(int=501),
            attempt_id=grade.attempt_id,
            session_item_id=UUID(int=502),
            item_version_id=grade.item_version_id,
            rubric_version_id=grade.rubric_version_id,
        ),
        band_id=UUID(int=503),
    )
    cipher = Cipher()
    return grade, binding, cipher, protect_result(grade, binding, cipher)


def test_only_encrypted_material_contains_answer_excerpts_and_feedback(protected):
    grade, binding, cipher, stored = protected
    assert reveal_result(stored, binding, cipher) == grade
    serialized = stored.model_dump_json()
    assert "synthetic property" not in serialized
    assert "Review the worked example" not in serialized
    assert "evidence_excerpt" not in serialized
    assert "feedback" not in serialized
    assert stored.criterion_points == {"R1": 1, "R2": 0}
    assert stored.score == grade.score
    assert stored.ciphertext not in repr(stored)


@pytest.mark.parametrize(
    "field", ["learner_id", "attempt_id", "session_item_id", "item_rubric", "band_id"]
)
def test_different_owner_attempt_assignment_rubric_or_band_cannot_read(protected, field):
    _, binding, cipher, stored = protected
    value = binding.model_dump()
    if field == "band_id":
        value["band_id"] = uuid4()
    elif field == "item_rubric":
        value["answer"]["item_version_id"] = value["answer"]["rubric_version_id"] = uuid4()
    else:
        value["answer"][field] = uuid4()
    with pytest.raises(GradeProtectionError, match="^RUBRIC_GRADE_READ_FAILED$"):
        reveal_result(stored, ResultBinding.model_validate(value), cipher)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("score", 0.0),
        ("points_awarded", 0),
        ("points_possible", 3),
        ("confidence", 0.1),
        ("criterion_points", {"R1": 0, "R2": 1}),
        ("hint_count", 1),
        ("grader_version", "untrusted-v1"),
        ("mastery_update_status", "COMPLETED"),
        ("ciphertext", "corrupt"),
    ],
)
def test_public_summary_cannot_be_forged_without_detection(protected, field, value):
    _, binding, cipher, stored = protected
    with pytest.raises(GradeProtectionError, match="^RUBRIC_GRADE_READ_FAILED$"):
        reveal_result(stored.model_copy(update={field: value}), binding, cipher)


def test_wrong_key_and_noncanonical_authenticated_payload_are_rejected(protected):
    _, binding, cipher, stored = protected
    with pytest.raises(GradeProtectionError):
        reveal_result(stored, binding, Cipher())
    raw = cipher.decrypt(stored.ciphertext)
    changed = stored.model_copy(
        update={"ciphertext": cipher.encrypt(json.dumps(json.loads(raw), indent=2))}
    )
    with pytest.raises(GradeProtectionError):
        reveal_result(changed, binding, cipher)


def test_invalid_grade_binding_cannot_be_written(protected):
    grade, binding, cipher, _ = protected
    with pytest.raises(GradeProtectionError, match="^RUBRIC_GRADE_WRITE_FAILED$"):
        protect_result(grade.model_copy(update={"attempt_id": uuid4()}), binding, cipher)


class FailingCipher:
    def encrypt(self, raw):
        raise RuntimeError("private provider diagnostics and synthetic property")

    def decrypt(self, raw):
        raise RuntimeError("private provider diagnostics and synthetic property")


def test_adapter_diagnostics_never_escape_closed_errors(protected):
    grade, binding, _, stored = protected
    for operation in (
        lambda: protect_result(grade, binding, FailingCipher()),
        lambda: reveal_result(stored, binding, FailingCipher()),
    ):
        with pytest.raises(GradeProtectionError) as caught:
            operation()
        assert "private" not in str(caught.value)
        assert "synthetic property" not in str(caught.value)
        assert caught.value.__suppress_context__


def test_oversized_plaintext_is_rejected_before_cipher_dispatch(protected):
    grade, binding, _, _ = protected
    payload = grade.model_dump()
    payload["feedback"]["correct_elements"] = ["界" * 2000] * 20
    payload["feedback"]["missing_elements"] = ["Δ" * 2000] * 20
    oversized = RubricGradeView.model_validate(payload)

    class UncalledCipher(Cipher):
        def encrypt(self, raw):
            pytest.fail("Oversized material reached encryption")

    with pytest.raises(GradeProtectionError, match="WRITE_FAILED"):
        protect_result(oversized, binding, UncalledCipher())


def test_ciphertext_size_and_ascii_bounds_apply_on_write_and_read(protected):
    grade, binding, cipher, stored = protected

    class InvalidCipher(Cipher):
        def __init__(self, value):
            self.value = value

        def encrypt(self, raw):
            return self.value

    for value in ("x" * (MAX_RESULT_CIPHERTEXT + 1), "非ASCII", ""):
        with pytest.raises(GradeProtectionError):
            protect_result(grade, binding, InvalidCipher(value))
        with pytest.raises(GradeProtectionError):
            reveal_result(stored.model_copy(update={"ciphertext": value}), binding, cipher)
