"""Local prefork hard-stop evidence; isolated Redis keys and synthetic database schema."""

import os
import shlex
import signal
import subprocess
import sys
import tempfile
import time
from datetime import timedelta
from uuid import uuid4

import pytest
from redis import Redis
from sqlalchemy.orm import Session

from apps.worker import exports
from apps.worker.main import make_worker
from services.domain.export_jobs import ExportJob
from services.export_jobs import claim_next, queue
from tests.integration.test_export_jobs import setup_job

pytestmark = pytest.mark.integration


def test_hard_stop_preserves_unpublished_job_and_finite_lease_recovery(content):
    identity, _, _, token, target = setup_job(content)
    queue(identity, token, target, uuid4(), uuid4())
    namespace = "kasoma:test:export-worker:" + uuid4().hex + ":"
    queue_name = "export-limit-" + uuid4().hex
    other_queue = "ordinary-isolation-" + uuid4().hex
    broker_url = identity.settings.redis_url.get_secret_value()
    initial_clock = identity.clock()

    app = make_worker(identity.settings)
    exports.register(app, identity.settings)
    app.conf.update(
        broker_transport_options={"global_keyprefix": namespace},
        task_queues={queue_name: {}},
        worker_prefetch_multiplier=1,
        control_exchange="export-test-" + uuid4().hex,
    )
    task = app.tasks["kasoma.prepare_personal_export"]
    # Accelerate only the test envelope; contract tests verify production 110/120 values.
    task.soft_time_limit, task.time_limit = 0.5, 1.5

    env = os.environ | {
        "APP_ENV": "test",
        "MODEL_PROVIDER": "fake",
        "EMAIL_PROVIDER": "fake",
        "DATABASE_URL": identity.settings.database_url.get_secret_value(),
        "KASOMA_EXPORT_TEST_NAMESPACE": namespace,
        "KASOMA_EXPORT_TEST_QUEUE": queue_name,
        "KASOMA_EXPORT_TEST_CLOCK": initial_clock.isoformat(),
    }

    with Redis.from_url(broker_url, socket_connect_timeout=2, socket_timeout=2) as cache:
        try:
            with tempfile.TemporaryFile(mode="w+") as log:
                # Exercise the repository's actual launch policy. Override only the
                # application/queue/node identity to retain isolated synthetic fixtures.
                recipe = subprocess.run(
                    ["make", "--no-print-directory", "-n", "worker-exports"],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout
                arguments = shlex.split(recipe)
                arguments = arguments[arguments.index("celery") + 1 :]
                arguments[arguments.index("-A") + 1] = "tests.fixtures.export_worker_app:app"
                arguments = [
                    "--queues=" + queue_name
                    if arg.startswith("--queues=")
                    else "--hostname=" + queue_name + "@%h"
                    if arg.startswith("--hostname=")
                    else "--loglevel=ERROR"
                    if arg.startswith("--loglevel=")
                    else arg
                    for arg in arguments
                ]
                process = subprocess.Popen(
                    [
                        sys.executable,
                        "-m",
                        "celery",
                        *arguments,
                        "--without-mingle",
                        "--without-gossip",
                        "--without-heartbeat",
                    ],
                    env=env,
                    stdout=log,
                    stderr=log,
                    start_new_session=True,
                )
                try:
                    app.send_task("kasoma.synthetic_export_worker_probe", queue=other_queue)
                    task.apply_async(queue=queue_name)
                    deadline = time.monotonic() + 20
                    while cache.get(namespace + "entered") is None and time.monotonic() < deadline:
                        time.sleep(0.05)
                    first_pid = cache.get(namespace + "entered")
                    assert first_pid is not None, "Worker never reached synthetic storage"
                    app.send_task("kasoma.synthetic_export_worker_probe", queue=queue_name)
                    while (
                        cache.get(namespace + "replacement") is None and time.monotonic() < deadline
                    ):
                        time.sleep(0.05)
                    replacement_pid = cache.get(namespace + "replacement")
                    assert replacement_pid is not None and replacement_pid != first_pid
                    assert cache.llen(namespace + other_queue) == 1
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
                    # The subprocess contains only synthetic fixtures; pytest captures on failure.
                    print(output)
                assert "Hard time limit (1.5s) exceeded" in output
            with Session(identity.engine) as db:
                job = db.get(ExportJob, target)
                assert job.status == "RUNNING" and job.attempts == 1
                abandoned = job.generation_id
            identity.clock = lambda: initial_clock + timedelta(seconds=180)
            assert claim_next(identity) is None  # Expired lease becomes a bounded retry.
            identity.clock = lambda: initial_clock + timedelta(seconds=210)
            new_claim = claim_next(identity)
            assert new_claim is not None and new_claim.generation_id != abandoned
        finally:
            app.close()
            # Remove only this invocation's random namespace after its worker is stopped.
            keys = list(cache.scan_iter(match=namespace + "*", count=100))
            assert len(keys) <= 100
            if keys:
                cache.delete(*keys)
