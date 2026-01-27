from engine.operators import OPERATORS
from validation.policy_validator import PolicyValidationError

def resolve_field(path: str, context: dict):
    parts = path.split(".")
    value = context
    for part in parts:
        value = value.get(part)
        if value is None:
            return None
    return value

def evaluate_conditions(conditions, context: dict) -> bool:
    results = []

    for condition in conditions.all:
        actual = resolve_field(condition.field, context)
        operator_fn = OPERATORS[condition.operator]
        results.append(operator_fn(actual, condition.value))

    return all(results)

def evaluate_policy(policy, context) -> str:
    if not evaluate_conditions(policy.conditions, context):
        return "DENY"
    
    return policy.effect