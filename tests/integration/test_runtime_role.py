"""Assessment under a real temporary login with limited grants, never SET ROLE as owner."""

import secrets
from uuid import uuid4

import pytest
from pydantic import SecretStr
from sqlalchemy import func, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

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
from services.domain.identity import RateBucket
from services.domain.mastery import MasteryEstimate, MasteryEvidence, MasteryHistory
from services.identity import IdentityError, IdentityService
from services.providers import FakeMessagingProvider
from tests.integration.test_assessment import assessment as assessment_fixture
from tests.integration.test_identity import consent, profile

assessment = assessment_fixture
pytestmark = pytest.mark.integration


def test_assessment_works_without_schema_or_evidence_rewrite_permissions(
    assessment, caplog, capsys
):
    original, client, actors, _, _, plan = assessment
    assert profile(client, actors["other"], "2000-01-01")[0]["id"]
    assert consent(client, actors["other"], "SELF").status_code == 200
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
                # PostgreSQL row locking needs UPDATE on at least one column. The existing
                # identity/revision trigger forbids changing this ID, and revision is not writable.
                db.execute(
                    text(f"GRANT UPDATE (id) ON {quoted_schema}.item_versions TO {quoted_role}")
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
        for statement in (
            f"CREATE TABLE {quoted_schema}.unauthorized_table (id int)",
            f"ALTER TABLE {quoted_schema}.attempts DISABLE TRIGGER ALL",
            f"DROP TABLE {quoted_schema}.grades",
            f"UPDATE {quoted_schema}.attempts SET channel = 'WHATSAPP'",
            f"UPDATE {quoted_schema}.grades SET answer_specification_hash = 'tampered'",
            f"UPDATE {quoted_schema}.user_roles SET role = 'ADMIN'",
            f"UPDATE {quoted_schema}.item_versions SET status = 'RETIRED'",
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
                db.execute(text(f"REVOKE ALL ON SCHEMA {quoted_schema} FROM {quoted_role}"))
                db.execute(text(f"DROP ROLE {quoted_role}"))
    with original.engine.connect() as db:
        assert (
            db.scalar(text("SELECT count(*) FROM pg_roles WHERE rolname = :role"), {"role": role})
            == 0
        )
