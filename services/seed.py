"""Idempotent local catalog only. Scenario fixtures await their domain migrations."""

from uuid import NAMESPACE_URL, UUID, uuid5

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from services.config import Settings
from services.database import engine_for
from services.domain.curriculum import Level, Subject, Topic

CLUSTERS = {
    "Mathematics": [
        "Algebra and Functions",
        "Geometry, Trigonometry and Measurement",
        "Statistics and Probability",
    ],
    "Physics": ["Mechanics and Energy", "Waves, Light and Sound", "Electricity and Magnetism"],
}


def fixture_id(name: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"kasoma:synthetic:v1:{name}")


def seed(settings: Settings) -> None:
    if settings.app_env != "development":
        raise ValueError("Seeding is restricted to the local development environment")
    engine = engine_for(settings)
    try:
        with Session(engine) as session, session.begin():
            session.execute(
                insert(Level)
                .values(id=fixture_id("S4"), name="S4")
                .on_conflict_do_nothing(index_elements=["id"])
            )
            for subject, topics in CLUSTERS.items():
                session.execute(
                    insert(Subject)
                    .values(
                        id=fixture_id(subject),
                        level_id=fixture_id("S4"),
                        name=subject,
                    )
                    .on_conflict_do_nothing(index_elements=["id"])
                )
                for topic in topics:
                    session.execute(
                        insert(Topic)
                        .values(
                            id=fixture_id(topic),
                            subject_id=fixture_id(subject),
                            name=topic,
                        )
                        .on_conflict_do_nothing(index_elements=["id"])
                    )
    finally:
        engine.dispose()


if __name__ == "__main__":
    seed(Settings())
    print("Synthetic local catalog seeded: S4, two subjects, six clusters.")
