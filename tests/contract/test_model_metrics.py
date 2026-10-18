"""FR-OPS-002: actual private SDK counters, truthful usage and closed bytes."""

from dataclasses import replace
from time import time_ns

import pytest
from opentelemetry.sdk.util.instrumentation import InstrumentationScope

from services.metric_reader import DeltaReader
from services.model_metrics import MAX_COUNT, ModelInterval, ModelMetrics, activate, project
from services.observed_model_gateway import ObservedModelGateway, reported_usage
from services.providers import FakeModelProvider, ModelResult, ModelTask


@pytest.fixture
def metric():
    reader = DeltaReader()
    owned = ModelMetrics(reader)
    activate(owned)
    yield owned, reader
    activate(None)
    owned.shutdown()


def test_sdk_delta_explicit_zero_unknown_and_exception_are_distinct(metric, caplog):
    owned, reader = metric
    assert owned.take(reader) is None
    task = ModelTask(
        task="grade_short_answer", prompt_version="CANARY-prompt", text="CANARY-answer"
    )
    fake = FakeModelProvider(
        [
            ModelResult(
                provider="fake",
                model="fixture-v1",
                status="CANDIDATE",
                input_tokens=100,
                output_tokens=20,
            ),
            ModelResult(
                provider="fake",
                model="fixture-v1",
                status="LOW_CONFIDENCE",
                input_tokens=0,
                output_tokens=0,
            ),
            ModelResult(provider="fake", model="fixture-v1", status="LOW_CONFIDENCE"),
            RuntimeError("CANARY-secret"),
        ]
    )
    gateway = ObservedModelGateway(fake)
    for _ in range(3):
        gateway.execute(task)
    with pytest.raises(RuntimeError, match="^Model gateway unavailable$"):
        gateway.execute(task)
    frame = owned.take(reader)
    assert frame.counts == (1, 2, 1, 2, 100, 20)
    assert ModelInterval.decode(frame.encode()) == frame
    assert b"CANARY" not in frame.encode() and "CANARY" not in caplog.text
    assert owned.take(reader) is None
    assert len(fake.calls) == 4


def test_idle_sdk_start_does_not_backdate_current_batch(metric):
    owned, reader = metric
    owned.record("CANDIDATE", 0, 0)
    owned.take(reader)
    before = time_ns()
    owned.record("LOW_CONFIDENCE", None, None)
    frame = owned.take(reader)
    assert frame.start_ns >= before and frame.counts == (0, 1, 0, 1, 0, 0)


@pytest.mark.parametrize(
    "counts",
    [
        (True, 0, 0, 0, 0, 0),
        (0,) * 5,
        [0] * 6,
        (0, 0, 1, 0, 0, 0),
        (1, 0, 0, 2, 0, 0),
        (1, 0, 0, 1, 1, 0),
        (1, 0, 0, 0, 8193, 0),
        (1, 0, 0, 0, 0, 4097),
        (MAX_COUNT, 1, 0, 0, 0, 0),
        (-1, 0, 0, 0, 0, 0),
    ],
)
def test_interval_rejects_incoherent_and_mutable_counts(counts):
    with pytest.raises(ValueError):
        ModelInterval(1, 2, counts)


@pytest.mark.parametrize(
    "body",
    [
        b"{}",
        b"x" * 1025,
        b'{"v":1,"start_ns":1,"end_ns":2,"counts":[0,0,0,0,0,0],"answer":"CANARY"}',
        b'{"v":1,"v":1,"start_ns":1,"end_ns":2,"counts":[0,0,0,0,0,0]}',
        b'{"v":1,"start_ns":1,"end_ns":2,"counts":[NaN,0,0,0,0,0]}',
    ],
)
def test_decode_rejects_private_unknown_duplicate_and_noncanonical_bytes(body):
    with pytest.raises(ValueError, match="^INVALID_MODEL_INTERVAL$"):
        ModelInterval.decode(body)


def test_projection_rejects_unowned_resource_scope_and_labels(metric):
    owned, reader = metric
    owned.record("CANDIDATE", 1, 2)
    data = reader.take()
    resource = data.resource_metrics[0]
    scope = resource.scope_metrics[0]
    series = scope.metrics[0]
    point = series.data.data_points[0]
    bad_point = replace(point, attributes={"answer": "CANARY"})
    bad_series = replace(series, data=replace(series.data, data_points=[bad_point]))
    bad_scope = replace(scope, metrics=[bad_series, *scope.metrics[1:]])
    bad_resource = replace(resource, scope_metrics=[bad_scope])
    with pytest.raises(ValueError, match="^INVALID_MODEL_POINT$"):
        project(replace(data, resource_metrics=[bad_resource]), owned.start_ns, 1)
    with pytest.raises(ValueError, match="^INVALID_MODEL_SCOPE$"):
        project(
            replace(
                data,
                resource_metrics=[
                    replace(
                        resource,
                        scope_metrics=[
                            replace(
                                scope,
                                scope=InstrumentationScope("CANARY", "1"),
                            )
                        ],
                    )
                ],
            ),
            owned.start_ns,
            1,
        )
    with pytest.raises(ValueError, match="^INCOHERENT_MODEL_COLLECTION$"):
        project(data, owned.start_ns, 2)


def test_missing_one_usage_field_is_unknown_and_closed_observer_cannot_fail_provider(metric):
    owned, reader = metric
    result = ModelResult(provider="fake", model="fixture-v1", status="CANDIDATE", input_tokens=1)
    assert reported_usage(result) == (None, None)
    owned.shutdown()
    gateway = ObservedModelGateway(FakeModelProvider([result]))
    assert (
        gateway.execute(ModelTask(task="grade_short_answer", prompt_version="synthetic", text=""))
        == result
    )


def test_collector_failure_and_shutdown_are_bounded_and_private(caplog):
    from unittest.mock import Mock

    from services.model_metric_collector import ModelMetricCollector

    store = Mock()
    store.pulse.side_effect = RuntimeError("CANARY-credentials")
    store.write.side_effect = RuntimeError("CANARY-answer")
    collector = ModelMetricCollector(store)
    try:
        assert not collector.collect_once()
        collector.metrics.record("CANDIDATE", 1, 2)
        assert not collector.collect_once()
        collector.start()
    finally:
        collector.close()
    assert not collector.thread.is_alive()
    store.cache.close.assert_called_once()
    assert "CANARY" not in caplog.text


def test_ordinary_worker_lifecycle_respects_role_and_environment(monkeypatch):
    from unittest.mock import Mock

    from apps.worker import model_metrics as worker
    from services.config import Settings

    worker.close_model_process()
    factory = Mock()
    monkeypatch.setattr(worker, "create_collector", factory)
    for env, enabled in [("development", False), ("production", True)]:
        monkeypatch.setattr(
            worker,
            "Settings",
            lambda env=env, enabled=enabled: Settings(
                app_env=env, model_observation_enabled=enabled
            ),
        )
        worker.initialize_model_process()
        assert worker._collector is None
    factory.assert_not_called()
    monkeypatch.setattr(
        worker, "Settings", lambda: Settings(app_env="test", model_observation_enabled=True)
    )
    worker.initialize_model_process()
    worker.initialize_model_process()
    factory.assert_called_once()
    factory.return_value.start.assert_called_once()
    worker.close_model_process()
    worker.close_model_process()
    factory.return_value.close.assert_called_once()
    assert worker._collector is None


def test_local_volume_warning_exact_boundary_and_recovery():
    from services.health import Health
    from services.operations import evaluate
    from services.operations_contracts import ModelUsage, OperationThresholds

    health = Health(status="ok", database="up", redis="up")
    limits = OperationThresholds(failed_imports=1, import_age_seconds=300, unresolved_flags=20)
    sample = ModelUsage(
        observed_attempts=99,
        candidate_responses=99,
        fallback_responses=0,
        no_result_attempts=0,
        usage_unknown_attempts=0,
        reported_input_tokens=0,
        reported_output_tokens=0,
        total_input_tokens=0,
        total_output_tokens=0,
        interval_count=1,
        capped=False,
    )
    assert evaluate(health, "up", None, limits, model_metric=sample) == []
    at = sample.model_copy(update={"observed_attempts": 100, "candidate_responses": 100})
    alerts = evaluate(health, "up", None, limits, model_metric=at)
    assert len(alerts) == 1 and alerts[0].code == "MODEL_GATEWAY_VOLUME"
    assert alerts[0].observed == alerts[0].threshold == 100
    assert evaluate(health, "up", None, limits, model_metric=None) == []
    assert evaluate(health, "up", None, limits, model_metric=sample) == []


def test_failed_observer_does_not_change_success_or_log_provider_payload(monkeypatch, caplog):
    from unittest.mock import Mock

    from services import model_metrics

    broken = Mock()
    broken.record.side_effect = RuntimeError("CANARY-secret")
    monkeypatch.setattr(model_metrics, "_active", broken)
    result = ModelResult(provider="fake", model="fixture-v1", status="LOW_CONFIDENCE")
    gateway = ObservedModelGateway(FakeModelProvider([result]))
    assert (
        gateway.execute(ModelTask(task="grade_short_answer", prompt_version="synthetic", text=""))
        == result
    )
    broken.record.assert_called_once_with("LOW_CONFIDENCE", None, None)
    assert "CANARY" not in caplog.text


def test_sdk_rejects_resource_dimensions_and_unowned_nonzero(metric):
    from opentelemetry.sdk.resources import Resource

    owned, reader = metric
    owned.record("CANDIDATE", 0, 0)
    data = reader.take()
    resource = data.resource_metrics[0]
    private_resource = replace(
        resource, resource=Resource({"service.name": "kasoma-worker-model", "actor": "CANARY"})
    )
    with pytest.raises(ValueError, match="^INVALID_MODEL_RESOURCE$"):
        project(replace(data, resource_metrics=[private_resource]), owned.start_ns, 1)
    with pytest.raises(ValueError, match="^UNOWNED_MODEL_OBSERVATION$"):
        project(data, None, 0)
