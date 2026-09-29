"""Supervise native web/API/worker; Ctrl-C terminates their process groups."""

import os
import signal
import subprocess
import time

commands = [
    [
        "uv",
        "run",
        "--frozen",
        "uvicorn",
        "apps.api.main:app",
        "--host",
        "127.0.0.1",
        "--no-access-log",
        "--log-level",
        "info",
    ],
    [
        "uv",
        "run",
        "--frozen",
        "celery",
        "-A",
        "apps.worker.entrypoint:app",
        "worker",
        "--loglevel=INFO",
        "--pool=solo",
        "--concurrency=1",
        "--beat",
        "--schedule=.local/celerybeat",
    ],
    ["corepack", "pnpm", "--filter", "@kasoma/web", "dev"],
]
processes = []
try:
    for command in commands:
        processes.append(subprocess.Popen(command, start_new_session=True))
    while all(process.poll() is None for process in processes):
        time.sleep(0.5)
    raise SystemExit("A development process exited; shutting down the group.")
except KeyboardInterrupt:
    pass
finally:
    for process in processes:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
    for process in processes:
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
