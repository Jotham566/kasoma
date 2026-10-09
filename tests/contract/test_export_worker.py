"""Dedicated task policy and sanitized failures without live provider or broker calls."""

import ast
import shlex
import socket
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from apps.worker import exports
from apps.worker.main import make_worker


def test_repository_launches_keep_export_work_exclusive_and_hard_limited():
    recipe = subprocess.run(
        ["make", "--no-print-directory", "-n", "worker-exports"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    command = shlex.split(recipe)
    for required in [
        "--pool=prefork",
        "--concurrency=1",
        "--prefetch-multiplier=1",
        "--queues=exports",
        "--include=apps.worker.export_tasks",
    ]:
        assert required in command
    assert "--beat" not in command
    tree = ast.parse(Path("scripts/dev.py").read_text())
    assignment = next(
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "commands" for target in node.targets)
    )
    commands = ast.literal_eval(assignment.value)
    ordinary = next(command for command in commands if "celery" in command)
    assert "--queues=operations,imports,messaging" in ordinary
    assert sum("--beat" in command for command in commands) == 1
    compose = (
        Path("docker-compose.yml").read_text().split("  worker:\n", 1)[1].split("  web:\n", 1)[0]
    )
    launch = next(
        line.strip()[9:] for line in compose.splitlines() if line.strip().startswith("command: ")
    )
    assert "--queues=operations,imports,messaging" in shlex.split(launch)


@pytest.mark.parametrize("service,prefix", [("worker", "worker"), ("export-worker", "exports")])
@pytest.mark.parametrize("response", ["healthy", "foreign", "missing", "invalid"])
def test_compose_health_requires_its_own_worker(monkeypatch, service, prefix, response):
    section = Path("docker-compose.yml").read_text().split(f"  {service}:\n", 1)[1]
    launch = next(line.strip() for line in section.splitlines() if "command:" in line)
    assert f"--hostname={prefix}@%h" in launch
    health = next(line.strip()[6:] for line in section.splitlines() if "test: [" in line)
    probe = ast.literal_eval(health)[-1]
    node = f"{prefix}@health-fixture"
    replies = {
        "healthy": {node: {"ok": "pong"}},
        "foreign": {"another@health-fixture": {"ok": "pong"}},
        "missing": None,
        "invalid": {node: {"error": "unavailable"}},
    }
    calls = []

    def inspect(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(ping=lambda: replies[response])

    app = SimpleNamespace(control=SimpleNamespace(inspect=inspect))
    monkeypatch.setitem(sys.modules, "apps.worker.entrypoint", SimpleNamespace(app=app))
    monkeypatch.setattr(socket, "gethostname", lambda: "health-fixture")
    with pytest.raises(SystemExit) as result:
        exec(probe, {})
    assert result.value.code == (0 if response == "healthy" else 1)
    assert calls == [{"destination": [node], "timeout": 3}]


def test_export_tasks_are_isolated_and_do_not_raise_ordinary_worker_limits(settings, monkeypatch):
    from apps.worker import export_tasks

    app = make_worker(settings)
    calls = []
    monkeypatch.setattr(export_tasks, "generation", lambda config: calls.append(config) or True)
    monkeypatch.setattr(export_tasks, "Settings", lambda: settings)
    try:
        assert "exports" in app.conf.task_queues
        exports.register(app, settings)
        task = app.tasks["kasoma.prepare_personal_export"]
        assert task.queue == "exports" and task.acks_late
        assert (task.soft_time_limit, task.time_limit) == (110, 120)
        assert task.run() is True and calls == [settings]
        cleanup = app.tasks["kasoma.cleanup_personal_exports"]
        assert cleanup.queue == "exports" and cleanup.acks_late
        assert (cleanup.soft_time_limit, cleanup.time_limit) == (15, 20)
        assert (app.conf.task_soft_time_limit, app.conf.task_time_limit) == (15, 20)
        assert app.conf.task_ignore_result
        for name in ["prepare-personal-export", "cleanup-personal-exports"]:
            schedule = app.conf.beat_schedule[name]
            assert schedule["options"]["queue"] == "exports"
            assert schedule["options"]["expires"] == schedule["schedule"]
    finally:
        app.close()


@pytest.mark.parametrize("stage", ["connect", "process", "dispose"])
def test_export_task_errors_hide_provider_and_database_diagnostics(settings, monkeypatch, stage):
    disposed = []

    def failure(*args, **kwargs):
        raise RuntimeError("synthetic confidential provider database details")

    def dispose():
        disposed.append(True)
        if stage == "dispose":
            failure()

    monkeypatch.setattr(
        exports,
        "engine_for",
        failure if stage == "connect" else lambda _: SimpleNamespace(dispose=dispose),
    )
    monkeypatch.setattr(exports, "IdentityService", lambda *args: None)
    monkeypatch.setattr(exports, "PrivateExportStorage", lambda *args: None)
    monkeypatch.setattr(
        exports, "process_one", failure if stage == "process" else lambda *args: True
    )
    with pytest.raises(
        RuntimeError, match="Personal export worker unavailable; diagnostics withheld"
    ) as exc:
        exports.generation(settings)
    assert exc.value.__suppress_context__
    assert disposed == ([] if stage == "connect" else [True])


def test_cleanup_worker_never_returns_private_cursor(settings, monkeypatch):
    closed = []

    class Cache:
        @classmethod
        def from_url(cls, url, **kwargs):
            assert kwargs == {"socket_connect_timeout": 2, "socket_timeout": 2}
            return cls()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            closed.append("cache")

    monkeypatch.setattr(exports, "Redis", Cache)
    monkeypatch.setattr(
        exports, "engine_for", lambda _: SimpleNamespace(dispose=lambda: closed.append("db"))
    )
    monkeypatch.setattr(exports, "IdentityService", lambda *args: None)
    monkeypatch.setattr(exports, "PrivateExportStorage", lambda *args: None)
    monkeypatch.setattr(
        exports,
        "sweep_with_cursor",
        lambda *args: SimpleNamespace(
            removed=2,
            generations=1,
            examined=4,
            failures=0,
            exhausted=False,
            cursor="private cursor",
        ),
    )
    result = exports.cleanup(settings, "00000000-0000-0000-0000-000000000001")
    assert result == {
        "removed": 2,
        "generations": 1,
        "examined": 4,
        "failures": 0,
        "exhausted": False,
    }
    assert closed == ["cache", "db"] and "private" not in str(result)
