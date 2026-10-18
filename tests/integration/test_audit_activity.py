"""FR-OPS-003: real bounded audit reads without individual record disclosure."""

import os
import subprocess
from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, insert, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.domain.content import AuditLog
from services.staff import provision

pytestmark = pytest.mark.integration
PATH = "/api/v1/admin/audit"


def rows(identity, actions):
    now = identity.clock()
    with identity.engine.begin() as db:
        db.execute(
            insert(AuditLog),
            [
                dict(
                    id=identifier,
                    actor_id=None,
                    target_id=UUID(int=90001),
                    action=action,
                    reason="synthetic confidential reason@example.invalid",
                    request_id=UUID(int=90002),
                    created_at=at,
                    before_hash="synthetic-private-before",
                    after_hash="synthetic-private-after",
                )
                for identifier, action, at in actions
            ],
        )
    return now


def read(client, actors):
    response = client.get(PATH, headers=actors["admin"])
    assert response.status_code == 200, response.text
    return response


def counts(response):
    return {row["category"]: row["count"] for row in response.json()["counts"]}


def test_roles_revocation_rate_and_reads_do_not_write_audit(content):
    identity, client, actors, _ = content
    assert client.get(PATH).status_code == 401
    for role in ["author", "reviewer", "second", "other", "support", "learner"]:
        assert client.get(PATH, headers=actors[role]).status_code == 403
    with Session(identity.engine) as db:
        before = db.scalar(select(func.count()).select_from(AuditLog))
    for _ in range(20):
        read(client, actors)
    assert client.get(PATH, headers=actors["admin"]).status_code == 429
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(AuditLog)) == before
    provision(identity, "admin@example.invalid", "ADMIN", revoke=True)
    assert client.get(PATH, headers=actors["admin"]).status_code == 403


def test_window_boundaries_unknown_actions_and_minimization(content):
    identity, client, actors, _ = content
    baseline = counts(read(client, actors))
    now = identity.clock()
    hidden = "synthetic-sensitive-unknown@example.invalid"
    rows(
        identity,
        [
            (uuid4(), "content.approved", now - timedelta(hours=24)),
            (uuid4(), "content.flag.read", now),
            (uuid4(), hidden, now),
            (uuid4(), "contentXimport.private", now),
            (uuid4(), "content_import.queued", now),
            (uuid4(), "legal_hold.created", now),
            (uuid4(), "data_request.created", now),
            (uuid4(), "staff.role.granted", now),
            (uuid4(), "grading_review.completed", now),
            (uuid4(), "content_import.queued", now - timedelta(hours=24, microseconds=1)),
            (uuid4(), "grading_review.completed", now + timedelta(microseconds=1)),
        ],
    )
    response = read(client, actors)
    observed = counts(response)
    assert observed == baseline | {
        "CONTENT": baseline["CONTENT"] + 1,
        "FLAGS": baseline["FLAGS"] + 1,
        "OTHER": baseline["OTHER"] + 2,
        "IMPORTS": baseline["IMPORTS"] + 1,
        "PRIVACY": baseline["PRIVACY"] + 2,
        "ROLES": baseline["ROLES"] + 1,
        "GRADING_REVIEW": baseline["GRADING_REVIEW"] + 1,
    }
    assert sum(observed.values()) == response.json()["sampled_count"]
    assert response.json()["capped"] is False
    for forbidden in [
        hidden,
        "reason@",
        "synthetic-private",
        str(UUID(int=90001)),
        str(UUID(int=90002)),
    ]:
        assert forbidden not in response.text
    assert set(response.json()) == {
        "window_start",
        "window_end",
        "sampled_count",
        "capped",
        "sample_limit",
        "counts",
        "measure",
    }
    with identity.engine.begin() as db, pytest.raises(DBAPIError):
        db.execute(text("UPDATE audit_log SET action='content.changed'"))
    with identity.engine.begin() as db, pytest.raises(DBAPIError):
        db.execute(text("DELETE FROM audit_log"))


def test_newest_sample_has_exact_cap_and_timestamp_tie_order(content):
    identity, client, actors, _ = content
    baseline = read(client, actors)
    existing = baseline.json()["sampled_count"]
    now = identity.clock() - timedelta(seconds=1)
    rows(
        identity,
        [(UUID(int=i), "content.approved", now) for i in range(1, 10001)]
        + [(UUID(int=0), "secret-excluded-sentinel", now)],
    )
    response = read(client, actors)
    assert response.json()["sampled_count"] == 10000
    assert response.json()["capped"] is True
    observed = counts(response)
    assert sum(observed.values()) == 10000
    assert observed["CONTENT"] == counts(baseline)["CONTENT"] + 10000 - existing
    assert observed["OTHER"] == counts(baseline)["OTHER"]
    assert "secret-excluded" not in response.text


def test_empty_window_after_fresh_admin_sign_in(content):
    from services.identity_contracts import OTPRequest, OTPVerify

    identity, client, actors, _ = content
    assert read(client, actors).json()["sampled_count"] > 0
    future = identity.clock() + timedelta(days=2)
    identity.clock = lambda: future
    challenge = identity.request_otp(
        OTPRequest(identifier="admin@example.invalid", device_id=uuid4()), "fresh-audit", None
    )
    credentials = identity.verify(
        OTPVerify(challenge_id=challenge.challenge_id, code="246810"), None, str(uuid4())
    )
    actors["admin"] = {"Authorization": "Bearer " + credentials.access_token}
    result = read(client, actors)
    assert result.json()["sampled_count"] == 0
    assert result.json()["capped"] is False
    assert counts(result) == dict.fromkeys(counts(result), 0)


@pytest.mark.parametrize("identity", ["0036"], indirect=True)
def test_additive_upgrade_keeps_existing_audit_and_immutable_guards(content):
    identity, client, actors, _ = content
    before = read(client, actors).json()
    for _ in range(2):
        subprocess.run(
            ["uv", "run", "--frozen", "alembic", "-c", "apps/api/alembic.ini", "upgrade", "head"],
            check=True,
            capture_output=True,
            env=os.environ | {"DATABASE_URL": identity.settings.database_url.get_secret_value()},
        )
    assert read(client, actors).json() == before
    with identity.engine.connect() as db:
        assert db.scalar(text("SELECT to_regclass('ix_audit_activity_window')")) is not None
