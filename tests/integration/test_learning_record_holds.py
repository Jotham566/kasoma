"""Exact learning-record preservation, owned joins and unchanged immutable evidence."""

from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.domain.data_requests import LegalHold, LegalHoldReceipt
from services.domain.mastery import MasteryEvidence, MasteryHistory
from services.legal_holds import active
from tests.integration.test_assessment import assessment as assessment_fixture
from tests.integration.test_data_exports import export
from tests.integration.test_data_requests import claim, create
from tests.integration.test_deletion_preview import get as preview
from tests.integration.test_flags import saved
from tests.integration.test_legal_holds import hold, prepare, release

assessment = assessment_fixture
pytestmark = pytest.mark.integration
KINDS = [
    ("GRADE", "grades", "attempt_id"),
    ("MASTERY_EVIDENCE", "mastery_evidence", "id"),
    ("MASTERY_HISTORY", "mastery_estimate_history", "id"),
]


def record_for(assessment, kind):
    attempt = UUID(saved(assessment)["attempt_id"])
    with Session(assessment[0].engine) as db:
        evidence = db.scalar(select(MasteryEvidence).where(MasteryEvidence.attempt_id == attempt))
        history = db.scalar(
            select(MasteryHistory.id).where(MasteryHistory.evidence_id == evidence.id)
        )
        return {"GRADE": attempt, "MASTERY_EVIDENCE": evidence.id, "MASTERY_HISTORY": history}[kind]


@pytest.mark.parametrize("kind,table,column", KINDS)
def test_learning_hold_lifecycle_preserves_exact_evidence(assessment, kind, table, column):
    identity, client, actors, *_ = assessment
    record = record_for(assessment, kind)
    target, body = prepare(assessment)
    body |= {"record_type": kind, "record_id": str(record)}
    headers = actors["admin"]
    key = str(uuid4())
    result = hold(client, headers, target, body, key)
    assert result.status_code == 201, result.text
    first = result.json()
    assert first["record_type"] == kind and first["record_id"] == str(record)
    assert hold(client, headers, target, body, key).json() == first
    second = hold(client, headers, target, body).json()
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(LegalHoldReceipt)) == 2
        assert active(db, kind, record, identity.clock())
        # No implied preservation of an account or another record kind sharing a UUID.
        assert not active(db, "ATTEMPT", record, identity.clock())
    for held in [first, second]:
        with (
            identity.engine.begin() as db,
            pytest.raises(DBAPIError, match="Record is legally held"),
        ):
            db.execute(text(f"DELETE FROM {table} WHERE {column}=:id"), {"id": record})
        response = release(client, headers, target, held["id"])
        assert response.status_code == 200, response.text
    with Session(identity.engine) as db:
        assert not active(db, kind, record, identity.clock())
    with identity.engine.begin() as db, pytest.raises(DBAPIError, match="append-only"):
        db.execute(text(f"DELETE FROM {table} WHERE {column}=:id"), {"id": record})
    at = identity.clock()
    expiring = hold(
        client, headers, target, body | {"expires_at": (at + timedelta(seconds=1)).isoformat()}
    )
    assert expiring.status_code == 201, expiring.text
    identity.clock = lambda: at + timedelta(seconds=1)
    with Session(identity.engine) as db:
        assert not active(db, kind, record, identity.clock())
    review = preview(client, headers, target).json()
    assert review["active_legal_holds"] == 0
    assert review["execution_enabled"] is False
    assert "LEGAL_HOLD_COVERAGE_INCOMPLETE" in review["blockers"]
    bundle = export(client, actors["learner"], create(client, actors["learner"]).json()["id"])
    assert bundle.status_code == 200, bundle.text
    assert first["id"] not in bundle.text
    assert body["decision_reference"] not in bundle.text


@pytest.mark.parametrize("kind,table,column", KINDS)
def test_learning_hold_api_and_sql_reject_foreign_or_absent_target(assessment, kind, table, column):
    identity, client, actors, *_ = assessment
    record = record_for(assessment, kind)
    target, body = prepare(assessment)
    body |= {"record_type": kind, "record_id": str(record)}
    held = hold(client, actors["admin"], target, body)
    assert held.status_code == 201, held.text
    other = create(client, actors["other"], "DELETE").json()["id"]
    assert claim(client, actors["admin"], other).status_code == 200
    assert hold(client, actors["admin"], other, body).status_code == 404
    assert (
        hold(client, actors["admin"], target, body | {"record_id": str(uuid4())}).status_code == 404
    )
    with Session(identity.engine) as db:
        row = db.get(LegalHold, UUID(held.json()["id"]))
        values = {c.name: getattr(row, c.name) for c in LegalHold.__table__.columns}
    for changes in [{"request_id": UUID(other)}, {"record_id": uuid4()}]:
        with Session(identity.engine) as db, pytest.raises(DBAPIError, match="belong to requester"):
            db.add(LegalHold(**(values | changes | {"id": uuid4()})))
            db.commit()
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(LegalHold)) == 1
        assert db.scalar(select(func.count()).select_from(LegalHoldReceipt)) == 1
