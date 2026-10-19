"""Only this dedicated executable reads the private executor configuration file."""

import os
from pathlib import Path

from apps.worker.retirement import make_retirement_worker
from services.export_retirement_config import CONFIG_PATH, load_executor

try:
    settings = load_executor(Path(os.environ.get("KASOMA_RETIREMENT_CONFIG", str(CONFIG_PATH))))
    app = make_retirement_worker(settings)
except Exception:
    raise RuntimeError(
        "Private retirement worker configuration unavailable; diagnostics withheld"
    ) from None
