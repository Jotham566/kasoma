"""FR-GRD-006: bounded reviewed hints, immutable legacy replay and independence."""

import pytest
from pydantic import ValidationError

from services.assessment_contracts import HintRequest
from services.content_contracts import DraftDocument
from services.mastery_engine import BASELINE, Evidence, estimate, fingerprint, normalize
from tests.contract.test_mastery_engine import NOW, grade


@pytest.mark.parametrize("hints", [[""], ["  "], ["x" * 1001], ["a"] * 4])
def test_hint_content_bounds(hints):
    with pytest.raises(ValidationError):
        DraftDocument(hints=hints)


@pytest.mark.parametrize("count", [0, 1, 2, 3])
def test_hint_count_weights_without_changing_observed_score(count):
    source = grade(hint_count=count, highest_hint_level=count)
    row = normalize(source)
    assert row.score == 1
    assert row.source.highest_hint_level == count
    assert row.independence_weight == pytest.approx(max(0.5, 1 - 0.15 * count))
    if count:
        independent = normalize(grade())
        assert row.base_weight < independent.base_weight


def test_legacy_hintless_evidence_preserves_original_hash_and_replay():
    source = grade()
    old_fields = source.model_dump(mode="json", exclude={"highest_hint_level"})
    old_hash = fingerprint(
        {
            "grade": old_fields,
            "configuration": BASELINE.model_dump(),
            "calculated_at": source.occurred_at.isoformat(),
        }
    )
    row = normalize(source)
    serialized = row.model_dump(mode="json")
    del serialized["source"]["highest_hint_level"]
    old = Evidence.model_validate(serialized)
    assert row.input_hash == old_hash
    assert old == row
    assert estimate(source.concept_id, source.competency_id, [old], NOW) == estimate(
        source.concept_id, source.competency_id, [row], NOW
    )


def test_hint_request_rejects_client_text_and_levels():
    for body in [
        {"expected_hint_level": -1},
        {"expected_hint_level": 4},
        {"expected_hint_level": 0, "hint_count": 0},
        {"expected_hint_level": 0, "text": "unreviewed"},
    ]:
        with pytest.raises(ValidationError):
            HintRequest.model_validate(body)
