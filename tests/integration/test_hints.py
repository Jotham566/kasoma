"""FR-GRD-006/007, FR-ID-003: reviewed hint disclosure and atomic evidence."""

from concurrent.futures import ThreadPoolExecutor
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from scripts.replay_mastery import verify
from services.assessment import AssessmentService
from services.assessment_contracts import HintRequest, SubmitAnswer
from services.domain.assessment import (
    AssessmentEvent,
    AssessmentReceipt,
    Attempt,
    HintUse,
    SessionItem,
)
from services.domain.mastery import MasteryEvidence
from services.hints import access
from services.identity import IdentityError
from tests.integration.test_assessment import answer as choice_answer
from tests.integration.test_assessment import next_item, start
from tests.integration.test_content import create, review, submit
from tests.integration.test_diagnostics import diagnostic as diagnostic_fixture

diagnostic = diagnostic_fixture

pytestmark = pytest.mark.integration
HINTS = [
    "Read the prompt carefully.",
    "Compare the labels.",
    "Check your selection before submitting.",
]


@pytest.fixture
def hinted(content, request):
    identity, client, actors, body = content
    document = body["document"] | {"hints": HINTS}
    if getattr(request, "param", "choice") == "numeric":
        document |= {
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
    draft = body | {"document": document}
    for _ in range(5):
        result = review(client, actors, submit(client, actors, create(client, actors, draft)))
        assert result.status_code == 200, result.text
    headers = actors["learner"]
    assert (
        client.patch(
            "/api/v1/me",
            headers=headers,
            json={
                "display_name": "Synthetic hints",
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
                "affirmative": True,
                "policy_version": identity.settings.consent_policy_version,
            },
        ).status_code
        == 200
    )
    plan = {
        "subject_id": body["subject_id"],
        "topic_id": body["document"]["topic_id"],
        "desired_item_count": 5,
    }
    session = start(client, headers, plan).json()["id"]
    return identity, client, actors, session


def hint(client, headers, session, item, level, key=None):
    return client.post(
        f"/api/v1/sessions/{session}/items/{item}/hint",
        headers=headers | {"Idempotency-Key": key or str(uuid4())},
        json={"expected_hint_level": level},
    )


@pytest.mark.parametrize("hinted", ["choice", "numeric"], indirect=True)
def test_hints_resume_freeze_independence_and_leave_post_answer_grade_unchanged(hinted):
    identity, client, actors, session = hinted
    headers = actors["learner"]
    item = next_item(client, headers, session)
    assert item["hints"] == [] and item["has_more_hints"]
    key = str(uuid4())
    response = hint(client, headers, session, item["session_item_id"], 0, key)
    assert response.status_code == 200, response.text
    assert response.json()["hints"] == [{"level": 1, "text": HINTS[0], "phase": "BEFORE_ANSWER"}]
    assert hint(client, headers, session, item["session_item_id"], 0, key).json() == response.json()
    assert hint(client, headers, session, item["session_item_id"], 0).status_code == 409
    assert next_item(client, headers, session)["hints"] == response.json()["hints"]
    if item["response_spec"]["type"] == "NUMERIC":
        result = client.post(
            f"/api/v1/sessions/{session}/attempts",
            headers=headers | {"Idempotency-Key": str(uuid4())},
            json={
                "session_item_id": item["session_item_id"],
                "response": {"type": "NUMERIC", "value": "1", "unit": "m"},
            },
        )
    else:
        result = choice_answer(client, headers, session, item)
    assert result.status_code == 200, result.text
    saved = result.json()
    assert saved["score"] == 1 and saved["hint_count"] == saved["highest_hint_level"] == 1
    post = client.post(
        f"/api/v1/attempts/{saved['attempt_id']}/hint",
        headers=headers | {"Idempotency-Key": str(uuid4())},
        json={"expected_hint_level": 1},
    )
    assert post.status_code == 200, post.text
    assert post.json()["hints"][-1]["phase"] == "AFTER_ANSWER"
    assert (
        client.get(f"/api/v1/attempts/{saved['attempt_id']}/grade", headers=headers).json() == saved
    )
    assert (
        client.get(f"/api/v1/attempts/{saved['attempt_id']}/hints", headers=headers).json()
        == post.json()
    )
    with Session(identity.engine) as db:
        attempt = db.get(Attempt, UUID(saved["attempt_id"]))
        row = db.scalar(select(MasteryEvidence).where(MasteryEvidence.attempt_id == attempt.id))
        assert row.snapshot["independence_weight"] == 0.85
        assert row.snapshot["source"]["highest_hint_level"] == 1
        event = db.scalar(
            select(AssessmentEvent).where(
                AssessmentEvent.attempt_id == attempt.id, AssessmentEvent.type == "mastery.updated"
            )
        )
        assert event.hint_count == event.highest_hint_level == 1
        assert verify(db) == 2
        with pytest.raises(DBAPIError), db.begin_nested():
            db.execute(text("UPDATE hint_uses SET level=3"))
        with pytest.raises(DBAPIError), db.begin_nested():
            db.execute(text("UPDATE attempts SET hint_count=0"))
    # Retry the saved hint even after submission cannot create new usage or reveal another level.
    assert hint(client, headers, session, item["session_item_id"], 0, key).json() == response.json()
    assert hint(client, headers, session, item["session_item_id"], 2).status_code == 409


def test_authorization_retirement_unserved_and_no_solution_bypass(hinted):
    identity, client, actors, session = hinted
    headers = actors["learner"]
    with Session(identity.engine) as db:
        assigned = list(
            db.scalars(
                select(SessionItem)
                .where(SessionItem.session_id == UUID(session))
                .order_by(SessionItem.position)
            )
        )
    assert hint(client, headers, session, assigned[0].id, 0).status_code == 404
    item = next_item(client, headers, session)
    assert hint(client, headers, session, assigned[1].id, 0).status_code == 404
    assert hint(client, actors["other"], session, item["session_item_id"], 0).status_code == 403
    # A separately consented learner still cannot access the assignment.
    subject = client.get("/api/v1/me", headers=headers).json()["subject_ids"]
    assert (
        client.patch(
            "/api/v1/me",
            headers=actors["other"],
            json={
                "display_name": "Synthetic other",
                "birth_date": "2000-01-01",
                "subject_ids": subject,
            },
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/api/v1/me/consents",
            headers=actors["other"] | {"Idempotency-Key": str(uuid4())},
            json={
                "consent_type": "SELF",
                "affirmative": True,
                "policy_version": identity.settings.consent_policy_version,
            },
        ).status_code
        == 200
    )
    assert hint(client, actors["other"], session, item["session_item_id"], 0).status_code == 404
    assert hint(client, headers, str(uuid4()), item["session_item_id"], 0).status_code == 404
    for level in range(3):
        assert hint(client, headers, session, item["session_item_id"], level).status_code == 200
    assert (
        hint(client, headers, session, item["session_item_id"], 3).json()["error"]["code"]
        == "HINT_UNAVAILABLE"
    )
    assert (
        client.get(
            f"/api/v1/attempts/{item['session_item_id']}/solution", headers=headers
        ).status_code
        == 404
    )
    # Retire through the content workflow.
    full = client.get(
        f"/api/v1/admin/item-versions/{item['item_version_id']}", headers=actors["reviewer"]
    ).json()
    assert (
        client.post(
            f"/api/v1/admin/item-versions/{item['item_version_id']}/retire",
            headers=actors["reviewer"] | {"Idempotency-Key": str(uuid4())},
            json={"expected_revision": full["revision"], "reason": "Synthetic withdrawal"},
        ).status_code
        == 200
    )
    assert hint(client, headers, session, item["session_item_id"], 3).status_code == 404
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
    assert hint(client, headers, session, item["session_item_id"], 0).status_code == 403


def test_concurrent_hint_and_answer_freeze_exact_disclosure(hinted):
    identity, client, actors, session = hinted
    headers = actors["learner"]
    item = next_item(client, headers, session)
    service, token = AssessmentService(identity), headers["Authorization"].split()[1]

    def reveal():
        try:
            return access(
                service,
                token,
                session_id=UUID(session),
                item_id=UUID(item["session_item_id"]),
                body=HintRequest(expected_hint_level=0),
                key=uuid4(),
                request=uuid4(),
            )
        except IdentityError as error:
            return error

    def respond():
        return service.submit(
            token,
            UUID(session),
            SubmitAnswer(
                session_item_id=UUID(item["session_item_id"]), response={"choice_id": "A"}
            ),
            uuid4(),
            uuid4(),
        )

    with ThreadPoolExecutor(max_workers=2) as workers:
        hint_future, answer_future = workers.submit(reveal), workers.submit(respond)
        disclosure, grade = hint_future.result(), answer_future.result()
    with Session(identity.engine) as db:
        count = db.scalar(select(func.count()).select_from(HintUse))
        assert grade.hint_count == count
        if isinstance(disclosure, IdentityError):
            assert count == 0
        else:
            assert count == 1
        assert verify(db) == 2


def test_hint_transaction_failure_rolls_back_usage_receipt_event(hinted, monkeypatch):
    identity, client, actors, session = hinted
    headers = actors["learner"]
    item = next_item(client, headers, session)
    original = AssessmentService.event

    def fail(*args, **kwargs):
        raise RuntimeError("Synthetic outbox failure")

    monkeypatch.setattr(AssessmentService, "event", fail)
    key = str(uuid4())
    assert hint(client, headers, session, item["session_item_id"], 0, key).status_code == 500
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(HintUse)) == 0
        assert (
            db.get(
                AssessmentReceipt,
                (UUID(client.get("/api/v1/me", headers=headers).json()["id"]), UUID(key)),
            )
            is None
        )
    monkeypatch.setattr(AssessmentService, "event", original)
    assert hint(client, headers, session, item["session_item_id"], 0, key).status_code == 200


def test_diagnostic_hints_are_disabled_before_and_after_submission(diagnostic):
    identity, client, actors, body = diagnostic
    from tests.integration.test_diagnostics import (
        start as start_diagnostic,
    )
    from tests.integration.test_diagnostics import (
        submit as diagnostic_submit,
    )

    headers = actors["learner"]
    session = start_diagnostic(client, headers, body["subject_id"]).json()["id"]
    item = next_item(client, headers, session)
    assert item["hints"] == [] and not item["has_more_hints"]
    assert hint(client, headers, session, item["session_item_id"], 0).status_code == 403
    attempt = diagnostic_submit(client, headers, session, item).json()["attempt_id"]
    assert (
        client.post(
            f"/api/v1/attempts/{attempt}/hint",
            headers=headers | {"Idempotency-Key": str(uuid4())},
            json={"expected_hint_level": 0},
        ).status_code
        == 403
    )
    assert client.get(f"/api/v1/attempts/{attempt}/hints", headers=headers).status_code == 403
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(HintUse)) == 0


def test_duplicate_hint_delivery_and_database_count_forgery(hinted):
    identity, client, actors, session = hinted
    headers = actors["learner"]
    item = next_item(client, headers, session)
    service, token, key = AssessmentService(identity), headers["Authorization"].split()[1], uuid4()

    def reveal(_):
        return access(
            service,
            token,
            session_id=UUID(session),
            item_id=UUID(item["session_item_id"]),
            body=HintRequest(expected_hint_level=0),
            key=key,
            request=uuid4(),
        )

    with ThreadPoolExecutor(max_workers=2) as workers:
        results = list(workers.map(reveal, range(2)))
    assert results[0] == results[1]
    owner = UUID(client.get("/api/v1/me", headers=headers).json()["id"])
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(HintUse)) == 1
        with pytest.raises(DBAPIError), db.begin_nested():
            db.add(
                Attempt(
                    id=uuid4(),
                    learner_id=owner,
                    session_item_id=UUID(item["session_item_id"]),
                    item_version_id=UUID(item["item_version_id"]),
                    choice_id="A",
                    response=None,
                    submitted_at=identity.clock(),
                    hint_count=0,
                    highest_hint_level=0,
                    channel="WEB",
                )
            )
            db.flush()
