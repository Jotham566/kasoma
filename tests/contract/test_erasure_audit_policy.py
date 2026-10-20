"""Approved exact action vocabulary; no invented policy, deadline or prefix fallback."""

import pytest

from services.erasure_audit_policy import AUDIT_RULES, AuditClassificationUncertain, rule_for


@pytest.mark.parametrize(
    "action",
    ["unknown", "content.flag.created.extra", "data_request.future", "", "secret@example.invalid"],
)
def test_unknown_action_has_only_a_fixed_private_failure(action):
    with pytest.raises(AuditClassificationUncertain) as raised:
        rule_for(action)
    assert str(raised.value) == "AUDIT_CLASSIFICATION_REQUIRES_REVIEW"
    assert action not in str(raised.value) or action == ""


def test_rules_are_immutable_and_do_not_invent_deadlines():
    assert len(AUDIT_RULES) == 35
    assert rule_for("data_request.created").classification == "MATERIAL_CASE"
    assert rule_for("content.flag.created").subject_is_actor
    assert not rule_for("content.flag.updated").subject_is_actor
    assert rule_for("content.flag.read").classification == "SECURITY"
    assert rule_for("operations.configuration.changed").classification == "STAFF"
    with pytest.raises(TypeError):
        AUDIT_RULES["new.action"] = rule_for("data_request.created")
    assert not hasattr(rule_for("data_request.created"), "deadline")
