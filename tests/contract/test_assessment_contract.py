import json
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

from services.assessment_contracts import StartRevision, SubmitAnswer
from services.content_contracts import DraftDocument
from services.grading import grade_choice


@pytest.mark.parametrize("key", ["score", "mastery", "hint_count", "role", "item_version_id"])
def test_learner_cannot_supply_authoritative_fields(key):
    with pytest.raises(ValidationError):
        SubmitAnswer.model_validate(
            {"session_item_id": str(uuid4()), "response": {"choice_id": "A"}, key: 1}
        )


@pytest.mark.parametrize("count", [0, 1, 4, 11, 100])
def test_revision_size_boundary(count):
    with pytest.raises(ValidationError):
        StartRevision(subject_id=uuid4(), topic_id=uuid4(), desired_item_count=count)


@pytest.mark.parametrize("maximum", [1, 2, 20])
@pytest.mark.parametrize("answer,score", [("A", 1), ("B", 0)])
def test_exact_single_choice_benchmark(maximum, answer, score):
    document = DraftDocument(
        choices=[{"id": "A", "text": "Alpha"}, {"id": "B", "text": "Beta"}],
        correct_choice_id="A",
        maximum_points=maximum,
        remediation="Read the labels.",
    )
    result = grade_choice(uuid4(), uuid4(), document, answer)
    assert result.score == score and result.points_awarded == maximum * score
    assert result.confidence == 1 and result.method == "DETERMINISTIC"
    with pytest.raises(ValueError):
        grade_choice(uuid4(), uuid4(), document, "Z")


def test_event_allowlist_excludes_answers_and_identifiers():
    schema = json.loads(Path("packages/analytics-schema/assessment-event.schema.json").read_text())
    assert not schema["additionalProperties"]
    assert set(schema["properties"]) == {
        "id",
        "session_id",
        "attempt_id",
        "type",
        "version",
        "request_id",
        "created_at",
    }
