"""ADR-068: one exclusively owned local PostgreSQL service per browser API process."""

import json
import os
import secrets
import signal
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from time import monotonic, sleep
from types import FrameType
from typing import Literal
from urllib.parse import urlsplit
from uuid import uuid4

from cryptography.fernet import Fernet
from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.engine import URL

from scripts.recovery_containers import OwnedServices, command, compose_image
from scripts.recovery_drill import local_database_url
from services.config import Settings
from services.database import engine_for


@contextmanager
def cleanup_on_termination() -> Iterator[None]:
    """Uvicorn re-raises SIGTERM after graceful shutdown; unwind owned-resource finally."""
    previous = signal.getsignal(signal.SIGTERM)

    def terminate(_number: int, _frame: FrameType | None) -> None:
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, terminate)
    try:
        yield
    finally:
        signal.signal(signal.SIGTERM, previous)


def unix_endpoint(value: str) -> bool:
    parsed = urlsplit(value)
    return bool(
        parsed.scheme == "unix"
        and not parsed.netloc
        and parsed.path.startswith("/")
        and not parsed.query
        and not parsed.fragment
        and not any(character in value for character in "\x00\r\n")
    )


@contextmanager
def pinned_local_docker() -> Iterator[None]:
    """Context inspection reads local metadata; pin one Unix endpoint for child commands."""
    previous_host = os.environ.get("DOCKER_HOST")
    previous_context = os.environ.get("DOCKER_CONTEXT")
    if previous_host and not unix_endpoint(previous_host):
        raise ValueError("Browser fixtures require a local Unix Docker endpoint")
    endpoint = (
        previous_host
        if previous_host and not previous_context
        else command(["docker", "context", "inspect", "--format", "{{.Endpoints.docker.Host}}"])
    )
    if not unix_endpoint(endpoint):
        raise ValueError("Browser fixtures require a local Unix Docker endpoint")
    os.environ["DOCKER_HOST"] = endpoint
    os.environ.pop("DOCKER_CONTEXT", None)
    try:
        yield
    finally:
        for key, value in [("DOCKER_HOST", previous_host), ("DOCKER_CONTEXT", previous_context)]:
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def require_test_profile(settings: Settings) -> None:
    # Preserve the existing standard local Compose guard; never connect to its data.
    local_database_url(settings)
    if (
        settings.model_provider != "fake"
        or settings.email_provider != "fake"
        or settings.sms_provider != "fake"
        or settings.whatsapp_provider != "fake"
        or settings.allow_external_api_calls
    ):
        raise ValueError("Synthetic fixtures require fake providers")


@contextmanager
def browser_database(settings: Settings) -> Iterator[Settings]:
    require_test_profile(settings)
    with pinned_local_docker():
        yield from _isolated_database(settings)


@contextmanager
def erasure_test_database(settings: Settings) -> Iterator[Settings]:
    """ADR-061/069 test source only; creates no execution capability or activation."""
    require_test_profile(settings)
    with pinned_local_docker():
        yield from _isolated_database(settings, purpose="erasure")


def _isolated_database(
    settings: Settings, *, purpose: Literal["browser", "erasure"] = "browser"
) -> Iterator[Settings]:
    invocation = uuid4().hex
    owned = OwnedServices(invocation, purpose=purpose)
    prefix = "e2e" if purpose == "browser" else "erasure.test"
    engine = None
    try:
        password = secrets.token_urlsafe(32)
        database = (
            "kasoma_browser_" if purpose == "browser" else "kasoma_erasure_test_"
        ) + invocation
        container_id = owned.create(
            "source-db",
            compose_image("postgres"),
            {
                "POSTGRES_USER": "kasoma",
                "POSTGRES_PASSWORD": password,
                "POSTGRES_DB": database,
            },
        )
        print(
            json.dumps(
                {
                    "event": prefix + ".database_created",
                    "container_id": container_id,
                    "invocation": invocation,
                },
                sort_keys=True,
            ),
            file=sys.stderr,
            flush=True,
        )
        url = URL.create(
            "postgresql+psycopg",
            username="kasoma",
            password=password,
            host="127.0.0.1",
            port=owned.port("source-db"),
            database=database,
        )
        fields = settings.model_dump() | {
            "database_url": SecretStr(url.render_as_string(hide_password=False)),
            "identity_encryption_key": SecretStr(Fernet.generate_key().decode()),
            "identity_lookup_key": SecretStr(secrets.token_urlsafe(48)),
            "jwt_signing_key": SecretStr(secrets.token_urlsafe(48)),
        }
        isolated = Settings(**fields)
        engine = engine_for(isolated)
        deadline = monotonic() + 30
        while True:
            try:
                with engine.connect() as db:
                    observed = db.scalar(text("SELECT current_database()"))
            except Exception:
                if monotonic() >= deadline:
                    raise RuntimeError(
                        "Synthetic test database startup unavailable; diagnostics withheld"
                    ) from None
                sleep(0.1)
            else:
                if observed != database:
                    raise ValueError("Synthetic test database identity mismatch")
                break
        yield isolated
    except Exception:
        raise RuntimeError("Synthetic test database unavailable; diagnostics withheld") from None
    finally:
        if engine is not None:
            engine.dispose()
        failed = owned.cleanup()
        print(
            json.dumps(
                {"event": prefix + ".database_cleanup", "cleanup_failed": failed}, sort_keys=True
            ),
            file=sys.stderr,
            flush=True,
        )
        if failed:
            raise RuntimeError("Owned test database cleanup failed; review reported ownership")
