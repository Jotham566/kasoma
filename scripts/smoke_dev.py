"""Bounded smoke of the prescribed dev command, with process-group cleanup."""

import os
import signal
import subprocess
import time
import urllib.request
from pathlib import Path

log = Path(".local/dev-smoke.log")
log.parent.mkdir(exist_ok=True)
with log.open("w") as output:
    process = subprocess.Popen(
        ["make", "dev"], stdout=output, stderr=subprocess.STDOUT, start_new_session=True
    )
    try:
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            try:
                with urllib.request.urlopen("http://127.0.0.1:3000", timeout=5) as response:
                    assert b"Services are ready." in response.read()
                print("make dev smoke passed: web consumes live API dependency health.")
                break
            except OSError:
                if process.poll() is not None:
                    raise SystemExit("make dev exited; inspect .local/dev-smoke.log") from None
                time.sleep(0.5)
        else:
            raise SystemExit("make dev readiness timeout")
    finally:
        os.killpg(process.pid, signal.SIGINT)
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=5)
