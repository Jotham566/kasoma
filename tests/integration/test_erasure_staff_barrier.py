"""ADR-061 prerequisite: local provisioning must not add dormant roles to disabled users."""

from uuid import uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from services.domain.content import AuditLog
from services.domain.identity import User, UserRole
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
