from engine.operators import OPERATORS
from engine.target_matcher import target_matches

DECISION_DENY = "DENY"
DECISION_NOT_APPLICABLE = "NOT_APPLICABLE"

def resolve_field(path: str, context: dict):
    parts = path.split(".")
    value = context
    for part in parts:
        if not isinstance(value, dict):
            return None
        value = value.get(part)
        if value is None:
            return None
    return value

def evaluate_conditions(conditions, context: dict) -> bool:
    condition_list = conditions.all if conditions.all is not None else conditions.any
    mode_all = conditions.all is not None

    if condition_list is None:
        raise ValueError("conditions must define exactly one of 'all' or 'any'")

    results = []
    for condition in condition_list:
        actual = resolve_field(condition.field, context)
        operator_fn = OPERATORS.get(condition.operator)
        if operator_fn is None:
            raise ValueError(f"Unsupported operator '{condition.operator}'")
        results.append(operator_fn(actual, condition.value))

    return all(results) if mode_all else any(results)

def evaluate_policy(policy, context) -> str:
    if not target_matches(policy.target, context):
        return DECISION_NOT_APPLICABLE
    
    if not evaluate_conditions(policy.conditions, context):
        return DECISION_DENY
    
    return policy.effect