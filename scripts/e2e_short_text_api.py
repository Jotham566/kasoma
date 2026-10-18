"""Isolated synthetic browser harness; no normal application imports this fixture authority."""

import os
import subprocess
from threading import Event, Thread
from uuid import uuid4

import uvicorn
from sqlalchemy import select, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from apps.api.main import create_app
from scripts.assessment_fixtures import seed_assessment
from scripts.grading_fixtures import unapproved_band
from scripts.short_text_fixture_model import SyntheticRubricModel
from services.assessment import AssessmentService
from services.config import Settings
from services.database import engine_for
from services.domain.curriculum import Subject, Topic
from services.grading_band_store import register
from services.identity import IdentityService
from services.providers import FakeMessagingProvider
from services.seed import seed
from services.short_text_eligibility import GradingScope
from services.short_text_policy import ShortTextPolicy
from services.short_text_processor import ShortTextProcessor


def main() -> None:
    baseline = Settings()
    engine = engine_for(baseline)
    schema = "e2e_short_text_" + uuid4().hex
    with engine.begin() as db:
        db.execute(text(f'CREATE SCHEMA "{schema}"'))
    url = make_url(baseline.database_url.get_secret_value()).update_query_dict(
        {"options": f"-csearch_path={schema},public"}
    )
    config = Settings(
        database_url=url.render_as_string(hide_password=False),
        email_provider="fake",
        model_provider="fake",
        short_text_enabled=True,
    )
    subprocess.run(
        ["uv", "run", "--frozen", "alembic", "-c", "apps/api/alembic.ini", "upgrade", "head"],
        check=True,
        capture_output=True,
        env=os.environ | {"DATABASE_URL": config.database_url.get_secret_value()},
    )
    seed(config)
    engine.dispose()
    engine = engine_for(config)
    fake = FakeMessagingProvider()
    identity = IdentityService(engine, config, fake, fake, code=lambda: "246810")
    seed_assessment(identity, short_text=True, diagnostic=True, mathematics_only=True)
    band_ids = set()
    with Session(engine) as db, db.begin():
        if db.scalar(text("SELECT current_schema()")) != schema:
            raise ValueError("Synthetic authority requires this harness's owned schema")
        subject = db.scalar(select(Subject).where(Subject.name == "Mathematics"))
        if subject is None:
            raise ValueError("Synthetic Mathematics scope missing")
        for topic in db.scalars(select(Topic).where(Topic.subject_id == subject.id)):
            band = unapproved_band(
                GradingScope(
                    subject_id=subject.id,
                    topic_id=topic.id,
                    language="en",
                    model_version=config.short_text_model_version,
                    prompt_version=config.short_text_prompt_version,
                    configuration_version=config.short_text_configuration_version,
                )
            ).model_copy(
                update={
                    "approval_id": uuid4(),
                    "approved_at": identity.clock(),
                    "subgroup_review": "APPROVED",
                }
            )
            register(db, band, identity.clock())
            db.execute(
                text("""UPDATE grading_bands SET enabled=true,activated_at=:now,
                updated_at=:now,revision=revision+1 WHERE id=:id"""),
                {"id": band.id, "now": identity.clock()},
            )
            band_ids.add(band.id)
    policy = ShortTextPolicy(identity, lambda band: band.id in band_ids)
    processor = ShortTextProcessor(
        AssessmentService(identity, policy),
        SyntheticRubricModel(),
        safety=lambda context, response: response.strip() == "Alpha",
    )
    app = create_app(
        config, identity, short_text_policy=policy, grading_wakeup=lambda settings, request_id: None
    )
    stop = Event()

    def drain() -> None:
        while not stop.wait(0.25):
            processor.process_one()

    worker = Thread(target=drain, daemon=True)
    worker.start()
    try:
        uvicorn.run(app, host="127.0.0.1", port=18000, access_log=False)
    finally:
        stop.set()
        worker.join(timeout=5)
        engine.dispose()


if __name__ == "__main__":
    main()
