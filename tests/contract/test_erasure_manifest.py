"""Approved71-source baseline and structural drift denials; never deletion clearance."""

import re
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from services.erasure_inventory import ObservedSource, SourceManifestChanged, assert_baseline
from services.erasure_manifest import BASELINE, BASELINE_REVISION, SourceColumn

ROOT = Path(__file__).resolve().parents[2]


def observed():
    return {
        name: ObservedSource(value.primary_key, value.columns) for name, value in BASELINE.items()
    }


def test_frozen_baseline_agrees_with_approved_disposition_and_factual_source_documents():
    manifest = (ROOT / "docs/implementation/E8_ERASURE_DISPOSITION_PROPOSAL.md").read_text()
    entries = {
        name: (tuple(key.strip() for key in pk.split(",")), action)
        for name, pk, action in re.findall(
            r"^\| `([a-z_]+)` \| `([^`]+)` \| ([A-Z]) \|", manifest, re.M
        )
    }
    entries |= {
        "operations_configuration_versions": (("id",), "K"),
        "operations_configuration_state": (("id",), "K"),
    }
    assert len(entries) == len(BASELINE) == 71
    assert {
        name: (value.primary_key, value.disposition) for name, value in BASELINE.items()
    } == entries
    inventory = (ROOT / "docs/implementation/E8_ERASURE_SOURCE_INVENTORY.md").read_text()
    sections = re.findall(r"^### `([^`]+)`\n(.*?)(?=^### |^## |\Z)", inventory, re.M | re.S)
    assert len(sections) == 69
    for name, body in sections:
        columns = body.split("Columns: ", 1)[1].split("\n\n", 1)[0]
        expected = tuple(
            SourceColumn(field, kind, nullable == "?")
            for field, nullable, kind in re.findall(r"`([a-z_0-9]+)(\?)?: ([^`]+)`", columns)
        )
        assert BASELINE[name].columns == expected
    assert sum(len(value.columns) for value in BASELINE.values()) == 501
    assert_baseline(BASELINE_REVISION, observed())


@pytest.mark.parametrize("revision", ["0042", "0043", "0045", "head", ""])
def test_migration_drift_refuses_same_table_shape(revision):
    with pytest.raises(SourceManifestChanged, match="^SOURCE_MANIFEST_CHANGED$"):
        assert_baseline(revision, observed())


def test_sources_cannot_be_added_removed_or_replaced():
    sources = observed()
    sources["unreviewed_archive"] = sources["users"]
    with pytest.raises(SourceManifestChanged):
        assert_baseline(BASELINE_REVISION, sources)
    sources.pop("users")
    with pytest.raises(SourceManifestChanged):
        assert_baseline(BASELINE_REVISION, sources)
    sources.pop("unreviewed_archive")
    with pytest.raises(SourceManifestChanged):
        assert_baseline(BASELINE_REVISION, sources)


@pytest.mark.parametrize("change", ["name", "type", "nullable", "removed", "added", "key"])
def test_column_and_primary_key_drift_fail_closed(change):
    sources = observed()
    original = sources["users"]
    column = original.columns[0]
    match change:
        case "name":
            revised = replace(column, name="another_id")
        case "type":
            revised = replace(column, type_name="text")
        case "nullable":
            revised = replace(column, nullable=not column.nullable)
        case _:
            revised = column
    columns = (revised,) + original.columns[1:]
    if change == "removed":
        columns = columns[1:]
    if change == "added":
        columns += (SourceColumn("new_profile_copy", "text", True),)
    sources["users"] = ObservedSource(("display_name",) if change == "key" else ("id",), columns)
    with pytest.raises(SourceManifestChanged, match="^SOURCE_MANIFEST_CHANGED$"):
        assert_baseline(BASELINE_REVISION, sources)


def test_manifest_is_not_mutable_runtime_configuration():
    with pytest.raises(TypeError):
        BASELINE["users"] = BASELINE["grades"]
    with pytest.raises(FrozenInstanceError):
        BASELINE["users"].disposition = "K"


@pytest.mark.parametrize("kind", ["p", "v", "f", "m"])
def test_changed_relation_kind_cannot_hide_new_partition_or_external_storage(kind):
    sources = observed()
    sources["users"] = replace(sources["users"], relation_kind=kind)
    with pytest.raises(SourceManifestChanged):
        assert_baseline(BASELINE_REVISION, sources)
