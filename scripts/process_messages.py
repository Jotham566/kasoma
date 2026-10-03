"""Drain bounded synthetic channel jobs using the worker's production-shaped local path."""

from services.config import Settings
from services.database import engine_for
from services.identity import IdentityService
from services.providers import FakeMessagingProvider
from services.whatsapp_jobs import process_messages


def main() -> None:
    settings = Settings()
    engine = engine_for(settings)
    try:
        fake = FakeMessagingProvider()
        count = process_messages(IdentityService(engine, settings, fake, fake))
        print(f"Synthetic channel jobs processed: {count}")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
