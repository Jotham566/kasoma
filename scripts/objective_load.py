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
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import date
from threading import Thread
from time import monotonic, process_time, sleep
from typing import Any
from uuid import uuid4

import httpx
import uvicorn
from pydantic import SecretStr
from sqlalchemy import Engine, create_engine, func, select, text
from sqlalchemy.orm import Session

from apps.api.main import create_app
from scripts.assessment_fixtures import seed_assessment
from scripts.recovery_drill import local_database_url
from services.assessment import AssessmentService
from services.assessment_contracts import GradeView, StartRevision, SubmitAnswer
from services.config import Settings
from services.database import engine_for
from services.domain.assessment import AssessmentSession, Attempt, Grade
from services.domain.content import ItemVersion
from services.export_retirement_install import owner_name
from services.identity import IdentityError, IdentityService
from services.identity_contracts import (
    ConsentInput,
    Credentials,
    OTPRequest,
    OTPVerify,
    ProfilePatch,
)
from services.providers import FakeMessagingProvider
from services.seed import seed

REGISTERED = 2000
ACTIVE = 500
CONCURRENT = 50
ANSWERS_PER_SECOND = 20
OPERATIONS = frozenset({"PROFILE", "START", "NEXT", "ANSWER", "STATE", "PROGRESS"})
HISTORY_SESSIONS = 10
OBJECTIVE_FORMATS = frozenset({"SINGLE_CHOICE", "NUMERIC"})


def database_name(value: str) -> str:
    if not re.fullmatch(r"kasoma_load_[0-9a-f]{32}", value):
        raise ValueError("Only a generated load database is allowed")
    return value


def cleanup_owner(admin: Engine, name: str) -> None:
    """Inspect only the owner derived from this invocation's dropped database."""
    role = owner_name(database_name(name), "public")
    with admin.connect() as db:
        safe = db.scalar(
            text("""
              SELECT NOT (r.rolcanlogin OR r.rolsuper OR r.rolcreatedb OR r.rolcreaterole
                OR r.rolinherit OR r.rolreplication OR r.rolbypassrls OR EXISTS(
                  SELECT 1 FROM pg_catalog.pg_auth_members m
                  WHERE m.roleid=r.oid OR m.member=r.oid))
              FROM pg_catalog.pg_roles r WHERE r.rolname=:role
            """),
            {"role": role},
        )
        if safe is None:
            return
        if safe is not True:
            raise RuntimeError("Isolated owner cleanup refused")
        # Restrictive DROP preserves PostgreSQL's cross-database dependency checks.
        db.execute(text(f'DROP ROLE "{role}"'))


def percentiles(values: list[float]) -> dict[str, float | int | None]:
    ordered = sorted(values)
    return {"samples": len(ordered)} | {
        f"p{p}_ms": round(ordered[math.ceil(len(ordered) * p / 100) - 1], 3) if ordered else None
        for p in (50, 95, 99)
    }


@dataclass
class Measurements:
    timings: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))
    answer_formats: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))
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
            elapsed = (monotonic() - started) * 1000
            self.timings[operation].append(elapsed)
            response_body = body.get("response") if body else None
            if operation == "ANSWER" and isinstance(response_body, dict):
                kind = response_body.get("type")
                if isinstance(kind, str) and kind in OBJECTIVE_FORMATS:
                    self.answer_formats[kind].append(elapsed)
            self.inflight -= 1

    def report(self) -> dict[str, object]:
        return {
            "operations": {
                key: percentiles(values) for key, values in sorted(self.timings.items())
            },
            "answer_formats": {
                key: percentiles(values) for key, values in sorted(self.answer_formats.items())
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
    for values in measured.answer_formats.values():
        p95 = percentiles(values)["p95_ms"]
        if p95 is None or p95 >= 500:
            return False
    return True


def fixture_response(kind: str, correct: bool = True) -> dict[str, str]:
    """Answers only for this runner's original fixtures, never infer a real answer key."""
    if kind == "SINGLE_CHOICE":
        return {"type": kind, "choice_id": "A" if correct else "B"}
    if kind == "NUMERIC":
        return {"type": kind, "value": "1.00" if correct else "2.00", "unit": "m"}
    raise ValueError("Unsupported synthetic objective format")


def history_correct(learner: int, position: int) -> bool:
    cohort = learner % 4
    return (
        cohort == 0
        or (cohort == 2 and position % 2 == 0)
        or (cohort == 3 and position >= HISTORY_SESSIONS * 5 // 2)
    )


def fixture_login(identity: IdentityService, index: int) -> Credentials:
    challenge = identity.request_otp(
        OTPRequest(identifier=f"load-{index}@example.invalid", device_id=uuid4()),
        f"synthetic-load-{index}",
        None,
    )
    return identity.verify(
        OTPVerify(challenge_id=challenge.challenge_id, code="246810"), None, str(uuid4())
    )


def populate(
    identity: IdentityService, history_mixed: bool = False
) -> tuple[list[Credentials], dict[str, object]]:
    seed(identity.settings)
    # Diagnostic fixtures make Physics numeric; reassessment supplies 48 items/topic.
    # Thus random UUID ordering cannot omit numeric load from the mixed profile.
    seed_assessment(identity, reassessment=True, diagnostic=history_mixed)
    subject = next(value.id for value in identity.subjects() if value.name == "Mathematics")
    subjects = [value.id for value in identity.subjects()] if history_mixed else [subject]
    tokens = []
    for index in range(REGISTERED):
        credentials = fixture_login(identity, index)
        token = credentials.access_token
        if index < ACTIVE:
            identity.update_profile(
                token,
                ProfilePatch(
                    display_name="Synthetic load learner",
                    birth_date=date(2000, 1, 1),
                    subject_ids=subjects,
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
            tokens.append(credentials)
    topic = AssessmentService(identity).topics(tokens[0].access_token, subject)[0].id
    return tokens, {"subject_id": str(subject), "topic_id": str(topic), "mode": "TOPIC"}


def prepare_history(
    identity: IdentityService,
    credentials: list[Credentials],
) -> tuple[list[str], list[dict[str, object]]]:
    """Use normal domain transactions; no fabricated grades or disabled protections."""
    assessment = AssessmentService(identity)
    subject_ids = {value.name: value.id for value in identity.subjects()}

    def learner(index: int) -> dict[str, object]:
        credentials[index] = identity.refresh(credentials[index].refresh_token)
        token = credentials[index].access_token
        subject = subject_ids["Mathematics" if index % 2 == 0 else "Physics"]
        topics = assessment.topics(token, subject)
        for session_index in range(HISTORY_SESSIONS):
            session = assessment.start(
                token,
                StartRevision(subject_id=subject, topic_id=topics[session_index % len(topics)].id),
                uuid4(),
                uuid4(),
            )
            for position in range(5):
                item = assessment.next_item(token, session.id, uuid4())
                correct = history_correct(index // 2, session_index * 5 + position)
                grade = assessment.submit(
                    token,
                    session.id,
                    SubmitAnswer.model_validate(
                        {
                            "session_item_id": item.session_item_id,
                            "response": fixture_response(item.response_spec.type, correct),
                        }
                    ),
                    uuid4(),
                    uuid4(),
                )
                if (
                    not isinstance(grade, GradeView)
                    or grade.score != int(correct)
                    or grade.mastery_update_status != "COMPLETED"
                ):
                    raise RuntimeError("Synthetic history verification failed")
        topic = next(
            (value for value in topics if value.name == "Electricity and Magnetism"), topics[0]
        )
        return {"subject_id": str(subject), "topic_id": str(topic.id), "mode": "TOPIC"}

    # Bounded fixture preparation, outside timed HTTP. No pool/application limit changes.
    with ThreadPoolExecutor(max_workers=8) as pool:
        plans = list(pool.map(learner, range(ACTIVE)))
    # Normal refresh rotation; token lifetimes and OTP cooldowns stay unchanged.
    return [identity.refresh(value.refresh_token).access_token for value in credentials], plans


async def exercise(
    port: int,
    tokens: list[str],
    plan: dict[str, object],
    measured: Measurements,
    plans: list[dict[str, object]] | None = None,
) -> None:
    if plans is not None and len(plans) != len(tokens):
        raise ValueError("Each learner requires exactly one plan")
    slots, pacer = asyncio.Semaphore(CONCURRENT), AnswerPacer()
    async with httpx.AsyncClient(
        base_url=f"http://127.0.0.1:{port}",
        trust_env=False,
        timeout=10,
        limits=httpx.Limits(max_connections=CONCURRENT, max_keepalive_connections=CONCURRENT),
    ) as client:

        async def learner(token: str, learner_plan: dict[str, object]) -> None:
            async with slots:
                try:
                    await measured.request(client, "PROFILE", "GET", "/api/v1/me", token)
                    state = await measured.request(
                        client, "START", "POST", "/api/v1/revision-sessions", token, learner_plan
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
                                "response": fixture_response(item["response_spec"]["type"]),
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
                        f"/api/v1/me/progress?subject_id={learner_plan['subject_id']}",
                        token,
                    )
                    if state["status"] == "COMPLETED" and state["answered_count"] == 5:
                        measured.completed += 1
                    else:
                        measured.errors += 1
                except RuntimeError:
                    return
                except (KeyError, TypeError, ValueError):
                    measured.errors += 1

        async with asyncio.timeout(300):
            await asyncio.gather(
                *(
                    learner(token, plans[index] if plans else plan)
                    for index, token in enumerate(tokens)
                )
            )


def run(settings: Settings, history_mixed: bool = False) -> dict[str, object]:
    url = local_database_url(settings)
    name = database_name("kasoma_load_" + uuid4().hex)
    admin = create_engine(
        url.set(database="postgres"), isolation_level="AUTOCOMMIT", hide_parameters=True
    )
    created = False
    owner_was_absent = False
    engine = None
    server = None
    thread = None
    listener = None
    measured: Measurements | None = None
    result: dict[str, object] = {
        "status": "FAILED",
        "profile": "isolated-history-mixed-http-v1"
        if history_mixed
        else "isolated-objective-http-v1",
    }
    stage = "CREATE_DATABASE"
    try:
        with admin.connect() as db:
            db.execute(text(f'CREATE DATABASE "{name}"'))
            created = True
        stage = "CHECK_OWNER_ROLE"
        with admin.connect() as db:
            exists = db.scalar(
                text("SELECT EXISTS(SELECT 1 FROM pg_catalog.pg_roles WHERE rolname=:role)"),
                {"role": owner_name(name, "public")},
            )
            if exists is not False:
                raise RuntimeError("Pre-existing isolated owner is preserved")
            owner_was_absent = True
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
        credentials, plan = populate(identity, history_mixed)
        tokens = [value.access_token for value in credentials]
        plans = None
        history_attempts = ACTIVE * HISTORY_SESSIONS * 5 if history_mixed else 0
        history_sessions = ACTIVE * HISTORY_SESSIONS if history_mixed else 0
        if history_mixed:
            stage = "SYNTHETIC_HISTORY"
            tokens, plans = prepare_history(identity, credentials)
        with Session(engine) as db:
            item_count = db.scalar(select(func.count()).select_from(ItemVersion)) or 0
            prior_attempts = db.scalar(select(func.count()).select_from(Attempt)) or 0
            prior_grades = db.scalar(select(func.count()).select_from(Grade)) or 0
            prior_sessions = (
                db.scalar(
                    select(func.count())
                    .select_from(AssessmentSession)
                    .where(AssessmentSession.status == "COMPLETED")
                )
                or 0
            )
        if (
            prior_attempts != history_attempts
            or prior_grades != history_attempts
            or prior_sessions != history_sessions
        ):
            raise RuntimeError("Synthetic history counts differ")
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
        asyncio.run(exercise(port, tokens, plan, measured, plans))
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
            and completed == ACTIVE + history_sessions
            and attempts == grades == ACTIVE * 5 + history_attempts
            and (not history_mixed or set(measured.answer_formats) == OBJECTIVE_FORMATS)
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
                "history_attempts": prior_attempts,
                "history_grades": prior_grades,
                "history_completed_sessions": prior_sessions,
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
    except Exception as exc:
        result.update({"status": "FAILED", "failed_stage": stage})
        if isinstance(exc, IdentityError):
            codes = {
                "OTP_INVALID",
                "OTP_RATE_LIMITED",
                "USAGE_LIMIT_REACHED",
                "AUTH_REQUIRED",
                "CONTENT_UNAVAILABLE",
                "VALIDATION_FAILED",
                "VERSION_CONFLICT",
            }
            result["failure_code"] = exc.code if exc.code in codes else "DOMAIN_REJECTED"
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
                if owner_was_absent:
                    cleanup_owner(admin, name)
            except Exception:
                result.update({"cleanup_failed": True, "status": "FAILED"})
        admin.dispose()
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--history-mixed", action="store_true")
    arguments = parser.parse_args()
    report = run(Settings(), history_mixed=arguments.history_mixed)
    print(json.dumps(report, sort_keys=True))
    raise SystemExit(0 if report["status"] == "PASSED" else 1)
