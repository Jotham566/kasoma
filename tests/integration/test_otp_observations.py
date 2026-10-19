"""FR-OPS-002/FR-ID-001: real fake-provider calls and restricted aggregate access."""

from uuid import uuid4

import pytest

pytestmark = pytest.mark.integration


def test_disabled_otp_metric_is_explicit_and_admin_only(content):
    service, client, actors, _ = content
    response = client.get("/api/v1/admin/operations", headers=actors["admin"])
    assert response.status_code == 200
    assert response.json()["otp_dispatch"] is None
    assert "OTP_DISPATCH" in response.json()["unavailable_metrics"]
    for role in ["learner", "author", "support"]:
        assert client.get("/api/v1/admin/operations", headers=actors[role]).status_code == 403


def test_actual_api_attempts_exclude_suppressed_sends_and_preserve_failures(identity, caplog):
    from unittest.mock import Mock

    from services.metric_reader import DeltaReader
    from services.otp_metrics import OTPMetrics

    service, client, messages, _ = identity
    reader = DeltaReader()
    metrics = OTPMetrics(reader)
    client.app.state.otp_observer = metrics

    def request(identifier):
        result = client.post(
            "/api/v1/auth/otp/request", json={"identifier": identifier, "device_id": str(uuid4())}
        )
        assert result.status_code == 202
        assert set(result.json()) == {"challenge_id", "message"}
        assert "CANARY" not in result.text and "246810" not in result.text
        return result.json()["challenge_id"]

    try:
        request("otp-observe@example.invalid")
        request("otp-observe@example.invalid")  # Cooldown: no provider invocation.
        request("+999000000001")
        assert metrics.take(reader).counts == (1, 0, 1, 0)
        assert len(messages.messages) == 2
        service.email = Mock()
        service.email.send.side_effect = RuntimeError("CANARY-recipient-code-provider")
        failed = request("otp-failure@example.invalid")
        assert metrics.take(reader).counts == (0, 1, 0, 0)
        denied = client.post(
            "/api/v1/auth/otp/request",
            json={
                "identifier": "guardian-unverified@example.invalid",
                "purpose": "GUARDIAN",
                "device_id": str(uuid4()),
            },
        )
        assert denied.status_code == 401
        assert metrics.take(reader) is None
        assert (
            client.post(
                "/api/v1/auth/otp/verify", json={"challenge_id": failed, "code": "246810"}
            ).status_code
            == 400
        )
        failing_observer = Mock()
        failing_observer.record.side_effect = RuntimeError("CANARY-observer")
        client.app.state.otp_observer = failing_observer
        service.email = messages
        good = request("otp-observer-failure@example.invalid")
        assert (
            client.post(
                "/api/v1/auth/otp/verify", json={"challenge_id": good, "code": "246810"}
            ).status_code
            == 200
        )
        service.sms = Mock()
        service.sms.send.side_effect = RuntimeError("CANARY-provider-and-observer")
        failed_again = request("+999000000003")
        assert (
            client.post(
                "/api/v1/auth/otp/verify", json={"challenge_id": failed_again, "code": "246810"}
            ).status_code
            == 400
        )
        assert "CANARY" not in caplog.text
    finally:
        metrics.shutdown()


def test_real_sdk_redis_admin_snapshot_alert_and_corruption(content, caplog):
    from unittest.mock import Mock

    from fastapi.testclient import TestClient

    from apps.api.main import create_app
    from services.otp_metric_collector import OTPMetricCollector
    from services.otp_metric_store import OTPMetricStore
    from services.request_metrics_collector import metric_cache, metric_scope

    service, _, actors, _ = content
    service.settings.otp_observation_enabled = True
    with metric_cache(service.settings) as cache:
        store = OTPMetricStore(cache, metric_scope(service.settings, purpose="otp-metrics"))
        collector = OTPMetricCollector(store)
        try:
            app = create_app(service.settings, service, otp_metrics_factory=lambda _: collector)
            with TestClient(app) as client:
                assert collector.thread.is_alive()
                assert collector.collect_once()
                assert store.read().counts == (0, 0, 0, 0)
                service.sms = Mock()
                service.sms.send.side_effect = RuntimeError("CANARY-sms-code")
                for contact in ["otp-live-fake@example.invalid", "+999000000002"]:
                    response = client.post(
                        "/api/v1/auth/otp/request",
                        json={"identifier": contact, "device_id": str(uuid4())},
                    )
                    assert response.status_code == 202
                    assert "CANARY" not in response.text
                assert collector.collect_once()
                response = client.get("/api/v1/admin/operations", headers=actors["admin"])
                assert response.status_code == 200
                data = response.json()
                assert data["otp_dispatch"]["observed_attempts"] == 2
                assert data["otp_dispatch"]["email_returned"] == 1
                assert data["otp_dispatch"]["sms_failed"] == 1
                assert data["otp_dispatch"]["best_effort"] is True
                assert "OTP_DISPATCH" not in data["unavailable_metrics"]
                assert "MESSAGING_USAGE" in data["unavailable_metrics"]
                assert "OTP_ADAPTER_FAILURES" in {value["code"] for value in data["alerts"]}
                assert str(collector.source) not in response.text
                token = cache.zrange(store.registry, 0, 0)[0].decode()
                cache.set(store.data_prefix + token, b"CANARY-invalid", keepttl=True)
                response = client.get("/api/v1/admin/operations", headers=actors["admin"])
                assert response.json()["otp_dispatch"] is None
                assert "OTP_ADAPTER_FAILURES" not in {
                    value["code"] for value in response.json()["alerts"]
                }
                assert "CANARY" not in response.text and "CANARY" not in caplog.text
        finally:
            collector.close()
    # The isolated content fixture owns this exact database/schema namespace only.
    with metric_cache(service.settings) as cache:
        keys = list(cache.scan_iter(match=store.prefix + "*", count=300))
        if keys:
            cache.delete(*keys)
