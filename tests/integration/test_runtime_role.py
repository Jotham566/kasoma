"""Assessment under a real temporary login with limited grants, never SET ROLE as owner."""

import secrets
from uuid import UUID, uuid4

import pytest
from pydantic import SecretStr
from sqlalchemy import func, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from scripts.grading_fixtures import unapproved_band
from services.assessment import AssessmentService
from services.assessment_contracts import ChoiceResponse, StartRevision, SubmitAnswer
from services.database import engine_for
from services.domain.assessment import (
    AssessmentEvent,
    AssessmentReceipt,
    AssessmentSession,
    Attempt,
    Grade,
    SessionItem,
)
from services.domain.curriculum import Topic
from services.domain.grading_audits import (
    GradingAuditAssignment,
    GradingPublication,
    GradingPublicationCounter,
)
from services.domain.grading_bands import GradingBandHistory
from services.domain.grading_work import GradingHistory, GradingWorkRow
from services.domain.identity import RateBucket
from services.domain.mastery import MasteryEstimate, MasteryEvidence, MasteryHistory
from services.grading_band_store import disable as disable_band
from services.grading_band_store import register as register_band
from services.grading_publications import publish
from services.grading_work_store import claim_next, enqueue, finish_neutral
from services.identity import IdentityError, IdentityService
from services.providers import FakeMessagingProvider
from services.short_text_eligibility import GradingScope
from tests.integration.test_assessment import assessment as assessment_fixture
from tests.integration.test_grading_bands import activate_synthetic
from tests.integration.test_identity import consent, profile

assessment = assessment_fixture
pytestmark = pytest.mark.integration


def test_assessment_works_without_schema_or_evidence_rewrite_permissions(
    assessment, caplog, capsys
):
    original, client, actors, _, _, plan = assessment
    assert profile(client, actors["other"], "2000-01-01")[0]["id"]
    assert consent(client, actors["other"], "SELF").status_code == 200
    with Session(original.engine) as db, db.begin():
        topic = db.scalar(select(Topic).order_by(Topic.id))
        band = unapproved_band(
            GradingScope(
                subject_id=topic.subject_id,
                topic_id=topic.id,
                language="en",
                model_version="fake-v1",
                prompt_version="synthetic-v2",
                configuration_version="test-v1",
            )
        )
        register_band(db, band, original.clock())
        publication_band = unapproved_band(
            band.scope.model_copy(
                update={"subject_id": UUID(plan["subject_id"]), "topic_id": UUID(plan["topic_id"])}
            )
        ).model_copy(
            update={
                "approval_id": uuid4(),
                "approved_at": original.clock(),
                "subgroup_review": "APPROVED",
            }
        )
        register_band(db, publication_band, original.clock())
        activate_synthetic(db, publication_band, original.clock())
    role = "kasoma_runtime_test_" + uuid4().hex
    with original.engine.connect() as db:
        schema = db.scalar(text("SELECT current_schema()"))
        assert db.scalar(
            text("SELECT rolsuper OR rolcreaterole FROM pg_roles WHERE rolname = current_user")
        ), "The isolated runtime-role test requires a local role-provisioning administrator"
    assert schema.startswith("identity_test_")
    password = secrets.token_urlsafe(32)
    quote = original.engine.dialect.identifier_preparer.quote
    quoted_schema, quoted_role = quote(schema), quote(role)
    created = False
    restricted = None
    try:
        try:
            with original.engine.begin() as db:
                # Bind the secret; it never appears in SQL text, command arguments or diagnostics.
                db.execute(
                    text("SELECT set_config('kasoma.test_role_password', :value, true)"),
                    {"value": password},
                )
                db.execute(
                    text(f"""DO $$ BEGIN
                    EXECUTE format('CREATE ROLE %I LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
                        NOINHERIT NOBYPASSRLS PASSWORD %L', '{role}',
                        current_setting('kasoma.test_role_password'));
                    END $$""")
                )
                db.execute(text(f"GRANT USAGE ON SCHEMA {quoted_schema} TO {quoted_role}"))
                db.execute(
                    text(f"GRANT SELECT ON ALL TABLES IN SCHEMA {quoted_schema} TO {quoted_role}")
                )
                for model, privileges in (
                    (RateBucket, "INSERT, UPDATE"),
                    (AssessmentSession, "INSERT, UPDATE"),
                    (SessionItem, "INSERT, UPDATE"),
                    (Attempt, "INSERT"),
                    (Grade, "INSERT"),
                    (AssessmentReceipt, "INSERT"),
                    (AssessmentEvent, "INSERT"),
                    (GradingWorkRow, "INSERT, UPDATE"),
                    (GradingHistory, "INSERT"),
                    (GradingBandHistory, "INSERT"),
                    (GradingPublication, "INSERT"),
                    (GradingAuditAssignment, "INSERT"),
                    (GradingPublicationCounter, "UPDATE"),
                    (MasteryEvidence, "INSERT"),
                    (MasteryEstimate, "INSERT, UPDATE"),
                    (MasteryHistory, "INSERT"),
                ):
                    db.execute(
                        text(
                            f"GRANT {privileges} ON {quoted_schema}.{quote(model.__tablename__)} "
                            f"TO {quoted_role}"
                        )
                    )
                db.execute(
                    text(
                        f"GRANT UPDATE (enabled,disabled_at,disable_reason,revision,updated_at) "
                        f"ON {quoted_schema}.grading_bands TO {quoted_role}"
                    )
                )
                # PostgreSQL row locking needs UPDATE on at least one column. The existing
                # identity/revision trigger forbids changing this ID, and revision is not writable.
                db.execute(
                    text(f"GRANT UPDATE (id) ON {quoted_schema}.item_versions TO {quoted_role}")
                )
                # Queue replay locks an existing attempt; only its immutable ID needs UPDATE
                # privilege for FOR UPDATE. The existing immutable trigger rejects changes.
                db.execute(text(f"GRANT UPDATE (id) ON {quoted_schema}.attempts TO {quoted_role}"))
                # attempt_hint_guard locks users; allow only the mutable profile-name
                # column, never identity/status/birth-date or role changes.
                db.execute(
                    text(f"GRANT UPDATE (display_name) ON {quoted_schema}.users TO {quoted_role}")
                )
        except DBAPIError:
            # A server-side dynamic SQL error can include expanded password text.
            raise RuntimeError("Temporary role provisioning failed; diagnostics withheld") from None
        created = True
        url = make_url(original.settings.database_url.get_secret_value()).set(
            username=role, password=password
        )
        settings = original.settings.model_copy(
            update={"database_url": SecretStr(url.render_as_string(hide_password=False))}
        )
        restricted = engine_for(settings)
        with restricted.connect() as db:
            assert db.scalar(text("SELECT current_user")) == role
            flags = db.execute(
                text("""SELECT rolsuper, rolcreatedb, rolcreaterole, rolbypassrls
                FROM pg_roles WHERE rolname = current_user""")
            ).one()
            assert flags == (False, False, False, False)
        fake = FakeMessagingProvider()
        identity = IdentityService(restricted, settings, fake, fake, original.clock)
        service = AssessmentService(identity)
        token = actors["learner"]["Authorization"].removeprefix("Bearer ")
        other = actors["other"]["Authorization"].removeprefix("Bearer ")
        session = service.start(token, StartRevision.model_validate(plan), uuid4(), uuid4())
        item = service.next_item(token, session.id, uuid4())
        answer = SubmitAnswer(
            session_item_id=item.session_item_id, response=ChoiceResponse(choice_id="A")
        )
        key = uuid4()
        grade = service.submit(token, session.id, answer, key, uuid4())
        assert grade.score == 1
        assert service.submit(token, session.id, answer, key, uuid4()) == grade
        with pytest.raises(IdentityError, match="RESOURCE_NOT_FOUND"):
            service.get(other, session.id)
        with Session(restricted) as db, db.begin():
            assert disable_band(db, band.id, original.clock(), "MANUAL")
            assert (
                db.scalar(
                    select(func.count())
                    .select_from(GradingBandHistory)
                    .where(GradingBandHistory.band_id == band.id)
                )
                == 2
            )
            publication = publish(db, publication_band.id, grade.attempt_id, original.clock())
            assert publication.ordinal == 1 and publication.audit_required
            assert db.scalar(select(func.count()).select_from(GradingAuditAssignment)) == 1
        for statement in (
            f"CREATE TABLE {quoted_schema}.unauthorized_table (id int)",
            f"UPDATE {quoted_schema}.grading_bands SET activated_at=now(),enabled=true",
            f"UPDATE {quoted_schema}.grading_bands SET approval_id=gen_random_uuid()",
            f"UPDATE {quoted_schema}.grading_bands SET held_out_exact=held_out_cases",
            f"DELETE FROM {quoted_schema}.grading_bands",
            f"UPDATE {quoted_schema}.grading_band_history SET snapshot=snapshot",
            f"DELETE FROM {quoted_schema}.grading_band_history",
            f"UPDATE {quoted_schema}.grading_publications SET ordinal=ordinal",
            f"DELETE FROM {quoted_schema}.grading_publications",
            f"UPDATE {quoted_schema}.grading_audit_assignments SET assigned_at=assigned_at",
            f"DELETE FROM {quoted_schema}.grading_audit_assignments",
            f"DELETE FROM {quoted_schema}.grading_publication_counters",
            f"ALTER TABLE {quoted_schema}.attempts DISABLE TRIGGER ALL",
            f"DROP TABLE {quoted_schema}.grades",
            f"DELETE FROM {quoted_schema}.assessment_grading_work",
            f"UPDATE {quoted_schema}.assessment_grading_history SET revision=revision+1",
            f"DELETE FROM {quoted_schema}.assessment_grading_history",
            f"UPDATE {quoted_schema}.attempts SET channel = 'WHATSAPP'",
            f"UPDATE {quoted_schema}.grades SET answer_specification_hash = 'tampered'",
            f"UPDATE {quoted_schema}.user_roles SET role = 'ADMIN'",
            f"UPDATE {quoted_schema}.item_versions SET status = 'RETIRED'",
            f"UPDATE {quoted_schema}.users SET id = gen_random_uuid()",
            f"UPDATE {quoted_schema}.users SET status = 'DISABLED'",
            f"UPDATE {quoted_schema}.users SET birth_date = '2000-01-01'",
            "SET session_replication_role = replica",
            "SET ROLE kasoma",
            "SELECT rolpassword FROM pg_authid",
        ):
            with restricted.connect() as db:
                with pytest.raises(DBAPIError) as rejected:
                    db.execute(text(statement))
                assert rejected.value.orig.sqlstate == "42501"
                db.rollback()
        with restricted.connect() as db:
            with pytest.raises(DBAPIError) as rejected:
                db.execute(text(f"UPDATE {quoted_schema}.item_versions SET id = id"))
            assert rejected.value.orig.sqlstate == "P0001"
            db.rollback()
        with Session(restricted) as db:
            for model in (Attempt, Grade, MasteryEvidence):
                assert db.scalar(select(func.count()).select_from(model)) == 1
        # Exercise the durable store under the same real restricted login. This valid
        # ungraded fixture is storage coverage, not short-text delivery enablement.
        next_assignment = service.next_item(token, session.id, uuid4())
        pending_id = uuid4()
        with Session(restricted) as db, db.begin():
            actor = service.authorize(db, token)
            db.add(
                Attempt(
                    id=pending_id,
                    learner_id=actor,
                    session_item_id=next_assignment.session_item_id,
                    item_version_id=next_assignment.item_version_id,
                    choice_id="A",
                    response=None,
                    submitted_at=identity.clock(),
                    hint_count=0,
                    highest_hint_level=0,
                    channel="WEB",
                )
            )
            db.flush()
            enqueue(db, pending_id, uuid4(), identity.clock())
        with Session(restricted) as db, db.begin():
            work = claim_next(db, identity.clock())
            assert work is not None
            finished = finish_neutral(db, pending_id, work.claim_id, identity.clock())
            assert finished.status == "LOW_CONFIDENCE"
            assert db.scalar(select(func.count()).select_from(GradingHistory)) == 3
        with restricted.connect() as db:
            with pytest.raises(DBAPIError) as rejected:
                db.execute(text(f"UPDATE {quoted_schema}.attempts SET id=id"))
            assert rejected.value.orig.sqlstate == "P0001"
            db.rollback()
        assert password not in caplog.text + capsys.readouterr().out
    finally:
        if restricted is not None:
            restricted.dispose()
        if created:
            with original.engine.begin() as db:
                db.execute(
                    text(f"REVOKE UPDATE (id) ON {quoted_schema}.item_versions FROM {quoted_role}")
                )
                db.execute(
                    text(f"REVOKE ALL ON ALL TABLES IN SCHEMA {quoted_schema} FROM {quoted_role}")
                )
                db.execute(
                    text(
                        f"REVOKE UPDATE (display_name) ON {quoted_schema}.users FROM {quoted_role}"
                    )
                )
                db.execute(
                    text(f"REVOKE UPDATE (id) ON {quoted_schema}.attempts FROM {quoted_role}")
                )
                db.execute(text(f"REVOKE ALL ON SCHEMA {quoted_schema} FROM {quoted_role}"))
                db.execute(
                    text(
                        f"REVOKE UPDATE (enabled,disabled_at,disable_reason,revision,updated_at) "
                        f"ON {quoted_schema}.grading_bands FROM {quoted_role}"
                    )
                )
                db.execute(text(f"DROP ROLE {quoted_role}"))
    with original.engine.connect() as db:
        assert (
            db.scalar(text("SELECT count(*) FROM pg_roles WHERE rolname = :role"), {"role": role})
            == 0
        )
