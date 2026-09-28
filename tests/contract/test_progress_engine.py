"""FR-MST-004/005: hand-calculated, confidence-aware synthetic rollups."""

from datetime import timedelta
from uuid import UUID

import pytest

from services.mastery_engine import estimate, normalize
from services.progress_engine import summarize
from tests.contract.test_mastery_engine import COMPETENCY, CONCEPT, NOW, grade

SKILL = (CONCEPT, COMPETENCY)


def rollup(rows, skills=None, at=NOW):
    return summarize(UUID(int=99), "Synthetic scope", skills or {SKILL}, rows, at)


def test_empty_scope_and_unassessed_skills_are_distinct():
    empty = summarize(UUID(int=99), "Empty", set(), [], NOW)
    assert empty.mastery is None and empty.confidence == 0
    prior = rollup([])
    assert prior.mastery == 0.5 and prior.confidence == 0
    assert prior.mapped_skill_count == 1 and prior.assessed_skill_count == 0
    assert prior.change == prior.display_state == "NOT_ENOUGH_EVIDENCE"


def test_equal_skill_mean_includes_prior_and_counts_unique_attempts():
    second = (CONCEPT, UUID(int=3))
    third = (CONCEPT, UUID(int=4))
    rows = [
        normalize(grade(mapping_weight=0.5)),
        normalize(grade(competency_id=second[1], mapping_weight=0.5)),
    ]
    result = rollup(rows, {SKILL, second, third})
    one = estimate(*SKILL, rows[:1], NOW)
    assert result.mastery == pytest.approx((2 * one.mastery + 0.5) / 3)
    assert result.confidence == pytest.approx(2 * one.confidence / 3)
    assert result.evidence_count == 1
    assert result.assessed_skill_count == 2 and result.mapped_skill_count == 3
    assert result.last_evidence_at == NOW
    assert result == rollup(list(reversed(rows)), {third, second, SKILL})


@pytest.mark.parametrize("score,change", [(1, "HIGHER"), (0, "LOWER"), (0.5, "UNCHANGED")])
def test_change_compares_same_scope_and_time_only_with_enough_confidence(score, change):
    rows = [normalize(grade(i, points_awarded=0.5)) for i in range(10)]
    rows.append(normalize(grade(20, points_awarded=score)))
    assert rollup(rows).change == change
    assert rollup(rows[:1]).change == "NOT_ENOUGH_EVIDENCE"
    aged = rollup(rows, at=NOW + timedelta(days=365))
    assert aged.confidence < rollup(rows).confidence
    assert aged.change == "NOT_ENOUGH_EVIDENCE"


def test_scoping_replay_and_corruption_rejection():
    row = normalize(grade())
    assert rollup([row, row]) == rollup([row])
    assert rollup([normalize(grade(concept_id=UUID(int=999)))]).evidence_count == 0
    with pytest.raises(ValueError, match="versioned"):
        rollup([row.model_copy(update={"base_weight": 999})])
    with pytest.raises(ValueError, match="after calculation"):
        rollup([normalize(grade(occurred_at=NOW + timedelta(seconds=1)))])
