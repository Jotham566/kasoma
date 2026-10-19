"""ADR-067: atomic, bounded, audited operational warning configuration."""

import hashlib
import json
from uuid import UUID, uuid4

from pydantic import ValidationError
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.config import Settings
from services.domain.content import AuditLog
from services.domain.operations_configuration import (
    WarningConfigurationState,
    WarningConfigurationVersion,
)
from services.identity import IdentityError, IdentityService
from services.operations_configuration_contracts import (
    ConfigurationChange,
    ConfigurationKey,
    ConfigurationPatch,
    ConfigurationView,
    WarningValues,
)
from services.staff import authorize

SETTING_FIELDS = {
    "request_p95_ms": "ops_request_p95_ms",
    "request_min_samples": "ops_request_min_samples",
    "failed_imports": "ops_failed_import_threshold",
    "import_age_seconds": "ops_import_age_seconds",
    "unresolved_flags": "ops_flag_backlog_threshold",
    "channel_failures": "ops_channel_failure_threshold",
    "channel_queue_age_seconds": "ops_channel_queue_age_seconds",
    "channel_dispatch_p95_ms": "ops_channel_dispatch_p95_ms",
    "channel_dispatch_min_samples": "ops_channel_dispatch_min_samples",
    "otp_failures": "ops_otp_failures_threshold",
    "model_gateway_attempts": "ops_model_gateway_attempts_threshold",
    "grading_age_seconds": "ops_grading_age_seconds",
    "export_failures": "ops_export_failure_threshold",
    "export_age_seconds": "ops_export_age_seconds",
}
ACTION = "operations.configuration.changed"


def defaults(settings: Settings) -> WarningValues:
    return WarningValues.model_validate(
        {key: getattr(settings, field) for key, field in SETTING_FIELDS.items()}
        | {"retirement_stall_seconds": settings.export_retirement_interval_seconds * 2}
    )


def fingerprint(value: dict[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def reference(nonce: UUID, revision: int, target: UUID | None, values: WarningValues) -> str:
    # A concurrency reference, not authorization. A fresh schema receives its own
    # nonce; a restored configuration preserves that immutable namespace.
    return fingerprint(
        {
            "format": "operations-warning-configuration-v1",
            "scope": str(nonce),
            "revision": revision,
            "version_id": str(target) if target else None,
            "values": values.model_dump(),
        }
    )


def state(db: Session, *, lock: bool = False) -> WarningConfigurationState:
    # An additive/partly migrated schema must not read a different schema's
    # configuration through a trailing public entry in search_path.
    if not db.scalar(
        text("""
        SELECT to_regclass(format('%I.operations_configuration_state',current_schema()))
          IS NOT NULL AND
          to_regclass(format('%I.operations_configuration_versions',current_schema()))
          IS NOT NULL
    """)
    ):
        raise ValueError("CONFIGURATION_STATE_UNAVAILABLE")
    query = select(WarningConfigurationState).where(WarningConfigurationState.id == 1)
    if lock:
        query = query.with_for_update()
    result = db.scalar(query.execution_options(populate_existing=True))
    if result is None:
        raise ValueError("CONFIGURATION_STATE_UNAVAILABLE")
    return result


def recorded(db: Session, pointer: WarningConfigurationState, target: UUID) -> ConfigurationView:
    row = db.get(WarningConfigurationVersion, target)
    if row is None or set(row.values) != set(WarningValues.model_fields):
        raise ValueError("CONFIGURATION_VERSION_UNAVAILABLE")
    values = WarningValues.model_validate(row.values)
    if reference(pointer.nonce, row.revision, row.id, values) != row.version_ref:
        raise ValueError("CONFIGURATION_VERSION_INVALID")
    return ConfigurationView(
        revision=row.revision,
        version=row.version_ref,
        source="VERSIONED",
        values=values,
        updated_at=row.created_at,
    )


def current(db: Session, settings: Settings) -> ConfigurationView:
    pointer = state(db)
    if pointer.revision == 0 and pointer.current_id is None:
        values = defaults(settings)
        return ConfigurationView(
            revision=0,
            version=reference(pointer.nonce, 0, None, values),
            source="ENVIRONMENT_DEFAULTS",
            values=values,
            updated_at=None,
        )
    if pointer.current_id is None:
        raise ValueError("CONFIGURATION_POINTER_UNAVAILABLE")
    view = recorded(db, pointer, pointer.current_id)
    if view.revision != pointer.revision:
        raise ValueError("CONFIGURATION_POINTER_INVALID")
    return view


def read(identity: IdentityService, token: str) -> ConfigurationView:
    try:
        with identity.transaction() as db:
            actor = authorize(identity, db, token, {"ADMIN"})[0]
            if not identity.rate(db, f"operations-configuration-read:{actor}", 60, 60):
                raise IdentityError("RATE_LIMITED", 429)
            return current(db, identity.settings)
    except (DBAPIError, ValueError):
        raise IdentityError("CONFIGURATION_UNAVAILABLE", 503) from None


def change(
    identity: IdentityService,
    token: str,
    key: ConfigurationKey,
    body: ConfigurationPatch,
    command: UUID,
    request_id: UUID,
) -> ConfigurationChange:
    try:
        with identity.transaction() as db:
            actor = authorize(identity, db, token, {"ADMIN"}, recent=True)[0]
            if key not in WarningValues.model_fields:
                raise IdentityError("VALIDATION_FAILED", 422)
            if not identity.rate(db, f"operations-configuration-write:{actor}", 10, 60):
                raise IdentityError("RATE_LIMITED", 429)
            pointer = state(db, lock=True)
            receipt_id = UUID(
                hex=identity.digest(
                    "operations-configuration-command", f"{pointer.nonce}:{actor}:{command}"
                )[:32]
            )
            command_hash = fingerprint({"key": key, **body.model_dump(mode="json")})
            receipt = db.get(AuditLog, receipt_id)
            if receipt is not None:
                row = db.get(WarningConfigurationVersion, receipt.target_id)
                if (
                    receipt.actor_id != actor
                    or receipt.action != ACTION
                    or row is None
                    or row.command_hash != command_hash
                    or row.changed_key != key
                    or row.reason != body.reason
                    or receipt.before_hash != row.previous_ref
                    or receipt.after_hash != row.version_ref
                ):
                    raise IdentityError("IDEMPOTENCY_CONFLICT", 409)
                return ConfigurationChange(recorded=recorded(db, pointer, row.id), replayed=True)
            previous = current(db, identity.settings)
            if previous.version != body.version:
                raise IdentityError("VERSION_CONFLICT", 409)
            try:
                values = WarningValues.model_validate(
                    previous.values.model_dump() | {key: body.value}
                )
            except ValidationError:
                raise IdentityError("VALIDATION_FAILED", 422) from None
            revision, target = pointer.revision + 1, uuid4()
            if revision > 2147483647:
                raise IdentityError("CONFIGURATION_UNAVAILABLE", 503)
            version_ref = reference(pointer.nonce, revision, target, values)
            row = WarningConfigurationVersion(
                id=target,
                revision=revision,
                values=values.model_dump(),
                version_ref=version_ref,
                previous_ref=previous.version,
                command_hash=command_hash,
                changed_key=key,
                reason=body.reason,
            )
            db.add(row)
            db.flush()
            db.add(
                AuditLog(
                    id=receipt_id,
                    actor_id=actor,
                    target_id=row.id,
                    action=ACTION,
                    reason=body.reason,
                    request_id=request_id,
                    before_hash=previous.version,
                    after_hash=version_ref,
                    created_at=row.created_at,
                )
            )
            pointer.revision, pointer.current_id = revision, row.id
            db.flush()
            return ConfigurationChange(recorded=recorded(db, pointer, row.id), replayed=False)
    except (DBAPIError, ValueError):
        raise IdentityError("CONFIGURATION_UNAVAILABLE", 503) from None
