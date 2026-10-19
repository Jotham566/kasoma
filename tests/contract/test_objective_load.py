"""Load runner isolation, measured errors, minimization and pacing without network calls."""

import asyncio
from unittest.mock import MagicMock, Mock

import httpx
import pytest
from pydantic import SecretStr

from scripts import objective_load as load


@pytest.mark.parametrize(
    "value",
    ["kasoma", "postgres", "kasoma_load_", "kasoma_load_" + "a" * 33, 'x"; DROP DATABASE kasoma'],
)
def test_rejects_non_generated_database_names(value):
    with pytest.raises(ValueError):
        load.database_name(value)


def test_nearest_rank_quantiles_and_empty_are_not_zero():
    assert load.percentiles([]) == {"samples": 0, "p50_ms": None, "p95_ms": None, "p99_ms": None}
    assert load.percentiles(list(range(1, 101))) == {
        "samples": 100,
        "p50_ms": 50,
        "p95_ms": 95,
        "p99_ms": 99,
    }


def test_slow_operation_cannot_hide_in_the_mixed_percentile():
    measured = load.Measurements()
    for operation in load.OPERATIONS:
        measured.timings[operation] = [10.0] * 100
    assert load.latency_passes(measured)
    measured.timings["START"] = [652.0]
    assert measured.report()["all_http"]["p95_ms"] == 10
    assert not load.latency_passes(measured)
    measured.timings["START"] = [500.0]
    assert not load.latency_passes(measured)
    measured.timings["START"] = []
    assert not load.latency_passes(measured)


def test_slow_numeric_subset_cannot_hide_in_choice_answers():
    measured = load.Measurements()
    for operation in load.OPERATIONS:
        measured.timings[operation] = [10.0] * 100
    measured.answer_formats["SINGLE_CHOICE"] = [10.0] * 99
    measured.answer_formats["NUMERIC"] = [501.0]
    assert measured.report()["all_http"]["p95_ms"] == 10
    assert not load.latency_passes(measured)
    measured.answer_formats["NUMERIC"] = [499.0]
    assert load.latency_passes(measured)


def local(settings):
    return settings.model_copy(
        update={
            "app_env": "development",
            "database_url": SecretStr("postgresql+psycopg://kasoma:secret@localhost:55432/keep_me"),
        }
    )


@pytest.mark.parametrize(
    "changed",
    [
        {"app_env": "production"},
        {
            "database_url": SecretStr(
                "postgresql+psycopg://kasoma:secret@remote.invalid:55432/keep_me"
            )
        },
    ],
)
@pytest.mark.parametrize("history_mixed", [False, True])
def test_rejects_unsafe_profile_before_connect(settings, monkeypatch, changed, history_mixed):
    connect = Mock(side_effect=AssertionError("must not connect"))
    monkeypatch.setattr(load, "create_engine", connect)
    with pytest.raises(ValueError):
        load.run(local(settings).model_copy(update=changed), history_mixed=history_mixed)
    connect.assert_not_called()


@pytest.mark.parametrize(
    "creation_fails,cleanup_fails", [(True, False), (False, False), (False, True)]
)
@pytest.mark.parametrize("history_mixed", [False, True])
def test_cleanup_only_created_database_and_redacts_failures(
    settings, monkeypatch, creation_fails, cleanup_fails, history_mixed
):
    engine = MagicMock()
    engine.connect.return_value.__enter__.return_value.scalar.side_effect = [False, None]
    execute = engine.connect.return_value.__enter__.return_value.execute
    execute.side_effect = (
        [RuntimeError("sensitive")]
        if creation_fails
        else [None, RuntimeError("sensitive") if cleanup_fails else None]
    )
    monkeypatch.setattr(load, "create_owner", Mock(return_value=1234))
    monkeypatch.setattr(load, "create_engine", lambda *a, **k: engine)
    migrate = Mock(side_effect=RuntimeError("sensitive"))
    monkeypatch.setattr(load.subprocess, "run", migrate)
    result = load.run(local(settings), history_mixed=history_mixed)
    assert result["status"] == "FAILED"
    assert result["cleanup_failed"] is cleanup_fails
    statements = [str(call.args[0]) for call in execute.call_args_list]
    assert len(statements) == (1 if creation_fails else 2)
    name = statements[0].split('"')[1]
    assert load.database_name(name) == name
    if not creation_fails:
        assert statements[1] == f'DROP DATABASE "{name}"'
        assert "keep_me" not in migrate.call_args.kwargs["env"]["DATABASE_URL"]
    assert "sensitive" not in str(result)
    assert "secret" not in str(result)


@pytest.mark.parametrize(
    "code,expected", [("OTP_INVALID", "OTP_INVALID"), ("secret-token", "DOMAIN_REJECTED")]
)
def test_domain_failure_diagnostics_are_closed_and_cleanup_still_runs(
    settings, monkeypatch, code, expected
):
    from services.identity import IdentityError

    engine = MagicMock()
    engine.connect.return_value.__enter__.return_value.scalar.side_effect = [False, None]
    monkeypatch.setattr(load, "create_owner", Mock(return_value=1234))
    monkeypatch.setattr(load, "create_engine", lambda *a, **k: engine)
    monkeypatch.setattr(load.subprocess, "run", Mock(side_effect=IdentityError(code)))
    result = load.run(local(settings), history_mixed=True)
    assert result["failure_code"] == expected
    assert result["cleanup_failed"] is False
    assert "secret" not in str(result)
    assert engine.connect.return_value.__enter__.return_value.execute.call_count == 2


@pytest.mark.parametrize(
    "status,payload",
    [(200, b'{"status":"ok"}'), (500, b"sensitive"), (200, b"[]"), (200, b"invalid")],
)
def test_real_measurement_boundary_records_errors_without_payload(status, payload):
    measured = load.Measurements()

    async def invoke():
        async with httpx.AsyncClient(
            base_url="http://127.0.0.1",
            transport=httpx.MockTransport(lambda request: httpx.Response(status, content=payload)),
        ) as client:
            if status == 200 and payload.startswith(b"{"):
                assert await measured.request(
                    client, "PROFILE", "GET", "/secret-path", "secret-token"
                ) == {"status": "ok"}
            else:
                with pytest.raises(RuntimeError, match="Synthetic request failed"):
                    await measured.request(client, "PROFILE", "GET", "/secret-path", "secret-token")

    asyncio.run(invoke())
    report = measured.report()
    assert measured.inflight == 0
    assert report["peak_inflight_http"] == 1
    assert len(measured.timings["PROFILE"]) == 1
    assert measured.errors == (0 if status == 200 and payload.startswith(b"{") else 1)
    assert "secret" not in str(report)
    assert "sensitive" not in str(report)


def test_pacer_spaces_answers_and_does_not_catch_up_after_idle(monkeypatch):
    clock = [1.0]
    waits = []
    monkeypatch.setattr(load, "monotonic", lambda: clock[0])

    async def sleep(delay):
        waits.append(delay)
        clock[0] += delay

    monkeypatch.setattr(load.asyncio, "sleep", sleep)

    async def exercise():
        pacer = load.AnswerPacer()
        for _ in range(3):
            assert await pacer.wait() == 0
        clock[0] = 100
        assert await pacer.wait() == 0
        assert await pacer.wait() == 0

    asyncio.run(exercise())
    assert waits == pytest.approx([0, 0.05, 0.05, 0, 0.05])


def test_concurrent_delayed_dispatches_do_not_collapse_into_a_burst(monkeypatch):
    clock = [1.0]
    yield_loop = asyncio.sleep
    monkeypatch.setattr(load, "monotonic", lambda: clock[0])

    async def exercise():
        gate = asyncio.Event()

        async def delayed_sleep(delay):
            due = clock[0] + delay
            await gate.wait()
            clock[0] = max(clock[0], due)

        monkeypatch.setattr(load.asyncio, "sleep", delayed_sleep)
        pacer = load.AnswerPacer()
        dispatched = []

        async def request():
            await pacer.wait()
            dispatched.append(clock[0])

        pending = [asyncio.create_task(request()) for _ in range(3)]
        await yield_loop(0)
        clock[0] = 2.0
        gate.set()
        await asyncio.gather(*pending)
        assert dispatched == pytest.approx([2.0, 2.05, 2.1])

    asyncio.run(exercise())


def test_normal_timer_jitter_does_not_reduce_the_offered_rate(monkeypatch):
    clock = [1.0]
    monkeypatch.setattr(load, "monotonic", lambda: clock[0])

    async def jittered_sleep(delay):
        clock[0] += delay + 0.001

    monkeypatch.setattr(load.asyncio, "sleep", jittered_sleep)

    async def exercise():
        pacer = load.AnswerPacer()
        dispatched = []
        for _ in range(3):
            await pacer.wait()
            dispatched.append(clock[0])
        assert dispatched == pytest.approx([1.001, 1.051, 1.101])

    asyncio.run(exercise())


@pytest.mark.parametrize("kind", ["SHORT_TEXT", "MULTIPLE_CHOICE", "unknown"])
def test_fixture_solver_refuses_unregistered_formats(kind):
    with pytest.raises(ValueError, match="Unsupported synthetic objective format"):
        load.fixture_response(kind)


@pytest.mark.parametrize("kind", sorted(load.OBJECTIVE_FORMATS))
@pytest.mark.parametrize("correct", [True, False])
def test_objective_fixture_responses_are_valid_contracts(kind, correct):
    from uuid import uuid4

    from services.assessment_contracts import SubmitAnswer

    value = load.fixture_response(kind, correct)
    parsed = SubmitAnswer.model_validate({"session_item_id": uuid4(), "response": value})
    assert parsed.response.model_dump() == value
    assert load.fixture_response(kind, not correct) != value


def test_history_has_strong_weak_inconsistent_and_improving_cohorts():
    rows = [
        [load.history_correct(cohort, position) for position in range(50)] for cohort in range(4)
    ]
    assert rows[0] == [True] * 50
    assert rows[1] == [False] * 50
    assert rows[2] == [True, False] * 25
    assert rows[3] == [False] * 25 + [True] * 25


@pytest.mark.parametrize("unsupported", [False, True])
def test_http_journeys_bind_each_plan_and_measure_numeric_without_external_calls(
    monkeypatch, unsupported
):
    requests = []
    positions = {"math": 0, "physics": 0}

    def handle(request):
        requests.append(request)
        token = request.headers["Authorization"].split()[1]
        if request.url.path.endswith("revision-sessions"):
            import json

            assert json.loads(request.content)["subject_id"] == token
            return httpx.Response(200, json={"id": token})
        if request.url.path.endswith("next-item"):
            kind = "NUMERIC" if token == "physics" else "SINGLE_CHOICE"
            if unsupported:
                kind = "SHORT_TEXT"
            return httpx.Response(
                200, json={"session_item_id": "fixture", "response_spec": {"type": kind}}
            )
        if request.url.path.endswith("attempts"):
            import json

            body = json.loads(request.content)
            expected = load.fixture_response("NUMERIC" if token == "physics" else "SINGLE_CHOICE")
            assert body["response"] == expected
            positions[token] += 1
            return httpx.Response(200, json={"score": 1, "mastery_update_status": "COMPLETED"})
        if request.url.path.endswith("progress"):
            assert request.url.params["subject_id"] == token
        return httpx.Response(200, json={"status": "COMPLETED", "answered_count": 5})

    original = httpx.AsyncClient
    monkeypatch.setattr(
        load.httpx,
        "AsyncClient",
        lambda **kwargs: original(**kwargs, transport=httpx.MockTransport(handle)),
    )

    async def no_pacing(self):
        return 0

    monkeypatch.setattr(load.AnswerPacer, "wait", no_pacing)
    measured = load.Measurements()
    plans = [{"subject_id": token} for token in positions]
    asyncio.run(load.exercise(1, list(positions), {}, measured, plans))
    assert all(request.url.host == "127.0.0.1" for request in requests)
    if unsupported:
        assert measured.errors == 2
        assert measured.completed == 0
        assert not measured.answer_formats
    else:
        assert positions == {"math": 5, "physics": 5}
        assert measured.completed == 2
        assert measured.errors == 0
        assert measured.report()["answer_formats"]["NUMERIC"]["samples"] == 5
        assert measured.report()["answer_formats"]["SINGLE_CHOICE"]["samples"] == 5
    assert "fixture" not in str(measured.report())


@pytest.mark.parametrize("history_mixed", [False, True])
@pytest.mark.parametrize(
    "before,after,drop_database_fails,drop_role_fails",
    [
        (False, None, False, False),
        (False, True, False, False),
        (True, None, False, False),
        (False, False, False, False),
        (False, True, True, False),
        (False, True, False, True),
        (False, RuntimeError("sensitive role lookup"), False, False),
        (RuntimeError("sensitive preflight"), None, False, False),
    ],
)
def test_exact_owned_role_lifecycle_and_private_failures(
    settings, monkeypatch, history_mixed, before, after, drop_database_fails, drop_role_fails
):
    from services.export_retirement_install import owner_name

    engine = MagicMock()
    connection = engine.connect.return_value.__enter__.return_value
    connection.scalar.side_effect = [before, after]
    statements = []

    def execute(statement):
        value = str(statement)
        statements.append(value)
        if value.startswith("DROP DATABASE") and drop_database_fails:
            raise RuntimeError("sensitive database cleanup")
        if value.startswith("DROP ROLE") and drop_role_fails:
            raise RuntimeError("sensitive role cleanup")

    connection.execute.side_effect = execute
    monkeypatch.setattr(load, "create_owner", Mock(return_value=1234))
    monkeypatch.setattr(load, "create_engine", lambda *a, **k: engine)
    migrate = Mock(side_effect=RuntimeError("sensitive migration"))
    monkeypatch.setattr(load.subprocess, "run", migrate)
    result = load.run(local(settings), history_mixed=history_mixed)
    name = statements[0].split('"')[1]
    role = owner_name(load.database_name(name), "public")
    assert statements[:2] == [f'CREATE DATABASE "{name}"', f'DROP DATABASE "{name}"']
    checked = before is False
    migration_reached = checked
    assert migrate.call_count == int(migration_reached)
    assert result["failed_stage"] == ("MIGRATE" if checked else "CHECK_OWNER_ROLE")
    assert result["status"] == "FAILED"
    cleanup_lookup = checked and not drop_database_fails
    assert connection.scalar.call_count == 1 + int(cleanup_lookup)
    for position, call in enumerate(connection.scalar.call_args_list):
        assert call.args[1] == (
            {"role": role} if position == 0 else {"role": role, "owner_oid": 1234}
        )
        assert "WHERE" in str(call.args[0]) and ":role" in str(call.args[0])
    role_drop = cleanup_lookup and after is True
    assert statements[2:] == ([f'DROP ROLE "{role}"'] if role_drop else [])
    assert result["cleanup_failed"] is bool(
        drop_database_fails
        or cleanup_lookup
        and (after is False or isinstance(after, Exception))
        or role_drop
        and drop_role_fails
    )
    assert all(value not in str(result) for value in ["sensitive", "secret", name, role])
    engine.dispose.assert_called_once()


@pytest.mark.parametrize("history_mixed", [False, True])
def test_failed_exclusive_creation_never_confers_owner_cleanup(
    settings, monkeypatch, history_mixed
):
    engine = MagicMock()
    connection = engine.connect.return_value.__enter__.return_value
    connection.scalar.return_value = False
    monkeypatch.setattr(load, "create_engine", lambda *a, **k: engine)
    create = Mock(side_effect=RuntimeError("sensitive concurrent role creation"))
    monkeypatch.setattr(load, "create_owner", create)
    migrate = Mock()
    monkeypatch.setattr(load.subprocess, "run", migrate)
    result = load.run(local(settings), history_mixed=history_mixed)
    statements = [str(call.args[0]) for call in connection.execute.call_args_list]
    name = statements[0].split('"')[1]
    assert statements == [f'CREATE DATABASE "{name}"', f'DROP DATABASE "{name}"']
    create.assert_called_once_with(engine, name)
    migrate.assert_not_called()
    assert connection.scalar.call_count == 1
    assert result["failed_stage"] == "CREATE_OWNER_ROLE"
    assert result["status"] == "FAILED"
    assert result["cleanup_failed"] is False
    assert "sensitive" not in str(result)
