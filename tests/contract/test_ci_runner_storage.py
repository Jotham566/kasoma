"""CI guard tests use only synthetic temporary SDK directories; never real SDK cleanup."""

import json
import os
import subprocess
import sys
from types import SimpleNamespace

import pytest

from scripts import ci_runner_storage as storage


@pytest.fixture
def runner(tmp_path, monkeypatch):
    base = (tmp_path / "runner" / "work").resolve()
    workspace = base / "kasoma" / "kasoma"
    workspace.mkdir(parents=True)
    temporary = base / "_temp"
    temporary.mkdir()
    monkeypatch.chdir(workspace)
    monkeypatch.setattr(storage, "WORKSPACE_ROOT", base)
    monkeypatch.setattr(storage.platform, "system", lambda: "Linux")
    monkeypatch.setattr(
        storage.platform, "freedesktop_os_release", lambda: {"ID": "ubuntu", "VERSION_ID": "24.04"}
    )
    monkeypatch.setattr(storage.os, "geteuid", lambda: 0)
    for key, value in {
        "CI": "true",
        "GITHUB_ACTIONS": "true",
        "KASOMA_CI_RUNNER_ENVIRONMENT": "github-hosted",
        "RUNNER_OS": "Linux",
        "RUNNER_ARCH": "X64",
        "GITHUB_WORKSPACE": str(workspace),
        "RUNNER_TEMP": str(temporary),
    }.items():
        monkeypatch.setenv(key, value)
    sdks = (("DOTNET", tmp_path.resolve() / "dotnet"), ("ANDROID", tmp_path.resolve() / "android"))
    for _, path in sdks:
        path.mkdir()
        (path / "synthetic-sdk").write_text("fixture")
    monkeypatch.setattr(storage, "SDKS", sdks)
    monkeypatch.setattr(
        storage.shutil,
        "disk_usage",
        lambda _: SimpleNamespace(total=100 * 1024**3, used=50 * 1024**3, free=50 * 1024**3),
    )
    return sdks


@pytest.mark.parametrize(
    "key,value",
    [
        ("CI", "false"),
        ("GITHUB_ACTIONS", "false"),
        ("KASOMA_CI_RUNNER_ENVIRONMENT", "self-hosted"),
        ("RUNNER_OS", "macOS"),
        ("RUNNER_ARCH", "ARM64"),
        ("GITHUB_WORKSPACE", "/"),
        ("RUNNER_TEMP", "/tmp"),
    ],
)
def test_wrong_profile_refuses_before_mutation(runner, monkeypatch, key, value):
    monkeypatch.setenv(key, value)
    with pytest.raises(storage.StorageError, match="NOT_DISPOSABLE"):
        storage.prepare()
    assert all((path / "synthetic-sdk").exists() for _, path in runner)


@pytest.mark.parametrize("change", ["platform", "release", "uid", "cwd"])
def test_host_identity_mismatch_cannot_be_overridden_by_ci_environment(runner, monkeypatch, change):
    if change == "platform":
        monkeypatch.setattr(storage.platform, "system", lambda: "Darwin")
    elif change == "release":
        monkeypatch.setattr(
            storage.platform,
            "freedesktop_os_release",
            lambda: {"ID": "ubuntu", "VERSION_ID": "26.04"},
        )
    elif change == "uid":
        monkeypatch.setattr(storage.os, "geteuid", lambda: 1001)
    else:
        monkeypatch.chdir(runner[0][1])
    with pytest.raises(storage.StorageError, match="NOT_DISPOSABLE"):
        storage.prepare()
    assert all((path / "synthetic-sdk").exists() for _, path in runner)


def test_only_fixed_synthetic_sdk_roots_removed_and_report_has_no_environment(runner, capsys):
    outside = runner[0][1].parent / "workspace-data"
    outside.write_text("not an SDK")
    storage.prepare()
    assert all(not path.exists() for _, path in runner)
    assert outside.read_text() == "not an SDK"
    reports = [json.loads(row) for row in capsys.readouterr().out.splitlines()]
    assert [r.get("stage") for r in reports] == ["BEFORE_PREPARE", None, "AFTER_PREPARE"]
    assert reports[1] == {"event": "ci.storage.prepared", "removed": ["DOTNET", "ANDROID"]}
    assert all(
        set(r) <= {"event", "stage", "total_bytes", "used_bytes", "free_bytes", "removed"}
        for r in reports
    )


def test_unsafe_second_target_cannot_cause_partial_or_followed_deletion(runner, monkeypatch):
    first = runner[0]
    link = first[1].parent / "sdk-link"
    link.symlink_to(runner[1][1], target_is_directory=True)
    monkeypatch.setattr(storage, "SDKS", (first, ("ANDROID", link)))
    with pytest.raises(storage.StorageError, match="UNSAFE_SDK_TARGET"):
        storage.prepare()
    assert all((path / "synthetic-sdk").exists() for _, path in runner)
    assert link.is_symlink()


def test_insufficient_capacity_is_a_failure_after_bounded_owned_cleanup(runner, monkeypatch):
    monkeypatch.setattr(
        storage.shutil, "disk_usage", lambda _: SimpleNamespace(total=100, used=100, free=0)
    )
    with pytest.raises(storage.StorageError, match="INSUFFICIENT_RUNNER_SPACE"):
        storage.prepare()


def test_default_mode_is_read_only_and_local_prepare_is_refused():
    script = os.path.abspath(storage.__file__)
    report = subprocess.run([sys.executable, script], capture_output=True, text=True)
    assert report.returncode == 0
    assert json.loads(report.stdout)["stage"] == "DIAGNOSTIC"
    denied = subprocess.run(
        [sys.executable, script, "--prepare"],
        capture_output=True,
        text=True,
        env=os.environ | {"KASOMA_CI_RUNNER_ENVIRONMENT": "self-hosted"},
    )
    assert denied.returncode == 1
    assert json.loads(denied.stdout) == {
        "event": "ci.storage.failed",
        "reason": "NOT_DISPOSABLE_HOSTED_RUNNER",
    }


def test_parent_symlink_is_rejected_without_touching_either_sdk(runner, monkeypatch):
    parent = runner[0][1].parent / "sdk-parent"
    parent.symlink_to(runner[1][1], target_is_directory=True)
    inner = runner[1][1] / "inner"
    inner.mkdir()
    monkeypatch.setattr(storage, "SDKS", (runner[0], ("ANDROID", parent / "inner")))
    with pytest.raises(storage.StorageError, match="UNSAFE_SDK_TARGET"):
        storage.prepare()
    assert all((path / "synthetic-sdk").exists() for _, path in runner)
    assert inner.exists()


def test_non_directory_target_is_rejected_before_any_cleanup(runner, monkeypatch):
    file = runner[0][1].parent / "not-a-directory"
    file.write_text("fixture")
    monkeypatch.setattr(storage, "SDKS", (runner[0], ("ANDROID", file)))
    with pytest.raises(storage.StorageError, match="UNSAFE_SDK_TARGET"):
        storage.prepare()
    assert file.read_text() == "fixture"
    assert all((path / "synthetic-sdk").exists() for _, path in runner)


def test_symlink_loop_is_a_closed_refusal(runner, monkeypatch):
    loop = runner[0][1].parent / "loop"
    loop.symlink_to(loop)
    monkeypatch.setattr(storage, "SDKS", (runner[0], ("ANDROID", loop)))
    with pytest.raises(storage.StorageError, match="UNSAFE_SDK_TARGET"):
        storage.prepare()
    assert all((path / "synthetic-sdk").exists() for _, path in runner)


@pytest.mark.parametrize("argument", ["--target=/", "--minimum-free=0"])
def test_no_cli_path_or_capacity_override(argument):
    result = subprocess.run(
        [sys.executable, os.path.abspath(storage.__file__), argument], capture_output=True
    )
    assert result.returncode == 2


@pytest.mark.parametrize("sufficient", [False, True])
def test_phase_capacity_check_is_read_only(runner, monkeypatch, sufficient):
    monkeypatch.setattr(sys, "argv", ["ci_runner_storage", "--check"])
    monkeypatch.setattr(
        storage.shutil,
        "disk_usage",
        lambda _: SimpleNamespace(
            total=100 * 1024**3, used=0, free=storage.MINIMUM_PHASE_FREE if sufficient else 0
        ),
    )
    assert storage.main() == (0 if sufficient else 1)
    assert all((path / "synthetic-sdk").exists() for _, path in runner)
