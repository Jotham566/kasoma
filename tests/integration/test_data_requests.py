"""FR-ID-006: rights access without learning consent; auditable, pending intake."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.data_request_contracts import DataRequestInput
from services.data_requests import DataRequestService
from services.domain.content import AuditLog
from services.domain.data_requests import DataRequest, DataRequestReceipt, DataRequestReview
from services.domain.identity import IdentityEvent
from services.staff import provision

pytestmark = pytest.mark.integration


def create(client, headers, kind="EXPORT", key=None):
    return client.post(
        "/api/v1/me/data-requests",
        headers=headers | {"Idempotency-Key": key or str(uuid4())},
        json={"kind": kind, "affirmative": True},
    )


def claim(client, headers, target, key=None):
    return client.post(
        f"/api/v1/admin/data-requests/{target}/claim",
        headers=headers | {"Idempotency-Key": key or str(uuid4())},
        json={},
    )


def test_intake_without_profile_and_after_minor_consent_withdrawal(content):
    identity, client, actors, body = content
    headers = actors["learner"]
    key = str(uuid4())
    result = create(client, headers, key=key)
    assert result.status_code == 201, result.text
    saved = result.json()
    assert saved["kind"] == "EXPORT" and saved["status"] == "QUEUED"
    assert saved["reviewed_at"] is None
    assert saved["retention_policy"] == "SIX_YEARS_AFTER_COMPLETION"
    assert create(client, headers, key=key).json() == saved
    assert create(client, headers).json() == saved
    assert create(client, headers, "DELETE", key).status_code == 409
    assert (
        client.patch(
            "/api/v1/me",
            headers=headers,
            json={
                "display_name": "Synthetic minor",
                "birth_date": "2010-01-01",
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
                "consent_type": "WITHDRAW",
                "policy_version": identity.settings.consent_policy_version,
                "affirmative": True,
            },
        ).status_code
        == 200
    )
    deletion = create(client, headers, "DELETE")
    assert deletion.status_code == 201, deletion.text
    assert client.get("/api/v1/sessions/active", headers=headers).status_code == 403
    assert client.get("/api/v1/me/data-requests", headers=headers).json()["data"]
    assert client.get(f"/api/v1/me/data-requests/{saved['id']}", headers=headers).json() == saved
    # Intake is not erasure: authentication and prior evidence remain available.
    assert client.get("/api/v1/me", headers=headers).status_code == 200
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(DataRequest)) == 2
        assert (
            db.scalar(
                select(func.count())
                .select_from(AuditLog)
                .where(AuditLog.action == "data_request.created")
            )
            == 2
        )
        events = list(
            db.scalars(select(IdentityEvent).where(IdentityEvent.type == "data_request.created"))
        )
        assert len(events) == 2 and all(set(e.payload) == {"request_id"} for e in events)


def test_ownership_roles_bounds_and_fresh_identity(content):
    identity, client, actors, _ = content
    saved = create(client, actors["learner"]).json()
    path = f"/api/v1/me/data-requests/{saved['id']}"
    assert create(client, {}).status_code == 401
    assert client.get(path, headers=actors["other"]).status_code == 404
    assert client.get(path, headers=actors["admin"]).status_code == 404
    assert client.get("/api/v1/me/data-requests", headers=actors["other"]).json()["data"] == []
    for role in ["learner", "author", "reviewer", "support"]:
        assert client.get("/api/v1/admin/data-requests", headers=actors[role]).status_code == 403
        assert claim(client, actors[role], saved["id"]).status_code == 403
    for limit in [0, 51]:
        assert (
            client.get(
                f"/api/v1/me/data-requests?limit={limit}", headers=actors["learner"]
            ).status_code
            == 422
        )
    now = identity.clock()
    identity.clock = lambda: now + timedelta(minutes=10)
    assert create(client, actors["learner"], "DELETE").json()["error"]["code"] == "REAUTH_REQUIRED"
    assert client.get(path, headers=actors["learner"]).status_code == 200
    assert client.get("/api/v1/admin/data-requests", headers=actors["admin"]).status_code == 401
    assert claim(client, actors["admin"], saved["id"]).status_code == 401


def test_review_audit_retries_and_immutable_evidence(content):
    identity, client, actors, _ = content
    saved = create(client, actors["learner"]).json()
    key = str(uuid4())
    response = claim(client, actors["admin"], saved["id"], key)
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "IN_REVIEW"
    assert claim(client, actors["admin"], saved["id"], key).json() == response.json()
    assert claim(client, actors["admin"], saved["id"]).json() == response.json()
    other = create(client, actors["learner"], "DELETE").json()
    assert claim(client, actors["admin"], other["id"], key).status_code == 409
    own = create(client, actors["admin"]).json()
    assert claim(client, actors["admin"], own["id"]).status_code == 403
    provision(identity, "other@example.invalid", "ADMIN")
    assert claim(client, actors["other"], saved["id"]).status_code == 409
    queue = client.get("/api/v1/admin/data-requests?limit=1", headers=actors["admin"])
    assert queue.status_code == 200 and queue.json()["next_cursor"]
    more = client.get(
        "/api/v1/admin/data-requests",
        headers=actors["admin"],
        params={"cursor": queue.json()["next_cursor"], "limit": 50},
    ).json()
    assert len(more["data"]) == 2
    assert not {"user_id", "actor_id", "authenticated_at"} & queue.json()["data"][0].keys()
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(DataRequestReview)) == 1
        assert (
            db.scalar(
                select(func.count())
                .select_from(AuditLog)
                .where(AuditLog.action == "data_request.review_started")
            )
            == 1
        )
        assert (
            db.scalar(
                select(func.count())
                .select_from(AuditLog)
                .where(AuditLog.action == "data_request.queue_read")
            )
            == 2
        )
    for table in ["data_subject_requests", "data_request_reviews", "data_request_receipts"]:
        with pytest.raises(DBAPIError), identity.engine.begin() as conn:
            conn.execute(text(f"DELETE FROM {table}"))
    with pytest.raises(DBAPIError), identity.engine.begin() as conn:
        conn.execute(text("UPDATE data_subject_requests SET kind='DELETE'"))
    with (
        pytest.raises(DBAPIError, match="Independent administrator"),
        identity.engine.begin() as conn,
    ):
        conn.execute(
            text("""INSERT INTO data_request_reviews(request_id,actor_id,created_at)
            SELECT id,user_id,created_at FROM data_subject_requests WHERE id=:id"""),
            {"id": UUID(other["id"])},
        )


def test_concurrent_creation_claim_and_atomic_failure(content, monkeypatch):
    identity, client, actors, _ = content
    service = DataRequestService(identity)
    token = actors["learner"]["Authorization"][7:]
    key = uuid4()
    body = DataRequestInput(kind="EXPORT", affirmative=True)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: service.create(token, body, key, uuid4()), range(2)))
    assert results[0] == results[1]
    admin = actors["admin"]["Authorization"][7:]
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(lambda _: service.claim(admin, results[0].id, uuid4(), uuid4()), range(2))
        )
    assert results[0] == results[1]
    original = identity.event

    def fail(*args, **kwargs):
        raise RuntimeError("Synthetic outbox failure")

    monkeypatch.setattr(identity, "event", fail)
    assert create(client, actors["learner"], "DELETE").status_code == 500
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(DataRequest)) == 1
        assert db.scalar(select(func.count()).select_from(DataRequestReceipt)) == 3
    monkeypatch.setattr(identity, "event", original)
    deletion = create(client, actors["learner"], "DELETE").json()
    monkeypatch.setattr(identity, "event", fail)
    assert claim(client, actors["admin"], deletion["id"]).status_code == 500
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(DataRequestReview)) == 1


def test_rate_limit_preserves_receipt_and_logout_blocks_access(content):
    _, client, actors, _ = content
    headers = actors["learner"]
    key = str(uuid4())
    saved = create(client, headers, key=key).json()
    for _ in range(9):
        assert create(client, headers).status_code == 201
    assert create(client, headers, "DELETE").status_code == 429
    assert create(client, headers, key=key).json() == saved
    assert client.post("/api/v1/auth/logout-all", headers=headers).status_code == 204
    assert create(client, headers).status_code == 401
    assert client.get(f"/api/v1/me/data-requests/{saved['id']}", headers=headers).status_code == 401
