"""Provisioned private configuration, actual LOGIN and end-to-end SQL batch execution."""

import pytest
from sqlalchemy import text
from sqlalchemy.engine import make_url

from services.export_retirement import RetirementUnavailable, execute
from services.export_retirement_access import provision
from services.export_retirement_config import ExecutorSettings, load_executor
from tests.integration.test_export_retirement import enable, historical

pytestmark = pytest.mark.integration


@pytest.fixture
def private_executor(content, tmp_path):
    identity, *_ = content
    path = tmp_path / "executor.env"
    role = None
    try:
        with identity.engine.begin() as db:
            provision(
                db,
                path,
                identity.settings.database_url.get_secret_value(),
                identity.settings.redis_url.get_secret_value(),
            )
        private = load_executor(path)
        role = make_url(private.database_url.get_secret_value()).username
        yield content, path, private
    finally:
        if role:
            with identity.engine.begin() as db:
                schema = db.scalar(text("SELECT current_schema()"))
                quoted = db.dialect.identifier_preparer.quote_schema(schema)
                db.execute(
                    text(
                        f"REVOKE EXECUTE ON FUNCTION {quoted}.retire_completed_export_evidence() "
                        f"FROM {role}"
                    )
                )
                db.execute(text(f"REVOKE USAGE ON SCHEMA {quoted} FROM {role}"))
                db.execute(text(f"DROP ROLE {role}"))


def enabled(private):
    return ExecutorSettings(**(private.model_dump() | {"enabled": True, "holds_enabled": True}))


def test_provisioned_executor_is_private_default_off_and_runs_one_bounded_batch(
    private_executor, caplog, capsys
):
    content, path, private = private_executor
    identity, *_ = content
    assert path.stat().st_mode & 0o777 == 0o600
    assert private.enabled is False and private.holds_enabled is False
    assert execute(private)[0].status == "DISABLED"
    active = enabled(private)
    assert execute(active)[0].status == "DISABLED"  # SQL activation is independent.
    source, *_ = historical(content)
    enable(identity)
    result, scope = execute(active)
    assert result.status == "PROCESSED" and result.removed.data_request_receipts == 3
    assert result.examined == 3 and scope[1] == private.namespace
    assert private.database_url.get_secret_value() not in caplog.text + capsys.readouterr().out
    with identity.engine.connect() as db:
        assert (
            db.scalar(
                text("SELECT count(*) FROM data_subject_requests WHERE id=:id"), {"id": source}
            )
            == 1
        )


@pytest.mark.parametrize("drift", ["TABLE_READ", "FUNCTION_PATH", "PUBLIC_EXECUTE"])
def test_executor_rejects_overprivileged_or_damaged_capability_before_call(private_executor, drift):
    content, _, private = private_executor
    identity, *_ = content
    historical(content)
    enable(identity)
    role = make_url(private.database_url.get_secret_value()).username
    with identity.engine.begin() as db:
        if drift == "TABLE_READ":
            db.execute(text(f"GRANT SELECT ON data_subject_requests TO {role}"))
        elif drift == "FUNCTION_PATH":
            db.execute(
                text("ALTER FUNCTION retire_completed_export_evidence() SET search_path=public")
            )
        else:
            db.execute(
                text("GRANT EXECUTE ON FUNCTION retire_completed_export_evidence() TO PUBLIC")
            )
    with pytest.raises(RetirementUnavailable, match="EXECUTION_UNAVAILABLE"):
        execute(enabled(private))
    with identity.engine.begin() as db:
        assert db.scalar(text("SELECT count(*) FROM data_request_receipts")) == 3
        if drift == "TABLE_READ":
            db.execute(text(f"REVOKE SELECT ON data_subject_requests FROM {role}"))


def test_existing_executor_config_and_role_are_not_overwritten(private_executor):
    content, path, _ = private_executor
    identity, *_ = content
    original = path.read_bytes()
    with (
        identity.engine.begin() as db,
        pytest.raises(ValueError, match="Existing retirement executor"),
    ):
        provision(
            db,
            path,
            identity.settings.database_url.get_secret_value(),
            identity.settings.redis_url.get_secret_value(),
        )
    assert path.read_bytes() == original


def test_cli_activation_audit_disable_independence_and_endpoint_binding(
    private_executor, monkeypatch, capsys
):
    from services import export_retirement_cli as cli

    content, path, private = private_executor
    identity, *_ = content
    monkeypatch.setattr(cli, "Settings", lambda **kwargs: identity.settings)
    monkeypatch.setenv("KASOMA_RETIREMENT_CONFIG", str(path))
    monkeypatch.setenv("KASOMA_RETIREMENT_ACTION", "enable")
    with pytest.raises(SystemExit):
        cli.main()
    value = (
        path.read_text()
        .replace("EXPORT_RETIREMENT_ENABLED='false'", "EXPORT_RETIREMENT_ENABLED='true'")
        .replace(
            "EXPORT_RETIREMENT_HOLDS_ENABLED='false'", "EXPORT_RETIREMENT_HOLDS_ENABLED='true'"
        )
    )
    path.write_text(value)
    cli.main()
    with identity.engine.connect() as db:
        assert db.scalar(text("SELECT enabled FROM export_retirement_state")) is True
        row = db.execute(
            text(
                "SELECT actor_id,reason FROM audit_log "
                "WHERE action='data_request.retirement_configuration'"
            )
        ).one()
        assert row == (None, "SYNTHETIC_RETIREMENT_ENABLED")
    path.write_text(
        value.replace(
            "EXPORT_RETIREMENT_HOLDS_ENABLED='true'", "EXPORT_RETIREMENT_HOLDS_ENABLED='false'"
        )
    )
    monkeypatch.setenv("KASOMA_RETIREMENT_ACTION", "disable")
    cli.main()
    with identity.engine.connect() as db:
        assert db.scalar(text("SELECT enabled FROM export_retirement_state")) is False
    assert private.database_url.get_secret_value() not in capsys.readouterr().out


def test_count_only_observations_and_admin_health_are_scoped_and_finite(private_executor):
    from services.export_retirement_observations import Observation, connection, key, read, record

    content, _, private = private_executor
    identity, client, actors, _ = content
    source, _, _, _ = historical(content)
    with identity.engine.connect() as db:
        scope = db.execute(text("SELECT current_database(),current_schema()")).one()
        index = db.scalar(
            text(
                "SELECT indexdef FROM pg_indexes WHERE "
                "schemaname=current_schema() AND indexname='ix_export_accountability_due'"
            )
        )
        assert "retention_due_at, id" in index and "completed_at IS NOT NULL" in index
    scope = tuple(scope)
    url = private.redis_url.get_secret_value()
    assert record(url, scope, Observation(status="FAILED"))
    current = read(url, scope)
    assert current[0].status == "FAILED" and current[1] == 1
    with connection(url) as cache:
        assert 0 < cache.ttl(key(*scope) + ":last") <= 300
        raw = cache.get(key(*scope) + ":last")
        assert str(source).encode() not in raw and b"database_url" not in raw
        bucket = cache.time()[0] // 300
        assert 0 < cache.ttl(key(*scope) + f":fail:{bucket}") <= 300
    response = client.get("/api/v1/admin/operations", headers=actors["admin"])
    assert response.status_code == 200, response.text
    health = response.json()["counts"]["retirement"]
    assert health is not None and health["due_requests"] == {"value": 1, "at_least": False}
    assert health["last_attempt_status"] == "FAILED" and health["scheduled"] is False
    assert (
        str(source) not in response.text
        and private.database_url.get_secret_value() not in response.text
    )
    assert "RETIREMENT_FAILED" not in {a["code"] for a in response.json()["alerts"]}
    for role in ["learner", "support", "author"]:
        assert client.get("/api/v1/admin/operations", headers=actors[role]).status_code == 403
    with connection(url) as cache:
        cache.set(key(*scope) + ":last", b'{"status":"learner@example.invalid"}', ex=300)
    assert read(url, scope) is None


def test_fresh_private_prefork_consumer_executes_only_its_queue(private_executor):
    import os
    import shlex
    import signal
    import subprocess
    import sys
    import tempfile
    import time
    from uuid import uuid4

    from redis import Redis

    from apps.worker.retirement import make_retirement_worker
    from services.export_retirement import QUEUE, TASK_NAME
    from services.export_retirement_observations import key

    content, path, private = private_executor
    identity, *_ = content
    historical(content)
    enable(identity)
    path.write_text(
        path.read_text().replace("='false'", "='true'") + "EXPORT_RETIREMENT_APP_ENV='test'\n"
    )
    namespace = "kasoma:test:retirement-worker:" + uuid4().hex + ":"
    other = "ordinary-" + uuid4().hex
    url = private.redis_url.get_secret_value()
    app = make_retirement_worker(enabled(private))
    app.conf.broker_transport_options = {"global_keyprefix": namespace}
    scope = (make_url(private.database_url.get_secret_value()).database, private.namespace)
    with Redis.from_url(url, socket_connect_timeout=2, socket_timeout=2) as cache:
        try:
            with tempfile.TemporaryFile(mode="w+") as log:
                recipe = subprocess.run(
                    ["make", "--no-print-directory", "-n", "worker-retirement"],
                    capture_output=True,
                    text=True,
                    check=True,
                ).stdout
                args = shlex.split(recipe)
                args = args[args.index("celery") + 1 :]
                args[args.index("-A") + 1] = "tests.fixtures.retirement_worker_app:app"
                process = subprocess.Popen(
                    [
                        sys.executable,
                        "-m",
                        "celery",
                        *args,
                        "--without-mingle",
                        "--without-gossip",
                        "--without-heartbeat",
                    ],
                    env=os.environ
                    | {
                        "KASOMA_RETIREMENT_CONFIG": str(path),
                        "KASOMA_RETIREMENT_TEST_NAMESPACE": namespace,
                    },
                    stdout=log,
                    stderr=log,
                    start_new_session=True,
                )
                try:
                    app.send_task(TASK_NAME, queue=other)
                    app.send_task(TASK_NAME, queue=QUEUE)
                    deadline = time.monotonic() + 25
                    while cache.get(key(*scope) + ":last") is None:
                        assert process.poll() is None, "Private worker exited before execution"
                        assert time.monotonic() < deadline, "Private worker did not execute"
                        time.sleep(0.05)
                    assert cache.llen(namespace + other) == 1
                    with identity.engine.connect() as db:
                        assert db.scalar(text("SELECT count(*) FROM data_request_receipts")) == 0
                        assert (
                            db.scalar(
                                text(
                                    "SELECT count(*) FROM audit_log WHERE "
                                    "action='data_request.export_retirement_batch'"
                                )
                            )
                            == 1
                        )
                finally:
                    if process.poll() is None:
                        os.killpg(process.pid, signal.SIGTERM)
                        try:
                            process.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            os.killpg(process.pid, signal.SIGKILL)
                            process.wait(timeout=5)
                    log.seek(0)
                    output = log.read()
                    assert private.database_url.get_secret_value() not in output
                    assert "Traceback" not in output, output.replace(
                        private.database_url.get_secret_value(), "[redacted synthetic DSN]"
                    )[-3500:]
        finally:
            app.close()
            # Only the random synthetic broker namespace, after its consumer has stopped.
            keys = list(cache.scan_iter(match=namespace + "*", count=100))
            assert len(keys) <= 100
            if keys:
                cache.delete(*keys)


@pytest.mark.parametrize("identity", ["0041"], indirect=True)
def test_additive_health_index_preserves_populated_accountability_and_activation(content):
    import os
    import subprocess

    identity, *_ = content
    source, *_ = historical(content)
    with identity.engine.begin() as db:
        before = db.execute(
            text("SELECT id,request_id,actor_id,key FROM data_request_receipts ORDER BY id")
        ).all()
        for _ in range(2):
            subprocess.run(
                ["make", "migrate"],
                check=True,
                capture_output=True,
                timeout=120,
                env=os.environ
                | {"DATABASE_URL": identity.settings.database_url.get_secret_value()},
            )
        assert (
            db.execute(
                text("SELECT id,request_id,actor_id,key FROM data_request_receipts ORDER BY id")
            ).all()
            == before
        )
        assert db.scalar(text("SELECT enabled FROM export_retirement_state")) is False
        assert (
            db.scalar(
                text("SELECT count(*) FROM data_subject_requests WHERE id=:id"), {"id": source}
            )
            == 1
        )
