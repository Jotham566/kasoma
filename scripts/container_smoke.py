"""Exercise application containers, then release app ports for native development."""

import json
import subprocess
import urllib.request

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
    subprocess.run(
        ["docker", "compose", "--profile", "application", "stop", "web", "worker", "api"],
        check=True,
    )
