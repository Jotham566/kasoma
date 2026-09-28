"""FR-MST-006: factor direction, prerequisite gates and exact deterministic replay."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from services.mastery_engine import estimate
from services.recommendation_engine import Candidate, RankingInput, Target, rank, replay

AT = datetime(2026, 9, 28, tzinfo=UTC)


def target(n=1, **updates):
    e = estimate(UUID(int=n), UUID(int=100), [], AT).model_copy(
        update={
            "mastery": 0.5,
            "confidence": 0.6,
            "last_evidence_at": AT - timedelta(days=2),
        }
        | updates
    )
    return Target(estimate=e, topic_id=UUID(int=n + 1000), topic=f"Synthetic topic {n}")


def candidates(t, count=10):
    return tuple(
        Candidate(
            item_id=UUID(int=t.estimate.concept_id.int * 100 + i),
            version_id=UUID(int=t.estimate.concept_id.int * 100 + i),
            concept_id=t.estimate.concept_id,
            competency_id=t.estimate.competency_id,
            mapping_weight=1,
            difficulty="STANDARD",
            response_type="SINGLE_CHOICE",
            scenario_hash=str(i),
            expected_seconds=60,
        )
        for i in range(count)
    )


def calculate(*targets, content=None):
    return rank(
        RankingInput(
            calculated_at=AT,
            targets=targets,
            candidates=content
            if content is not None
            else tuple(c for t in targets for c in candidates(t)),
            desired_item_count=5,
        )
    )


@pytest.mark.parametrize(
    "field,value",
    [("mastery", 0.3), ("confidence", 0.2), ("last_evidence_at", AT - timedelta(days=6))],
)
def test_estimate_factors_raise_priority_and_change_winner(field, value):
    first, second = target(1), target(2)
    assert calculate(first, second).concept_id == first.estimate.concept_id
    improved = second.model_copy(
        update={"estimate": second.estimate.model_copy(update={field: value})}
    )
    result = calculate(first, improved)
    assert result.concept_id == second.estimate.concept_id
    assert result.scores[1].priority > result.scores[0].priority


def test_importance_repetition_readiness_and_availability():
    first, second, prerequisite = target(1), target(2), target(3, mastery=0.46)
    assert (
        calculate(first, second.model_copy(update={"importance": 1.5})).concept_id
        == second.estimate.concept_id
    )
    assert (
        calculate(first.model_copy(update={"recent_exposures": 1}), second).concept_id
        == second.estimate.concept_id
    )
    dependent = first.model_copy(
        update={"prerequisite_concepts": (prerequisite.estimate.concept_id,)}
    )
    result = calculate(
        dependent, second, prerequisite, content=candidates(dependent) + candidates(second)
    )
    assert (
        result.scores[0].factors["prerequisite_readiness"]
        < result.scores[1].factors["prerequisite_readiness"]
    )
    assert result.concept_id == second.estimate.concept_id
    assert (
        calculate(first, second, content=candidates(first, 4) + candidates(second)).concept_id
        == second.estimate.concept_id
    )
    assert calculate(first, content=()).reason_code == "CONTENT_UNAVAILABLE"


def test_confident_prerequisite_gap_redirects_including_transitive_and_unavailable():
    prerequisite = target(1, mastery=0.44, confidence=0.35)
    dependent = target(2, mastery=0.01).model_copy(update={"prerequisite_concepts": (UUID(int=1),)})
    result = calculate(prerequisite, dependent)
    assert result.concept_id == UUID(int=1)
    assert result.reason_code == "GATHER_MORE_EVIDENCE"  # Never overstate sparse evidence.
    assert (
        calculate(prerequisite, dependent, content=candidates(dependent)).reason_code
        == "CONTENT_UNAVAILABLE"
    )
    uncertain = prerequisite.model_copy(
        update={"estimate": prerequisite.estimate.model_copy(update={"confidence": 0.349})}
    )
    assert calculate(uncertain, dependent).concept_id == UUID(int=2)
    third = target(3, mastery=0).model_copy(update={"prerequisite_concepts": (UUID(int=2),)})
    assert calculate(prerequisite, dependent, third).concept_id == UUID(int=1)


def test_replay_ties_and_invalid_graph():
    a, b = target(1), target(2)
    plan = calculate(b, a)
    assert plan == calculate(a, b)
    replay(plan)
    with pytest.raises(ValueError, match="mismatch"):
        replay(plan.model_copy(update={"learner_text": "Changed"}))
    with pytest.raises(ValueError, match="Duplicate"):
        calculate(a, a)
    with pytest.raises(ValueError, match="Cyclic"):
        calculate(
            a.model_copy(update={"prerequisite_concepts": (UUID(int=2),)}),
            b.model_copy(update={"prerequisite_concepts": (UUID(int=1),)}),
        )
    with pytest.raises(ValueError, match="calculation"):
        calculate(target(1, calculated_at=AT + timedelta(seconds=1)))


def test_item_mapping_difficulty_diversity_exposure_and_no_identity_repeats():
    t = target()
    content = candidates(t)
    # Equal mapping and difficulty: new formats and scenarios win before exposure and ID.
    content = tuple(
        c.model_copy(update={"scenario_hash": "same", "historical_exposures": 3}) for c in content
    )
    special = content[-1].model_copy(
        update={"response_type": "NUMERIC", "scenario_hash": "other", "historical_exposures": 0}
    )
    content = content[:-1] + (special,)
    result = calculate(t, content=content)
    assert result.item_version_ids[0] == special.version_id
    assert len(set(result.item_version_ids)) == 5
    assert len(result.item_reasons) == 5
    assert result.estimated_minutes == 5
    # Mapping strength precedes desired difficulty.
    special = special.model_copy(update={"mapping_weight": 0.5})
    assert (
        special.version_id not in calculate(t, content=content[:-1] + (special,)).item_version_ids
    )


def test_unknown_prerequisite_is_neutral_and_factor_bounds_hold():
    t = target(1, last_evidence_at=None).model_copy(
        update={
            "prerequisite_concepts": (UUID(int=9),),
            "recent_exposures": 1000,
        }
    )
    result = calculate(t)
    factors = result.scores[0].factors
    assert factors["prerequisite_readiness"] == pytest.approx(0.7)
    assert factors["spacing_due"] == 1.3
    assert factors["recent_repetition_penalty"] == 0.3
    assert result.scores[0].blocked_by == ()
    assert result.concept_id == t.estimate.concept_id
