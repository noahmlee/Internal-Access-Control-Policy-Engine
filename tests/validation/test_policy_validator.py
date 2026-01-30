import pytest
from tests.fixtures.policy import valid_policy
from validation.policy_validator import (
    PolicyValidationError,
    validate_policy_semantics,
)
from validation.schema import Policy


def test_unknown_operator_fails():
    data = valid_policy()
    data["conditions"]["all"][0]["operator"] = "contains"

    policy = Policy(**data)

    with pytest.raises(PolicyValidationError, match="Unsupported operator"):
        validate_policy_semantics(policy)


def test_illegal_field_path_fails():
    data = valid_policy()
    data["conditions"]["all"][0]["field"] = "__dict__"

    policy = Policy(**data)

    with pytest.raises(PolicyValidationError, match="Illegal field path"):
        validate_policy_semantics(policy)


def test_operator_value_mismatch_fails():
    data = valid_policy()
    data["conditions"]["all"][0]["operator"] = "in"
    data["conditions"]["all"][0]["value"] = "admin"

    policy = Policy(**data)

    with pytest.raises(PolicyValidationError, match="expects a list"):
        validate_policy_semantics(policy)


def test_valid_policy_passes_semantic_validation():
    policy = Policy(**valid_policy())
    validate_policy_semantics(policy)
