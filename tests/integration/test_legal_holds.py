"""FR-ID-006/BR-010: scoped preservation, authorization, atomic evidence and expiry."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.domain.content import AuditLog
from services.domain.data_requests import DataRequest, LegalHold, LegalHoldReceipt
from services.domain.identity import Consent, IdentityEvent
from services.legal_hold_contracts import HoldInput
from services.legal_holds import LegalHoldService, active
from services.staff import provision
from tests.integration.test_assessment import assessment as assessment_fixture
from tests.integration.test_data_exports import export
from tests.integration.test_data_requests import claim, create
from tests.integration.test_deletion_preview import get as preview
from tests.integration.test_flags import report, saved

assessment = assessment_fixture
pytestmark = pytest.mark.integration


def prepare(content):
    identity, client, actors, *_ = content
    target = create(client, actors["learner"], "DELETE").json()["id"]
    assert claim(client, actors["admin"], target).status_code == 200
    body = {
        "record_type": "DATA_REQUEST",
        "record_id": target,
        "decision_reference": str(uuid4()),
        "reason": "LEGAL_OBLIGATION",
        # Also active under the real database clock for trigger tests.
        "expires_at": (identity.clock() + timedelta(days=365)).isoformat(),
        "affirmative": True,
    }
    return target, body


def path(target):
    return f"/api/v1/admin/data-requests/{target}/holds"


def hold(client, headers, target, body, key=None):
    return client.post(
        path(target), headers=headers | {"Idempotency-Key": key or str(uuid4())}, json=body
    )


def release(client, headers, target, hold_id, body=None, key=None):
    return client.post(
        f"{path(target)}/{hold_id}/release",
        headers=headers | {"Idempotency-Key": key or str(uuid4())},
        json=body or {"decision_reference": str(uuid4()), "affirmative": True},
    )


def test_lifecycle_retries_preview_and_export_boundary(content):
    identity, client, actors, _ = content
    target, body = prepare(content)
    headers = actors["admin"]
    key = str(uuid4())
    response = hold(client, headers, target, body, key)
    assert response.status_code == 201, response.text
    first = response.json()
    assert first["status"] == "ACTIVE"
    assert response.headers["cache-control"] == "no-store"
    assert not {"created_by", "released_by", "user_id", "payload"} & first.keys()
    assert hold(client, headers, target, body, key).json() == first
    equivalent = body | {
        "expires_at": body["expires_at"].replace("12:00:00+00:00", "15:00:00+03:00")
    }
    assert hold(client, headers, target, equivalent, key).json() == first
    assert (
        hold(client, headers, target, body | {"reason": "SECURITY_INVESTIGATION"}, key).status_code
        == 409
    )
    view = preview(client, headers, target).json()
    assert view["active_legal_holds"] == 1 and view["active_holds_at_least"] is False
    assert "ACTIVE_RECORD_HOLDS" in view["blockers"]
    assert "LEGAL_HOLD_COVERAGE_INCOMPLETE" in view["blockers"]
    assert view["execution_enabled"] is False
    receipt = {"decision_reference": str(uuid4()), "affirmative": True}
    release_key = str(uuid4())
    result = release(client, headers, target, first["id"], receipt, release_key)
    assert result.status_code == 200, result.text
    assert result.json()["status"] == "RELEASED"
    assert (
        release(client, headers, target, first["id"], receipt, release_key).json() == result.json()
    )
    assert hold(client, headers, target, body, key).json() == result.json()
    assert release(client, headers, target, first["id"], receipt).status_code == 409
    assert release(client, headers, target, first["id"], receipt, key).status_code == 409
    view = preview(client, headers, target).json()
    assert view["active_legal_holds"] == 0 and "ACTIVE_RECORD_HOLDS" not in view["blockers"]
    assert view["execution_enabled"] is False
    exported = export(client, actors["learner"], create(client, actors["learner"]).json()["id"])
    assert exported.status_code == 200, exported.text
    assert "legal_hold" not in exported.text and first["id"] not in exported.text
    assert body["decision_reference"] not in exported.text
    with Session(identity.engine) as db:
        assert db.get(DataRequest, UUID(target)).completed_at is None
        assert db.scalar(select(func.count()).select_from(LegalHold)) == 1
        assert db.scalar(select(func.count()).select_from(LegalHoldReceipt)) == 2
        events = list(
            db.scalars(select(IdentityEvent).where(IdentityEvent.type.like("legal_hold.%")))
        )
        assert {e.type for e in events} == {"legal_hold.created", "legal_hold.released"}
        assert all(set(e.payload) == {"request_id"} for e in events)
        assert (
            db.scalar(
                select(func.count())
                .select_from(AuditLog)
                .where(AuditLog.action.like("legal_hold.%"))
            )
            == 2
        )


def test_independent_claimant_fresh_auth_and_scope(content):
    identity, client, actors, _ = content
    target, body = prepare(content)
    assert hold(client, {}, target, body).status_code == 401
    for role in ["learner", "author", "reviewer", "support"]:
        assert hold(client, actors[role], target, body).status_code == 403
        assert client.get(path(target), headers=actors[role]).status_code == 403
    provision(identity, "other@example.invalid", "ADMIN")
    assert hold(client, actors["other"], target, body).status_code == 403
    assert client.get(path(target), headers=actors["other"]).status_code == 403
    own = create(client, actors["admin"], "DELETE").json()["id"]
    assert hold(client, actors["admin"], own, body).status_code == 403
    export_id = create(client, actors["learner"]).json()["id"]
    assert hold(client, actors["admin"], export_id, body).status_code == 409
    for record in [own, str(uuid4())]:
        assert (
            hold(client, actors["admin"], target, body | {"record_id": record}).status_code == 404
        )
    created = hold(client, actors["admin"], target, body).json()
    assert release(client, actors["other"], target, created["id"]).status_code == 403
    now = identity.clock()
    identity.clock = lambda: now + timedelta(minutes=10)
    assert client.get(path(target), headers=actors["admin"]).status_code == 401
    assert release(client, actors["admin"], target, created["id"]).status_code == 401
    identity.clock = lambda: now
    provision(identity, "admin@example.invalid", "ADMIN", revoke=True)
    assert hold(client, actors["admin"], target, body).status_code == 403
    assert release(client, actors["admin"], target, created["id"]).status_code == 403
    assert claim(client, actors["other"], own).status_code == 200
    review = preview(client, actors["other"], own).json()
    related = {
        row["source"]: row["count"]
        for row in review["sources"]
        if row["retention"] == "STAFF_PROVENANCE_REVIEW"
    }
    assert related["legal_holds"] == related["legal_hold_receipts"] == 1
    assert "STAFF_RECORDS_REQUIRE_REVIEW" in review["blockers"]


def test_four_record_kinds_foreign_ownership_and_delete_guards(assessment):
    identity, client, actors, *_ = assessment
    attempt = saved(assessment)["attempt_id"]
    flagged = report(client, actors["learner"], attempt).json()["id"]
    target, body = prepare(assessment)
    with Session(identity.engine) as db:
        consent = str(db.scalar(select(Consent.id)))
    for kind, record, table in [
        ("CONSENT", consent, "consent_records"),
        ("ATTEMPT", attempt, "attempts"),
        ("CONTENT_FLAG", flagged, "content_flags"),
        ("DATA_REQUEST", target, "data_subject_requests"),
    ]:
        result = hold(
            client, actors["admin"], target, body | {"record_type": kind, "record_id": record}
        )
        assert result.status_code == 201, result.text
        with Session(identity.engine) as db:
            assert active(db, kind, UUID(record), identity.clock())
        with (
            identity.engine.begin() as db,
            pytest.raises(DBAPIError, match="Record is legally held"),
        ):
            db.execute(text(f"DELETE FROM {table} WHERE id=:id"), {"id": record})
    other = create(client, actors["other"], "DELETE").json()["id"]
    assert claim(client, actors["admin"], other).status_code == 200
    for kind, record in [("CONSENT", consent), ("ATTEMPT", attempt), ("CONTENT_FLAG", flagged)]:
        assert (
            hold(
                client, actors["admin"], other, body | {"record_type": kind, "record_id": record}
            ).status_code
            == 404
        )


def test_expiry_multiple_holds_pagination_and_validation(content):
    identity, client, actors, _ = content
    target, body = prepare(content)
    now = identity.clock()
    assert (
        hold(client, actors["admin"], target, body | {"expires_at": now.isoformat()}).status_code
        == 422
    )
    first = hold(
        client,
        actors["admin"],
        target,
        body | {"expires_at": (now + timedelta(seconds=1)).isoformat()},
    ).json()
    second = hold(
        client,
        actors["admin"],
        target,
        body | {"expires_at": (now + timedelta(seconds=2)).isoformat()},
    ).json()
    page = client.get(path(target) + "?limit=1", headers=actors["admin"]).json()
    assert len(page["data"]) == 1 and page["next_cursor"]
    last = client.get(
        path(target) + f"?limit=1&cursor={page['next_cursor']}", headers=actors["admin"]
    ).json()
    assert last["next_cursor"] is None
    assert {page["data"][0]["id"], last["data"][0]["id"]} == {first["id"], second["id"]}
    assert client.get(path(target) + "?limit=51", headers=actors["admin"]).status_code == 422
    identity.clock = lambda: now + timedelta(seconds=1)
    with Session(identity.engine) as db:
        assert active(db, "DATA_REQUEST", UUID(target), identity.clock())
    assert release(client, actors["admin"], target, first["id"]).status_code == 409
    assert preview(client, actors["admin"], target).json()["active_legal_holds"] == 1
    identity.clock = lambda: now + timedelta(seconds=2)
    with Session(identity.engine) as db:
        assert not active(db, "DATA_REQUEST", UUID(target), identity.clock())
    assert all(
        r["status"] == "EXPIRED"
        for r in client.get(path(target), headers=actors["admin"]).json()["data"]
    )
    assert preview(client, actors["admin"], target).json()["active_legal_holds"] == 0


def test_sql_evidence_immutability_finite_dates_and_ownership(content):
    identity, client, actors, _ = content
    target, body = prepare(content)
    held = hold(client, actors["admin"], target, body).json()["id"]
    other = create(client, actors["other"], "DELETE").json()["id"]
    mutations = [
        "DELETE FROM legal_holds",
        "DELETE FROM legal_hold_receipts",
        "UPDATE legal_hold_receipts SET request_hash='bad'",
        "UPDATE legal_holds SET expires_at=expires_at+interval '1 day'",
        "UPDATE legal_holds SET decision_reference=gen_random_uuid()",
        "UPDATE legal_holds SET record_id=gen_random_uuid()",
        "UPDATE legal_holds SET released_at=created_at",
    ]
    for sql in mutations:
        with identity.engine.begin() as db, pytest.raises(DBAPIError):
            db.execute(text(sql))
    # Bypass the service: SQL still rejects cross-owner, unsupported and infinite holds.
    for changes in [
        {"record_id": other},
        {"record_type": "USER"},
        {"expires_at": "infinity"},
        {"expires_at": "2026-01-01T00:00:00Z"},
        {"created_by": client.get("/api/v1/me", headers=actors["learner"]).json()["id"]},
    ]:
        with Session(identity.engine) as db:
            source = db.get(LegalHold, UUID(held))
            values = {c.name: getattr(source, c.name) for c in LegalHold.__table__.columns}
        values.update(changes | {"id": uuid4()})
        with Session(identity.engine) as db, pytest.raises(DBAPIError):
            db.add(LegalHold(**values))
            db.commit()
    assert release(client, actors["admin"], target, held).status_code == 200
    with identity.engine.begin() as db, pytest.raises(DBAPIError):
        db.execute(text("UPDATE legal_holds SET release_reference=gen_random_uuid()"))


def test_concurrent_retries_and_rollback(content, monkeypatch):
    identity, client, actors, _ = content
    target, body = prepare(content)
    service = LegalHoldService(identity)
    key = uuid4()
    token = actors["admin"]["Authorization"].removeprefix("Bearer ")
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(
                lambda _: service.create(token, UUID(target), HoldInput(**body), key, uuid4()),
                range(2),
            )
        )
    assert results[0].id == results[1].id
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(LegalHold)) == 1
        assert db.scalar(select(func.count()).select_from(LegalHoldReceipt)) == 1

    def fail(*args):
        raise RuntimeError("Synthetic evidence failure")

    monkeypatch.setattr(identity, "event", fail)
    assert hold(client, actors["admin"], target, body).status_code == 500
    assert release(client, actors["admin"], target, str(results[0].id)).status_code == 500
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(LegalHold)) == 1
        assert db.scalar(select(func.count()).select_from(LegalHoldReceipt)) == 1
        assert db.get(LegalHold, results[0].id).released_at is None
        assert (
            db.scalar(
                select(func.count())
                .select_from(AuditLog)
                .where(AuditLog.action.like("legal_hold.%"))
            )
            == 1
        )


def test_bounded_reads_mutations_and_authorized_replay(content):
    identity, client, actors, _ = content
    target, body = prepare(content)
    key = str(uuid4())
    first = hold(client, actors["admin"], target, body, key)
    for _ in range(9):
        assert hold(client, actors["admin"], target, body).status_code == 201
    assert hold(client, actors["admin"], target, body).status_code == 429
    assert hold(client, actors["admin"], target, body, key).json() == first.json()
    for _ in range(60):
        assert client.get(path(target), headers=actors["admin"]).status_code == 200
    assert client.get(path(target), headers=actors["admin"]).status_code == 429
    assert client.post("/api/v1/auth/logout-all", headers=actors["admin"]).status_code == 204
    assert hold(client, actors["admin"], target, body, key).status_code == 401
