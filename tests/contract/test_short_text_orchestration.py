"""Budget/retry/independence rehearsal using FakeModelProvider only."""

import json
from uuid import UUID

import pytest

from services.providers import FakeModelProvider, ModelResult
from services.short_text_orchestration import RehearsalBudget, rehearse_short_text
from services.short_text_validation import SyntheticRubricContext


@pytest.fixture
def context():
    return SyntheticRubricContext(
        rubric_version_id=UUID(int=1),
        item_version_id=UUID(int=2),
        maximum_points=1,
        criteria=[
            {
                "criterion_id": "R1",
                "maximum_points": 1,
                "criterion_text": "Name the original synthetic label.",
                "acceptable_evidence": ["synthetic"],
                "common_errors": ["A different label is supplied."],
                "prohibited_inferences": ["Do not infer an omitted label."],
            }
        ],
        misconception_ids=[],
        correct_elements=["Synthetic match."],
        missing_elements=["Synthetic missing."],
        next_actions=["Review the example."],
    )


def candidate(points=1, **kwargs):
    raw = json.dumps(
        {
            "criterion_results": [
                {
                    "criterion_id": "R1",
                    "points_awarded": points,
                    "evidence_excerpt": "synthetic" if points else "",
                    "justification_code": "SUPPORTED" if points else "MISSING",
                }
            ],
            "total_points": points,
            "confidence": 1.0,
            "detected_misconception_ids": [],
            "feedback": {
                "correct_elements": [],
                "missing_elements": [],
                "next_action": "Review the example.",
            },
        }
    )
    return ModelResult(
        status="CANDIDATE",
        provider="fake",
        model="fixture-v1",
        raw_output=raw,
        input_tokens=100,
        output_tokens=100,
        **kwargs,
    )


def run(gateway, context, **kwargs):
    return rehearse_short_text(
        gateway,
        context=context,
        response=kwargs.pop("response", "synthetic response"),
        flagged=kwargs.pop("flagged", False),
        budget=kwargs.pop("budget", RehearsalBudget()),
        **kwargs,
    )


def test_independent_passes_share_context_not_candidates(context):
    gateway = FakeModelProvider([candidate(), candidate()])
    result = run(gateway, context)
    assert result.status == "AGREEING_CANDIDATES"
    assert result.automatic_scoring_enabled is False
    assert result.requests == 2
    assert result.input_tokens == result.output_tokens == 200
    assert result.rubric_version_id == context.rubric_version_id
    first, second = gateway.calls
    assert first.prompt_version == "synthetic-short-text-criteria-first-v2"
    assert second.prompt_version == "synthetic-short-text-evidence-first-v2"
    for task in (first, second):
        assert task.structured_input["rubric"]["criteria"] == [
            context.criteria[0].model_dump(mode="json")
        ]
    assert first.prompt_version != second.prompt_version
    assert first.context_references == second.context_references
    assert first.structured_input["rubric"] == second.structured_input["rubric"]
    assert first.structured_input["instruction"] != second.structured_input["instruction"]
    assert first.response_schema == second.response_schema
    assert "criterion_results" not in second.structured_input
    assert "synthetic response" not in repr(first)
    assert "synthetic response" not in repr(result)


@pytest.mark.parametrize("bad_pass", [0, 1])
def test_one_schema_repair_total(context, bad_pass):
    fixtures = [candidate(), candidate()]
    fixtures.insert(bad_pass, candidate().model_copy(update={"raw_output": "broken json"}))
    gateway = FakeModelProvider(fixtures)
    assert run(gateway, context).status == "AGREEING_CANDIDATES"
    assert len(gateway.calls) == 3
    assert sum(task.structured_input["repair_schema"] for task in gateway.calls) == 1
    assert gateway.calls[bad_pass + 1].prompt_version.endswith("-repair")


def test_second_invalid_schema_stops_without_extra_call(context):
    invalid = candidate().model_copy(update={"raw_output": "{}"})
    gateway = FakeModelProvider([invalid, invalid, candidate()])
    assert run(gateway, context).reason == "VALIDATION_FAILED"
    assert len(gateway.calls) == 2
    gateway = FakeModelProvider([invalid, candidate(), invalid, candidate()])
    assert run(gateway, context).reason == "VALIDATION_FAILED"
    assert len(gateway.calls) == 3


def test_same_total_cannot_hide_criterion_disagreement(context):
    # Two-point fixture can have equal totals with different criterion points.
    context.maximum_points = 2
    context.criteria.append(context.criteria[0].model_copy(update={"criterion_id": "R2"}))
    one = json.loads(candidate().raw_output)
    two = json.loads(candidate().raw_output)
    one["criterion_results"].append(
        {
            "criterion_id": "R2",
            "points_awarded": 0,
            "evidence_excerpt": "",
            "justification_code": "MISSING",
        }
    )
    two["criterion_results"][0].update(
        points_awarded=0, evidence_excerpt="", justification_code="MISSING"
    )
    two["criterion_results"].append(
        {
            "criterion_id": "R2",
            "points_awarded": 1,
            "evidence_excerpt": "synthetic",
            "justification_code": "SUPPORTED",
        }
    )
    gateway = FakeModelProvider(
        [
            candidate().model_copy(update={"raw_output": json.dumps(one)}),
            candidate().model_copy(update={"raw_output": json.dumps(two)}),
        ]
    )
    assert run(gateway, context).reason == "DISAGREEMENT"


def test_total_disagreement_never_scores(context):
    gateway = FakeModelProvider([candidate(), candidate(0)])
    result = run(gateway, context)
    assert result.reason == "DISAGREEMENT"
    assert result.candidate is None
    assert result.automatic_scoring_enabled is False


@pytest.mark.parametrize("failure", [TimeoutError("secret diagnostic"), RuntimeError("raw answer")])
def test_provider_failures_never_echo_or_retry(context, failure, caplog):
    gateway = FakeModelProvider([failure, candidate()])
    result = run(gateway, context)
    assert result.reason == "PROVIDER_FAILURE"
    assert result.requests == 1
    assert str(failure) not in result.model_dump_json()
    assert str(failure) not in caplog.text


def test_preflight_and_provider_flags(context):
    gateway = FakeModelProvider([candidate(flagged=True)])
    assert run(gateway, context, flagged=True).reason == "FLAGGED"
    assert run(gateway, context, response=" ").reason == "INPUT_INVALID"
    assert run(gateway, context, response="x" * 2001).reason == "INPUT_INVALID"
    assert gateway.calls == []
    assert run(gateway, context).reason == "FLAGGED"
    assert len(gateway.calls) == 1


def test_default_fake_falls_back(context):
    result = run(FakeModelProvider(), context)
    assert result.reason == "PROVIDER_FALLBACK"
    assert result.candidate is None


def test_semantic_validation_failure_does_not_repair(context):
    invalid = json.loads(candidate().raw_output)
    invalid["criterion_results"][0]["evidence_excerpt"] = "invented"
    gateway = FakeModelProvider(
        [candidate().model_copy(update={"raw_output": json.dumps(invalid)})]
    )
    assert run(gateway, context).reason == "VALIDATION_FAILED"
    assert len(gateway.calls) == 1


def test_deadline_rejects_late_result_and_no_followup(context):
    ticks = iter([0, 0, 0.1])
    gateway = FakeModelProvider([candidate(), candidate()])
    assert (
        run(
            gateway, context, budget=RehearsalBudget(timeout_ms=100), clock=lambda: next(ticks)
        ).reason
        == "BUDGET"
    )
    assert gateway.calls[0].timeout_ms == 100
    assert len(gateway.calls) == 1


def test_pre_dispatch_budget_exhaustion(context):
    gateway = FakeModelProvider([candidate()])
    assert run(gateway, context, budget=RehearsalBudget(max_tokens=2)).reason == "BUDGET"
    assert gateway.calls == []
    ticks = iter([0, 1])
    assert (
        run(
            gateway, context, budget=RehearsalBudget(timeout_ms=1), clock=lambda: next(ticks)
        ).reason
        == "BUDGET"
    )
    assert gateway.calls == []


def test_token_reservations_and_reported_excess(context):
    gateway = FakeModelProvider([candidate(), candidate()])
    result = run(gateway, context, budget=RehearsalBudget(max_tokens=1224))
    assert result.reason == "BUDGET"
    assert result.requests == 1
    task = gateway.calls[0]
    assert task.max_input_tokens + task.max_output_tokens == 1224
    gateway = FakeModelProvider([candidate().model_copy(update={"output_tokens": 1025})])
    assert run(gateway, context).reason == "BUDGET"
    assert len(gateway.calls) == 1


def test_repair_respects_request_ceiling(context):
    invalid = candidate().model_copy(update={"raw_output": "{}"})
    gateway = FakeModelProvider([invalid, candidate(), candidate()])
    assert run(gateway, context, budget=RehearsalBudget(max_requests=2)).reason == "BUDGET"
    assert len(gateway.calls) == 2


@pytest.mark.parametrize(
    "field,value",
    [
        ("short_text_max_requests", 1),
        ("short_text_max_requests", 4),
        ("short_text_max_tokens", 1),
        ("short_text_max_tokens", 16385),
        ("short_text_timeout_ms", 0),
        ("short_text_timeout_ms", 5001),
    ],
)
def test_runtime_budget_configuration_cannot_expand_existing_envelope(field, value):
    from pydantic import ValidationError

    from services.config import Settings

    with pytest.raises(ValidationError):
        Settings(**{field: value})


def test_runtime_defaults_match_existing_shared_budget():
    from services.config import Settings

    settings = Settings()
    budget = RehearsalBudget()
    assert (
        settings.short_text_max_requests,
        settings.short_text_max_tokens,
        settings.short_text_timeout_ms,
    ) == (budget.max_requests, budget.max_tokens, budget.timeout_ms)
