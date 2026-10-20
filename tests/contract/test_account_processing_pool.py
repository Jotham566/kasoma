"""ADR-070: pool/session lock cleanup under failures and interruptions."""

from contextlib import nullcontext
from unittest.mock import Mock
from uuid import UUID

import pytest

from services.account_processing import (
    ProcessingGateUnavailable,
    dispatch_connections,
    dispatch_gate,
)


def connection(results):
    owned = Mock()
    owned.scalar.side_effect = results
    owned.in_transaction.return_value = False
    engine = Mock()
    engine.connect.return_value = nullcontext(owned)
    return engine, owned


def test_acquisition_transaction_ends_before_body_and_release_precedes_return():
    engine, owned = connection([True, True])
    with dispatch_gate(engine, UUID(int=1)):
        owned.commit.assert_called_once_with()
        assert owned.scalar.call_count == 1
        owned.invalidate.assert_not_called()
    assert owned.commit.call_count == 2
    owned.invalidate.assert_not_called()
    for call in owned.scalar.call_args_list:
        assert call.args[1] == {"subject": UUID(int=1)}
        assert "kasoma.account-processing.v1:" in str(call.args[0])


@pytest.mark.parametrize(
    "subjects",
    [(), (UUID(int=1), UUID(int=2), UUID(int=3)), [UUID(int=1)], ("untrusted",), (None,), (1,)],
)
def test_dispatch_subject_set_is_closed_before_connection_checkout(subjects):
    engine = Mock()
    with pytest.raises(ProcessingGateUnavailable), dispatch_connections(engine, subjects):
        raise AssertionError("Invalid or unbounded subject set must not dispatch")
    engine.connect.assert_not_called()


@pytest.mark.parametrize("failure", [RuntimeError("synthetic"), KeyboardInterrupt()])
def test_uncertain_acquisition_discards_connection_and_never_enters_body(failure):
    engine, owned = connection([failure])
    with pytest.raises(type(failure)), dispatch_gate(engine, UUID(int=1)):
        raise AssertionError("Uncertain dispatch must not run")
    owned.invalidate.assert_called_once_with()


def test_busy_exclusive_gate_refuses_dispatch():
    engine, owned = connection([False])
    with pytest.raises(ProcessingGateUnavailable), dispatch_gate(engine, UUID(int=1)):
        raise AssertionError("Busy dispatch must not run")
    owned.invalidate.assert_called_once_with()


@pytest.mark.parametrize("result", [False, RuntimeError("synthetic"), KeyboardInterrupt()])
def test_uncertain_unlock_never_returns_a_locked_connection_to_pool(result):
    engine, owned = connection([True, result])
    error = ProcessingGateUnavailable if result is False else type(result)
    with pytest.raises(error), dispatch_gate(engine, UUID(int=1)):
        pass
    owned.invalidate.assert_called_once_with()


def test_provider_failure_still_releases_session_gate():
    engine, owned = connection([True, True])
    with pytest.raises(ValueError, match="synthetic"), dispatch_gate(engine, UUID(int=1)):
        raise ValueError("synthetic")
    assert owned.scalar.call_count == owned.commit.call_count == 2
    owned.invalidate.assert_not_called()


@pytest.mark.parametrize("commit_index", [1, 2])
def test_uncertain_acquisition_or_release_commit_discards_session(commit_index):
    engine, owned = connection([True, True])
    owned.commit.side_effect = (
        [RuntimeError("synthetic commit failure")]
        if commit_index == 1
        else [None, RuntimeError("synthetic commit failure")]
    )
    entered = False
    with pytest.raises(RuntimeError, match="synthetic commit failure"):
        with dispatch_gate(engine, UUID(int=1)):
            entered = True
    assert entered == (commit_index == 2)
    owned.invalidate.assert_called_once_with()


def test_missing_current_namespace_is_not_a_silent_unlocked_transaction():
    from services.account_processing import coordinate

    db = Mock()
    db.execute.return_value.one_or_none.return_value = None
    with pytest.raises(ProcessingGateUnavailable):
        coordinate(db, UUID(int=1))
