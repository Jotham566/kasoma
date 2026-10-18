"""Original synthetic assessment evidence for an isolated recovery drill only."""

import re
from datetime import date
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from scripts.assessment_fixtures import seed_assessment
from scripts.grading_fixtures import unapproved_band
from scripts.recovery_channel_receipts import populate_channel_receipts
from scripts.recovery_exports import RecoveryExport, populate_export
from scripts.recovery_short_text import populate_short_text
from services.assessment import AssessmentService
from services.assessment_contracts import ChoiceResponse, StartRevision, SubmitAnswer
from services.config import Settings
from services.database import engine_for
from services.domain.assessment import Attempt
from services.grading_band_store import disable as disable_band
from services.grading_band_store import register as register_band
from services.grading_publications import publish
from services.grading_work_store import claim_next, enqueue, finish_neutral
from services.identity import IdentityService
from services.identity_contracts import ConsentInput, OTPRequest, OTPVerify, ProfilePatch
from services.providers import FakeMessagingProvider
from services.seed import seed
from services.short_text_eligibility import GradingScope


def populate(settings: Settings) -> RecoveryExport:
    seed(settings)
    engine = engine_for(settings)
    fake = FakeMessagingProvider()
    identity = IdentityService(engine, settings, fake, fake, code=lambda: "246810")
    try:
        seed_assessment(identity, mathematics_only=True)
        challenge = identity.request_otp(
            OTPRequest(identifier="recovery-learner@example.invalid", device_id=uuid4()),
            "synthetic-recovery",
            None,
        )
        token = identity.verify(
            OTPVerify(challenge_id=challenge.challenge_id, code="246810"), None, str(uuid4())
        ).access_token
        subject = next(
            subject.id for subject in identity.subjects() if subject.name == "Mathematics"
        )
        identity.update_profile(
            token,
            ProfilePatch(
                display_name="Synthetic recovery learner",
                birth_date=date(2000, 1, 1),
                subject_ids=[subject],
            ),
            str(uuid4()),
        )
        identity.consent(
            token,
            ConsentInput(
                consent_type="SELF",
                policy_version=settings.consent_policy_version,
                affirmative=True,
            ),
            uuid4(),
            str(uuid4()),
        )
        assessment = AssessmentService(identity)
        topic = assessment.topics(token, subject)[0].id
        band = unapproved_band(
            GradingScope(
                subject_id=subject,
                topic_id=topic,
                language="en",
                model_version="fake-v1",
                prompt_version="synthetic-v2",
                configuration_version="test-v1",
            )
        )
        with Session(engine) as db, db.begin():
            register_band(db, band, identity.clock())
            disable_band(db, band.id, identity.clock(), "MANUAL")
        session = assessment.start(
            token, StartRevision(subject_id=subject, topic_id=topic), uuid4(), uuid4()
        )
        item = assessment.next_item(token, session.id, uuid4())
        grade = assessment.submit(
            token,
            session.id,
            SubmitAnswer(
                session_item_id=item.session_item_id,
                response=ChoiceResponse(choice_id="A"),
            ),
            uuid4(),
            uuid4(),
        )
        # Owner-only synthetic transition in the drill's generated database. This is
        # storage recovery evidence, never a report authority or learner enablement.
        with Session(engine) as db, db.begin():
            database = db.scalar(text("SELECT current_database()"))
            if not re.fullmatch(r"kasoma_drill_src_[0-9a-f]{32}", database or ""):
                raise ValueError("Synthetic publication requires an isolated recovery source")
            publication_band = unapproved_band(band.scope).model_copy(
                update={
                    "approval_id": uuid4(),
                    "approved_at": identity.clock(),
                    "subgroup_review": "APPROVED",
                }
            )
            register_band(db, publication_band, identity.clock())
            db.execute(
                text("""UPDATE grading_bands SET enabled=true,activated_at=:now,
                updated_at=:now,revision=revision+1 WHERE id=:id"""),
                {"now": identity.clock(), "id": publication_band.id},
            )
            publish(db, publication_band.id, grade.attempt_id, identity.clock())
            disable_band(db, publication_band.id, identity.clock(), "MANUAL")
        # Valid ungraded synthetic attempt for durable-state recovery; no assignment
        # guard or academic eligibility is bypassed and no model call is performed.
        pending_item = assessment.next_item(token, session.id, uuid4())
        attempt_id = uuid4()
        with Session(engine) as db, db.begin():
            actor = assessment.authorize(db, token)
            db.add(
                Attempt(
                    id=attempt_id,
                    learner_id=actor,
                    session_item_id=pending_item.session_item_id,
                    item_version_id=pending_item.item_version_id,
                    choice_id="A",
                    response=None,
                    submitted_at=identity.clock(),
                    hint_count=0,
                    highest_hint_level=0,
                    channel="WEB",
                )
            )
            db.flush()
            enqueue(db, attempt_id, uuid4(), identity.clock())
        with Session(engine) as db, db.begin():
            work = claim_next(db, identity.clock())
            if work is None or work.claim_id is None:
                raise RuntimeError("Synthetic grading claim missing")
            finish_neutral(db, attempt_id, work.claim_id, identity.clock())
        # Finish the existing plan so its objective items are excluded from the
        # subsequent synthetic written-answer plan through the normal selector.
        for _ in range(3):
            remaining = assessment.next_item(token, session.id, uuid4())
            assessment.submit(
                token,
                session.id,
                SubmitAnswer(
                    session_item_id=remaining.session_item_id,
                    response=ChoiceResponse(choice_id="A"),
                ),
                uuid4(),
                uuid4(),
            )
        populate_short_text(identity, token, subject, topic)
        populate_channel_receipts(identity, token)
        return populate_export(identity, token)
    finally:
        engine.dispose()
