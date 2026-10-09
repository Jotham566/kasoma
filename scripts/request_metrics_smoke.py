"""Verify the running local API publishes minimized metrics into scoped Redis."""

import time
import urllib.request

from services.config import Settings
from services.request_metrics_collector import metric_cache, metric_scope
from services.request_metrics_store import RequestMetricStore


def main() -> None:
    settings = Settings()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with metric_cache(settings) as cache:
        store = RequestMetricStore(cache, metric_scope(settings))
        baseline = store.read()
        before = baseline.observed_end_ns if baseline else None
        for _ in range(20):
            with opener.open("http://127.0.0.1:8000/api/v1/live", timeout=2) as response:
                if response.status != 200:
                    raise RuntimeError("METRIC_SMOKE_API_UNAVAILABLE")
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            current = store.read()
            if (
                current is not None
                and current.estimate.sample_size >= 20
                and current.observed_end_ns is not None
                and (before is None or current.observed_end_ns > before)
            ):
                print(
                    "Request metrics smoke passed: live API collection and scoped Redis projection."
                )
                return
            time.sleep(0.2)
    raise RuntimeError("METRIC_SMOKE_COLLECTION_UNAVAILABLE")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise SystemExit(f"Request metrics smoke failed: {type(exc).__name__}") from None
