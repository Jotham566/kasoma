import os
import subprocess
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.engine import make_url

from apps.api.main import create_app
from services.config import Settings
from services.database import engine_for
from services.identity import IdentityService
from services.providers import FakeMessagingProvider
from services.seed import seed


@pytest.fixture
def identity():
    baseline = Settings()
    engine = engine_for(baseline)
    schema = "identity_test_" + uuid4().hex
    with engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    url = make_url(baseline.database_url.get_secret_value()).update_query_dict(
        {"options": f"-csearch_path={schema},public"}
    )
    config = Settings(database_url=url.render_as_string(hide_password=False), email_provider="fake")
    env = os.environ | {"DATABASE_URL": config.database_url.get_secret_value()}
    # Exercise actual foundation -> identity migration, preserving the seeded catalog.
    for target in ["0001", "head", "head"]:
        subprocess.run(
            ["uv", "run", "--frozen", "alembic", "-c", "apps/api/alembic.ini", "upgrade", target],
            check=True,
            env=env,
            capture_output=True,
        )
        if target == "0001":
            seed(config, foundation_only=True)
    local = engine_for(config)
    now = [datetime(2026, 9, 23, 12, 0, tzinfo=UTC)]
    messages = FakeMessagingProvider()
    service = IdentityService(local, config, messages, messages, lambda: now[0], lambda: "246810")
    with TestClient(create_app(config, service)) as client:
        yield service, client, messages, now
    local.dispose()
    # Keep isolated synthetic schema for debugging; no destructive teardown.
    engine.dispose()
