"""Calendar retention is independent of the 24-hour disposable retry copy."""

from datetime import UTC, datetime

from apps.worker.main import make_worker
from services.config import Settings
from services.data_exports import retention_due


def test_calendar_deadline_and_bounded_periodic_cleanup():
    assert retention_due(datetime(2024, 2, 29, 12, tzinfo=UTC)) == datetime(
        2030, 2, 28, 12, tzinfo=UTC
    )
    worker = make_worker(Settings())
    assert worker.conf.beat_schedule["expire-exports"]["schedule"] == 300
    assert "kasoma.expire_exports" in worker.tasks
    worker.close()
