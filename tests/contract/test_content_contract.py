import json
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

from services.content_contracts import CHECKLIST, CreateDraft, DraftDocument, ReviewInput


def test_privileged_mutations_reject_status_and_author_injection():
    for injected in [{"status": "APPROVED"}, {"author_id": str(uuid4())}, {"synthetic": False}]:
        with pytest.raises(ValidationError):
            CreateDraft.model_validate(
                {"subject_id": str(uuid4()), "document": {}, "change_reason": "fixture", **injected}
            )


@pytest.mark.parametrize(
    "document",
    [
        {"response_type": "UNREVIEWED_AI"},
        {"difficulty": "ARBITRARY"},
        {"competency_mappings": [{"competency_id": str(uuid4()), "weight": float("nan")}]},
        {"prompt": "x" * 4001},
        {"choices": [{"id": "<script>", "text": "No"}]},
    ],
)
def test_bounded_content_contract(document):
    with pytest.raises(ValidationError):
        DraftDocument.model_validate(document)


def test_checklist_and_registered_event_shape():
    assert len(CHECKLIST) == 15
    review = ReviewInput(
        expected_revision=1,
        reason="Synthetic test",
        decision="APPROVE",
        checklist=sorted(CHECKLIST),
    )
    assert set(review.checklist) == CHECKLIST
    schema = json.loads(Path("packages/analytics-schema/content-event.schema.json").read_text())
    assert schema["additionalProperties"] is False
    assert set(schema["properties"]) == {
        "id",
        "item_version_id",
        "type",
        "version",
        "request_id",
        "created_at",
    }
