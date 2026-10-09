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
def test_rejects_unsafe_profile_before_connect(settings, monkeypatch, changed):
    connect = Mock(side_effect=AssertionError("must not connect"))
    monkeypatch.setattr(load, "create_engine", connect)
    with pytest.raises(ValueError):
        load.run(local(settings).model_copy(update=changed))
    connect.assert_not_called()


@pytest.mark.parametrize(
    "creation_fails,cleanup_fails", [(True, False), (False, False), (False, True)]
)
def test_cleanup_only_created_database_and_redacts_failures(
    settings, monkeypatch, creation_fails, cleanup_fails
):
    engine = MagicMock()
    execute = engine.connect.return_value.__enter__.return_value.execute
    execute.side_effect = (
        [RuntimeError("sensitive")]
        if creation_fails
        else [None, RuntimeError("sensitive") if cleanup_fails else None]
    )
    monkeypatch.setattr(load, "create_engine", lambda *a, **k: engine)
    migrate = Mock(side_effect=RuntimeError("sensitive"))
    monkeypatch.setattr(load.subprocess, "run", migrate)
    result = load.run(local(settings))
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
