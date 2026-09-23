import pytest

from services.config import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(
        _env_file=None,
        app_env="test",
        database_url="postgresql+psycopg://synthetic:synthetic@localhost:5432/synthetic",
        redis_url="redis://localhost:6379/15",
        object_storage_access_key="synthetic-test-only",
        object_storage_secret_key="synthetic-test-only",
        jwt_signing_key="synthetic-test-only",
        model_provider="fake",
        email_provider="fake",
    )
