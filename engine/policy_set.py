from __future__ import annotations
from typing import Any, Iterable, Literal, Optional
from engine.decision import Decision, TraceEntry
from engine.evaluator import evaluate_policy_decision


ConflictStrategy = Literal["deny_overrides"]


def evaluate_policies_decision(
    policies: Iterable[Any],
    context: dict[str, Any],
    *,
    strategy: ConflictStrategy = "deny_overrides",
) -> Decision:
    policies_list = list(policies)
    traces: list[TraceEntry] = []

    matched: list[Decision] = []
    for policy in policies_list:
        d = evaluate_policy_decision(policy, context)
        traces.append(
            TraceEntry(
                kind="policy",
                ok=d.decision != "NOT_APPLICABLE",
                policy_id=d.policy_id,
                detail=d.decision,
            )
        )
        if d.decision != "NOT_APPLICABLE":
            matched.append(d)

    if not matched:
        return Decision(
            decision="NOT_APPLICABLE",
            policy_id=None,
            trace=traces,
            reason="no applicable policies",
        )

    if strategy != "deny_overrides":
        raise ValueError(f"unsupported strategy '{strategy}'")

    deny = next((d for d in matched if d.decision == "DENY"), None)
    if deny is not None:
        return Decision(
            decision="DENY",
            policy_id=deny.policy_id,
            trace=traces + deny.trace,
            reason="deny overrides",
        )

    allow = next((d for d in matched if d.decision == "ALLOW"), None)
    if allow is not None:
        return Decision(
            decision="ALLOW",
            policy_id=allow.policy_id,
            trace=traces + allow.trace,
            reason="allow (no denies matched)",
        )

    return Decision(
        decision="NOT_APPLICABLE",
        policy_id=None,
        trace=traces,
        reason="no applicable policies",
    )
