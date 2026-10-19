"""Dedicated least-privilege maintenance consumer; no normal API/worker credentials."""

import os
from pathlib import Path
from typing import Any

from celery import Celery
from celery.app.trace import setup_worker_optimizations
from celery.loaders.app import AppLoader
from sqlalchemy.engine import make_url

from services.export_retirement import QUEUE, TASK_NAME, execute
from services.export_retirement_config import CONFIG_PATH, ExecutorSettings, load_executor
from services.export_retirement_observations import Observation, record
from services.observability import correlation_id, emit


def make_retirement_worker(settings: ExecutorSettings) -> Celery:
    app = Celery(
        "kasoma-retirement",
        broker=settings.redis_url.get_secret_value(),
        loader=RetirementLoader,
        set_as_current=False,
    )
    app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        task_ignore_result=True,
        timezone="UTC",
        enable_utc=True,
        task_default_queue=QUEUE,
        task_queues={QUEUE: {}},
        task_soft_time_limit=12,
        task_time_limit=15,
        task_publish_retry=False,
        broker_connection_retry_on_startup=True,
        worker_hijack_root_logger=False,
    )

    register(app, settings)
    return app


def register(app: Celery, settings: ExecutorSettings) -> None:
    @app.task(shared=False, name=TASK_NAME, queue=QUEUE, acks_late=True, bind=True)  # type: ignore[untyped-decorator]
    def retire(task: Any) -> dict[str, object]:
        request = correlation_id((task.request.headers or {}).get("kasoma_correlation_id"))
        if not settings.enabled:
            return {"status": "DISABLED"}
        database = (
            make_url(settings.database_url.get_secret_value()).database
            if settings.database_url
            else None
        )
        scope = (database, settings.namespace) if database is not None else None
        try:
            result, confirmed_scope = execute(settings)
        except Exception:
            if scope and scope[0]:
                record(settings.redis_url.get_secret_value(), scope, Observation(status="FAILED"))
            emit("export.retirement.failed", request, "WORKER", 503)
            raise RuntimeError("Retirement task unavailable; diagnostics withheld") from None
        if confirmed_scope:
            record(
                settings.redis_url.get_secret_value(),
                confirmed_scope,
                Observation(
                    status=result.status,
                    removed=sum(result.removed.model_dump().values()),
                    examined=result.examined,
                    exhausted=result.exhausted,
                ),
            )
        emit("export.retirement.completed", str(result.batch_id or request), "WORKER", 200)
        # The SQL batch UUID is a correlation identity, never a source/user identifier.
        return result.model_dump(mode="json")

    # A private consumer must not inherit unrelated shared tasks imported elsewhere.
    for name in list(app.tasks):
        if name != TASK_NAME:
            app.tasks.unregister(name)


def restore_private_tasks(sender: Any = None, **kwargs: Any) -> None:
    # Billiard spawn reconstructs the Celery app from configuration, not its task
    # closures. Re-register only on this private app, never via global shared_task.
    if sender is not None and sender.main == "kasoma-retirement" and TASK_NAME not in sender.tasks:
        try:
            settings = load_executor(
                Path(os.environ.get("KASOMA_RETIREMENT_CONFIG", str(CONFIG_PATH)))
            )
            register(sender, settings)
        except Exception:
            raise RuntimeError(
                "Private worker initialization refused; diagnostics withheld"
            ) from None


class RetirementLoader(AppLoader):  # type: ignore[misc]
    """Reconstruct only the private app's registry after native process spawning."""

    def import_default_modules(self) -> Any:
        modules = super().import_default_modules()
        restore_private_tasks(self.app)
        return modules

    def init_worker_process(self) -> None:
        setup_worker_optimizations(self.app)
