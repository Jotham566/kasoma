"""FR-WA-002/003/005: lossless bounded representation without a second grader."""

from uuid import uuid4

import pytest

from services.content_contracts import Choice, DraftDocument
from services.grading import grade_choice, grade_multiple_choice, grade_numeric
from services.whatsapp_format import parse_reply, question_text, supports
from tests.contract.test_numeric import spec


def question(**changes):
    return DraftDocument.model_validate(
        {
            "channel_suitability": ["WEB", "WHATSAPP"],
            "prompt": "Choose the requested label.",
            "choices": [{"id": "Z", "text": "Alpha"}, {"id": "B", "text": "Beta"}],
            "correct_choice_id": "Z",
            "worked_solution": "SECRET worked solution",
            "remediation": "SECRET remediation",
            **changes,
        }
    )


def test_complete_question_boundary_and_no_answer_key_projection():
    doc = question()
    rendered = question_text(doc, 1)
    assert "1. Alpha" in rendered and "2. Beta" in rendered and "Question 1/5" in rendered
    assert "SECRET" not in rendered and "Z" not in rendered
    assert question_text(doc, 1, len(rendered)) == rendered
    with pytest.raises(ValueError):
        question_text(doc, 1, len(rendered) - 1)
    assert not supports(question(prompt="x" * 500))
    assert not supports(question(channel_suitability=["WEB"]))
    with pytest.raises(ValueError):
        question_text(doc, 6)


@pytest.mark.parametrize(
    "rich",
    [
        "![diagram](x)",
        "<img src=x>",
        "<svg>",
        r"\includegraphics{x}",
        r"\begin{matrix}",
        "$$x$$",
        r"\[x\]",
    ],
)
def test_image_and_rich_rendering_excluded(rich):
    assert not supports(question(prompt=rich))
    assert not supports(question(choices=[{"id": "A", "text": rich}, {"id": "B", "text": "Beta"}]))


def test_numbered_choice_normalization_reuses_grader():
    doc = question()
    parsed = parse_reply(doc, " 1 ")
    assert parsed.choice_id == "Z"
    assert grade_choice(uuid4(), uuid4(), doc, parsed.choice_id).score == 1
    multiple = question(
        response_type="MULTIPLE_CHOICE", correct_choice_id="", correct_choice_ids=["B", "Z"]
    )
    parsed = parse_reply(multiple, "2, 1")
    assert parsed.choice_ids == ["B", "Z"]
    assert grade_multiple_choice(uuid4(), uuid4(), multiple, parsed.choice_ids).score == 1
    assert parse_reply(multiple, "1").choice_ids == ["Z"]


@pytest.mark.parametrize(
    "raw", ["", "0", "9", "3", "A", "1,1", "1,2", "1,", "1.0", "01", "1 2", "١", "x" * 97]
)
def test_ambiguous_or_oversized_single_choice_rejected(raw):
    with pytest.raises(ValueError):
        parse_reply(question(), raw)


def test_numeric_representation_and_significant_figures_preserved():
    doc = question(
        response_type="NUMERIC",
        choices=[],
        correct_choice_id="",
        numeric_spec=spec(
            significant_figures_policy="EXACT",
            significant_figures=3,
            accepted_forms=["DECIMAL", "SCIENTIFIC"],
        ),
    )
    text = question_text(doc, 5)
    assert "Units: m, cm" in text and "3 significant figures" in text
    for raw, value, unit in [("1.00 | m", "1.00", "m"), ("100. | cm", "100.", "cm")]:
        parsed = parse_reply(doc, raw)
        assert (parsed.value, parsed.unit) == (value, unit)
        assert grade_numeric(uuid4(), uuid4(), doc, parsed.value, parsed.unit).score == 1
    parsed = parse_reply(doc, "1.0 | m")
    assert grade_numeric(uuid4(), uuid4(), doc, parsed.value, parsed.unit).score == 0
    no_unit = question(
        response_type="NUMERIC",
        choices=[],
        correct_choice_id="",
        numeric_spec=spec(canonical_unit="", units=[{"label": "", "factor": "1", "offset": "0"}]),
    )
    assert parse_reply(no_unit, "1").unit == ""
    assert "no unit" in question_text(no_unit, 1)


@pytest.mark.parametrize(
    "raw", ["NaN | m", "1e99 | m", "1/0 | m", "1 | unknown", "1 | m | m", "1 m", "1", "1,2 | m"]
)
def test_numeric_invalid_forms_do_not_create_a_response(raw):
    doc = question(response_type="NUMERIC", choices=[], correct_choice_id="", numeric_spec=spec())
    with pytest.raises(ValueError):
        parse_reply(doc, raw)


def test_choice_labels_do_not_depend_on_correct_answer():
    doc = question()
    alternative = doc.model_copy(update={"correct_choice_id": "B", "worked_solution": "different"})
    assert question_text(doc, 1) == question_text(alternative, 1)
    assert parse_reply(doc, "2") == parse_reply(alternative, "2")
    assert not supports(doc.model_copy(update={"choices": [Choice(id="A", text="only one")]}))


def test_invalid_numeric_policy_and_duplicate_choice_ids_are_unsuitable():
    assert not supports(
        question(
            response_type="NUMERIC",
            choices=[],
            correct_choice_id="",
            numeric_spec=spec(significant_figures_policy="EXACT", significant_figures=3),
        )
    )
    assert not supports(question(choices=[{"id": "A", "text": "One"}, {"id": "A", "text": "Two"}]))
