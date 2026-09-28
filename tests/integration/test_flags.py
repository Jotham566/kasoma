"""Owned reporting, immutable sources, confidential triage and independent publication."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.domain.content import AuditLog, ContentEvent
from services.domain.flags import ContentFlag, FlagHistory
from services.domain.mastery import MasteryHistory
from services.flag_contracts import FlagInput
from services.flags import FlagService
from services.identity_contracts import ConsentInput
from tests.integration.test_assessment import answer, next_item, start
from tests.integration.test_assessment import assessment as assessment_fixture
from tests.integration.test_content import create, review, submit
from tests.integration.test_diagnostics import diagnostic as diagnostic_fixture
from tests.integration.test_diagnostics import start as start_diagnostic
from tests.integration.test_diagnostics import submit as save_diagnostic

assessment = assessment_fixture
diagnostic = diagnostic_fixture
pytestmark = pytest.mark.integration


def saved(assessment):
    identity, client, actors, body, versions, plan = assessment
    session = start(client, actors["learner"], plan).json()["id"]
    grade = answer(
        client, actors["learner"], session, next_item(client, actors["learner"], session)
    ).json()
    return grade


def report(client, headers, attempt, body=None, key=None):
    return client.post(
        f"/api/v1/attempts/{attempt}/flag",
        headers=headers | {"Idempotency-Key": key or str(uuid4())},
        json=body or {"category": "GRADE_DISPUTE", "comment": "Synthetic grade issue"},
    )


def triage(client, headers, flag, **changes):
    body = {
        "expected_revision": flag["revision"],
        "status": "IN_REVIEW",
        "priority": "NORMAL",
        "claim": True,
    } | changes
    return client.patch(
        f"/api/v1/admin/content-flags/{flag['id']}",
        headers=headers | {"Idempotency-Key": str(uuid4())},
        json=body,
    )


def test_report_replay_encryption_audit_and_triage_lifecycle(assessment):
    identity, client, actors, body, versions, plan = assessment
    grade = saved(assessment)
    attempt = grade["attempt_id"]
    key = str(uuid4())
    response = report(client, actors["learner"], attempt, key=key)
    assert response.status_code == 201, response.text
    receipt = response.json()
    assert set(receipt) == {"id", "category", "created_at"}
    assert report(client, actors["learner"], attempt, key=key).json() == receipt
    assert report(client, actors["learner"], attempt).json() == receipt
    assert (
        report(
            client,
            actors["learner"],
            attempt,
            {"category": "GRADE_DISPUTE", "comment": "different"},
            key,
        ).status_code
        == 409
    )
    assert (
        report(
            client,
            actors["learner"],
            attempt,
            {"category": "GRADE_DISPUTE", "comment": "different"},
        ).status_code
        == 409
    )
    path = f"/api/v1/admin/content-flags/{receipt['id']}"
    detail = client.get(path, headers=actors["reviewer"]).json()
    assert detail["item_version_id"] == grade["item_version_id"]
    assert detail["comment"] == "Synthetic grade issue"
    assert not {"reporter_id", "attempt_id", "response", "grade"} & detail.keys()
    assert triage(client, actors["author"], detail).status_code == 409
    claim = triage(client, actors["reviewer"], detail)
    assert claim.status_code == 200, claim.text
    current = claim.json()
    assert current["revision"] == 2 and current["status"] == "IN_REVIEW"
    assert triage(client, actors["second"], detail).status_code == 409
    terminal = {
        "expected_revision": 2,
        "status": "RESOLVED",
        "priority": "HIGH",
        "resolution": "Synthetic checked rubric; no evidence changes.",
    }
    key = str(uuid4())
    headers = actors["reviewer"] | {"Idempotency-Key": key}
    result = client.patch(path, headers=headers, json=terminal)
    assert result.status_code == 200, result.text
    assert client.patch(path, headers=headers, json=terminal).json() == result.json()
    assert len(result.json()["history"]) == 3
    assert result.json()["retention_due_at"].startswith(str(identity.clock().year + 2))
    # SQL CHECK permits UNKNOWN; the explicit non-null guard must reject this
    # before the deferred history check, rather than silently lose the deadline.
    with (
        pytest.raises(DBAPIError, match="terminal_flag_retention_required"),
        identity.engine.begin() as conn,
    ):
        conn.execute(text("UPDATE content_flags SET retention_due_at=NULL, revision=revision+1"))
    reopened = triage(client, actors["second"], result.json())
    assert reopened.status_code == 200, reopened.text
    assert reopened.json()["retention_due_at"] is None
    assert reopened.json()["resolution"] == ""
    assert (
        client.get(f"/api/v1/attempts/{attempt}/grade", headers=actors["learner"]).json() == grade
    )
    with Session(identity.engine) as db:
        row = db.get(ContentFlag, UUID(receipt["id"]))
        assert row.reporter_id and row.item_version_id == UUID(grade["item_version_id"])
        assert "Synthetic" not in row.comment_encrypted
        assert identity.decrypt(row.comment_encrypted) == "Synthetic grade issue"
        assert db.scalar(select(func.count()).select_from(ContentFlag)) == 1
        assert db.scalar(select(func.count()).select_from(FlagHistory)) == 4
        assert db.scalar(select(func.count()).select_from(MasteryHistory)) == 1
        audits = list(db.scalars(select(AuditLog).where(AuditLog.action.like("content.flag.%"))))
        assert any(a.action == "content.flag.read" for a in audits)
        assert all("Synthetic grade issue" not in a.reason for a in audits)
        assert (
            db.scalar(
                select(func.count())
                .select_from(ContentEvent)
                .where(ContentEvent.type.like("content.flag.%"))
            )
            == 4
        )
    for sql in [
        "UPDATE content_flags SET reporter_id=gen_random_uuid()",
        "UPDATE content_flags SET revision=revision+1",
        "DELETE FROM content_flag_history",
    ]:
        with pytest.raises(DBAPIError), identity.engine.begin() as conn:
            conn.execute(text(sql))


def test_ownership_roles_consent_and_privileged_fields(assessment):
    identity, client, actors, body, versions, plan = assessment
    grade = saved(assessment)
    attempt = grade["attempt_id"]
    assert report(client, {}, attempt).status_code == 401
    assert report(client, actors["learner"], str(uuid4())).status_code == 404
    for injected in [
        {"item_version_id": str(uuid4())},
        {"priority": "HIGH"},
        {"reporter_id": str(uuid4())},
    ]:
        assert (
            report(client, actors["learner"], attempt, {"category": "OTHER"} | injected).status_code
            == 422
        )
    receipt = report(client, actors["learner"], attempt).json()
    for role in ["learner", "other", "support"]:
        assert client.get("/api/v1/admin/content-flags", headers=actors[role]).status_code == 403
        assert (
            client.get(
                f"/api/v1/admin/content-flags/{receipt['id']}", headers=actors[role]
            ).status_code
            == 403
        )
        assert triage(client, actors[role], receipt | {"revision": 1}).status_code == 403
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
    assert report(client, other, attempt).status_code == 404
    assert client.get(f"/api/v1/attempts/{attempt}/flag", headers=other).status_code == 404
    identity.consent(
        actors["learner"]["Authorization"][7:],
        ConsentInput(
            consent_type="WITHDRAW",
            affirmative=True,
            policy_version=identity.settings.consent_policy_version,
        ),
        uuid4(),
        str(uuid4()),
    )
    assert report(client, actors["learner"], attempt).status_code == 403
    assert (
        client.get(f"/api/v1/attempts/{attempt}/flag", headers=actors["learner"]).status_code == 403
    )


def test_concurrent_duplicate_and_atomic_failure(assessment, monkeypatch):
    identity, client, actors, body, versions, plan = assessment
    grade = saved(assessment)
    service = FlagService(identity)
    token = actors["learner"]["Authorization"][7:]

    def once(_):
        return service.create(
            token, UUID(grade["attempt_id"]), FlagInput(category="OTHER"), uuid4(), uuid4()
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(once, range(2)))
    assert results[0] == results[1]

    def fail(*args, **kwargs):
        raise RuntimeError("Injected audit failure")

    monkeypatch.setattr(service, "audit", fail)
    with pytest.raises(RuntimeError):
        service.create(
            token, UUID(grade["attempt_id"]), FlagInput(category="UNCLEAR"), uuid4(), uuid4()
        )
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(ContentFlag)) == 1
        assert db.scalar(select(func.count()).select_from(FlagHistory)) == 1


@pytest.mark.parametrize("before_flag", [False, True])
def test_disputed_successor_needs_second_independent_review(assessment, before_flag):
    identity, client, actors, body, versions, plan = assessment
    grade = saved(assessment)
    successor = (
        create(client, actors, body | {"source_version_id": grade["item_version_id"]})
        if before_flag
        else None
    )
    assert report(client, actors["learner"], grade["attempt_id"]).status_code == 201
    if successor is None:
        successor = create(client, actors, body | {"source_version_id": grade["item_version_id"]})
        assert successor["requires_second_review"]
    pending = submit(client, actors, successor)
    first = review(client, actors, pending)
    assert first.status_code == 200 and first.json()["status"] == "IN_REVIEW"
    second = review(client, actors, first.json(), actor="second")
    assert second.status_code == 200 and second.json()["status"] == "APPROVED"


def test_queue_pagination_priority_and_fresh_auth(assessment):
    identity, client, actors, body, versions, plan = assessment
    grade = saved(assessment)
    for category in ["UNSAFE_CONTENT", "OTHER", "UNCLEAR"]:
        assert (
            report(
                client, actors["learner"], grade["attempt_id"], {"category": category}
            ).status_code
            == 201
        )
    first = client.get("/api/v1/admin/content-flags?limit=2", headers=actors["reviewer"]).json()
    second = client.get(
        "/api/v1/admin/content-flags",
        headers=actors["reviewer"],
        params={"limit": 2, "cursor": first["next_cursor"]},
    ).json()
    assert len({r["id"] for r in first["data"] + second["data"]}) == 3
    assert second["next_cursor"] is None
    unsafe = next(r for r in first["data"] + second["data"] if r["category"] == "UNSAFE_CONTENT")
    assert unsafe["priority"] == "HIGH"
    assert (
        triage(
            client, actors["reviewer"], unsafe, status="DISMISSED", resolution="Synthetic duplicate"
        ).status_code
        == 200
    )
    queue = client.get("/api/v1/admin/content-flags?status=OPEN", headers=actors["admin"]).json()
    assert len(queue["data"]) == 2
    for query in ["limit=51", "status=INVALID", "cursor=bad"]:
        assert (
            client.get(
                "/api/v1/admin/content-flags?" + query, headers=actors["reviewer"]
            ).status_code
            == 422
        )
    now = identity.clock()
    identity.clock = lambda: now + timedelta(minutes=11)
    assert triage(client, actors["reviewer"], unsafe).status_code == 401


def test_diagnostic_reporting_does_not_unseal_feedback(diagnostic):
    identity, client, actors, body = diagnostic
    headers = actors["learner"]
    session = start_diagnostic(client, headers, body["subject_id"]).json()["id"]
    receipt = save_diagnostic(client, headers, session, next_item(client, headers, session)).json()
    result = report(client, headers, receipt["attempt_id"])
    assert result.status_code == 201, result.text
    view = client.get(f"/api/v1/diagnostics/{session}", headers=headers).json()
    assert view["result"] is None
    assert view["answered_attempts"] == [{"attempt_id": receipt["attempt_id"], "position": 1}]
    assert (
        client.get(f"/api/v1/attempts/{receipt['attempt_id']}/grade", headers=headers).status_code
        == 403
    )
    assert "score" not in result.text


def test_new_report_limit_preserves_successful_retry(assessment):
    identity, client, actors, body, versions, plan = assessment
    headers = actors["learner"]
    session = start(client, headers, plan).json()["id"]
    grades = [
        answer(client, headers, session, next_item(client, headers, session)).json()
        for _ in range(2)
    ]
    first = None
    key = str(uuid4())
    for index, (grade, category) in enumerate(
        (g, c)
        for g in grades
        for c in [
            "OTHER",
            "UNCLEAR",
            "QUESTION_ERROR",
            "ACCESSIBILITY",
            "GRADE_DISPUTE",
            "UNSAFE_CONTENT",
        ]
    ):
        result = report(
            client,
            headers,
            grade["attempt_id"],
            {"category": category},
            key if index == 0 else None,
        )
        assert result.status_code == (201 if index < 10 else 429), result.text
        if index == 0:
            first = result.json()
    assert (
        report(client, headers, grades[0]["attempt_id"], {"category": "OTHER"}, key).json() == first
    )
