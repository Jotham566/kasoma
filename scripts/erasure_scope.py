"""ADR-061 privileged fresh-source proof; never loaded by an API or ordinary worker.

The proof is issued before migrations inside the exclusively created test resource's
lifetime. It cannot be reconstructed from environment variables, labels, a schema
name or a database URL. It grants no SQL capability or erasure activation by itself.
"""

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from weakref import WeakSet

from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.engine import make_url

from scripts.browser_database import (
    _isolated_database,
    pinned_local_docker,
    require_fake_profile,
    require_test_profile,
)
from scripts.recovery_containers import OwnedServices
from services.config import Settings
from services.database import engine_for

_ISSUER = object()


class _Issuance:
    pass


_PENDING: WeakSet[_Issuance] = WeakSet()


class FreshScopeUnavailable(ValueError):
    def __init__(self) -> None:
        super().__init__("FRESH_ERASURE_SCOPE_UNAVAILABLE")


def _bound_source(owned: OwnedServices, settings: Settings, container_id: str) -> str:
    """Validate the exact local resource/URL before opening any SQL connection."""
    try:
        require_fake_profile(settings)
        if (
            owned.purpose != "erasure"
            or owned.created != {"source-db": container_id}
            or owned.uncertain
        ):
            raise FreshScopeUnavailable()
        item = owned.inspect_owned("source-db")
        state = item.get("State")
        if not isinstance(state, dict) or state.get("Running") is not True:
            raise FreshScopeUnavailable()
        url = make_url(settings.database_url.get_secret_value())
        expected = "kasoma_erasure_test_" + owned.invocation
        if (
            url.drivername != "postgresql+psycopg"
            or url.host != "127.0.0.1"
            or url.port != owned.port("source-db")
            or url.database != expected
            or url.query
            or not url.username
            or not url.password
        ):
            raise FreshScopeUnavailable()
        return expected
    except Exception:
        raise FreshScopeUnavailable() from None


@dataclass
class _Lease:
    live: bool = True


@dataclass(frozen=True, eq=False, repr=False)
class FreshErasureScope:
    """A process-local bootstrap proof, bound to an exact resource and its live scope."""

    _issuer: object = field(repr=False)
    _owned: OwnedServices = field(repr=False)
    settings: Settings = field(repr=False)
    database_oid: int
    namespace_oid: int
    _container_id: str = field(repr=False)
    _database_url: SecretStr = field(repr=False)
    nonce: UUID = field(default_factory=uuid4, repr=False)
    _lease: _Lease = field(default_factory=_Lease, init=False, repr=False)

    def __post_init__(self) -> None:
        if self._issuer is not _ISSUER:
            raise FreshScopeUnavailable()

    def verify(self) -> None:
        """Recheck resource and catalog identity, without printing connection details."""
        if (
            self not in _ISSUED
            or not self._lease.live
            or self._issuer is not _ISSUER
            or self._owned.purpose != "erasure"
            or self._owned.created != {"source-db": self._container_id}
            or self._owned.uncertain
            or self.settings.database_url != self._database_url
        ):
            raise FreshScopeUnavailable()
        try:
            expected = _bound_source(self._owned, self.settings, self._container_id)
            engine = engine_for(self.settings)
            try:
                with engine.connect() as db:
                    identity = db.execute(
                        text("""
                      SELECT d.oid,n.oid FROM pg_catalog.pg_database d
                      CROSS JOIN pg_catalog.pg_namespace n
                      WHERE d.datname=current_database() AND d.datname=:database
                        AND n.nspname='public' AND current_schema()='public'
                    """),
                        {"database": expected},
                    ).one_or_none()
                    if identity is None or tuple(identity) != (
                        self.database_oid,
                        self.namespace_oid,
                    ):
                        raise FreshScopeUnavailable()
            finally:
                engine.dispose()
        except Exception:
            raise FreshScopeUnavailable() from None


_ISSUED: WeakSet[FreshErasureScope] = WeakSet()


def _issue(ticket: _Issuance, owned: OwnedServices, settings: Settings) -> FreshErasureScope:
    """Only the fresh creation callback calls this before any application migration."""
    if ticket not in _PENDING:
        raise FreshScopeUnavailable()
    _PENDING.discard(ticket)  # Consume before inspecting/connecting; no replay or adoption.
    if owned.purpose != "erasure" or set(owned.created) != {"source-db"} or owned.uncertain:
        raise FreshScopeUnavailable()
    _bound_source(owned, settings, owned.created["source-db"])
    engine = engine_for(settings)
    try:
        with engine.connect() as db:
            identity = db.execute(
                text("""
              SELECT d.oid,n.oid FROM pg_catalog.pg_database d CROSS JOIN pg_catalog.pg_namespace n
              WHERE d.datname=current_database() AND n.nspname='public'
                AND current_schema()='public'
                AND pg_has_role(current_user,n.nspowner,'USAGE')
                AND pg_has_role(current_user,d.datdba,'USAGE')
            """)
            ).one_or_none()
            # No existing application tables, views, extension schemas or functions
            # are adopted. PostgreSQL's own public/schema catalog is not learner data.
            populated = db.scalar(
                text("""
              SELECT EXISTS(SELECT 1 FROM pg_catalog.pg_class c
                JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace
                WHERE n.nspname NOT IN ('pg_catalog','information_schema')
                  AND n.nspname NOT LIKE 'pg_toast%' AND n.nspname NOT LIKE 'pg_temp%')
                OR EXISTS(SELECT 1 FROM pg_catalog.pg_proc p
                  JOIN pg_catalog.pg_namespace n ON n.oid=p.pronamespace
                  WHERE n.nspname NOT IN ('pg_catalog','information_schema'))
                OR EXISTS(SELECT 1 FROM pg_catalog.pg_namespace n
                  WHERE n.nspname NOT IN ('public','pg_catalog','information_schema')
                    AND n.nspname NOT LIKE 'pg_toast%' AND n.nspname NOT LIKE 'pg_temp%')
            """)
            )
            if identity is None or populated is not False:
                raise FreshScopeUnavailable()
            result = FreshErasureScope(
                _ISSUER,
                owned,
                settings,
                identity[0],
                identity[1],
                owned.created["source-db"],
                settings.database_url,
            )
    except Exception:
        raise FreshScopeUnavailable() from None
    finally:
        engine.dispose()
    _ISSUED.add(result)
    try:
        result.verify()
    except BaseException:
        _ISSUED.discard(result)
        result._lease.live = False
        raise
    return result


@contextmanager
def fresh_erasure_scope(settings: Settings) -> Iterator[FreshErasureScope]:
    """Create a new fake-only source; no caller URL/schema/SQL/cleanup selector."""
    require_test_profile(settings)
    proof: FreshErasureScope | None = None
    ticket = _Issuance()
    _PENDING.add(ticket)

    def attest(owned: OwnedServices, isolated: Settings) -> None:
        nonlocal proof
        proof = _issue(ticket, owned, isolated)

    with pinned_local_docker():
        try:
            with _scope_database(settings, attest) as isolated:
                if proof is None or isolated is not proof.settings:
                    raise FreshScopeUnavailable()
                proof.verify()
                try:
                    yield proof
                finally:
                    _ISSUED.discard(proof)
                    proof._lease.live = False
        finally:
            _PENDING.discard(ticket)
            if proof is not None:
                _ISSUED.discard(proof)
                proof._lease.live = False


@contextmanager
def _scope_database(
    settings: Settings, attest: Callable[[OwnedServices, Settings], None]
) -> Iterator[Settings]:
    yield from _isolated_database(settings, purpose="erasure", attest=attest)
