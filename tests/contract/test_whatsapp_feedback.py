"""FR-WA-005: exact bounds and authenticated web fallback without answer truncation."""

from uuid import uuid4

import pytest

from services.grading import grade_choice
from services.whatsapp_feedback import feedback_text
from tests.contract.test_whatsapp_format import question


def result(**changes):
    return grade_choice(uuid4(), uuid4(), question(**changes), "B")


def test_short_feedback_retains_academic_text_and_owned_web_link():
    session = uuid4()
    grade = result(remediation="Read the labels again.")
    message = feedback_text(grade, session, 1, "http://localhost:3000/")
    assert "Points: 0/1" in message
    assert "Read the labels again." in message
    assert f"http://localhost:3000/revise?session={session}" in message
    assert "CONTINUE" in message and "STOP" in message
    assert "SECRET worked solution" not in message
    assert len(message) <= 500


@pytest.mark.parametrize("remediation", ["", "x" * 600, "![diagram](x)", r"\[x\]"])
def test_unsuitable_detail_uses_full_web_fallback(remediation):
    message = feedback_text(result(remediation=remediation), uuid4(), 5, "http://localhost:3000")
    assert "Details and worked solution: http://localhost:3000/revise?session=" in message
    assert "Five answers saved." in message and "CONTINUE" not in message
    assert "![" not in message and "x" * 100 not in message and r"\[" not in message
    assert len(message) <= 500


def test_limit_applies_to_complete_message_without_truncating_link():
    grade, session = result(remediation="x" * 600), uuid4()
    message = feedback_text(grade, session, 2, "http://localhost:3000")
    assert feedback_text(grade, session, 2, "http://localhost:3000", len(message)) == message
    with pytest.raises(ValueError):
        feedback_text(grade, session, 2, "http://localhost:3000", len(message) - 1)


@pytest.mark.parametrize(
    "origin",
    [
        "https://external.invalid",
        "http://secret@localhost:3000",
        "http://localhost:3000?token=secret",
        "http://localhost:3000/#fragment",
        "http://localhost:3000/path",
        "ftp://localhost",
        "http://localhost:3000\n",
        "//localhost:3000",
    ],
)
def test_invalid_or_secret_bearing_link_origin_rejected(origin):
    with pytest.raises(ValueError):
        feedback_text(result(), uuid4(), 1, origin)


@pytest.mark.parametrize("position,limit", [(0, 500), (6, 500), (1, 0), (1, 501)])
def test_invalid_bounds_rejected(position, limit):
    with pytest.raises(ValueError):
        feedback_text(result(), uuid4(), position, "http://localhost:3000", limit)
