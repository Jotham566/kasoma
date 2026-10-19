"""Payload-free, best-effort OTP observer port; never accepts message content."""

from typing import Literal, Protocol


class OTPObserver(Protocol):
    def record(
        self, kind: Literal["EMAIL", "SMS"], outcome: Literal["RETURNED", "FAILED"]
    ) -> None: ...


def observe(
    observer: OTPObserver | None,
    kind: Literal["EMAIL", "SMS"],
    outcome: Literal["RETURNED", "FAILED"],
) -> None:
    try:
        if observer is not None:
            observer.record(kind, outcome)
    except Exception:
        # Instrumentation cannot change OTP behavior or expose observer diagnostics.
        return
