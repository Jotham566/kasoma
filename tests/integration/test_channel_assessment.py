"""FR-WA-002/003/004: real shared transactions and immutable channel provenance."""

from copy import deepcopy
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.assessment import AssessmentService
from services.assessment_contracts import StartRevision, SubmitAnswer
from services.domain.assessment import Attempt, SessionItem
from services.domain.mastery import MasteryEstimate, MasteryEvidence
from services.identity import IdentityError
from tests.contract.test_numeric import spec
from tests.integration.test_assessment import prepare_assessment, start
from tests.integration.test_content import mutate
from tests.integration.test_identity import consent, profile

pytestmark = pytest.mark.integration


def ready(content, response_type="SINGLE_CHOICE", **changes):
    identity, client, actors, body = content
    document = body["document"] | {"channel_suitability": ["WEB", "WHATSAPP"], **changes}
    if response_type == "NUMERIC":
        document |= {
            "response_type": response_type,
            "choices": [],
            "correct_choice_id": "",
            "numeric_spec": spec().model_dump(mode="json"),
        }
    elif response_type == "MULTIPLE_CHOICE":
        document |= {
            "response_type": response_type,
            "correct_choice_id": "",
            "correct_choice_ids": ["A", "B"],
        }
    return prepare_assessment((identity, client, actors, body | {"document": document}))


def actor_id(client, headers):
    return UUID(client.get("/api/v1/me", headers=headers).json()["id"])


def evidence_value(snapshot):
    value = deepcopy(snapshot)
    value.pop("input_hash")
    value["source"].pop("attempt_id")
    return value


@pytest.mark.parametrize("response_type", ["SINGLE_CHOICE", "MULTIPLE_CHOICE", "NUMERIC"])
def test_five_answers_have_web_channel_grade_and_mastery_parity(content, response_type):
    identity, client, actors, _, _, plan = ready(content, response_type)
    service = AssessmentService(identity)
    profile(client, actors["other"], "2000-01-01")
    assert consent(client, actors["other"], "SELF").status_code == 200
    wa_actor = actor_id(client, actors["other"])
    web_actor = actor_id(client, actors["learner"])
    web = start(client, actors["learner"], plan).json()
    key = uuid4()
    with Session(identity.engine) as db, db.begin():
        wa = service.start_in_transaction(
            db, wa_actor, StartRevision.model_validate(plan), key, uuid4(), channel="WHATSAPP"
        )
        assert (
            service.start_in_transaction(
                db, wa_actor, StartRevision.model_validate(plan), key, uuid4(), channel="WHATSAPP"
            ).id
            == wa.id
        )
    # Neither public channel spoofing nor cross-channel receipt reuse is accepted.
    assert start(client, actors["other"], plan | {"channel": "WHATSAPP"}).status_code == 422
    assert start(client, actors["other"], plan, str(key)).status_code == 409
    for index in range(5):
        item = client.get(
            f"/api/v1/sessions/{web['id']}/next-item", headers=actors["learner"]
        ).json()
        response = {"type": "SINGLE_CHOICE", "choice_id": "A" if index % 2 == 0 else "B"}
        if response_type == "MULTIPLE_CHOICE":
            response = {
                "type": response_type,
                "choice_ids": ["A", "B"] if index % 2 == 0 else ["B"],
            }
        elif response_type == "NUMERIC":
            response = {
                "type": response_type,
                "value": "1.00" if index % 2 == 0 else "2",
                "unit": "m",
            }
        result = client.post(
            f"/api/v1/sessions/{web['id']}/attempts",
            headers=actors["learner"] | {"Idempotency-Key": str(uuid4())},
            json={"session_item_id": item["session_item_id"], "response": response},
        )
        assert result.status_code == 200, result.text
        with Session(identity.engine) as db, db.begin():
            channel_item = service.next_item_in_transaction(
                db, wa_actor, wa.id, uuid4(), channel="WHATSAPP"
            )
            assert str(channel_item.item_version_id) == item["item_version_id"]
            answer = SubmitAnswer.model_validate(
                {"session_item_id": channel_item.session_item_id, "response": response}
            )
            answer_key = uuid4()
            grade = service.submit_in_transaction(
                db, wa_actor, wa.id, answer, answer_key, uuid4(), channel="WHATSAPP"
            )
            replay = service.submit_in_transaction(
                db, wa_actor, wa.id, answer, answer_key, uuid4(), channel="WHATSAPP"
            )
            assert replay == grade
            expected = result.json()
            expected.pop("attempt_id")
            assert grade.model_dump(mode="json", exclude={"attempt_id"}) == expected
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(Attempt)) == 10
        for actor, channel in [(web_actor, "WEB"), (wa_actor, "WHATSAPP")]:
            assert set(db.scalars(select(Attempt.channel).where(Attempt.learner_id == actor))) == {
                channel
            }
        evidence = []
        estimates = []
        for actor in [web_actor, wa_actor]:
            rows = list(
                db.scalars(select(MasteryEvidence).where(MasteryEvidence.learner_id == actor))
            )
            evidence.append(
                sorted(
                    [evidence_value(r.snapshot) for r in rows],
                    key=lambda v: v["source"]["item_version_id"],
                )
            )
            value = deepcopy(
                db.scalar(
                    select(MasteryEstimate).where(MasteryEstimate.learner_id == actor)
                ).snapshot
            )
            value.pop("input_hash")
            value.pop("input_attempt_ids")
            estimates.append(value)
        assert evidence[0] == evidence[1]
        assert estimates[0] == estimates[1]


def test_unsupported_web_assignments_are_never_replaced_or_graded_for_channel(content):
    identity, client, actors, _, _, plan = ready(content, channel_suitability=["WEB"])
    service = AssessmentService(identity)
    actor = actor_id(client, actors["learner"])
    with (
        pytest.raises(IdentityError, match="INSUFFICIENT_CONTENT"),
        Session(identity.engine) as db,
        db.begin(),
    ):
        service.start_in_transaction(
            db, actor, StartRevision.model_validate(plan), uuid4(), uuid4(), channel="WHATSAPP"
        )
    web = start(client, actors["learner"], plan).json()
    with (
        pytest.raises(IdentityError, match="CONTENT_NOT_APPROVED"),
        Session(identity.engine) as db,
        db.begin(),
    ):
        service.start_in_transaction(
            db, actor, StartRevision.model_validate(plan), uuid4(), uuid4(), channel="WHATSAPP"
        )
    with (
        pytest.raises(IdentityError, match="CONTENT_NOT_APPROVED"),
        Session(identity.engine) as db,
        db.begin(),
    ):
        service.next_item_in_transaction(db, actor, UUID(web["id"]), uuid4(), channel="WHATSAPP")
    item = client.get(f"/api/v1/sessions/{web['id']}/next-item", headers=actors["learner"]).json()
    # The database rejects bypassing the application capability check.
    with (
        pytest.raises(DBAPIError, match="Unsupported channel assignment"),
        Session(identity.engine) as db,
        db.begin(),
    ):
        db.execute(
            text("""INSERT INTO attempts
          (id,learner_id,session_item_id,item_version_id,choice_id,submitted_at,hint_count,channel)
          VALUES (:id,:actor,:item,:version,'A',:at,0,'WHATSAPP')"""),
            {
                "id": uuid4(),
                "actor": actor,
                "item": UUID(item["session_item_id"]),
                "version": UUID(item["item_version_id"]),
                "at": identity.clock(),
            },
        )
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(Attempt)) == 0
        assert db.scalar(select(func.count()).select_from(SessionItem)) == 5


def test_channel_shape_and_current_approval_are_rechecked(content):
    identity, client, actors, _, versions, plan = ready(content)
    service = AssessmentService(identity)
    actor = actor_id(client, actors["learner"])
    for changes in [{"desired_item_count": 6}, {"mode": "RECOMMENDED", "topic_id": None}]:
        with (
            pytest.raises(IdentityError, match="VALIDATION_FAILED"),
            Session(identity.engine) as db,
            db.begin(),
        ):
            service.start_in_transaction(
                db,
                actor,
                StartRevision.model_validate(plan | changes),
                uuid4(),
                uuid4(),
                channel="WHATSAPP",
            )
    with Session(identity.engine) as db, db.begin():
        session = service.start_in_transaction(
            db, actor, StartRevision.model_validate(plan), uuid4(), uuid4(), channel="WHATSAPP"
        )
        item = service.next_item_in_transaction(db, actor, session.id, uuid4(), channel="WHATSAPP")
    version = next(v for v in versions if v["id"] == str(item.item_version_id))
    retired = mutate(
        client,
        f"item-versions/{version['id']}/retire",
        actors["admin"],
        {"expected_revision": version["revision"], "reason": "Synthetic channel withdrawal"},
    )
    assert retired.status_code == 200, retired.text
    from services.content import ContentError

    with pytest.raises(ContentError), Session(identity.engine) as db, db.begin():
        service.submit_in_transaction(
            db,
            actor,
            session.id,
            SubmitAnswer.model_validate(
                {"session_item_id": item.session_item_id, "response": {"choice_id": "A"}}
            ),
            uuid4(),
            uuid4(),
            channel="WHATSAPP",
        )
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(Attempt)) == 0


def test_web_plan_can_resume_on_channel_without_replacing_assignments(content):
    identity, client, actors, _, versions, plan = ready(content)
    service = AssessmentService(identity)
    actor = actor_id(client, actors["learner"])
    web = start(client, actors["learner"], plan).json()
    with Session(identity.engine) as db, db.begin():
        resumed = service.start_in_transaction(
            db, actor, StartRevision.model_validate(plan), uuid4(), uuid4(), channel="WHATSAPP"
        )
        assert str(resumed.id) == web["id"]
        item = service.next_item_in_transaction(db, actor, resumed.id, uuid4(), channel="WHATSAPP")
        answer = SubmitAnswer.model_validate(
            {"session_item_id": item.session_item_id, "response": {"choice_id": "A"}}
        )
        service.submit_in_transaction(
            db, actor, resumed.id, answer, uuid4(), uuid4(), channel="WHATSAPP"
        )
        assigned = set(
            db.scalars(
                select(SessionItem.item_version_id).where(SessionItem.session_id == resumed.id)
            )
        )
        assert assigned == {UUID(v["id"]) for v in versions}
    next_web = client.get(f"/api/v1/sessions/{web['id']}/next-item", headers=actors["learner"])
    assert next_web.status_code == 200 and next_web.json()["position"] == 2
    with pytest.raises(DBAPIError, match="append-only"), Session(identity.engine) as db, db.begin():
        db.execute(
            text("UPDATE attempts SET channel='WEB' WHERE learner_id=:actor"), {"actor": actor}
        )


def test_whatsapp_only_version_does_not_become_web_eligible_by_session_resume(content):
    identity, client, actors, _, _, plan = ready(content, channel_suitability=["WHATSAPP"])
    service = AssessmentService(identity)
    actor = actor_id(client, actors["learner"])
    with Session(identity.engine) as db, db.begin():
        session = service.start_in_transaction(
            db, actor, StartRevision.model_validate(plan), uuid4(), uuid4(), channel="WHATSAPP"
        )
        item = service.next_item_in_transaction(db, actor, session.id, uuid4(), channel="WHATSAPP")
    assert (
        client.get(
            f"/api/v1/sessions/{session.id}/next-item", headers=actors["learner"]
        ).status_code
        == 409
    )
    response = client.post(
        f"/api/v1/sessions/{session.id}/attempts",
        headers=actors["learner"] | {"Idempotency-Key": str(uuid4())},
        json={"session_item_id": str(item.session_item_id), "response": {"choice_id": "A"}},
    )
    assert response.status_code == 409
    with (
        pytest.raises(DBAPIError, match="Unsupported channel assignment"),
        Session(identity.engine) as db,
        db.begin(),
    ):
        db.execute(
            text("""INSERT INTO attempts
          (id,learner_id,session_item_id,item_version_id,choice_id,submitted_at,hint_count,channel)
          VALUES (:id,:actor,:item,:version,'A',:at,0,'WEB')"""),
            {
                "id": uuid4(),
                "actor": actor,
                "item": item.session_item_id,
                "version": item.item_version_id,
                "at": identity.clock(),
            },
        )
    with Session(identity.engine) as db, db.begin():
        assert db.scalar(select(func.count()).select_from(Attempt)) == 0
        grade = service.submit_in_transaction(
            db,
            actor,
            session.id,
            SubmitAnswer.model_validate(
                {"session_item_id": item.session_item_id, "response": {"choice_id": "A"}}
            ),
            uuid4(),
            uuid4(),
            channel="WHATSAPP",
        )
        assert grade.score == 1
