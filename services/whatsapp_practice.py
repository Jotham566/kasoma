"""Reply-bound local practice; grading and mastery remain in the assessment service."""

from datetime import timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.assessment import AssessmentService
from services.assessment_contracts import StartRevision, SubmitAnswer
from services.content_contracts import DraftDocument
from services.domain.assessment import Attempt, SessionItem
from services.domain.curriculum import Topic
from services.domain.messaging import (
    ChannelLink,
    ConversationState,
    InboundMessage,
    OutboundMessage,
)
from services.identity import IdentityError, IdentityService
from services.whatsapp_format import parse_reply


def queue(
    identity: IdentityService,
    db: Session,
    incoming: InboundMessage,
    link: ChannelLink,
    template: str,
) -> OutboundMessage:
    from services.whatsapp_processing import queue_reply

    outgoing = queue_reply(identity, db, incoming, link, template)
    outgoing.link_revision = link.revision
    return outgoing


def state_for(identity: IdentityService, db: Session, link: ChannelLink) -> ConversationState:
    now = identity.clock()
    state = db.get(ConversationState, link.id)
    if state and (state.link_revision != link.revision or state.expires_at <= now):
        db.delete(state)
        db.flush()
        state = None
    if state is None:
        state = ConversationState(
            link_id=link.id,
            actor_id=link.user_id,
            link_revision=link.revision,
            updated_at=now,
            expires_at=now + timedelta(hours=24),
        )
        db.add(state)
    return state


def menu(
    service: AssessmentService,
    db: Session,
    incoming: InboundMessage,
    link: ChannelLink,
    state: ConversationState,
) -> None:
    profile = service.identity.profile(db, link.user_id)
    topics = list(
        db.scalars(
            select(Topic)
            .where(Topic.subject_id.in_(profile.subject_ids))
            .order_by(Topic.subject_id, Topic.id)
            .limit(7)
        )
    )
    if not 1 <= len(topics) <= 6:
        raise IdentityError("INSUFFICIENT_CONTENT", 409)
    outgoing = queue(service.identity, db, incoming, link, "PRACTICE_MENU")
    outgoing.menu_topic_ids = [str(t.id) for t in topics]
    db.flush()
    state.session_id, state.expected_outbound_id = None, outgoing.id
    db.flush()
    # Validate the complete menu before persisting it as the next reply target.
    from services.whatsapp_render import render_practice

    render_practice(service.identity, db, outgoing)


def question(
    service: AssessmentService,
    db: Session,
    incoming: InboundMessage,
    link: ChannelLink,
    state: ConversationState,
) -> None:
    if state.session_id is None:
        menu(service, db, incoming, link, state)
        return
    item = service.next_item_in_transaction(
        db, link.user_id, state.session_id, incoming.request_id, channel="WHATSAPP"
    )
    outgoing = queue(service.identity, db, incoming, link, "PRACTICE_QUESTION")
    outgoing.session_item_id = item.session_item_id
    db.flush()
    state.expected_outbound_id = outgoing.id


def process(
    identity: IdentityService, db: Session, incoming: InboundMessage, link: ChannelLink
) -> None:
    service = AssessmentService(identity)
    service.authorize_actor(db, link.user_id)
    state = state_for(identity, db, link)
    now = identity.clock()
    state.updated_at = now
    state.expires_at = now + timedelta(hours=24)
    if incoming.command == "PROGRESS":
        queue(identity, db, incoming, link, "PROGRESS")
    elif incoming.command in {"START", "CONTINUE"}:
        if state.session_id:
            current = service.owned(db, link.user_id, state.session_id)
            if current.status != "ACTIVE":
                state.session_id, state.expected_outbound_id = None, None
        question(service, db, incoming, link, state)
    elif incoming.command == "ANSWER":
        outgoing = (
            db.get(OutboundMessage, state.expected_outbound_id)
            if state.expected_outbound_id
            else None
        )
        if (
            not outgoing
            or outgoing.provider_id != incoming.reply_reference
            or outgoing.status not in {"SENT", "DELIVERED", "READ"}
            or outgoing.actor_id != link.user_id
            or outgoing.link_id != link.id
            or outgoing.link_revision != link.revision
            or outgoing.recipient_hash != incoming.sender_hash
            or not incoming.reply_encrypted
        ):
            raise IdentityError("RESOURCE_NOT_FOUND", 404)
        raw = identity.decrypt(incoming.reply_encrypted)
        if outgoing.template == "PRACTICE_MENU" and outgoing.menu_topic_ids:
            if raw.strip() not in {str(n) for n in range(1, len(outgoing.menu_topic_ids) + 1)}:
                raise IdentityError("VALIDATION_FAILED", 422)
            topic = db.get(Topic, UUID(outgoing.menu_topic_ids[int(raw.strip()) - 1]))
            if topic is None:
                raise IdentityError("RESOURCE_NOT_FOUND", 404)
            started = service.start_in_transaction(
                db,
                link.user_id,
                StartRevision(subject_id=topic.subject_id, topic_id=topic.id),
                incoming.id,
                incoming.request_id,
                channel="WHATSAPP",
            )
            state.session_id = started.id
            question(service, db, incoming, link, state)
        elif outgoing.template == "PRACTICE_QUESTION" and state.session_id:
            item = db.get(SessionItem, outgoing.session_item_id)
            if item is None or item.session_id != state.session_id:
                raise IdentityError("RESOURCE_NOT_FOUND", 404)
            session = service.owned(db, link.user_id, state.session_id)
            version = service.content.assessment_version(
                db, item.item_version_id, session.subject_id
            )
            response = parse_reply(DraftDocument.model_validate(version.document), raw)
            grade = service.submit_in_transaction(
                db,
                link.user_id,
                session.id,
                SubmitAnswer(session_item_id=item.id, response=response),
                incoming.id,
                incoming.request_id,
                channel="WHATSAPP",
            )
            # Only revision sessions pass the channel gate; diagnostic receipts cannot reach here.
            if not db.get(Attempt, grade.attempt_id):
                raise IdentityError("RESOURCE_NOT_FOUND", 404)
            reply = queue(identity, db, incoming, link, "PRACTICE_FEEDBACK")
            reply.attempt_id, reply.session_item_id = grade.attempt_id, item.id
            state.expected_outbound_id = None
        else:
            raise IdentityError("VALIDATION_FAILED", 422)
    else:
        queue(identity, db, incoming, link, "PRACTICE_NOTICE")
