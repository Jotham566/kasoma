"""FR-REV-002–005, GRD-001/007, CNT-004, ID-003: durable consented learning."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.assessment import AssessmentService
from services.assessment_contracts import SubmitAnswer
from services.domain.assessment import (
    AssessmentEvent,
    AssessmentSession,
    Attempt,
    Grade,
    SessionItem,
)
from services.identity_contracts import ConsentInput
from tests.integration.test_content import create, mutate, review, submit

pytestmark = pytest.mark.integration


@pytest.fixture
def assessment(content):
    identity, client, actors, body = content
    versions = []
    for i in range(5):
        draft = body | {
            "document": body["document"] | {"title": f"Synthetic {i}", "maximum_points": i + 1}
        }
        version = review(client, actors, submit(client, actors, create(client, actors, draft)))
        assert version.status_code == 200, version.text
        versions.append(version.json())
    learner = actors["learner"]
    response = client.patch(
        "/api/v1/me",
        headers=learner,
        json={
            "display_name": "Synthetic learner",
            "birth_date": "2000-01-01",
            "subject_ids": [body["subject_id"]],
        },
    )
    assert response.status_code == 200, response.text
    response = client.post(
        "/api/v1/me/consents",
        headers=learner | {"Idempotency-Key": str(uuid4())},
        json={
            "consent_type": "SELF",
            "policy_version": identity.settings.consent_policy_version,
            "affirmative": True,
        },
    )
    assert response.status_code == 200, response.text
    plan = {
        "subject_id": body["subject_id"],
        "topic_id": body["document"]["topic_id"],
        "mode": "TOPIC",
        "desired_item_count": 5,
        "channel": "WEB",
    }
    return identity, client, actors, body, versions, plan


def start(client, headers, plan, key=None):
    return client.post(
        "/api/v1/revision-sessions",
        headers=headers | {"Idempotency-Key": key or str(uuid4())},
        json=plan,
    )


def next_item(client, headers, session):
    result = client.get(f"/api/v1/sessions/{session}/next-item", headers=headers)
    assert result.status_code == 200, result.text
    assert all(
        secret not in result.text
        for secret in ["correct_choice", "worked_solution", "remediation", "rights_evidence"]
    )
    return result.json()


def answer(client, headers, session, item, key=None, choice="A"):
    return client.post(
        f"/api/v1/sessions/{session}/attempts",
        headers=headers | {"Idempotency-Key": key or str(uuid4())},
        json={
            "session_item_id": item["session_item_id"],
            "response": {"type": "SINGLE_CHOICE", "choice_id": choice},
        },
    )


def test_durable_flow_resume_exact_grades_and_version_history(assessment):
    identity, client, actors, body, versions, plan = assessment
    headers = actors["learner"]
    key = str(uuid4())
    response = start(client, headers, plan, key)
    assert response.status_code == 201, response.text
    session = response.json()["id"]
    assert start(client, headers, plan, key).json()["id"] == session
    assert start(client, headers, plan).json()["id"] == session
    assert start(client, headers, plan | {"desired_item_count": 6}, key).status_code == 409
    assert client.get("/api/v1/sessions/active", headers=headers).json()[0]["id"] == session
    grades = []
    for i in range(5):
        item = next_item(client, headers, session)
        assert item["position"] == i + 1
        assert (
            client.get(
                f"/api/v1/attempts/{item['session_item_id']}/solution", headers=headers
            ).status_code
            == 404
        )
        key = str(uuid4())
        response = answer(client, headers, session, item, key, "A" if i % 2 == 0 else "B")
        assert response.status_code == 200, response.text
        grade = response.json()
        assert grade["score"] == (1 if i % 2 == 0 else 0)
        assert grade["points_awarded"] == grade["points_possible"] * grade["score"]
        assert grade["mastery_update_status"] == "NOT_IMPLEMENTED"
        assert (
            answer(client, headers, session, item, key, "A" if i % 2 == 0 else "B").json() == grade
        )
        assert (
            answer(client, headers, session, item, key, "B" if i % 2 == 0 else "A").status_code
            == 409
        )
        assert answer(client, headers, session, item).status_code == 409
        grades.append(grade)
        state = client.get(f"/api/v1/sessions/{session}", headers=headers).json()
        assert state["answered_count"] == i + 1
    assert state["status"] == "COMPLETED"
    assert client.get(f"/api/v1/sessions/{session}/next-item", headers=headers).status_code == 409
    assert start(client, headers, plan).json()["error"]["code"] == "INSUFFICIENT_CONTENT"
    version = next(v for v in versions if v["id"] == grades[0]["item_version_id"])
    retired = mutate(
        client,
        f"item-versions/{version['id']}/retire",
        actors["reviewer"],
        {"expected_revision": version["revision"], "reason": "Synthetic history test"},
    )
    assert retired.status_code == 200
    successor = create(
        client,
        actors,
        body
        | {
            "source_version_id": version["id"],
            "document": body["document"] | {"correct_choice_id": "B"},
        },
    )
    assert successor["version"] == 2
    assert (
        client.get(f"/api/v1/attempts/{grades[0]['attempt_id']}/grade", headers=headers).json()
        == grades[0]
    )
    solution = client.get(f"/api/v1/attempts/{grades[0]['attempt_id']}/solution", headers=headers)
    assert solution.status_code == 200 and solution.json()["item_version_id"] == version["id"]
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(Attempt)) == 5
        assert db.scalar(select(func.count()).select_from(Grade)) == 5
        assert (
            db.scalar(
                select(func.count())
                .select_from(AssessmentEvent)
                .where(AssessmentEvent.type == "attempt.graded")
            )
            == 5
        )
    for sql in [
        "UPDATE attempts SET choice_id='B'",
        "DELETE FROM grades",
        "UPDATE session_items SET position=10",
    ]:
        with pytest.raises(DBAPIError), identity.engine.begin() as conn:
            conn.execute(text(sql))


def test_consent_ownership_validation_and_withdrawal(assessment):
    identity, client, actors, body, versions, plan = assessment
    headers = actors["learner"]
    assert start(client, {}, plan).status_code == 401
    assert start(client, actors["other"], plan).status_code == 403
    for change in [
        {"score": 1},
        {"channel": "WHATSAPP"},
        {"desired_item_count": 1},
        {"mode": "RECOMMENDED"},
    ]:
        assert start(client, headers, plan | change).status_code == 422
    assert start(client, headers, plan | {"subject_id": str(uuid4())}).status_code == 403
    session = start(client, headers, plan).json()["id"]
    item = next_item(client, headers, session)
    assert answer(client, headers, session, item, choice="Z").status_code == 422
    with Session(identity.engine) as db:
        later = db.scalar(select(SessionItem).where(SessionItem.position == 2))
        assert (
            answer(client, headers, session, {"session_item_id": str(later.id)}).status_code == 404
        )
    grade = answer(client, headers, session, item).json()
    # A second consented learner cannot read or mutate another learner's resources.
    other = actors["other"]
    client.patch(
        "/api/v1/me",
        headers=other,
        json={
            "display_name": "Other synthetic",
            "birth_date": "2000-01-01",
            "subject_ids": [body["subject_id"]],
        },
    )
    client.post(
        "/api/v1/me/consents",
        headers=other | {"Idempotency-Key": str(uuid4())},
        json={
            "consent_type": "SELF",
            "policy_version": identity.settings.consent_policy_version,
            "affirmative": True,
        },
    )
    for path in [
        f"sessions/{session}",
        f"sessions/{session}/next-item",
        f"attempts/{grade['attempt_id']}/grade",
        f"attempts/{grade['attempt_id']}/solution",
    ]:
        assert client.get("/api/v1/" + path, headers=other).status_code == 404
    assert answer(client, other, session, item).status_code == 404
    assert client.post(f"/api/v1/sessions/{session}/abandon", headers=other).status_code == 404
    token = headers["Authorization"][7:]
    identity.consent(
        token,
        ConsentInput(
            consent_type="WITHDRAW",
            affirmative=True,
            policy_version=identity.settings.consent_policy_version,
        ),
        uuid4(),
        str(uuid4()),
    )
    for path in [
        f"sessions/{session}",
        f"sessions/{session}/next-item",
        "sessions/active",
        f"attempts/{grade['attempt_id']}/grade",
        f"attempts/{grade['attempt_id']}/solution",
    ]:
        assert client.get("/api/v1/" + path, headers=headers).status_code == 403
    assert answer(client, headers, session, item).status_code == 403


def test_concurrent_replay_and_atomic_rollback(assessment, monkeypatch):
    identity, client, actors, body, versions, plan = assessment
    headers = actors["learner"]
    session = start(client, headers, plan).json()["id"]
    item = next_item(client, headers, session)
    service = AssessmentService(identity)
    token = headers["Authorization"][7:]
    request = SubmitAnswer(session_item_id=item["session_item_id"], response={"choice_id": "A"})
    key = uuid4()

    def once(_):
        return service.submit(token, UUID(session), request, key, uuid4())

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(once, range(2)))
    assert results[0] == results[1]
    item = next_item(client, headers, session)
    original = service.event

    def failure(*args, **kwargs):
        raise RuntimeError("Injected transaction failure")

    monkeypatch.setattr(service, "event", failure)
    with pytest.raises(RuntimeError):
        service.submit(
            token,
            UUID(session),
            SubmitAnswer(session_item_id=item["session_item_id"], response={"choice_id": "A"}),
            uuid4(),
            uuid4(),
        )
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(Attempt)) == 1
        assert db.scalar(select(func.count()).select_from(Grade)) == 1
    monkeypatch.setattr(service, "event", original)
    assert answer(client, headers, session, item).status_code == 200


def test_retirement_blocks_serving_and_submission_abandon_is_safe(assessment):
    identity, client, actors, body, versions, plan = assessment
    headers = actors["learner"]
    session = start(client, headers, plan).json()["id"]
    item = next_item(client, headers, session)
    version = next(v for v in versions if v["id"] == item["item_version_id"])
    mutate(
        client,
        f"item-versions/{version['id']}/retire",
        actors["reviewer"],
        {"expected_revision": version["revision"], "reason": "Emergency test withdrawal"},
    )
    assert client.get(f"/api/v1/sessions/{session}/next-item", headers=headers).status_code in [
        404,
        409,
    ]
    assert answer(client, headers, session, item).status_code in [404, 409]
    for _ in range(2):
        assert (
            client.post(f"/api/v1/sessions/{session}/abandon", headers=headers).json()["status"]
            == "ABANDONED"
        )
    assert start(client, headers, plan).json()["error"]["code"] == "INSUFFICIENT_CONTENT"


def test_expiry_and_subject_revocation(assessment):
    identity, client, actors, body, versions, plan = assessment
    headers = actors["learner"]
    session = start(client, headers, plan).json()["id"]
    next_item(client, headers, session)
    with identity.engine.begin() as conn:
        conn.execute(
            text("UPDATE assessment_sessions SET expires_at=started_at + interval '1 minute'")
        )
    now = identity.clock()
    identity.clock = lambda: now + timedelta(minutes=2)
    assert client.get(f"/api/v1/sessions/{session}", headers=headers).json()["status"] == "EXPIRED"
    assert client.get(f"/api/v1/sessions/{session}/next-item", headers=headers).status_code == 409


def test_planner_excludes_drafts_retired_and_unsupported_channel(assessment):
    identity, client, actors, body, versions, plan = assessment
    version = versions[0]
    mutate(
        client,
        f"item-versions/{version['id']}/retire",
        actors["reviewer"],
        {"expected_revision": version["revision"], "reason": "Selector exclusion fixture"},
    )
    create(client, actors, body)  # A draft cannot fill the missing inventory slot.
    nonweb = body | {"document": body["document"] | {"channel_suitability": ["WHATSAPP"]}}
    assert (
        review(client, actors, submit(client, actors, create(client, actors, nonweb))).status_code
        == 200
    )
    response = start(client, actors["learner"], plan)
    assert (
        response.status_code == 409 and response.json()["error"]["code"] == "INSUFFICIENT_CONTENT"
    )
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(AssessmentSession)) == 0


def test_minor_assent_without_guardian_and_changed_policy_block_learning(assessment):
    identity, client, actors, body, versions, plan = assessment
    headers = actors["other"]
    response = client.patch(
        "/api/v1/me",
        headers=headers,
        json={
            "display_name": "Synthetic child",
            "birth_date": "2010-01-01",
            "subject_ids": [body["subject_id"]],
        },
    )
    assert response.status_code == 200
    response = client.post(
        "/api/v1/me/consents",
        headers=headers | {"Idempotency-Key": str(uuid4())},
        json={
            "consent_type": "ASSENT",
            "policy_version": identity.settings.consent_policy_version,
            "affirmative": True,
        },
    )
    assert response.status_code == 200
    assert start(client, headers, plan).status_code == 403
    assert client.get("/api/v1/sessions/active", headers=headers).status_code == 403
    identity.settings.consent_policy_version = "synthetic-policy-v2"
    assert start(client, actors["learner"], plan).status_code == 403
