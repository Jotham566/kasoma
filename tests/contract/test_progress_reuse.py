"""FR-MST-004/005: exact legacy outputs with bounded request-local replay work."""

import hashlib
import json
from datetime import timedelta
from pathlib import Path
from uuid import UUID

import pytest

from services import progress_engine as engine
from services.mastery_engine import normalize
from tests.contract.progress_reuse_fixtures import SCOPES, SKILLS, cases
from tests.contract.test_mastery_engine import NOW, grade

BASELINE = json.loads(
    (Path(__file__).parents[1] / "fixtures/progress-rollup-v1-reuse-baseline.json").read_text()
)


def fingerprint(value):
    return hashlib.sha256(
        json.dumps(value.model_dump(mode="json"), sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


@pytest.mark.parametrize("case,rows,at,scopes", cases())
def test_legacy_complete_summary_fingerprints(case, rows, at, scopes):
    for i, (name, skills) in enumerate(scopes):
        assert (
            fingerprint(engine.summarize(UUID(int=i + 1), name, skills, rows, at))
            == BASELINE[f"{case}:{name}"]
        )


@pytest.mark.parametrize("case,rows,at,scopes", cases())
def test_reused_complete_summary_fingerprints(case, rows, at, scopes):
    context = engine.RollupContext(rows, at)
    for i, (name, skills) in enumerate(scopes):
        assert (
            fingerprint(context.summarize(UUID(int=i + 1), name, skills))
            == BASELINE[f"{case}:{name}"]
        )


def test_replays_identical_skill_inputs_only_once_and_reuses_unchanged_before(monkeypatch):
    _, rows, at, _ = cases()[3]
    actual = engine.estimate
    calls = []

    def observed(concept, competency, evidence, when):
        calls.append((concept, competency, tuple(e.input_hash for e in evidence), when))
        return actual(concept, competency, evidence, when)

    monkeypatch.setattr(engine, "estimate", observed)
    context = engine.RollupContext(rows, at)
    for _ in range(2):
        for i, (name, skills) in enumerate(SCOPES):
            context.summarize(UUID(int=i + 1), name, skills)
    assert len(calls) == len(set(calls))
    # One current estimate and one changed latest-attempt comparison per skill;
    # other skills' before inputs are identical to their current inputs.
    assert len(calls) == 2 * len(SKILLS)


def test_context_copies_input_and_does_not_share_mutable_summaries_or_fresh_reads():
    rows = [normalize(grade())]
    context = engine.RollupContext(rows, NOW)
    scope = {(UUID(int=1), UUID(int=2))}
    first = context.summarize(UUID(int=99), "Synthetic", scope)
    rows.clear()
    assert context.summarize(UUID(int=99), "Synthetic", scope) == first
    first.name = "Mutated returned DTO"
    assert context.summarize(UUID(int=99), "Synthetic", scope).name == "Synthetic"
    fresh = engine.RollupContext(rows, NOW).summarize(UUID(int=99), "Synthetic", scope)
    assert fresh.evidence_count == 0
    later = engine.RollupContext([normalize(grade())], NOW + timedelta(days=10))
    assert later.summarize(UUID(int=99), "Synthetic", scope).input_hash != first.input_hash


@pytest.mark.parametrize("failure", ["future", "forged", "conflict"])
def test_reuse_preserves_corruption_and_future_rejection(failure):
    row = normalize(grade())
    if failure == "future":
        rows = [normalize(grade(occurred_at=NOW + timedelta(seconds=1)))]
    elif failure == "forged":
        rows = [row.model_copy(update={"base_weight": 999})]
    else:
        rows = [row, normalize(grade(points_awarded=0))]
    context = engine.RollupContext(rows, NOW)
    for _ in range(2):
        with pytest.raises(ValueError):
            context.summarize(UUID(int=99), "Synthetic", SKILLS)
