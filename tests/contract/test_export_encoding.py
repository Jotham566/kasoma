"""Byte limits include metadata/escaping and stop source consumption without a partial result."""

import json
from contextlib import closing

import pytest

from services.data_export_encoding import encode_records
from services.identity import IdentityError


def test_complete_envelope_exact_limit_and_empty_sections():
    rows = [("empty", None), ("answers", None), ("answers", {"text": 'π "quoted"\nline', "n": 0})]
    metadata = {"request_id": "synthetic", "exclusions": ["No guardian evidence"]}
    expected = {"records": {"empty": [], "answers": [rows[-1][1]]}, **metadata}
    limit = len(json.dumps(expected, sort_keys=True, separators=(",", ":")).encode())
    raw = b"".join(encode_records(iter(rows), lambda: metadata, max_bytes=limit))
    assert json.loads(raw) == expected
    assert len(raw) == limit
    with pytest.raises(IdentityError, match="EXPORT_LIMIT_REACHED"):
        b"".join(encode_records(iter(rows), lambda: metadata, max_bytes=limit - 1))


def test_no_sections_and_metadata_budget_are_validated():
    assert json.loads(b"".join(encode_records(iter([]), lambda: {}, max_bytes=None))) == {
        "records": {}
    }
    with pytest.raises(IdentityError, match="EXPORT_LIMIT_REACHED"):
        b"".join(encode_records(iter([]), lambda: {"description": "x" * 200}, max_bytes=50))


def test_limit_stops_consumption_and_closes_source_before_metadata():
    observed, closed = [], []

    def source():
        try:
            yield "answers", None
            for i in range(1000):
                observed.append(i)
                yield "answers", {"text": "synthetic" * 100}
        finally:
            closed.append(True)

    def metadata():
        raise AssertionError("Do not finish an exhausted export")

    with pytest.raises(IdentityError, match="EXPORT_LIMIT_REACHED"):
        b"".join(encode_records(source(), metadata, max_bytes=100))
    assert observed == [0] and closed == [True]


def test_consumer_cancellation_closes_an_active_source():
    closed = []

    def source():
        try:
            yield "answers", None
            yield "answers", {"text": "synthetic"}
            raise AssertionError("Consumer cancelled")
        finally:
            closed.append(True)

    with closing(encode_records(source(), lambda: {}, max_bytes=None)) as chunks:
        assert next(chunks) == b'{"records":{'
        assert next(chunks) == b'"answers":['
    assert closed == [True]


@pytest.mark.parametrize(
    "rows",
    [
        [("answer", {})],
        [("answers", None), ("different", {})],
        [("answers", None), ("answers", None)],
    ],
)
def test_malformed_section_sequences_fail_closed(rows):
    with pytest.raises(ValueError):
        b"".join(encode_records(iter(rows), lambda: {}, max_bytes=None))


def test_metadata_cannot_override_records_or_serialize_nonfinite_values():
    with pytest.raises(ValueError, match="cannot replace"):
        b"".join(encode_records(iter([]), lambda: {"records": {}}, max_bytes=None))
    with pytest.raises(ValueError):
        b"".join(
            encode_records(
                iter([("x", None), ("x", {"n": float("nan")})]), lambda: {}, max_bytes=None
            )
        )
