"""Strict, generated identity API contracts (FR-ID-001–005)."""

from datetime import date
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class OTPRequest(Contract):
    identifier: str = Field(min_length=3, max_length=254)
    purpose: Literal["LOGIN", "LINK", "GUARDIAN"] = "LOGIN"
    device_id: UUID


class OTPAccepted(Contract):
    challenge_id: UUID
    message: str = "If eligible, a verification code will be delivered."


class OTPVerify(Contract):
    purpose: Literal["LOGIN", "LINK"] = "LOGIN"
    challenge_id: UUID
    code: str = Field(pattern=r"^[0-9]{6}$")


class Credentials(Contract):
    access_token: str
    refresh_token: str
    expires_in: Literal[900] = 900
    token_type: Literal["Bearer"] = "Bearer"


class Refresh(Contract):
    refresh_token: str = Field(min_length=32, max_length=128)


class ProfilePatch(Contract):
    display_name: str = Field(min_length=1, max_length=80)
    birth_date: date
    subject_ids: list[UUID] = Field(min_length=1, max_length=2)


class SubjectView(Contract):
    id: UUID
    name: str


class ProfileView(Contract):
    id: UUID
    display_name: str | None
    birth_date: date | None
    level: Literal["Senior 4"] = "Senior 4"
    subject_ids: list[UUID]
    consent_required: list[str]
    learning_allowed: bool
    policy_version: str
    identifier_count: int


class ConsentInput(Contract):
    consent_type: Literal["SELF", "ASSENT", "GUARDIAN", "WITHDRAW"]
    policy_version: str = Field(max_length=80)
    affirmative: Literal[True]
    guardian_name: str | None = Field(default=None, min_length=1, max_length=80)
    guardian_relationship: str | None = Field(default=None, min_length=1, max_length=80)
    challenge_id: UUID | None = None
    code: str | None = Field(default=None, pattern=r"^[0-9]{6}$")
