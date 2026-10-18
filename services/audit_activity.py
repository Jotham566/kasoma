"""Bounded audit activity, without record-level support access or free text."""

from collections import Counter
from datetime import datetime, timedelta
from typing import Literal

from pydantic import Field
from sqlalchemy import case, select

from services.domain.content import AuditLog
from services.identity import IdentityError, IdentityService
from services.identity_contracts import Contract
from services.staff import authorize

Category = Literal["CONTENT", "FLAGS", "IMPORTS", "PRIVACY", "ROLES", "GRADING_REVIEW", "OTHER"]
CATEGORIES: tuple[Category, ...] = (
    "CONTENT",
    "FLAGS",
    "IMPORTS",
    "PRIVACY",
    "ROLES",
    "GRADING_REVIEW",
    "OTHER",
)
LIMIT = 10000


class AuditActivityCount(Contract):
    category: Category
    count: int = Field(ge=0, le=LIMIT)


class AuditActivity(Contract):
    window_start: datetime
    window_end: datetime
    sampled_count: int = Field(ge=0, le=LIMIT)
    capped: bool
    sample_limit: Literal[10000] = 10000
    counts: list[AuditActivityCount] = Field(min_length=7, max_length=7)
    measure: Literal["AUDIT_ACTIVITY_SAMPLE"] = "AUDIT_ACTIVITY_SAMPLE"


PREFIXES: tuple[tuple[str, Category], ...] = (
    ("content.flag.", "FLAGS"),
    ("content.", "CONTENT"),
    ("content_import.", "IMPORTS"),
    ("data_request.", "PRIVACY"),
    ("legal_hold.", "PRIVACY"),
    ("staff.role.", "ROLES"),
    ("grading_review.", "GRADING_REVIEW"),
)


def read(identity: IdentityService, token: str) -> AuditActivity:
    with identity.transaction() as db:
        actor = authorize(identity, db, token, {"ADMIN"})[0]
        if not identity.rate(db, f"audit-activity-read:{actor}", 20, 60):
            raise IdentityError("RATE_LIMITED", 429)
        end = identity.clock()
        start = end - timedelta(hours=24)
        # Classify inside SQL: arbitrary audit action text never crosses this boundary.
        category_expression = case(
            *[
                (AuditLog.action.startswith(prefix, autoescape=True), name)
                for prefix, name in PREFIXES
            ],
            else_="OTHER",
        )
        categories = list(
            db.scalars(
                select(category_expression)
                .where(AuditLog.created_at >= start, AuditLog.created_at <= end)
                .order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
                .limit(LIMIT + 1)
            )
        )
        counts = Counter(categories[:LIMIT])
        return AuditActivity(
            window_start=start,
            window_end=end,
            sampled_count=min(len(categories), LIMIT),
            capped=len(categories) > LIMIT,
            counts=[AuditActivityCount(category=name, count=counts[name]) for name in CATEGORIES],
        )
