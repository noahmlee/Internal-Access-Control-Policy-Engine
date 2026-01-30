import pytest

from engine.errors import ContextValidationError
from engine.evaluator import evaluate_policy
from tests.fixtures.context import base_context
from tests.fixtures.policy import valid_policy
from validation.schema import Policy


def test_policy_allows_when_condition_matches():
    policy = Policy(**valid_policy())
    context = base_context()

    decision = evaluate_policy(policy, context)

    assert decision == "ALLOW"


def test_policy_denies_when_condition_fails():
    data = valid_policy()
    policy = Policy(**data)

    context = base_context()
    context["user"]["role"] = "viewer"

    decision = evaluate_policy(policy, context)

    assert decision == "DENY"


def test_missing_field_raises_context_validation_error():
    policy = Policy(**valid_policy())

    context = base_context()
    del context["user"]["role"]

    with pytest.raises(ContextValidationError, match="missing field"):
        evaluate_policy(policy, context)


def test_in_operator_allows_when_value_in_list():
    data = valid_policy()
    data["conditions"]["all"][0] = {
        "field": "user.role",
        "operator": "in",
        "value": ["admin", "owner"],
    }

    policy = Policy(**data)
    context = base_context()

    decision = evaluate_policy(policy, context)

    assert decision == "ALLOW"


def test_all_conditions_must_pass():
    data = valid_policy()
    data["conditions"]["all"].append(
        {
            "field": "environment.env",
            "operator": "equals",
            "value": "prod",
        }
    )

    policy = Policy(**data)
    context = base_context()

    decision = evaluate_policy(policy, context)

    assert decision == "ALLOW"


def test_policy_denies_when_resource_type_mismatch():
    policy = Policy(**valid_policy())
    context = base_context()
    context["resource"]["type"] = "image"

    assert evaluate_policy(policy, context) == "NOT_APPLICABLE"


def test_any_conditions_allow_when_one_matches():
    data = valid_policy()
    data["conditions"] = {
        "any": [
            {"field": "user.role", "operator": "equals", "value": "viewer"},
            {"field": "user.role", "operator": "equals", "value": "admin"},
        ]
    }
    policy = Policy(**data)
    context = base_context()

    assert evaluate_policy(policy, context) == "ALLOW"


def test_any_conditions_deny_when_none_match():
    data = valid_policy()
    data["conditions"] = {
        "any": [
            {"field": "user.role", "operator": "equals", "value": "viewer"},
            {"field": "environment.env", "operator": "equals", "value": "staging"},
        ]
    }
    policy = Policy(**data)
    context = base_context()

    assert evaluate_policy(policy, context) == "DENY"
