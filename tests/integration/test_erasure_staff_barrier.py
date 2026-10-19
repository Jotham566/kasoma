"""ADR-061 prerequisite: local provisioning must not add dormant roles to disabled users."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Event
from uuid import uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from services.domain.content import AuditLog
from services.domain.identity import AuthSession, Identifier, User, UserRole
from services.identity import IdentityError
from services.identity_contracts import OTPRequest, OTPVerify
from services.staff import provision

pytestmark = pytest.mark.integration


def test_disabled_identity_cannot_gain_role_but_existing_role_can_be_revoked(identity):
    service, *_ = identity
    email = "disabled-provision@example.invalid"
    challenge = service.request_otp(OTPRequest(identifier=email, device_id=uuid4()), "test", None)
    credentials = service.verify(
        OTPVerify(challenge_id=challenge.challenge_id, code="246810"), None, str(uuid4())
    )
    subject = service.me(credentials.access_token).id
    assert provision(service, email, "SUPPORT_READONLY") == subject
    with Session(service.engine) as db, db.begin():
        db.get(User, subject).status = "DISABLED"
        before = db.scalar(select(func.count()).select_from(AuditLog))
    for role in ["ADMIN", "SUPPORT_READONLY"]:
        with pytest.raises(ValueError, match="Disabled identities"):
            provision(service, email, role)
    with Session(service.engine) as db:
        assert set(db.scalars(select(UserRole.role).where(UserRole.user_id == subject))) == {
            "SUPPORT_READONLY"
        }
        assert db.scalar(select(func.count()).select_from(AuditLog)) == before
    assert provision(service, email, "SUPPORT_READONLY", revoke=True) == subject
    with Session(service.engine) as db:
        assert list(db.scalars(select(UserRole).where(UserRole.user_id == subject))) == []
        assert db.get(User, subject).status == "DISABLED"
        assert db.scalar(select(func.count()).select_from(AuditLog)) == before + 1


def test_existing_login_waits_for_user_barrier_and_rechecks_status(identity, monkeypatch):
    service, _, _, now = identity
    email = "verify-barrier@example.invalid"
    challenge = service.request_otp(OTPRequest(identifier=email, device_id=uuid4()), "test", None)
    credentials = service.verify(
        OTPVerify(challenge_id=challenge.challenge_id, code="246810"), None, str(uuid4())
    )
    subject = service.me(credentials.access_token).id
    now[0] += timedelta(seconds=61)
    challenge = service.request_otp(OTPRequest(identifier=email, device_id=uuid4()), "test", None)
    reached = Event()
    original_lock = service.lock

    def observed_lock(db, key):
        if key == str(subject):
            reached.set()
        original_lock(db, key)

    monkeypatch.setattr(service, "lock", observed_lock)
    # Hold precisely the existing user barrier; no timing sleep or real provider.
    with ThreadPoolExecutor(max_workers=1) as pool:
        with Session(service.engine) as db, db.begin():
            original_lock(db, str(subject))
            before = db.scalar(select(func.count()).select_from(AuthSession))
            future = pool.submit(
                service.verify,
                OTPVerify(challenge_id=challenge.challenge_id, code="246810"),
                None,
                str(uuid4()),
            )
            assert reached.wait(5), "Verification did not coordinate with the user barrier"
            assert not future.done()
            db.get(User, subject).status = "DISABLED"
        with pytest.raises(IdentityError, match="AUTH_REQUIRED"):
            future.result(timeout=5)
    with Session(service.engine) as db:
        assert db.scalar(select(func.count()).select_from(AuthSession)) == before
        assert db.get(User, subject).status == "DISABLED"


def test_concurrently_bound_login_requires_fresh_verification(identity, monkeypatch):
    service, _, _, _ = identity
    email = "new-binding@example.invalid"
    challenge = service.request_otp(OTPRequest(identifier=email, device_id=uuid4()), "test", None)
    original_consume = service.consume
    bound_user = uuid4()

    def bind_before_consume(db, body, purposes, owner):
        # Represents another completed registration after the unbound pre-read.
        with Session(service.engine) as other, other.begin():
            other.add(User(id=bound_user, status="ACTIVE", created_at=service.clock()))
            other.flush()
            other.add(
                Identifier(
                    id=uuid4(),
                    user_id=bound_user,
                    type="EMAIL",
                    normalized_value_encrypted=service.encrypt(email),
                    lookup_hash=service.digest("identifier", email),
                    verified_at=service.clock(),
                )
            )
        return original_consume(db, body, purposes, owner)

    monkeypatch.setattr(service, "consume", bind_before_consume)
    with pytest.raises(IdentityError, match="AUTH_REQUIRED"):
        service.verify(
            OTPVerify(challenge_id=challenge.challenge_id, code="246810"), None, str(uuid4())
        )
    with Session(service.engine) as db:
        assert db.scalar(select(func.count()).select_from(User)) == 1
        assert db.scalar(select(func.count()).select_from(AuthSession)) == 0
        assert db.get(User, bound_user).status == "ACTIVE"
