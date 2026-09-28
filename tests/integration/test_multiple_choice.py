"""FR-GRD-001: independently reviewed sets, atomic evidence and version pinning."""

import json
from concurrent.futures import ThreadPoolExecutor
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from scripts.replay_mastery import verify
from services.assessment import AssessmentService
from services.assessment_contracts import SubmitAnswer
from services.domain.assessment import Attempt, Grade
from tests.integration.test_assessment import next_item, prepare_assessment, start
from tests.integration.test_content import create, mutate, review, submit
from tests.integration.test_reassessments import begin, publish

pytestmark = pytest.mark.integration


def multi(body):
    return body | {
        "document": body["document"]
        | {
            "response_type": "MULTIPLE_CHOICE",
            "correct_choice_id": "",
            "correct_choice_ids": ["C", "A"],
            "choices": [{"id": c, "text": c} for c in "ABCD"],
            "hints": ["Compare every label carefully."],
        }
    }


@pytest.fixture
def assessment(content):
    identity, client, actors, body = content
    return prepare_assessment((identity, client, actors, multi(body)))


def answer(client, headers, session, item, ids, key=None):
    return client.post(
        f"/api/v1/sessions/{session}/attempts",
        headers=headers | {"Idempotency-Key": key or str(uuid4())},
        json={
            "session_item_id": item["session_item_id"],
            "response": {"type": "MULTIPLE_CHOICE", "choice_ids": ids},
        },
    )


def test_review_requires_valid_key_and_format(content):
    _, client, actors, body = content
    for change in [
        {"correct_choice_ids": []},
        {"correct_choice_ids": ["Z"]},
        {"correct_choice_id": "A"},
        {"choices": [{"id": "A", "text": "A"}]},
        {"choices": [{"id": "A", "text": "A"}, {"id": "A", "text": "B"}]},
    ]:
        draft = multi(body)
        draft["document"].update(change)
        version = create(client, actors, draft)
        response = mutate(
            client,
            f"item-versions/{version['id']}/submit",
            actors["author"],
            {"expected_revision": version["revision"], "reason": "Invalid set fixture"},
        )
        assert response.status_code == 409, response.text
    version = submit(client, actors, create(client, actors, multi(body)))
    assert review(client, actors, version, actor="author").status_code == 409
    approved = review(client, actors, version)
    assert approved.status_code == 200
    assert approved.json()["document"]["correct_choice_ids"] == ["A", "C"]


def test_full_flow_canonical_retry_and_immutable_history(assessment):
    identity, client, actors, body, versions, plan = assessment
    headers = actors["learner"]
    session = start(client, headers, plan).json()["id"]
    results = []
    for index, ids in enumerate([["C", "A"], ["A"], ["A", "B", "C"], ["B"], ["A", "C"]]):
        item = next_item(client, headers, session)
        assert set(item["response_spec"]) == {"type", "choices"}
        assert item["response_spec"]["type"] == "MULTIPLE_CHOICE"
        if index == 0:
            for invalid in [[], ["A", "A"], ["Z"], list("ABCDEFGHI")]:
                assert answer(client, headers, session, item, invalid).status_code == 422
            assert (
                client.post(
                    f"/api/v1/sessions/{session}/attempts",
                    headers=headers | {"Idempotency-Key": str(uuid4())},
                    json={
                        "session_item_id": item["session_item_id"],
                        "response": {"type": "SINGLE_CHOICE", "choice_id": "A"},
                    },
                ).status_code
                == 422
            )
            hint = client.post(
                f"/api/v1/sessions/{session}/items/{item['session_item_id']}/hint",
                headers=headers | {"Idempotency-Key": str(uuid4())},
                json={"expected_hint_level": 0},
            )
            assert hint.status_code == 200, hint.text
        key = str(uuid4())
        response = answer(client, headers, session, item, ids, key)
        assert response.status_code == 200, response.text
        grade = response.json()
        assert grade["score"] == (1 if index in [0, 4] else 0)
        assert grade["points_awarded"] == grade["score"] * grade["points_possible"]
        assert grade["hint_count"] == (1 if index == 0 else 0)
        assert answer(client, headers, session, item, list(reversed(ids)), key).json() == grade
        assert answer(client, headers, session, item, ["D"], key).status_code == 409
        assert answer(client, headers, session, item, ids).status_code == 409
        results.append(grade)
    state = client.get(f"/api/v1/sessions/{session}", headers=headers).json()
    assert state["status"] == "COMPLETED" and state["answered_count"] == 5
    first = results[0]
    version = next(v for v in versions if v["id"] == first["item_version_id"])
    assert (
        mutate(
            client,
            f"item-versions/{version['id']}/retire",
            actors["reviewer"],
            {"expected_revision": version["revision"], "reason": "Pinned history test"},
        ).status_code
        == 200
    )
    create(
        client,
        actors,
        body
        | {
            "source_version_id": version["id"],
            "document": body["document"] | {"correct_choice_ids": ["B"]},
        },
    )
    assert (
        client.get(f"/api/v1/attempts/{first['attempt_id']}/grade", headers=headers).json() == first
    )
    assert (
        client.get(f"/api/v1/attempts/{first['attempt_id']}/solution", headers=headers).status_code
        == 200
    )
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(Attempt)) == 5
        assert db.scalar(select(func.count()).select_from(Grade)) == 5
        assert verify(db) >= 5
        saved = db.get(Attempt, UUID(first["attempt_id"]))
        assert saved.choice_id is None and saved.response["choice_ids"] == ["A", "C"]
        with pytest.raises(DBAPIError), db.begin_nested():
            db.execute(text("UPDATE attempts SET response='{}'"))


def test_concurrent_retry_rollback_and_reassessment(assessment, monkeypatch):
    identity, client, actors, body, _, plan = assessment
    headers = actors["learner"]
    session = start(client, headers, plan).json()["id"]
    item = next_item(client, headers, session)
    service = AssessmentService(identity)
    token = headers["Authorization"][7:]
    key = uuid4()

    def once(ids):
        return service.submit(
            token,
            UUID(session),
            SubmitAnswer(
                session_item_id=item["session_item_id"],
                response={"type": "MULTIPLE_CHOICE", "choice_ids": ids},
            ),
            key,
            uuid4(),
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(once, [["C", "A"], ["A", "C"]]))
    assert results[0] == results[1]
    original = results[0].model_dump(mode="json")
    item = next_item(client, headers, session)
    key = uuid4()
    original_event = service.event

    def fail(*args, **kwargs):
        raise RuntimeError("Synthetic transaction failure")

    monkeypatch.setattr(service, "event", fail)
    with pytest.raises(RuntimeError):
        once(["A", "C"])
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(Attempt)) == 1
    monkeypatch.setattr(service, "event", original_event)
    target = publish(client, actors, body, "Select the two labels printed on the ready controls.")
    child_response = begin(client, headers, original["attempt_id"])
    assert child_response.status_code == 200, child_response.text
    child = child_response.json()
    item = next_item(client, headers, child["id"])
    assert item["item_version_id"] == target["id"]
    result = answer(client, headers, child["id"], item, ["C", "A"])
    assert result.status_code == 200 and result.json()["score"] == 1
    assert result.json()["hint_count"] == 0
    assert (
        client.get(f"/api/v1/attempts/{original['attempt_id']}/grade", headers=headers).json()
        == original
    )
    with Session(identity.engine) as db:
        assert verify(db) >= 2


def test_database_rejects_noncanonical_or_malformed_sets(assessment):
    identity, client, actors, _, _, plan = assessment
    session = start(client, actors["learner"], plan).json()["id"]
    item = next_item(client, actors["learner"], session)
    cases = [
        None,
        [],
        {},
        {"type": "MULTIPLE_CHOICE"},
        {"type": "MULTIPLE_CHOICE", "choice_ids": None},
        *[
            {"type": "MULTIPLE_CHOICE", "choice_ids": ids}
            for ids in [[], ["C", "A"], ["A", "A"], ["a"], [1], [None], list("ABCDEFGHI")]
        ],
        {"type": "MULTIPLE_CHOICE", "choice_ids": ["A"], "score": 1},
    ]
    with identity.engine.begin() as conn:
        for value in cases:
            assert not conn.scalar(
                text("SELECT valid_multiple_response(CAST(:v AS jsonb))"), {"v": json.dumps(value)}
            )
        assert conn.scalar(
            text("SELECT valid_multiple_response(CAST(:v AS jsonb))"),
            {"v": json.dumps({"type": "MULTIPLE_CHOICE", "choice_ids": ["A", "C"]})},
        )
    # Valid shape but unknown member must fail the assignment guard, before evidence writes.
    with pytest.raises(DBAPIError, match="active assignment"), identity.engine.begin() as conn:
        conn.execute(
            text("""INSERT INTO attempts
          (id, learner_id, session_item_id, item_version_id, response, submitted_at, hint_count)
          SELECT :id, s.learner_id, si.id, si.item_version_id,
            '{"type":"MULTIPLE_CHOICE","choice_ids":["Z"]}'::jsonb, now(), 0
          FROM session_items si JOIN assessment_sessions s ON s.id=si.session_id
          WHERE si.id=:item"""),
            {"id": uuid4(), "item": UUID(item["session_item_id"])},
        )
