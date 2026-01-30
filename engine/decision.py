from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


DecisionOutcome = Literal["ALLOW", "DENY", "NOT_APPLICABLE"]


class TraceEntry(BaseModel):
    kind: Literal["target", "condition", "policy"]
    ok: bool

    field: Optional[str] = None
    operator: Optional[str] = None
    expected: Optional[Any] = None
    actual: Optional[Any] = None

    detail: Optional[str] = None
    policy_id: Optional[str] = None


class Decision(BaseModel):
    decision: DecisionOutcome
    policy_id: Optional[str] = None
    trace: list[TraceEntry] = Field(default_factory=list)
    reason: Optional[str] = None
