"""Run one local operational snapshot/alert sweep without external delivery."""

from uuid import uuid4

from services.config import Settings
from services.database import engine_for
from services.identity import IdentityService
from services.operations import monitor
from services.providers import FakeMessagingProvider


def main() -> None:
    settings = Settings()
    engine = engine_for(settings)
    try:
        fake = FakeMessagingProvider()
        count = monitor(IdentityService(engine, settings, fake, fake), uuid4())
        print(f"Active operational alerts: {count}")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
