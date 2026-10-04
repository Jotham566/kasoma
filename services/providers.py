"""Provider boundaries for the foundation; no learner grading is enabled."""

import smtplib
from collections.abc import Sequence
from email.message import EmailMessage
from typing import Literal, Protocol
from urllib.parse import urlsplit
from uuid import UUID

import httpx
from minio import Minio
from pydantic import BaseModel, ConfigDict, Field, JsonValue
from urllib3 import PoolManager, Timeout

from services.config import Settings, require_local


class ModelTask(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    task: Literal[
        "grade_short_answer",
        "rephrase_explanation",
        "extract_content_candidate",
        "embed_approved_content",
    ]
    schema_version: Literal[1] = 1
    classification: Literal["synthetic"] = "synthetic"
    prompt_version: str = Field(min_length=1, max_length=80)
    text: str = Field(max_length=2000, repr=False)
    context_references: list[UUID] = Field(default_factory=list, max_length=20)
    structured_input: dict[str, JsonValue] = Field(default_factory=dict, repr=False)
    response_schema: dict[str, JsonValue] = Field(default_factory=dict, repr=False)
    timeout_ms: int = Field(default=1000, ge=1, le=30000, strict=True)
    max_input_tokens: int = Field(default=4096, ge=1, le=8192, strict=True)
    max_output_tokens: int = Field(default=1024, ge=1, le=4096, strict=True)
    max_cost_usd: Literal[0] = 0


class ModelResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["LOW_CONFIDENCE", "CANDIDATE"]
    provider: str
    model: str
    schema_version: Literal[1] = 1
    adapter_version: Literal["foundation-1"] = "foundation-1"
    raw_output: str | None = Field(default=None, max_length=16384, repr=False)
    input_tokens: int = Field(default=0, ge=0, le=8192, strict=True)
    output_tokens: int = Field(default=0, ge=0, le=4096, strict=True)
    flagged: bool = Field(default=False, strict=True)


class ModelGateway(Protocol):
    def execute(self, task: ModelTask) -> ModelResult: ...


class FakeModelProvider:
    def __init__(self, fixtures: Sequence[ModelResult | Exception] = ()) -> None:
        self._fixtures = list(fixtures)
        self.calls: list[ModelTask] = []

    def execute(self, task: ModelTask) -> ModelResult:
        self.calls.append(task.model_copy(deep=True))
        if self._fixtures:
            fixture = self._fixtures.pop(0)
            if isinstance(fixture, Exception):
                raise fixture
            return fixture.model_copy(deep=True)
        return ModelResult(status="LOW_CONFIDENCE", provider="fake", model="fixture-v1")


class OllamaConnectivity:
    """Manual connectivity probe only; grading/evaluation awaits approved benchmarks."""

    def __init__(self, endpoint: str) -> None:
        self.endpoint = require_local(endpoint).rstrip("/")

    def available(self) -> bool:
        with httpx.Client(timeout=5, trust_env=False, follow_redirects=False) as client:
            response = client.get(f"{self.endpoint}/models")
            return response.status_code == 200


class MessagingProvider(Protocol):
    def send(self, recipient: str, body: str) -> str: ...


class FakeMessagingProvider:
    """Captures only synthetic in-memory test messages. Never logs bodies."""

    def __init__(self) -> None:
        self.messages: list[tuple[str, str]] = []

    def send(self, recipient: str, body: str) -> str:
        self.messages.append((recipient, body))
        return f"fake-message-{len(self.messages)}"


class MailpitEmailProvider:
    def __init__(self, settings: Settings) -> None:
        self.host = settings.mailpit_host
        self.port = settings.mailpit_port

    def send(self, recipient: str, body: str) -> str:
        message = EmailMessage()
        message["From"] = "kasoma@example.invalid"
        message["To"] = recipient
        message["Subject"] = "Kasoma local message"
        message.set_content(body)
        with smtplib.SMTP(self.host, self.port, timeout=5) as client:
            client.send_message(message)
        return "mailpit-captured"


class ObjectStorage(Protocol):
    def ensure_container(self) -> None: ...


class MinioObjectStorage:
    def __init__(self, settings: Settings) -> None:
        endpoint = urlsplit(settings.object_storage_endpoint)
        self.client = Minio(
            endpoint.netloc,
            access_key=settings.object_storage_access_key.get_secret_value(),
            secret_key=settings.object_storage_secret_key.get_secret_value(),
            secure=endpoint.scheme == "https",
            http_client=PoolManager(timeout=Timeout(connect=2, read=5), retries=0),
        )
        self.container = settings.object_storage_container

    def ensure_container(self) -> None:
        if not self.client.bucket_exists(self.container):
            self.client.make_bucket(self.container)
