import json
import logging
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from apps.api.main import create_app
from apps.worker.main import make_worker
from services.config import Settings, require_local
from services.health import Health
from services.observability import correlation_id, emit
from services.providers import FakeMessagingProvider, FakeModelProvider, ModelTask


def test_health_and_correlation(settings, monkeypatch, caplog):
    monkeypatch.setattr(
        "apps.api.main.dependency_health", lambda _: Health(status="ok", database="up", redis="up")
    )
    request_id = str(uuid4())
    with caplog.at_level(logging.INFO, logger="kasoma"), TestClient(create_app(settings)) as client:
        response = client.get("/api/v1/health", headers={"request_id": request_id})
    assert response.status_code == 200
    assert response.headers["request_id"] == request_id
    assert response.json() == {"status": "ok", "api": "up", "database": "up", "redis": "up"}
    assert request_id in caplog.text


def test_degraded_health(settings, monkeypatch):
    monkeypatch.setattr(
        "apps.api.main.dependency_health",
        lambda _: Health(status="degraded", database="down", redis="up"),
    )
    with TestClient(create_app(settings)) as client:
        assert client.get("/api/v1/health").status_code == 503
        assert client.get("/api/v1/live").status_code == 200
        response = client.get("/me")
        assert response.status_code == 404
        assert response.json()["error"]["request_id"] == response.headers["request_id"]


def test_internal_errors_are_redacted(settings, monkeypatch, caplog):
    def fail(_):
        raise RuntimeError("CANARY-answer-token-guardian")

    monkeypatch.setattr("apps.api.main.dependency_health", fail)
    with TestClient(create_app(settings)) as client:
        response = client.get("/api/v1/health")
    assert response.status_code == 500
    assert "CANARY" not in response.text + caplog.text


@pytest.mark.parametrize(
    "patch",
    [
        {"app_env": "production"},
        {"allow_external_api_calls": True},
        {"model_provider": "production"},
        {"model_provider": "gemini-free-eval"},
        {"model_base_url": "https://example.com/v1"},
        {"model_provider": "local"},
        {"sms_provider": "africas_talking"},
        {"jwt_signing_key": ""},
    ],
)
def test_configuration_fails_closed(settings, patch):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **(settings.model_dump() | patch))


def test_configuration_errors_hide_secrets(settings):
    with pytest.raises(ValidationError) as error:
        Settings(
            _env_file=None,
            **(
                settings.model_dump()
                | {
                    "database_url": "postgresql+psycopg://user:CANARY@external.test/db",
                }
            ),
        )
    assert "CANARY" not in str(error.value)


@given(st.text())
def test_untrusted_correlation_is_always_uuid(value):
    normalized = correlation_id(value)
    assert str(UUID(normalized)) == normalized
    assert correlation_id(normalized) == normalized


def test_worker_keeps_web_request_id(settings, caplog):
    app = make_worker(settings)
    app.conf.task_always_eager = True
    request_id = str(uuid4())
    with caplog.at_level(logging.INFO, logger="kasoma"):
        result = (
            app.tasks["kasoma.smoke"].apply(headers={"kasoma_correlation_id": request_id}).get()
        )
    assert result == {"status": "ok", "correlation_id": request_id}
    event = json.loads(
        next(record.message for record in caplog.records if "worker.smoke" in record.message)
    )
    assert event["correlation_id"] == request_id
    assert set(event) == {"event", "correlation_id", "channel", "status", "schema_version"}


def test_fake_providers_are_deterministic():
    model = FakeModelProvider()
    for task in [
        "grade_short_answer",
        "rephrase_explanation",
        "extract_content_candidate",
        "embed_approved_content",
    ]:
        value = ModelTask(task=task, prompt_version="synthetic-v1", text="Synthetic fixture")
        assert model.execute(value) == model.execute(value)
        assert model.execute(value).status == "LOW_CONFIDENCE"
    messages = FakeMessagingProvider()
    assert messages.send("synthetic", "fixture") == "fake-message-1"
    assert messages.messages == [("synthetic", "fixture")]


def test_local_endpoint_rejects_lookalikes():
    for url in ["https://localhost.evil.test", "http://localhost@evil.test", "file:///tmp/test"]:
        with pytest.raises(ValueError):
            require_local(url)


def test_network_guard_blocks_external_socket():
    import socket

    from pytest_socket import SocketBlockedError

    with pytest.raises(SocketBlockedError):
        socket.socket()


def test_log_schema(caplog):
    with caplog.at_level(logging.INFO, logger="kasoma"):
        emit("api.request", str(uuid4()), "WEB", 200)
    assert "schema_version" in caplog.text


def test_seed_scenario_boundary():
    from pathlib import Path

    fixture = json.loads(Path("tests/fixtures/seed-scenarios.json").read_text())
    assert fixture["classification"] == "synthetic"
    assert fixture["academic_release_eligible"] is False
    assert {item["type"] for item in fixture["items"]} == {
        "SINGLE_CHOICE",
        "MULTIPLE_CHOICE",
        "NUMERIC",
        "SHORT_TEXT",
    }
    assert len(fixture["trajectories"]) == 5


def test_queue_adapter_propagates_correlation():
    from unittest.mock import Mock

    from services.jobs import CeleryJobQueue

    app = Mock()
    app.send_task.return_value.id = "job-1"
    request_id = str(uuid4())
    assert CeleryJobQueue(app).smoke(request_id) == "job-1"
    app.send_task.assert_called_once_with(
        "kasoma.smoke", headers={"kasoma_correlation_id": request_id}
    )


def test_unavailable_dependencies_are_safely_reported(settings, monkeypatch):
    from services.health import dependency_health

    class Unavailable:
        def connect(self):
            raise RuntimeError("CANARY-database-secret")

        def dispose(self):
            return None

    monkeypatch.setattr("services.health.engine_for", lambda _: Unavailable())
    result = dependency_health(settings)
    assert result.database == "down"
    assert result.redis == "down"
    assert "CANARY" not in result.model_dump_json()
