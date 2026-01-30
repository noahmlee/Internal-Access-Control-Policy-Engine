"""CLI for policy validation and evaluation."""

import argparse
import json
import sys
from pathlib import Path

from validation.policy_validator import validate_policy_semantics
from validation.schema import Policy

from engine import evaluate_policies_decision, evaluate_policy_decision


def _load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _load_yaml(path: Path) -> dict:
    try:
        import yaml
    except ImportError:
        sys.exit(
            "PyYAML is required for YAML policy files. Install with: pip install pyyaml"
        )
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_policy(path: Path) -> dict:
    suffix = path.suffix.lower()
    if suffix in (".yaml", ".yml"):
        return _load_yaml(path)
    if suffix == ".json":
        return _load_json(path)
    sys.exit(
        f"Unsupported policy file format: {path.suffix}. Use .json, .yaml, or .yml"
    )


def load_context(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def cmd_validate(args: argparse.Namespace) -> int:
    path = Path(args.policy)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1
    try:
        data = load_policy(path)
        policy = Policy(**data)
        validate_policy_semantics(policy)
        print(f"OK: {path}")
        return 0
    except Exception as e:
        print(f"Validation failed: {e}", file=sys.stderr)
        return 1


def cmd_evaluate(args: argparse.Namespace) -> int:
    policy_path = Path(args.policy)
    context_path = Path(args.context)
    if not policy_path.exists():
        print(f"Error: policy file not found: {policy_path}", file=sys.stderr)
        return 1
    if not context_path.exists():
        print(f"Error: context file not found: {context_path}", file=sys.stderr)
        return 1
    try:
        policy_data = load_policy(policy_path)
        context = load_context(context_path)
        policy = Policy(**policy_data)
        validate_policy_semantics(policy)
        result = evaluate_policy_decision(policy, context)
        print(result.decision)
        if args.trace:
            for entry in result.trace:
                print(f"  {entry.kind}: ok={entry.ok} {entry.detail or ''}".strip())
        return 0
    except Exception as e:
        print(f"Evaluation failed: {e}", file=sys.stderr)
        return 1


def cmd_evaluate_multi(args: argparse.Namespace) -> int:
    context_path = Path(args.context)
    if not context_path.exists():
        print(f"Error: context file not found: {context_path}", file=sys.stderr)
        return 1
    policies = []
    for p in args.policies:
        path = Path(p)
        if not path.exists():
            print(f"Error: policy file not found: {path}", file=sys.stderr)
            return 1
        policy_data = load_policy(path)
        policies.append(Policy(**policy_data))
    try:
        context = load_context(context_path)
        for policy in policies:
            validate_policy_semantics(policy)
        result = evaluate_policies_decision(policies, context)
        print(result.decision)
        if args.trace:
            for entry in result.trace:
                print(f"  {entry.kind}: ok={entry.ok} {entry.detail or ''}".strip())
        return 0
    except Exception as e:
        print(f"Evaluation failed: {e}", file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="ace",
        description="Access Control Engine: validate and evaluate policies.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate a policy file")
    validate_parser.add_argument(
        "policy", help="Path to policy file (.json, .yaml, .yml)"
    )
    validate_parser.set_defaults(func=cmd_validate)

    evaluate_parser = subparsers.add_parser(
        "evaluate", help="Evaluate one policy against a context"
    )
    evaluate_parser.add_argument("policy", help="Path to policy file")
    evaluate_parser.add_argument("context", help="Path to context file (.json)")
    evaluate_parser.add_argument(
        "-t", "--trace", action="store_true", help="Print evaluation trace"
    )
    evaluate_parser.set_defaults(func=cmd_evaluate)

    multi_parser = subparsers.add_parser(
        "evaluate-policies",
        help="Evaluate multiple policies (deny-overrides) against a context",
    )
    multi_parser.add_argument(
        "policies",
        nargs="+",
        help="Paths to policy files",
    )
    multi_parser.add_argument("context", help="Path to context file (.json)")
    multi_parser.add_argument(
        "-t", "--trace", action="store_true", help="Print evaluation trace"
    )
    multi_parser.set_defaults(func=cmd_evaluate_multi)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
