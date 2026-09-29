"""Run the same bounded expiry sweep as the local Celery schedule."""

from uuid import uuid4

from services.config import Settings
from services.data_exports import expire
from services.database import engine_for
from services.identity import IdentityService
from services.providers import FakeMessagingProvider


def main() -> None:
    settings = Settings()
    engine = engine_for(settings)
    try:
        fake = FakeMessagingProvider()
        count = expire(IdentityService(engine, settings, fake, fake), uuid4())
        print(f"Expired export copies removed: {count}; accountability evidence preserved.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
