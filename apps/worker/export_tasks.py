"""Importable shared task definitions for native spawn and Linux prefork workers."""

from typing import Any

from celery import current_app, shared_task
from celery.app.trace import setup_worker_optimizations
from celery.signals import worker_process_init

from apps.worker.exports import cleanup, generation
from services.config import Settings
from services.observability import correlation_id


@worker_process_init.connect(weak=False)  # type: ignore[untyped-decorator]
def initialize_export_process(**kwargs: Any) -> None:
    # Billiard defaults to spawn on macOS. Celery's fork fast-path state is not inherited
    # there, so bind its task registry after the child loader has imported this module.
    setup_worker_optimizations(current_app)


@shared_task(  # type: ignore[untyped-decorator]
    name="kasoma.prepare_personal_export",
    queue="exports",
    acks_late=True,
    soft_time_limit=110,
    time_limit=120,
)
def prepare_export() -> bool:
    return generation(Settings())


@shared_task(  # type: ignore[untyped-decorator]
    name="kasoma.cleanup_personal_exports",
    queue="exports",
    bind=True,
    acks_late=True,
    soft_time_limit=15,
    time_limit=20,
)
def cleanup_exports(task: Any) -> dict[str, int | bool]:
    request_id = correlation_id((task.request.headers or {}).get("kasoma_correlation_id"))
    return cleanup(Settings(), request_id)
