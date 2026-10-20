"""Closed server compiler, not a caller-selected SQL/row/clock interface."""

from scripts.erasure_plan_sql import compile_plan_helpers


def test_compiler_quotes_names_and_keeps_subjects_typed_and_rows_uncapped():
    value = compile_plan_helpers('cap"; unsafe', 'crypto"; unsafe')
    assert '"cap""; unsafe".source_version(_subject uuid,_plan uuid)' in value
    assert '"crypto""; unsafe".hmac(' in value
    assert ":subject" not in value
    assert "LIMIT " not in value
    assert "x.xmin::text" in value
    assert "WHEN x.id=_plan THEN to_jsonb(x)-'version'" in value
    assert "fingerprint_key" in value and "RETURN encode(_state,'hex')" in value


def test_plan_lifetime_is_trusted_bounded_configuration_not_a_caller_cutoff():
    from unittest.mock import Mock

    import pytest

    from scripts.erasure_capability import CapabilityInstallUnavailable, install

    for value in [0, -1, 601, True, "600"]:
        proof = Mock()
        with pytest.raises(CapabilityInstallUnavailable):
            install(proof, plan_ttl_seconds=value)
        proof.verify.assert_not_called()
