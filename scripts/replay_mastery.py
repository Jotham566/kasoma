"""Read-only local replay of every recorded projection; never invokes a provider."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.config import Settings
from services.database import engine_for
from services.domain.mastery import MasteryEstimate, MasteryEvidence, MasteryHistory
from services.mastery_engine import Estimate, Evidence, estimate


def verify(db: Session) -> int:
    checked = 0
    for row in list(db.scalars(select(MasteryHistory))) + list(db.scalars(select(MasteryEstimate))):
        expected = Estimate.model_validate(row.snapshot)
        if isinstance(row, MasteryHistory):
            owner = db.get(MasteryEvidence, row.evidence_id)
            if owner is None:
                raise ValueError("Missing evidence")
            learner = owner.learner_id
        else:
            learner = row.learner_id
        sources = list(
            db.scalars(
                select(MasteryEvidence).where(
                    MasteryEvidence.learner_id == learner,
                    MasteryEvidence.concept_id == expected.concept_id,
                    MasteryEvidence.competency_id == expected.competency_id,
                    MasteryEvidence.attempt_id.in_(expected.input_attempt_ids),
                )
            )
        )
        replayed = estimate(
            expected.concept_id,
            expected.competency_id,
            [Evidence.model_validate(r.snapshot) for r in sources],
            expected.calculated_at,
            expected.configuration,
        )
        if replayed != expected:
            raise ValueError("Mastery replay mismatch")
        checked += 1
    return checked


def main() -> None:
    settings = Settings()
    if settings.app_env not in {"development", "test"}:
        raise ValueError("Local synthetic replay only")
    engine = engine_for(settings)
    try:
        with Session(engine) as db:
            checked = verify(db)
        print(f"Mastery replay matched {checked} stored projections; no data changed.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
