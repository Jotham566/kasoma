"""Explicit synthetic workflow fixture; never imported by production entry points."""

from datetime import timedelta
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.content import ContentService
from services.content_contracts import CHECKLIST, CreateDraft, ReviewInput, Transition
from services.domain.content import ItemVersion
from services.identity import IdentityService
from services.identity_contracts import OTPRequest, OTPVerify
from services.providers import FakeMessagingProvider
from services.staff import provision


def seed_assessment(identity: IdentityService) -> None:
    if identity.settings.app_env not in {"development", "test"}:
        raise ValueError("Synthetic fixtures only")
    with Session(identity.engine) as db:
        existing = list(
            db.scalars(
                select(ItemVersion.id).where(
                    ItemVersion.document["title"].as_string().like("Synthetic assessment fixture %")
                )
            )
        )
        if len(existing) >= 30:
            return
    # Isolate fixture delivery from configured interactive Mailpit; no delivery side effects.
    fake = FakeMessagingProvider()
    clock = identity.clock
    service = IdentityService(
        identity.engine,
        identity.settings,
        fake,
        fake,
        clock=lambda: clock() - timedelta(minutes=2),
        code=lambda: "246810",
    )
    tokens = []
    for role in ["CONTENT_AUTHOR", "ACADEMIC_REVIEWER"]:
        email = f"fixture-{role.lower()}@example.invalid"
        challenge = service.request_otp(OTPRequest(identifier=email, device_id=uuid4()), role, None)
        credentials = service.verify(
            OTPVerify(challenge_id=challenge.challenge_id, code="246810"), None, str(uuid4())
        )
        provision(service, email, role)
        tokens.append(credentials.access_token)
    content = ContentService(service)
    context = content.context(tokens[0])
    for topic in context.topics:
        concept = next(c for c in context.concepts if c.parent_id == topic.id)
        for index in range(5):
            title = f"Synthetic assessment fixture {topic.id}/{index}"
            with Session(identity.engine) as db:
                if db.scalar(
                    select(ItemVersion.id).where(ItemVersion.document["title"].as_string() == title)
                ):
                    continue
            doc = {
                "title": title,
                "topic_id": topic.id,
                "concept_id": concept.id,
                "learning_outcome_reference": concept.syllabus_reference,
                "competency_mappings": [{"competency_id": context.competencies[0].id, "weight": 1}],
                "prompt": f"Synthetic interface check {index + 1}: choose the label Alpha.",
                "choices": [{"id": "A", "text": "Alpha"}, {"id": "B", "text": "Beta"}],
                "correct_choice_id": "A",
                "worked_solution": "The requested label is Alpha, option A.",
                "remediation": "Read the labels and compare them with the requested label.",
                "source": "Original synthetic software fixture",
                "rights_status": "ORIGINAL_KASOMA",
                "rights_evidence": "Original software fixture; no external source",
                "rights_conditions": "Synthetic testing only; not academic release content",
            }
            version = content.create(
                tokens[0],
                CreateDraft(
                    subject_id=topic.parent_id,
                    document=doc,
                    change_reason="Explicit synthetic fixture setup",
                ),
                uuid4(),
                uuid4(),
            )
            version = content.mutate(
                tokens[0],
                version.id,
                "submit",
                Transition(
                    expected_revision=version.revision, reason="Synthetic workflow submission"
                ),
                uuid4(),
                uuid4(),
            )
            content.mutate(
                tokens[1],
                version.id,
                "review",
                ReviewInput(
                    expected_revision=version.revision,
                    reason="Synthetic software fixture checklist; not academic approval",
                    decision="APPROVE",
                    checklist=sorted(CHECKLIST),
                ),
                uuid4(),
                uuid4(),
            )


def main() -> None:
    from services.config import Settings
    from services.database import engine_for

    config = Settings()
    engine = engine_for(config)
    try:
        fake = FakeMessagingProvider()
        seed_assessment(IdentityService(engine, config, fake, fake))
    finally:
        engine.dispose()
    print("Synthetic assessment workflow fixtures ready; excluded from academic release counts.")


if __name__ == "__main__":
    main()
