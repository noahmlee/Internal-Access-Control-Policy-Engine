from __future__ import annotations
from typing import Any
from engine.errors import ContextValidationError


def target_matches(target, context) -> bool:
    resource = context.get("resource")
    if not isinstance(resource, dict):
        raise ContextValidationError("context.resource is required")
    resource_type = resource.get("type")
    if resource_type is None:
        raise ContextValidationError("context.resource.type is required")

    environment = context.get("environment")
    if not isinstance(environment, dict):
        raise ContextValidationError("context.environment is required")
    env = environment.get("env")
    if env is None:
        raise ContextValidationError("context.environment.env is required")

    if target.resource_type != resource_type:
        return False

    if target.environment != env:
        return False

    return True