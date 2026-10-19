"""Read-only rollups; equal skill weighting is a versioned synthetic display default."""

import math
from datetime import datetime
from uuid import UUID

from services.mastery_engine import (
    BASELINE,
    Estimate,
    Evidence,
    display_state,
    estimate,
    fingerprint,
)
from services.progress_contracts import ProgressSummary

Skill = tuple[UUID, UUID]
VERSION = "progress-rollup-v1"


class RollupContext:
    """One read's immutable evidence and time; never shared between requests."""

    def __init__(self, evidence: list[Evidence], at: datetime):
        self._at = at
        self._grouped: dict[Skill, list[Evidence]] = {}
        self._attempts: dict[Skill, set[UUID]] = {}
        self._cache: dict[tuple[Skill, UUID | None], Estimate] = {}
        for row in evidence:
            skill = (row.source.concept_id, row.source.competency_id)
            self._grouped.setdefault(skill, []).append(row)
            self._attempts.setdefault(skill, set()).add(row.source.attempt_id)

    def _estimate(self, skill: Skill, omitted: UUID | None = None) -> Estimate:
        # Removing an attempt absent from this skill leaves identical replay inputs.
        if omitted not in self._attempts.get(skill, set()):
            omitted = None
        key = (skill, omitted)
        if key not in self._cache:
            rows = self._grouped.get(skill, [])
            if omitted is not None:
                rows = [row for row in rows if row.source.attempt_id != omitted]
            self._cache[key] = estimate(*skill, rows, self._at)
        return self._cache[key]

    def summarize(self, identifier: UUID, name: str, skills: set[Skill]) -> ProgressSummary:
        at = self._at
        scoped = [row for skill in skills for row in self._grouped.get(skill, ())]
        keys = sorted(skills, key=lambda s: (str(s[0]), str(s[1])))
        current = [self._estimate(key) for key in keys]
        mastery = math.fsum(e.mastery for e in current) / len(current) if current else None
        confidence = math.fsum(e.confidence for e in current) / len(current) if current else 0.0
        change = "NOT_ENOUGH_EVIDENCE"
        if scoped and current and confidence >= 0.25:
            latest = max(scoped, key=lambda e: (e.source.occurred_at, str(e.source.attempt_id)))
            before = [self._estimate(key, latest.source.attempt_id) for key in keys]
            previous_confidence = math.fsum(e.confidence for e in before) / len(before)
            if previous_confidence >= 0.25:
                previous_mastery = math.fsum(e.mastery for e in before) / len(before)
                delta = (
                    mastery if mastery is not None else BASELINE.prior_score
                ) - previous_mastery
                change = "UNCHANGED" if abs(delta) < 1e-12 else ("HIGHER" if delta > 0 else "LOWER")
        return ProgressSummary(
            id=identifier,
            name=name,
            mastery=mastery,
            confidence=confidence,
            display_state=display_state(
                mastery if mastery is not None else BASELINE.prior_score, confidence
            ),
            evidence_count=len({e.source.attempt_id for e in scoped}),
            assessed_skill_count=sum(e.evidence_count > 0 for e in current),
            mapped_skill_count=len(current),
            last_evidence_at=max((e.source.occurred_at for e in scoped), default=None),
            change=change,
            input_hash=fingerprint(
                {
                    "aggregation": VERSION,
                    "estimates": [e.input_hash for e in current],
                    "calculated_at": at.isoformat(),
                }
            ),
        )


def summarize(
    identifier: UUID, name: str, skills: set[Skill], evidence: list[Evidence], at: datetime
) -> ProgressSummary:
    return RollupContext(evidence, at).summarize(identifier, name, skills)
