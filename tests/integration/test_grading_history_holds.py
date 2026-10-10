"""Exact immutable grading snapshots remain held while workflow advances independently."""

from uuid import uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.domain.grading_work import GradingHistory
from services.grading_work_store import claim_next, enqueue, finish_neutral
from tests.integration.test_assessment import assessment as assessment_fixture
from tests.integration.test_data_requests import claim, create
from tests.integration.test_grading_work_store import ungraded as ungraded_fixture
from tests.integration.test_legal_holds import hold, prepare, release

assessment = assessment_fixture
ungraded = ungraded_fixture
pytestmark = pytest.mark.integration


def test_exact_history_hold_preserves_snapshot_without_freezing_new_transitions(
    ungraded, assessment
):
    identity, attempt = ungraded
    _, client, actors, *_ = assessment
    with Session(identity.engine) as db, db.begin():
        enqueue(db, attempt, uuid4(), identity.clock())
        history = db.scalar(select(GradingHistory))
        history_id, original = history.id, history.snapshot
    target, body = prepare(assessment)
    key = str(uuid4())
    body |= {"record_type": "GRADING_HISTORY", "record_id": str(history_id)}
    held = hold(client, actors["admin"], target, body, key)
    assert held.status_code == 201, held.text
    assert hold(client, actors["admin"], target, body, key).json() == held.json()
    with Session(identity.engine) as db, db.begin():
        running = claim_next(db, identity.clock())
        finish_neutral(db, attempt, running.claim_id, identity.clock())
    with Session(identity.engine) as db:
        assert db.get(GradingHistory, history_id).snapshot == original
        assert db.scalar(select(func.count()).select_from(GradingHistory)) == 3
    with identity.engine.begin() as db, pytest.raises(DBAPIError, match="Record is legally held"):
        db.execute(text("DELETE FROM assessment_grading_history WHERE id=:id"), {"id": history_id})
    with identity.engine.begin() as db, pytest.raises(DBAPIError, match="history is immutable"):
        db.execute(
            text("UPDATE assessment_grading_history SET snapshot='{}' WHERE id=:id"),
            {"id": history_id},
        )
    released = release(client, actors["admin"], target, held.json()["id"])
    assert released.status_code == 200, released.text
    # Release removes only the hold, never the independent history immutability rule.
    with identity.engine.begin() as db, pytest.raises(DBAPIError, match="history is immutable"):
        db.execute(text("DELETE FROM assessment_grading_history WHERE id=:id"), {"id": history_id})


def test_history_hold_rejects_foreign_request_and_wrong_staff(ungraded, assessment):
    identity, attempt = ungraded
    _, client, actors, *_ = assessment
    with Session(identity.engine) as db, db.begin():
        enqueue(db, attempt, uuid4(), identity.clock())
        history_id = db.scalar(select(GradingHistory.id))
    target, body = prepare(assessment)
    body |= {"record_type": "GRADING_HISTORY", "record_id": str(history_id)}
    for name in ["learner", "support", "reviewer"]:
        assert hold(client, actors[name], target, body).status_code == 403
    foreign = create(client, actors["other"], "DELETE").json()["id"]
    assert claim(client, actors["admin"], foreign).status_code == 200
    assert hold(client, actors["admin"], foreign, body).status_code == 404
    assert (
        hold(client, actors["admin"], target, body | {"record_id": str(uuid4())}).status_code == 404
    )
    # A bare attempt UUID is not accepted as an exact history record ID.
    assert (
        hold(client, actors["admin"], target, body | {"record_id": str(attempt)}).status_code == 404
    )
