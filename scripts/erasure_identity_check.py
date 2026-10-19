"""ADR-069: run a closed identity test target against a fresh owned local database."""

import os
import signal
import subprocess  # nosec B404 -- fixed absolute Make target; no shell or user-selected command.

from scripts.browser_database import cleanup_on_termination, erasure_test_database
from services.config import Settings


def verify(environment: dict[str, str]) -> None:
    process = subprocess.Popen(  # nosec B603 -- constant argv; credentials only in private env.
        ["/usr/bin/make", "test-erasure-identity"], env=environment, start_new_session=True
    )
    try:
        if process.wait(timeout=600) != 0:
            raise RuntimeError("Synthetic identity verification failed")
    finally:
        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait(timeout=10)


def run() -> None:
    settings = Settings(model_provider="fake", email_provider="fake")
    with cleanup_on_termination(), erasure_test_database(settings) as config:
        environment = os.environ | {
            "APP_ENV": "development",
            "DATABASE_URL": config.database_url.get_secret_value(),
            "IDENTITY_ENCRYPTION_KEY": config.identity_encryption_key.get_secret_value(),
            "IDENTITY_LOOKUP_KEY": config.identity_lookup_key.get_secret_value(),
            "JWT_SIGNING_KEY": config.jwt_signing_key.get_secret_value(),
            "MODEL_PROVIDER": "fake",
            "EMAIL_PROVIDER": "fake",
            "SMS_PROVIDER": "fake",
            "WHATSAPP_PROVIDER": "fake",
            "ALLOW_EXTERNAL_API_CALLS": "false",
        }
        # No caller-controlled selector, shell, URL, SQL, role or cleanup target.
        verify(environment)


def main() -> None:
    try:
        run()
    except SystemExit:
        # A termination signal unwinds child/container cleanup but is never a pass.
        raise SystemExit(143) from None


if __name__ == "__main__":
    main()
