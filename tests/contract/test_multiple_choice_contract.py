"""FR-GRD-001: exhaustive exact-set matching, strict bounds and safe projection."""

from itertools import combinations, permutations
from uuid import uuid4

import pytest
from pydantic import ValidationError

from services.assessment_contracts import MultipleChoiceResponse, MultipleChoiceResponseSpec
from services.content_contracts import DraftDocument
from services.grading import grade_multiple_choice


def document():
    return DraftDocument(
        response_type="MULTIPLE_CHOICE",
        choices=[{"id": c, "text": c} for c in "ABCD"],
        correct_choice_ids=["C", "A"],
        maximum_points=3,
    )


def test_all_nonempty_subsets_and_permutations_have_exact_scores():
    doc = document()
    assert doc.correct_choice_ids == ["A", "C"]
    for size in range(1, 5):
        for subset in combinations("ABCD", size):
            for selected in permutations(subset):
                result = grade_multiple_choice(uuid4(), uuid4(), doc, list(selected))
                assert result.score == (1 if set(selected) == {"A", "C"} else 0)
                assert result.points_awarded == result.score * 3
                assert result.grader_version == "multiple-choice-set-v1"
    safe = MultipleChoiceResponseSpec(choices=doc.choices).model_dump()
    assert set(safe) == {"type", "choices"}


@pytest.mark.parametrize("ids", [[], ["A", "A"], ["a"], ["AA"], [1], list("ABCDEFGHI")])
def test_invalid_response_sets_are_rejected(ids):
    with pytest.raises(ValidationError):
        MultipleChoiceResponse(type="MULTIPLE_CHOICE", choice_ids=ids)


def test_canonical_response_and_strict_keys():
    a = MultipleChoiceResponse(type="MULTIPLE_CHOICE", choice_ids=["C", "A"])
    b = MultipleChoiceResponse(type="MULTIPLE_CHOICE", choice_ids=["A", "C"])
    assert a == b and a.choice_ids == ["A", "C"]
    with pytest.raises(ValidationError):
        MultipleChoiceResponse(type="MULTIPLE_CHOICE", choice_ids=["A"], score=1)
    with pytest.raises(ValidationError):
        DraftDocument(correct_choice_ids=["A", "A"])
    for ids in [[], ["Z"], ["A", "A"]]:
        with pytest.raises(ValueError):
            grade_multiple_choice(uuid4(), uuid4(), document(), ids)
