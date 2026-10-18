"""FR-GRD-004: bounded wake-up, durable recovery and secret-free failure logging."""

from apps.worker.main import make_worker
from services.short_text_wakeup import wake


def test_wakeup_sends_no_answer_or_identity_and_never_retries(settings, monkeypatch):
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

    monkeypatch.setattr("services.short_text_wakeup.Celery", App)
    wake(settings, "synthetic-correlation")
    config = calls[0]
    assert config["broker_connection_timeout"] == 0.2
    assert config["broker_connection_max_retries"] == 0
    assert config["broker_transport_options"]["socket_timeout"] == 0.2
    assert config["task_publish_retry"] is False
    assert calls[1] == (
        "kasoma.grade_short_text",
        {
            "queue": "grading",
            "retry": False,
            "headers": {"kasoma_correlation_id": "synthetic-correlation"},
        },
    )


def test_broker_failure_logs_no_diagnostics(settings, monkeypatch, caplog):
    def unavailable(*args, **kwargs):
        raise RuntimeError("CANARY confidential broker credential")

    monkeypatch.setattr("services.short_text_wakeup.Celery", unavailable)
    wake(settings, "synthetic-correlation")
    assert "grading.wakeup_failed" in caplog.text and "CANARY" not in caplog.text


def test_periodic_drain_survives_lost_wakeup_with_hard_limit_below_lease(settings):
    worker = make_worker(settings)
    try:
        assert worker.conf.beat_schedule["short-text-grading"] == {
            "task": "kasoma.grade_short_text",
            "schedule": 5.0,
            "options": {"queue": "grading"},
        }
        assert worker.conf.task_routes["kasoma.grade_short_text"] == {"queue": "grading"}
        assert "grading" in worker.conf.task_queues
        task = worker.tasks["kasoma.grade_short_text"]
        assert task.acks_late is True
        assert worker.conf.task_soft_time_limit < worker.conf.task_time_limit < 30
        assert worker.conf.task_publish_retry is False
    finally:
        worker.close()
