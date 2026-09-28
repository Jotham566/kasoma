"""Pure, versioned mastery calculation. No persistence, providers or answer text.

FR-MST-001–003/005; specification 05 and ADR-017. The orchestration layer must
supply immutable, authorized grade evidence. This module never assigns academics.
"""

import hashlib
import json
import math
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", allow_inf_nan=False)


class EngineConfig(FrozenModel):
    algorithm_version: Literal["weighted-evidence-v1"] = "weighted-evidence-v1"
    configuration_version: str = Field(default="mastery-baseline-v1", min_length=1)
    difficulty_mapping_version: Literal["content-difficulty-v1"] = "content-difficulty-v1"
    prior_score: float = Field(default=0.5, ge=0, le=1)
    prior_weight: float = Field(default=2.0, gt=0)
    half_life_days: float = Field(default=30.0, gt=0)
    confidence_scale: float = Field(default=5.0, gt=0)
    foundational_weight: float = Field(default=0.85, gt=0)
    core_weight: float = Field(default=1.0, gt=0)
    stretch_weight: float = Field(default=1.15, gt=0)


BASELINE = EngineConfig()


class GradeInput(FrozenModel):
    attempt_id: UUID
    item_id: UUID
    item_version_id: UUID
    concept_id: UUID
    competency_id: UUID
    occurred_at: AwareDatetime
    response_type: Literal["SINGLE_CHOICE", "MULTIPLE_CHOICE", "NUMERIC", "SHORT_TEXT"]
    content_difficulty: Literal["FOUNDATIONAL", "STANDARD", "CHALLENGING"]
    points_awarded: float = Field(ge=0)
    points_possible: float = Field(gt=0)
    hint_count: int = Field(default=0, ge=0)
    solution_seen_before_grade: bool = False
    grade_confidence: float = Field(ge=0, le=1)
    method: Literal["DETERMINISTIC", "RUBRIC_MODEL", "HUMAN"]
    status: Literal["GRADED", "PENDING", "LOW_CONFIDENCE", "REVIEW_REQUIRED"]
    mapping_weight: float = Field(gt=0, le=1)

    @model_validator(mode="after")
    def valid_points(self) -> "GradeInput":
        if self.points_awarded > self.points_possible:
            raise ValueError("Awarded points exceed possible points")
        return self


class Evidence(FrozenModel):
    calculated_at: AwareDatetime
    reason_code: Literal["GRADED_SKILL_MAPPING"] = "GRADED_SKILL_MAPPING"
    source: GradeInput
    score: float = Field(ge=0, le=1)
    engine_difficulty: Literal["FOUNDATIONAL", "CORE", "STRETCH"]
    difficulty_weight: float = Field(gt=0)
    independence_weight: float = Field(ge=0.5, le=1)
    confidence_weight: float = Field(ge=0, le=1)
    base_weight: float = Field(ge=0)
    configuration: EngineConfig
    input_hash: str


DisplayState = Literal[
    "NOT_ENOUGH_EVIDENCE", "DEVELOPING_ESTIMATE", "NEEDS_ATTENTION", "DEVELOPING", "STRONG"
]


class Estimate(FrozenModel):
    concept_id: UUID
    competency_id: UUID
    mastery: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    display_state: DisplayState
    evidence_count: int = Field(ge=0)
    input_attempt_ids: tuple[UUID, ...]
    effective_weight: float = Field(ge=0)
    distinct_item_count: int = Field(ge=0)
    distinct_format_count: int = Field(ge=0)
    last_evidence_at: AwareDatetime | None
    calculated_at: AwareDatetime
    configuration: EngineConfig
    input_hash: str
    reason_code: Literal["NO_EVIDENCE", "WEIGHTED_GRADED_EVIDENCE"]


def fingerprint(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def normalize(
    grade: GradeInput, config: EngineConfig = BASELINE, calculated_at: datetime | None = None
) -> Evidence | None:
    """Only resolved graded evidence is eligible; no confidence-only override."""
    if grade.status != "GRADED":
        return None
    difficulty: Literal["FOUNDATIONAL", "CORE", "STRETCH"]
    if grade.content_difficulty == "FOUNDATIONAL":
        difficulty, weight = "FOUNDATIONAL", config.foundational_weight
    elif grade.content_difficulty == "STANDARD":
        difficulty, weight = "CORE", config.core_weight
    else:
        difficulty, weight = "STRETCH", config.stretch_weight
    independence = max(
        0.5, 1 - 0.15 * grade.hint_count - 0.25 * int(grade.solution_seen_before_grade)
    )
    confidence = 1.0 if grade.method == "DETERMINISTIC" else grade.grade_confidence
    calculated_at = calculated_at or grade.occurred_at
    return Evidence(
        calculated_at=calculated_at,
        source=grade,
        score=grade.points_awarded / grade.points_possible,
        engine_difficulty=difficulty,
        difficulty_weight=weight,
        independence_weight=independence,
        confidence_weight=confidence,
        base_weight=weight * independence * confidence * grade.mapping_weight,
        configuration=config,
        input_hash=fingerprint(
            {
                "grade": grade.model_dump(mode="json"),
                "configuration": config.model_dump(),
                "calculated_at": calculated_at.isoformat(),
            }
        ),
    )


def display_state(mastery: float, confidence: float) -> DisplayState:
    if confidence < 0.25:
        return "NOT_ENOUGH_EVIDENCE"
    if confidence < 0.5:
        return "DEVELOPING_ESTIMATE"
    if mastery < 0.5:
        return "NEEDS_ATTENTION"
    return "DEVELOPING" if mastery < 0.75 else "STRONG"


def estimate(
    concept_id: UUID,
    competency_id: UUID,
    evidence: list[Evidence],
    calculated_at: AwareDatetime,
    config: EngineConfig = BASELINE,
) -> Estimate:
    """Replay a single skill at an explicit instant, deduplicating exact deliveries.

    Conflicting replays, mixed skills/configs, future evidence and forged derived
    fields are rejected. Persisted uniqueness must additionally be enforced by the
    future repository; this function cannot establish cross-request durability.
    """
    if calculated_at.tzinfo is None or calculated_at.utcoffset() is None:
        raise ValueError("Calculation time must be timezone-aware")
    unique: dict[UUID, Evidence] = {}
    for row in evidence:
        source = row.source
        if (source.concept_id, source.competency_id) != (concept_id, competency_id):
            raise ValueError("Evidence belongs to another skill")
        if row.configuration != config or normalize(source, config, row.calculated_at) != row:
            raise ValueError("Evidence does not match its versioned calculation")
        if source.occurred_at > calculated_at or row.calculated_at > calculated_at:
            raise ValueError("Evidence occurs after calculation time")
        previous = unique.get(source.attempt_id)
        if previous is not None and previous != row:
            raise ValueError("Conflicting evidence for one attempt and skill")
        unique[source.attempt_id] = row
    rows = sorted(unique.values(), key=lambda row: str(row.source.attempt_id))
    weights = [
        row.base_weight
        * 0.5
        ** (
            (calculated_at - row.source.occurred_at).total_seconds() / 86400 / config.half_life_days
        )
        for row in rows
    ]
    effective = math.fsum(weights)
    weighted_score = math.fsum(
        row.score * weight for row, weight in zip(rows, weights, strict=True)
    )
    mastery = (config.prior_score * config.prior_weight + weighted_score) / (
        config.prior_weight + effective
    )
    items = len({row.source.item_id for row in rows})
    formats = len({row.source.response_type for row in rows})
    coverage = min(1.0, items / 3) * min(1.0, formats / 2)
    confidence = -math.expm1(-effective / config.confidence_scale) * (0.6 + 0.4 * coverage)
    return Estimate(
        concept_id=concept_id,
        competency_id=competency_id,
        mastery=mastery,
        confidence=confidence,
        display_state=display_state(mastery, confidence),
        evidence_count=len(rows),
        input_attempt_ids=tuple(row.source.attempt_id for row in rows),
        effective_weight=effective,
        distinct_item_count=items,
        distinct_format_count=formats,
        last_evidence_at=max((row.source.occurred_at for row in rows), default=None),
        calculated_at=calculated_at,
        configuration=config,
        input_hash=fingerprint(
            {
                "concept_id": str(concept_id),
                "competency_id": str(competency_id),
                "evidence": [row.input_hash for row in rows],
                "calculated_at": calculated_at.isoformat(),
                "configuration": config.model_dump(),
            }
        ),
        reason_code="WEIGHTED_GRADED_EVIDENCE" if rows else "NO_EVIDENCE",
    )
