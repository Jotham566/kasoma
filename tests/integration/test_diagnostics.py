"""FR-DIAG-001–005 and FR-MST-001–003/005: synthetic durable diagnostics."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from scripts.assessment_fixtures import seed_assessment
from scripts.replay_mastery import verify
from services.assessment import AssessmentService
from services.assessment_contracts import StartDiagnostic
from services.domain.assessment import AssessmentSession, Attempt, Grade, SessionItem
from services.domain.content import ItemVersion
from services.domain.mastery import MasteryEstimate, MasteryEvidence, MasteryHistory
from services.mastery import project_skill

pytestmark = pytest.mark.integration


@pytest.fixture
def diagnostic(content, request):
    identity, client, actors, body = content
    seed_assessment(identity, diagnostic=True)
    context = client.get("/api/v1/admin/content-context", headers=actors["author"]).json()
    selected = getattr(request, "param", "Mathematics")
    body = body | {
        "subject_id": next(s["id"] for s in context["subjects"] if s["name"] == selected)
    }
    headers = actors["learner"]
    assert (
        client.patch(
            "/api/v1/me",
            headers=headers,
            json={
                "display_name": "Synthetic diagnostic learner",
                "birth_date": "2000-01-01",
                "subject_ids": [body["subject_id"]],
            },
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/api/v1/me/consents",
            headers=headers | {"Idempotency-Key": str(uuid4())},
            json={
                "consent_type": "SELF",
                "policy_version": identity.settings.consent_policy_version,
                "affirmative": True,
            },
        ).status_code
        == 200
    )
    return identity, client, actors, body


def start(client, headers, subject, key=None):
    return client.post(
        "/api/v1/diagnostics",
        headers=headers | {"Idempotency-Key": key or str(uuid4())},
        json={"subject_id": subject},
    )


def next_item(client, headers, session):
    response = client.get(f"/api/v1/sessions/{session}/next-item", headers=headers)
    assert response.status_code == 200, response.text
    for hidden in [
        "expected_value",
        "correct_choice",
        "worked_solution",
        "remediation",
        "absolute_tolerance",
    ]:
        assert hidden not in response.text
    return response.json()


def submit(client, headers, session, item, key=None, correct=True):
    response = {"type": "SINGLE_CHOICE", "choice_id": "A" if correct else "B"}
    if item["response_spec"]["type"] == "NUMERIC":
        response = {"type": "NUMERIC", "value": "1.00" if correct else "2.00", "unit": "m"}
    return client.post(
        f"/api/v1/sessions/{session}/attempts",
        headers=headers | {"Idempotency-Key": key or str(uuid4())},
        json={"session_item_id": item["session_item_id"], "response": response},
    )


@pytest.mark.parametrize("diagnostic", ["Mathematics", "Physics"], indirect=True)
@pytest.mark.parametrize("correct", [True, False])
def test_diagnostic_complete_coverage_hidden_grades_resume_and_replay(diagnostic, correct):
    identity, client, actors, body = diagnostic
    headers = actors["learner"]
    started = start(client, headers, body["subject_id"])
    assert started.status_code == 201, started.text
    session = started.json()["id"]
    assert started.json()["result"] is None
    assert start(client, headers, body["subject_id"]).json()["id"] == session
    seen = []
    for index in range(15):
        item = next_item(client, headers, session)
        assert next_item(client, headers, session) == item
        seen.append(UUID(item["item_version_id"]))
        key = str(uuid4())
        response = submit(client, headers, session, item, key, correct)
        assert response.status_code == 200, response.text
        saved = response.json()
        assert saved["status"] == "SAVED"
        assert not {"score", "feedback", "points_awarded"} & saved.keys()
        assert submit(client, headers, session, item, key, correct).json() == saved
        assert submit(client, headers, session, item).status_code == 409
        assert (
            client.get(
                f"/api/v1/attempts/{saved['attempt_id']}/solution", headers=headers
            ).status_code
            == 403
        )
        grade = client.get(f"/api/v1/attempts/{saved['attempt_id']}/grade", headers=headers)
        assert grade.status_code == (200 if index == 14 else 403)
        state = client.get(f"/api/v1/diagnostics/{session}", headers=headers).json()
        assert state["answered_count"] == index + 1
        assert state["result"] is None if index < 14 else state["result"] is not None
        assert client.get(f"/api/v1/sessions/{session}", headers=headers).json() == state
    assert state["status"] == "COMPLETED"
    assert len({s["topic_id"] for s in state["result"]["skills"]}) == 3
    assert len({s["competency_id"] for s in state["result"]["skills"]}) >= 2
    assert state["result"]["recommendation"]["learner_text"]
    assert state["result"]["recommendation"]["topic_id"]
    assert all(0 <= s["confidence"] <= 1 for s in state["result"]["skills"])
    assert client.get(f"/api/v1/sessions/{session}/next-item", headers=headers).status_code == 409
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(Attempt)) == 15
        assert db.scalar(select(func.count()).select_from(MasteryEvidence)) == 15
        assert db.scalar(select(func.count()).select_from(MasteryHistory)) == 15
        docs = [db.get(ItemVersion, v).document for v in seen[:3]]
        assert len({d["topic_id"] for d in docs}) == 3
        assert all(d["difficulty"] == "STANDARD" for d in docs)
        later = [db.get(ItemVersion, version).document["difficulty"] for version in seen[3:]]
        assert ("CHALLENGING" if correct else "FOUNDATIONAL") in later
        assert verify(db) >= 15
        for current in db.scalars(select(MasteryEstimate)):
            replay = project_skill(
                db, current.learner_id, current.concept_id, current.competency_id, identity.clock()
            )
            assert replay.model_dump(mode="json") == current.snapshot
    for statement in [
        "UPDATE mastery_evidence SET snapshot=snapshot",
        "DELETE FROM mastery_estimate_history",
        "UPDATE assessment_sessions SET diagnostic_result='{}' WHERE kind='DIAGNOSTIC'",
    ]:
        with pytest.raises(DBAPIError), identity.engine.begin() as connection:
            connection.execute(text(statement))
    assert client.get(f"/api/v1/diagnostics/{session}", headers=headers).json() == state


def test_concurrent_start_authorization_and_withdrawal(diagnostic):
    identity, client, actors, body = diagnostic
    token = actors["learner"]["Authorization"].removeprefix("Bearer ")
    service = AssessmentService(identity)
    request = StartDiagnostic(subject_id=UUID(body["subject_id"]))
    with ThreadPoolExecutor(max_workers=2) as pool:
        plans = list(
            pool.map(
                lambda _: service.diagnostics.start(token, request, uuid4(), uuid4()), range(2)
            )
        )
    assert plans[0].id == plans[1].id
    session = str(plans[0].id)
    for path in [f"diagnostics/{session}", f"sessions/{session}/next-item"]:
        assert client.get("/api/v1/" + path).status_code == 401
        assert client.get("/api/v1/" + path, headers=actors["other"]).status_code in {403, 404}
    assert start(client, actors["learner"], str(uuid4())).status_code == 403
    withdrawal = client.post(
        "/api/v1/me/consents",
        headers=actors["learner"] | {"Idempotency-Key": str(uuid4())},
        json={
            "consent_type": "WITHDRAW",
            "policy_version": identity.settings.consent_policy_version,
            "affirmative": True,
        },
    )
    assert withdrawal.status_code == 200
    assert (
        client.get(f"/api/v1/diagnostics/{session}", headers=actors["learner"]).status_code == 403
    )
    assert start(client, actors["learner"], body["subject_id"]).status_code == 403


def test_failed_mastery_write_rolls_back_answer_grade_and_ack(diagnostic, monkeypatch):
    identity, client, actors, body = diagnostic
    headers = actors["learner"]
    session = start(client, headers, body["subject_id"]).json()["id"]
    item = next_item(client, headers, session)
    key = str(uuid4())
    import services.mastery as mastery

    original = mastery.record

    def fail(*args):
        original(*args)
        raise RuntimeError("Synthetic transactional failure")

    monkeypatch.setattr(mastery, "record", fail)
    assert submit(client, headers, session, item, key).status_code == 500
    with Session(identity.engine) as db:
        for model in [Attempt, Grade, MasteryEvidence, MasteryHistory]:
            assert db.scalar(select(func.count()).select_from(model)) == 0
    monkeypatch.setattr(mastery, "record", original)
    assert submit(client, headers, session, item, key).status_code == 200


def test_incomplete_inventory_fails_without_shortening(content):
    identity, client, actors, body = content
    headers = actors["learner"]
    client.patch(
        "/api/v1/me",
        headers=headers,
        json={
            "display_name": "Synthetic",
            "birth_date": "2000-01-01",
            "subject_ids": [body["subject_id"]],
        },
    )
    client.post(
        "/api/v1/me/consents",
        headers=headers | {"Idempotency-Key": str(uuid4())},
        json={
            "consent_type": "SELF",
            "policy_version": identity.settings.consent_policy_version,
            "affirmative": True,
        },
    )
    response = start(client, headers, body["subject_id"])
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INSUFFICIENT_CONTENT"
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(AssessmentSession)) == 0


def test_expired_diagnostic_resumes_safely_as_a_new_plan(diagnostic):
    identity, client, actors, body = diagnostic
    headers = actors["learner"]
    session = start(client, headers, body["subject_id"]).json()["id"]
    next_item(client, headers, session)
    with identity.engine.begin() as connection:
        connection.execute(
            text("UPDATE assessment_sessions SET expires_at=started_at + interval '1 minute'")
        )
    now = identity.clock()
    identity.clock = lambda: now + timedelta(minutes=2)
    expired = client.get(f"/api/v1/diagnostics/{session}", headers=headers)
    assert expired.json()["status"] == "EXPIRED"
    assert client.get(f"/api/v1/sessions/{session}/next-item", headers=headers).status_code == 409
    replacement = start(client, headers, body["subject_id"])
    assert replacement.status_code == 201, replacement.text
    assert replacement.json()["id"] != session
    assert replacement.json()["answered_count"] == 0


def test_retired_item_blocks_delivery_and_unknown_client_state_is_rejected(diagnostic):
    identity, client, actors, body = diagnostic
    headers = actors["learner"]
    bad = client.post(
        "/api/v1/diagnostics",
        headers=headers | {"Idempotency-Key": str(uuid4())},
        json={"subject_id": body["subject_id"], "desired_item_count": 16, "score": 1},
    )
    assert bad.status_code == 422
    session = start(client, headers, body["subject_id"]).json()["id"]
    item = next_item(client, headers, session)
    with Session(identity.engine) as db:
        version = db.get(ItemVersion, UUID(item["item_version_id"]))
        revision = version.revision
    retired = client.post(
        f"/api/v1/admin/item-versions/{item['item_version_id']}/retire",
        headers=actors["reviewer"] | {"Idempotency-Key": str(uuid4())},
        json={"expected_revision": revision, "reason": "Synthetic emergency withdrawal"},
    )
    assert retired.status_code == 200, retired.text
    assert client.get(f"/api/v1/sessions/{session}/next-item", headers=headers).status_code in {
        404,
        409,
    }
    assert submit(client, headers, session, item).status_code in {404, 409}
    assert (
        client.post(f"/api/v1/sessions/{session}/abandon", headers=headers).json()["status"]
        == "ABANDONED"
    )
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(Attempt)) == 0


def test_legacy_grade_reconciliation_preserves_original_and_requires_consent(diagnostic):
    from services.content_contracts import DraftDocument
    from services.grading import grade_choice

    identity, client, actors, body = diagnostic
    headers = actors["learner"]
    plan = client.post(
        "/api/v1/revision-sessions",
        headers=headers | {"Idempotency-Key": str(uuid4())},
        json={
            "subject_id": body["subject_id"],
            "topic_id": body["document"]["topic_id"],
            "desired_item_count": 5,
        },
    )
    assert plan.status_code == 201, plan.text
    item = next_item(client, headers, plan.json()["id"])
    # Reproduce a valid pre-E5 writer: immutable attempt+grade without mastery rows.
    attempt_id = uuid4()
    with Session(identity.engine) as db, db.begin():
        session = db.get(AssessmentSession, UUID(plan.json()["id"]))
        version = db.get(ItemVersion, UUID(item["item_version_id"]))
        legacy = grade_choice(
            attempt_id, version.id, DraftDocument.model_validate(version.document), "A"
        )
        assert legacy.mastery_update_status == "NOT_IMPLEMENTED"
        db.add(
            Attempt(
                id=attempt_id,
                learner_id=session.learner_id,
                session_item_id=UUID(item["session_item_id"]),
                item_version_id=version.id,
                choice_id="A",
                response=None,
                submitted_at=identity.clock(),
                hint_count=0,
                channel="WEB",
            )
        )
        db.flush()
        db.add(
            Grade(
                attempt_id=attempt_id,
                item_version_id=version.id,
                answer_specification_hash=version.content_hash,
                result=legacy.model_dump(mode="json"),
            )
        )

    def consent(kind):
        response = client.post(
            "/api/v1/me/consents",
            headers=headers | {"Idempotency-Key": str(uuid4())},
            json={
                "consent_type": kind,
                "policy_version": identity.settings.consent_policy_version,
                "affirmative": True,
            },
        )
        assert response.status_code == 200, response.text

    with Session(identity.engine) as db:
        existing_session = db.get(AssessmentSession, UUID(plan.json()["id"]))
        reserved = set(
            db.scalars(
                select(SessionItem.item_version_id).where(
                    SessionItem.session_id == existing_session.id
                )
            )
        )
        eligible = AssessmentService(identity).diagnostics.candidates(
            db, existing_session.learner_id, existing_session.subject_id
        )
        assert not reserved.intersection(v.id for v in eligible)
    assert (
        client.post(f"/api/v1/sessions/{plan.json()['id']}/abandon", headers=headers).status_code
        == 200
    )
    consent("WITHDRAW")
    assert start(client, headers, body["subject_id"]).status_code == 403
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(MasteryEvidence)) == 0
    consent("SELF")
    assert start(client, headers, body["subject_id"]).status_code == 201
    assert start(client, headers, body["subject_id"]).status_code == 201
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(MasteryEvidence)) == 1
        assert db.scalar(select(func.count()).select_from(MasteryHistory)) == 1
        assert db.get(Grade, attempt_id).result == legacy.model_dump(mode="json")
        assert verify(db) == 2
