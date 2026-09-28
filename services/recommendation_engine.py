"""FR-MST-006: pure, replayable ranking over safe, versioned synthetic inputs."""

from math import prod
from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, Field

from services.mastery_engine import Estimate, FrozenModel, fingerprint


class RankingConfig(FrozenModel):
    algorithm_version: Literal["recommendation-v1"] = "recommendation-v1"
    configuration_version: Literal["synthetic-ranking-v1"] = "synthetic-ranking-v1"
    review_days: float = Field(default=7, gt=0)
    repetition_step: float = Field(default=0.1, ge=0, le=1)
    prerequisite_threshold: float = 0.45
    prerequisite_confidence: float = 0.35
    sparse_confidence: float = 0.5


class Target(FrozenModel):
    estimate: Estimate
    topic_id: UUID
    topic: str
    importance: float = Field(default=1, ge=0.5, le=1.5)
    prerequisite_concepts: tuple[UUID, ...] = ()
    recent_exposures: int = Field(default=0, ge=0)


class Candidate(FrozenModel):
    item_id: UUID
    version_id: UUID
    concept_id: UUID
    competency_id: UUID
    mapping_weight: float = Field(gt=0, le=1)
    difficulty: Literal["FOUNDATIONAL", "STANDARD", "CHALLENGING"]
    response_type: Literal["SINGLE_CHOICE", "NUMERIC"]
    scenario_hash: str
    historical_exposures: int = Field(default=0, ge=0)
    expected_seconds: int = Field(ge=10, le=3600)


class RankingInput(FrozenModel):
    calculated_at: AwareDatetime
    configuration: RankingConfig = RankingConfig()
    curriculum_version_ids: tuple[UUID, ...] = ()
    targets: tuple[Target, ...]
    candidates: tuple[Candidate, ...]
    desired_item_count: int = Field(ge=5, le=10)


class Score(FrozenModel):
    concept_id: UUID
    competency_id: UUID
    factors: dict[str, float]
    priority: float
    prerequisite_impact: int
    blocked_by: tuple[UUID, ...]


class RankedPlan(FrozenModel):
    inputs: RankingInput
    input_hash: str
    scores: tuple[Score, ...]
    concept_id: UUID | None
    competency_id: UUID | None
    topic_id: UUID | None
    topic: str | None
    item_version_ids: tuple[UUID, ...]
    reason_code: Literal[
        "GATHER_MORE_EVIDENCE", "PREREQUISITE_GAP", "PRACTISE_SUPPORTED_GAP", "CONTENT_UNAVAILABLE"
    ]
    learner_text: str
    item_reasons: tuple[str, ...]
    estimated_minutes: int


def rank(inputs: RankingInput) -> RankedPlan:
    """Snapshot is canonicalized so database row order cannot change replay."""
    targets = sorted(
        inputs.targets, key=lambda t: (str(t.estimate.concept_id), str(t.estimate.competency_id))
    )
    candidates = sorted(inputs.candidates, key=lambda c: (str(c.version_id), str(c.competency_id)))
    inputs = inputs.model_copy(update={"targets": tuple(targets), "candidates": tuple(candidates)})
    config, at = inputs.configuration, inputs.calculated_at
    keys = [(t.estimate.concept_id, t.estimate.competency_id) for t in targets]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate skill input")
    if len({(c.version_id, c.competency_id) for c in candidates}) != len(candidates):
        raise ValueError("Duplicate candidate mapping")
    graph: dict[UUID, set[UUID]] = {}
    for target in targets:
        estimate = target.estimate
        if estimate.calculated_at != at or (
            estimate.last_evidence_at and estimate.last_evidence_at > at
        ):
            raise ValueError("Mismatched calculation time")
        graph.setdefault(estimate.concept_id, set()).update(target.prerequisite_concepts)
    visited: set[UUID] = set()
    visiting: set[UUID] = set()

    def visit(concept: UUID) -> None:
        if concept in visiting:
            raise ValueError("Cyclic prerequisite graph")
        if concept in visited:
            return
        visiting.add(concept)
        for prerequisite in graph.get(concept, set()):
            visit(prerequisite)
        visiting.remove(concept)
        visited.add(concept)

    for concept in graph:
        visit(concept)
    gaps = {
        t.estimate.concept_id
        for t in targets
        if t.estimate.mastery < config.prerequisite_threshold
        and t.estimate.confidence >= config.prerequisite_confidence
    }

    def blockers(concept: UUID) -> set[UUID]:
        result: set[UUID] = set()
        for prerequisite in graph.get(concept, set()):
            if prerequisite in gaps:
                result.add(prerequisite)
            result.update(blockers(prerequisite))
        return result

    blocked = {concept: blockers(concept) for concept in graph}
    impact = {concept: sum(concept in values for values in blocked.values()) for concept in graph}
    scores = []
    for target in targets:
        e = target.estimate
        age = (
            config.review_days
            if e.last_evidence_at is None
            else (at - e.last_evidence_at).total_seconds() / 86400
        )
        prerequisites = [
            min(
                (t.estimate.mastery for t in targets if t.estimate.concept_id == prerequisite),
                default=0.5,
            )
            for prerequisite in graph[e.concept_id]
        ]
        available_items = {
            c.item_id
            for c in candidates
            if (c.concept_id, c.competency_id) == (e.concept_id, e.competency_id)
        }
        factors = {
            "gap": 1 - e.mastery,
            "importance": target.importance,
            "uncertainty": 0.75 + 0.5 * (1 - e.confidence),
            "spacing_due": 0.8 + 0.5 * min(1, age / config.review_days),
            "prerequisite_readiness": 0.4 + 0.6 * min(prerequisites, default=1),
            "recent_repetition_penalty": max(
                0.3, 1 - config.repetition_step * target.recent_exposures
            ),
            "available_content_factor": float(len(available_items) >= inputs.desired_item_count),
        }
        scores.append(
            Score(
                concept_id=e.concept_id,
                competency_id=e.competency_id,
                factors=factors,
                priority=prod(factors.values()),
                prerequisite_impact=impact[e.concept_id],
                blocked_by=tuple(sorted(blocked[e.concept_id], key=str)),
            )
        )
    by_key = {(s.concept_id, s.competency_id): s for s in scores}

    def ordering(t: Target) -> tuple[float, int, float, float, int, str, str]:
        e = t.estimate
        s = by_key[(e.concept_id, e.competency_id)]
        return (
            -s.priority,
            -s.prerequisite_impact,
            -t.importance,
            e.last_evidence_at.timestamp() if e.last_evidence_at else float("-inf"),
            t.recent_exposures,
            str(e.concept_id),
            str(e.competency_id),
        )

    eligible = [
        t
        for t in targets
        if by_key[(t.estimate.concept_id, t.estimate.competency_id)].factors[
            "available_content_factor"
        ]
    ]
    if eligible:
        preferred = min(eligible, key=ordering)
        needs = blocked[preferred.estimate.concept_id]
        if needs:
            eligible = [
                t
                for t in eligible
                if t.estimate.concept_id in needs and not blocked[t.estimate.concept_id]
            ]
    if not eligible:
        return RankedPlan(
            inputs=inputs,
            input_hash=fingerprint(inputs.model_dump(mode="json")),
            scores=tuple(scores),
            concept_id=None,
            competency_id=None,
            topic_id=None,
            topic=None,
            item_version_ids=(),
            reason_code="CONTENT_UNAVAILABLE",
            learner_text="More reviewed content is needed before recommending practice.",
            item_reasons=(),
            estimated_minutes=0,
        )
    chosen = min(eligible, key=ordering)
    e = chosen.estimate
    sparse = e.confidence < config.sparse_confidence
    reason: Literal["GATHER_MORE_EVIDENCE", "PREREQUISITE_GAP", "PRACTISE_SUPPORTED_GAP"] = (
        "GATHER_MORE_EVIDENCE"
        if sparse
        else "PREREQUISITE_GAP"
        if impact[e.concept_id]
        else "PRACTISE_SUPPORTED_GAP"
    )
    message = (
        f"Practise {chosen.topic} to gather more evidence. This is a developing estimate."
        if sparse
        else f"Practise {chosen.topic} to strengthen a prerequisite before dependent skills."
        if impact[e.concept_id]
        else f"Continue practice in {chosen.topic} based on current evidence and review timing."
    )
    desired = (
        "STANDARD"
        if sparse
        else "FOUNDATIONAL"
        if e.mastery < 0.5
        else "CHALLENGING"
        if e.mastery >= 0.75
        else "STANDARD"
    )
    pool = [
        c for c in candidates if (c.concept_id, c.competency_id) == (e.concept_id, e.competency_id)
    ]
    selected: list[Candidate] = []
    while len(selected) < inputs.desired_item_count:
        formats = {c.response_type for c in selected}
        scenarios = {c.scenario_hash for c in selected}
        selected.append(
            min(
                pool,
                key=lambda c: (
                    -c.mapping_weight,
                    c.difficulty != desired,
                    c.response_type in formats,
                    c.scenario_hash in scenarios,
                    c.historical_exposures,
                    str(c.item_id),
                    str(c.version_id),
                ),
            )
        )
        pool = [c for c in pool if c.item_id != selected[-1].item_id]
    return RankedPlan(
        inputs=inputs,
        input_hash=fingerprint(inputs.model_dump(mode="json")),
        scores=tuple(scores),
        concept_id=e.concept_id,
        competency_id=e.competency_id,
        topic_id=chosen.topic_id,
        topic=chosen.topic,
        item_version_ids=tuple(c.version_id for c in selected),
        reason_code=reason,
        learner_text=message,
        item_reasons=tuple(
            f"Question {i + 1}: approved mapping to this skill; "
            "selected for mapping strength, difficulty, variety and prior exposure."
            for i, _ in enumerate(selected)
        ),
        estimated_minutes=max(1, round(sum(c.expected_seconds for c in selected) / 60)),
    )


def replay(plan: RankedPlan) -> None:
    if rank(plan.inputs) != plan:
        raise ValueError("Recommendation replay mismatch")
