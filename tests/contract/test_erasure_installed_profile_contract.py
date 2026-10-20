"""Strict artifact envelope and closed fields; fixtures confer no SQL clearance."""

import json
from uuid import UUID

import pytest
from pydantic import ValidationError

from services import erasure_installed_profile as artifact
from services.erasure_catalog import CATEGORIES, RAW_CATEGORIES, CatalogDigest
from services.erasure_catalog_bindings import (
    BOUND_EXPRESSIONS,
    BoundExpression,
    CatalogBindings,
    ConstantSlot,
)


def profile():
    bindings = CatalogBindings(16384, 2200, 18001, 18002, 18003, 10, UUID(int=91))
    expressions = {}
    for key, names in BOUND_EXPRESSIONS.items():
        slots = {}
        for name in names:
            value = bindings.value(name)
            if type(value) is int:
                slot = ConstantSlot(kind="INTEGER", width=8)
            elif type(value) is UUID:
                slot = ConstantSlot(kind="UUID", width=16)
            else:
                width = 4 + len(str(value).encode())
                slot = ConstantSlot(
                    kind="TEXT", width=width, prefix=tuple((width << 2).to_bytes(4, "little"))
                )
            slots[name] = slot
        expressions[key] = BoundExpression(
            key=key, template=" ".join("@" + name.upper() + "@" for name in names), slots=slots
        )
    return artifact.InstalledProfile(
        migration_sources_sha256="0" * 64,
        recipe_sources_sha256="1" * 64,
        expressions=expressions,
        raw={name: CatalogDigest(count=0, digest="2" * 64) for name in RAW_CATEGORIES},
        full={name: CatalogDigest(count=0, digest="3" * 64) for name in CATEGORIES},
    )


@pytest.mark.parametrize("field", ["expressions", "raw", "full"])
def test_missing_or_extra_category_is_not_an_installed_profile(field):
    value = json.loads(profile().canonical())
    value[field].pop(next(iter(value[field])))
    with pytest.raises(ValidationError, match="Incomplete"):
        artifact.InstalledProfile.model_validate_json(json.dumps(value))
    value = json.loads(profile().canonical())
    value[field]["UNEXPECTED"] = next(iter(value[field].values()))
    with pytest.raises(ValidationError):
        artifact.InstalledProfile.model_validate_json(json.dumps(value))


def test_artifact_loader_refuses_missing_or_changed_recipe_without_regeneration(
    tmp_path, monkeypatch
):
    expected = profile()
    path = tmp_path / "test-only-profile.json"
    monkeypatch.setattr(artifact, "PROFILE_PATH", path)
    monkeypatch.setattr(artifact, "migration_digest", lambda: "0" * 64)
    monkeypatch.setattr(artifact, "recipe_digest", lambda: "1" * 64)
    with pytest.raises(FileNotFoundError):
        artifact.load_installed_profile()
    assert not path.exists()
    path.write_text(expected.canonical())
    assert artifact.load_installed_profile() == expected
    monkeypatch.setattr(artifact, "recipe_digest", lambda: "4" * 64)
    with pytest.raises(ValueError, match="recipe changed"):
        artifact.load_installed_profile()
    assert path.read_text() == expected.canonical()


@pytest.mark.parametrize(
    "field,value",
    [
        ("capability", "isolated-erasure-capability-v6"),
        ("postgres_major", 17),
        ("revision", "0044"),
    ],
)
def test_other_recipe_is_not_silently_adopted(field, value):
    data = json.loads(profile().canonical())
    data[field] = value
    with pytest.raises(ValidationError):
        artifact.InstalledProfile.model_validate_json(json.dumps(data))
