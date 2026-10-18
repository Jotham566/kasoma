"""Observe only actual provider-port attempts; never log task/result content."""

from services.model_metrics import observe
from services.providers import ModelGateway, ModelResult, ModelTask


def reported_usage(result: ModelResult) -> tuple[int | None, int | None]:
    if {"input_tokens", "output_tokens"} <= result.model_fields_set:
        return result.input_tokens, result.output_tokens
    return None, None


class ObservedModelGateway:
    def __init__(self, inner: ModelGateway):
        self.inner = inner

    def execute(self, task: ModelTask) -> ModelResult:
        try:
            result = self.inner.execute(task)
            if not isinstance(result, ModelResult):
                raise ValueError("Invalid provider result")
        except Exception:
            observe("UNAVAILABLE", None, None)
            raise RuntimeError("Model gateway unavailable") from None
        incoming, outgoing = reported_usage(result)
        observe(result.status, incoming, outgoing)
        return result
