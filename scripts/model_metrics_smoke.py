"""Fixed development fake-provider probe; no learner, inference or cloud call."""

import time
from uuid import uuid4

from apps.worker.main import make_worker
from services.config import Settings
from services.model_metric_store import ModelMetricStore
from services.request_metrics_collector import metric_cache, metric_scope


def main() -> None:
    settings = Settings()
    if settings.app_env != "development":
        raise RuntimeError("MODEL_SMOKE_DEVELOPMENT_ONLY")
    with metric_cache(settings) as cache:
        store = ModelMetricStore(cache, metric_scope(settings, purpose="model-metrics"))
        baseline = store.read()
        before = baseline.observed_end_ns if baseline else None
        make_worker(settings).send_task(
            "kasoma.model_metrics_smoke", args=[str(uuid4())], queue="operations"
        )
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            current = store.read()
            if (
                current is not None
                and current.counts[1] >= 1
                and current.counts[4] >= 1
                and current.counts[5] >= 1
                and current.observed_end_ns is not None
                and (before is None or current.observed_end_ns > before)
            ):
                print(
                    "Model metrics smoke passed: fixed fake worker probe "
                    "and private Redis projection."
                )
                return
            time.sleep(0.2)
    raise RuntimeError("MODEL_SMOKE_COLLECTION_UNAVAILABLE")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise SystemExit(f"Model metrics smoke failed: {type(exc).__name__}") from None
