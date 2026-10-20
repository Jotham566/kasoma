"""Closed typed slot contracts preserve every nonbound raw-tree byte."""

from dataclasses import replace
from uuid import UUID

import pytest

from services.erasure_catalog_bindings import CatalogBindings, freeze_expression

KEY = "CONSTRAINT:CAPABILITY.control:control_owner_oid_check"


def bindings():
    return CatalogBindings(16384, 2200, 18001, 18002, 18003, 10, UUID(int=91))


def constant(value, *, oid=23, declared=4, location=173):
    octets = "".join(str(part) + " " for part in value.to_bytes(8, "little"))
    return (
        "{CONST :consttype " + str(oid) + " :consttypmod -1 :constcollid 0 "
        ":constlen 4 :constbyval true :constisnull false :location "
        + str(location)
        + " :constvalue "
        + str(declared)
        + " [ "
        + octets
        + "]}"
    )


def test_expected_integer_slot_preserves_locations_and_all_outer_fields():
    original = bindings()
    tree = "{OPEXPR :opno 607 :args (" + constant(original.owner_oid) + ") :location 141}"
    expected = freeze_expression(KEY, tree, original)
    varied = replace(original, owner_oid=100001)
    assert expected.render(original) == tree
    assert expected.render(varied) == tree.replace(constant(18001), constant(100001))
    assert ":location 173" in expected.template and ":location 141" in expected.template
    assert expected.model_validate_json(expected.model_dump_json()).render(
        varied
    ) == expected.render(varied)


@pytest.mark.parametrize("bad", [True, 0, -1, 2**31, "18001"])
def test_unknown_integer_representation_is_refused(bad):
    with pytest.raises(ValueError, match="Unsupported installed catalog"):
        replace(bindings(), owner_oid=bad)


@pytest.mark.parametrize(
    "tree",
    [
        constant(18002),
        constant(18001, oid=20),
        constant(18001, declared=8),
        constant(18001) + constant(18001, location=99),
    ],
)
def test_changed_missing_or_ambiguous_constant_is_not_learned(tree):
    with pytest.raises(ValueError, match="exactly once"):
        freeze_expression(KEY, tree, bindings())


def test_unknown_field_is_not_a_new_binding_permission():
    with pytest.raises(ValueError, match="Unknown installed expression"):
        freeze_expression("CONSTRAINT:public.users:anything", constant(18001), bindings())
