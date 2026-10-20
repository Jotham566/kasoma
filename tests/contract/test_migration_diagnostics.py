"""NFR-MNT-001/SEC-002: failed verification stays failed without raw diagnostic data."""

import pytest

from scripts.migration_diagnostics import classify


@pytest.mark.parametrize(
    "message,code",
    [
        (b"No space left on device", "STORAGE_EXHAUSTED"),
        (b"psycopg.errors.DiskFull", "STORAGE_EXHAUSTED"),
        (b"out of shared memory", "SHARED_MEMORY_EXHAUSTED"),
        (b"out of memory", "MEMORY_EXHAUSTED"),
        (b"canceling statement due to statement timeout", "STATEMENT_TIMEOUT"),
        (b"canceling statement due to lock timeout", "LOCK_TIMEOUT"),
        (b"connection refused", "CONNECTION_UNAVAILABLE"),
        (None, "UNCLASSIFIED"),
        (b"unrecognized failure", "UNCLASSIFIED"),
    ],
)
def test_only_closed_failure_category_is_returned(message, code):
    sensitive = b"synthetic-credential-that-must-not-be-returned"
    assert classify(sensitive + (message or b"") + sensitive) == code
    assert classify(message) == code


def test_only_bounded_diagnostic_tail_is_used():
    assert classify(b"No space left on device" + b"X" * 32768) == "UNCLASSIFIED"
