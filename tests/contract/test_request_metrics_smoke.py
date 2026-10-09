"""Smoke failures stay bounded; empty/stale telemetry never counts as acceptance."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from scripts import request_metrics_smoke as smoke


@pytest.mark.parametrize("fresh", [True, False])
def test_smoke_requires_new_nonempty_collection(monkeypatch, settings, fresh, capsys):
    monkeypatch.setattr(smoke, "Settings", lambda: settings)
    monkeypatch.setattr(smoke, "metric_cache", lambda _: MagicMock())
    before = SimpleNamespace(observed_end_ns=1, estimate=SimpleNamespace(sample_size=20))
    after = SimpleNamespace(
        observed_end_ns=2 if fresh else 1, estimate=SimpleNamespace(sample_size=20)
    )
    store = MagicMock()
    store.read.side_effect = [before, after]
    monkeypatch.setattr(smoke, "RequestMetricStore", lambda *_: store)
    http = MagicMock()
    http.return_value.__enter__.return_value.status = 200

    def opener(proxy):
        assert proxy.proxies == {}
        return SimpleNamespace(open=http)

    monkeypatch.setattr(smoke.urllib.request, "build_opener", opener)
    ticks = iter([0, 0, 16])
    monkeypatch.setattr(smoke.time, "monotonic", lambda: next(ticks))
    monkeypatch.setattr(smoke.time, "sleep", lambda _: None)
    if fresh:
        smoke.main()
        assert "smoke passed" in capsys.readouterr().out
    else:
        with pytest.raises(RuntimeError, match="^METRIC_SMOKE_COLLECTION_UNAVAILABLE$"):
            smoke.main()
        assert "passed" not in capsys.readouterr().out
    assert http.call_count == 20
    assert all(call.args == ("http://127.0.0.1:8000/api/v1/live",) for call in http.call_args_list)
    assert all(call.kwargs == {"timeout": 2} for call in http.call_args_list)
