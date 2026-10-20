"""ADR-061 private relational source registry, never erasure/preservation clearance.

No payload, credential, private key or source-ID list leaves this reader. The full
schema, payload/version, hold and SQL-capability checks remain separate gates.
"""

import hmac
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Literal
from uuid import UUID

from psycopg import sql
from sqlalchemy import Connection, text

from services.erasure_inventory import SourceManifestChanged, check_source_shape
from services.erasure_manifest import BASELINE


class OwnershipConflict(ValueError):
    def __init__(self, code: str = "SOURCE_OWNERSHIP_UNCERTAIN") -> None:
        self.code = code
        super().__init__(code)


# __S__ is substituted only with a server-observed quoted schema identifier.
# Reviewed B608: these five f-strings interpolate only the fixed SQL constants
# below. No caller input is concatenated; schema identifiers are separately quoted
# by psycopg and the subject UUID remains a SQL bind in every compiled query.
_SESSION = "SELECT id FROM __S__.assessment_sessions WHERE learner_id=:subject"
_ITEM = f"SELECT id FROM __S__.session_items WHERE session_id IN ({_SESSION})"  # nosec B608
_ATTEMPT = "SELECT id FROM __S__.attempts WHERE learner_id=:subject"
_EVIDENCE = "SELECT id FROM __S__.mastery_evidence WHERE learner_id=:subject"
_REQUEST = "SELECT id FROM __S__.data_subject_requests WHERE user_id=:subject"
_HOLD = f"SELECT id FROM __S__.legal_holds WHERE request_id IN ({_REQUEST})"  # nosec B608
_FLAG = "SELECT id FROM __S__.content_flags WHERE reporter_id=:subject"
_CAPTURE = f"SELECT id FROM __S__.channel_preservation_snapshots WHERE request_id IN ({_REQUEST})"  # nosec B608
_AUTHORED = "SELECT id FROM __S__.items WHERE author_id=:subject"
_VERSION = (
    f"SELECT id FROM __S__.item_versions WHERE author_id=:subject OR item_id IN ({_AUTHORED})"  # nosec B608
)
_AUDIT_REVIEW = (
    f"SELECT a.id FROM __S__.grading_audit_assignments a WHERE a.attempt_id IN ({_ATTEMPT})"  # nosec B608
)

# No fallback by naming convention. K/shared opaque T entries own no learner rows.
# Lifecycle rows participate as case evidence; callers must explicitly account for
# their own writes when later turning this reference reader into an issued plan.
_BASE_PREDICATES = MappingProxyType(
    {
        "account_erasure_state": None,
        "account_erasure_plans": f"x.request_id IN ({_REQUEST})",
        "account_erasure_jobs": f"x.request_id IN ({_REQUEST})",
        "alembic_version": None,
        "assessment_grading_history": f"x.attempt_id IN ({_ATTEMPT})",
        "assessment_grading_work": f"x.attempt_id IN ({_ATTEMPT})",
        "assessment_outbox_events": f"x.session_id IN ({_SESSION})",
        "assessment_receipts": "x.learner_id=:subject",
        "assessment_sessions": "x.learner_id=:subject",
        "attempts": "x.learner_id=:subject",
        "audit_log": None,  # Filled from the closed source graph below.
        "auth_sessions": "x.user_id=:subject",
        "channel_links": "x.user_id=:subject",
        "channel_mutation_receipts": "x.actor_id=:subject",
        "channel_preservation_bodies": f"x.snapshot_id IN ({_CAPTURE})",
        "channel_preservation_disposals": f"x.snapshot_id IN ({_CAPTURE})",
        "channel_preservation_snapshots": f"x.request_id IN ({_REQUEST})",
        "channel_senders": None,
        "competencies": None,
        "concepts": None,
        "consent_records": "x.user_id=:subject",
        "content_flag_history": f"x.flag_id IN ({_FLAG})",
        "content_flag_receipts": f"x.flag_id IN ({_FLAG})",
        "content_flags": "x.reporter_id=:subject",
        "content_import_jobs": "x.actor_id=:subject",
        "content_mutation_receipts": f"x.actor_id=:subject OR x.item_version_id IN ({_VERSION})",
        "content_outbox_events": f"x.item_version_id IN ({_VERSION})",
        "content_reviews": f"x.reviewer_id=:subject OR x.item_version_id IN ({_VERSION})",
        "conversation_states": "x.actor_id=:subject",
        "data_exports": f"x.request_id IN ({_REQUEST})",
        "data_request_receipts": f"x.request_id IN ({_REQUEST})",
        "data_request_reviews": f"x.request_id IN ({_REQUEST})",
        "data_subject_requests": "x.user_id=:subject",
        "export_retirement_state": None,
        "grades": f"x.attempt_id IN ({_ATTEMPT})",
        "grading_audit_assignments": f"x.attempt_id IN ({_ATTEMPT})",
        "grading_audit_reviews": f"x.id IN ({_AUDIT_REVIEW})",
        "grading_band_history": None,
        "grading_bands": None,
        "grading_publication_counters": None,
        "grading_publications": f"x.attempt_id IN ({_ATTEMPT})",
        "grading_review_counters": None,
        "hint_uses": "x.learner_id=:subject",
        "identity_outbox_events": "x.user_id=:subject",
        "identity_rate_buckets": None,
        "inbound_messages": "x.actor_id=:subject",
        "item_mappings": f"x.item_version_id IN ({_VERSION})",
        "item_versions": f"x.id IN ({_VERSION})",
        "items": "x.author_id=:subject",
        "learner_profiles": "x.user_id=:subject",
        "learner_subjects": "x.user_id=:subject",
        "legal_hold_receipts": f"x.hold_id IN ({_HOLD})",
        "legal_holds": f"x.request_id IN ({_REQUEST})",
        "levels": None,
        "link_codes": "x.user_id=:subject",
        "mastery_estimate_history": f"x.evidence_id IN ({_EVIDENCE})",
        "mastery_estimates": "x.learner_id=:subject",
        "mastery_evidence": "x.learner_id=:subject",
        "operations_configuration_state": None,
        "operations_configuration_versions": None,
        "otp_challenges": "x.user_id=:subject",  # Never attribute an unbound row by lookup_hash.
        "outbound_messages": "x.actor_id=:subject",
        "personal_export_generations": f"x.request_id IN ({_REQUEST})",
        "personal_export_jobs": f"x.request_id IN ({_REQUEST})",
        "reassessments": f"x.original_attempt_id IN ({_ATTEMPT})",
        "recommendation_snapshots": "x.learner_id=:subject",
        "rubric_criteria": f"x.rubric_id IN ({_VERSION})",
        "rubrics": f"x.id IN ({_VERSION})",
        "session_items": f"x.id IN ({_ITEM})",
        "subjects": None,
        "topics": None,
        "user_identifiers": "x.user_id=:subject",
        "user_roles": "x.user_id=:subject",
        "users": "x.id=:subject",
    }
)


def _audit_predicate() -> str:
    # UUID source identities come from the frozen typed PK manifest, never from a
    # column-name heuristic. Composite retry keys are deliberately not target IDs.
    targets = []
    for name, definition in BASELINE.items():
        predicate = _BASE_PREDICATES[name]
        if predicate is None or name == "audit_log":
            continue
        keys = definition.primary_key
        if name == "data_request_receipts":
            keys = ("id",)  # Explicit0039 public evidence identity, not actor/key.
        if len(keys) != 1:
            continue
        column = next(c for c in definition.columns if c.name == keys[0])
        if column.type_name != "uuid":
            continue
        targets.append(
            sql.SQL("SELECT y.{} FROM __S__.{} y WHERE {}").format(
                sql.Identifier(column.name),
                sql.Identifier(name),
                sql.SQL(predicate.replace("x.", "y.")),
            )
        )
    joined = sql.SQL(" UNION ALL ").join(targets).as_string()
    return "x.actor_id=:subject OR x.target_id=:subject OR x.target_id IN (" + joined + ")"


PREDICATES = MappingProxyType(dict(_BASE_PREDICATES) | {"audit_log": _audit_predicate()})


def assert_registry() -> None:
    if PREDICATES.keys() != BASELINE.keys():
        raise SourceManifestChanged()
    for name, source in BASELINE.items():
        non_account = source.disposition == "K" or name in {
            "channel_senders",
            "identity_rate_buckets",
        }
        if non_account != (PREDICATES[name] is None):
            raise SourceManifestChanged()
        if source.disposition == "T" and name not in {
            "channel_senders",
            "identity_rate_buckets",
            "account_erasure_plans",
        }:
            raise SourceManifestChanged()


def _qualified(template: str, schema: str) -> str:
    return template.replace("__S__", sql.Identifier(schema).as_string())


def source_query(name: str, schema: str) -> str:
    """Private closed-registry SQL compiler. No arbitrary table/column/predicate input."""
    assert_registry()
    predicate = PREDICATES.get(name)
    if predicate is None:
        raise SourceManifestChanged()
    table = sql.SQL("{}.{}").format(sql.Identifier(schema), sql.Identifier(name))
    order = sql.SQL(",").join(
        sql.SQL("x.{}").format(sql.Identifier(k)) for k in BASELINE[name].primary_key
    )
    # Digest inside PostgreSQL: no body, credential or source key is transferred.
    statement = sql.SQL("""
      SELECT encode(sha256(convert_to(x.xmin::text || ':' || to_jsonb(x)::text,'UTF8')),'hex')
      FROM {} x WHERE {} ORDER BY {}
    """).format(table, sql.SQL(_qualified(predicate, schema)), order)
    return statement.as_string()


@dataclass(frozen=True, repr=False)
class OwnershipFingerprint:
    version: str
    counts: Mapping[str, int] = field(repr=False)
    # Structural relationships/fingerprint alone never authorize closure or removal.
    semantic_clearance: Literal[False] = field(default=False, init=False)


def fingerprint(db: Connection, subject: UUID, key: bytes) -> OwnershipFingerprint:
    """Uncapped streaming reference fold in an already-open read-only RR snapshot.

    This is not an issued plan: lifecycle self-writes, all JSON versions, cross-owner
    edges, audit classification, holds, privileges and SQL scope must be validated
    before a future authorization function can use a source seal.
    """
    if len(key) < 32:
        raise ValueError("A private purpose-bound fingerprint key is required")
    if (
        not db.in_transaction()
        or db.scalar(text("SHOW transaction_isolation")) != "repeatable read"
        or db.scalar(text("SHOW transaction_read_only")) != "on"
    ):
        raise OwnershipConflict()
    assert_registry()
    check_source_shape(db)
    schema = db.scalar(text("SELECT current_schema()"))
    if not isinstance(schema, str):
        raise SourceManifestChanged()
    reject_staff_provenance(db, subject, schema)
    validate_relations(db, subject, schema)
    database_oid, namespace_oid = db.execute(
        text("""
      SELECT d.oid,n.oid FROM pg_catalog.pg_database d CROSS JOIN pg_catalog.pg_namespace n
      WHERE d.datname=current_database() AND n.nspname=current_schema()
    """)
    ).one()
    domain = (
        b"kasoma.erasure.owned-source.0045.v1\0"
        + subject.bytes
        + database_oid.to_bytes(4)
        + namespace_oid.to_bytes(4)
    )
    state = hmac.digest(key, domain, "sha256")
    counts = {}
    for name in sorted(PREDICATES):
        encoded = name.encode("ascii")
        state = hmac.digest(key, b"S" + state + len(encoded).to_bytes(2) + encoded, "sha256")
        count = 0
        if PREDICATES[name] is not None:
            rows = db.execute(
                text(source_query(name, schema)),
                {"subject": subject},
                execution_options={"stream_results": True, "yield_per": 128},
            )
            try:
                for digest in rows.scalars():
                    state = hmac.digest(key, b"R" + state + bytes.fromhex(digest), "sha256")
                    count += 1
            finally:
                rows.close()
        counts[name] = count
        state = hmac.digest(key, b"E" + state + count.to_bytes(8), "sha256")
    return OwnershipFingerprint(state.hex(), MappingProxyType(counts))


# Only edges that assert learner ownership. Staff actor/reviewer and shared-content
# FKs are not ownership edges; treating them as such would claim somebody else's data.
OWNERSHIP_EDGES = (
    ("learner_profiles", "user_id", "users", "id"),
    ("learner_subjects", "user_id", "learner_profiles", "user_id"),
    ("user_identifiers", "user_id", "users", "id"),
    ("auth_sessions", "user_id", "users", "id"),
    ("otp_challenges", "user_id", "users", "id"),
    ("consent_records", "user_id", "users", "id"),
    ("identity_outbox_events", "user_id", "users", "id"),
    ("link_codes", "user_id", "users", "id"),
    ("channel_links", "user_id", "users", "id"),
    ("assessment_sessions", "learner_id", "users", "id"),
    ("session_items", "session_id", "assessment_sessions", "id"),
    ("attempts", "learner_id", "users", "id"),
    ("attempts", "session_item_id", "session_items", "id"),
    ("grades", "attempt_id", "attempts", "id"),
    ("hint_uses", "learner_id", "users", "id"),
    ("hint_uses", "session_item_id", "session_items", "id"),
    ("assessment_receipts", "learner_id", "users", "id"),
    ("assessment_receipts", "session_id", "assessment_sessions", "id"),
    ("assessment_receipts", "attempt_id", "attempts", "id"),
    ("assessment_receipts", "hint_use_id", "hint_uses", "id"),
    ("assessment_outbox_events", "session_id", "assessment_sessions", "id"),
    ("assessment_outbox_events", "attempt_id", "attempts", "id"),
    ("recommendation_snapshots", "learner_id", "users", "id"),
    ("reassessments", "original_attempt_id", "attempts", "id"),
    ("reassessments", "session_id", "assessment_sessions", "id"),
    ("mastery_evidence", "learner_id", "users", "id"),
    ("mastery_evidence", "attempt_id", "grades", "attempt_id"),
    ("mastery_estimates", "learner_id", "users", "id"),
    ("mastery_estimate_history", "evidence_id", "mastery_evidence", "id"),
    ("assessment_grading_work", "attempt_id", "attempts", "id"),
    ("assessment_grading_history", "attempt_id", "assessment_grading_work", "attempt_id"),
    ("grading_publications", "attempt_id", "attempts", "id"),
    ("grading_audit_assignments", "attempt_id", "grading_publications", "attempt_id"),
    ("grading_audit_reviews", "id", "grading_audit_assignments", "id"),
    ("data_subject_requests", "user_id", "users", "id"),
    ("data_request_reviews", "request_id", "data_subject_requests", "id"),
    ("data_request_receipts", "request_id", "data_subject_requests", "id"),
    ("data_exports", "request_id", "data_subject_requests", "id"),
    ("personal_export_jobs", "request_id", "data_subject_requests", "id"),
    ("personal_export_generations", "request_id", "personal_export_jobs", "request_id"),
    ("account_erasure_plans", "request_id", "data_subject_requests", "id"),
    ("account_erasure_jobs", "request_id", "data_subject_requests", "id"),
    ("account_erasure_jobs", "subject_id", "users", "id"),
    ("legal_holds", "request_id", "data_subject_requests", "id"),
    ("legal_hold_receipts", "hold_id", "legal_holds", "id"),
    ("channel_preservation_snapshots", "request_id", "data_subject_requests", "id"),
    ("channel_preservation_bodies", "snapshot_id", "channel_preservation_snapshots", "id"),
    ("channel_preservation_disposals", "snapshot_id", "channel_preservation_snapshots", "id"),
    ("content_flags", "reporter_id", "users", "id"),
    ("content_flags", "attempt_id", "attempts", "id"),
    ("content_flag_history", "flag_id", "content_flags", "id"),
    ("content_flag_receipts", "flag_id", "content_flags", "id"),
    ("conversation_states", "actor_id", "users", "id"),
    ("conversation_states", "link_id", "channel_links", "id"),
    ("conversation_states", "session_id", "assessment_sessions", "id"),
    ("conversation_states", "expected_outbound_id", "outbound_messages", "id"),
    ("inbound_messages", "actor_id", "users", "id"),
    ("outbound_messages", "actor_id", "users", "id"),
    ("outbound_messages", "inbound_id", "inbound_messages", "id"),
    ("outbound_messages", "link_id", "channel_links", "id"),
    ("outbound_messages", "session_item_id", "session_items", "id"),
    ("outbound_messages", "attempt_id", "attempts", "id"),
)


def validate_relations(db: Connection, subject: UUID, schema: str) -> None:
    """Check both outgoing and incoming ownership, including dangling scoped parents."""
    assert_registry()
    for child, column, parent, target in OWNERSHIP_EDGES:
        child_scope = PREDICATES[child]
        parent_scope = PREDICATES[parent]
        if child_scope is None or parent_scope is None:
            raise SourceManifestChanged()
        statement = sql.SQL("""
          SELECT EXISTS(SELECT 1 FROM {}.{} c LEFT JOIN {}.{} p ON c.{}=p.{}
            WHERE c.{} IS NOT NULL AND
              COALESCE(({}),false) IS DISTINCT FROM COALESCE(({}),false))
        """).format(
            sql.Identifier(schema),
            sql.Identifier(child),
            sql.Identifier(schema),
            sql.Identifier(parent),
            sql.Identifier(column),
            sql.Identifier(target),
            sql.Identifier(column),
            sql.SQL(_qualified(child_scope.replace("x.", "c."), schema)),
            sql.SQL(_qualified(parent_scope.replace("x.", "p."), schema)),
        )
        if db.scalar(text(statement.as_string()), {"subject": subject}):
            raise OwnershipConflict()


# A report's initial own history/receipt is learner evidence. Staff assignments,
# subsequent triage or activity on somebody else's case must not be erased as it.
STAFF_REFERENCES = (
    ("data_request_reviews", "x.actor_id=:subject"),
    ("data_request_receipts", f"x.actor_id=:subject AND x.request_id NOT IN ({_REQUEST})"),
    ("legal_holds", "x.created_by=:subject OR x.released_by=:subject"),
    ("legal_hold_receipts", "x.actor_id=:subject"),
    ("channel_preservation_snapshots", "x.captured_by=:subject"),
    ("grading_audit_reviews", "x.reviewer_id=:subject"),
    ("account_erasure_jobs", "x.authorized_by=:subject"),
    ("content_flags", "x.owner_id=:subject"),
    (
        "content_flag_history",
        (
            "x.owner_id=:subject OR (x.actor_id=:subject AND NOT "
            f"(x.flag_id IN ({_FLAG}) AND x.revision=1 AND x.status='OPEN' "
            "AND x.owner_id IS NULL AND x.resolution_hash IS NULL))"
        ),
    ),
    ("content_flag_receipts", f"x.actor_id=:subject AND x.flag_id NOT IN ({_FLAG})"),
    (
        "audit_log",
        (
            "(x.target_id=:subject AND x.action IN ('staff.role.granted','staff.role.revoked')) "
            "OR (x.actor_id=:subject AND x.action IN ('content.created','content.edit',"
            "'content.submit','content.review','content.retire','content_import.queued',"
            "'content_import.completed','content_import.failed','content.flag.updated',"
            "'data_request.review_started','data_request.deletion_previewed',"
            "'legal_hold.created','legal_hold.released','grading_review.completed',"
            "'operations.configuration.changed'))"
        ),
    ),
)


def reject_staff_provenance(db: Connection, subject: UUID, schema: str) -> None:
    checks = [
        (name, PREDICATES[name])
        for name, definition in BASELINE.items()
        if definition.disposition == "S"
    ] + list(STAFF_REFERENCES)
    for name, predicate in checks:
        if predicate is None:
            raise SourceManifestChanged()
        statement = sql.SQL("SELECT EXISTS(SELECT 1 FROM {}.{} x WHERE {})").format(
            sql.Identifier(schema), sql.Identifier(name), sql.SQL(_qualified(predicate, schema))
        )
        if db.scalar(text(statement.as_string()), {"subject": subject}):
            raise OwnershipConflict("STAFF_PROVENANCE_REQUIRES_REVIEW")
