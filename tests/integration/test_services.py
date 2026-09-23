"""Run against an isolated schema; never truncate a developer database."""

import os
import subprocess
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.engine import make_url

from services.config import Settings
from services.database import engine_for
from services.health import dependency_health
from services.seed import seed

pytestmark = pytest.mark.integration


def test_migrations_seed_and_dependencies():
    settings = Settings()
    assert dependency_health(settings).status == "ok", "Run make services first"
    engine = engine_for(settings)
    schema = "test_" + uuid4().hex
    with engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    url = make_url(settings.database_url.get_secret_value()).update_query_dict(
        {"options": f"-csearch_path={schema},public"}
    )
    env = os.environ | {"DATABASE_URL": url.render_as_string(hide_password=False)}
    # A fresh schema is empty; rerun tests upgrade idempotency. No release snapshot exists yet.
    for _ in range(2):
        subprocess.run(
            ["uv", "run", "--frozen", "alembic", "-c", "apps/api/alembic.ini", "upgrade", "head"],
            check=True,
            env=env,
            capture_output=True,
        )
    isolated = Settings(database_url=url.render_as_string(hide_password=False))
    seed(isolated)
    seed(isolated)
    check = engine_for(isolated)
    with check.connect() as connection:
        assert connection.scalar(text("SELECT count(*) FROM levels")) == 1
        assert connection.scalar(text("SELECT count(*) FROM subjects")) == 2
        assert connection.scalar(text("SELECT count(*) FROM topics")) == 6
        assert (
            connection.scalar(text("SELECT extname FROM pg_extension WHERE extname='vector'"))
            == "vector"
        )
    check.dispose()
    engine.dispose()


def test_local_storage_and_mailpit():
    import httpx

    from services.providers import MailpitEmailProvider, MinioObjectStorage

    settings = Settings()
    storage = MinioObjectStorage(settings)
    storage.ensure_container()
    assert storage.client.bucket_exists(settings.object_storage_container)
    # No external email delivery: this adapter can connect only to local Mailpit.
    assert (
        MailpitEmailProvider(settings).send(
            "synthetic@example.invalid", "Synthetic local-only foundation test."
        )
        == "mailpit-captured"
    )
    with httpx.Client(trust_env=False, timeout=5) as client:
        assert (
            client.get(f"http://localhost:9000/{settings.object_storage_container}").status_code
            == 403
        )
        response = client.get("http://localhost:8025/api/v1/messages")
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_real_worker_smoke(tmp_path):
    import time

    from apps.worker.main import make_worker

    settings = Settings()
    request_id = str(uuid4())
    queue = "foundation-test-" + uuid4().hex
    log = tmp_path / "worker.log"
    with log.open("w") as output:
        worker = subprocess.Popen(
            [
                "uv",
                "run",
                "--frozen",
                "celery",
                "-A",
                "apps.worker.entrypoint:app",
                "worker",
                "--pool=solo",
                "--concurrency=1",
                "--loglevel=INFO",
                "-Q",
                queue,
                "--without-gossip",
                "--without-mingle",
                "--without-heartbeat",
            ],
            stdout=output,
            stderr=subprocess.STDOUT,
        )
        try:
            app = make_worker(settings)
            app.send_task(
                "kasoma.smoke", queue=queue, headers={"kasoma_correlation_id": request_id}
            )
            deadline = time.monotonic() + 20
            while time.monotonic() < deadline:
                if request_id in log.read_text():
                    break
                assert worker.poll() is None, "Worker exited before processing smoke task"
                time.sleep(0.2)
            assert request_id in log.read_text(), "Worker did not propagate the correlation ID"
            app.close()
        finally:
            worker.terminate()
            try:
                worker.wait(timeout=5)
            except subprocess.TimeoutExpired:
                worker.kill()
                worker.wait(timeout=5)
