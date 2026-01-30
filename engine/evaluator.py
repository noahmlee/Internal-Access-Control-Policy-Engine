from __future__ import annotations

from typing import Any, Optional

from engine.decision import Decision, TraceEntry
from engine.errors import ContextValidationError
from engine.operators import OPERATORS
from engine.target_matcher import target_matches

DECISION_DENY = "DENY"
DECISION_NOT_APPLICABLE = "NOT_APPLICABLE"

def resolve_field(path: str, context: dict[str, Any]) -> Any:
    parts = path.split(".")
    value: Any = context
    for part in parts:
        if not isinstance(value, dict):
            raise ContextValidationError(f"missing field '{path}'")
        value = value.get(part)
        if value is None:
            raise ContextValidationError(f"missing field '{path}'")
    return value

def evaluate_conditions(conditions, context: dict[str, Any]) -> bool:
    condition_list = conditions.all if conditions.all is not None else conditions.any
    mode_all = conditions.all is not None

    if condition_list is None:
        raise ValueError("conditions must define exactly one of 'all' or 'any'")

    results: list[bool] = []
    for condition in condition_list:
        actual = resolve_field(condition.field, context)
        operator_fn = OPERATORS.get(condition.operator)
        if operator_fn is None:
            raise ValueError(f"Unsupported operator '{condition.operator}'")
        results.append(operator_fn(actual, condition.value))

    return all(results) if mode_all else any(results)

def evaluate_policy(policy, context: dict[str, Any]) -> str:
    if not target_matches(policy.target, context):
        return DECISION_NOT_APPLICABLE
    
    if not evaluate_conditions(policy.conditions, context):
        return DECISION_DENY
    
    return policy.effect


def evaluate_policy_decision(policy, context: dict[str, Any]) -> Decision:
    policy_id: Optional[str] = getattr(policy, "policy_id", None)
    trace: list[TraceEntry] = []

    if not target_matches(policy.target, context):
        trace.append(
            TraceEntry(
                kind="target",
                ok=False,
                detail="target did not match request context",
            )
        )
        return Decision(
            decision=DECISION_NOT_APPLICABLE,
            policy_id=policy_id,
            trace=trace,
            reason="target mismatch",
        )

    trace.append(TraceEntry(kind="target", ok=True))

    condition_list = (
        policy.conditions.all
        if policy.conditions.all is not None
        else policy.conditions.any
    )
    mode_all = policy.conditions.all is not None

    if condition_list is None:
        raise ValueError("conditions must define exactly one of 'all' or 'any'")

    results: list[bool] = []
    for condition in condition_list:
        actual = resolve_field(condition.field, context)
        operator_fn = OPERATORS.get(condition.operator)
        if operator_fn is None:
            raise ValueError(f"Unsupported operator '{condition.operator}'")
        ok = operator_fn(actual, condition.value)
        results.append(ok)
        trace.append(
            TraceEntry(
                kind="condition",
                ok=ok,
                field=condition.field,
                operator=condition.operator,
                expected=condition.value,
                actual=actual,
            )
        )

    conditions_ok = all(results) if mode_all else any(results)
    if not conditions_ok:
        return Decision(
            decision=DECISION_DENY,
            policy_id=policy_id,
            trace=trace,
            reason="conditions not satisfied",
        )

    return Decision(
        decision=getattr(policy.effect, "value", policy.effect),
        policy_id=policy_id,
        trace=trace,
        reason="conditions satisfied",
    )
