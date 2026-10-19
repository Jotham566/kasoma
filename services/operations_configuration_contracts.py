"""Closed operational warning configuration; no secrets or learner data."""

from datetime import datetime
from typing import Literal, Self

from pydantic import ConfigDict, Field, model_validator

from services.identity_contracts import Contract
from services.operations_contracts import OperationThresholds

ConfigurationKey = Literal[
    "request_p95_ms",
    "request_min_samples",
    "failed_imports",
    "import_age_seconds",
    "unresolved_flags",
    "channel_failures",
    "channel_queue_age_seconds",
    "channel_dispatch_p95_ms",
    "channel_dispatch_min_samples",
    "otp_failures",
    "model_gateway_attempts",
    "grading_age_seconds",
    "export_failures",
    "export_age_seconds",
    "retirement_stall_seconds",
]
ConfigurationReason = Literal["INCREASE_SENSITIVITY", "REDUCE_NOISE", "REVIEWED_BASELINE"]


class WarningValues(OperationThresholds):
    model_config = ConfigDict(extra="forbid", strict=True, hide_input_in_errors=True)


class ConfigurationPatch(Contract):
    model_config = ConfigDict(extra="forbid", strict=True, hide_input_in_errors=True)
    version: str = Field(pattern=r"^[a-f0-9]{64}$")
    value: int = Field(ge=1, le=86400, strict=True)
    reason: ConfigurationReason


class ConfigurationView(Contract):
    schema_version: Literal[1] = 1
    revision: int = Field(ge=0, le=2147483647)
    version: str = Field(pattern=r"^[a-f0-9]{64}$")
    source: Literal["ENVIRONMENT_DEFAULTS", "VERSIONED"]
    values: WarningValues
    updated_at: datetime | None

    @model_validator(mode="after")
    def coherent_source(self) -> Self:
        if (self.revision == 0) != (self.source == "ENVIRONMENT_DEFAULTS"):
            raise ValueError("INVALID_CONFIGURATION_SOURCE")
        if (self.updated_at is None) != (self.revision == 0):
            raise ValueError("INVALID_CONFIGURATION_TIME")
        if self.updated_at is not None and self.updated_at.utcoffset() is None:
            raise ValueError("INVALID_CONFIGURATION_TIME")
        return self


class ConfigurationChange(Contract):
    """Recorded version, which may be older than the independently read current state."""

    recorded: ConfigurationView
    replayed: bool
