"""Deterministic legacy progress replay inputs; all identifiers are synthetic."""

from datetime import timedelta
from uuid import UUID

from services.mastery_engine import normalize
from tests.contract.test_mastery_engine import NOW, grade

SKILLS = {(UUID(int=c), UUID(int=k)) for c in (1, 3) for k in (2, 4)}
SCOPES = [
    ("Subject", SKILLS),
    ("First topic", {s for s in SKILLS if s[0].int == 1}),
    ("Second topic", {s for s in SKILLS if s[0].int == 3}),
    ("First competency", {s for s in SKILLS if s[1].int == 2}),
    ("Second competency", {s for s in SKILLS if s[1].int == 4}),
]


def cases():
    dense = [
        normalize(
            grade(
                index + 100 * (concept.int - 1),
                concept_id=concept,
                competency_id=competency,
                occurred_at=NOW - timedelta(days=index % 3),
                points_awarded=(index % 3) / 2,
                response_type="SINGLE_CHOICE" if index % 2 else "NUMERIC",
                mapping_weight=0.5,
            )
        )
        for concept, competency in sorted(SKILLS)
        for index in range(12)
    ]
    assert all(row is not None for row in dense)
    sparse = [normalize(grade())]
    return [
        ("empty", [], NOW, [("Empty", set())]),
        ("prior", [], NOW, SCOPES),
        ("sparse", sparse, NOW, SCOPES),
        ("dense", dense, NOW, SCOPES),
        ("duplicates", dense + dense[:5], NOW, SCOPES),
        ("reversed", list(reversed(dense)), NOW, SCOPES),
        ("decayed", dense, NOW + timedelta(days=365), SCOPES),
    ]
