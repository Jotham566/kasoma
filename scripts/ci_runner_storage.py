"""Fixed disposable-runner SDK cleanup; default invocation only reports root space."""

import argparse
import json
import os
import platform
import shutil
from pathlib import Path

WORKSPACE_ROOT = Path("/home/runner/work")
MINIMUM_FREE = 24 * 1024**3
MINIMUM_PHASE_FREE = 8 * 1024**3
SDKS = (
    ("DOTNET", Path("/usr/share/dotnet")),
    ("ANDROID", Path("/usr/local/lib/android/sdk")),
)


class StorageError(Exception):
    pass


def disposable_host() -> bool:
    try:
        base = WORKSPACE_ROOT
        workspace = Path(os.environ.get("GITHUB_WORKSPACE", "/")).resolve()
        temporary = Path(os.environ.get("RUNNER_TEMP", "/")).resolve()
        release = platform.freedesktop_os_release()
        return (
            platform.system() == "Linux"
            and release.get("ID") == "ubuntu"
            and release.get("VERSION_ID") == "24.04"
            and os.environ.get("CI") == "true"
            and os.environ.get("GITHUB_ACTIONS") == "true"
            and os.environ.get("KASOMA_CI_RUNNER_ENVIRONMENT") == "github-hosted"
            and os.environ.get("RUNNER_OS") == "Linux"
            and os.environ.get("RUNNER_ARCH") == "X64"
            and os.geteuid() == 0
            and workspace.is_relative_to(base)
            and len(workspace.relative_to(base).parts) == 2
            and workspace == Path.cwd().resolve()
            and temporary == base / "_temp"
            and bool(getattr(shutil.rmtree, "avoids_symlink_attacks", False))
        )
    except (OSError, ValueError, RuntimeError):
        return False


def report(stage: str) -> int:
    usage = shutil.disk_usage("/")
    print(
        json.dumps(
            {
                "event": "ci.storage",
                "stage": stage,
                "total_bytes": usage.total,
                "used_bytes": usage.used,
                "free_bytes": usage.free,
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return usage.free


def prepare() -> None:
    if not disposable_host():
        raise StorageError("NOT_DISPOSABLE_HOSTED_RUNNER")
    # Validate the complete fixed list before removing anything, including parent symlinks.
    for _, path in SDKS:
        try:
            unsafe = (
                path.resolve() != path or path.is_symlink() or (path.exists() and not path.is_dir())
            )
        except (OSError, RuntimeError):
            raise StorageError("UNSAFE_SDK_TARGET") from None
        if unsafe:
            raise StorageError("UNSAFE_SDK_TARGET")
    report("BEFORE_PREPARE")
    removed = []
    for label, path in SDKS:
        if path.exists():
            shutil.rmtree(path)
            removed.append(label)
    print(json.dumps({"event": "ci.storage.prepared", "removed": removed}), flush=True)
    if report("AFTER_PREPARE") < MINIMUM_FREE:
        raise StorageError("INSUFFICIENT_RUNNER_SPACE")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--prepare", action="store_true")
    modes.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.prepare:
            prepare()
        elif args.check:
            if report("CHECK") < MINIMUM_PHASE_FREE:
                raise StorageError("INSUFFICIENT_RUNNER_SPACE")
        else:
            report("DIAGNOSTIC")
    except StorageError as error:
        print(json.dumps({"event": "ci.storage.failed", "reason": str(error)}), flush=True)
        return 1
    except OSError:
        print(
            json.dumps({"event": "ci.storage.failed", "reason": "FILESYSTEM_UNAVAILABLE"}),
            flush=True,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
