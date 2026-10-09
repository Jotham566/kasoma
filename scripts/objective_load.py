"""Isolated synthetic loopback HTTP load; never targets a supplied application URL."""

import asyncio
import json
import math
import os
import re
import resource
import socket
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from threading import Thread
from time import monotonic, process_time, sleep
from typing import Any
from uuid import uuid4

import httpx
import uvicorn
from pydantic import SecretStr
from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import Session

from apps.api.main import create_app
from scripts.assessment_fixtures import seed_assessment
from scripts.recovery_drill import local_database_url
from services.assessment import AssessmentService
from services.config import Settings
from services.database import engine_for
from services.domain.assessment import AssessmentSession, Attempt, Grade
from services.domain.content import ItemVersion
from services.identity import IdentityService
from services.identity_contracts import ConsentInput, OTPRequest, OTPVerify, ProfilePatch
from services.providers import FakeMessagingProvider
from services.seed import seed

REGISTERED = 2000
ACTIVE = 500
CONCURRENT = 50
ANSWERS_PER_SECOND = 20
OPERATIONS = frozenset({"PROFILE", "START", "NEXT", "ANSWER", "STATE", "PROGRESS"})


def database_name(value: str) -> str:
    if not re.fullmatch(r"kasoma_load_[0-9a-f]{32}", value):
        raise ValueError("Only a generated load database is allowed")
    return value


def percentiles(values: list[float]) -> dict[str, float | int | None]:
    ordered = sorted(values)
    return {"samples": len(ordered)} | {
        f"p{p}_ms": round(ordered[math.ceil(len(ordered) * p / 100) - 1], 3) if ordered else None
        for p in (50, 95, 99)
    }


@dataclass
class Measurements:
    timings: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))
    errors: int = 0
    inflight: int = 0
    peak_inflight: int = 0
    completed: int = 0
    dispatch_lag_ms: list[float] = field(default_factory=list)
    answer_dispatches: list[float] = field(default_factory=list)

    async def request(
        self,
        client: httpx.AsyncClient,
        operation: str,
        method: str,
        path: str,
        token: str,
        body: dict[str, object] | None = None,
    ) -> dict[str, Any]:
        if operation not in OPERATIONS:
            raise ValueError("Unregistered measurement")
        started = monotonic()
        self.inflight += 1
        self.peak_inflight = max(self.peak_inflight, self.inflight)
        try:
            response = await client.request(
                method,
                path,
                headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid4())},
                json=body,
            )
            response.raise_for_status()
            result = response.json()
            if not isinstance(result, dict):
                raise ValueError("Unexpected response shape")
            return result
        except (httpx.HTTPError, ValueError):
            self.errors += 1
            raise RuntimeError("Synthetic request failed") from None
        finally:
            self.timings[operation].append((monotonic() - started) * 1000)
            self.inflight -= 1

    def report(self) -> dict[str, object]:
        return {
            "operations": {
                key: percentiles(values) for key, values in sorted(self.timings.items())
            },
            "all_http": percentiles([v for values in self.timings.values() for v in values]),
            "errors": self.errors,
            "completed_learners": self.completed,
            "peak_inflight_http": self.peak_inflight,
            "answer_dispatch_lag": percentiles(self.dispatch_lag_ms),
            "observed_answer_dispatch_per_second": round(
                (len(self.answer_dispatches) - 1)
                / (self.answer_dispatches[-1] - self.answer_dispatches[0]),
                3,
            )
            if len(self.answer_dispatches) > 1
            and self.answer_dispatches[-1] > self.answer_dispatches[0]
            else None,
        }


class AnswerPacer:
    def __init__(self) -> None:
        self.next_at = 0.0
        self.lock = asyncio.Lock()

    async def wait(self) -> float:
        async with self.lock:
            at = max(monotonic(), self.next_at)
            await asyncio.sleep(max(0, at - monotonic()))
            dispatched = monotonic()
            period = 1 / ANSWERS_PER_SECOND
            # Keep the target cadence across ordinary timer jitter, but skip a missed
            # interval rather than releasing accumulated work as a catch-up burst.
            self.next_at = (dispatched if dispatched - at >= period else at) + period
            return max(0, (dispatched - at) * 1000)


def latency_passes(measured: Measurements) -> bool:
    # A fast, frequent read must not mask a slow session-start or submission route.
    for operation in OPERATIONS:
        p95 = percentiles(measured.timings.get(operation, []))["p95_ms"]
        if p95 is None or p95 >= 500:
            return False
    return True


def populate(identity: IdentityService) -> tuple[list[str], dict[str, object]]:
    seed(identity.settings)
    # 288 reviewed original fixtures, spanning all six configured topic clusters.
    seed_assessment(identity, reassessment=True)
    subject = next(value.id for value in identity.subjects() if value.name == "Mathematics")
    tokens = []
    for index in range(REGISTERED):
        challenge = identity.request_otp(
            OTPRequest(identifier=f"load-{index}@example.invalid", device_id=uuid4()),
            f"synthetic-load-{index}",
            None,
        )
        token = identity.verify(
            OTPVerify(challenge_id=challenge.challenge_id, code="246810"), None, str(uuid4())
        ).access_token
        if index < ACTIVE:
            identity.update_profile(
                token,
                ProfilePatch(
                    display_name="Synthetic load learner",
                    birth_date=date(2000, 1, 1),
                    subject_ids=[subject],
                ),
                str(uuid4()),
            )
            identity.consent(
                token,
                ConsentInput(
                    consent_type="SELF",
                    policy_version=identity.settings.consent_policy_version,
                    affirmative=True,
                ),
                uuid4(),
                str(uuid4()),
            )
            tokens.append(token)
    topic = AssessmentService(identity).topics(tokens[0], subject)[0].id
    return tokens, {"subject_id": str(subject), "topic_id": str(topic), "mode": "TOPIC"}


async def exercise(
    port: int, tokens: list[str], plan: dict[str, object], measured: Measurements
) -> None:
    slots, pacer = asyncio.Semaphore(CONCURRENT), AnswerPacer()
    async with httpx.AsyncClient(
        base_url=f"http://127.0.0.1:{port}",
        trust_env=False,
        timeout=10,
        limits=httpx.Limits(max_connections=CONCURRENT, max_keepalive_connections=CONCURRENT),
    ) as client:

        async def learner(token: str) -> None:
            async with slots:
                try:
                    await measured.request(client, "PROFILE", "GET", "/api/v1/me", token)
                    state = await measured.request(
                        client, "START", "POST", "/api/v1/revision-sessions", token, plan
                    )
                    session = str(state["id"])
                    for _ in range(5):
                        item = await measured.request(
                            client, "NEXT", "GET", f"/api/v1/sessions/{session}/next-item", token
                        )
                        measured.dispatch_lag_ms.append(await pacer.wait())
                        measured.answer_dispatches.append(monotonic())
                        grade = await measured.request(
                            client,
                            "ANSWER",
                            "POST",
                            f"/api/v1/sessions/{session}/attempts",
                            token,
                            {
                                "session_item_id": item["session_item_id"],
                                "response": {"type": "SINGLE_CHOICE", "choice_id": "A"},
                            },
                        )
                        if grade["score"] != 1 or grade["mastery_update_status"] != "COMPLETED":
                            measured.errors += 1
                            return
                    state = await measured.request(
                        client, "STATE", "GET", f"/api/v1/sessions/{session}", token
                    )
                    await measured.request(
                        client,
                        "PROGRESS",
                        "GET",
                        f"/api/v1/me/progress?subject_id={plan['subject_id']}",
                        token,
                    )
                    if state["status"] == "COMPLETED" and state["answered_count"] == 5:
                        measured.completed += 1
                    else:
                        measured.errors += 1
                except RuntimeError:
                    return
                except (KeyError, TypeError):
                    measured.errors += 1

        async with asyncio.timeout(300):
            await asyncio.gather(*(learner(token) for token in tokens))


def run(settings: Settings) -> dict[str, object]:
    url = local_database_url(settings)
    name = database_name("kasoma_load_" + uuid4().hex)
    admin = create_engine(
        url.set(database="postgres"), isolation_level="AUTOCOMMIT", hide_parameters=True
    )
    created = False
    engine = None
    server = None
    thread = None
    listener = None
    measured: Measurements | None = None
    result: dict[str, object] = {"status": "FAILED", "profile": "isolated-objective-http-v1"}
    stage = "CREATE_DATABASE"
    try:
        with admin.connect() as db:
            db.execute(text(f'CREATE DATABASE "{name}"'))
            created = True
        local_url = url.set(database=name).render_as_string(hide_password=False)
        stage = "MIGRATE"
        subprocess.run(
            ["make", "migrate"],
            env=os.environ | {"DATABASE_URL": local_url},
            check=True,
            capture_output=True,
            timeout=120,
        )
        config = Settings(
            **(
                settings.model_dump()
                | {
                    "database_url": SecretStr(local_url),
                    "model_provider": "fake",
                    "email_provider": "fake",
                    "sms_provider": "fake",
                    "allow_external_api_calls": False,
                }
            )
        )
        engine = engine_for(config)
        fake = FakeMessagingProvider()
        identity = IdentityService(engine, config, fake, fake, code=lambda: "246810")
        stage = "SYNTHETIC_FIXTURES"
        tokens, plan = populate(identity)
        with Session(engine) as db:
            item_count = db.scalar(select(func.count()).select_from(ItemVersion)) or 0
        if not 250 <= item_count <= 400:
            raise RuntimeError("Fixture inventory is outside the specified range")
        stage = "START_LOOPBACK_HTTP"
        listener = socket.socket()
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
        server = uvicorn.Server(
            uvicorn.Config(create_app(config, identity), access_log=False, log_level="warning")
        )
        thread = Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
        thread.start()
        deadline = monotonic() + 15
        while not server.started and thread.is_alive() and monotonic() < deadline:
            sleep(0.05)
        if not server.started:
            raise RuntimeError("Isolated server failed to start")
        stage = "HTTP_PROFILE"
        measured = Measurements()
        started, cpu = monotonic(), process_time()
        asyncio.run(exercise(port, tokens, plan, measured))
        duration, cpu_seconds = monotonic() - started, process_time() - cpu
        with Session(engine) as db:
            attempts = db.scalar(select(func.count()).select_from(Attempt)) or 0
            grades = db.scalar(select(func.count()).select_from(Grade)) or 0
            completed = (
                db.scalar(
                    select(func.count())
                    .select_from(AssessmentSession)
                    .where(AssessmentSession.status == "COMPLETED")
                )
                or 0
            )
        all_values = [v for values in measured.timings.values() for v in values]
        non_ai_p95 = percentiles(all_values)["p95_ms"]
        answer_p95 = percentiles(measured.timings["ANSWER"])["p95_ms"]
        passed = (
            measured.errors == 0
            and measured.completed == ACTIVE
            and completed == ACTIVE
            and attempts == grades == ACTIVE * 5
            and measured.peak_inflight == CONCURRENT
            and non_ai_p95 is not None
            and non_ai_p95 < 500
            and answer_p95 is not None
            and answer_p95 < 1500
            and latency_passes(measured)
        )
        result.update(
            {
                "status": "PASSED" if passed else "FAILED",
                "registered_learners": REGISTERED,
                "active_learners": ACTIVE,
                "concurrency_limit": CONCURRENT,
                "reviewed_synthetic_items": item_count,
                "target_answer_dispatch_per_second": ANSWERS_PER_SECOND,
                "duration_seconds": round(duration, 3),
                "attempts": attempts,
                "grades": grades,
                "completed_sessions": completed,
                "cpu_seconds_client_and_api": round(cpu_seconds, 3),
                "peak_rss_bytes_client_api_and_fixture_setup": resource.getrusage(
                    resource.RUSAGE_SELF
                ).ru_maxrss
                * (1 if sys.platform == "darwin" else 1024),
                "database_resources_measured": False,
                "production_acceptance": False,
                **measured.report(),
            }
        )
    except Exception:
        result.update({"status": "FAILED", "failed_stage": stage})
        if measured is not None:
            result.update(measured.report())
    finally:
        if server:
            server.should_exit = True
        if thread:
            thread.join(timeout=15)
        if listener:
            listener.close()
        if engine:
            engine.dispose()
        result["cleanup_failed"] = False
        if created:
            try:
                if thread and thread.is_alive():
                    raise RuntimeError("Isolated server is still active")
                with admin.connect() as db:
                    db.execute(text(f'DROP DATABASE "{database_name(name)}"'))
            except Exception:
                result.update({"cleanup_failed": True, "status": "FAILED"})
        admin.dispose()
    return result


if __name__ == "__main__":
    report = run(Settings())
    print(json.dumps(report, sort_keys=True))
    raise SystemExit(0 if report["status"] == "PASSED" else 1)
