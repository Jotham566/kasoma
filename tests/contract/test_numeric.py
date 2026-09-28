"""FR-GRD-002: synthetic numeric correctness and hostile-input regression cases."""

from fractions import Fraction
from uuid import uuid4

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from services.assessment_contracts import NumericResponse, SubmitAnswer
from services.content_contracts import DraftDocument
from services.grading import grade_numeric
from services.numeric import NumericSpec, evaluate_numeric, parse_number, specification_errors


def spec(**changes):
    return NumericSpec.model_validate(
        {
            "expected_value": "1",
            "canonical_unit": "m",
            "units": [
                {"label": "m", "factor": "1", "offset": "0"},
                {"label": "cm", "factor": "1/100", "offset": "0"},
            ],
            "absolute_tolerance": "0",
            "relative_tolerance": "0",
            "accepted_forms": ["DECIMAL", "SCIENTIFIC", "FRACTION"],
            "significant_figures_policy": "IGNORE",
            "significant_figures": None,
            **changes,
        }
    )


@pytest.mark.parametrize(
    "raw,unit,score",
    [
        ("1", "m", True),
        ("100", "cm", True),
        ("1e2", "cm", True),
        ("2/2", "m", True),
        ("+1.0", "m", True),
        (" 1 ", "m", True),
        ("0.99", "m", False),
        ("-1", "m", False),
    ],
)
def test_exact_equivalent_forms_and_units(raw, unit, score):
    assert evaluate_numeric(spec(), raw, unit) == (score, True)


@pytest.mark.parametrize(
    "expected,absolute,relative,raw,matched",
    [
        ("1", "0.1", "0", "1.1", True),
        ("1", "0.1", "0", "0.9", True),
        ("1", "0.1", "0", "1.1000000000000001", False),
        ("1", "0.1", "0", "0.8999999999999999", False),
        ("-10", "0", "0.1", "-11", True),
        ("-10", "0", "0.1", "-8.999", False),
        ("0", "0", "0.2", "0", True),
        ("0", "0", "0.2", "0.01", False),
        ("0", "0.01", "0.2", "-0.01", True),
        ("1/3", "0", "0", "2/6", True),
        ("1/3", "0", "0", "0.333333", False),
        ("10", "0.2", "0.1", "11", True),
    ],
)
def test_inclusive_absolute_relative_and_zero_boundaries(
    expected, absolute, relative, raw, matched
):
    assert (
        evaluate_numeric(
            spec(expected_value=expected, absolute_tolerance=absolute, relative_tolerance=relative),
            raw,
            "m",
        )[0]
        is matched
    )


def test_reviewed_offset_conversion():
    answer = spec(
        expected_value="273.15",
        canonical_unit="K",
        units=[
            {"label": "K", "factor": "1", "offset": "0"},
            {"label": "C", "factor": "1", "offset": "273.15"},
        ],
    )
    assert evaluate_numeric(answer, "0", "C") == (True, True)
    assert evaluate_numeric(answer, "273.15", "K") == (True, True)
    assert not evaluate_numeric(answer, "0", "K")[0]


@pytest.mark.parametrize(
    "raw,count",
    [
        ("1200", 2),
        ("1200.", 4),
        ("1.200e3", 4),
        ("1200e0", 4),
        ("0.00120", 3),
        ("-1.20", 3),
        ("0", 1),
        ("0.00", 2),
        (".0500", 3),
    ],
)
def test_explicit_significant_figure_convention(raw, count):
    assert parse_number(raw)[2] == count


def test_precision_is_independent_of_unit_conversion_and_numeric_correctness():
    answer = spec(
        accepted_forms=["DECIMAL", "SCIENTIFIC"],
        significant_figures_policy="EXACT",
        significant_figures=3,
    )
    assert evaluate_numeric(answer, "1.00", "m") == (True, True)
    assert evaluate_numeric(answer, "1", "m") == (True, False)
    assert evaluate_numeric(answer, "1.00e2", "cm") == (True, True)
    document = DraftDocument(
        response_type="NUMERIC",
        numeric_spec=answer,
        maximum_points=2,
        remediation="Check precision.",
    )
    grade = grade_numeric(uuid4(), uuid4(), document, "1", "m")
    assert grade.points_awarded == 0 and grade.score == 0
    assert grade.feedback.correct_elements and grade.feedback.missing_elements


@pytest.mark.parametrize(
    "raw",
    [
        "",
        " ",
        "NaN",
        "Infinity",
        "-inf",
        "1/0",
        "1+1",
        "__import__('os')",
        "1,000",
        "1 m",
        "0x10",
        "1e13",
        "1e-13",
        "1000000000001",
        "9" * 65,
        "<script>",
        "1e99999999",
        "1//2",
        "1/2/3",
        "2**999999",
        "１",
        "1\x00",
    ],
)
def test_hostile_and_unsupported_numeric_syntax(raw):
    with pytest.raises(ValueError):
        parse_number(raw)


@pytest.mark.parametrize(
    "changes,field",
    [
        ({"expected_value": "NaN"}, "expected_value"),
        ({"absolute_tolerance": "-1"}, "absolute_tolerance"),
        ({"relative_tolerance": "1.1"}, "relative_tolerance"),
        ({"canonical_unit": "unknown"}, "canonical_unit"),
        ({"units": [{"label": "m", "factor": "0", "offset": "0"}]}, "units"),
        ({"units": [{"label": "m", "factor": "1", "offset": "1"}]}, "units"),
        ({"units": [{"label": "m", "factor": "1", "offset": "0"}] * 2}, "units"),
        ({"accepted_forms": ["DECIMAL", "DECIMAL"]}, "accepted_forms"),
        (
            {"significant_figures_policy": "EXACT", "significant_figures": None},
            "significant_figures",
        ),
        ({"significant_figures_policy": "EXACT", "significant_figures": 3}, "significant_figures"),
        ({"significant_figures": 3}, "significant_figures"),
    ],
)
def test_invalid_specifications_are_publication_errors(changes, field):
    assert field in specification_errors(spec(**changes))


def test_unsupported_form_and_unknown_unit_are_not_graded():
    with pytest.raises(ValueError):
        evaluate_numeric(spec(accepted_forms=["DECIMAL"]), "1e0", "m")
    with pytest.raises(ValueError):
        evaluate_numeric(spec(), "1", "M")
    with pytest.raises(ValidationError):
        NumericResponse(type="NUMERIC", value="1", unit="m", score=1)
    with pytest.raises(ValidationError):
        SubmitAnswer(
            session_item_id=uuid4(), response={"type": "NUMERIC", "value": "1", "choice_id": "A"}
        )


@given(st.integers(min_value=-100000, max_value=100000), st.integers(min_value=1, max_value=1000))
def test_rational_conversion_equivalence(value, factor):
    expected = Fraction(value, factor)
    answer = spec(
        expected_value=str(expected),
        units=[
            {"label": "m", "factor": "1", "offset": "0"},
            {"label": "scaled", "factor": f"1/{factor}", "offset": "0"},
        ],
    )
    assert evaluate_numeric(answer, str(value), "scaled") == (True, True)
    assert evaluate_numeric(answer, str(expected), "m") == (True, True)


@given(st.integers(-10000, 10000), st.integers(0, 100), st.integers(1, 100))
def test_tolerance_boundary_is_exact(center, tolerance, denominator):
    answer = spec(
        expected_value=str(center), absolute_tolerance=str(Fraction(tolerance, denominator))
    )
    boundary = Fraction(center) + Fraction(tolerance, denominator)
    assert evaluate_numeric(answer, str(boundary), "m")[0]
    assert not evaluate_numeric(answer, str(boundary + Fraction(1, denominator * 1000)), "m")[0]
