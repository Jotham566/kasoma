"""Payload-free synthetic report comparison; never inference or approval (ADR-052)."""

import json
import os
import stat
from pathlib import Path
from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import AfterValidator, AwareDatetime, Field, model_validator

from services.short_text_validation import StrictContract


def payload_free_label(value: str) -> str:
    if "://" in value:
        raise ValueError("Labels cannot contain endpoint URLs")
    return value


Label = Annotated[
    str,
    Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:/+-]*$"),
    AfterValidator(payload_free_label),
]
Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Count = Annotated[int, Field(ge=0, le=1_000_000_000)]
Cases = Annotated[int, Field(ge=0, le=10_000)]
MAX_REPORT_BYTES = 512 * 1024


class BenchmarkReference(StrictContract):
    version: Label
    sha256: Digest
    cases: int = Field(ge=1, le=10_000)


class RuntimeProfile(StrictContract):
    alias: Literal["fake", "local-fast", "local-quality", "local-stretch", "gemini-free-eval"]
    hardware: Literal["synthetic-test", "apple-m4-mac-mini-16gb", "hosted"]
    model_digest: Digest | None = None
    license_sha256: Digest | None = None
    model_billions: int | None = Field(default=None, ge=4, le=12)
    quantization: Annotated[str, Field(pattern=r"^Q[45][A-Za-z0-9_]{0,15}$")] | None = None
    ollama_version: Label | None = None

    @model_validator(mode="after")
    def local_profile(self) -> "RuntimeProfile":
        local = self.alias.startswith("local-")
        if local:
            sizes = {"local-fast": {4}, "local-quality": {7, 8}, "local-stretch": {12}}
            if (
                self.hardware != "apple-m4-mac-mini-16gb"
                or self.model_digest is None
                or self.license_sha256 is None
                or self.model_billions not in sizes[self.alias]
                or self.quantization is None
                or self.ollama_version is None
            ):
                raise ValueError("Complete supported local profile required")
        elif self.hardware != (
            "hosted" if self.alias == "gemini-free-eval" else "synthetic-test"
        ) or any(
            value is not None
            for value in (
                self.model_digest,
                self.license_sha256,
                self.model_billions,
                self.quantization,
                self.ollama_version,
            )
        ):
            raise ValueError("Provider runtime profile mismatch")
        return self


class InferenceConfiguration(StrictContract):
    version: Label
    context_tokens: int = Field(ge=1024, le=8192)
    maximum_input_tokens: int = Field(ge=1, le=8192)
    maximum_output_tokens: int = Field(ge=1, le=4096)
    temperature: int = Field(ge=0, le=0)

    @model_validator(mode="after")
    def context_fits(self) -> "InferenceConfiguration":
        if self.maximum_input_tokens + self.maximum_output_tokens > self.context_tokens:
            raise ValueError("Input/output budget must fit context")
        return self


class Outcomes(StrictContract):
    scored: Cases
    low_confidence: Cases
    invalid_output: Cases
    provider_failure: Cases
    safety_fallback: Cases
    not_run: Cases
    exact: Cases
    within_tolerance: Cases
    critical_errors: Cases


class ReportUsage(StrictContract):
    requests: Count
    request_ceiling: int = Field(ge=1, le=30_000)
    input_tokens: Count | None
    output_tokens: Count | None
    input_token_ceiling: int = Field(ge=1, le=1_000_000_000)
    output_token_ceiling: int = Field(ge=1, le=1_000_000_000)
    cost_usd: int | None = Field(ge=0, le=0)
    rate_limit_responses: Count
    observed_requests_per_minute: Count | None
    observed_tokens_per_minute: Count | None


class Latency(StrictContract):
    sample_count: Cases
    p50_ms: int | None = Field(ge=0, le=1_000_000)
    p95_ms: int | None = Field(ge=0, le=1_000_000)
    maximum_ms: int | None = Field(ge=0, le=1_000_000)

    @model_validator(mode="after")
    def ordered(self) -> "Latency":
        values = (self.p50_ms, self.p95_ms, self.maximum_ms)
        if self.sample_count == 0:
            if any(value is not None for value in values):
                raise ValueError("Unmeasured latency must be unavailable")
        elif (
            self.p50_ms is None
            or self.p95_ms is None
            or self.maximum_ms is None
            or not self.p50_ms <= self.p95_ms <= self.maximum_ms
        ):
            raise ValueError("Measured ordered latency required")
        return self


class EvaluationReport(StrictContract):
    version: Literal["kasoma-evaluation-report-v1"]
    classification: Literal["synthetic"]
    report_id: UUID
    benchmark: BenchmarkReference
    task: Literal["grade_short_answer"]
    response_schema_version: Label
    metric_policy: Literal["short-text-comparison-v1"]
    provider: Literal["fake", "ollama", "gemini-free-eval"]
    model_identifier: Label = Field(repr=False)
    provider_terms_sha256: Digest | None
    adapter_version: Label
    prompt_version: Label
    runtime: RuntimeProfile
    configuration: InferenceConfiguration
    started_at: AwareDatetime
    finished_at: AwareDatetime
    sanitizer: Literal["SYNTHETIC_PAYLOAD_FREE"]
    outcomes: Outcomes
    usage: ReportUsage
    latency: Latency

    @model_validator(mode="after")
    def coherent(self) -> "EvaluationReport":
        outcomes, usage, cases = self.outcomes, self.usage, self.benchmark.cases
        expected_provider = (
            "ollama" if self.runtime.alias.startswith("local-") else self.runtime.alias
        )
        hosted = self.provider == "gemini-free-eval"
        if (
            (self.provider == "fake") != (self.provider_terms_sha256 is None)
            or usage.rate_limit_responses > usage.requests
            or (
                hosted
                and (not usage.observed_requests_per_minute or not usage.observed_tokens_per_minute)
            )
            or (
                not hosted
                and (
                    usage.observed_requests_per_minute is not None
                    or usage.observed_tokens_per_minute is not None
                )
            )
        ):
            raise ValueError("Declared terms/quota evidence required")
        total = sum(
            (
                outcomes.scored,
                outcomes.low_confidence,
                outcomes.invalid_output,
                outcomes.provider_failure,
                outcomes.safety_fallback,
                outcomes.not_run,
            )
        )
        if (
            self.provider != expected_provider
            or self.finished_at < self.started_at
            or total != cases
            or not outcomes.exact <= outcomes.within_tolerance <= outcomes.scored
            or outcomes.critical_errors > cases - outcomes.not_run
            or self.latency.sample_count > cases - outcomes.not_run
            or not 2 * outcomes.scored <= usage.requests <= usage.request_ceiling <= 3 * cases
            or (usage.input_tokens is not None and usage.input_tokens > usage.input_token_ceiling)
            or (
                usage.output_tokens is not None and usage.output_tokens > usage.output_token_ceiling
            )
        ):
            raise ValueError("Incoherent evaluation evidence")
        return self


def summary(report: EvaluationReport) -> dict[str, Any]:
    cases, outcomes = report.benchmark.cases, report.outcomes
    return {
        "cases": cases,
        "outcomes": outcomes.model_dump(),
        "exact_all_cases": round(outcomes.exact / cases, 6),
        "within_tolerance_all_cases": round(outcomes.within_tolerance / cases, 6),
        "complete": outcomes.not_run == 0,
        "latency": report.latency.model_dump(),
        "usage": report.usage.model_dump(),
    }


def compare(baseline: EvaluationReport, candidate: EvaluationReport) -> dict[str, Any]:
    if (
        baseline.benchmark != candidate.benchmark
        or baseline.task != candidate.task
        or baseline.response_schema_version != candidate.response_schema_version
        or baseline.metric_policy != candidate.metric_policy
    ):
        raise ValueError("INCOMPARABLE_REPORTS")
    changed = [
        field
        for field in (
            "provider",
            "provider_terms_sha256",
            "model_identifier",
            "adapter_version",
            "prompt_version",
            "runtime",
            "configuration",
        )
        if getattr(baseline, field) != getattr(candidate, field)
    ]
    return {
        "version": "kasoma-evaluation-comparison-v1",
        "baseline_report_id": str(baseline.report_id),
        "candidate_report_id": str(candidate.report_id),
        "changed_fields": changed,
        "baseline": summary(baseline),
        "candidate": summary(candidate),
        "academic_approval_established": False,
        "automatic_scoring_enabled": False,
    }


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate report key")
        result[key] = value
    return result


def read_report(path: Path) -> EvaluationReport:
    # Nonblocking open prevents a swapped FIFO from hanging before fstat. Reject
    # final symlinks and nonregular files, and read only the explicit byte ceiling.
    descriptor = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
    with os.fdopen(descriptor, "rb") as source:
        if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
            raise ValueError("Regular local report required")
        content = source.read(MAX_REPORT_BYTES + 1)
    if len(content) > MAX_REPORT_BYTES:
        raise ValueError("Report size exceeded")
    parsed = json.loads(content, object_pairs_hook=unique_object)
    # JSON-mode validates UUID/datetime strings without enabling general coercion.
    return EvaluationReport.model_validate_json(json.dumps(parsed, allow_nan=False))
