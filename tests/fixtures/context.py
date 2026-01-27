def base_context():
    return {
        "user": {"id": "1", "role": "admin"},
        "resource": {"type": "document"},
        "environment": {"env": "prod"},
    }