"""Closed-by-default runtime scope/report boundary for the candidate learner flow."""

from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.content_contracts import DraftDocument
from services.domain.content import Item, ItemVersion
from services.domain.grading_bands import GradingBandRow
from services.grading_band_store import snapshot
from services.identity import IdentityService
from services.short_text_eligibility import CalibrationBand, GradingScope
from services.short_text_validation import SyntheticRubricContext

ApprovalAuthority = Callable[[CalibrationBand], bool]


class ShortTextPolicy:
    def __init__(
        self, identity: IdentityService, authority: ApprovalAuthority | None = None
    ) -> None:
        self.identity = identity
        # An enabled DB row and plausible approval UUID are insufficient authority.
        # No authority is configured by the normal application or seeded dataset.
        self.authority = authority

    def scope(self, db: Session, version: ItemVersion) -> GradingScope:
        item = db.get(Item, version.item_id)
        if item is None or version.topic_id is None:
            raise ValueError("Missing rubric scope")
        settings = self.identity.settings
        return GradingScope(
            subject_id=item.subject_id,
            topic_id=version.topic_id,
            language="en",
            model_version=settings.short_text_model_version,
            prompt_version=settings.short_text_prompt_version,
            configuration_version=settings.short_text_configuration_version,
        )

    def approved(self, band: CalibrationBand) -> bool:
        if not self.identity.settings.short_text_enabled or self.authority is None:
            return False
        try:
            return self.authority(band) is True
        except Exception:
            # A report resolver outage is not academic approval or learner feedback.
            return False

    def band_for(self, db: Session, version: ItemVersion) -> GradingBandRow | None:
        if (
            not self.identity.settings.short_text_enabled
            or self.authority is None
            or version.status != "APPROVED"
            or not version.synthetic
            or version.document.get("response_type") != "SHORT_TEXT"
        ):
            return None
        scope = self.scope(db, version)
        rows = list(
            db.scalars(
                select(GradingBandRow)
                .where(
                    GradingBandRow.subject_id == scope.subject_id,
                    GradingBandRow.topic_id == scope.topic_id,
                    GradingBandRow.language == scope.language,
                    GradingBandRow.model_version == scope.model_version,
                    GradingBandRow.prompt_version == scope.prompt_version,
                    GradingBandRow.configuration_version == scope.configuration_version,
                    GradingBandRow.enabled.is_(True),
                    GradingBandRow.activated_at <= self.identity.clock(),
                )
                .order_by(GradingBandRow.id)
                .limit(2)
                .with_for_update(read=True)
                .execution_options(populate_existing=True)
            )
        )
        # Do not silently choose authority when simultaneously enabled reports conflict.
        if len(rows) != 1 or not self.approved(snapshot(rows[0])):
            return None
        return rows[0]

    def context(self, version: ItemVersion) -> SyntheticRubricContext:
        document = DraftDocument.model_validate(version.document)
        if (
            not version.synthetic
            or document.response_type != "SHORT_TEXT"
            or document.rubric is None
        ):
            raise ValueError("Reviewed synthetic rubric required")
        return SyntheticRubricContext(
            rubric_version_id=version.id,
            item_version_id=version.id,
            maximum_points=document.maximum_points,
            criteria=document.rubric.criteria,
            misconception_ids=[],
            correct_elements=[document.worked_solution],
            missing_elements=[document.remediation],
            next_actions=[document.remediation],
        )
