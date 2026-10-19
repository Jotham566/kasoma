"""Roadmap3.5 / FR-MST-004/005: read-only owned practice-day projection."""

from collections.abc import Iterable
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from services.progress_contracts import PracticeActivity

KAMPALA = ZoneInfo("Africa/Kampala")


def practice_activity(timestamps: Iterable[datetime], at: datetime) -> PracticeActivity:
    """The caller supplies only its already-authorized, validated visible evidence."""
    if at.utcoffset() is None:
        raise ValueError("Practice activity requires an aware read time")
    end = at.astimezone(KAMPALA).date()
    start = end - timedelta(days=6)
    lower = datetime.combine(start, time.min, tzinfo=KAMPALA)
    days: set[date] = set()
    for stamp in timestamps:
        if stamp.utcoffset() is None:
            raise ValueError("Practice activity requires aware evidence times")
        if stamp > at:
            raise ValueError("Practice activity cannot include future evidence")
        if stamp >= lower:
            days.add(stamp.astimezone(KAMPALA).date())
    return PracticeActivity(days_practised=len(days), window_start=start, window_end=end)
