"""Actual private entrypoint with only a randomized local broker namespace override."""

import os
import re

from apps.worker.retirement_entrypoint import app, settings

namespace = os.environ["KASOMA_RETIREMENT_TEST_NAMESPACE"]
if settings.app_env != "test" or not re.fullmatch(
    r"kasoma:test:retirement-worker:[a-f0-9]{32}:", namespace
):
    raise RuntimeError("Isolated synthetic retirement worker required")
app.conf.update(
    broker_transport_options={"global_keyprefix": namespace},
    control_exchange="retirement-test-" + namespace,
)
