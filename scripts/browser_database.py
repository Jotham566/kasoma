"""ADR-068: one exclusively owned local PostgreSQL service per browser API process."""

import json
import secrets
import signal
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from time import monotonic, sleep
from types import FrameType
from uuid import uuid4

from cryptography.fernet import Fernet
from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.engine import URL

from scripts.recovery_containers import OwnedServices, compose_image
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


@contextmanager
def browser_database(settings: Settings) -> Iterator[Settings]:
    # Preserve the existing standard local Compose guard; never connect to its data.
    local_database_url(settings)
    if (
        settings.model_provider != "fake"
        or settings.email_provider != "fake"
        or settings.sms_provider != "fake"
        or settings.whatsapp_provider != "fake"
        or settings.allow_external_api_calls
    ):
        raise ValueError("Browser fixtures require fake providers")
    invocation = uuid4().hex
    owned = OwnedServices(invocation, purpose="browser")
    engine = None
    try:
        password = secrets.token_urlsafe(32)
        database = "kasoma_browser_" + invocation
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
                    "event": "e2e.database_created",
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
                        "Browser database startup unavailable; diagnostics withheld"
                    ) from None
                sleep(0.1)
            else:
                if observed != database:
                    raise ValueError("Browser database identity mismatch")
                break
        yield isolated
    except Exception:
        raise RuntimeError("Synthetic browser database unavailable; diagnostics withheld") from None
    finally:
        if engine is not None:
            engine.dispose()
        failed = owned.cleanup()
        print(
            json.dumps({"event": "e2e.database_cleanup", "cleanup_failed": failed}, sort_keys=True),
            file=sys.stderr,
            flush=True,
        )
        if failed:
            raise RuntimeError("Owned browser database cleanup failed; review reported ownership")
