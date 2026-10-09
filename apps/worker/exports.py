"""ADR-048 dedicated export task registration and scheduling."""

from typing import cast

from celery import Celery
from redis import Redis

from services.config import Settings
from services.database import engine_for
from services.export_cleanup_cursor import CursorCache, sweep_with_cursor
from services.export_processing import process_one
from services.export_storage import PrivateExportStorage
from services.identity import IdentityService
from services.observability import emit
from services.providers import FakeMessagingProvider


def generation(settings: Settings) -> bool:
    try:
        engine = engine_for(settings)
        try:
            fake = FakeMessagingProvider()
            return process_one(
                IdentityService(engine, settings, fake, fake), PrivateExportStorage(settings)
            )
        finally:
            engine.dispose()
    except Exception:
        raise RuntimeError("Personal export worker unavailable; diagnostics withheld") from None


def cleanup(settings: Settings, request_id: str) -> dict[str, int | bool]:
    try:
        engine = engine_for(settings)
        try:
            fake = FakeMessagingProvider()
            with Redis.from_url(
                settings.redis_url.get_secret_value(), socket_connect_timeout=2, socket_timeout=2
            ) as cache:
                result = sweep_with_cursor(
                    IdentityService(engine, settings, fake, fake),
                    PrivateExportStorage(settings),
                    cast(CursorCache, cache),
                )
            emit("export.cleanup.completed", request_id, "WORKER", 503 if result.failures else 200)
            return {
                "removed": result.removed,
                "generations": result.generations,
                "examined": result.examined,
                "failures": result.failures,
                "exhausted": result.exhausted,
            }
        finally:
            engine.dispose()
    except Exception:
        raise RuntimeError("Personal export cleanup unavailable; diagnostics withheld") from None


def register(app: Celery, settings: Settings) -> None:
    # Only a dedicated single-concurrency prefork worker may consume this queue.
    # The normal worker must explicitly consume operations,imports,messaging.
    app.conf.task_queues = {**app.conf.task_queues, "exports": {}}
    app.conf.beat_schedule = {
        **app.conf.beat_schedule,
        "prepare-personal-export": {
            "task": "kasoma.prepare_personal_export",
            "schedule": 15.0,
            "options": {"queue": "exports", "expires": 15},
        },
        "cleanup-personal-exports": {
            "task": "kasoma.cleanup_personal_exports",
            "schedule": 60.0,
            "options": {"queue": "exports", "expires": 60},
        },
    }

    # Spawned macOS children import shared task definitions into their own app registry.
    app.conf.imports = tuple(dict.fromkeys((*app.conf.imports, "apps.worker.export_tasks")))
    from apps.worker import export_tasks  # noqa: F401
