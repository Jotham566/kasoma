"""Closed synthetic gateway telemetry; content fingerprints use a disposable HMAC key."""

import hashlib
import hmac
import json
import math
import secrets
from collections.abc import Callable
from time import monotonic
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from services.observability import logger
from services.providers import ModelGateway, ModelResult, ModelTask

PromptVersion = Literal[
    "synthetic-short-text-criteria-first-v2",
    "synthetic-short-text-criteria-first-v2-repair",
    "synthetic-short-text-evidence-first-v2",
    "synthetic-short-text-evidence-first-v2-repair",
    "UNREGISTERED",
]
PROMPTS = {
    f"synthetic-short-text-{order}-v2{suffix}"
    for order in ("criteria-first", "evidence-first")
    for suffix in ("", "-repair")
}
RehearsalReason = Literal[
    "AGREEMENT",
    "FLAGGED",
    "INPUT_INVALID",
    "BUDGET",
    "PROVIDER_FAILURE",
    "PROVIDER_FALLBACK",
    "VALIDATION_FAILED",
    "DISAGREEMENT",
]


class TelemetryEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, hide_input_in_errors=True)
    schema_version: Literal[1] = 1
    correlation_id: UUID
    deployment: Literal["offline-synthetic-rehearsal"] = "offline-synthetic-rehearsal"
    elapsed_ms: int = Field(ge=0)


class ModelCallEvent(TelemetryEvent):
    event: Literal["model.call"] = "model.call"
    call_index: int = Field(ge=1, le=3)
    task: Literal["grade_short_answer"] = "grade_short_answer"
    prompt_version: PromptVersion
    provider: Literal["fake", "UNREGISTERED", "UNAVAILABLE"]
    model: Literal["fixture-v1", "UNREGISTERED", "UNAVAILABLE"]
    status: Literal["CANDIDATE", "LOW_CONFIDENCE", "FLAGGED", "FAILED"]
    input_tokens: int | None = Field(ge=0, le=8192)
    output_tokens: int | None = Field(ge=0, le=4096)
    usage_source: Literal["PROVIDER_REPORTED", "UNAVAILABLE"]
    input_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    output_fingerprint: str | None = Field(pattern=r"^[a-f0-9]{64}$")


class RehearsalEvent(TelemetryEvent):
    event: Literal["model.rehearsal"] = "model.rehearsal"
    reason: RehearsalReason
    requests: int = Field(ge=0, le=3)
    automatic_scoring_enabled: Literal[False] = False


class RehearsalTelemetry:
    def __init__(
        self, request_id: UUID | None = None, *, clock: Callable[[], float] = monotonic
    ) -> None:
        self.request_id = request_id or uuid4()
        self.clock = clock
        self.started = clock()
        # Not retained or logged. Fingerprints are comparable only inside this rehearsal.
        self._key = secrets.token_bytes(32)

    def fingerprint(self, value: str) -> str:
        return hmac.new(self._key, value.encode(), hashlib.sha256).hexdigest()

    def elapsed(self, start: float) -> int:
        return max(0, math.ceil((self.clock() - start) * 1000))

    @staticmethod
    def emit(event: TelemetryEvent) -> None:
        logger.info(event.model_dump_json())

    def execute(self, gateway: ModelGateway, task: ModelTask, index: int) -> ModelResult:
        if task.task != "grade_short_answer":
            raise ValueError("Telemetry requires a synthetic short-text task")
        started = self.clock()
        base = {
            "correlation_id": self.request_id,
            "call_index": index,
            "prompt_version": task.prompt_version
            if task.prompt_version in PROMPTS
            else "UNREGISTERED",
            "input_fingerprint": self.fingerprint(
                json.dumps(task.model_dump(mode="json"), sort_keys=True)
            ),
        }
        try:
            output = gateway.execute(task)
        except Exception:
            self.emit(
                ModelCallEvent.model_validate(
                    base
                    | {
                        "elapsed_ms": self.elapsed(started),
                        "provider": "UNAVAILABLE",
                        "model": "UNAVAILABLE",
                        "status": "FAILED",
                        "input_tokens": None,
                        "output_tokens": None,
                        "usage_source": "UNAVAILABLE",
                        "output_fingerprint": None,
                    }
                )
            )
            raise RuntimeError("Model call failed") from None
        self.emit(
            ModelCallEvent.model_validate(
                base
                | {
                    "elapsed_ms": self.elapsed(started),
                    "provider": "fake" if output.provider == "fake" else "UNREGISTERED",
                    "model": "fixture-v1"
                    if output.provider == "fake" and output.model == "fixture-v1"
                    else "UNREGISTERED",
                    "status": "FLAGGED" if output.flagged else output.status,
                    "input_tokens": output.input_tokens,
                    "output_tokens": output.output_tokens,
                    "usage_source": "PROVIDER_REPORTED",
                    "output_fingerprint": self.fingerprint(output.raw_output)
                    if output.raw_output is not None
                    else None,
                }
            )
        )
        return output

    def finish(self, reason: RehearsalReason, requests: int) -> None:
        self.emit(
            RehearsalEvent(
                correlation_id=self.request_id,
                elapsed_ms=self.elapsed(self.started),
                reason=reason,
                requests=requests,
            )
        )
