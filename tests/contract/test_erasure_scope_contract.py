"""No config/URL/label-only bootstrap authority or secret-bearing errors."""

from unittest.mock import Mock

import pytest

from scripts import erasure_scope as scope
from scripts.recovery_containers import OwnedServices
from services.config import Settings


def test_fabricated_issuer_is_rejected_without_database_or_docker(monkeypatch):
    engine = Mock()
    monkeypatch.setattr(scope, "engine_for", engine)
    settings = Settings()
    with pytest.raises(scope.FreshScopeUnavailable, match="^FRESH_ERASURE_SCOPE_UNAVAILABLE$"):
        scope.FreshErasureScope(
            object(),
            OwnedServices("a" * 32, purpose="erasure"),
            settings,
            1,
            2,
            "b" * 64,
            settings.database_url,
        )
    engine.assert_not_called()


def test_provider_or_nonlocal_root_is_refused_before_creating_resources(monkeypatch):
    create = Mock()
    monkeypatch.setattr(scope, "_isolated_database", create)
    for changes in [
        {"model_provider": "local"},
        {"database_url": "postgresql+psycopg://kasoma:synthetic@remote.invalid:55432/kasoma"},
        {"database_url": "postgresql+psycopg://kasoma:synthetic@localhost:5432/kasoma"},
    ]:
        with pytest.raises(ValueError):
            settings = Settings(**changes)
            with scope.fresh_erasure_scope(settings):
                pytest.fail("Unsupported root profile reached the test body")
    create.assert_not_called()


def test_unregistered_issuance_ticket_cannot_adopt_resource_metadata(monkeypatch):
    engine = Mock()
    monkeypatch.setattr(scope, "engine_for", engine)
    owned = OwnedServices("a" * 32, purpose="erasure")
    owned.created["source-db"] = "b" * 64
    with pytest.raises(scope.FreshScopeUnavailable):
        scope._issue(scope._Issuance(), owned, Settings())
    engine.assert_not_called()


def test_mismatched_root_url_is_refused_before_any_sql_connection(monkeypatch):
    engine = Mock()
    monkeypatch.setattr(scope, "engine_for", engine)
    owned = Mock(spec=OwnedServices)
    owned.invocation = "a" * 32
    owned.created = {"source-db": "b" * 64}
    owned.uncertain = []
    owned.purpose = "erasure"
    owned.inspect_owned.return_value = {"State": {"Running": True}}
    owned.port.return_value = 12345
    ticket = scope._Issuance()
    scope._PENDING.add(ticket)
    with pytest.raises(scope.FreshScopeUnavailable):
        scope._issue(ticket, owned, Settings())
    engine.assert_not_called()
