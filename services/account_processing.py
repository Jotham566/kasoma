"""ADR-070 coordination only: no closure, authorization or erasure capability."""

from collections.abc import Iterator
from contextlib import contextmanager
from uuid import UUID

from sqlalchemy import Connection, Engine, text
from sqlalchemy.orm import Session

# A non-secret coordination namespace, computed by PostgreSQL on both sides.
_KEY = (
    "(hashtextextended('kasoma.account-processing.v1:' || "
    "pg_catalog.to_regnamespace(current_schema())::oid::text || ':' || CAST(:subject AS text),0) "
    "| (-9223372036854775808)::bigint)"
)
_SHARED_TRANSACTION = text(
    # Only the fixed module constant is interpolated; subject remains a UUID bind.
    f"SELECT pg_advisory_xact_lock_shared({_KEY}) FROM pg_catalog.pg_namespace "  # nosec B608
    "WHERE oid=pg_catalog.to_regnamespace(current_schema())"
)
_SHARED_SESSION = text(f"SELECT pg_try_advisory_lock_shared({_KEY})")
_RELEASE_SESSION = text(f"SELECT pg_advisory_unlock_shared({_KEY})")


class ProcessingGateUnavailable(RuntimeError):
    def __init__(self) -> None:
        super().__init__("ACCOUNT_PROCESSING_GATE_UNAVAILABLE")


def coordinate(db: Session, subject: UUID) -> None:
    """Call after the existing HMAC account lock, before protected transaction work."""
    if db.execute(_SHARED_TRANSACTION, {"subject": subject}).one_or_none() is None:
        raise ProcessingGateUnavailable()


@contextmanager
def dispatch_gate(engine: Engine, subject: UUID) -> Iterator[None]:
    """Preserve the side-effect-only guard port used by the model gateway."""
    with dispatch_connection(engine, subject):
        yield


@contextmanager
def dispatch_connection(engine: Engine, subject: UUID) -> Iterator[Connection]:
    """One owned idle connection; no transaction, row or HMAC lock spans inference.

    Invalidate on an uncertain acquisition/release: pool rollback does not release
    session advisory locks. This function never reads or grants subject authority.
    """
    with engine.connect() as connection:
        try:
            if connection.scalar(_SHARED_SESSION, {"subject": subject}) is not True:
                raise ProcessingGateUnavailable()
            connection.commit()
        except BaseException:
            connection.invalidate()
            raise
        try:
            # A caller may reuse this same connection for its short recheck, then
            # commit before dispatch. No spare pool checkout is required.
            yield connection
        finally:
            try:
                if connection.in_transaction():
                    connection.rollback()
                if connection.scalar(_RELEASE_SESSION, {"subject": subject}) is not True:
                    raise ProcessingGateUnavailable()
                connection.commit()
            except BaseException:
                connection.invalidate()
                raise
