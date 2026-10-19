"""ADR-068: only exclusively owned synthetic resources; no review-data fallback."""

import json
import signal
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock

import pytest
from pydantic import SecretStr
from sqlalchemy.engine import make_url

from scripts.browser_database import browser_database, cleanup_on_termination
from scripts.recovery_containers import BROWSER_LABEL, LABEL, OwnedServices

INVOCATION = "a" * 32
CID = "b" * 64
IMAGE = "sha256:" + "c" * 64


def standard(settings):
    return settings.model_copy(
        update={
            "app_env": "development",
            "database_url": SecretStr("postgresql+psycopg://kasoma:private@localhost:55432/kasoma"),
        }
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"app_env": "production"},
        {"model_provider": "local"},
        {"email_provider": "mailpit"},
        {"sms_provider": "external"},
        {"whatsapp_provider": "external"},
        {"allow_external_api_calls": True},
        {
            "database_url": SecretStr(
                "postgresql+psycopg://kasoma:private@remote.invalid:55432/kasoma"
            )
        },
        {"database_url": SecretStr("postgresql+psycopg://kasoma:private@localhost:5432/kasoma")},
        {
            "database_url": SecretStr(
                "postgresql+psycopg://kasoma:private@localhost:55432/kasoma?options=x"
            )
        },
    ],
)
def test_unsafe_profile_never_resolves_images_or_creates_resources(settings, monkeypatch, changes):
    create = Mock(side_effect=AssertionError("Must not create"))
    image = Mock(side_effect=AssertionError("Must not resolve"))
    monkeypatch.setattr("scripts.browser_database.OwnedServices", create)
    monkeypatch.setattr("scripts.browser_database.compose_image", image)
    with pytest.raises(ValueError):
        with browser_database(standard(settings).model_copy(update=changes)):
            pytest.fail("No unsafe fixture")
    create.assert_not_called()
    image.assert_not_called()


def mocked_services(monkeypatch):
    services = Mock()
    services.create.return_value = CID
    services.port.return_value = 55433
    services.cleanup.return_value = []
    factory = Mock(return_value=services)
    monkeypatch.setattr("scripts.browser_database.OwnedServices", factory)
    monkeypatch.setattr("scripts.browser_database.uuid4", lambda: SimpleNamespace(hex=INVOCATION))
    monkeypatch.setattr("scripts.browser_database.compose_image", lambda name: IMAGE)
    engine = MagicMock()
    db = engine.connect.return_value.__enter__.return_value
    db.scalar.return_value = "kasoma_browser_" + INVOCATION
    connect = Mock(return_value=engine)
    monkeypatch.setattr("scripts.browser_database.engine_for", connect)
    return services, factory, engine, db, connect


def test_new_private_keys_loopback_url_and_owned_cleanup(settings, monkeypatch, capsys):
    services, factory, engine, _, _ = mocked_services(monkeypatch)
    baseline = standard(settings)
    original = baseline.database_url.get_secret_value()
    with browser_database(baseline) as config:
        url = make_url(config.database_url.get_secret_value())
        assert (url.host, url.port, url.database) == (
            "127.0.0.1",
            55433,
            "kasoma_browser_" + INVOCATION,
        )
        assert url.password != "private" and url.password
        assert config.identity_encryption_key != baseline.identity_encryption_key
        assert config.identity_lookup_key != baseline.identity_lookup_key
        assert config.jwt_signing_key != baseline.jwt_signing_key
        factory.assert_called_once_with(INVOCATION, purpose="browser")
        env = services.create.call_args.args[2]
        assert set(env) == {"POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB"}
        assert env["POSTGRES_PASSWORD"] == url.password
        assert url.password not in repr(config)
    assert baseline.database_url.get_secret_value() == original
    engine.dispose.assert_called_once()
    services.cleanup.assert_called_once()
    events = [json.loads(line) for line in capsys.readouterr().err.splitlines()]
    assert events == [
        {"event": "e2e.database_created", "container_id": CID, "invocation": INVOCATION},
        {"event": "e2e.database_cleanup", "cleanup_failed": []},
    ]


@pytest.mark.parametrize("failure", ["create", "port", "identity", "body"])
def test_partial_startup_and_body_failure_cleanup_only_the_owned_services(
    settings, monkeypatch, failure
):
    services, _, engine, db, _ = mocked_services(monkeypatch)
    if failure == "create":
        services.create.side_effect = RuntimeError("synthetic startup failed")
    elif failure == "port":
        services.port.side_effect = ValueError("port refused")
    elif failure == "identity":
        db.scalar.return_value = "wrong-database"
    with pytest.raises((RuntimeError, ValueError)):
        with browser_database(standard(settings)):
            if failure == "body":
                raise RuntimeError("synthetic body failed")
    services.cleanup.assert_called_once()
    if failure in {"identity", "body"}:
        engine.dispose.assert_called_once()


def test_bounded_startup_withholds_diagnostics_and_cleanup_failure_is_fatal(settings, monkeypatch):
    services, _, _, db, _ = mocked_services(monkeypatch)
    db.scalar.side_effect = RuntimeError("canary-private-db-diagnostic")
    times = iter([0, 31])
    monkeypatch.setattr("scripts.browser_database.monotonic", lambda: next(times))
    with pytest.raises(RuntimeError, match="diagnostics withheld") as failure:
        with browser_database(standard(settings)):
            pytest.fail("No startup")
    assert "canary-private" not in str(failure.value)
    services.cleanup.assert_called_once()
    services, *_ = mocked_services(monkeypatch)
    services.cleanup.return_value = ["kasoma-browser-source-db-" + INVOCATION]
    monkeypatch.setattr("scripts.browser_database.monotonic", lambda: 0)
    with pytest.raises(RuntimeError, match="cleanup failed"):
        with browser_database(standard(settings)):
            pass


def test_browser_purpose_has_distinct_label_and_only_one_component(monkeypatch):
    calls = []

    def command(args, *, environment=None):
        calls.append((args, environment))
        return CID

    monkeypatch.setattr("scripts.recovery_containers.command", command)
    with pytest.raises(ValueError, match="PURPOSE_INVALID"):
        OwnedServices(INVOCATION, purpose="arbitrary")
    services = OwnedServices(INVOCATION, purpose="browser")
    for part in ["destination-db", "source-objects", "destination-objects"]:
        with pytest.raises(ValueError, match="COMPONENT_INVALID"):
            services.create(part, IMAGE, {})
    assert calls == []
    services.create(
        "source-db",
        IMAGE,
        {
            "POSTGRES_USER": "kasoma",
            "POSTGRES_PASSWORD": "canary-private",
            "POSTGRES_DB": "fixture",
        },
    )
    args, env = calls[0]
    assert args[args.index("--name") + 1] == "kasoma-browser-source-db-" + INVOCATION
    assert args[args.index("--label") + 1] == BROWSER_LABEL + "=" + INVOCATION
    assert LABEL + "=" + INVOCATION not in args
    assert "canary-private" not in str(args) and env["POSTGRES_PASSWORD"] == "canary-private"


def test_browser_cannot_adopt_recovery_label_or_cleanup_by_name(monkeypatch):
    calls = []

    def command(args, **kwargs):
        calls.append(args)
        return json.dumps([{"Id": CID, "Config": {"Labels": {LABEL: INVOCATION}}, "Mounts": []}])

    monkeypatch.setattr("scripts.recovery_containers.command", command)
    services = OwnedServices(INVOCATION, {"source-db": CID}, purpose="browser")
    assert services.cleanup() == ["kasoma-browser-source-db-" + INVOCATION]
    assert calls == [["docker", "inspect", CID]]


def test_sigterm_unwinds_owned_cleanup_and_restores_the_previous_handler(settings, monkeypatch):
    services, *_ = mocked_services(monkeypatch)
    previous = signal.getsignal(signal.SIGTERM)
    with pytest.raises(SystemExit) as stopped:
        with cleanup_on_termination(), browser_database(standard(settings)):
            signal.raise_signal(signal.SIGTERM)
    assert stopped.value.code == 0
    assert signal.getsignal(signal.SIGTERM) is previous
    services.cleanup.assert_called_once()


def test_private_body_exception_is_withheld_after_owned_cleanup(settings, monkeypatch, capsys):
    services, *_ = mocked_services(monkeypatch)
    with pytest.raises(RuntimeError, match="diagnostics withheld") as failure:
        with browser_database(standard(settings)):
            raise ValueError("canary-private-body")
    assert "canary-private" not in str(failure.value)
    captured = capsys.readouterr()
    assert "canary-private" not in captured.err + captured.out
    services.cleanup.assert_called_once()
