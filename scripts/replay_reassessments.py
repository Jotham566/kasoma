"""Read-only verification of frozen reassessment selection and pinned content hashes."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.config import Settings
from services.database import engine_for
from services.domain.assessment import Reassessment
from services.domain.content import ItemVersion
from services.mastery_engine import fingerprint
from services.reassessment_engine import select_candidate


def verify(db: Session) -> int:
    count = 0
    for row in db.scalars(select(Reassessment)):
        selected = select_candidate(row.snapshot)
        if (
            fingerprint(row.snapshot) != row.input_hash
            or selected["version_id"] != str(row.item_version_id)
            or selected["basis"] != row.basis
        ):
            raise ValueError("Reassessment selection replay mismatch")
        for candidate in row.snapshot["candidates"]:
            version = db.get(ItemVersion, UUID(candidate["version_id"]))
            if version is None or version.content_hash != candidate["content_hash"]:
                raise ValueError("Reassessment content history mismatch")
        source = db.get(ItemVersion, UUID(row.snapshot["original_version_id"]))
        if source is None or source.content_hash != row.snapshot["original_content_hash"]:
            raise ValueError("Reassessment original history mismatch")
        count += 1
    return count


def main() -> None:
    settings = Settings()
    if settings.app_env not in {"development", "test"}:
        raise ValueError("Local synthetic replay only")
    engine = engine_for(settings)
    try:
        with Session(engine) as db:
            count = verify(db)
        print(f"Reassessment replay matched {count} snapshots; no data changed.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
