"""Private executor configuration and worker boundaries; no live broker/model calls."""

import os
import subprocess
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from apps.worker.retirement import make_retirement_worker
from services.export_retirement import Batch, Removed, execute
from services.export_retirement_config import ExecutorSettings, load_executor


@pytest.mark.parametrize(
    "change",
    [
        {"enabled": True},
        {"app_env": "production"},
        {"database_url": "postgresql+psycopg://user:canary-private@remote.invalid/test"},
        {"database_url": "http://user:canary-private@localhost/test"},
        {
            "database_url": "postgresql+psycopg://user:canary-private@localhost/test?host=remote.invalid"
        },
        {
            "enabled": True,
            "holds_enabled": True,
            "database_url": "postgresql+psycopg://user:canary-private@localhost/kasoma",
        },
    ],
)
def test_private_executor_configuration_rejects_unsafe_or_incomplete_values(change):
    with pytest.raises(ValidationError) as failure:
        ExecutorSettings(**change)
    assert "canary-private" not in str(failure.value)


def test_disabled_executor_has_no_database_side_effects(monkeypatch):
    connect = Mock(side_effect=AssertionError("Must not connect"))
    monkeypatch.setattr("services.export_retirement.executor_engine", connect)
    assert execute(ExecutorSettings()) == (Batch(status="DISABLED"), None)
    connect.assert_not_called()


def test_private_loader_requires_owned_regular0600_file_and_preserves_shared_env(tmp_path):
    path = tmp_path / "executor.env"
    path.write_text("EXPORT_RETIREMENT_ENABLED=false\n")
    path.chmod(0o644)
    with pytest.raises(ValueError, match="private regular"):
        load_executor(path)
    path.chmod(0o600)
    assert load_executor(path).enabled is False
    link = tmp_path / "link.env"
    link.symlink_to(path)
    with pytest.raises(ValueError, match="private regular"):
        load_executor(link)
    assert path.stat().st_uid == os.getuid()


def test_batch_schema_enforces_conservation_and_closed_status():
    with pytest.raises(ValidationError):
        Removed(data_request_receipts=100, data_request_reviews=1)
    for change in [
        {"examined": 201},
        {"status": "PROCESSED"},
        {"examined": 1},
        {"source_id": "forbidden"},
        {"status": "ARBITRARY_DIAGNOSTIC"},
    ]:
        with pytest.raises(ValidationError):
            Batch.model_validate({"status": "DISABLED"} | change)


def test_dedicated_worker_limits_and_no_beat_or_shared_credential(settings, monkeypatch):
    from apps.worker.main import make_worker
    from services.config import Settings
    from services.export_retirement import QUEUE, TASK_NAME

    assert "export_retirement_database_url" not in Settings.model_fields
    normal = make_worker(settings)
    private = make_retirement_worker(ExecutorSettings())
    try:
        assert TASK_NAME not in normal.tasks
        assert set(private.tasks) == {TASK_NAME}
        assert set(private.conf.task_queues) == {QUEUE}
        assert private.conf.task_ignore_result
        assert (private.conf.task_soft_time_limit, private.conf.task_time_limit) == (12, 15)
        assert not private.conf.beat_schedule
        task = private.tasks[TASK_NAME]
        assert task.queue == QUEUE and task.acks_late
        assert task.run()["status"] == "DISABLED"
    finally:
        private.close()
        normal.close()
    recipe = subprocess.run(
        ["make", "--no-print-directory", "-n", "worker-retirement"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    for value in [
        "--queues=privacy-maintenance",
        "--concurrency=1",
        "--pool=prefork",
        "--prefetch-multiplier=1",
        "--hostname=privacy@%h",
    ]:
        assert value in recipe
    assert "--beat" not in recipe


def test_scheduler_requires_isolated_scope_holds_and_never_registers_private_task(settings):
    from uuid import uuid4

    from pydantic import SecretStr
    from sqlalchemy.engine import make_url

    from apps.worker.main import make_worker
    from services.config import Settings
    from services.export_retirement import QUEUE, TASK_NAME

    fields = settings.model_dump()
    with pytest.raises(ValidationError):
        Settings(**(fields | {"export_retirement_enabled": True}))
    schema = "identity_test_" + uuid4().hex
    url = make_url(settings.database_url.get_secret_value()).update_query_dict(
        {"options": f"-csearch_path={schema},public"}
    )
    enabled = Settings(
        **(
            fields
            | {
                "database_url": SecretStr(url.render_as_string(hide_password=False)),
                "export_retirement_enabled": True,
                "export_evidence_holds_enabled": True,
            }
        )
    )
    app = make_worker(enabled)
    try:
        assert TASK_NAME not in app.tasks
        assert app.conf.beat_schedule["retire-export-evidence"] == {
            "task": TASK_NAME,
            "schedule": 300.0,
            "options": {"queue": QUEUE, "expires": 300},
        }
        assert (app.conf.task_soft_time_limit, app.conf.task_time_limit) == (15, 20)
    finally:
        app.close()
    for interval in [59, 3601]:
        with pytest.raises(ValidationError):
            Settings(**(fields | {"export_retirement_interval_seconds": interval}))


def test_failed_worker_task_redacts_diagnostics_and_records_only_closed_failure(monkeypatch):
    from uuid import uuid4

    from services.export_retirement import TASK_NAME

    private = ExecutorSettings(
        enabled=True,
        holds_enabled=True,
        namespace="identity_test_" + uuid4().hex,
        database_url="postgresql+psycopg://executor:canary-private@localhost/kasoma",
    )
    recorded = []

    def fail(*args):
        raise RuntimeError("canary-private confidential SQL/provider/credential")

    monkeypatch.setattr("apps.worker.retirement.execute", fail)
    monkeypatch.setattr(
        "apps.worker.retirement.record", lambda *args: recorded.append(args) or False
    )
    app = make_retirement_worker(private)
    try:
        with pytest.raises(RuntimeError, match="diagnostics withheld") as error:
            app.tasks[TASK_NAME].run()
        assert "canary-private" not in str(error.value)
        assert recorded[0][2].status == "FAILED"
        assert recorded[0][2].model_dump() == {
            "status": "FAILED",
            "removed": 0,
            "examined": 0,
            "exhausted": False,
            "observed_at": 0,
        }
    finally:
        app.close()


def test_retirement_alert_boundaries_disable_and_recovery():
    from services.health import Health
    from services.operations import evaluate
    from services.operations_contracts import Count, OperationThresholds, RetirementCounts
    from tests.contract.test_operations_contract import values

    healthy = Health(status="ok", database="up", redis="up")
    limits = OperationThresholds(failed_imports=1, import_age_seconds=300, unresolved_flags=20)
    counts = RetirementCounts(
        scheduled=True,
        database_enabled=True,
        scope_allowed=True,
        due_requests=Count(value=0),
        last_db_progress_seconds=599,
        last_attempt_status="PROCESSED",
        last_attempt_at=None,
        last_removed=0,
        last_examined=0,
        failures_current_interval=Count(value=0),
        observation_available=True,
    )

    def alerts(changes):
        return {
            row.code
            for row in evaluate(
                healthy, "up", values(retirement=counts.model_copy(update=changes)), limits
            )
        }

    assert alerts({}) == set()
    breached = {"last_db_progress_seconds": 600, "failures_current_interval": Count(value=1)}
    assert alerts(breached) == {"RETIREMENT_FAILED", "RETIREMENT_STALLED"}
    for flag in ["scheduled", "database_enabled", "scope_allowed"]:
        assert alerts(breached | {flag: False}) == set()
    assert alerts(breached | {"observation_available": False}) == {"RETIREMENT_STALLED"}
    assert alerts({}) == set()


@pytest.mark.parametrize("age,valid", [(299, True), (300, False), (-1, False)])
def test_observation_clock_boundaries_and_dataset_isolation(monkeypatch, age, valid):
    from services import export_retirement_observations as observations

    cache = Mock()
    cache.__enter__ = Mock(return_value=cache)
    cache.__exit__ = Mock(return_value=False)
    cache.eval.return_value = [
        observations.Observation(status="PROCESSED", observed_at=1000).model_dump_json().encode(),
        b"0",
        1000 + age,
    ]
    monkeypatch.setattr(observations, "connection", lambda url: cache)
    assert (observations.read("redis://localhost", ("db", "one")) is not None) is valid
    assert observations.key("db", "one") != observations.key("db", "two")
