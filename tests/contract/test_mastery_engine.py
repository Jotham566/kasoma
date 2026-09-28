"""Specification 05 formula, invariants and replay; synthetic evidence only."""

import math
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from services.mastery_engine import BASELINE, GradeInput, display_state, estimate, normalize

NOW = datetime(2026, 9, 28, 12, tzinfo=UTC)
CONCEPT, COMPETENCY = UUID(int=1), UUID(int=2)


def grade(index=1, **changes):
    return GradeInput.model_validate(
        {
            "attempt_id": UUID(int=100 + index),
            "item_id": UUID(int=200 + index),
            "item_version_id": UUID(int=300 + index),
            "concept_id": CONCEPT,
            "competency_id": COMPETENCY,
            "occurred_at": NOW,
            "response_type": "SINGLE_CHOICE",
            "content_difficulty": "STANDARD",
            "points_awarded": 1,
            "points_possible": 1,
            "grade_confidence": 1,
            "method": "DETERMINISTIC",
            "status": "GRADED",
            "mapping_weight": 1,
        }
        | changes
    )


def project(*sources, when=NOW):
    rows = [normalize(source) for source in sources]
    assert all(row is not None for row in rows)
    return estimate(CONCEPT, COMPETENCY, rows, when)


def test_neutral_prior_is_not_a_confident_grade():
    result = project()
    assert result.mastery == 0.5
    assert result.confidence == result.effective_weight == result.evidence_count == 0
    assert result.last_evidence_at is None
    assert result.display_state == "NOT_ENOUGH_EVIDENCE"
    assert result.reason_code == "NO_EVIDENCE"


def test_hand_calculated_baseline_and_recorded_versions():
    result = project(grade())
    assert result.mastery == pytest.approx(2 / 3)
    assert result.effective_weight == 1
    assert result.confidence == pytest.approx((1 - math.exp(-1 / 5)) * (0.6 + 0.4 / 6))
    assert result.configuration.difficulty_mapping_version == "content-difficulty-v1"
    assert result.configuration.algorithm_version == "weighted-evidence-v1"
    assert len(result.input_hash) == 64
    assert result.display_state == "NOT_ENOUGH_EVIDENCE"


@pytest.mark.parametrize(
    "label,engine,weight",
    [
        ("FOUNDATIONAL", "FOUNDATIONAL", 0.85),
        ("STANDARD", "CORE", 1),
        ("CHALLENGING", "STRETCH", 1.15),
    ],
)
def test_adr017_mapping_preserves_original_label(label, engine, weight):
    row = normalize(grade(content_difficulty=label))
    assert row.source.content_difficulty == label
    assert row.engine_difficulty == engine
    assert row.base_weight == weight


@pytest.mark.parametrize("status", ["PENDING", "LOW_CONFIDENCE", "REVIEW_REQUIRED"])
def test_unresolved_grades_are_not_evidence_even_with_high_confidence(status):
    assert normalize(grade(status=status, grade_confidence=1)) is None


def test_independence_floor_and_solution_penalty():
    independent = normalize(grade())
    hinted = normalize(grade(hint_count=1))
    solution = normalize(grade(solution_seen_before_grade=True))
    dependent = normalize(grade(hint_count=100, solution_seen_before_grade=True))
    assert independent.independence_weight == 1
    assert hinted.independence_weight == 0.85
    assert solution.independence_weight == 0.75
    assert dependent.independence_weight == 0.5
    assert project(grade()).mastery > project(grade(hint_count=1)).mastery


def test_confidence_and_mapping_weights():
    assert normalize(grade(grade_confidence=0.2)).confidence_weight == 1
    model = normalize(grade(method="RUBRIC_MODEL", grade_confidence=0.8, mapping_weight=0.5))
    assert model.base_weight == 0.4
    assert project(grade()).confidence > project(grade(mapping_weight=0.5)).confidence
    assert project(grade()).mastery > project(grade(mapping_weight=0.5)).mastery


def test_recency_halves_weight_and_moves_estimate_toward_prior():
    current = project(grade())
    old = project(grade(), when=NOW + timedelta(days=30))
    assert old.effective_weight == current.effective_weight / 2
    assert old.mastery == pytest.approx(1.5 / 2.5)
    assert old.confidence < current.confidence
    failed = project(grade(points_awarded=0), when=NOW + timedelta(days=30))
    assert failed.mastery > project(grade(points_awarded=0)).mastery


def test_coverage_uses_stable_items_and_formats_not_versions():
    repeated = project(grade(), grade(2, item_id=UUID(int=201)), grade(3, item_id=UUID(int=201)))
    diverse_items = project(grade(), grade(2), grade(3))
    diverse_formats = project(grade(), grade(2), grade(3, response_type="NUMERIC"))
    assert repeated.distinct_item_count == 1
    assert repeated.mastery == diverse_items.mastery == diverse_formats.mastery
    assert repeated.confidence < diverse_items.confidence < diverse_formats.confidence


@pytest.mark.parametrize(
    "score,confidence,state",
    [
        (1, 0.24999, "NOT_ENOUGH_EVIDENCE"),
        (1, 0.25, "DEVELOPING_ESTIMATE"),
        (0, 0.49999, "DEVELOPING_ESTIMATE"),
        (0.49999, 0.5, "NEEDS_ATTENTION"),
        (0.5, 0.5, "DEVELOPING"),
        (0.74999, 1, "DEVELOPING"),
        (0.75, 0.5, "STRONG"),
    ],
)
def test_display_boundaries(score, confidence, state):
    assert display_state(score, confidence) == state


def test_replay_is_order_independent_and_duplicate_delivery_is_idempotent():
    sources = [grade(), grade(2, points_awarded=0), grade(3, response_type="NUMERIC")]
    original = project(*sources)
    replay = project(*reversed(sources), sources[0])
    assert original == replay
    assert original.evidence_count == 3
    assert project(*sources, when=NOW + timedelta(days=1)).input_hash != original.input_hash


def test_conflicting_duplicate_or_corrupted_evidence_fails_closed():
    with pytest.raises(ValueError, match="Conflicting"):
        project(grade(), grade(points_awarded=0))
    row = normalize(grade())
    with pytest.raises(ValueError, match="versioned"):
        estimate(CONCEPT, COMPETENCY, [row.model_copy(update={"base_weight": 999})], NOW)
    with pytest.raises(ValueError, match="versioned"):
        estimate(
            CONCEPT, COMPETENCY, [row], NOW, BASELINE.model_copy(update={"half_life_days": 60})
        )


def test_cross_skill_and_future_evidence_rejected():
    with pytest.raises(ValueError, match="another skill"):
        project(grade(concept_id=UUID(int=999)))
    with pytest.raises(ValueError, match="after calculation"):
        project(grade(occurred_at=NOW + timedelta(seconds=1)))
    with pytest.raises(ValueError, match="timezone-aware"):
        project(grade(), when=NOW.replace(tzinfo=None))


@pytest.mark.parametrize(
    "change",
    [
        {"points_awarded": 2},
        {"points_awarded": -1},
        {"points_possible": 0},
        {"grade_confidence": float("nan")},
        {"points_possible": float("inf")},
        {"mapping_weight": 0},
        {"mapping_weight": 1.1},
        {"hint_count": -1},
        {"occurred_at": NOW.replace(tzinfo=None)},
        {"content_difficulty": "CORE"},
        {"answer_text": "never accepted here"},
    ],
)
def test_invalid_or_answer_bearing_inputs_rejected(change):
    with pytest.raises(ValidationError):
        grade(**change)


@given(st.lists(st.floats(min_value=0, max_value=1, allow_nan=False), max_size=40))
def test_mastery_confidence_bounds_and_replay(scores):
    sources = [grade(i, points_awarded=score) for i, score in enumerate(scores)]
    result = project(*sources)
    assert 0 <= result.mastery <= 1
    assert 0 <= result.confidence <= 1
    assert result == project(*reversed(sources))


@given(st.integers(min_value=0, max_value=50), st.integers(min_value=0, max_value=3650))
def test_hints_and_age_never_increase_correct_evidence_influence(hints, days):
    independent = project(grade())
    affected = project(grade(hint_count=hints), when=NOW + timedelta(days=days))
    assert 0.5 <= affected.mastery <= independent.mastery
    assert affected.confidence <= independent.confidence
