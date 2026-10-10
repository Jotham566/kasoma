"""Original synthetic assessment evidence for an isolated recovery drill only."""

from datetime import date
from uuid import uuid4

from sqlalchemy.orm import Session

from scripts.assessment_fixtures import seed_assessment
from scripts.recovery_exports import RecoveryExport, populate_export
from services.assessment import AssessmentService
from services.assessment_contracts import ChoiceResponse, StartRevision, SubmitAnswer
from services.config import Settings
from services.database import engine_for
from services.domain.assessment import Attempt
from services.grading_work_store import claim_next, enqueue, finish_neutral
from services.identity import IdentityService
from services.identity_contracts import ConsentInput, OTPRequest, OTPVerify, ProfilePatch
from services.providers import FakeMessagingProvider
from services.seed import seed


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
        session = assessment.start(
            token, StartRevision(subject_id=subject, topic_id=topic), uuid4(), uuid4()
        )
        item = assessment.next_item(token, session.id, uuid4())
        assessment.submit(
            token,
            session.id,
            SubmitAnswer(
                session_item_id=item.session_item_id,
                response=ChoiceResponse(choice_id="A"),
            ),
            uuid4(),
            uuid4(),
        )
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
        return populate_export(identity, token)
    finally:
        engine.dispose()
