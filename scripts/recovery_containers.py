"""ADR-065: exclusively owned, bounded disposable local recovery services."""

import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from typing import Literal

LABEL = "org.kasoma.synthetic-recovery"
BROWSER_LABEL = "org.kasoma.synthetic-browser"
PARTS = {"source-db", "destination-db", "source-objects", "destination-objects"}


class RecoveryCommandError(RuntimeError):
    def __init__(self, kind: str) -> None:
        self.kind = (
            kind
            if kind
            in {
                "TIMEOUT",
                "IMAGE_UNAVAILABLE",
                "NAME_CONFLICT",
                "STORAGE_FULL",
                "DOCKER_UNAVAILABLE",
            }
            else "COMMAND_FAILED"
        )
        super().__init__(self.kind)


def image_id(value: str) -> str:
    if re.fullmatch(r"sha256:[a-f0-9]{64}", value) is None:
        raise ValueError("RECOVERY_IMAGE_INVALID")
    return value


def invocation_id(value: str) -> str:
    if re.fullmatch(r"[a-f0-9]{32}", value) is None:
        raise ValueError("RECOVERY_INVOCATION_INVALID")
    return value


def command(args: list[str], *, environment: dict[str, str] | None = None) -> str:
    try:
        result = subprocess.run(
            args,
            env=dict(os.environ, **(environment or {})),
            capture_output=True,
            text=True,
            check=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        raise RecoveryCommandError("TIMEOUT") from None
    except subprocess.CalledProcessError as error:
        diagnostic = (error.stderr or "").lower()
        kind = next(
            (
                value
                for phrase, value in (
                    ("no such image", "IMAGE_UNAVAILABLE"),
                    ("container name", "NAME_CONFLICT"),
                    ("no space left", "STORAGE_FULL"),
                    ("cannot connect to the docker daemon", "DOCKER_UNAVAILABLE"),
                )
                if phrase in diagnostic
            ),
            "COMMAND_FAILED",
        )
        raise RecoveryCommandError(kind) from None
    return result.stdout.strip()


def compose_image(service: str) -> str:
    approved = {
        "postgres": "pgvector/pgvector:0.8.2-pg16",
        "minio": "kasoma-minio:2025-09-07-source",
    }
    if service not in approved:
        raise ValueError("RECOVERY_SERVICE_INVALID")
    configuration = json.loads(command(["docker", "compose", "config", "--format", "json"]))
    reference = configuration.get("services", {}).get(service, {}).get("image")
    if reference != approved[service]:
        raise ValueError("RECOVERY_IMAGE_UNAVAILABLE")
    return image_id(command(["docker", "image", "inspect", "--format", "{{.Id}}", reference]))


@dataclass(repr=False)
class OwnedServices:
    invocation: str
    created: dict[str, str] = field(default_factory=dict)
    uncertain: list[str] = field(default_factory=list)
    purpose: Literal["recovery", "browser"] = field(default="recovery", kw_only=True)

    def __post_init__(self) -> None:
        invocation_id(self.invocation)
        if self.purpose not in {"recovery", "browser"}:
            raise ValueError("RECOVERY_PURPOSE_INVALID")

    @property
    def label(self) -> str:
        if self.purpose not in {"recovery", "browser"}:
            raise ValueError("RECOVERY_PURPOSE_INVALID")
        return LABEL if self.purpose == "recovery" else BROWSER_LABEL

    def name(self, part: str) -> str:
        if self.purpose not in {"recovery", "browser"}:
            raise ValueError("RECOVERY_PURPOSE_INVALID")
        if part not in PARTS or (self.purpose == "browser" and part != "source-db"):
            raise ValueError("RECOVERY_COMPONENT_INVALID")
        return f"kasoma-{self.purpose}-{part}-{self.invocation}"

    def create(self, part: str, image: str, environment: dict[str, str]) -> str:
        name = self.name(part)
        if part not in PARTS or part in self.created:
            raise ValueError("RECOVERY_COMPONENT_INVALID")
        image_id(image)
        database = part.endswith("-db")
        expected = (
            {"POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB"}
            if database
            else {"MINIO_ROOT_USER", "MINIO_ROOT_PASSWORD"}
        )
        if set(environment) != expected or any(not value for value in environment.values()):
            raise ValueError("RECOVERY_ENVIRONMENT_INVALID")
        port, path, size = (
            (5432, "/var/lib/postgresql/data", "256m") if database else (9000, "/data", "64m")
        )
        args = [
            "docker",
            "create",
            "--pull=never",
            "--name",
            name,
            "--label",
            f"{self.label}={self.invocation}",
            "--memory",
            "512m",
            "--pids-limit",
            "256",
            "--publish",
            f"127.0.0.1::{port}",
            "--tmpfs",
            f"{path}:rw,size={size}",
        ]
        for key in sorted(environment):
            args.extend(["--env", key])
        args.append(image)
        if not database:
            args.extend(
                ["server", "/data", "--address", ":9000", "--console-address", "127.0.0.1:9001"]
            )
        self.uncertain.append(part)
        cid = command(args, environment=environment)
        if re.fullmatch(r"[a-f0-9]{64}", cid) is None:
            # A derived name is never cleanup authority after an ambiguous create.
            raise ValueError("RECOVERY_CREATION_ID_UNAVAILABLE")
        self.created[part] = cid
        self.uncertain.remove(part)
        command(["docker", "start", cid])
        return cid

    def inspect_owned(self, part: str) -> dict[str, object]:
        self.name(part)
        cid = self.created[part]
        result = json.loads(command(["docker", "inspect", cid]))
        if not isinstance(result, list) or len(result) != 1 or not isinstance(result[0], dict):
            raise ValueError("RECOVERY_OWNERSHIP_UNAVAILABLE")
        item = result[0]
        if (
            item.get("Id") != cid
            or item.get("Config", {}).get("Labels", {}).get(self.label) != self.invocation
        ):
            raise ValueError("RECOVERY_OWNERSHIP_MISMATCH")
        if any(mount.get("Type") in {"bind", "volume"} for mount in item.get("Mounts", [])):
            raise ValueError("RECOVERY_PERSISTENT_MOUNT_REFUSED")
        return item

    def port(self, part: str) -> int:
        item = self.inspect_owned(part)
        port = "5432/tcp" if part.endswith("-db") else "9000/tcp"
        # Docker inspection is untrusted structural input. Never use arbitrary URLs.
        network = item.get("NetworkSettings")
        if not isinstance(network, dict) or not isinstance(network.get("Ports"), dict):
            raise ValueError("RECOVERY_PORT_UNAVAILABLE")
        bindings = network["Ports"].get(port)
        if not isinstance(bindings, list) or len(bindings) != 1:
            raise ValueError("RECOVERY_PORT_UNAVAILABLE")
        binding = bindings[0]
        if not isinstance(binding, dict) or binding.get("HostIp") != "127.0.0.1":
            raise ValueError("RECOVERY_NONLOCAL_PORT_REFUSED")
        value = binding.get("HostPort")
        if (
            not isinstance(value, str)
            or re.fullmatch(r"[0-9]{4,5}", value) is None
            or not 1024 <= int(value) <= 65535
        ):
            raise ValueError("RECOVERY_PORT_UNAVAILABLE")
        return int(value)

    def cleanup(self) -> list[str]:
        failed = [self.name(part) for part in self.uncertain]
        for part, cid in reversed(self.created.items()):
            try:
                self.inspect_owned(part)
                command(["docker", "rm", "--force", cid])
            except Exception:
                failed.append(self.name(part))
        return failed

    def stop(self, part: str) -> None:
        self.inspect_owned(part)
        command(["docker", "stop", "--time", "10", self.created[part]])
        item = self.inspect_owned(part)
        state = item.get("State")
        if not isinstance(state, dict) or state.get("Running") is not False:
            raise ValueError("RECOVERY_SOURCE_STILL_RUNNING")
