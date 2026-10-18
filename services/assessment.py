"""Shared assessment orchestration. No channel/provider-specific scoring logic."""

from datetime import timedelta
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.assessment_contracts import (
    AnsweredItem,
    AttemptGrade,
    ChoiceResponse,
    DiagnosticReceipt,
    DiagnosticView,
    LearnerItem,
    MultipleChoiceResponse,
    MultipleChoiceResponseSpec,
    NumericResponse,
    NumericResponseSpec,
    PromptBlock,
    RecommendationView,
    ResponseSpec,
    SessionView,
    ShortTextResponseSpec,
    SolutionView,
    StartRevision,
    SubmitAnswer,
    TopicView,
)
from services.assessment_outcomes import outcome
from services.content import ContentService
from services.content_contracts import DraftDocument
from services.domain.assessment import (
    AssessmentEvent,
    AssessmentReceipt,
    AssessmentSession,
    Attempt,
    Grade,
    Reassessment,
    SessionItem,
)
from services.domain.content import ItemVersion
from services.domain.curriculum import Level, Subject, Topic
from services.domain.identity import LearnerProfile, User
from services.grading import grade_choice, grade_multiple_choice, grade_numeric
from services.identity import IdentityError, IdentityService
from services.mastery import reconcile
from services.short_text_contracts import ShortTextResponse
from services.short_text_policy import ShortTextPolicy
from services.short_text_submission import submit_encrypted


class AssessmentService:
    def __init__(self, identity: IdentityService, short_text: ShortTextPolicy | None = None):
        self.identity = identity
        self.short_text = short_text or ShortTextPolicy(identity)
        self.content = ContentService(identity, self.short_text)
        from services.diagnostics import Diagnostics

        self.diagnostics = Diagnostics(self)

    def assignment_band(self, db: Session, version: ItemVersion) -> UUID | None:
        if version.document.get("response_type") != "SHORT_TEXT":
            return None
        band = self.short_text.band_for(db, version)
        if band is None:
            raise IdentityError("CONTENT_NOT_APPROVED", 409)
        return band.id

    def authorize(self, db: Session, token: str, subject: UUID | None = None) -> UUID:
        actor = self.identity.authenticate(db, token).user_id
        return self.authorize_actor(db, actor, subject)

    def authorize_actor(self, db: Session, actor: UUID, subject: UUID | None = None) -> UUID:
        """Internal trusted-actor entry only; every call rechecks current authorization."""
        self.identity.lock(db, str(actor))
        user = db.get(User, actor, populate_existing=True)
        if user is None or user.status != "ACTIVE":
            raise IdentityError("AUTH_REQUIRED", 401)
        profile = self.identity.profile(db, actor)
        if not profile.learning_allowed:
            raise IdentityError("CONSENT_REQUIRED", 403)
        level = db.scalar(
            select(Level.name).join(LearnerProfile).where(LearnerProfile.user_id == actor)
        )
        if level != "S4" or (subject is not None and subject not in profile.subject_ids):
            raise IdentityError("FORBIDDEN", 403)
        return actor

    def event(
        self,
        db: Session,
        session: UUID,
        event: str,
        request: UUID,
        attempt: UUID | None = None,
        *,
        hint_count: int | None = None,
        highest_hint_level: int | None = None,
    ) -> None:
        db.add(
            AssessmentEvent(
                id=uuid4(),
                session_id=session,
                attempt_id=attempt,
                type=event,
                version=1,
                hint_count=hint_count,
                highest_hint_level=highest_hint_level,
                request_id=request,
                created_at=self.identity.clock(),
            )
        )

    def owned(self, db: Session, actor: UUID, session_id: UUID) -> AssessmentSession:
        session = db.scalar(
            select(AssessmentSession)
            .where(AssessmentSession.id == session_id, AssessmentSession.learner_id == actor)
            .with_for_update()
        )
        if session is None:
            raise IdentityError("RESOURCE_NOT_FOUND", 404)
        if session.status == "ACTIVE" and session.expires_at <= self.identity.clock():
            session.status = "EXPIRED"
        return session

    def view(self, db: Session, session: AssessmentSession) -> SessionView:
        answers = [
            AnsweredItem(
                session_item_id=item.id,
                position=item.position,
                grade=self.grade(db, attempt.id),
            )
            for item, attempt in db.execute(
                select(SessionItem, Attempt)
                .join(Attempt, Attempt.session_item_id == SessionItem.id)
                .where(SessionItem.session_id == session.id)
                .order_by(SessionItem.position)
            )
        ]
        if session.topic_id is None:
            raise ValueError("Revision requires a topic")
        link = db.scalar(select(Reassessment).where(Reassessment.session_id == session.id))
        original = db.get(Attempt, link.original_attempt_id) if link else None
        original_item = db.get(SessionItem, original.session_item_id) if original else None
        return SessionView(
            kind=session.kind,
            original_attempt_id=original.id if original else None,
            original_session_id=original_item.session_id if original_item else None,
            id=session.id,
            subject_id=session.subject_id,
            topic_id=session.topic_id,
            status=session.status,
            item_count=session.item_count,
            answered_count=len(answers),
            recommendation_reason=session.reason,
            plan_version=session.plan_version,
            expires_at=session.expires_at,
            answers=answers,
        )

    def topics(self, token: str, subject: UUID) -> list[TopicView]:
        with Session(self.identity.engine) as db, db.begin():
            self.authorize(db, token, subject)
            return [
                TopicView(id=t.id, name=t.name)
                for t in db.scalars(
                    select(Topic)
                    .join(Subject)
                    .join(Level)
                    .where(
                        Topic.subject_id == subject,
                        Level.name == "S4",
                        Subject.name.in_(["Mathematics", "Physics"]),
                    )
                    .order_by(Topic.name)
                )
            ]

    def replay(
        self, db: Session, actor: UUID, key: UUID, fingerprint: str
    ) -> AssessmentReceipt | None:
        receipt = db.get(AssessmentReceipt, (actor, key))
        if receipt and receipt.request_hash != fingerprint:
            raise IdentityError("IDEMPOTENCY_CONFLICT", 409)
        return receipt

    @staticmethod
    def check_channel(channel: str) -> None:
        if channel not in {"WEB", "WHATSAPP"}:
            raise IdentityError("VALIDATION_FAILED", 422)

    def channel_session(self, db: Session, session: AssessmentSession, channel: str) -> None:
        self.check_channel(channel)
        if channel == "WEB":
            return
        if session.kind != "REVISION" or session.item_count != 5:
            raise IdentityError("VALIDATION_FAILED", 422)
        from services.whatsapp_format import supports

        items = list(
            db.scalars(
                select(SessionItem)
                .join(ItemVersion, ItemVersion.id == SessionItem.item_version_id)
                .where(SessionItem.session_id == session.id)
                .order_by(ItemVersion.item_id, ItemVersion.id)
            )
        )
        if len(items) != 5:
            raise IdentityError("CONTENT_NOT_APPROVED", 409)
        for item in items:
            version = self.content.assessment_version(db, item.item_version_id, session.subject_id)
            if not supports(DraftDocument.model_validate(version.document)):
                raise IdentityError("CONTENT_NOT_APPROVED", 409)

    def start(self, token: str, body: StartRevision, key: UUID, request: UUID) -> SessionView:
        with Session(self.identity.engine) as db, db.begin():
            actor = self.identity.authenticate(db, token).user_id
            return self.start_in_transaction(db, actor, body, key, request)

    def start_in_transaction(
        self,
        db: Session,
        actor: UUID,
        body: StartRevision,
        key: UUID,
        request: UUID,
        *,
        channel: str = "WEB",
    ) -> SessionView:
        self.authorize_actor(db, actor, body.subject_id)
        self.check_channel(channel)
        if channel == "WHATSAPP" and (body.mode != "TOPIC" or body.desired_item_count != 5):
            raise IdentityError("VALIDATION_FAILED", 422)
        fingerprint = self.identity.digest(
            "assessment",
            ("" if channel == "WEB" else "WHATSAPP:") + "start:" + body.model_dump_json(),
        )
        receipt = self.replay(db, actor, key, fingerprint)
        if receipt:
            existing = self.owned(db, actor, receipt.session_id)
            self.channel_session(db, existing, channel)
            return self.view(db, existing)
        # Expire all stale revision reservations under the same learner lock.
        # Otherwise an expired manual plan can still hold the topic's unique index.
        for stale in db.scalars(
            select(AssessmentSession).where(
                AssessmentSession.learner_id == actor,
                AssessmentSession.subject_id == body.subject_id,
                AssessmentSession.kind == "REVISION",
                AssessmentSession.status == "ACTIVE",
                AssessmentSession.expires_at <= self.identity.clock(),
            )
        ):
            stale.status = "EXPIRED"
        db.flush()
        recommended = body.mode == "RECOMMENDED"
        if not recommended:
            topic = db.get(Topic, body.topic_id)
            if not topic or topic.subject_id != body.subject_id:
                raise IdentityError("VALIDATION_FAILED", 422)
        active = db.scalar(
            select(AssessmentSession)
            .where(
                AssessmentSession.learner_id == actor,
                AssessmentSession.subject_id == body.subject_id,
                AssessmentSession.kind == "REVISION",
                AssessmentSession.recommendation_snapshot.is_not(None)
                if recommended
                else AssessmentSession.topic_id == body.topic_id,
                AssessmentSession.status == "ACTIVE",
            )
            .order_by(AssessmentSession.started_at)
        )
        if active:
            if active.item_count != body.desired_item_count:
                raise IdentityError("VERSION_CONFLICT", 409)
            self.channel_session(db, active, channel)
            session = active
        else:
            if not self.identity.rate(db, "assessment-start:" + str(actor), 30, 3600):
                raise IdentityError("USAGE_LIMIT_REACHED", 429)
            snapshot = None
            topic_id = body.topic_id
            reason = "Practice the topic you selected."
            reasons = [reason] * body.desired_item_count
            plan_version = "topic-choice-v1"
            if recommended:
                from services.recommendations import plan

                try:
                    selected = plan(self, db, actor, body.subject_id, body.desired_item_count)
                except ValueError as error:
                    raise IdentityError("CONTENT_NOT_APPROVED", 409) from error
                if selected.topic_id is None:
                    raise IdentityError("INSUFFICIENT_CONTENT", 409)
                topic_id, reason = selected.topic_id, selected.learner_text
                reasons = list(selected.item_reasons)
                plan_version = selected.inputs.configuration.algorithm_version
                snapshot = selected.model_dump(mode="json")
                candidates = self.content.assessment_versions(
                    db, list(selected.item_version_ids), body.subject_id
                )
            else:
                candidates = self.diagnostics.candidates(
                    db,
                    actor,
                    body.subject_id,
                    channel=channel,
                    topic_id=topic_id,
                    per_topic_limit=body.desired_item_count,
                )
                if candidates:
                    candidates = self.content.assessment_versions(
                        db, [v.id for v in candidates], body.subject_id
                    )
            if len(candidates) < body.desired_item_count:
                raise IdentityError("INSUFFICIENT_CONTENT", 409)
            session = AssessmentSession(
                id=uuid4(),
                learner_id=actor,
                subject_id=body.subject_id,
                topic_id=topic_id,
                recommendation_snapshot=snapshot,
                status="ACTIVE",
                item_count=len(candidates),
                reason=reason,
                plan_version=plan_version,
                started_at=self.identity.clock(),
                expires_at=self.identity.clock()
                + timedelta(days=self.identity.settings.assessment_session_days),
            )
            db.add(session)
            db.flush()
            db.add_all(
                [
                    SessionItem(
                        id=uuid4(),
                        session_id=session.id,
                        item_version_id=v.id,
                        position=i + 1,
                        reason=reasons[i],
                        grading_band_id=self.assignment_band(db, v),
                    )
                    for i, v in enumerate(candidates)
                ]
            )
            self.event(db, session.id, "session.started", request)
        db.add(
            AssessmentReceipt(
                learner_id=actor, key=key, request_hash=fingerprint, session_id=session.id
            )
        )
        db.flush()
        return self.view(db, session)

    def recommendation(self, token: str, subject: UUID) -> RecommendationView:
        from services.recommendations import plan

        with Session(self.identity.engine) as db, db.begin():
            actor = self.authorize(db, token, subject)
            if not self.identity.rate(db, "recommendation-read:" + str(actor), 60, 3600):
                raise IdentityError("USAGE_LIMIT_REACHED", 429)
            try:
                result = plan(self, db, actor, subject, 5)
            except ValueError as error:
                raise IdentityError("CONTENT_NOT_APPROVED", 409) from error
            return RecommendationView(
                subject_id=subject,
                topic_id=result.topic_id,
                topic=result.topic,
                reason_code=result.reason_code,
                learner_text=result.learner_text,
                estimated_minutes=result.estimated_minutes,
                algorithm_version=result.inputs.configuration.algorithm_version,
                configuration_version=result.inputs.configuration.configuration_version,
                input_hash=result.input_hash,
                calculated_at=result.inputs.calculated_at,
                diagnostic_suggested=result.reason_code == "GATHER_MORE_EVIDENCE",
            )

    def active(self, token: str) -> list[SessionView]:
        with Session(self.identity.engine) as db, db.begin():
            actor = self.authorize(db, token)
            allowed = self.identity.profile(db, actor).subject_ids
            sessions = list(
                db.scalars(
                    select(AssessmentSession)
                    .where(
                        AssessmentSession.learner_id == actor,
                        AssessmentSession.status == "ACTIVE",
                        AssessmentSession.kind.in_(["REVISION", "REASSESSMENT"]),
                        AssessmentSession.subject_id.in_(allowed),
                    )
                    .order_by(AssessmentSession.started_at)
                )
            )
            return [
                self.view(db, self.owned(db, actor, s.id))
                for s in sessions
                if s.expires_at > self.identity.clock()
            ]

    def get(
        self, token: str, session_id: UUID, request: UUID | None = None
    ) -> SessionView | DiagnosticView:
        with Session(self.identity.engine) as db, db.begin():
            actor = self.authorize(db, token)
            session = self.owned(db, actor, session_id)
            self.authorize(db, token, session.subject_id)
            self.diagnostics.complete_if_ready(db, session, request or uuid4())
            return (
                self.diagnostics.view(db, session)
                if session.kind == "DIAGNOSTIC"
                else self.view(db, session)
            )

    def pending(self, db: Session, session_id: UUID) -> SessionItem | None:
        return db.scalar(
            select(SessionItem)
            .where(
                SessionItem.session_id == session_id,
                ~select(Attempt.id).where(Attempt.session_item_id == SessionItem.id).exists(),
            )
            .order_by(SessionItem.position)
            .limit(1)
        )

    def next_item(self, token: str, session_id: UUID, request: UUID) -> LearnerItem:
        with Session(self.identity.engine) as db, db.begin():
            actor = self.identity.authenticate(db, token).user_id
            return self.next_item_in_transaction(db, actor, session_id, request)

    def next_item_in_transaction(
        self,
        db: Session,
        actor: UUID,
        session_id: UUID,
        request: UUID,
        *,
        channel: str = "WEB",
    ) -> LearnerItem:
        self.authorize_actor(db, actor)
        session = self.owned(db, actor, session_id)
        self.authorize_actor(db, actor, session.subject_id)
        self.channel_session(db, session, channel)
        if session.status != "ACTIVE":
            raise IdentityError("SESSION_NOT_ACTIVE", 409)
        item = self.pending(db, session.id)
        if item is None and session.kind == "DIAGNOSTIC":
            item = self.diagnostics.assign(db, session)
        if item is None:
            raise IdentityError("SESSION_NOT_ACTIVE", 409)
        version = self.content.assessment_version(
            db, item.item_version_id, session.subject_id, assigned_band_id=item.grading_band_id
        )
        document = DraftDocument.model_validate(version.document)
        if channel not in document.channel_suitability:
            raise IdentityError("CONTENT_NOT_APPROVED", 409)
        if item.served_at is None:
            item.served_at = self.identity.clock()
            self.event(db, session.id, "item.served", request)
        if document.response_type == "NUMERIC":
            spec = document.numeric_spec
            if spec is None:
                raise IdentityError("CONTENT_NOT_APPROVED", 409)
            response_spec: (
                ResponseSpec
                | MultipleChoiceResponseSpec
                | NumericResponseSpec
                | ShortTextResponseSpec
            ) = NumericResponseSpec(
                unit_options=[u.label for u in spec.units],
                accepted_forms=spec.accepted_forms,
                significant_figures_policy=spec.significant_figures_policy,
                significant_figures=spec.significant_figures,
            )
        elif document.response_type == "SHORT_TEXT":
            response_spec = ShortTextResponseSpec()
        elif document.response_type == "MULTIPLE_CHOICE":
            response_spec = MultipleChoiceResponseSpec(choices=document.choices)
        else:
            response_spec = ResponseSpec(choices=document.choices)
        from services.hints import state

        revealed = state(db, item.id, document) if session.kind == "REVISION" else None
        return LearnerItem(
            session_item_id=item.id,
            item_version_id=version.id,
            position=item.position,
            prompt_blocks=[PromptBlock(content=document.prompt)],
            response_spec=response_spec,
            maximum_points=document.maximum_points,
            selection_reason=item.reason,
            hints=revealed.hints if revealed else [],
            has_more_hints=revealed.has_more_hints if revealed else False,
        )

    def submit(
        self, token: str, session_id: UUID, body: SubmitAnswer, key: UUID, request: UUID
    ) -> AttemptGrade | DiagnosticReceipt:
        with Session(self.identity.engine) as db, db.begin():
            actor = self.identity.authenticate(db, token).user_id
            return self.submit_in_transaction(db, actor, session_id, body, key, request)

    def submit_in_transaction(
        self,
        db: Session,
        actor: UUID,
        session_id: UUID,
        body: SubmitAnswer,
        key: UUID,
        request: UUID,
        *,
        channel: str = "WEB",
    ) -> AttemptGrade | DiagnosticReceipt:
        self.authorize_actor(db, actor)
        session = self.owned(db, actor, session_id)
        self.authorize_actor(db, actor, session.subject_id)
        self.check_channel(channel)
        fingerprint = self.identity.digest(
            "assessment",
            ("" if channel == "WEB" else "WHATSAPP:")
            + str(session_id)
            + ":answer:"
            + body.model_dump_json(),
        )
        receipt = self.replay(db, actor, key, fingerprint)
        if receipt and receipt.attempt_id:
            return (
                DiagnosticReceipt(attempt_id=receipt.attempt_id)
                if session.kind == "DIAGNOSTIC"
                else self.grade(db, receipt.attempt_id)
            )
        self.channel_session(db, session, channel)
        if db.scalar(
            select(Attempt.id).where(
                Attempt.session_item_id == body.session_item_id, Attempt.learner_id == actor
            )
        ):
            raise IdentityError("ITEM_ALREADY_ANSWERED", 409)
        if session.status != "ACTIVE":
            raise IdentityError("SESSION_NOT_ACTIVE", 409)
        item = self.pending(db, session.id)
        if item is None or item.id != body.session_item_id or item.served_at is None:
            raise IdentityError("RESOURCE_NOT_FOUND", 404)
        version = self.content.assessment_version(
            db, item.item_version_id, session.subject_id, assigned_band_id=item.grading_band_id
        )
        document = DraftDocument.model_validate(version.document)
        if channel not in document.channel_suitability:
            raise IdentityError("CONTENT_NOT_APPROVED", 409)
        attempt_id = uuid4()
        if document.response_type != body.response.type:
            raise IdentityError("VALIDATION_FAILED", 422)
        if isinstance(body.response, ShortTextResponse):
            if channel != "WEB":
                raise IdentityError("VALIDATION_FAILED", 422)
            return submit_encrypted(
                self,
                db,
                actor,
                session,
                item,
                version,
                body.response,
                attempt_id,
                key,
                request,
                fingerprint,
            )
        try:
            if isinstance(body.response, NumericResponse):
                result = grade_numeric(
                    attempt_id, version.id, document, body.response.value, body.response.unit
                )
            elif isinstance(body.response, MultipleChoiceResponse):
                result = grade_multiple_choice(
                    attempt_id, version.id, document, body.response.choice_ids
                )
            else:
                result = grade_choice(attempt_id, version.id, document, body.response.choice_id)
        except ValueError:
            raise IdentityError("VALIDATION_FAILED", 422) from None
        from services.hints import counts

        hint_count, highest_hint_level = counts(db, item.id)
        db.add(
            Attempt(
                id=attempt_id,
                learner_id=actor,
                session_item_id=item.id,
                item_version_id=version.id,
                choice_id=body.response.choice_id
                if isinstance(body.response, ChoiceResponse)
                else None,
                response=None
                if isinstance(body.response, ChoiceResponse)
                else body.response.model_dump(mode="json"),
                submitted_at=self.identity.clock(),
                hint_count=hint_count,
                highest_hint_level=highest_hint_level,
                channel=channel,
            )
        )
        db.flush()
        result = result.model_copy(
            update={
                "mastery_update_status": "COMPLETED",
                "hint_count": hint_count,
                "highest_hint_level": highest_hint_level,
            }
        )
        db.add(
            Grade(
                attempt_id=attempt_id,
                item_version_id=version.id,
                answer_specification_hash=version.content_hash,
                result=result.model_dump(mode="json"),
            )
        )
        db.add(
            AssessmentReceipt(
                learner_id=actor,
                key=key,
                request_hash=fingerprint,
                session_id=session.id,
                attempt_id=attempt_id,
            )
        )
        db.flush()
        reconcile(db, actor, self.identity.clock())
        self.event(db, session.id, "attempt.graded", request, attempt_id)
        self.event(
            db,
            session.id,
            "mastery.updated",
            request,
            attempt_id,
            hint_count=hint_count,
            highest_hint_level=highest_hint_level,
        )
        if session.kind == "DIAGNOSTIC":
            self.diagnostics.complete_if_ready(db, session, request)
            return DiagnosticReceipt(attempt_id=attempt_id)
        completed = self.pending(db, session.id) is None
        if completed and session.kind == "REASSESSMENT":
            self.event(db, session.id, "reassessment.completed", request, attempt_id)
        if completed:
            session.status, session.completed_at = "COMPLETED", self.identity.clock()
            self.event(
                db,
                session.id,
                "session.completed",
                request,
            )
        return result

    def grade(self, db: Session, attempt_id: UUID) -> AttemptGrade:
        return outcome(self.identity, db, attempt_id)

    def result(
        self, token: str, attempt_id: UUID, solution: bool = False
    ) -> AttemptGrade | SolutionView:
        with Session(self.identity.engine) as db, db.begin():
            actor = self.authorize(db, token)
            attempt = db.scalar(
                select(Attempt).where(Attempt.id == attempt_id, Attempt.learner_id == actor)
            )
            if attempt is None:
                raise IdentityError("RESOURCE_NOT_FOUND", 404)
            item = db.get(SessionItem, attempt.session_item_id)
            if item is None:
                raise IdentityError("RESOURCE_NOT_FOUND", 404)
            session = self.owned(db, actor, item.session_id)
            self.authorize(db, token, session.subject_id)
            if session.kind == "DIAGNOSTIC" and (solution or session.status != "COMPLETED"):
                raise IdentityError("FORBIDDEN", 403)
            if solution:
                version = db.get(ItemVersion, attempt.item_version_id)
                if version is None:
                    raise IdentityError("RESOURCE_NOT_FOUND", 404)
                return SolutionView(
                    attempt_id=attempt.id,
                    item_version_id=version.id,
                    worked_solution=DraftDocument.model_validate(version.document).worked_solution,
                )
            if attempt.response and attempt.response.get("type") == "SHORT_TEXT":
                if not self.identity.rate(db, "short-text-feedback:" + str(actor), 120, 60):
                    raise IdentityError("USAGE_LIMIT_REACHED", 429)
            return self.grade(db, attempt.id)

    def abandon(self, token: str, session_id: UUID, request: UUID) -> SessionView | DiagnosticView:
        with Session(self.identity.engine) as db, db.begin():
            actor = self.authorize(db, token)
            session = self.owned(db, actor, session_id)
            self.authorize(db, token, session.subject_id)
            if session.status == "ACTIVE":
                session.status = "ABANDONED"
                self.event(db, session.id, "session.abandoned", request)
            return (
                self.diagnostics.view(db, session)
                if session.kind == "DIAGNOSTIC"
                else self.view(db, session)
            )
