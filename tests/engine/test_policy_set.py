import pytest
from engine.errors import ContextValidationError
from tests.fixtures.context import base_context
from tests.fixtures.policy import valid_policy
from validation.schema import Policy

from engine import evaluate_policies_decision


def test_policy_set_not_applicable_when_no_policy_matches_target():
    data = valid_policy()
    data["target"]["resource_type"] = "image"
    policy = Policy(**data)

    result = evaluate_policies_decision([policy], base_context())

    assert result.decision == "NOT_APPLICABLE"
    assert result.reason == "no applicable policies"


def test_policy_set_deny_overrides_allow():
    allow_data = valid_policy()
    allow_policy = Policy(**allow_data)

    deny_data = valid_policy()
    deny_data["policy_id"] = "deny.admin.document.prod.v1"
    deny_data["conditions"]["all"][0] = {
        "field": "user.role",
        "operator": "equals",
        "value": "admin",
    }
    deny_data["effect"] = "DENY"
    deny_policy = Policy(**deny_data)

    result = evaluate_policies_decision([allow_policy, deny_policy], base_context())

    assert result.decision == "DENY"
    assert result.policy_id == "deny.admin.document.prod.v1"
    assert result.reason == "deny overrides"


def test_policy_set_raises_when_context_missing_required_target_fields():
    policy = Policy(**valid_policy())
    context = base_context()
    del context["resource"]["type"]

    with pytest.raises(ContextValidationError):
        evaluate_policies_decision([policy], context)
