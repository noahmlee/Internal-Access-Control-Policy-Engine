## Access Control Engine (Decision Engine)

A small, deterministic **policy decision engine** for authorization.

Given:
- a **policy** (target + conditions + effect)
- a **request context** (user/resource/environment data)

the engine returns a decision: `ALLOW`, `DENY`, or `NOT_APPLICABLE`.

This project is intentionally focused on **decisioning**, not identity/authentication or enforcement.

See the contract: `docs/policy_contract.md`.

## Quickstart

Create a virtual environment, install dependencies, run tests:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

Or install with dev tools (ruff, black, mypy, pytest-cov):

```bash
pip install -e ".[dev]"
pytest -q
```

## Development / CI

- **Lint**: `ruff check engine validation context cli tests`
- **Format**: `black engine validation context cli tests`
- **Type check**: `mypy engine validation cli`
- **Tests with coverage**: `pytest --cov=engine --cov=validation --cov-report=term`
- **Pre-commit**: `pre-commit install` then `pre-commit run --all-files`

GitHub Actions (`.github/workflows/ci.yml`) runs lint, format check, mypy, and pytest with coverage on each push.

## Minimal usage (library)

```python
from validation.schema import Policy
from validation.policy_validator import validate_policy_semantics
from engine import evaluate_policy_decision

policy_data = {
    "policy_id": "admin.document.prod.allow.v1",
    "description": "Admins can access documents in prod",
    "target": {"resource_type": "document", "environment": "prod"},
    "conditions": {
        "all": [
            {"field": "user.role", "operator": "equals", "value": "admin"},
        ]
    },
    "effect": "ALLOW",
}

context = {
    "user": {"id": "1", "role": "admin"},
    "resource": {"type": "document"},
    "environment": {"env": "prod"},
}

policy = Policy(**policy_data)         # structural validation
validate_policy_semantics(policy)      # semantic validation
result = evaluate_policy_decision(policy, context)

print(result.decision)    # "ALLOW"
print(result.policy_id)   # "admin.document.prod.allow.v1"
print(result.reason)      # "conditions satisfied"
print(result.trace)       # list of trace entries (target + condition evaluations)
```

## Evaluating multiple policies

```python
from engine import evaluate_policies_decision

policies = [Policy(**policy_data)]
result = evaluate_policies_decision(policies, context)
print(result.decision)
```

## Policy format

Policies are plain data (JSON/YAML-compatible). The schema is defined in `validation/schema.py`.

Example policy (YAML-style):

```yaml
policy_id: admin.document.prod.allow.v1
description: Admins can access documents in prod
target:
  resource_type: document
  environment: prod
conditions:
  all:
    - field: user.role
      operator: equals
      value: admin
effect: ALLOW
```

## Request context format

The engine expects a dict with at least these top-level keys:

```json
{
  "user": {"id": "1", "role": "admin"},
  "resource": {"type": "document"},
  "environment": {"env": "prod"}
}
```

Field references in conditions are dotted paths like `user.role` or `environment.env`.

## How evaluation works (high-level)

- If the **target does not match**, the engine returns `NOT_APPLICABLE`.
- Otherwise it evaluates the condition group:
  - `all`: every condition must be true
  - `any`: at least one condition must be true
- If conditions fail, decision is `DENY`.
- If conditions pass, decision is the policy `effect`.

More detail and diagrams are in:
- `docs/decision_flow.md`
- `docs/architecture.md`
- `docs/policy_lifecycle.md`

## Supported operators

Implemented in `engine/operators.py`:
- `equals`
- `in`
- `gt`
- `lt`

## Project structure

- `engine/`: policy evaluation (target matching + operators + evaluator)
- `validation/`: schema + semantic validation rules
- `docs/`: contract, architecture, evaluation flow, lifecycle
- `tests/`: unit tests and fixtures

## Current scope / limitations

- Evaluation supports **single-policy** and **multi-policy** (deny-overrides) via `evaluate_policies_decision(...)`.
- Missing required context fields raise `engine.errors.ContextValidationError`.

## Roadmap (next)

- Additional conflict strategies (priority, first-match, allow-overrides)
- CLI for validating/evaluating policies from files
- Packaging (`pyproject.toml`) + CI (GitHub Actions)
