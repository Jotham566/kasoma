"""Synthetic report/approval identifiers exercise policy, never academic acceptance."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from pydantic import ValidationError

from services.short_text_eligibility import (
    AuditOutcome,
    AuditState,
    CalibrationBand,
    GradingScope,
    audit_required,
    eligibility,
)

NOW = datetime(2026, 10, 10, tzinfo=UTC)
SCOPE = GradingScope(
    subject_id=UUID(int=1),
    topic_id=UUID(int=2),
    language="en",
    model_version="fake-v1",
    prompt_version="synthetic-v2",
    configuration_version="test-v1",
)


@pytest.fixture
def band():
    return CalibrationBand(
        id=UUID(int=3),
        scope=SCOPE,
        minimum_characters=10,
        maximum_characters=100,
        benchmark_id=UUID(int=4),
        report_sha256="a" * 64,
        benchmark_cases=100,
        benchmark_within_tolerance=85,
        held_out_cases=20,
        held_out_exact=18,
        critical_errors=0,
        subgroup_review="APPROVED",
        approval_id=UUID(int=5),
        approved_at=NOW,
        enabled=True,
    )


def decide(band, **overrides):
    return eligibility(
        band,
        **{
            "scope": SCOPE,
            "response_characters": 25,
            "audit": AuditState(band_id=UUID(int=3), returned_grades=0, assigned_audits=0),
            "now": NOW,
            **overrides,
        },
    )


def test_exact_thresholds_are_necessary_not_sufficient_authority(band):
    assert decide(band) == "ELIGIBLE_CANDIDATE"
    assert decide(None) == "UNAPPROVED"
    assert decide(band.model_copy(update={"enabled": False})) == "DISABLED"
    assert (
        decide(band.model_copy(update={"approval_id": None, "approved_at": None})) == "UNAPPROVED"
    )
    assert (
        decide(band.model_copy(update={"approved_at": NOW + timedelta(seconds=1)})) == "UNAPPROVED"
    )


@pytest.mark.parametrize(
    "field,value,reason",
    [
        ("benchmark_within_tolerance", 84, "BENCHMARK"),
        ("held_out_exact", 17, "CALIBRATION"),
        ("subgroup_review", "PENDING", "SUBGROUP"),
        ("subgroup_review", "HARMFUL", "SUBGROUP"),
        ("critical_errors", 1, "CRITICAL_ERROR"),
    ],
)
def test_each_academic_gate_is_independent(band, field, value, reason):
    assert decide(band.model_copy(update={field: value})) == reason


@pytest.mark.parametrize(
    "field,value",
    [
        ("subject_id", UUID(int=8)),
        ("topic_id", UUID(int=9)),
        ("model_version", "fake-v2"),
        ("prompt_version", "synthetic-v3"),
        ("configuration_version", "test-v2"),
    ],
)
def test_every_scope_and_version_must_match(band, field, value):
    assert decide(band, scope=SCOPE.model_copy(update={field: value})) == "SCOPE_MISMATCH"


@pytest.mark.parametrize(
    "length,expected",
    [
        (9, "LENGTH_MISMATCH"),
        (10, "ELIGIBLE_CANDIDATE"),
        (100, "ELIGIBLE_CANDIDATE"),
        (101, "LENGTH_MISMATCH"),
        (0, "LENGTH_MISMATCH"),
        (2001, "LENGTH_MISMATCH"),
        (True, "LENGTH_MISMATCH"),
    ],
)
def test_character_band_boundaries(band, length, expected):
    assert decide(band, response_characters=length) == expected


def state(exact, *, critical=False, disabled=False):
    results = tuple(
        AuditOutcome(
            grade_id=UUID(int=i + 100),
            exact=correct,
            critical_error=critical and i == 0,
            completed_at=NOW,
        )
        for i, correct in enumerate(exact)
    )
    return AuditState(
        band_id=UUID(int=3),
        returned_grades=len(results) * 10,
        assigned_audits=len(results),
        completed_audits=len(results),
        recent=results,
        disabled=disabled,
    )


def test_rolling_agreement_and_sticky_disablement(band):
    assert decide(band, audit=state([True] * 9 + [False])) == "ELIGIBLE_CANDIDATE"
    assert decide(band, audit=state([True] * 8 + [False] * 2)) == "AUDIT_AGREEMENT"
    assert decide(band, audit=state([False])) == "AUDIT_AGREEMENT"
    assert decide(band, audit=state([True], critical=True)) == "CRITICAL_ERROR"
    assert decide(band, audit=state([True] * 100, disabled=True)) == "DISABLED"


def test_pending_audits_do_not_count_as_agreement(band):
    audit = state([False]).model_copy(update={"returned_grades": 100, "assigned_audits": 10})
    assert decide(band, audit=audit) == "AUDIT_AGREEMENT"
    with pytest.raises(ValidationError):
        decide(band, audit=audit.model_copy(update={"recent": ()}))


def test_every_publication_prefix_meets_ten_percent_assignment():
    assigned = 0
    for ordinal in range(1, 10001):
        assigned += audit_required(ordinal)
        assert assigned == (ordinal + 9) // 10
        assert assigned * 10 >= ordinal
    for invalid in (0, -1, True, 1.5, 1_000_000_001):
        with pytest.raises(ValueError):
            audit_required(invalid)


def test_assignment_coverage_and_cross_band_replay(band):
    audit = AuditState(band_id=band.id, returned_grades=11, assigned_audits=1)
    assert decide(band, audit=audit) == "AUDIT_COVERAGE"
    assert (
        decide(band, audit=audit.model_copy(update={"assigned_audits": 2})) == "ELIGIBLE_CANDIDATE"
    )
    with pytest.raises(ValueError, match="another band"):
        decide(band, audit=audit.model_copy(update={"band_id": UUID(int=999)}))


@pytest.mark.parametrize(
    "change",
    [
        {"held_out_exact": 21},
        {"benchmark_within_tolerance": 101},
        {"minimum_characters": 101},
        {"approval_id": None},
        {"approved_at": NOW.replace(tzinfo=None)},
        {"held_out_cases": 0},
        {"enabled": 1},
        {"policy_version": "unapproved-v2"},
        {"model_confidence": 1.0},
        {"report_sha256": "not-a-digest"},
    ],
)
def test_malformed_or_unvalidated_report_copies_fail_closed(band, change):
    with pytest.raises(ValidationError):
        decide(band.model_copy(update=change))


def test_audit_window_bound_order_uniqueness_and_clock(band):
    audit = state([True, True])
    first, second = audit.recent
    for invalid in (
        audit.model_copy(update={"recent": (first, first)}),
        audit.model_copy(
            update={
                "recent": (
                    first.model_copy(update={"completed_at": NOW + timedelta(seconds=1)}),
                    second,
                )
            }
        ),
        audit.model_copy(update={"assigned_audits": 1}),
    ):
        with pytest.raises(ValidationError):
            decide(band, audit=invalid)
    with pytest.raises(ValidationError):
        state([True] * 101)
    with pytest.raises(ValueError, match="future"):
        eligibility(
            band.model_copy(update={"approved_at": NOW - timedelta(seconds=2)}),
            scope=SCOPE,
            response_characters=25,
            audit=state([True]),
            now=NOW - timedelta(seconds=1),
        )
    with pytest.raises(ValueError, match="timezone"):
        decide(band, now=NOW.replace(tzinfo=None))
