"""Provider boundaries for the foundation; no learner grading is enabled."""

import smtplib
from email.message import EmailMessage
from typing import Literal, Protocol
from urllib.parse import urlsplit

import httpx
from minio import Minio
from pydantic import BaseModel, ConfigDict
from urllib3 import PoolManager, Timeout

from services.config import Settings, require_local


class ModelTask(BaseModel):
    model_config = ConfigDict(extra="forbid")
    task: Literal[
        "grade_short_answer",
        "rephrase_explanation",
        "extract_content_candidate",
        "embed_approved_content",
    ]
    schema_version: Literal[1] = 1
    classification: Literal["synthetic"] = "synthetic"
    prompt_version: str
    text: str


class ModelResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["LOW_CONFIDENCE", "CANDIDATE"]
    provider: str
    model: str
    schema_version: Literal[1] = 1
    adapter_version: Literal["foundation-1"] = "foundation-1"


class ModelGateway(Protocol):
    def execute(self, task: ModelTask) -> ModelResult: ...


class FakeModelProvider:
    def execute(self, task: ModelTask) -> ModelResult:
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
