import pytest

from pydantic import ValidationError
from tests.fixtures.policy import valid_policy
from validation.schema import Policy


def test_valid_policy_passes():
    policy = Policy(**valid_policy())
    assert policy.policy_id == "test.policy.v1"


def test_missing_required_field_fails():
    data = valid_policy()
    del data["effect"]

    with pytest.raises(ValidationError):
        Policy(**data)


def test_both_all_and_any_fails():
    data = valid_policy()
    data["conditions"]["any"] = [
        {
            "field": "user.department",
            "operator": "equals",
            "value": "engineering",
        }
    ]

    with pytest.raises(ValidationError):
        Policy(**data)


def test_neither_all_nor_any_fails():
    data = valid_policy()
    data["conditions"] = {}

    with pytest.raises(ValidationError):
        Policy(**data)


def test_invalid_effect_fails():
    data = valid_policy()
    data["effect"] = "PERMIT"

    with pytest.raises(ValidationError):
        Policy(**data)
