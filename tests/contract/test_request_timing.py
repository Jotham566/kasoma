"""Correlated response-start timing without URLs, credentials or answer data."""

import json
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from apps.api.main import create_app


@pytest.mark.parametrize(
    "method,path,body,status,channel",
    [
        ("GET", "/api/v1/live?answer=CANARY-private", None, 200, "WEB"),
        ("GET", "/CANARY-private", None, 404, "WEB"),
        (
            "GET",
            "/api/v1/webhooks/whatsapp?hub.verify_token=CANARY-private",
            None,
            503,
            "WHATSAPP",
        ),
        (
            "POST",
            "/api/v1/auth/otp/request",
            {"identifier": "CANARY-private", "purpose": "invalid"},
            422,
            "WEB",
        ),
    ],
)
def test_request_timing_is_minimized(
    settings, monkeypatch, caplog, capsys, method, path, body, status, channel
):
    ticks = iter([10.0, 10.0124])
    monkeypatch.setattr("apps.api.main.perf_counter", lambda: next(ticks))
    request_id = str(uuid4())
    with TestClient(create_app(settings)) as client:
        response = client.request(
            method,
            path,
            json=body,
            headers={
                "request_id": request_id,
                "Authorization": "Bearer CANARY-private",
            },
        )
    assert response.status_code == status
    events = [
        json.loads(record.message)
        for record in caplog.records
        if '"event": "api.request"' in record.message
    ]
    assert events == [
        {
            "event": "api.request",
            "correlation_id": request_id,
            "channel": channel,
            "status": status,
            "schema_version": 1,
            "response_start_ms": 13,
        }
    ]
    assert response.headers["request_id"] == request_id
    assert "CANARY" not in caplog.text + capsys.readouterr().out


def test_internal_failure_has_timing_without_exception_details(
    settings, monkeypatch, caplog, capsys
):
    ticks = iter([5.0, 5.0])
    monkeypatch.setattr("apps.api.main.perf_counter", lambda: next(ticks))

    def fail(_):
        raise RuntimeError("CANARY-secret-answer")

    monkeypatch.setattr("apps.api.main.dependency_health", fail)
    with TestClient(create_app(settings)) as client:
        response = client.get("/api/v1/health")
    assert response.status_code == 500
    event = next(
        json.loads(record.message)
        for record in caplog.records
        if '"event": "api.request"' in record.message
    )
    assert event["status"] == 500
    assert event["response_start_ms"] == 0
    assert "CANARY" not in response.text + caplog.text + capsys.readouterr().out


def test_timing_contract_is_additive_for_existing_worker_events():
    schema = json.loads(Path("packages/analytics-schema/foundation-event.schema.json").read_text())
    assert "response_start_ms" not in schema["required"]
    assert schema["properties"]["response_start_ms"]["type"] == "integer"
    assert schema["properties"]["response_start_ms"]["minimum"] == 0
    assert schema["additionalProperties"] is False
