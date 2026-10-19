"""ADR-069: closed child command, private environment and owned process shutdown."""

import signal
import subprocess
from contextlib import nullcontext
from unittest.mock import Mock

import pytest

from scripts import erasure_identity_check as check


def process(monkeypatch, outcome, *, poll=0):
    child = Mock(pid=123456)
    child.wait.side_effect = outcome
    child.poll.return_value = poll
    spawn = Mock(return_value=child)
    kill = Mock()
    monkeypatch.setattr(check.subprocess, "Popen", spawn)
    monkeypatch.setattr(check.os, "killpg", kill)
    return child, spawn, kill


def test_fixed_command_has_no_shell_or_caller_selector(monkeypatch):
    child, spawn, kill = process(monkeypatch, [0])
    environment = {"DATABASE_URL": "synthetic-private-url"}
    check.verify(environment)
    spawn.assert_called_once_with(
        ["/usr/bin/make", "test-erasure-identity"], env=environment, start_new_session=True
    )
    child.wait.assert_called_once_with(timeout=600)
    kill.assert_not_called()


def test_failed_tests_never_become_success(monkeypatch):
    _, _, kill = process(monkeypatch, [2], poll=2)
    with pytest.raises(RuntimeError, match="verification failed"):
        check.verify({})
    kill.assert_not_called()


@pytest.mark.parametrize(
    "interruption", [KeyboardInterrupt(), subprocess.TimeoutExpired("synthetic", 600)]
)
def test_interrupted_child_is_stopped_before_database_cleanup(monkeypatch, interruption):
    child, _, kill = process(monkeypatch, [interruption, 0], poll=None)
    with pytest.raises(type(interruption)):
        check.verify({})
    kill.assert_called_once_with(child.pid, signal.SIGTERM)
    assert child.wait.call_args.kwargs == {"timeout": 10}


def test_unresponsive_owned_child_gets_bounded_escalation(monkeypatch):
    timeout = subprocess.TimeoutExpired("synthetic", 600)
    child, _, kill = process(
        monkeypatch, [timeout, subprocess.TimeoutExpired("synthetic", 10), 0], poll=None
    )
    with pytest.raises(subprocess.TimeoutExpired):
        check.verify({})
    assert [call.args for call in kill.call_args_list] == [
        (child.pid, signal.SIGTERM),
        (child.pid, signal.SIGKILL),
    ]


def test_child_environment_is_fake_and_uses_only_new_private_database(
    settings, monkeypatch, capsys
):
    monkeypatch.setenv("MODEL_PROVIDER", "external")
    monkeypatch.setenv("ALLOW_EXTERNAL_API_CALLS", "true")
    isolated = settings.model_copy(
        update={"model_provider": "fake", "allow_external_api_calls": False}
    )
    monkeypatch.setattr(check, "Settings", lambda **kwargs: settings.model_copy(update=kwargs))
    factory = Mock(return_value=nullcontext(isolated))
    monkeypatch.setattr(check, "erasure_test_database", factory)
    monkeypatch.setattr(check, "cleanup_on_termination", nullcontext)
    verify = Mock()
    monkeypatch.setattr(check, "verify", verify)
    check.run()
    environment = verify.call_args.args[0]
    assert environment["DATABASE_URL"] == isolated.database_url.get_secret_value()
    assert (
        environment["IDENTITY_ENCRYPTION_KEY"]
        == isolated.identity_encryption_key.get_secret_value()
    )
    assert all(
        environment[name] == "fake"
        for name in ["MODEL_PROVIDER", "EMAIL_PROVIDER", "SMS_PROVIDER", "WHATSAPP_PROVIDER"]
    )
    assert environment["ALLOW_EXTERNAL_API_CALLS"] == "false"
    assert capsys.readouterr().out == ""


def test_child_exit_during_shutdown_still_reaps_and_preserves_interruption(monkeypatch):
    child, _, kill = process(monkeypatch, [KeyboardInterrupt(), 0], poll=None)
    kill.side_effect = ProcessLookupError
    with pytest.raises(KeyboardInterrupt):
        check.verify({})
    assert child.wait.call_count == 2


def test_termination_is_never_reported_as_a_pass(monkeypatch):
    def interrupted():
        raise SystemExit(0)

    monkeypatch.setattr(check, "run", interrupted)
    with pytest.raises(SystemExit) as stopped:
        check.main()
    assert stopped.value.code == 143
