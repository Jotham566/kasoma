"""Drain a bounded batch using the same processor as the local Celery schedule."""

from services.config import Settings
from services.content_imports import process_imports
from services.database import engine_for
from services.identity import IdentityService
from services.providers import FakeMessagingProvider


def main() -> None:
    settings = Settings()
    engine = engine_for(settings)
    try:
        fake = FakeMessagingProvider()
        count = process_imports(IdentityService(engine, settings, fake, fake))
        print(f"Draft import jobs processed: {count}")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
