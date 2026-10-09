"""Bound native diagnostic framing and keep browser error payloads out of output."""

import json

import pytest

from scripts.firefox_native_browser import Wire


class Connection:
    def __init__(self, data):
        self.data = bytearray(data)
        self.sent = bytearray()

    def recv(self, size):
        result = bytes(self.data[:size])
        del self.data[:size]
        return result

    def sendall(self, data):
        self.sent.extend(data)


def frame(value):
    payload = json.dumps(value, ensure_ascii=False).encode()
    return str(len(payload)).encode() + b":" + payload


@pytest.mark.parametrize("data", [b"", b":", b"x:", b"0:", b"1048577:", b"999999999:", b"3:{}"])
def test_invalid_or_incomplete_protocol_frames_fail_closed(data):
    with pytest.raises(RuntimeError):
        Wire(Connection(data)).read()


def test_protocol_uses_byte_lengths_and_matches_reply_sequence():
    connection = Connection(frame([1, 1, None, {"value": "synthetic"}]))
    wire = Wire(connection)
    assert wire.command("probe", {"value": "é"}) == {"value": "synthetic"}
    sent = Wire(Connection(connection.sent)).read()
    assert sent == [0, 1, "probe", {"value": "é"}]


@pytest.mark.parametrize(
    "reply",
    [
        {},
        [1],
        [1, 2, None, {}],
        [0, 1, None, {}],
        [1, 99, {"error": "unexpected alert open"}, None],
    ],
)
def test_unmatched_or_malformed_replies_fail_closed(reply):
    with pytest.raises(RuntimeError):
        Wire(Connection(frame(reply))).command("probe", {})


def test_error_details_never_enter_diagnostic_exception():
    reply = [1, 1, {"error": "javascript error", "message": "private sentinel"}, None]
    with pytest.raises(RuntimeError, match="javascript error") as caught:
        Wire(Connection(frame(reply))).command("probe", {})
    assert "private sentinel" not in str(caught.value)


def test_native_failure_dialog_notification_retries_observation_once():
    error = {"error": "unexpected alert open", "message": "synthetic dialog"}
    connection = Connection(frame([1, 1, error, None]) + frame([1, 2, None, {"value": True}]))
    assert Wire(connection).command("WebDriver:ExecuteAsyncScript", {}) == {"value": True}
    replay = Wire(Connection(connection.sent))
    assert replay.read() == [0, 1, "WebDriver:ExecuteAsyncScript", {}]
    assert replay.read() == [0, 2, "WebDriver:ExecuteAsyncScript", {}]


def test_repeated_native_dialog_never_retries_indefinitely():
    error = {"error": "unexpected alert open"}
    connection = Connection(frame([1, 1, error, None]) + frame([1, 2, error, None]))
    with pytest.raises(RuntimeError, match="unexpected alert open"):
        Wire(connection).command("WebDriver:ExecuteAsyncScript", {})


def test_native_export_input_accepts_only_owned_synthetic_cookie_shape():
    from scripts.firefox_native_export import validate

    target = "00000000-0000-4000-8000-000000000001"
    cookies = [{"name": "kasoma_access", "value": "synthetic-token"}]
    assert validate({"target": target, "cookies": cookies}) == (target, cookies)
    bad = [
        {"target": "../escape", "cookies": cookies},
        {"target": target, "cookies": []},
        {"target": target, "cookies": cookies * 2},
        {"target": target, "cookies": [{"name": "foreign", "value": "x"}]},
        {"target": target, "cookies": [{"name": "kasoma_access", "value": "x\nsecret"}]},
        {"target": target, "cookies": [{"name": "kasoma_access", "value": "x" * 1025}]},
        {"target": target, "cookies": cookies, "origin": "https://example.invalid"},
        {"target": target, "cookies": [{**cookies[0], "domain": "example.invalid"}]},
    ]
    for payload in bad:
        with pytest.raises(ValueError):
            validate(payload)
