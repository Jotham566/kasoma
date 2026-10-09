"""Incremental JSON encoding; enforce the complete envelope's byte cap before collection."""

import json
from collections.abc import Callable, Generator, Iterator
from typing import Any

from services.identity import IdentityError

ExportRecord = tuple[str, dict[str, Any] | None]


def encode_records(
    records: Iterator[ExportRecord],
    metadata: Callable[[], dict[str, Any]],
    *,
    max_bytes: int | None,
) -> Generator[bytes, None, None]:
    """None opens an explicit section, including empty ones; rows follow that section.

    Caller retains the transaction. Generator closure releases its source, including on
    byte exhaustion or consumer cancellation. No fragment is a completed export artifact.
    """
    encoder = json.JSONEncoder(sort_keys=True, separators=(",", ":"), allow_nan=False)
    total = 0

    def piece(value: str) -> bytes:
        nonlocal total
        raw = value.encode("utf-8")
        total += len(raw)
        if max_bytes is not None and total > max_bytes:
            raise IdentityError("EXPORT_LIMIT_REACHED", 409)
        return raw

    try:
        yield piece('{"records":{')
        seen: set[str] = set()
        section = None
        has_rows = False
        for name, record in records:
            if record is None:
                if name in seen:
                    raise ValueError("Duplicate export section")
                seen.add(name)
                if section is not None:
                    yield piece("],")
                section, has_rows = name, False
                yield piece(encoder.encode(name) + ":[")
            else:
                if section != name:
                    raise ValueError("Export row has no matching section")
                if has_rows:
                    yield piece(",")
                has_rows = True
                for fragment in encoder.iterencode(record):
                    yield piece(fragment)
        yield piece("]}" if section is not None else "}")
        header = metadata()
        if "records" in header:
            raise ValueError("Export metadata cannot replace records")
        for name in sorted(header):
            yield piece("," + encoder.encode(name) + ":")
            for fragment in encoder.iterencode(header[name]):
                yield piece(fragment)
        yield piece("}")
    finally:
        if isinstance(records, Generator):
            records.close()
