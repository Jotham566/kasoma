"""Explicit ordinary-worker import; export-only workers do not register this lifecycle."""

from typing import Any
from uuid import UUID

from celery import shared_task
from celery.signals import worker_process_init, worker_process_shutdown, worker_shutdown

from services.config import Settings
from services.model_metric_collector import ModelMetricCollector, create_collector
from services.model_metrics import activate
from services.model_telemetry import RehearsalTelemetry
from services.observed_model_gateway import ObservedModelGateway
from services.providers import FakeModelProvider, ModelResult, ModelTask

_collector: ModelMetricCollector | None = None


def initialize_model_process(**kwargs: Any) -> None:
    global _collector
    if _collector is not None:
        return
    owned: ModelMetricCollector | None = None
    try:
        settings = Settings()
        if not settings.model_observation_enabled or settings.app_env not in {
            "development",
            "test",
        }:
            return
        owned = create_collector(settings)
        owned.start()
        activate(owned.metrics)
        _collector = owned
    except Exception:
        # Observability failure cannot prevent the worker from starting.
        activate(None)
        _collector = None
        if owned is not None:
            try:
                owned.close()
            except Exception:
                return


def close_model_process(**kwargs: Any) -> None:
    global _collector
    owned, _collector = _collector, None
    activate(None)
    if owned is not None:
        try:
            owned.close()
        except Exception:
            return


worker_process_init.connect(initialize_model_process, weak=False)
worker_process_shutdown.connect(close_model_process, weak=False)
worker_shutdown.connect(close_model_process, weak=False)


@shared_task(name="kasoma.model_metrics_smoke", queue="operations", ignore_result=True)  # type: ignore[untyped-decorator]
def model_metrics_smoke(request_id: str) -> None:
    settings = Settings()
    if settings.app_env != "development" or not settings.model_observation_enabled:
        raise RuntimeError("Synthetic metric probe is development-only")
    # Fixed original synthetic observation; no learner, corpus, model or network call.
    fake = FakeModelProvider(
        [
            ModelResult(
                status="LOW_CONFIDENCE",
                provider="fake",
                model="fixture-v1",
                input_tokens=1,
                output_tokens=1,
            )
        ]
    )
    RehearsalTelemetry(UUID(request_id)).execute(
        ObservedModelGateway(fake),
        ModelTask(
            task="grade_short_answer",
            prompt_version="synthetic-short-text-criteria-first-v2",
            text="",
            structured_input={"synthetic_metric_probe": True},
        ),
        1,
    )
