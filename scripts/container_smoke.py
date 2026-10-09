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
            "export-worker",
            "web",
        ],
        check=True,
    )
    with urllib.request.urlopen("http://localhost:8000/api/v1/health", timeout=5) as response:
        assert json.load(response)["status"] == "ok"
    with urllib.request.urlopen("http://localhost:3000", timeout=10) as response:
        assert b"Services are ready." in response.read()
    subprocess.run(["uv", "run", "--frozen", "python", "-m", "scripts.export_smoke"], check=True)
    subprocess.run(
        ["uv", "run", "--frozen", "python", "-m", "scripts.request_metrics_smoke"], check=True
    )
    print("Container smoke passed: service health and owned export through worker/storage/web.")
finally:
    started_here = [
        name for name in ["web", "export-worker", "worker", "api"] if name not in already_running
    ]
    if started_here:
        subprocess.run(
            ["docker", "compose", "--profile", "application", "stop", *started_here], check=True
        )
