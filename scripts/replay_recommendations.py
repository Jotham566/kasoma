"""Read-only replay of immutable recommendation inputs and committed plans."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.config import Settings
from services.database import engine_for
from services.domain.assessment import AssessmentSession, RecommendationSnapshot
from services.recommendation_engine import RankedPlan, replay


def verify(db: Session) -> int:
    checked = 0
    for row in db.scalars(select(RecommendationSnapshot)):
        replay(RankedPlan.model_validate(row.snapshot))
        checked += 1
    for session in db.scalars(
        select(AssessmentSession).where(AssessmentSession.recommendation_snapshot.is_not(None))
    ):
        replay(RankedPlan.model_validate(session.recommendation_snapshot))
        checked += 1
    return checked


def main() -> None:
    settings = Settings()
    if settings.app_env not in {"development", "test"}:
        raise ValueError("Local synthetic replay only")
    engine = engine_for(settings)
    try:
        with Session(engine) as db:
            count = verify(db)
        print(f"Recommendation replay matched {count} snapshots; no data changed.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
