"""Approved ADR-061 structural baseline; dispositions are not executable SQL authority.

Frozen from the assessed0044 inventory. Runtime code never parses documentation.
Ownership, payload versions, holds, privileges and barriers require separate validation.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal

Disposition = Literal["K", "S", "U", "C", "I", "L", "M", "R", "A", "F", "X", "B", "T"]


@dataclass(frozen=True)
class SourceColumn:
    name: str
    type_name: str
    nullable: bool


@dataclass(frozen=True)
class SourceDefinition:
    disposition: Disposition
    primary_key: tuple[str, ...]
    columns: tuple[SourceColumn, ...]


def _source(action: Disposition, key: tuple[str, ...], shape: str) -> SourceDefinition:
    columns = []
    for field in shape.split():
        name, kind = field.split(":")
        columns.append(SourceColumn(name.removesuffix("?"), kind, name.endswith("?")))
    return SourceDefinition(action, key, tuple(columns))


BASELINE_REVISION = "0044"
BASELINE: Mapping[str, SourceDefinition] = MappingProxyType(
    {
        "alembic_version": _source("K", ("version_num",), "version_num:varchar"),
        "assessment_grading_history": _source(
            "L", ("id",), "id:uuid attempt_id:uuid revision:int4 snapshot:jsonb"
        ),
        "assessment_grading_work": _source(
            "L",
            ("attempt_id",),
            "attempt_id:uuid correlation_id:uuid revision:int4 status:text "
            "queued_at:timestamptz claim_id?:uuid claimed_at?:timestamptz "
            "lease_until?:timestamptz finished_at?:timestamptz reason?:text",
        ),
        "assessment_outbox_events": _source(
            "L",
            ("id",),
            "id:uuid session_id:uuid attempt_id?:uuid type:text version:int4 request_id:uuid "
            "created_at:timestamptz published_at?:timestamptz hint_count?:int4 "
            "highest_hint_level?:int4",
        ),
        "assessment_receipts": _source(
            "L",
            ("learner_id", "key"),
            "learner_id:uuid key:uuid request_hash:text session_id:uuid attempt_id?:uuid "
            "hint_use_id?:uuid",
        ),
        "assessment_sessions": _source(
            "L",
            ("id",),
            "id:uuid learner_id:uuid subject_id:uuid topic_id?:uuid status:text "
            "item_count:int4 reason:text plan_version:text started_at:timestamptz "
            "expires_at:timestamptz completed_at?:timestamptz kind:text "
            "diagnostic_result?:json recommendation_snapshot?:json",
        ),
        "attempts": _source(
            "L",
            ("id",),
            "id:uuid learner_id:uuid session_item_id:uuid item_version_id:uuid "
            "choice_id?:text submitted_at:timestamptz hint_count:int4 channel:text "
            "response?:jsonb highest_hint_level:int4 rubric_version_id?:uuid",
        ),
        "audit_log": _source(
            "A",
            ("id",),
            "id:uuid actor_id?:uuid target_id:uuid action:text reason:text request_id:uuid "
            "before_hash?:text after_hash?:text created_at:timestamptz",
        ),
        "auth_sessions": _source(
            "C",
            ("id",),
            "id:uuid user_id:uuid family:uuid access_hash:varchar refresh_hash:varchar "
            "authenticated_at:timestamptz access_expires_at:timestamptz "
            "expires_at:timestamptz rotated_at?:timestamptz revoked_at?:timestamptz",
        ),
        "channel_links": _source(
            "I",
            ("id",),
            "id:uuid user_id:uuid sender_hash:text external_identifier_encrypted?:text "
            "status:text revision:int4 linked_at:timestamptz opted_out_at?:timestamptz "
            "updated_at:timestamptz",
        ),
        "channel_mutation_receipts": _source(
            "M",
            ("actor_id", "key"),
            "actor_id:uuid key:uuid request_hash:text created_at:timestamptz",
        ),
        "channel_preservation_bodies": _source(
            "B", ("snapshot_id",), "snapshot_id:uuid encrypted_payload:text"
        ),
        "channel_preservation_disposals": _source(
            "A", ("snapshot_id",), "snapshot_id:uuid disposed_at:timestamptz"
        ),
        "channel_preservation_snapshots": _source(
            "A",
            ("id",),
            "id:uuid request_id:uuid source_kind:text source_link_id:uuid link_revision:int4 "
            "source_state_version?:int8 source_version:text captured_by:uuid "
            "captured_at:timestamptz",
        ),
        "channel_senders": _source(
            "T",
            ("sender_hash",),
            "sender_hash:text barrier_at?:timestamptz last_provider_at?:timestamptz "
            "updated_at:timestamptz",
        ),
        "competencies": _source("K", ("id",), "id:uuid name:varchar"),
        "concepts": _source(
            "K",
            ("id",),
            "id:uuid topic_id:uuid name:varchar syllabus_reference:text synthetic:bool",
        ),
        "consent_records": _source(
            "R",
            ("id",),
            "id:uuid user_id:uuid consent_type:text basis:text policy_version:text "
            "evidence_encrypted?:text granted_at:timestamptz revoked_at?:timestamptz "
            "idempotency_key:uuid request_hash:text",
        ),
        "content_flag_history": _source(
            "F",
            ("id",),
            "id:uuid flag_id:uuid actor_id:uuid revision:int4 status:text priority:text "
            "owner_id?:uuid resolution_hash?:text created_at:timestamptz",
        ),
        "content_flag_receipts": _source(
            "F", ("actor_id", "key"), "actor_id:uuid key:uuid request_hash:text flag_id:uuid"
        ),
        "content_flags": _source(
            "F",
            ("id",),
            "id:uuid item_id:uuid item_version_id:uuid attempt_id:uuid reporter_id:uuid "
            "category:text comment_encrypted:text report_hash:text status:text priority:text "
            "owner_id?:uuid revision:int4 resolution_encrypted?:text created_at:timestamptz "
            "updated_at:timestamptz resolved_at?:timestamptz retention_due_at?:timestamptz",
        ),
        "content_import_jobs": _source(
            "S",
            ("id",),
            "id:uuid actor_id:uuid key:uuid request_hash:text request_id:uuid payload?:jsonb "
            "results:jsonb status:text attempts:int4 error_code?:text created_at:timestamptz "
            "available_at:timestamptz expires_at:timestamptz finished_at?:timestamptz",
        ),
        "content_mutation_receipts": _source(
            "S",
            ("actor_id", "key"),
            "actor_id:uuid key:uuid request_hash:text item_version_id:uuid",
        ),
        "content_outbox_events": _source(
            "S",
            ("id",),
            "id:uuid item_version_id:uuid type:text version:int4 request_id:uuid "
            "created_at:timestamptz",
        ),
        "content_reviews": _source(
            "S",
            ("id",),
            "id:uuid item_version_id:uuid reviewer_id:uuid content_hash:text "
            "review_round:int4 decision:text checklist:json reason:text "
            "created_at:timestamptz",
        ),
        "conversation_states": _source(
            "M",
            ("link_id",),
            "link_id:uuid actor_id:uuid link_revision:int4 session_id?:uuid "
            "expected_outbound_id?:uuid updated_at:timestamptz expires_at:timestamptz "
            "state_version:int8",
        ),
        "data_exports": _source(
            "X",
            ("request_id",),
            "request_id:uuid encrypted_payload:text digest:text created_at:timestamptz "
            "expires_at:timestamptz",
        ),
        "data_request_receipts": _source(
            "A",
            ("actor_id", "key"),
            "actor_id:uuid key:uuid request_hash:text request_id:uuid id:uuid",
        ),
        "data_request_reviews": _source(
            "A", ("request_id",), "request_id:uuid actor_id:uuid created_at:timestamptz"
        ),
        "data_subject_requests": _source(
            "A",
            ("id",),
            "id:uuid user_id:uuid kind:text authenticated_at:timestamptz "
            "verification_method:text retention_policy:text created_at:timestamptz "
            "completed_at?:timestamptz retention_due_at?:timestamptz export_digest?:text",
        ),
        "export_retirement_state": _source(
            "K",
            ("singleton",),
            "singleton:bool enabled:bool phase:int2 next_receipt?:uuid next_review?:uuid "
            "next_job?:uuid next_request?:uuid updated_at:timestamptz",
        ),
        "grades": _source(
            "L",
            ("attempt_id",),
            "attempt_id:uuid item_version_id:uuid answer_specification_hash:text result:json "
            "rubric_version_id?:uuid",
        ),
        "grading_audit_assignments": _source(
            "L", ("id",), "id:uuid attempt_id:uuid assigned_at:timestamptz"
        ),
        "grading_audit_reviews": _source(
            "L",
            ("id",),
            "id:uuid band_id:uuid reviewer_id:uuid criterion_points:jsonb critical_error:text "
            "exact_agreement:bool completion_ordinal:int8 completed_at:timestamptz "
            "request_key:uuid request_hash:text correlation_id:uuid",
        ),
        "grading_band_history": _source(
            "K", ("id",), "id:uuid band_id:uuid revision:int4 snapshot:jsonb"
        ),
        "grading_bands": _source(
            "K",
            ("id",),
            "id:uuid subject_id:uuid topic_id:uuid language:text model_version:text "
            "prompt_version:text configuration_version:text policy_version:text "
            "minimum_characters:int4 maximum_characters:int4 benchmark_id:uuid "
            "report_sha256:text benchmark_cases:int8 benchmark_within_tolerance:int8 "
            "held_out_cases:int8 held_out_exact:int8 critical_errors:int8 "
            "subgroup_review:text approval_id?:uuid approved_at?:timestamptz enabled:bool "
            "created_at:timestamptz updated_at:timestamptz activated_at?:timestamptz "
            "disabled_at?:timestamptz disable_reason?:text revision:int4",
        ),
        "grading_publication_counters": _source(
            "K", ("band_id",), "band_id:uuid returned_grades:int8 assigned_audits:int8"
        ),
        "grading_publications": _source(
            "L",
            ("attempt_id",),
            "attempt_id:uuid band_id:uuid ordinal:int8 audit_required:bool "
            "published_at:timestamptz sampling_policy:text session_ordinal?:int4",
        ),
        "grading_review_counters": _source("K", ("band_id",), "band_id:uuid completed_audits:int8"),
        "hint_uses": _source(
            "L",
            ("id",),
            "id:uuid learner_id:uuid session_item_id:uuid level:int4 phase:text "
            "created_at:timestamptz",
        ),
        "identity_outbox_events": _source(
            "L",
            ("id",),
            "id:uuid user_id:uuid type:text version:int4 payload:json created_at:timestamptz",
        ),
        "identity_rate_buckets": _source(
            "T", ("key",), "key:varchar count:int4 expires_at:timestamptz"
        ),
        "inbound_messages": _source(
            "M",
            ("id",),
            "id:uuid message_hash:text request_hash:text request_id:uuid sender_hash:text "
            "sender_encrypted?:text actor_id?:uuid command:text code_hash?:text "
            "status_reference?:text delivery_status?:text provider_at:timestamptz "
            "received_at:timestamptz available_at:timestamptz processed_at?:timestamptz "
            "status:text attempts:int4 error_code?:text reply_reference?:text "
            "reply_encrypted?:text",
        ),
        "item_mappings": _source(
            "S",
            ("item_version_id", "competency_id"),
            "item_version_id:uuid competency_id:uuid weight:float8",
        ),
        "item_versions": _source(
            "S",
            ("id",),
            "id:uuid item_id:uuid version:int4 revision:int4 review_round:int4 status:varchar "
            "author_id:uuid topic_id?:uuid concept_id?:uuid document:json "
            "content_hash:varchar requires_second_review:bool synthetic:bool "
            "created_at:timestamptz updated_at:timestamptz",
        ),
        "items": _source(
            "S", ("id",), "id:uuid subject_id:uuid author_id:uuid created_at:timestamptz"
        ),
        "learner_profiles": _source("I", ("user_id",), "user_id:uuid level_id:uuid"),
        "learner_subjects": _source("I", ("user_id", "subject_id"), "user_id:uuid subject_id:uuid"),
        "legal_hold_receipts": _source(
            "A", ("actor_id", "key"), "actor_id:uuid key:uuid request_hash:text hold_id:uuid"
        ),
        "legal_holds": _source(
            "A",
            ("id",),
            "id:uuid request_id:uuid record_type:text record_id:uuid decision_reference:uuid "
            "reason:text created_by:uuid created_at:timestamptz expires_at:timestamptz "
            "released_at?:timestamptz released_by?:uuid release_reference?:uuid",
        ),
        "levels": _source("K", ("id",), "id:uuid name:varchar"),
        "link_codes": _source(
            "C",
            ("id",),
            "id:uuid user_id:uuid key:uuid code_hash?:text created_at:timestamptz "
            "expires_at:timestamptz consumed_at?:timestamptz revoked_at?:timestamptz",
        ),
        "mastery_estimate_history": _source("L", ("id",), "id:uuid evidence_id:uuid snapshot:json"),
        "mastery_estimates": _source(
            "L",
            ("learner_id", "concept_id", "competency_id"),
            "learner_id:uuid concept_id:uuid competency_id:uuid snapshot:json",
        ),
        "mastery_evidence": _source(
            "L",
            ("id",),
            "id:uuid learner_id:uuid attempt_id:uuid concept_id:uuid competency_id:uuid "
            "occurred_at:timestamptz snapshot:json",
        ),
        "operations_configuration_state": _source(
            "K", ("id",), "id:int4 nonce:uuid revision:int4 current_id?:uuid"
        ),
        "operations_configuration_versions": _source(
            "K",
            ("id",),
            "id:uuid revision:int4 thresholds:jsonb version_ref:text previous_ref:text "
            "command_hash:text changed_key:text reason:text created_at:timestamptz",
        ),
        "otp_challenges": _source(
            "C",
            ("id",),
            "id:uuid purpose:varchar user_id?:uuid policy_version:text type:varchar "
            "lookup_hash:varchar encrypted_identifier:text code_hash:varchar attempts:int4 "
            "expires_at:timestamptz consumed_at?:timestamptz",
        ),
        "outbound_messages": _source(
            "M",
            ("id",),
            "id:uuid inbound_id:uuid link_id?:uuid actor_id?:uuid recipient_hash:text "
            "recipient_encrypted?:text template:text status:text provider_id?:text "
            "attempts:int4 error_code?:text created_at:timestamptz available_at:timestamptz "
            "sent_at?:timestamptz status_at?:timestamptz link_revision?:int4 "
            "session_item_id?:uuid attempt_id?:uuid menu_topic_ids?:json",
        ),
        "personal_export_generations": _source(
            "X",
            ("id",),
            "id:uuid request_id:uuid created_at:timestamptz lease_until:timestamptz "
            "published_at?:timestamptz expires_at?:timestamptz encrypted_manifest?:text "
            "digest?:text size?:int4",
        ),
        "personal_export_jobs": _source(
            "A",
            ("request_id",),
            "request_id:uuid status:text correlation_id:uuid created_at:timestamptz "
            "queued_at:timestamptz updated_at:timestamptz finished_at?:timestamptz "
            "next_attempt_at?:timestamptz attempts:int4 failure?:text grant_family?:uuid "
            "grant_authenticated_at?:timestamptz generation_id?:uuid",
        ),
        "reassessments": _source(
            "L",
            ("original_attempt_id",),
            "original_attempt_id:uuid session_id:uuid item_version_id:uuid basis:text "
            "elapsed_seconds:float8 snapshot:json input_hash:text",
        ),
        "recommendation_snapshots": _source(
            "L", ("id",), "id:uuid learner_id:uuid subject_id:uuid input_hash:text snapshot:json"
        ),
        "rubric_criteria": _source(
            "S",
            ("rubric_id", "criterion_id"),
            "rubric_id:uuid criterion_id:text position:int4 maximum_points:int4 "
            "criterion_text:text acceptable_evidence:jsonb common_errors:jsonb "
            "prohibited_inferences:jsonb",
        ),
        "rubrics": _source("S", ("id",), "id:uuid maximum_points:int4"),
        "session_items": _source(
            "L",
            ("id",),
            "id:uuid session_id:uuid item_version_id:uuid position:int4 reason:text "
            "served_at?:timestamptz grading_band_id?:uuid",
        ),
        "subjects": _source("K", ("id",), "id:uuid level_id:uuid name:varchar"),
        "topics": _source("K", ("id",), "id:uuid subject_id:uuid name:varchar"),
        "user_identifiers": _source(
            "I",
            ("id",),
            "id:uuid user_id:uuid type:varchar normalized_value_encrypted:text "
            "lookup_hash:varchar verified_at:timestamptz",
        ),
        "user_roles": _source(
            "S", ("user_id", "role"), "user_id:uuid role:varchar granted_at:timestamptz"
        ),
        "users": _source(
            "U",
            ("id",),
            "id:uuid status:varchar display_name?:text birth_date?:date created_at:timestamptz",
        ),
    }
)
