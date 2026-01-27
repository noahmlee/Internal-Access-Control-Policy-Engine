from enum import Enum
from typing import Any, List, Optional
from pydantic import BaseModel, Field, root_validator

# Schema definitions derived from docs/policy_contract.md

class Effect(str, Enum):
    # Defines the outcome of a policy when all conditions are satisfied.
    ALLOW = "ALLOW"
    DENY = "DENY"
    
class Target(BaseModel):
    # Defines what a policy applies to.
    # Policies whose targets do not match a request are not evaluated.
    resource_type: str = Field(..., description="Type of the target resource")
    environment: str = Field(..., description="Environment (e.g. prod, staging)")
    
class Condition(BaseModel):
    # A single boolean expression evaluated against the request context.
    field: str = Field(
        ...,
        description="Dotted path into the request context (e.g. user.role)"
    )
    operator: str = Field(
        ...,
        description="Symbolic operator name (validated separately)"
    )
    value: Any = Field(
        None,
        description="Comparison value (operator-dependent)"
    )
    
class Conditions(BaseModel):
    # Logical grouping of conditions.
    # Exactly one of 'all' or 'any' must be defined.
    all: Optional[List[Condition]] = None
    any: Optional[List[Condition]] = None
    
    @root_validator
    def validate_condition_group(cls, values):
        all_conditions = values.get("all")
        any_conditions = values.get("any")
        
        if all_conditions and any_conditions:
            raise ValueError("Only one of 'all' or 'any' may be defined")
        
        if not all_conditions and not any_conditions:
            raise ValueError("One of 'all' or 'any' must be defined")
        
        return values
    
class Policy(BaseModel):
    # A declarative access control policy.
    policy_id: str = Field(
        ...,
        description="Globally unique, versioned policy identifier"
    )
    description: Optional[str] = Field(
        None,
        description="Human-readable description of the policy intent"
    )
    target: Target
    conditions: Conditions
    effect: Effect