"""Read-only rollups; equal skill weighting is a versioned synthetic display default."""

import math
from datetime import datetime
from uuid import UUID

from services.mastery_engine import BASELINE, Evidence, display_state, estimate, fingerprint
from services.progress_contracts import ProgressSummary

Skill = tuple[UUID, UUID]
VERSION = "progress-rollup-v1"


def summarize(
    identifier: UUID, name: str, skills: set[Skill], evidence: list[Evidence], at: datetime
) -> ProgressSummary:
    scoped = [e for e in evidence if (e.source.concept_id, e.source.competency_id) in skills]
    grouped: dict[Skill, list[Evidence]] = {skill: [] for skill in skills}
    for row in scoped:
        grouped[(row.source.concept_id, row.source.competency_id)].append(row)
    keys = sorted(skills, key=lambda s: (str(s[0]), str(s[1])))
    current = [estimate(*key, grouped[key], at) for key in keys]
    mastery = math.fsum(e.mastery for e in current) / len(current) if current else None
    confidence = math.fsum(e.confidence for e in current) / len(current) if current else 0.0
    change = "NOT_ENOUGH_EVIDENCE"
    if scoped and current and confidence >= 0.25:
        latest = max(scoped, key=lambda e: (e.source.occurred_at, str(e.source.attempt_id)))
        before = [
            estimate(
                *key,
                [e for e in grouped[key] if e.source.attempt_id != latest.source.attempt_id],
                at,
            )
            for key in keys
        ]
        previous_confidence = math.fsum(e.confidence for e in before) / len(before)
        if previous_confidence >= 0.25:
            previous_mastery = math.fsum(e.mastery for e in before) / len(before)
            delta = (mastery if mastery is not None else BASELINE.prior_score) - previous_mastery
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
