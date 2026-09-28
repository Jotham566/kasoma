"""FR-GRD-008 deterministic transfer selection guards."""

from uuid import uuid4

import pytest

from services.content_contracts import DraftDocument
from services.reassessment_engine import (
    CONFIG,
    near_duplicate,
    primary,
    same_skill,
    select_candidate,
)


@pytest.mark.parametrize(
    "left,right",
    [
        ("What is 12 + 24?", "WHAT is 93 + 18?"),
        (
            "A taxi travels 12 km in two hours. Find its speed.",
            "A taxi travels 50 km in two hours; find its speed!",
        ),
        ("Select the marked symbol in the diagram", "Select marked symbol in the diagram"),
        ("ＰＩＣＫ Alpha", "pick alpha"),
    ],
)
def test_rejects_text_and_numeric_structure_clones(left, right):
    assert near_duplicate(left, right)
    assert near_duplicate(right, left)


def test_distinct_context_is_not_text_clone():
    assert not near_duplicate(
        "Select the Alpha label.", "The test panel has two controls. Which one starts the timer?"
    )


def test_primary_and_difficulty_are_required():
    a, b = sorted([uuid4(), uuid4()], key=str)
    doc = DraftDocument(
        concept_id=uuid4(),
        competency_mappings=[
            {"competency_id": b, "weight": 0.5},
            {"competency_id": a, "weight": 0.5},
        ],
    )
    assert primary(doc) == a
    assert same_skill(doc, doc)
    assert not same_skill(doc, doc.model_copy(update={"difficulty": "CHALLENGING"}))
    assert not same_skill(doc, DraftDocument())


def test_reviewed_pair_precedes_fallback_and_replay_ties_are_stable():
    fallback = {"basis": "SAME_SKILL_DIFFICULTY", "version_id": "a"}
    pair = {"basis": "EQUIVALENT", "version_id": "z"}
    snapshot = {"configuration": CONFIG, "candidates": [fallback, pair]}
    assert select_candidate(snapshot) == pair
    snapshot["candidates"].reverse()
    assert select_candidate(snapshot) == pair
    with pytest.raises(ValueError):
        select_candidate({"configuration": CONFIG | {"version": "unknown"}, "candidates": [pair]})
