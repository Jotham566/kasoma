"""Synthetic-only CLI worker used to verify prefork hard interruption and lease recovery."""

import os
import re
import time
from datetime import datetime

from billiard.exceptions import SoftTimeLimitExceeded
from celery import shared_task
from redis import Redis
from sqlalchemy.engine import make_url

from apps.worker import exports
from apps.worker.main import make_worker
from services.config import Settings
from services.identity import IdentityService

settings = Settings()
namespace = os.environ["KASOMA_EXPORT_TEST_NAMESPACE"]
queue_name = os.environ["KASOMA_EXPORT_TEST_QUEUE"]
clock = datetime.fromisoformat(os.environ["KASOMA_EXPORT_TEST_CLOCK"])
options = make_url(settings.database_url.get_secret_value()).query.get("options", "")
if (
    settings.app_env != "test"
    or not re.fullmatch(r"-csearch_path=identity_test_[a-f0-9]{32},public", options)
    or not re.fullmatch(r"kasoma:test:export-worker:[a-f0-9]{32}:", namespace)
    or not re.fullmatch(r"export-limit-[a-f0-9]{32}", queue_name)
    or clock.utcoffset() is None
):
    raise RuntimeError("Isolated synthetic worker configuration required")


class StalledStorage:
    def __init__(self, settings):
        pass

    def put(self, *args):
        with Redis.from_url(settings.redis_url.get_secret_value()) as cache:
            cache.set(namespace + "entered", str(os.getpid()), ex=120)
        while True:
            try:
                time.sleep(10)
            except SoftTimeLimitExceeded:
                continue


exports.PrivateExportStorage = StalledStorage
exports.IdentityService = lambda engine, config, email, sms: IdentityService(
    engine, config, email, sms, clock=lambda: clock
)
app = make_worker(settings)
exports.register(app, settings)
app.conf.update(
    broker_transport_options={"global_keyprefix": namespace},
    task_queues={queue_name: {}},
    worker_prefetch_multiplier=1,
    control_exchange="export-test-" + queue_name,
    imports=("apps.worker.export_tasks", "tests.fixtures.export_worker_app"),
)
task = app.tasks["kasoma.prepare_personal_export"]
task.soft_time_limit, task.time_limit = 0.5, 1.5


@shared_task(name="kasoma.synthetic_export_worker_probe")
def probe():
    with Redis.from_url(settings.redis_url.get_secret_value()) as cache:
        cache.set(namespace + "replacement", str(os.getpid()), ex=120)
