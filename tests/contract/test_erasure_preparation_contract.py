"""A metadata collector cannot replace fresh-source creation authority."""

import pytest

from scripts.erasure_capability import CapabilityInstallUnavailable, install, prepare_catalog


@pytest.mark.parametrize("operation", ["INSTALL", "PREPARE"])
def test_duck_typed_scope_is_refused_before_its_methods_are_called(operation):
    calls = []

    class OtherScope:
        def verify(self):
            calls.append(True)

    with pytest.raises(CapabilityInstallUnavailable):
        if operation == "INSTALL":
            install(OtherScope())
        else:
            prepare_catalog(OtherScope(), lambda *_: calls.append(True))
    assert calls == []
