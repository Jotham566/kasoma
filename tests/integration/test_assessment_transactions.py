"""FR-WA-003/004 foundation: reuse one grading transaction without impersonating a bearer."""

from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from services.assessment import AssessmentService
from services.assessment_contracts import ChoiceResponse, StartRevision, SubmitAnswer
from services.domain.assessment import (
    AssessmentEvent,
    AssessmentReceipt,
    AssessmentSession,
    Attempt,
    Grade,
    SessionItem,
)
from services.domain.identity import User
from services.domain.mastery import MasteryEstimate, MasteryEvidence, MasteryHistory
from services.identity import IdentityError
from tests.integration.test_assessment import assessment as assessment_fixture
from tests.integration.test_assessment import start
from tests.integration.test_identity import consent, profile

assessment = assessment_fixture
pytestmark = pytest.mark.integration


def test_shared_transaction_rollback_and_committed_web_retry(assessment):
    identity, client, actors, _, _, plan = assessment
    service = AssessmentService(identity)
    actor = UUID(client.get("/api/v1/me", headers=actors["learner"]).json()["id"])
    body = StartRevision.model_validate(plan)
    start_key, answer_key, request = uuid4(), uuid4(), uuid4()
    with pytest.raises(RuntimeError, match="synthetic delivery failure"):
        with Session(identity.engine) as db, db.begin():
            session = service.start_in_transaction(db, actor, body, start_key, request)
            item = service.next_item_in_transaction(db, actor, session.id, request)
            answer = SubmitAnswer(
                session_item_id=item.session_item_id, response=ChoiceResponse(choice_id="A")
            )
            grade = service.submit_in_transaction(
                db, actor, session.id, answer, answer_key, request
            )
            assert grade.score == 1
            db.flush()
            assert db.scalar(select(func.count()).select_from(MasteryEvidence)) > 0
            raise RuntimeError("synthetic delivery failure")
    with Session(identity.engine) as db:
        for model in [
            AssessmentSession,
            SessionItem,
            Attempt,
            Grade,
            AssessmentReceipt,
            AssessmentEvent,
            MasteryEstimate,
            MasteryEvidence,
            MasteryHistory,
        ]:
            assert db.scalar(select(func.count()).select_from(model)) == 0
    with Session(identity.engine) as db, db.begin():
        session = service.start_in_transaction(db, actor, body, start_key, request)
        item = service.next_item_in_transaction(db, actor, session.id, request)
        answer = SubmitAnswer(
            session_item_id=item.session_item_id, response=ChoiceResponse(choice_id="A")
        )
        grade = service.submit_in_transaction(db, actor, session.id, answer, answer_key, request)
    # Existing web fingerprints and receipts remain valid across the internal boundary.
    assert start(client, actors["learner"], plan, str(start_key)).json()["id"] == str(session.id)
    replay = client.post(
        f"/api/v1/sessions/{session.id}/attempts",
        headers=actors["learner"] | {"Idempotency-Key": str(answer_key)},
        json=answer.model_dump(mode="json"),
    )
    assert replay.status_code == 200 and replay.json() == grade.model_dump(mode="json")
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(Attempt)) == 1
        assert db.scalar(select(func.count()).select_from(Grade)) == 1


def test_internal_actor_methods_recheck_consent_account_and_enrollment(assessment):
    identity, client, actors, _, _, plan = assessment
    service = AssessmentService(identity)
    actor = UUID(client.get("/api/v1/me", headers=actors["learner"]).json()["id"])
    body = StartRevision.model_validate(plan)
    with (
        pytest.raises(IdentityError, match="AUTH_REQUIRED"),
        Session(identity.engine) as db,
        db.begin(),
    ):
        service.start_in_transaction(db, uuid4(), body, uuid4(), uuid4())
    with (
        pytest.raises(IdentityError, match="FORBIDDEN"),
        Session(identity.engine) as db,
        db.begin(),
    ):
        service.start_in_transaction(
            db, actor, body.model_copy(update={"subject_id": uuid4()}), uuid4(), uuid4()
        )
    assert consent(client, actors["learner"], "WITHDRAW").status_code == 200
    with (
        pytest.raises(IdentityError, match="CONSENT_REQUIRED"),
        Session(identity.engine) as db,
        db.begin(),
    ):
        service.start_in_transaction(db, actor, body, uuid4(), uuid4())
    assert consent(client, actors["learner"], "SELF").status_code == 200
    with Session(identity.engine) as db:
        stale = db.get(User, actor)
        with Session(identity.engine) as writer, writer.begin():
            row = writer.get(User, actor)
            row.status = "DISABLED"
        assert stale.status == "ACTIVE"
        with pytest.raises(IdentityError, match="AUTH_REQUIRED"):
            service.authorize_actor(db, actor)


def test_internal_submission_cannot_cross_learner_ownership(assessment):
    identity, client, actors, _, _, plan = assessment
    service = AssessmentService(identity)
    actor = UUID(client.get("/api/v1/me", headers=actors["learner"]).json()["id"])
    body = StartRevision.model_validate(plan)
    with Session(identity.engine) as db, db.begin():
        session = service.start_in_transaction(db, actor, body, uuid4(), uuid4())
        item = service.next_item_in_transaction(db, actor, session.id, uuid4())
    # A staff account has no learning consent and gains no bypass through this boundary.
    staff = UUID(client.get("/api/v1/me", headers=actors["admin"]).json()["id"])
    with (
        pytest.raises(IdentityError, match="CONSENT_REQUIRED"),
        Session(identity.engine) as db,
        db.begin(),
    ):
        service.submit_in_transaction(
            db,
            staff,
            session.id,
            SubmitAnswer(
                session_item_id=item.session_item_id, response=ChoiceResponse(choice_id="A")
            ),
            uuid4(),
            uuid4(),
        )
    profile(client, actors["admin"], "2000-01-01")
    assert consent(client, actors["admin"], "SELF").status_code == 200
    with (
        pytest.raises(IdentityError, match="RESOURCE_NOT_FOUND"),
        Session(identity.engine) as db,
        db.begin(),
    ):
        service.submit_in_transaction(
            db,
            staff,
            session.id,
            SubmitAnswer(
                session_item_id=item.session_item_id, response=ChoiceResponse(choice_id="A")
            ),
            uuid4(),
            uuid4(),
        )
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(Attempt)) == 0
