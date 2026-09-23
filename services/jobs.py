from typing import Protocol

from celery import Celery

from services.observability import correlation_id


class JobQueue(Protocol):
    def smoke(self, request_id: str) -> str: ...


class CeleryJobQueue:
    def __init__(self, app: Celery) -> None:
        self.app = app

    def smoke(self, request_id: str) -> str:
        result = self.app.send_task(
            "kasoma.smoke",
            headers={"kasoma_correlation_id": correlation_id(request_id)},
        )
        return str(result.id)


class FakeJobQueue:
    def __init__(self) -> None:
        self.requests: list[str] = []

    def smoke(self, request_id: str) -> str:
        self.requests.append(correlation_id(request_id))
        return f"fake-job-{len(self.requests)}"
