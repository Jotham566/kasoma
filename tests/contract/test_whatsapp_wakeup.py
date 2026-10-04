"""NFR-PERF-002: bounded local wake-up, no broker outage can reject durable intake."""

from services.whatsapp_wakeup import wake


def test_wakeup_uses_only_task_reference_and_bounded_no_retry_policy(settings, monkeypatch):
    calls = []

    class App:
        def __init__(self, *args, **kwargs):
            self.conf = self

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def update(self, **kwargs):
            calls.append(kwargs)

        def send_task(self, name, **kwargs):
            calls.append((name, kwargs))

    monkeypatch.setattr("services.whatsapp_wakeup.Celery", App)
    wake(settings, "synthetic-correlation")
    assert calls[0]["broker_transport_options"]["socket_timeout"] == 0.2
    assert calls[0]["task_publish_retry"] is False
    assert calls[1] == (
        "kasoma.channel_messages",
        {
            "queue": "messaging",
            "retry": False,
            "headers": {"kasoma_correlation_id": "synthetic-correlation"},
        },
    )


def test_unavailable_broker_is_safe_and_does_not_log_diagnostics(settings, monkeypatch, caplog):
    def unavailable(*args, **kwargs):
        raise RuntimeError("CANARY secret broker connection details")

    monkeypatch.setattr("services.whatsapp_wakeup.Celery", unavailable)
    wake(settings, "synthetic-correlation")
    assert "channel.wakeup_failed" in caplog.text
    assert "CANARY" not in caplog.text
