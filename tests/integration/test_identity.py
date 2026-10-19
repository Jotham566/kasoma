"""FR-ID-001–005: synthetic API journeys against real PostgreSQL constraints."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from services.domain.identity import (
    AuthSession,
    Challenge,
    Consent,
    Identifier,
    IdentityEvent,
    User,
)
from services.identity import IdentityError
from services.identity_contracts import OTPRequest, OTPVerify

pytestmark = pytest.mark.integration


def request_code(client, identifier="learner@example.invalid", purpose="LOGIN", headers=None):
    response = client.post(
        "/api/v1/auth/otp/request",
        json={"identifier": identifier, "purpose": purpose, "device_id": str(uuid4())},
        headers=headers or {},
    )
    assert response.status_code == 202
    assert "246810" not in response.text
    return response.json()["challenge_id"]


def login(client, identifier="learner@example.invalid"):
    challenge = request_code(client, identifier)
    response = client.post(
        "/api/v1/auth/otp/verify", json={"challenge_id": challenge, "code": "246810"}
    )
    assert response.status_code == 200, response.text
    tokens = response.json()
    return {"Authorization": "Bearer " + tokens["access_token"]}, tokens


def profile(client, headers, birth_date="2008-09-23"):
    subjects = client.get("/api/v1/curriculum/subjects").json()
    assert {s["name"] for s in subjects} == {"Mathematics", "Physics"}
    body = {
        "display_name": "Synthetic learner",
        "birth_date": birth_date,
        "subject_ids": [s["id"] for s in subjects],
    }
    response = client.patch("/api/v1/me", json=body, headers=headers)
    assert response.status_code == 200, response.text
    return response.json(), body


def consent(client, headers, kind, **extra):
    return client.post(
        "/api/v1/me/consents",
        headers=headers | {"Idempotency-Key": str(uuid4())},
        json={
            "consent_type": kind,
            "policy_version": "synthetic-development-v1",
            "affirmative": True,
            **extra,
        },
    )


def test_adult_identity_consent_rotation_revocation_and_privacy(identity, caplog):
    service, client, messages, now = identity
    assert client.get("/api/v1/me").status_code == 401
    headers, tokens = login(client)
    before, body = profile(client, headers)
    assert before["consent_required"] == ["SELF"]  # exactly eighteenth birthday
    assert not before["learning_allowed"]
    response = consent(client, headers, "SELF")
    assert response.json()["learning_allowed"]
    assert service.require_learning(tokens["access_token"])
    assert consent(client, headers, "WITHDRAW").json()["learning_allowed"] is False
    with pytest.raises(IdentityError, match="CONSENT_REQUIRED"):
        service.require_learning(tokens["access_token"])
    assert (
        client.patch("/api/v1/me", json=body | {"role": "ADMIN"}, headers=headers).status_code
        == 422
    )
    assert (
        client.patch(
            "/api/v1/me", json=body | {"subject_ids": [str(uuid4())]}, headers=headers
        ).status_code
        == 422
    )
    rotated = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert rotated.status_code == 200
    fresh = {"Authorization": "Bearer " + rotated.json()["access_token"]}
    assert client.get("/api/v1/me", headers=headers).status_code == 401
    assert client.get("/api/v1/me", headers=fresh).status_code == 200
    assert (
        client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        ).status_code
        == 401
    )
    assert client.get("/api/v1/me", headers=fresh).status_code == 401  # family revoked on reuse
    with Session(service.engine) as db:
        identifier = db.scalar(select(Identifier))
        assert "learner@example.invalid" not in identifier.normalized_value_encrypted
        assert db.scalar(select(User)).display_name != "Synthetic learner"
        events = list(db.scalars(select(IdentityEvent)))
        assert "registration.completed" in {e.type for e in events}
        assert all(set(e.payload) == {"request_id"} for e in events)
        assert all(s.access_hash != tokens["access_token"] for s in db.scalars(select(AuthSession)))
    assert all(
        value not in caplog.text
        for value in ["246810", "learner@example.invalid", tokens["access_token"]]
    )


def test_minor_guardian_binding_assent_policy_and_ownership(identity):
    service, client, messages, now = identity
    headers, tokens = login(client)
    state, body = profile(client, headers, "2010-01-01")
    assert state["consent_required"] == ["ASSENT", "GUARDIAN"]
    assert consent(client, headers, "SELF").status_code == 422
    assert consent(client, headers, "GUARDIAN").status_code == 422
    assert not consent(client, headers, "ASSENT").json()["learning_allowed"]
    assert (
        client.patch(
            "/api/v1/me", json=body | {"birth_date": "2000-01-01"}, headers=headers
        ).status_code
        == 409
    )
    other, _ = login(client, "other@example.invalid")
    assert client.get("/api/v1/me", headers=other).json()["id"] != state["id"]
    assert client.get("/api/v1/me/" + state["id"], headers=other).status_code == 404
    guardian = request_code(client, "guardian@example.invalid", "GUARDIAN", headers)
    # Cannot authenticate or grant another learner's consent with guardian challenge.
    assert (
        client.post(
            "/api/v1/auth/otp/verify", json={"challenge_id": guardian, "code": "246810"}
        ).status_code
        == 400
    )
    profile(client, other, "2011-01-01")
    extra = {
        "guardian_name": "Synthetic guardian",
        "guardian_relationship": "Parent",
        "challenge_id": guardian,
        "code": "246810",
    }
    assert consent(client, other, "GUARDIAN", **extra).status_code == 400
    request_body = {
        "consent_type": "GUARDIAN",
        "policy_version": state["policy_version"],
        "affirmative": True,
        **extra,
    }
    idempotency = headers | {"Idempotency-Key": str(uuid4())}
    for _ in range(2):
        accepted = client.post("/api/v1/me/consents", headers=idempotency, json=request_body)
        assert accepted.status_code == 200, accepted.text
        assert accepted.json()["learning_allowed"]
    assert (
        client.post(
            "/api/v1/me/consents",
            headers=idempotency,
            json=request_body | {"guardian_name": "Changed"},
        ).status_code
        == 409
    )
    with Session(service.engine) as db:
        assert (
            db.scalar(
                select(func.count()).select_from(Consent).where(Consent.consent_type == "GUARDIAN")
            )
            == 1
        )
    service.settings.consent_policy_version = "synthetic-development-v2"
    assert not client.get("/api/v1/me", headers=headers).json()["learning_allowed"]
    assert consent(client, headers, "ASSENT").status_code == 409


def test_otp_expiry_attempts_single_use_limits_and_generic_response(identity):
    service, client, messages, now = identity
    challenge = request_code(client)
    suppressed = request_code(client)
    assert len(messages.messages) == 1
    for _ in range(5):
        assert (
            client.post(
                "/api/v1/auth/otp/verify", json={"challenge_id": challenge, "code": "000000"}
            ).status_code
            == 400
        )
    assert (
        client.post(
            "/api/v1/auth/otp/verify", json={"challenge_id": challenge, "code": "246810"}
        ).status_code
        == 429
    )
    now[0] += timedelta(seconds=61)
    expiring = request_code(client)
    now[0] += timedelta(minutes=10)
    assert (
        client.post(
            "/api/v1/auth/otp/verify", json={"challenge_id": expiring, "code": "246810"}
        ).status_code
        == 400
    )
    headers, tokens = login(client, "verified@example.invalid")
    with Session(service.engine) as db:
        used = db.scalar(select(Challenge).where(Challenge.consumed_at.is_not(None)))
        used_id = str(used.id)
    assert (
        client.post(
            "/api/v1/auth/otp/verify", json={"challenge_id": used_id, "code": "246810"}
        ).status_code
        == 400
    )
    existing = client.post(
        "/api/v1/auth/otp/request",
        json={"identifier": "verified@example.invalid", "device_id": str(uuid4())},
    )
    unknown = client.post(
        "/api/v1/auth/otp/request",
        json={"identifier": "unknown@example.invalid", "device_id": str(uuid4())},
    )
    assert existing.status_code == unknown.status_code == 202
    assert existing.json()["message"] == unknown.json()["message"]
    assert suppressed


def test_linking_requires_recent_auth_and_does_not_duplicate_user(identity):
    service, client, messages, now = identity
    headers, tokens = login(client)
    first_id = client.get("/api/v1/me", headers=headers).json()["id"]
    challenge = request_code(client, "+256700000001", "LINK", headers)
    linked = client.post(
        "/api/v1/auth/otp/verify",
        headers=headers,
        json={"challenge_id": challenge, "code": "246810", "purpose": "LINK"},
    )
    assert linked.status_code == 200, linked.text
    assert client.get("/api/v1/me", headers=headers).json()["identifier_count"] == 2
    now[0] += timedelta(seconds=61)
    phone_headers, _ = login(client, "+256700000001")
    assert client.get("/api/v1/me", headers=phone_headers).json()["id"] == first_id
    assert client.post("/api/v1/auth/logout", headers=phone_headers).status_code == 204
    assert client.get("/api/v1/me", headers=headers).status_code == 200
    now[0] += timedelta(minutes=10)
    response = client.post(
        "/api/v1/auth/otp/request",
        headers=headers,
        json={"identifier": "new@example.invalid", "purpose": "LINK", "device_id": str(uuid4())},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "REAUTH_REQUIRED"
    assert client.post("/api/v1/auth/logout-all", headers=headers).status_code == 204
    assert client.get("/api/v1/me", headers=headers).status_code == 401


@pytest.mark.parametrize("existing", [False, True])
def test_concurrent_verification_only_one_wins(identity, existing):
    service, client, messages, now = identity
    if existing:
        login(client, "race@example.invalid")
        now[0] += timedelta(seconds=61)
    challenge = service.request_otp(
        OTPRequest(identifier="race@example.invalid", device_id=uuid4()), "peer", None
    )

    def verify_once(_):
        try:
            service.verify(
                OTPVerify(challenge_id=challenge.challenge_id, code="246810"), None, str(uuid4())
            )
            return "ok"
        except IdentityError as error:
            return error.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(verify_once, range(2))) == ["OTP_INVALID", "ok"]
    with Session(service.engine) as db:
        assert db.scalar(select(func.count()).select_from(User)) == 1


def test_device_and_peer_send_limits_and_provider_failure(identity):
    service, client, messages, now = identity
    device = uuid4()
    for index in range(11):
        service.request_otp(
            OTPRequest(identifier=f"device-{index}@example.invalid", device_id=device),
            "peer-a",
            None,
        )
    assert len(messages.messages) == 10
    # A changed device cannot escape the independent peer quota.
    for index in range(21):
        service.request_otp(
            OTPRequest(identifier=f"peer-{index}@example.invalid", device_id=uuid4()),
            "peer-b",
            None,
        )
    assert len(messages.messages) == 30

    class FailedProvider:
        def send(self, recipient, body):
            raise RuntimeError("CANARY provider credentials")

    service.email = FailedProvider()
    failed = service.request_otp(
        OTPRequest(identifier="failure@example.invalid", device_id=uuid4()), "peer-c", None
    )
    with pytest.raises(IdentityError, match="OTP_INVALID"):
        service.verify(
            OTPVerify(challenge_id=failed.challenge_id, code="246810"), None, str(uuid4())
        )


def test_session_expiry_and_existing_identity_collision(identity):
    service, client, messages, now = identity
    first, first_tokens = login(client)
    second, _ = login(client, "second@example.invalid")
    now[0] += timedelta(seconds=61)
    link = request_code(client, "second@example.invalid", "LINK", first)
    result = client.post(
        "/api/v1/auth/otp/verify",
        headers=first,
        json={"challenge_id": link, "code": "246810", "purpose": "LINK"},
    )
    assert result.status_code == 409
    assert client.get("/api/v1/me", headers=first).json()["identifier_count"] == 1
    now[0] += timedelta(minutes=15)
    assert client.get("/api/v1/me", headers=first).status_code == 401
    assert client.get("/api/v1/me", headers=second).status_code == 401
    now[0] += timedelta(days=30)
    assert (
        client.post(
            "/api/v1/auth/refresh", json={"refresh_token": first_tokens["refresh_token"]}
        ).status_code
        == 401
    )
