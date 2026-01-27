def target_matches(target, context) -> bool:
    """
    Returns True if the policy target matches the request context.
    """
    if target.resource_type != context["resource"]["type"]:
        return False

    if target.environment != context["environment"]["env"]:
        return False

    return True