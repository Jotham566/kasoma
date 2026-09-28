"""Isolated synthetic Playwright API; never imported by application entry points."""

import os
import subprocess
from datetime import timedelta
from uuid import uuid4

import uvicorn
from sqlalchemy import text
from sqlalchemy.engine import make_url

from apps.api.main import create_app
from scripts.assessment_fixtures import seed_assessment
from services.config import Settings
from services.database import engine_for
from services.identity import IdentityService
from services.identity_contracts import OTPRequest, OTPVerify
from services.providers import FakeMessagingProvider
from services.seed import seed
from services.staff import provision


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
    clock = service.clock
    service.clock = lambda: clock() - timedelta(seconds=61)
    for label, roles in {
        "author": ["CONTENT_AUTHOR", "ACADEMIC_REVIEWER"],
        "reviewer": ["ACADEMIC_REVIEWER"],
        "second": ["ACADEMIC_REVIEWER"],
    }.items():
        email = f"e2e-content-{label}@example.invalid"
        challenge = service.request_otp(
            OTPRequest(identifier=email, device_id=uuid4()), label, None
        )
        service.verify(
            OTPVerify(challenge_id=challenge.challenge_id, code="246810"), None, str(uuid4())
        )
        for role in roles:
            provision(service, email, role)
    service.clock = clock
    seed_assessment(service, mathematics_only=True, hints=True)
    seed_assessment(service, numeric=True, hints=True)
    seed_assessment(service, diagnostic=True, hints=True)
    try:
        uvicorn.run(create_app(config, service), host="127.0.0.1", port=18000, access_log=False)
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
