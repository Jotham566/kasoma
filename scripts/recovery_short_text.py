"""Encrypted synthetic result recovery, confined to generated drill databases."""

import re
from uuid import UUID, uuid4

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from scripts.assessment_fixtures import seed_assessment
from scripts.grading_fixtures import unapproved_band
from scripts.short_text_fixture_model import SyntheticRubricModel
from services.assessment import AssessmentService
from services.assessment_contracts import StartRevision, SubmitAnswer
from services.assessment_outcomes import grade_projection, response_projection
from services.domain.assessment import Attempt, Grade
from services.domain.grading_audits import GradingAuditAssignment, GradingAuditReview
from services.grading_band_store import register
from services.grading_review_contracts import AuditReviewInput
from services.grading_reviews import GradingReviewService
from services.identity import IdentityService
from services.identity_contracts import OTPRequest, OTPVerify
from services.rubric_grade_contracts import RubricGradeView
from services.short_text_contracts import ShortTextResponse
from services.short_text_eligibility import GradingScope
from services.short_text_policy import ShortTextPolicy
from services.short_text_processor import ShortTextProcessor


def populate_short_text(identity: IdentityService, token: str, subject: UUID, topic: UUID) -> None:
    with Session(identity.engine) as db:
        database = db.scalar(text("SELECT current_database()"))
        if not re.fullmatch(r"kasoma_drill_src_[0-9a-f]{32}", database or ""):
            raise ValueError("Synthetic authority requires an isolated recovery source")
    seed_assessment(identity, short_text=True, mathematics_only=True)
    config = identity.settings
    band = unapproved_band(
        GradingScope(
            subject_id=subject,
            topic_id=topic,
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
    with Session(identity.engine) as db, db.begin():
        register(db, band, identity.clock())
        db.execute(
            text("""UPDATE grading_bands SET enabled=true,activated_at=:now,
            updated_at=:now,revision=revision+1 WHERE id=:id"""),
            {"id": band.id, "now": identity.clock()},
        )
    original_enabled = config.short_text_enabled
    config.short_text_enabled = True
    try:
        policy = ShortTextPolicy(identity, lambda candidate: candidate.id == band.id)
        service = AssessmentService(identity, policy)
        session = service.start(
            token, StartRevision(subject_id=subject, topic_id=topic), uuid4(), uuid4()
        )
        item = service.next_item(token, session.id, uuid4())
        if item.response_spec.type != "SHORT_TEXT":
            raise RuntimeError("Recovery fixture did not select a reviewed short-text item")
        pending = service.submit(
            token,
            session.id,
            SubmitAnswer(
                session_item_id=item.session_item_id,
                response=ShortTextResponse(type="SHORT_TEXT", text="  Alpha\n"),
            ),
            uuid4(),
            uuid4(),
        )
        gateway = SyntheticRubricModel()
        if not ShortTextProcessor(
            service, gateway, safety=lambda context, response: response.strip() == "Alpha"
        ).process_one():
            raise RuntimeError("Synthetic encrypted publication missing")
        result = service.result(token, pending.attempt_id)
        if (
            not isinstance(result, RubricGradeView)
            or result.points_awarded != 1
            or len(gateway.calls) != 2
        ):
            raise RuntimeError("Synthetic encrypted publication is incomplete")
        challenge = identity.request_otp(
            OTPRequest(
                identifier="fixture-short-text-academic_reviewer@example.invalid", device_id=uuid4()
            ),
            "synthetic-recovery-reviewer",
            None,
        )
        reviewer = identity.verify(
            OTPVerify(challenge_id=challenge.challenge_id, code="246810"), None, str(uuid4())
        ).access_token
        with Session(identity.engine) as db:
            audit = db.scalar(
                select(GradingAuditAssignment).where(
                    GradingAuditAssignment.attempt_id == pending.attempt_id
                )
            )
            if audit is None:
                raise RuntimeError("Synthetic expert assignment missing")
            target = audit.id
        reviews = GradingReviewService(identity)
        reviews.get(reviewer, target)
        reviews.complete(
            reviewer,
            target,
            AuditReviewInput.model_validate_json(
                '{"criterion_points":[{"criterion_id":"R1","points_awarded":1}],"critical_error":"NONE","affirmative":true}'
            ),
            uuid4(),
            uuid4(),
        )
    finally:
        config.short_text_enabled = original_enabled


def verify_short_text(identity: IdentityService) -> None:
    """Read/decrypt the restored fixture without invoking learner auth or model work."""
    with Session(identity.engine) as db:
        rows = db.execute(
            select(Attempt, Grade)
            .join(Grade, Grade.attempt_id == Attempt.id)
            .where(Attempt.response["type"].as_string() == "SHORT_TEXT")
        ).all()
        if len(rows) != 1:
            raise RuntimeError("Restored encrypted short-text evidence missing")
        attempt, stored = rows[0]
        answer = response_projection(identity, attempt)
        result = grade_projection(identity, db, attempt, stored)
        if (
            answer != {"type": "SHORT_TEXT", "text": "  Alpha\n"}
            or not isinstance(result, RubricGradeView)
            or result.points_awarded != 1
            or result.criterion_results[0].evidence_excerpt != "Alpha"
        ):
            raise RuntimeError("Restored encrypted evidence did not decrypt coherently")
        review = db.scalar(
            select(GradingAuditReview)
            .join(GradingAuditAssignment, GradingAuditAssignment.id == GradingAuditReview.id)
            .where(GradingAuditAssignment.attempt_id == attempt.id)
        )
        if review is None or review.criterion_points != {"R1": 1} or not review.exact_agreement:
            raise RuntimeError("Restored independent expert evidence is incomplete")
