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


def seed_assessment(
    identity: IdentityService,
    numeric: bool = False,
    mathematics_only: bool = False,
    diagnostic: bool = False,
) -> None:
    if identity.settings.app_env not in {"development", "test"}:
        raise ValueError("Synthetic fixtures only")
    prefix = "Synthetic numeric fixture" if numeric else "Synthetic assessment fixture"
    if diagnostic:
        prefix = "Synthetic diagnostic fixture"
    expected_count = 90 if diagnostic else (5 if numeric else (15 if mathematics_only else 30))
    with Session(identity.engine) as db:
        existing = list(
            db.scalars(
                select(ItemVersion.id).where(
                    ItemVersion.document["title"].as_string().like(prefix + " %")
                )
            )
        )
        if len(existing) >= expected_count:
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
        namespace = "diagnostic-" if diagnostic else ("numeric-" if numeric else "")
        email = f"fixture-{namespace}{role.lower()}@example.invalid"
        challenge = service.request_otp(OTPRequest(identifier=email, device_id=uuid4()), role, None)
        credentials = service.verify(
            OTPVerify(challenge_id=challenge.challenge_id, code="246810"), None, str(uuid4())
        )
        provision(service, email, role)
        tokens.append(credentials.access_token)
    content = ContentService(service)
    context = content.context(tokens[0])
    math_id = next(s.id for s in context.subjects if s.name == "Mathematics")
    for topic in context.topics:
        if numeric and topic.name != "Electricity and Magnetism":
            continue
        if mathematics_only and topic.parent_id != math_id:
            continue
        concept = next(c for c in context.concepts if c.parent_id == topic.id)
        for index in range(15 if diagnostic else 5):
            title = f"{prefix} {topic.id}/{index}"
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
            if diagnostic:
                doc.update(
                    {
                        "difficulty": ["STANDARD", "FOUNDATIONAL", "CHALLENGING"][index % 3],
                        "competency_mappings": [
                            {"competency_id": context.competencies[index % 2].id, "weight": 1}
                        ],
                    }
                )
            if numeric or (diagnostic and topic.parent_id != math_id):
                doc.update(
                    {
                        "response_type": "NUMERIC",
                        "choices": [],
                        "correct_choice_id": "",
                        "prompt": (
                            f"Synthetic length check {index + 1}: "
                            "enter a length equivalent to 100 cm, using three significant figures."
                        ),
                        "worked_solution": (
                            "100 cm is 1.00 m, or 1.00e2 cm, using three significant figures."
                        ),
                        "remediation": "Check the unit and significant figures.",
                        "numeric_spec": {
                            "expected_value": "1",
                            "canonical_unit": "m",
                            "units": [
                                {"label": "m", "factor": "1", "offset": "0"},
                                {"label": "cm", "factor": "1/100", "offset": "0"},
                            ],
                            "absolute_tolerance": "0",
                            "relative_tolerance": "0",
                            "accepted_forms": ["DECIMAL", "SCIENTIFIC"],
                            "significant_figures_policy": "EXACT",
                            "significant_figures": 3,
                        },
                    }
                )
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
    import argparse

    from services.config import Settings
    from services.database import engine_for

    parser = argparse.ArgumentParser()
    parser.add_argument("--numeric", action="store_true")
    parser.add_argument("--diagnostic", action="store_true")
    args = parser.parse_args()
    config = Settings()
    engine = engine_for(config)
    try:
        fake = FakeMessagingProvider()
        seed_assessment(
            IdentityService(engine, config, fake, fake),
            numeric=args.numeric,
            diagnostic=args.diagnostic,
        )
    finally:
        engine.dispose()
    print("Synthetic assessment workflow fixtures ready; excluded from academic release counts.")


if __name__ == "__main__":
    main()
