from typing import Any, Iterable
from validation.schema import Policy, Condition

class PolicyValidationError(Exception):
    """
    Raised when a policy violates semantic validation rules.
    """
    pass

# Operator registry: defines allowed operators and their constraints
OPERATOR_DEFINITIONS = {
    "equals": {
        "expects_iterable": False,
    },
    "in": {
        "expects_iterable": True,
    },
    "gt": {
        "expects_numeric": True,
    },
    "lt": {
        "expects_numeric": True,
    },
}

ALLOWED_FIELD_PREFIXES = {
    "user.",
    "resource.",
    "request.",
}

def validate_policy_semantics(policy: Policy) -> None:
    """
    Enforces semantic rules on a structurally valid policy.
    Raises PolicyValidationError on failure.
    """
    conditions = (
        policy.conditions.all
        if policy.conditions.all is not None
        else policy.conditions.any
    )
    
    for condition in conditions:
        _validate_condition(condition)
        
def _validate_condition(condition: Condition) -> None:
    _validate_operator(condition)
    _validate_field_path(condition)
    _validate_operator_value(condition)
    
def _validate_operator(condition: Condition) -> None:
    if condition.operator not in OPERATOR_DEFINITIONS:
        raise PolicyValidationError(
            f"Unsupported operator '{condition.operator}'"
        )
    
def _validate_field_path(condition: Condition) -> None:
    if not any(
        condition.field.startswith(prefix)
        for prefix in ALLOWED_FIELD_PREFIXES
    ):
        raise PolicyValidationError(
            f"Illegal field path '{condition.field}'"
        )
        
def _validate_operator_value(condition: Condition) -> None:
    rules = OPERATOR_DEFINITIONS.get(condition.operator, {})
    
    if rules.get("expects_iterable"):
        if not isinstance(condition.value, Iterable) or isinstance(condition.value, str):
            raise PolicyValidationError(
                f"Operator '{condition.operator}' expects a list value"
            )
            
    if rules.get("expects_numeric"):
        if not isinstance(condition.value, (int, float)):
            raise PolicyValidationError(
                f"Operator '{condition.operator}' expects a numeric value"
            )