"""FR-MST-004/005, NFR-LOC-001: seven owned Kampala calendar dates, not a streak."""

from datetime import UTC, date, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from services.practice_activity import practice_activity
from services.progress_contracts import PracticeActivity

AT = datetime(2026, 10, 20, 0, 5, tzinfo=UTC)


def test_empty_window_has_explicit_kampala_calendar_boundaries():
    result = practice_activity([], AT)
    assert result.days_practised == 0
    assert result.window_start == date(2026, 10, 14)
    assert result.window_end == date(2026, 10, 20)
    assert result.window_days == 7
    assert result.time_zone == "Africa/Kampala" and result.version == "practice-days-v1"


def test_one_utc_date_can_include_two_kampala_practice_dates():
    before = datetime(2026, 10, 19, 20, 59, 59, tzinfo=UTC)
    midnight = datetime(2026, 10, 19, 21, tzinfo=UTC)
    assert practice_activity([before, midnight], AT).days_practised == 2


def test_first_midnight_is_inclusive_and_now_is_not_rounded_to_end_of_today():
    lower = datetime(2026, 10, 13, 21, tzinfo=UTC)
    assert practice_activity([lower - timedelta(microseconds=1)], AT).days_practised == 0
    assert practice_activity([lower, AT], AT).days_practised == 2
    with pytest.raises(ValueError, match="future evidence"):
        practice_activity([AT + timedelta(microseconds=1)], AT)


def test_seven_days_deduplicate_mappings_and_repeated_practice_without_order_dependence():
    stamps = [AT - timedelta(days=d) for d in range(7)]
    result = practice_activity(stamps, AT)
    assert result.days_practised == 7
    assert practice_activity(list(reversed(stamps)) * 3, AT) == result
    assert practice_activity([AT, AT, AT - timedelta(minutes=1)], AT).days_practised == 1


def test_older_dates_and_equivalent_timestamp_representations():
    other_zone = timezone(timedelta(hours=-7))
    assert practice_activity([AT.astimezone(other_zone)], AT) == practice_activity([AT], AT)
    assert practice_activity([AT - timedelta(days=30)], AT).days_practised == 0
    # The observer's timezone never changes the explicit Kampala calendar window.
    assert practice_activity([AT], AT.astimezone(other_zone)) == practice_activity([AT], AT)


def test_year_boundary_is_calendar_based():
    at = datetime(2026, 12, 31, 21, tzinfo=UTC)
    result = practice_activity([at], at)
    assert result.window_end == date(2027, 1, 1)
    assert result.window_start == date(2026, 12, 26)


@pytest.mark.parametrize("naive_clock", [True, False])
def test_naive_times_never_use_the_host_timezone(naive_clock):
    with pytest.raises(ValueError, match="aware"):
        practice_activity(
            [AT] if naive_clock else [AT.replace(tzinfo=None)],
            AT.replace(tzinfo=None) if naive_clock else AT,
        )


@pytest.mark.parametrize(
    "changes",
    [
        {"days_practised": -1},
        {"days_practised": 8},
        {"days_practised": True},
        {"window_end": date(2026, 10, 21)},
        {"window_days": 8},
        {"time_zone": "UTC"},
        {"version": "unknown"},
        {"learner_id": "not accepted"},
    ],
)
def test_projection_rejects_invalid_counts_windows_versions_and_extra_identity(changes):
    data = practice_activity([], AT).model_dump()
    with pytest.raises(ValidationError):
        PracticeActivity.model_validate(data | changes)
