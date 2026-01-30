def valid_policy():
    return {
        "policy_id": "test.policy.v1",
        "target": {
            "resource_type": "document",
            "environment": "prod"
        },
        "conditions": {
            "all": [
                {
                    "field": "user.role",
                    "operator": "equals",
                    "value": "admin"
                }
            ]
        },
        "effect": "ALLOW"
    }
