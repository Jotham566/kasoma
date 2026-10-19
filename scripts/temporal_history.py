"""ADR-066: chronological synthetic history through unchanged domain services."""

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from services.assessment import AssessmentService
from services.assessment_contracts import (
    DiagnosticReceipt,
    DiagnosticView,
    GradeView,
    StartDiagnostic,
    StartRevision,
    SubmitAnswer,
)
from services.domain.assessment import AssessmentSession, Attempt, SessionItem
from services.identity import IdentityService
from services.identity_contracts import Credentials
from services.providers import FakeMessagingProvider

REVISION_AGES = (90, 75, 60, 45, 30, 21, 14, 7, 2, 1)
DIAGNOSTIC_AGE = 91
REGISTRATION_AGE = 94


def prepare(
    identity: IdentityService,
    credentials: list[Credentials],
    anchor: datetime,
    login: Callable[[IdentityService, int], Credentials],
    response: Callable[[str, bool], dict[str, str]],
    correct: Callable[[int, int], bool],
) -> tuple[list[str], list[dict[str, object]]]:
    if anchor.utcoffset() is None or not credentials:
        raise ValueError("Temporal fixture requires an aware anchor and learners")
    subjects = {value.name: value.id for value in identity.subjects()}

    def learner(index: int) -> dict[str, object]:
        at = anchor - timedelta(days=DIAGNOSTIC_AGE)
        fake = FakeMessagingProvider()
        historical = IdentityService(
            identity.engine, identity.settings, fake, fake, clock=lambda: at, code=lambda: "246810"
        )
        assessment = AssessmentService(historical)
        subject = subjects["Mathematics" if index % 2 == 0 else "Physics"]
        credentials[index] = login(historical, index)
        token = credentials[index].access_token
        diagnostic = assessment.diagnostics.start(
            token, StartDiagnostic(subject_id=subject), uuid4(), uuid4()
        )
        for position in range(15):
            item = assessment.next_item(token, diagnostic.id, uuid4())
            receipt = assessment.submit(
                token,
                diagnostic.id,
                SubmitAnswer.model_validate(
                    {
                        "session_item_id": item.session_item_id,
                        "response": response(
                            item.response_spec.type, correct(index // 2, position)
                        ),
                    }
                ),
                uuid4(),
                uuid4(),
            )
            if not isinstance(receipt, DiagnosticReceipt) or receipt.status != "SAVED":
                raise ValueError("Temporal diagnostic answer was not sealed")
        completed = assessment.get(token, diagnostic.id)
        if (
            not isinstance(completed, DiagnosticView)
            or completed.status != "COMPLETED"
            or completed.answered_count != 15
            or completed.result is None
            or not completed.result.skills
        ):
            raise ValueError("Temporal diagnostic did not complete normally")
        topics = assessment.topics(token, subject)
        for session_index, age in enumerate(REVISION_AGES):
            at = anchor - timedelta(days=age)
            credentials[index] = login(historical, index)
            token = credentials[index].access_token
            session = assessment.start(
                token,
                StartRevision(subject_id=subject, topic_id=topics[session_index % len(topics)].id),
                uuid4(),
                uuid4(),
            )
            for position in range(5):
                item = assessment.next_item(token, session.id, uuid4())
                expected = correct(index // 2, session_index * 5 + position)
                grade = assessment.submit(
                    token,
                    session.id,
                    SubmitAnswer.model_validate(
                        {
                            "session_item_id": item.session_item_id,
                            "response": response(item.response_spec.type, expected),
                        }
                    ),
                    uuid4(),
                    uuid4(),
                )
                if (
                    not isinstance(grade, GradeView)
                    or grade.score != int(expected)
                    or grade.mastery_update_status != "COMPLETED"
                ):
                    raise ValueError("Temporal revision grade did not match fixture")
        topic = next(
            (value for value in topics if value.name == "Electricity and Magnetism"), topics[0]
        )
        return {"subject_id": str(subject), "topic_id": str(topic.id), "mode": "TOPIC"}

    with ThreadPoolExecutor(max_workers=8) as pool:
        plans = list(pool.map(learner, range(len(credentials))))
    # Re-authenticate after all historical preparation, so early workers' current
    # access credentials do not expire while the remaining fixtures are built.
    # Never extend the fixed 30-day lifetime of a historical refresh family.
    for index in range(len(credentials)):
        credentials[index] = login(identity, index)
    return [value.access_token for value in credentials], plans


def composition(engine: Engine, anchor: datetime, active: int) -> dict[str, object]:
    if anchor.utcoffset() is None or type(active) is not int or active < 1:
        raise ValueError("Temporal fixture scope invalid")
    ages = {anchor - timedelta(days=age): age for age in REVISION_AGES}
    totals = {age: 0 for age in REVISION_AGES}
    diagnostic_answers = 0
    with Session(engine) as db:
        rows = db.execute(
            select(AssessmentSession.kind, Attempt.submitted_at, func.count())
            .select_from(Attempt)
            .join(SessionItem, SessionItem.id == Attempt.session_item_id)
            .join(AssessmentSession, AssessmentSession.id == SessionItem.session_id)
            .group_by(AssessmentSession.kind, Attempt.submitted_at)
        )
        for kind, at, count in rows:
            if kind == "DIAGNOSTIC" and at == anchor - timedelta(days=DIAGNOSTIC_AGE):
                diagnostic_answers += count
            elif kind == "REVISION" and at in ages:
                totals[ages[at]] += count
            else:
                raise ValueError("Temporal fixture contains unexpected history")
        diagnostic_sessions = (
            db.scalar(
                select(func.count())
                .select_from(AssessmentSession)
                .where(
                    AssessmentSession.kind == "DIAGNOSTIC",
                    AssessmentSession.status == "COMPLETED",
                    AssessmentSession.item_count == 15,
                    AssessmentSession.diagnostic_result.is_not(None),
                )
            )
            or 0
        )
        owners = (
            db.scalar(
                select(func.count(func.distinct(AssessmentSession.learner_id))).where(
                    AssessmentSession.kind == "DIAGNOSTIC", AssessmentSession.status == "COMPLETED"
                )
            )
            or 0
        )
    if (
        diagnostic_sessions != active
        or owners != active
        or diagnostic_answers != active * 15
        or any(value != active * 5 for value in totals.values())
    ):
        raise ValueError("Temporal diagnostic or age composition differs")
    return {
        "history_diagnostic_sessions": diagnostic_sessions,
        "history_diagnostic_answers": diagnostic_answers,
        "history_revision_age_counts": {str(age): value for age, value in totals.items()},
        "history_diagnostic_age_days": DIAGNOSTIC_AGE,
    }
