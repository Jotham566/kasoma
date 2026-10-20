"""Closed failure categories for synthetic migration subprocesses; never echo stderr."""


def classify(stderr: bytes | None) -> str:
    sample = (stderr or b"")[-32768:].lower()
    for code, markers in (
        ("STORAGE_EXHAUSTED", (b"no space left on device", b"psycopg.errors.diskfull")),
        ("SHARED_MEMORY_EXHAUSTED", (b"out of shared memory",)),
        ("MEMORY_EXHAUSTED", (b"out of memory",)),
        ("STATEMENT_TIMEOUT", (b"canceling statement due to statement timeout",)),
        ("LOCK_TIMEOUT", (b"canceling statement due to lock timeout",)),
        ("CONNECTION_UNAVAILABLE", (b"connection refused", b"could not connect to server")),
    ):
        if any(marker in sample for marker in markers):
            return code
    return "UNCLASSIFIED"
