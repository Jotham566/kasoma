"""Offline report evidence is synthetic and cannot establish academic approval."""

import json
import os
from copy import deepcopy
from uuid import uuid4

import pytest
from pydantic import ValidationError

from scripts.compare_evaluations import main
from services.evaluation_reports import MAX_REPORT_BYTES, EvaluationReport, compare, read_report


def document():
    return {
        "version": "kasoma-evaluation-report-v1",
        "classification": "synthetic",
        "report_id": str(uuid4()),
        "benchmark": {"version": "original-synthetic-v1", "sha256": "a" * 64, "cases": 10},
        "task": "grade_short_answer",
        "response_schema_version": "synthetic-rubric-v1",
        "metric_policy": "short-text-comparison-v1",
        "provider": "fake",
        "provider_terms_sha256": None,
        "model_identifier": "fixture-v1",
        "adapter_version": "foundation-1",
        "prompt_version": "synthetic-criteria-first-v2",
        "runtime": {"alias": "fake", "hardware": "synthetic-test"},
        "configuration": {
            "version": "fixture-v1",
            "context_tokens": 8192,
            "maximum_input_tokens": 4096,
            "maximum_output_tokens": 1024,
            "temperature": 0,
        },
        "started_at": "2026-10-18T10:00:00Z",
        "finished_at": "2026-10-18T10:01:00Z",
        "sanitizer": "SYNTHETIC_PAYLOAD_FREE",
        "outcomes": {
            "scored": 8,
            "low_confidence": 1,
            "invalid_output": 0,
            "provider_failure": 1,
            "safety_fallback": 0,
            "not_run": 0,
            "exact": 7,
            "within_tolerance": 8,
            "critical_errors": 0,
        },
        "usage": {
            "requests": 18,
            "request_ceiling": 30,
            "input_tokens": 1000,
            "output_tokens": 1000,
            "input_token_ceiling": 10000,
            "output_token_ceiling": 10000,
            "cost_usd": 0,
            "rate_limit_responses": 0,
            "observed_requests_per_minute": None,
            "observed_tokens_per_minute": None,
        },
        "latency": {"sample_count": 10, "p50_ms": 100, "p95_ms": 200, "maximum_ms": 300},
    }


def report(body=None):
    return EvaluationReport.model_validate_json(json.dumps(document() if body is None else body))


def test_complete_denominator_retains_fallbacks_and_comparison_never_approves():
    baseline = report()
    other = baseline.model_dump(mode="json")
    other["prompt_version"] = "synthetic-next-v3"
    other["model_identifier"] = "fixture-v2"
    result = compare(baseline, report(other))
    assert result["baseline"]["within_tolerance_all_cases"] == 0.8
    assert result["baseline"]["exact_all_cases"] == 0.7
    assert result["changed_fields"] == ["model_identifier", "prompt_version"]
    assert result["academic_approval_established"] is result["automatic_scoring_enabled"] is False
    encoded = json.dumps(result)
    assert "fixture-v2" not in encoded and "synthetic-next-v3" not in encoded
    assert compare(baseline, baseline)["changed_fields"] == []


@pytest.mark.parametrize("field,value", [("sha256", "b" * 64), ("version", "other-v1")])
def test_mismatched_frozen_evidence_is_not_comparable(field, value):
    first = report()
    second = first.model_dump(mode="json")
    second["benchmark"][field] = value
    with pytest.raises(ValueError, match="INCOMPARABLE_REPORTS"):
        compare(first, report(second))


def test_changed_output_schema_is_not_silently_compared():
    first = report()
    second = first.model_dump(mode="json") | {"response_schema_version": "other-v2"}
    with pytest.raises(ValueError, match="INCOMPARABLE_REPORTS"):
        compare(first, report(second))


def test_all_fallback_and_unrun_cases_have_no_correct_numerator_or_fake_usage():
    body = document()
    body["outcomes"] |= {
        "scored": 0,
        "low_confidence": 9,
        "provider_failure": 0,
        "not_run": 1,
        "exact": 0,
        "within_tolerance": 0,
    }
    body["usage"] |= {"requests": 0, "input_tokens": None, "output_tokens": None, "cost_usd": None}
    body["latency"] = {"sample_count": 0, "p50_ms": None, "p95_ms": None, "maximum_ms": None}
    result = compare(report(body), report(body))["candidate"]
    assert result["exact_all_cases"] == result["within_tolerance_all_cases"] == 0
    assert not result["complete"] and result["usage"]["input_tokens"] is None
    assert result["latency"]["p95_ms"] is None


@pytest.mark.parametrize(
    "path,value",
    [
        (("classification",), "real"),
        (("learner_email",), "canary@example.invalid"),
        (("raw_output",), "PRIVATE_RESPONSE_CANARY"),
        (("prompt_version",), "https://cloud.invalid"),
        (("outcomes", "exact"), 9),
        (("outcomes", "scored"), 9),
        (("outcomes", "critical_errors"), 11),
        (("outcomes", "exact"), True),
        (("outcomes", "exact"), "7"),
        (("usage", "requests"), 15),
        (("usage", "request_ceiling"), 31),
        (("usage", "input_tokens"), 10001),
        (("usage", "cost_usd"), 1),
        (("usage", "rate_limit_responses"), 19),
        (("usage", "observed_requests_per_minute"), 10),
        (("runtime", "license_sha256"), "e" * 64),
        (("latency", "p95_ms"), 301),
        (("latency", "sample_count"), 11),
        (("latency", "p50_ms"), None),
        (("configuration", "temperature"), True),
        (("configuration", "context_tokens"), 1024),
        (("finished_at",), "2026-10-17T10:00:00Z"),
        (("started_at",), "2026-10-18T10:00:00"),
    ],
)
def test_invalid_private_or_incoherent_report_is_rejected(path, value):
    body = document()
    target = body
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(ValidationError):
        report(body)


def test_supported_local_and_hosted_profiles_compare_without_model_calls():
    body = document() | {
        "provider": "ollama",
        "model_identifier": "synthetic-local-model",
        "provider_terms_sha256": "c" * 64,
    }
    body["runtime"] = {
        "alias": "local-quality",
        "hardware": "apple-m4-mac-mini-16gb",
        "model_digest": "b" * 64,
        "license_sha256": "d" * 64,
        "model_billions": 8,
        "quantization": "Q4_K_M",
        "ollama_version": "synthetic-v1",
    }
    local = report(body)
    external = deepcopy(body) | {"provider": "gemini-free-eval"}
    external["runtime"] = {"alias": "gemini-free-eval", "hardware": "hosted"}
    external["usage"] |= {"observed_requests_per_minute": 10, "observed_tokens_per_minute": 10000}
    result = compare(local, report(external))
    assert result["changed_fields"] == ["provider", "runtime"]
    for field in (
        "model_digest",
        "license_sha256",
        "model_billions",
        "quantization",
        "ollama_version",
    ):
        broken = deepcopy(body)
        broken["runtime"].pop(field)
        with pytest.raises(ValidationError):
            report(broken)


@pytest.mark.parametrize(
    "payload",
    [
        b"{}",
        b"\xff",
        b'{"version":1,"version":2}',
        b'{"unknown":NaN}',
        b"[" * 2000,
        b" " * (MAX_REPORT_BYTES + 1),
    ],
)
def test_bounded_reader_rejects_malformed_ambiguous_or_oversized_files(tmp_path, payload):
    source = tmp_path / "report.json"
    source.write_bytes(payload)
    with pytest.raises((ValueError, RecursionError)):
        read_report(source)


def test_reader_rejects_symlink_directory_and_fifo_without_blocking(tmp_path):
    source = tmp_path / "report.json"
    source.write_text(json.dumps(document()))
    link = tmp_path / "link.json"
    link.symlink_to(source)
    fifo = tmp_path / "fifo"
    os.mkfifo(fifo)
    for target in (link, fifo, tmp_path):
        with pytest.raises((OSError, ValueError)):
            read_report(target)


def test_cli_actual_reader_is_deterministic_and_errors_do_not_echo_inputs(
    tmp_path, monkeypatch, capsys
):
    source = tmp_path / "report.json"
    source.write_text(json.dumps(document()))
    for name in ("KASOMA_EVAL_BASELINE", "KASOMA_EVAL_CANDIDATE"):
        monkeypatch.setenv(name, str(source))
    assert main() == 0
    first = capsys.readouterr().out
    assert main() == 0 and capsys.readouterr().out == first
    source.write_text('{"raw_output":"PRIVATE_RESPONSE_CANARY@example.invalid"}')
    assert main() == 1
    error = capsys.readouterr().out
    assert json.loads(error)["code"] == "REPORT_COMPARISON_REJECTED"
    assert str(tmp_path) not in error and "CANARY" not in error
    monkeypatch.delenv("KASOMA_EVAL_BASELINE")
    assert main() == 1
    assert json.loads(capsys.readouterr().out)["code"] == "REPORT_PATHS_REQUIRED"
