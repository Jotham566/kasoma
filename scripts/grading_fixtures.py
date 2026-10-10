"""Unapproved synthetic calibration metadata for tests/recovery only, never seeding."""

from uuid import uuid4

from services.short_text_eligibility import CalibrationBand, GradingScope


def unapproved_band(scope: GradingScope) -> CalibrationBand:
    return CalibrationBand(
        id=uuid4(),
        scope=scope,
        minimum_characters=1,
        maximum_characters=2000,
        benchmark_id=uuid4(),
        report_sha256="a" * 64,
        benchmark_cases=100,
        benchmark_within_tolerance=85,
        held_out_cases=20,
        held_out_exact=18,
        critical_errors=0,
        subgroup_review="PENDING",
    )
