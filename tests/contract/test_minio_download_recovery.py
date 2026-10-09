"""NFR-MNT-001: exercise the real build helper without dependency/network calls."""

import os
import subprocess
from pathlib import Path

import pytest

HELPER = Path(__file__).resolve().parents[2] / "infra/containers/download-go-modules.sh"


@pytest.mark.parametrize(
    ("failures", "verify_status", "downloads", "verified", "status"),
    [(0, 0, 1, True, 0), (2, 0, 3, True, 0), (3, 0, 3, False, 1), (0, 9, 1, True, 9)],
)
def test_bounded_download_recovery_and_terminal_verification(
    tmp_path, failures, verify_status, downloads, verified, status
):
    fake_go = tmp_path / "go"
    fake_go.write_text(
        """#!/bin/sh
set -eu
printf '%s\\n' "$*" >> "$KASOMA_TEST_GO_LOG"
case "$*" in
  'mod download')
    count=0
    if [ -f "$KASOMA_TEST_GO_COUNTER" ]; then count=$(cat "$KASOMA_TEST_GO_COUNTER"); fi
    count=$((count + 1))
    printf '%s\\n' "$count" > "$KASOMA_TEST_GO_COUNTER"
    [ "$count" -gt "$KASOMA_TEST_GO_FAILURES" ]
    ;;
  'mod verify') exit "$KASOMA_TEST_GO_VERIFY_STATUS" ;;
  *) exit 99 ;;
esac
"""
    )
    fake_go.chmod(0o700)
    calls = tmp_path / "calls"
    result = subprocess.run(
        ["sh", str(HELPER)],
        env=os.environ
        | {
            "PATH": str(tmp_path) + os.pathsep + os.environ["PATH"],
            "KASOMA_TEST_GO_LOG": str(calls),
            "KASOMA_TEST_GO_COUNTER": str(tmp_path / "counter"),
            "KASOMA_TEST_GO_FAILURES": str(failures),
            "KASOMA_TEST_GO_VERIFY_STATUS": str(verify_status),
        },
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    assert result.returncode == status
    assert calls.read_text().splitlines() == ["mod download"] * downloads + (
        ["mod verify"] if verified else []
    )
    assert result.stderr.count("retrying pinned dependencies") == downloads - 1
