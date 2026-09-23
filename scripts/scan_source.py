"""Scan only Git-eligible source, including uncommitted new files, with Gitleaks."""

import shutil
import subprocess
import tempfile
from pathlib import Path

root = Path.cwd()
names = (
    subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
    )
    .decode()
    .split("\0")
)
with tempfile.TemporaryDirectory(prefix="kasoma-source-") as directory:
    destination = Path(directory)
    for name in names:
        source = root / name
        if not name or not source.is_file():
            continue
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{destination}:/repo:ro",
            "zricethezav/gitleaks:v8.24.3",
            "dir",
            "/repo",
            "--redact",
        ],
        check=True,
    )
