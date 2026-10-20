"""ADR-072 case-only plan transport; no installation, closure or erasure capability."""

from dataclasses import dataclass
from uuid import UUID

from psycopg import sql
from sqlalchemy import text

from services.database import engine_for
from services.domain.data_requests import DataRequest, DataRequestReview
from services.domain.identity import UserRole
from services.erasure_capability_contract import CAPABILITY_VERSION
from services.erasure_config import load_erasure
from services.erasure_contracts import ErasurePlan
from services.identity import IdentityError, IdentityService


@dataclass(frozen=True, repr=False)
class PlanContext:
    session_id: UUID
    database_oid: int
    namespace_oid: int
    source_nonce: UUID


def context(identity: IdentityService, token: str, target: UUID) -> PlanContext:
    # End this ordinary transaction before using a second private connection.
    with identity.transaction() as db:
        auth = identity.authenticate(db, token, recent=True)
        if db.get(UserRole, (auth.user_id, "ADMIN")) is None:
            raise IdentityError("FORBIDDEN", 403)
        if not identity.rate(db, "erasure-plan-read:" + str(auth.user_id), 10, 60):
            raise IdentityError("RATE_LIMITED", 429)
        request = db.get(DataRequest, target)
        if request is None:
            raise IdentityError("RESOURCE_NOT_FOUND", 404)
        if request.user_id == auth.user_id:
            raise IdentityError("SELF_REVIEW_FORBIDDEN", 403)
        if request.kind != "DELETE":
            raise IdentityError("DELETE_REQUIRED", 409)
        if request.completed_at is not None:
            raise IdentityError("REQUEST_COMPLETED", 409)
        review = db.get(DataRequestReview, target)
        if review is None or review.actor_id != auth.user_id:
            raise IdentityError("REVIEW_OWNERSHIP_REQUIRED", 403)
        # Fenced metadata only, never a credential or a learner-body projection.
        source = db.execute(
            text("""
          SELECT s.database_oid,s.namespace_oid,s.scope_nonce
          FROM account_erasure_state s JOIN pg_catalog.pg_database d
            ON d.oid=s.database_oid AND d.datname=current_database()
          JOIN pg_catalog.pg_namespace n ON n.oid=s.namespace_oid
            AND n.nspname=current_schema()
          WHERE s.singleton=1 AND s.original_scope_eligible
            AND s.owner_oid IS NOT NULL AND s.executor_oid IS NOT NULL
        """)
        ).one_or_none()
        if source is None:
            raise IdentityError("ERASURE_UNAVAILABLE", 503)
        return PlanContext(auth.id, source.database_oid, source.namespace_oid, source.scope_nonce)


def plan(identity: IdentityService, token: str, target: UUID, correlation: UUID) -> ErasurePlan:
    engine = None
    try:
        actor = context(identity, token, target)
        cfg = load_erasure()
        if (
            not cfg.enabled
            or cfg.authorizer_database_url is None
            or cfg.capability_namespace is None
            or cfg.namespace != "public"
            or identity.settings.app_env not in {"development", "test"}
            or identity.settings.model_provider != "fake"
            or identity.settings.email_provider != "fake"
            or identity.settings.sms_provider != "fake"
            or identity.settings.whatsapp_provider != "fake"
            or identity.settings.allow_external_api_calls
        ):
            raise IdentityError("ERASURE_UNAVAILABLE", 503)
        private = identity.settings.model_copy(update={"database_url": cfg.authorizer_database_url})
        engine = engine_for(private)
        with engine.connect().execution_options(isolation_level="REPEATABLE READ") as db:
            with db.begin():
                db.execute(text("SET LOCAL statement_timeout='5000ms'"))
                readiness = sql.SQL("SELECT {}.readiness()").format(
                    sql.Identifier(cfg.capability_namespace)
                )
                if db.scalar(text(readiness.as_string())) != {
                    "version": CAPABILITY_VERSION,
                    "creation_enabled": False,
                    "execution_enabled": False,
                }:
                    raise IdentityError("ERASURE_UNAVAILABLE", 503)
                statement = sql.SQL(
                    "SELECT {}.issue_plan(:session,:case,CAST(:database AS oid),"
                    "CAST(:namespace AS oid),:nonce,:correlation)"
                ).format(sql.Identifier(cfg.capability_namespace))
                result = ErasurePlan.model_validate(
                    db.scalar(
                        text(statement.as_string()),
                        {
                            "session": actor.session_id,
                            "case": target,
                            "database": actor.database_oid,
                            "namespace": actor.namespace_oid,
                            "nonce": actor.source_nonce,
                            "correlation": correlation,
                        },
                    )
                )
                if result.request_id != target or result.authorization_available:
                    # This staged v3 implementation cannot assert completed clearance.
                    raise IdentityError("ERASURE_UNAVAILABLE", 503)
                return result
    except IdentityError:
        raise
    except Exception:
        # Driver/context errors cannot reflect private URLs/session IDs or source data.
        raise IdentityError("ERASURE_UNAVAILABLE", 503) from None
    finally:
        if engine is not None:
            engine.dispose()
