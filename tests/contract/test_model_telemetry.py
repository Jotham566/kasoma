"""NFR-OBS-001: synthetic gateway metadata cannot disclose task or provider payloads."""

import hashlib
import json
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from pydantic import TypeAdapter, ValidationError

from services.model_telemetry import ModelCallEvent, RehearsalEvent, RehearsalTelemetry
from services.providers import FakeModelProvider, ModelResult, ModelTask
from tests.contract.test_short_text_orchestration import candidate, run
from tests.contract.test_short_text_orchestration import context as rubric_context

context = rubric_context


def events(caplog):
    return [
        json.loads(record.message)
        for record in caplog.records
        if '"event":"model.' in record.message
    ]


def task(**kwargs):
    return ModelTask(
        task="grade_short_answer",
        prompt_version="synthetic-short-text-criteria-first-v2",
        text="CANARY-answer",
        structured_input={"rubric": "CANARY-criterion"},
        **kwargs,
    )


def test_correlated_calls_and_outcome_include_repairs_without_content(context, caplog, capsys):
    request_id = uuid4()
    broken = candidate().model_copy(update={"raw_output": "CANARY-invalid-answer"})
    gateway = FakeModelProvider([broken, candidate(), candidate()])
    result = run(gateway, context, request_id=request_id)
    assert result.reason == "AGREEMENT" and result.requests == 3
    logged = events(caplog)
    calls, outcome = logged[:-1], logged[-1]
    assert [event["call_index"] for event in calls] == [1, 2, 3]
    assert calls[1]["prompt_version"].endswith("-repair")
    assert all(event["correlation_id"] == str(request_id) for event in logged)
    assert all(event["elapsed_ms"] >= 0 for event in logged)
    assert sum(event["input_tokens"] for event in calls) == result.input_tokens
    assert sum(event["output_tokens"] for event in calls) == result.output_tokens
    assert outcome["reason"] == "AGREEMENT" and outcome["automatic_scoring_enabled"] is False
    assert "CANARY" not in caplog.text + capsys.readouterr().out
    for event in calls:
        assert ModelCallEvent.model_validate_json(json.dumps(event))
    assert RehearsalEvent.model_validate_json(json.dumps(outcome))
    for forbidden in ["criterion_text", "evidence_excerpt", "context_references", "raw_output"]:
        assert forbidden not in caplog.text
    assert str(context.item_version_id) not in caplog.text
    assert str(context.rubric_version_id) not in caplog.text


@pytest.mark.parametrize("failure", [RuntimeError("CANARY-secret"), TimeoutError("CANARY-answer")])
def test_failure_records_unknown_usage_not_zero_or_diagnostics(context, caplog, failure):
    result = run(FakeModelProvider([failure]), context)
    assert result.reason == "PROVIDER_FAILURE" and result.requests == 1
    call, outcome = events(caplog)
    assert call["status"] == "FAILED"
    assert call["provider"] == call["model"] == call["usage_source"] == "UNAVAILABLE"
    assert call["input_tokens"] is call["output_tokens"] is call["output_fingerprint"] is None
    assert outcome["reason"] == "PROVIDER_FAILURE"
    assert "CANARY" not in caplog.text


@pytest.mark.parametrize(
    "response,flagged,reason", [(" ", False, "INPUT_INVALID"), ("synthetic", True, "FLAGGED")]
)
def test_preflight_emits_outcome_without_fabricated_call(
    context, caplog, response, flagged, reason
):
    gateway = FakeModelProvider()
    run(gateway, context, response=response, flagged=flagged)
    assert not gateway.calls
    assert len(events(caplog)) == 1
    assert events(caplog)[0]["reason"] == reason
    assert events(caplog)[0]["requests"] == 0
    UUID(events(caplog)[0]["correlation_id"])


def test_elapsed_rounding_and_unregistered_metadata_are_minimized(caplog):
    ticks = iter([5.0, 5.0, 5.0124, 5.0124])
    telemetry = RehearsalTelemetry(clock=lambda: next(ticks))
    unregistered = task().model_copy(update={"prompt_version": "CANARY-prompt-secret"})
    output = ModelResult(
        status="CANDIDATE",
        provider="CANARY-provider",
        model="CANARY-model",
        raw_output="CANARY-raw",
    )
    assert telemetry.execute(FakeModelProvider([output]), unregistered, 1) == output
    telemetry.finish("VALIDATION_FAILED", 1)
    call, summary = events(caplog)
    assert call["elapsed_ms"] == summary["elapsed_ms"] == 13
    assert call["provider"] == call["model"] == call["prompt_version"] == "UNREGISTERED"
    assert "CANARY" not in caplog.text


def test_fingerprints_are_keyed_and_scoped_to_one_rehearsal(caplog):
    first, second = RehearsalTelemetry(), RehearsalTelemetry()
    value = "CANARY-low-entropy-answer"
    assert first.fingerprint(value) == first.fingerprint(value)
    assert first.fingerprint(value) != second.fingerprint(value)
    assert first.fingerprint(value) != hashlib.sha256(value.encode()).hexdigest()
    output = candidate().model_copy(update={"raw_output": value})
    for index in [1, 2]:
        first.execute(FakeModelProvider([output]), task(), index)
    calls = events(caplog)
    assert calls[0]["input_fingerprint"] == calls[1]["input_fingerprint"]
    assert calls[0]["output_fingerprint"] == calls[1]["output_fingerprint"]
    assert "CANARY" not in caplog.text
    assert first._key.hex() not in caplog.text


@pytest.mark.parametrize("flagged,status", [(False, "LOW_CONFIDENCE"), (True, "FLAGGED")])
def test_fallback_and_flag_metadata_do_not_claim_validated_grades(context, caplog, flagged, status):
    output = ModelResult(
        status="LOW_CONFIDENCE", provider="fake", model="fixture-v1", flagged=flagged
    )
    run(FakeModelProvider([output]), context)
    call, outcome = events(caplog)
    assert call["status"] == status
    assert call["usage_source"] == "PROVIDER_REPORTED"
    assert call["output_fingerprint"] is None
    assert outcome["automatic_scoring_enabled"] is False


def test_telemetry_schema_stays_closed_and_matches_typed_events():
    schema = json.loads(Path("packages/analytics-schema/model-telemetry.schema.json").read_text())
    expected = TypeAdapter(ModelCallEvent | RehearsalEvent).json_schema()
    assert schema == expected | {"$schema": "https://json-schema.org/draft/2020-12/schema"}
    for name in ["ModelCallEvent", "RehearsalEvent"]:
        assert schema["$defs"][name]["additionalProperties"] is False
    with pytest.raises(ValidationError):
        RehearsalEvent(
            correlation_id=uuid4(),
            elapsed_ms=0,
            reason="AGREEMENT",
            requests=2,
            answer="CANARY-secret",
        )


def test_wrong_task_is_rejected_before_provider_dispatch(caplog):
    gateway = FakeModelProvider()
    wrong = task().model_copy(update={"task": "rephrase_explanation"})
    with pytest.raises(ValueError, match="Telemetry requires"):
        RehearsalTelemetry().execute(gateway, wrong, 1)
    assert not gateway.calls and not events(caplog)
