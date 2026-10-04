"""Reconstruct authorized practice replies from immutable references at delivery time."""

from uuid import UUID

from sqlalchemy.orm import Session

from services.assessment import AssessmentService
from services.content_contracts import DraftDocument
from services.domain.assessment import Attempt, SessionItem
from services.domain.curriculum import Subject, Topic
from services.domain.messaging import ConversationState, OutboundMessage
from services.identity import IdentityError, IdentityService
from services.whatsapp_feedback import application_origin, feedback_text
from services.whatsapp_format import MAX_MESSAGE_CHARS, question_text


def render_practice(identity: IdentityService, db: Session, row: OutboundMessage) -> str:
    if row.actor_id is None or row.link_id is None:
        raise IdentityError("AUTH_REQUIRED", 401)
    service = AssessmentService(identity)
    service.authorize_actor(db, row.actor_id)
    origin = application_origin(identity.settings.app_public_url)
    if row.template == "PRACTICE_NOTICE":
        message = (
            "Send START or CONTINUE for five-question practice. Reply directly to the latest "
            "menu or question with your choice. Send PROGRESS or STOP. "
            f"Manage practice: {origin}/revise"
        )
    elif row.template == "PROGRESS":
        message = (
            f"View your saved progress after signing in: {origin}/progress\nSend CONTINUE or STOP."
        )
    elif row.template == "PRACTICE_FEEDBACK":
        attempt = db.get(Attempt, row.attempt_id) if row.attempt_id else None
        item = db.get(SessionItem, row.session_item_id) if row.session_item_id else None
        if (
            not attempt
            or not item
            or attempt.learner_id != row.actor_id
            or attempt.session_item_id != item.id
        ):
            raise IdentityError("RESOURCE_NOT_FOUND", 404)
        session = service.owned(db, row.actor_id, item.session_id)
        service.authorize_actor(db, row.actor_id, session.subject_id)
        if session.kind != "REVISION" or session.item_count != 5:
            raise IdentityError("FORBIDDEN", 403)
        service.content.assessment_version(db, item.item_version_id, session.subject_id)
        message = feedback_text(service.grade(db, attempt.id), session.id, item.position, origin)
    else:
        state = db.get(ConversationState, row.link_id)
        if (
            not state
            or state.expected_outbound_id != row.id
            or state.actor_id != row.actor_id
            or state.link_revision != row.link_revision
            or state.expires_at <= identity.clock()
        ):
            raise IdentityError("RESOURCE_NOT_FOUND", 404)
        if row.template == "PRACTICE_MENU" and row.menu_topic_ids:
            lines = ["Choose a topic for five questions:"]
            for number, topic_id in enumerate(row.menu_topic_ids, 1):
                topic = db.get(Topic, UUID(topic_id))
                if topic is None:
                    raise IdentityError("RESOURCE_NOT_FOUND", 404)
                service.authorize_actor(db, row.actor_id, topic.subject_id)
                subject = db.get(Subject, topic.subject_id)
                if subject is None:
                    raise IdentityError("RESOURCE_NOT_FOUND", 404)
                lines.append(f"{number}. {subject.name}: {topic.name}")
            lines.append("Reply to this message with one topic number. Send STOP to stop replies.")
            message = "\n".join(lines)
        elif row.template == "PRACTICE_QUESTION" and row.session_item_id:
            item = db.get(SessionItem, row.session_item_id)
            if not item or state.session_id != item.session_id:
                raise IdentityError("RESOURCE_NOT_FOUND", 404)
            session = service.owned(db, row.actor_id, item.session_id)
            service.authorize_actor(db, row.actor_id, session.subject_id)
            service.channel_session(db, session, "WHATSAPP")
            pending = service.pending(db, session.id)
            if session.status != "ACTIVE" or not pending or pending.id != item.id:
                raise IdentityError("SESSION_NOT_ACTIVE", 409)
            version = service.content.assessment_version(
                db, item.item_version_id, session.subject_id
            )
            message = question_text(DraftDocument.model_validate(version.document), item.position)
        else:
            raise IdentityError("VALIDATION_FAILED", 422)
    if len(message) > MAX_MESSAGE_CHARS:
        raise IdentityError("VALIDATION_FAILED", 422)
    return message
