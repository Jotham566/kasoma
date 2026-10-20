import os
import subprocess
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.engine import make_url

from apps.api.main import create_app
from scripts.migration_diagnostics import classify
from services.config import Settings
from services.database import engine_for
from services.identity import IdentityService
from services.identity_contracts import OTPRequest, OTPVerify
from services.providers import FakeMessagingProvider
from services.seed import seed
from services.staff import provision


@pytest.fixture
def identity(request):
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
    migration_target = getattr(request, "param", "head")
    for target in ["0001", migration_target, migration_target]:
        try:
            subprocess.run(
                [
                    "uv",
                    "run",
                    "--frozen",
                    "alembic",
                    "-c",
                    "apps/api/alembic.ini",
                    "upgrade",
                    target,
                ],
                check=True,
                env=env,
                capture_output=True,
            )
        except subprocess.CalledProcessError as failure:
            # Keep failures failed without rendering environment, SQL or credentials.
            raise RuntimeError(
                f"Synthetic migration failed ({classify(failure.stderr)}); diagnostics withheld"
            ) from None
        if target == "0001":
            seed(config, foundation_only=True)
    local = engine_for(config)
    now = [datetime(2026, 9, 23, 12, 0, tzinfo=UTC)]
    messages = FakeMessagingProvider()
    service = IdentityService(local, config, messages, messages, lambda: now[0], lambda: "246810")
    with TestClient(
        create_app(config, service, channel_wakeup=lambda settings, request_id: None)
    ) as client:
        yield service, client, messages, now
    local.dispose()
    # Keep isolated synthetic schema for debugging; no destructive teardown.
    engine.dispose()


@pytest.fixture
def content(identity):
    identity_service, client, messages, now = identity
    seed(identity_service.settings)
    actors = {}
    for name, roles in {
        "author": ["CONTENT_AUTHOR", "ACADEMIC_REVIEWER"],
        "reviewer": ["ACADEMIC_REVIEWER"],
        "second": ["ACADEMIC_REVIEWER"],
        "other": ["CONTENT_AUTHOR"],
        "admin": ["ADMIN"],
        "support": ["SUPPORT_READONLY"],
        "learner": [],
    }.items():
        email = f"{name}@example.invalid"
        challenge = identity_service.request_otp(
            OTPRequest(identifier=email, device_id=uuid4()), name, None
        )
        credentials = identity_service.verify(
            OTPVerify(challenge_id=challenge.challenge_id, code="246810"), None, str(uuid4())
        )
        for role in roles:
            provision(identity_service, email, role)
        actors[name] = {"Authorization": "Bearer " + credentials.access_token}
    context = client.get("/api/v1/admin/content-context", headers=actors["author"]).json()
    subject = context["subjects"][0]
    topic = next(t for t in context["topics"] if t["parent_id"] == subject["id"])
    concept = next(c for c in context["concepts"] if c["parent_id"] == topic["id"])
    document = {
        "title": "Synthetic selector fixture",
        "topic_id": topic["id"],
        "concept_id": concept["id"],
        "competency_mappings": [{"competency_id": context["competencies"][0]["id"], "weight": 1}],
        "learning_outcome_reference": concept["syllabus_reference"],
        "prompt": "Synthetic test: choose the option labelled Alpha.",
        "choices": [{"id": "A", "text": "Alpha"}, {"id": "B", "text": "Beta"}],
        "correct_choice_id": "A",
        "worked_solution": "The requested label is Alpha, option A.",
        "remediation": "Read the two labels again.",
        "source": "Original synthetic workflow fixture",
        "rights_status": "ORIGINAL_KASOMA",
        "rights_evidence": "Original fixture, no third-party material",
        "rights_conditions": "Test use only; not academic release content",
    }
    return (
        identity_service,
        client,
        actors,
        {
            "subject_id": subject["id"],
            "document": document,
            "change_reason": "Synthetic workflow test",
        },
    )
