"""FR-GRD-008: independent reassessment, durable linkage and protected history."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from scripts.replay_mastery import verify as verify_mastery
from scripts.replay_reassessments import verify
from services.assessment import AssessmentService
from services.domain.assessment import AssessmentEvent, Attempt, Reassessment
from services.reassessments import access
from tests.integration.test_assessment import answer, next_item, start
from tests.integration.test_assessment import assessment as assessment_fixture
from tests.integration.test_content import create, mutate, review, submit

assessment = assessment_fixture
pytestmark = pytest.mark.integration
PROMPT = "The test panel has two controls. Which one starts the timer?"


@pytest.fixture
def original(assessment):
    identity, client, actors, body, versions, plan = assessment
    headers = actors["learner"]
    session = start(client, headers, plan).json()["id"]
    item = next_item(client, headers, session)
    grade = answer(client, headers, session, item, choice="B").json()
    return identity, client, actors, body, session, grade


def publish(client, actors, body, prompt=PROMPT, equivalents=None):
    draft = body | {
        "document": body["document"] | {"prompt": prompt, "equivalents": equivalents or []}
    }
    response = review(client, actors, submit(client, actors, create(client, actors, draft)))
    assert response.status_code == 200, response.text
    return response.json()


def begin(client, headers, attempt, key=None):
    return client.post(
        f"/api/v1/attempts/{attempt}/reassessment",
        headers=headers | {"Idempotency-Key": key or str(uuid4())},
    )


def test_explicit_preference_independent_evidence_resume_and_immutable_original(original):
    identity, client, actors, body, parent, saved = original
    headers = actors["learner"]
    publish(client, actors, body, "Inspect the status board and locate its ready indicator.")
    pair = publish(
        client,
        actors,
        body,
        equivalents=[{"version_id": saved["item_version_id"], "confidence": 0.9}],
    )
    key = str(uuid4())
    started = begin(client, headers, saved["attempt_id"], key)
    assert started.status_code == 200, started.text
    child = started.json()
    assert child["kind"] == "REASSESSMENT" and child["item_count"] == 1
    assert child["original_session_id"] == parent
    assert child["original_attempt_id"] == saved["attempt_id"]
    assert begin(client, headers, saved["attempt_id"], key).json() == child
    assert begin(client, headers, saved["attempt_id"]).json() == child
    assert (
        client.get(f"/api/v1/attempts/{saved['attempt_id']}/reassessment", headers=headers).json()
        == child
    )
    assert child in client.get("/api/v1/sessions/active", headers=headers).json()
    item = next_item(client, headers, child["id"])
    assert item["item_version_id"] == pair["id"]
    assert not item["has_more_hints"]
    assert (
        client.post(
            f"/api/v1/sessions/{child['id']}/items/{item['session_item_id']}/hint",
            headers=headers | {"Idempotency-Key": str(uuid4())},
            json={"expected_hint_level": 0},
        ).status_code
        == 403
    )
    assert (
        client.get(
            f"/api/v1/attempts/{item['session_item_id']}/solution", headers=headers
        ).status_code
        == 404
    )
    result = answer(client, headers, child["id"], item).json()
    assert result["score"] == 1 and result["hint_count"] == 0
    assert result["attempt_id"] != saved["attempt_id"]
    assert (
        client.get(f"/api/v1/attempts/{saved['attempt_id']}/grade", headers=headers).json() == saved
    )
    assert begin(client, headers, result["attempt_id"]).status_code == 403
    assert begin(client, headers, saved["attempt_id"]).json()["status"] == "COMPLETED"
    with Session(identity.engine) as db:
        link = db.get(Reassessment, UUID(saved["attempt_id"]))
        assert link.basis == "EQUIVALENT"
        assert link.snapshot["candidates"][0]
        assert verify(db) == 1 and verify_mastery(db) == 3
        assert db.scalar(select(func.count()).select_from(Attempt)) == 2
        assert (
            db.scalar(
                select(func.count())
                .select_from(AssessmentEvent)
                .where(AssessmentEvent.type == "reassessment.completed")
            )
            == 1
        )
        with pytest.raises(DBAPIError), db.begin_nested():
            db.execute(text("UPDATE reassessments SET elapsed_seconds=0"))
        with pytest.raises(DBAPIError), db.begin_nested():
            db.execute(
                text("UPDATE assessment_sessions SET item_count=2 WHERE kind='REASSESSMENT'")
            )


def test_fallback_shortage_seen_reserved_and_clones(original):
    identity, client, actors, body, parent, saved = original
    headers = actors["learner"]
    assert (
        begin(client, headers, saved["attempt_id"]).json()["error"]["code"]
        == "REASSESSMENT_UNAVAILABLE"
    )
    # A new stable identity with the same wording is still a duplicate.
    publish(client, actors, body, body["document"]["prompt"])
    assert begin(client, headers, saved["attempt_id"]).status_code == 409
    target = publish(client, actors, body)
    child = begin(client, headers, saved["attempt_id"]).json()
    item = next_item(client, headers, child["id"])
    assert item["item_version_id"] == target["id"]
    # The same candidate is now reserved/seen, so a second original cannot use it.
    second = answer(client, headers, parent, next_item(client, headers, parent)).json()
    assert begin(client, headers, second["attempt_id"]).status_code == 409
    with Session(identity.engine) as db:
        assert db.get(Reassessment, UUID(saved["attempt_id"])).basis == "SAME_SKILL_DIFFICULTY"
        assert db.scalar(select(func.count()).select_from(Reassessment)) == 1


def test_concurrent_start_and_atomic_rollback(original, monkeypatch):
    identity, client, actors, body, parent, saved = original
    publish(client, actors, body)
    service = AssessmentService(identity)
    original_event = AssessmentService.event

    def fail(*args, **kwargs):
        raise RuntimeError("Synthetic outbox failure")

    monkeypatch.setattr(AssessmentService, "event", fail)
    assert begin(client, actors["learner"], saved["attempt_id"]).status_code == 500
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(Reassessment)) == 0
    monkeypatch.setattr(AssessmentService, "event", original_event)
    token = actors["learner"]["Authorization"].split()[1]
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(
                lambda _: access(service, token, UUID(saved["attempt_id"]), uuid4(), uuid4()),
                range(2),
            )
        )
    assert results[0].id == results[1].id
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(Reassessment)) == 1


def test_authorization_retirement_expiry_and_consent(original):
    identity, client, actors, body, parent, saved = original
    headers = actors["learner"]
    target = publish(client, actors, body)
    assert begin(client, actors["other"], saved["attempt_id"]).status_code == 403
    assert begin(client, headers, str(uuid4())).status_code == 404
    child = begin(client, headers, saved["attempt_id"]).json()
    # Retirement after assignment must prevent serving the question.
    response = mutate(
        client,
        f"item-versions/{target['id']}/retire",
        actors["reviewer"],
        {"expected_revision": target["revision"], "reason": "Synthetic withdrawal"},
    )
    assert response.status_code == 200
    assert (
        client.get(f"/api/v1/sessions/{child['id']}/next-item", headers=headers).status_code == 404
    )
    # Expired child remains the same historical link and cannot mint a replacement.
    now = identity.clock()
    with identity.engine.begin() as conn:
        conn.execute(
            text(
                "UPDATE assessment_sessions SET expires_at=started_at+interval '1 second' "
                "WHERE kind='REASSESSMENT'"
            )
        )
    identity.clock = lambda: now + timedelta(seconds=2)
    assert begin(client, headers, saved["attempt_id"]).json()["status"] == "EXPIRED"
    assert (
        client.post(
            "/api/v1/me/consents",
            headers=headers | {"Idempotency-Key": str(uuid4())},
            json={
                "consent_type": "WITHDRAW",
                "affirmative": True,
                "policy_version": identity.settings.consent_policy_version,
            },
        ).status_code
        == 200
    )
    assert begin(client, headers, saved["attempt_id"]).status_code == 403


def test_equivalence_publication_rejects_clones_and_review_by_either_author(content):
    from services.staff import provision

    identity, client, actors, body = content
    target = publish(client, actors, body, body["document"]["prompt"])
    claim = [{"version_id": target["id"], "confidence": 0.9}]
    clone = body | {"document": body["document"] | {"equivalents": claim}}
    rejected = mutate(client, "items", actors["other"], clone)
    assert rejected.status_code == 409
    assert "equivalents" in rejected.text
    changed = clone | {
        "document": clone["document"] | {"prompt": PROMPT, "difficulty": "CHALLENGING"}
    }
    assert mutate(client, "items", actors["other"], changed).status_code == 409
    # Pair author differs from target author; neither may approve this claim.
    valid = clone | {"document": clone["document"] | {"prompt": PROMPT}}
    other_actors = actors | {"author": actors["other"]}
    version = submit(client, other_actors, create(client, other_actors, valid))
    provision(identity, "author@example.invalid", "ACADEMIC_REVIEWER")
    assert (
        review(client, actors, version, actor="author").json()["error"]["code"]
        == "SELF_REVIEW_FORBIDDEN"
    )
    assert review(client, actors, version).status_code == 200


def test_numeric_reassessment_uses_shared_grader_and_new_evidence(original):
    identity, client, actors, body, parent, saved = original
    document = body["document"] | {
        "response_type": "NUMERIC",
        "choices": [],
        "correct_choice_id": "",
        "numeric_spec": {
            "expected_value": "1",
            "canonical_unit": "m",
            "units": [{"label": "m", "factor": "1", "offset": "0"}],
            "absolute_tolerance": "0",
            "relative_tolerance": "0",
            "accepted_forms": ["DECIMAL"],
            "significant_figures_policy": "IGNORE",
            "significant_figures": None,
        },
    }
    publish(
        client,
        actors,
        body | {"document": document},
        "A rope measures one metre. Report its length in metres.",
    )
    headers = actors["learner"]
    child = begin(client, headers, saved["attempt_id"]).json()
    item = next_item(client, headers, child["id"])
    key = str(uuid4())
    payload = {
        "session_item_id": item["session_item_id"],
        "response": {"type": "NUMERIC", "value": "1", "unit": "m"},
    }
    path = f"/api/v1/sessions/{child['id']}/attempts"
    response = client.post(path, headers=headers | {"Idempotency-Key": key}, json=payload)
    assert response.status_code == 200, response.text
    assert response.json()["score"] == 1
    assert (
        client.post(path, headers=headers | {"Idempotency-Key": key}, json=payload).json()
        == response.json()
    )
    with Session(identity.engine) as db:
        assert verify_mastery(db) == 3
        assert verify(db) == 1


def test_consented_other_learner_cannot_start_or_read_reassessment(original):
    identity, client, actors, body, parent, saved = original
    publish(client, actors, body)
    assert begin(client, actors["learner"], saved["attempt_id"]).status_code == 200
    other = actors["other"]
    assert (
        client.patch(
            "/api/v1/me",
            headers=other,
            json={
                "display_name": "Synthetic other",
                "birth_date": "2000-01-01",
                "subject_ids": [body["subject_id"]],
            },
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/api/v1/me/consents",
            headers=other | {"Idempotency-Key": str(uuid4())},
            json={
                "consent_type": "SELF",
                "affirmative": True,
                "policy_version": identity.settings.consent_policy_version,
            },
        ).status_code
        == 200
    )
    assert begin(client, other, saved["attempt_id"]).status_code == 404
    assert (
        client.get(
            f"/api/v1/attempts/{saved['attempt_id']}/reassessment", headers=other
        ).status_code
        == 404
    )
