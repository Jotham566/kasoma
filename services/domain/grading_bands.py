"""Global calibration metadata; no learner answers, grades or reviewer identities."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from services.database import Base


class GradingBandRow(Base):
    __tablename__ = "grading_bands"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    subject_id: Mapped[UUID] = mapped_column(ForeignKey("subjects.id"))
    topic_id: Mapped[UUID] = mapped_column(ForeignKey("topics.id"))
    language: Mapped[str]
    model_version: Mapped[str]
    prompt_version: Mapped[str]
    configuration_version: Mapped[str]
    policy_version: Mapped[str]
    minimum_characters: Mapped[int]
    maximum_characters: Mapped[int]
    benchmark_id: Mapped[UUID]
    report_sha256: Mapped[str]
    benchmark_cases: Mapped[int]
    benchmark_within_tolerance: Mapped[int]
    held_out_cases: Mapped[int]
    held_out_exact: Mapped[int]
    critical_errors: Mapped[int]
    subgroup_review: Mapped[str]
    approval_id: Mapped[UUID | None]
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    enabled: Mapped[bool]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    disabled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    disable_reason: Mapped[str | None]
    revision: Mapped[int]


class GradingBandHistory(Base):
    __tablename__ = "grading_band_history"
    __table_args__ = (UniqueConstraint("band_id", "revision"),)
    id: Mapped[UUID] = mapped_column(primary_key=True)
    band_id: Mapped[UUID] = mapped_column(ForeignKey("grading_bands.id"))
    revision: Mapped[int]
    snapshot: Mapped[dict[str, Any]] = mapped_column(JSON)
