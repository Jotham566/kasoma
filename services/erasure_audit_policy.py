"""ADR-061 exact audit classification, never an inferred deadline or removal grant."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal
from uuid import UUID

from sqlalchemy import Connection

AuditClass = Literal["MATERIAL_CASE", "MATERIAL_CLOSURE", "SECURITY", "STAFF", "SYSTEM"]
AuditTarget = Literal["CASE", "HOLD", "FLAG", "GRADING_REVIEW", "ACTOR", "STAFF", "SYSTEM"]


class AuditClassificationUncertain(ValueError):
    def __init__(self) -> None:
        # Never reflect an unknown action: it is an untrusted database string.
        super().__init__("AUDIT_CLASSIFICATION_REQUIRES_REVIEW")


@dataclass(frozen=True)
class AuditRule:
    classification: AuditClass
    target: AuditTarget
    subject_is_actor: bool = False
    request_kind: Literal["EXPORT", "DELETE"] | None = None


# Exact ADR-061 table, including the explicitly approved0043/0044 addendum.
# No prefix matching. Anchors/deadlines, holds and dependency disposal are separate
# checks: classifying an audit never manufactures a completed case or closure clock.
AUDIT_RULES = MappingProxyType(
    {
        "data_request.erasure_plan_read": AuditRule("SECURITY", "CASE"),
        "data_request.erasure_plan_expiry_batch": AuditRule("SYSTEM", "SYSTEM"),
        "data_request.created": AuditRule("MATERIAL_CASE", "CASE", True),
        "data_request.review_started": AuditRule("MATERIAL_CASE", "CASE"),
        "data_export.queued": AuditRule("MATERIAL_CASE", "CASE", True, "EXPORT"),
        "data_export.completed": AuditRule("MATERIAL_CASE", "CASE", True, "EXPORT"),
        "legal_hold.created": AuditRule("MATERIAL_CASE", "HOLD"),
        "legal_hold.released": AuditRule("MATERIAL_CASE", "HOLD"),
        "data_request.queue_read": AuditRule("SECURITY", "ACTOR"),
        "data_request.deletion_previewed": AuditRule("SECURITY", "CASE", request_kind="DELETE"),
        "data_export.retrieved": AuditRule("SECURITY", "CASE", True, "EXPORT"),
        "legal_hold.queue_read": AuditRule("SECURITY", "CASE", request_kind="DELETE"),
        "legal_hold.source_checked": AuditRule("SECURITY", "CASE", request_kind="DELETE"),
        "legal_hold.export_sources_read": AuditRule("SECURITY", "CASE", request_kind="DELETE"),
        "content.flag.created": AuditRule("MATERIAL_CLOSURE", "FLAG", True),
        "content.flag.updated": AuditRule("MATERIAL_CLOSURE", "FLAG"),
        "content.flag.queue_read": AuditRule("SECURITY", "ACTOR"),
        "content.flag.read": AuditRule("SECURITY", "FLAG"),
        "grading_review.queue_read": AuditRule("SECURITY", "ACTOR"),
        "grading_review.read": AuditRule("SECURITY", "GRADING_REVIEW"),
        "grading_review.receipt_read": AuditRule("SECURITY", "GRADING_REVIEW"),
        "grading_review.completed": AuditRule("MATERIAL_CLOSURE", "GRADING_REVIEW"),
        "content.created": AuditRule("STAFF", "STAFF"),
        "content.edit": AuditRule("STAFF", "STAFF"),
        "content.submit": AuditRule("STAFF", "STAFF"),
        "content.review": AuditRule("STAFF", "STAFF"),
        "content.retire": AuditRule("STAFF", "STAFF"),
        "content_import.queued": AuditRule("STAFF", "STAFF"),
        "content_import.completed": AuditRule("STAFF", "STAFF"),
        "content_import.failed": AuditRule("STAFF", "STAFF"),
        "staff.role.granted": AuditRule("STAFF", "STAFF"),
        "staff.role.revoked": AuditRule("STAFF", "STAFF"),
        "operations.configuration.changed": AuditRule("STAFF", "STAFF"),
        "data_request.export_retirement_batch": AuditRule("SYSTEM", "SYSTEM"),
        "data_request.retirement_configuration": AuditRule("SYSTEM", "SYSTEM"),
    }
)


def rule_for(action: str) -> AuditRule:
    try:
        return AUDIT_RULES[action]
    except KeyError:
        raise AuditClassificationUncertain() from None


def validate_audit_sources(db: Connection, subject: UUID, schema: str) -> Mapping[str, int]:
    """Private snapshot gate; returns counts, never audit bodies, IDs or deadlines.

    This gate is deliberately separate from the structural/ownership fingerprint.
    It proves only exact action/target/actor classification, not preservation,
    lawful-root expiry, source integrity, SQL scope or permission to close/remove.
    """
    from psycopg import sql
    from sqlalchemy import text

    from services.erasure_sources import PREDICATES, OwnershipConflict, _qualified

    if (
        not db.in_transaction()
        or db.scalar(text("SHOW transaction_isolation")) != "repeatable read"
        or db.scalar(text("SHOW transaction_read_only")) != "on"
        or db.scalar(text("SELECT current_schema()")) != schema
    ):
        raise AuditClassificationUncertain()
    templates = {
        "CASE": "SELECT id FROM __S__.data_subject_requests WHERE user_id=:subject",
        "HOLD": "SELECT h.id FROM __S__.legal_holds h JOIN __S__.data_subject_requests r "
        "ON r.id=h.request_id WHERE r.user_id=:subject AND r.kind='DELETE'",
        "FLAG": "SELECT id FROM __S__.content_flags WHERE reporter_id=:subject",
        "GRADING_REVIEW": "SELECT a.id FROM __S__.grading_audit_assignments a "
        "JOIN __S__.attempts p ON p.id=a.attempt_id WHERE p.learner_id=:subject",
    }
    columns: list[sql.Composable] = [
        sql.SQL("x.target_id IN ({}) AS {}").format(
            sql.SQL(_qualified(template, schema)), sql.Identifier(kind)
        )
        for kind, template in templates.items()
    ]
    columns.append(sql.SQL('x.target_id=x.actor_id AS "ACTOR"'))
    for kind in ["EXPORT", "DELETE"]:
        columns.append(
            sql.SQL(
                "EXISTS(SELECT 1 FROM {}.data_subject_requests r "
                "WHERE r.id=x.target_id AND r.user_id=:subject AND r.kind={}) AS {}"
            ).format(sql.Identifier(schema), sql.Literal(kind), sql.Identifier(kind))
        )
    predicate = PREDICATES["audit_log"]
    if predicate is None:
        raise AuditClassificationUncertain()
    statement = sql.SQL("""
      SELECT x.action,x.actor_id=:subject AS subject_actor,x.actor_id IS NOT NULL AS has_actor,
        isfinite(x.created_at) AND x.created_at<=clock_timestamp() AS valid_clock, {}
      FROM {}.audit_log x WHERE {} ORDER BY x.id
    """).format(
        sql.SQL(",").join(columns),
        sql.Identifier(schema),
        sql.SQL(_qualified(predicate, schema)),
    )
    rows = db.execute(
        text(statement.as_string()),
        {"subject": subject},
        execution_options={"stream_results": True, "yield_per": 128},
    )
    counts = {"MATERIAL_CASE": 0, "MATERIAL_CLOSURE": 0, "SECURITY": 0}
    try:
        for row in rows.mappings():
            rule = rule_for(row["action"])
            if rule.classification == "STAFF" or (
                row["subject_actor"]
                and not rule.subject_is_actor
                and rule.classification != "SYSTEM"
            ):
                raise OwnershipConflict("STAFF_PROVENANCE_REQUIRES_REVIEW")
            targets = [kind for kind in [*templates, "ACTOR"] if row[kind]]
            if (
                rule.classification == "SYSTEM"
                or not row["has_actor"]
                or not row["valid_clock"]
                or targets != [rule.target]
                or bool(row["subject_actor"]) != rule.subject_is_actor
                or (rule.request_kind is not None and not row[rule.request_kind])
            ):
                raise AuditClassificationUncertain()
            counts[rule.classification] += 1
    finally:
        rows.close()
    return MappingProxyType(counts)
