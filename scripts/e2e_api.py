"""Isolated synthetic Playwright API; never imported by application entry points."""

import os
import subprocess
from uuid import uuid4

import uvicorn
from sqlalchemy import text
from sqlalchemy.engine import make_url

from apps.api.main import create_app
from services.config import Settings
from services.database import engine_for
from services.identity import IdentityService
from services.providers import FakeMessagingProvider
from services.seed import seed


def main() -> None:
    config = Settings()
    engine = engine_for(config)
    schema = "e2e_" + uuid4().hex
    with engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    url = make_url(config.database_url.get_secret_value()).update_query_dict(
        {"options": f"-csearch_path={schema},public"}
    )
    config = Settings(database_url=url.render_as_string(hide_password=False), email_provider="fake")
    subprocess.run(
        ["uv", "run", "--frozen", "alembic", "-c", "apps/api/alembic.ini", "upgrade", "head"],
        env=os.environ | {"DATABASE_URL": config.database_url.get_secret_value()},
        check=True,
        capture_output=True,
    )
    seed(config)
    engine.dispose()
    engine = engine_for(config)
    messages = FakeMessagingProvider()
    service = IdentityService(engine, config, messages, messages, code=lambda: "246810")
    try:
        uvicorn.run(create_app(config, service), host="127.0.0.1", port=8000, access_log=False)
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
