"""ADR-061: closed case-only contracts; these types grant no execution authority."""

from datetime import timedelta
from typing import Annotated, Literal, Self
from uuid import UUID

from pydantic import AwareDatetime, Field, StrictBool, field_validator, model_validator

from services.identity_contracts import Contract

Policy = Literal["synthetic-account-erasure-v1"]
Manifest = Literal["erasure-0044-v1"]
Version = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
DurablePhase = Literal[
    "AUTHORIZED", "BARRIER_APPLIED", "PRESERVING", "REMOVING", "VERIFYING", "COMPLETED"
]
Blocker = Literal[
    "EXECUTION_DISABLED",
    "ISOLATED_SCOPE_REQUIRED",
    "SOURCE_MANIFEST_CHANGED",
    "SOURCE_OWNERSHIP_UNCERTAIN",
    "STAFF_PROVENANCE_REQUIRES_REVIEW",
    "EMBEDDED_REFERENCES_REQUIRE_REVIEW",
    "PRESERVATION_INCOMPLETE",
    "EXPORT_DRAIN_REQUIRED",
    "CLAIMANT_AUTHORITY_UNAVAILABLE",
    "PROCESSOR_UNAVAILABLE",
    "VERIFICATION_INCOMPLETE",
]
Failure = Literal["DATABASE_UNAVAILABLE", "BATCH_TIMEOUT", "INTEGRITY_CHECK_FAILED"]


class ErasureAuthorization(Contract):
    """No subject, source, cutoff, completion override or caller-provided SQL."""

    plan_id: UUID
    plan_version: Version
    decision_reference: UUID
    affirmative: StrictBool

    @field_validator("affirmative")
    @classmethod
    def confirmed(cls, value: bool) -> bool:
        if not value:
            raise ValueError("Affirmative confirmation is required")
        return value


class ErasurePlan(Contract):
    request_id: UUID
    plan_id: UUID
    version: Version
    policy: Policy = "synthetic-account-erasure-v1"
    manifest: Manifest = "erasure-0044-v1"
    observed_at: AwareDatetime
    expires_at: AwareDatetime
    authorization_available: StrictBool
    blockers: list[Blocker] = Field(max_length=11)

    @model_validator(mode="after")
    def bounded(self) -> Self:
        lifetime = self.expires_at - self.observed_at
        if not timedelta(0) < lifetime <= timedelta(minutes=10):
            raise ValueError("Plan lifetime must be positive and at most ten minutes")
        if len(set(self.blockers)) != len(self.blockers):
            raise ValueError("Blockers must be distinct")
        if self.authorization_available != (not self.blockers):
            raise ValueError("Authorization availability must agree with blockers")
        return self


class ErasureStatus(Contract):
    """Minimized durable progress, independent of the learner request's IN_REVIEW state."""

    request_id: UUID
    policy: Policy = "synthetic-account-erasure-v1"
    manifest: Manifest = "erasure-0044-v1"
    phase: DurablePhase
    blocker: Blocker | None = None
    failure: Failure | None = None
    authorized_at: AwareDatetime
    closed_at: AwareDatetime | None = None
    completed_at: AwareDatetime | None = None

    @model_validator(mode="after")
    def coherent(self) -> Self:
        if self.blocker is not None and self.failure is not None:
            raise ValueError("Progress cannot be both blocked and failed")
        if (self.phase == "AUTHORIZED") != (self.closed_at is None):
            raise ValueError("Closure must agree with the last durable phase")
        if self.closed_at is not None and self.closed_at < self.authorized_at:
            raise ValueError("Closure cannot precede authorization")
        if (self.phase == "COMPLETED") != (self.completed_at is not None):
            raise ValueError("Completion must agree with the last durable phase")
        if self.completed_at is not None:
            if self.blocker is not None or self.failure is not None:
                raise ValueError("Blocked or failed work cannot be complete")
            if self.closed_at is None or self.completed_at < self.closed_at:
                raise ValueError("Completion cannot precede closure")
        return self
