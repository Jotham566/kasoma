"""FR-ID-006/BR-010: minimized and audited review, with no destructive side effects."""

from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from services.database import Base
from services.domain.content import AuditLog
from services.domain.data_requests import DataRequest
from services.domain.identity import Challenge
from services.identity_contracts import OTPRequest
from services.staff import provision
from tests.integration.test_assessment import answer, next_item, start
from tests.integration.test_assessment import assessment as assessment_fixture
from tests.integration.test_data_requests import claim, create

pytestmark = pytest.mark.integration
assessment = assessment_fixture


def get(client, headers, target):
    return client.get(f"/api/v1/admin/data-requests/{target}/deletion-preview", headers=headers)


def source(result, name, policy=None):
    return next(
        s
        for s in result["sources"]
        if s["source"] == name and (not policy or s["retention"] == policy)
    )


def snapshot(engine):
    with Session(engine) as db:
        return {
            name: list(db.execute(select(table).order_by(*table.primary_key.columns)))
            for name, table in Base.metadata.tables.items()
            if name not in {"audit_log", "identity_rate_buckets"}
        }


def test_independent_claimant_only_fresh_admin_and_request_kind(content):
    identity, client, actors, _ = content
    target = create(client, actors["learner"], "DELETE").json()["id"]
    assert get(client, {}, target).status_code == 401
    for role in ["learner", "author", "reviewer", "support"]:
        assert get(client, actors[role], target).status_code == 403
    assert get(client, actors["admin"], str(uuid4())).status_code == 404
    assert (
        get(client, actors["admin"], target).json()["error"]["code"] == "REVIEW_OWNERSHIP_REQUIRED"
    )
    assert claim(client, actors["admin"], target).status_code == 200
    provision(identity, "other@example.invalid", "ADMIN")
    assert get(client, actors["other"], target).status_code == 403
    own = create(client, actors["admin"], "DELETE").json()["id"]
    assert get(client, actors["admin"], own).json()["error"]["code"] == "SELF_REVIEW_FORBIDDEN"
    exported = create(client, actors["learner"]).json()["id"]
    assert get(client, actors["admin"], exported).json()["error"]["code"] == "DELETE_REQUIRED"
    now = identity.clock()
    identity.clock = lambda: now + timedelta(minutes=10)
    assert get(client, actors["admin"], target).status_code == 401
    identity.clock = lambda: now
    assert client.post("/api/v1/auth/logout-all", headers=actors["admin"]).status_code == 204
    assert get(client, actors["admin"], target).status_code == 401


def test_preview_without_decryption_is_count_only_audited_and_non_destructive(
    assessment, monkeypatch
):
    identity, client, actors, _, _, plan = assessment
    learner = actors["learner"]
    session = start(client, learner, plan).json()["id"]
    assert answer(client, learner, session, next_item(client, learner, session)).status_code == 200
    target = create(client, learner, "DELETE").json()["id"]
    assert claim(client, actors["admin"], target).status_code == 200
    before = snapshot(identity.engine)

    def forbidden(*args):
        raise AssertionError("Preview must not decrypt personal data")

    original_decrypt = identity.decrypt
    monkeypatch.setattr(identity, "decrypt", forbidden)
    result = get(client, actors["admin"], target)
    assert result.status_code == 200, result.text
    view = result.json()
    assert view["execution_enabled"] is False
    assert source(view, "user_identifiers")["count"] == 1
    assert source(view, "account_erasure_jobs", "SIX_YEARS_AFTER_COMPLETION")["count"] == 0
    assert source(view, "account_erasure_jobs", "STAFF_PROVENANCE_REVIEW")["count"] == 0
    assert source(view, "account_erasure_plans")["retention"] == "TRANSIENT_EXPIRY"
    assert source(view, "attempts")["count"] == 1
    assert source(view, "grades")["count"] == 1
    assert source(view, "session_items")["count"] == 5
    assert source(view, "mastery_evidence")["count"] == 1
    assert source(view, "consent_records")["retention"] == "SIX_YEARS_AFTER_CLOSURE_OR_WITHDRAWAL"
    assert source(view, "data_subject_requests")["retention"] == "SIX_YEARS_AFTER_COMPLETION"
    assert "STAFF_RECORDS_REQUIRE_REVIEW" not in view["blockers"]
    for forbidden_value in [
        "learner@example.invalid",
        "Synthetic learner",
        "Alpha",
        "246810",
        "access_hash",
        "birth_date",
    ]:
        assert forbidden_value not in result.text
    assert result.headers["cache-control"] == "no-store"
    assert snapshot(identity.engine) == before
    with Session(identity.engine) as db:
        assert (
            db.scalar(
                select(func.count())
                .select_from(AuditLog)
                .where(AuditLog.action == "data_request.deletion_previewed")
            )
            == 1
        )
        assert db.get(DataRequest, UUID(target)).completed_at is None
    monkeypatch.setattr(identity, "decrypt", original_decrypt)
    assert client.get(f"/api/v1/sessions/{session}/next-item", headers=learner).status_code == 200


def test_unbound_login_challenges_and_lower_bound_counts(content, monkeypatch):
    import services.deletion_preview as module

    identity, client, actors, _ = content
    target = create(client, actors["learner"], "DELETE").json()["id"]
    assert claim(client, actors["admin"], target).status_code == 200
    now = identity.clock()
    identity.clock = lambda: now + timedelta(seconds=61)
    challenge = identity.request_otp(
        OTPRequest(identifier="learner@example.invalid", device_id=uuid4()), "preview", None
    )
    with Session(identity.engine) as db:
        assert db.get(Challenge, challenge.challenge_id).user_id is None
    # Another learner's bound guardian challenge must not be attributed by hash alone.
    other_id = UUID(client.get("/api/v1/me", headers=actors["other"]).json()["id"])
    with Session(identity.engine) as db, db.begin():
        db.add(
            Challenge(
                id=uuid4(),
                purpose="GUARDIAN",
                user_id=other_id,
                policy_version=identity.settings.consent_policy_version,
                type="EMAIL",
                lookup_hash=identity.digest("identifier", "learner@example.invalid"),
                encrypted_identifier=identity.encrypt("learner@example.invalid"),
                code_hash=identity.digest("otp", "synthetic"),
                attempts=0,
                expires_at=identity.clock() + timedelta(minutes=10),
                consumed_at=None,
            )
        )
    exact = get(client, actors["admin"], target)
    assert exact.status_code == 200, exact.text
    assert source(exact.json(), "otp_challenges")["count"] == 2
    monkeypatch.setattr(module, "COUNT_LIMIT", 1)
    result = get(client, actors["admin"], target)
    assert result.status_code == 200, result.text
    row = source(result.json(), "otp_challenges")
    assert row["count"] == 1 and row["at_least"] is True
    assert source(result.json(), "user_identifiers")["at_least"] is False


def test_staff_provenance_after_role_revocation_and_preview_rate_limit(content):
    identity, client, actors, body = content
    from tests.integration.test_content import create as create_content

    assert create_content(client, actors, body)["id"]
    target = create(client, actors["author"], "DELETE").json()["id"]
    assert claim(client, actors["admin"], target).status_code == 200
    provision(identity, "author@example.invalid", "CONTENT_AUTHOR", revoke=True)
    provision(identity, "author@example.invalid", "ACADEMIC_REVIEWER", revoke=True)
    result = get(client, actors["admin"], target)
    assert result.status_code == 200, result.text
    assert source(result.json(), "user_roles")["count"] == 0
    assert source(result.json(), "items")["count"] == 1
    assert "STAFF_RECORDS_REQUIRE_REVIEW" in result.json()["blockers"]
    for _ in range(9):
        assert get(client, actors["admin"], target).status_code == 200
    assert get(client, actors["admin"], target).status_code == 429


def test_failed_inventory_or_audit_never_returns_partial_preview(content, monkeypatch):
    import services.deletion_preview as module

    identity, client, actors, _ = content
    target = create(client, actors["learner"], "DELETE").json()["id"]
    assert claim(client, actors["admin"], target).status_code == 200
    before = snapshot(identity.engine)

    def fail(*args):
        raise RuntimeError("Synthetic preview failure")

    original = module.inventory
    monkeypatch.setattr(module, "inventory", fail)
    assert get(client, actors["admin"], target).status_code == 500
    monkeypatch.setattr(module, "inventory", original)
    monkeypatch.setattr(module.DataRequestService, "audit", fail)
    assert get(client, actors["admin"], target).status_code == 500
    assert snapshot(identity.engine) == before
    with Session(identity.engine) as db:
        assert (
            db.scalar(
                select(func.count())
                .select_from(AuditLog)
                .where(AuditLog.action == "data_request.deletion_previewed")
            )
            == 0
        )
