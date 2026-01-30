from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, Field, model_validator


class Effect(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"


class Target(BaseModel):
    resource_type: str = Field(..., description="Type of the target resource")
    environment: str = Field(..., description="Environment (e.g. prod, staging)")


class Condition(BaseModel):
    field: str = Field(
        ...,
        description="Dotted path into the request context (e.g. user.role)",
    )
    operator: str = Field(
        ...,
        description="Symbolic operator name (validated separately)",
    )
    value: Any = Field(
        None,
        description="Comparison value (operator-dependent)",
    )


class Conditions(BaseModel):
    all: Optional[List[Condition]] = None
    any: Optional[List[Condition]] = None

    @model_validator(mode="after")
    def validate_condition_group(self):
        if self.all and self.any:
            raise ValueError("Only one of 'all' or 'any' may be defined")

        if not self.all and not self.any:
            raise ValueError("One of 'all' or 'any' must be defined")

        return self


class Policy(BaseModel):
    policy_id: str = Field(
        ...,
        description="Globally unique, versioned policy identifier",
    )
    description: Optional[str] = Field(
        None,
        description="Human-readable description of the policy intent",
    )
    target: Target
    conditions: Conditions
    effect: Effect
