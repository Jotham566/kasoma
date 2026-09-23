"""Identity-owned tables; no learning or academic data."""

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from services.database import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    display_name: Mapped[str | None]
    birth_date: Mapped[date | None]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Identifier(Base):
    __tablename__ = "user_identifiers"
    __table_args__ = (UniqueConstraint("type", "lookup_hash"),)
    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    type: Mapped[str] = mapped_column(String(10))
    normalized_value_encrypted: Mapped[str]
    lookup_hash: Mapped[str] = mapped_column(String(64))
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AuthSession(Base):
    __tablename__ = "auth_sessions"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    family: Mapped[UUID] = mapped_column(index=True)
    access_hash: Mapped[str] = mapped_column(String(64), unique=True)
    refresh_hash: Mapped[str] = mapped_column(String(64), unique=True)
    authenticated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    access_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    rotated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Challenge(Base):
    __tablename__ = "otp_challenges"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    purpose: Mapped[str] = mapped_column(String(12))
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    policy_version: Mapped[str]
    type: Mapped[str] = mapped_column(String(10))
    lookup_hash: Mapped[str] = mapped_column(String(64), index=True)
    encrypted_identifier: Mapped[str]
    code_hash: Mapped[str] = mapped_column(String(64))
    attempts: Mapped[int] = mapped_column(default=0)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class RateBucket(Base):
    __tablename__ = "identity_rate_buckets"
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    count: Mapped[int]
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class LearnerProfile(Base):
    __tablename__ = "learner_profiles"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    level_id: Mapped[UUID] = mapped_column(ForeignKey("levels.id"))


class LearnerSubject(Base):
    __tablename__ = "learner_subjects"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("learner_profiles.user_id"), primary_key=True)
    subject_id: Mapped[UUID] = mapped_column(ForeignKey("subjects.id"), primary_key=True)


class Consent(Base):
    __tablename__ = "consent_records"
    __table_args__ = (UniqueConstraint("user_id", "idempotency_key"),)
    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    consent_type: Mapped[str]
    basis: Mapped[str]
    policy_version: Mapped[str]
    evidence_encrypted: Mapped[str | None]
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    idempotency_key: Mapped[UUID]
    request_hash: Mapped[str]


class IdentityEvent(Base):
    __tablename__ = "identity_outbox_events"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    type: Mapped[str]
    version: Mapped[int] = mapped_column(default=1)
    payload: Mapped[dict[str, str]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
