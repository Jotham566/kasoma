"""Exercise application containers and preserve previously running application services."""

import json
import subprocess
import urllib.request

already_running = set(
    subprocess.check_output(
        ["docker", "compose", "ps", "--services", "--status", "running"], text=True
    ).splitlines()
)
try:
    subprocess.run(
        [
            "docker",
            "compose",
            "--profile",
            "application",
            "up",
            "-d",
            "--wait",
            "--wait-timeout",
            "90",
            "api",
            "worker",
            "web",
        ],
        check=True,
    )
    with urllib.request.urlopen("http://localhost:8000/api/v1/health", timeout=5) as response:
        assert json.load(response)["status"] == "ok"
    with urllib.request.urlopen("http://localhost:3000", timeout=10) as response:
        assert b"Services are ready." in response.read()
    print("Container smoke passed: API/database/Redis, worker health and web client.")
finally:
    started_here = [name for name in ["web", "worker", "api"] if name not in already_running]
    if started_here:
        subprocess.run(
            ["docker", "compose", "--profile", "application", "stop", *started_here], check=True
        )
