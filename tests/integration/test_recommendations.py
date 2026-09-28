"""FR-REV-001/006, FR-MST-006: durable recommended plans and safe previews."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.assessment import AssessmentService
from services.assessment_contracts import StartRevision
from services.domain.assessment import AssessmentSession, RecommendationSnapshot, SessionItem
from services.recommendation_engine import RankedPlan, replay
from tests.integration.test_assessment import answer, next_item, start
from tests.integration.test_diagnostics import diagnostic as diagnostic_fixture

diagnostic = diagnostic_fixture

pytestmark = pytest.mark.integration


def request_plan(body, count=5):
    return {
        "subject_id": body["subject_id"],
        "mode": "RECOMMENDED",
        "topic_id": None,
        "desired_item_count": count,
        "channel": "WEB",
    }


@pytest.mark.parametrize("count", [5, 10])
def test_recommended_preview_plan_resume_replay_and_mastery(diagnostic, count):
    identity, client, actors, body = diagnostic
    if count == 10:
        from scripts.assessment_fixtures import seed_assessment

        seed_assessment(identity, mathematics_only=True)
    headers = actors["learner"]
    preview = client.get(
        "/api/v1/me/recommendations/next",
        headers=headers,
        params={"subject_id": body["subject_id"]},
    )
    assert preview.status_code == 200, preview.text
    assert preview.json()["diagnostic_suggested"]
    assert preview.json()["reason_code"] == "GATHER_MORE_EVIDENCE"
    for secret in [
        "correct_choice",
        "worked_solution",
        "scores",
        "candidates",
        "input_attempt_ids",
    ]:
        assert secret not in preview.text
    duplicate = client.get(
        "/api/v1/me/recommendations/next",
        headers=headers,
        params={"subject_id": body["subject_id"]},
    )
    assert duplicate.json() == preview.json()
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(RecommendationSnapshot)) == 1
    key = str(uuid4())
    result = start(client, headers, request_plan(body, count), key)
    assert result.status_code == 201, result.text
    session = result.json()["id"]
    assert result.json()["plan_version"] == "recommendation-v1"
    assert result.json()["recommendation_reason"]
    assert start(client, headers, request_plan(body, count), key).json()["id"] == session
    assert start(client, headers, request_plan(body, count)).json()["id"] == session
    with Session(identity.engine) as db:
        row = db.get(AssessmentSession, UUID(session))
        frozen = RankedPlan.model_validate(row.recommendation_snapshot)
        replay(frozen)
        items = list(
            db.scalars(
                select(SessionItem)
                .where(SessionItem.session_id == UUID(session))
                .order_by(SessionItem.position)
            )
        )
        assert tuple(i.item_version_id for i in items) == frozen.item_version_ids
        assert all(i.reason for i in items)
    for _ in range(count):
        item = next_item(client, headers, session)
        result = answer(client, headers, session, item)
        assert result.status_code == 200, result.text
        assert result.json()["mastery_update_status"] == "COMPLETED"
    assert (
        client.get(f"/api/v1/sessions/{session}", headers=headers).json()["status"] == "COMPLETED"
    )
    with Session(identity.engine) as db:
        assert db.get(
            AssessmentSession, UUID(session)
        ).recommendation_snapshot == frozen.model_dump(mode="json")
        with pytest.raises(DBAPIError), db.begin_nested():
            db.execute(
                text("UPDATE assessment_sessions SET recommendation_snapshot=NULL WHERE id=:id"),
                {"id": session},
            )
        with pytest.raises(DBAPIError), db.begin_nested():
            db.execute(text("UPDATE recommendation_snapshots SET snapshot='{}'"))


def test_concurrent_starts_and_unserved_reservations(diagnostic):
    identity, client, actors, body = diagnostic
    headers = actors["learner"]
    service = AssessmentService(identity)
    payload = StartRevision.model_validate(request_plan(body))
    token = headers["Authorization"].split()[1]
    with ThreadPoolExecutor(max_workers=2) as workers:
        sessions = list(
            workers.map(lambda _: service.start(token, payload, uuid4(), uuid4()).id, range(2))
        )
    assert sessions[0] == sessions[1]
    # Diagnostic inventory must exclude every reserved item, not just served ones.
    with Session(identity.engine) as db:
        row = db.get(AssessmentSession, sessions[0])
        reserved = set(
            db.scalars(select(SessionItem.item_version_id).where(SessionItem.session_id == row.id))
        )
        available = {
            v.id for v in service.diagnostics.candidates(db, row.learner_id, row.subject_id)
        }
        assert reserved.isdisjoint(available)
    # A topic request for the same target resumes, rather than allocating overlapping content.
    response = start(
        client, headers, request_plan(body) | {"mode": "TOPIC", "topic_id": str(row.topic_id)}
    )
    assert response.json()["id"] == str(sessions[0])


def test_authorization_validation_inventory_and_withdrawal(diagnostic):
    identity, client, actors, body = diagnostic
    params = {"subject_id": body["subject_id"]}
    assert client.get("/api/v1/me/recommendations/next", params=params).status_code == 401
    assert (
        client.get(
            "/api/v1/me/recommendations/next", headers=actors["other"], params=params
        ).status_code
        == 403
    )
    headers = actors["learner"]
    assert (
        client.get(
            "/api/v1/me/recommendations/next", headers=headers, params={"subject_id": str(uuid4())}
        ).status_code
        == 403
    )
    for changes in [
        {"topic_id": body["document"]["topic_id"]},
        {"score": 1},
        {"desired_item_count": 11},
        {"desired_item_count": 4},
    ]:
        assert start(client, headers, request_plan(body) | changes).status_code == 422
    assert start(client, headers, request_plan(body) | {"mode": "TOPIC"}).status_code == 422
    # Retire via reviewed content workflow; previews must not expose a stale plan.
    with Session(identity.engine) as db:
        from services.domain.content import ItemVersion

        versions = list(db.scalars(select(ItemVersion).where(ItemVersion.status == "APPROVED")))
        for version in versions:
            response = client.post(
                f"/api/v1/admin/item-versions/{version.id}/retire",
                headers=actors["admin"] | {"Idempotency-Key": str(uuid4())},
                json={
                    "expected_revision": version.revision,
                    "reason": "Synthetic inventory withdrawal",
                },
            )
            assert response.status_code == 200, response.text
    unavailable = client.get("/api/v1/me/recommendations/next", headers=headers, params=params)
    assert unavailable.json()["reason_code"] == "CONTENT_UNAVAILABLE"
    assert start(client, headers, request_plan(body)).status_code == 409
    withdrawal = client.post(
        "/api/v1/me/consents",
        headers=headers | {"Idempotency-Key": str(uuid4())},
        json={
            "consent_type": "WITHDRAW",
            "policy_version": identity.settings.consent_policy_version,
            "affirmative": True,
        },
    )
    assert withdrawal.status_code == 200, withdrawal.text
    assert (
        client.get("/api/v1/me/recommendations/next", headers=headers, params=params).status_code
        == 403
    )
    assert start(client, headers, request_plan(body)).status_code == 403


def test_manual_plan_does_not_conflict_with_recommended_start(diagnostic):
    identity, client, actors, body = diagnostic
    headers = actors["learner"]
    preview = client.get(
        "/api/v1/me/recommendations/next",
        headers=headers,
        params={"subject_id": body["subject_id"]},
    ).json()
    manual = start(
        client, headers, request_plan(body) | {"mode": "TOPIC", "topic_id": preview["topic_id"]}
    )
    assert manual.status_code == 201, manual.text
    adaptive = start(client, headers, request_plan(body))
    assert adaptive.status_code == 201, adaptive.text
    assert adaptive.json()["topic_id"] != manual.json()["topic_id"]
    from scripts.replay_recommendations import verify

    with Session(identity.engine) as db:
        assert verify(db) >= 3


def test_expired_manual_plan_releases_topic_for_recommendation(diagnostic):
    identity, client, actors, body = diagnostic
    headers = actors["learner"]
    preview = client.get(
        "/api/v1/me/recommendations/next",
        headers=headers,
        params={"subject_id": body["subject_id"]},
    ).json()
    manual = start(
        client,
        headers,
        request_plan(body)
        | {
            "mode": "TOPIC",
            "topic_id": preview["topic_id"],
        },
    ).json()
    with identity.engine.begin() as connection:
        connection.execute(
            text("UPDATE assessment_sessions SET expires_at=started_at + interval '1 minute'")
        )
    now = identity.clock()
    identity.clock = lambda: now + timedelta(minutes=2)
    result = start(client, headers, request_plan(body))
    assert result.status_code == 201, result.text
    assert result.json()["topic_id"] == manual["topic_id"]
    assert result.json()["id"] != manual["id"]
    with Session(identity.engine) as db:
        assert db.get(AssessmentSession, UUID(manual["id"])).status == "EXPIRED"
