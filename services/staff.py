"""Identity-owned role checks and explicitly invoked synthetic local provisioning."""

import os
from uuid import UUID, uuid4

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from services.domain.content import AuditLog
from services.domain.identity import Identifier, UserRole
from services.identity import IdentityError, IdentityService, normalize

ROLES = {"CONTENT_AUTHOR", "ACADEMIC_REVIEWER", "ADMIN", "SUPPORT_READONLY"}


def authorize(
    identity: IdentityService, db: Session, token: str, required: set[str], recent: bool = False
) -> tuple[UUID, set[str]]:
    actor = identity.authenticate(db, token, recent=recent).user_id
    roles = set(db.scalars(select(UserRole.role).where(UserRole.user_id == actor)))
    if not roles & required:
        raise IdentityError("FORBIDDEN", 403)
    return actor, roles


def provision(identity: IdentityService, email: str, role: str, revoke: bool = False) -> UUID:
    kind, normalized = normalize(email)
    if (
        identity.settings.app_env != "development"
        or kind != "EMAIL"
        or not normalized.endswith(".invalid")
    ):
        raise ValueError("Local provisioning requires a verified synthetic .invalid email")
    if role not in ROLES:
        raise ValueError("Unsupported staff role")
    with identity.transaction() as db:
        identifier = db.scalar(
            select(Identifier).where(
                Identifier.type == "EMAIL",
                Identifier.lookup_hash == identity.digest("identifier", normalized),
            )
        )
        if identifier is None:
            raise ValueError("Verify the synthetic identity first")
        identity.lock(db, str(identifier.user_id))
        existing = db.get(UserRole, (identifier.user_id, role))
        if revoke:
            db.execute(
                delete(UserRole).where(
                    UserRole.user_id == identifier.user_id, UserRole.role == role
                )
            )
        elif existing is None:
            db.add(UserRole(user_id=identifier.user_id, role=role, granted_at=identity.clock()))
        db.add(
            AuditLog(
                id=uuid4(),
                actor_id=None,
                target_id=identifier.user_id,
                action="staff.role.revoked" if revoke else "staff.role.granted",
                reason=f"Explicit local synthetic bootstrap: {role}",
                request_id=uuid4(),
                created_at=identity.clock(),
                before_hash=None,
                after_hash=None,
            )
        )
        return identifier.user_id


def main() -> None:
    from services.config import Settings
    from services.database import engine_for
    from services.providers import FakeMessagingProvider

    config = Settings()
    engine = engine_for(config)
    fake = FakeMessagingProvider()
    try:
        identity = IdentityService(engine, config, fake, fake)
        user = provision(
            identity,
            os.environ.get("KASOMA_STAFF_EMAIL", ""),
            os.environ.get("KASOMA_STAFF_ROLE", ""),
            os.environ.get("KASOMA_STAFF_REVOKE") == "1",
        )
        print(f"Local synthetic role action audited for {user}.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
