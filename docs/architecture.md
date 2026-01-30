## Architecture

This project is split into two concerns:

- **Validation**: reject unsafe or ambiguous policies before evaluation
- **Evaluation**: deterministically compute a decision from a policy + context

The guiding constraints live in `docs/policy_contract.md`.

## Components (high-level)

```mermaid
flowchart LR
  Caller[Application / Service] -->|policy + context| Schema[validation/schema.py\n(Pydantic models)]
  Schema --> Semantics[validation/policy_validator.py\n(semantic rules)]
  Semantics --> Evaluator[engine/evaluator.py]
  Evaluator --> Decision[engine/decision.py]
  Caller --> PolicySet[engine/policy_set.py]
  PolicySet --> Evaluator
  Evaluator --> Target[engine/target_matcher.py]
  Evaluator --> Ops[engine/operators.py]
  Evaluator -->|decision| Caller
```

## Module responsibilities

### `validation/schema.py`

Defines the **structural** policy contract using Pydantic models:
- `Policy` (id, description, target, conditions, effect)
- `Target` (resource_type, environment)
- `Conditions` (`all` xor `any`)
- `Condition` (field, operator, value)

This layer ensures policies are well-formed before deeper checks.

### `validation/policy_validator.py`

Implements **semantic validation** rules:
- operator is supported
- condition field paths are constrained to safe prefixes (`user.*`, `resource.*`, `request.*`)
- operator/value compatibility (e.g., `in` expects a list-like value, `gt` expects numeric)

### `engine/target_matcher.py`

Fast exclusion filter to avoid evaluating irrelevant policies:
- compares `target.resource_type` to `context["resource"]["type"]`
- compares `target.environment` to `context["environment"]["env"]`

If a policy target does not match, the evaluator returns `NOT_APPLICABLE`.

### `engine/operators.py`

Pure, deterministic operator functions used by evaluation:
- `equals(a, b)`
- `in(a, b)`
- `gt(a, b)`
- `lt(a, b)`

This is an extension point: add new operators here and register them in `OPERATORS`.

### `engine/evaluator.py`

Performs evaluation for a single policy:
- target match
- resolve dotted fields in the request context
- evaluate condition group (`all` or `any`)
- return a decision (`ALLOW`, `DENY`, or `NOT_APPLICABLE`), optionally as a structured object

### `engine/decision.py`

Defines structured decision outputs:
- `Decision` (decision, policy_id, reason, trace)
- `TraceEntry` (target and condition evaluation steps)

### `engine/policy_set.py`

Evaluates a set of policies against a single request context and applies a conflict strategy.

Currently implemented:
- `deny_overrides`: if any applicable policy yields `DENY`, overall decision is `DENY`; otherwise `ALLOW` if any allows; otherwise `NOT_APPLICABLE`

## Data shapes

### Policy shape

Policies are JSON/YAML-compatible data that map to `validation.schema.Policy`.

### Request context shape

The evaluator expects a dict with top-level keys:
- `user`
- `resource`
- `environment`

Condition fields refer to dotted paths like `user.role` and `environment.env`.

## Extension points

- **Add operators**: implement a function in `engine/operators.py`, add to `OPERATORS`, and update semantic rules in `validation/policy_validator.py`.
- **Add target fields**: extend `Target` in `validation/schema.py` and update `engine/target_matcher.py` accordingly.
- **Add richer decisions**: introduce a structured decision object that includes trace/explanation (per `docs/policy_contract.md`).
