"""Optional native Mac CLI installation; never downloads weights or runs inference."""

import hashlib
import platform
import subprocess
import tarfile
from pathlib import Path

VERSION = "0.34.3"
DIGEST = "2c45865f94bce0d4d1d2567603dd2fdacaf375585220a175aa4800105193d36e"
archive = Path(".local/ollama-darwin.tgz")
destination = Path(".local/ollama")
marker = destination / ".installed-version"
if marker.exists() and marker.read_text().strip() == VERSION and (destination / "ollama").is_file():
    print(f"Native Ollama {VERSION} already installed; existing runtime preserved.")
    raise SystemExit(0)
if platform.system() != "Darwin":
    raise SystemExit("This setup profile is for macOS. Install host-native Ollama for your OS.")
archive.parent.mkdir(exist_ok=True)
if not archive.exists() or hashlib.file_digest(archive.open("rb"), "sha256").hexdigest() != DIGEST:
    subprocess.run(
        [
            "curl",
            "--fail",
            "--location",
            "--retry",
            "2",
            "--max-time",
            "3600",
            f"https://github.com/ollama/ollama/releases/download/v{VERSION}/ollama-darwin.tgz",
            "--output",
            str(archive),
        ],
        check=True,
    )
with archive.open("rb") as source:
    if hashlib.file_digest(source, "sha256").hexdigest() != DIGEST:
        raise SystemExit("Ollama archive checksum mismatch; refusing installation")
destination.mkdir(exist_ok=True)
with tarfile.open(archive) as source:
    source.extractall(destination, filter="data")
marker.write_text(VERSION + "\n")
print(f"Native Ollama {VERSION} installed locally. No model downloaded; use make ollama-serve.")
