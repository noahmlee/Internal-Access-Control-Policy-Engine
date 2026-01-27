# Policy Contract - Access Control Engine

## Purpose

An access control policy defines when a user is allowed or denied permission to perform an action on a resource within a given context.

Policies are **declarative**, and **deterministic**.

---

## Core Principles

1. Policies do not execute code

- Policies describe intent, not behavior.

2. Policies are evaluated deterministically

- Given the same input, a policy always produces the same result.

3. Policies must be explainable

- Every decision must include a human-readable explanation.

4. Policies are safe by construction

- Invalid or ambiguous policies are rejected before execution.

---

## Policy Responsibilities

A policy answers **one question**:

> "Does this request meet the criteria for this decision?"

A policy **does not**:

- mutate state
- call external services
- depend on time unless explicitly provided in context
- infer missing data

---

## Policy Structure

Each policy consists of four parts:

1. Identity

- A globally unique, versioned identifier
- Used for auditing, debugging, and traceability
  Example:
  > `admin_write_access_v1`

2. Target

- Defines what the policy applies to
- Targets are used to quickly exclude policies that are irrelevant to a request
  Examples:
- resource type
- environment
- application domain
  **If a policy's target does not match the request, the policy is not evaluated further.**

3. Conditions

- Defines when a policy applies
- Conditions are evaluated against request data
- Conditions are combined using logical ALL or ANY
- Each condition must be independently evaluatable
  Examples:
- user.role equals admin
- action in [write, delete]
- context.mfa_verified is true
  In documentation, condition evaluation may be represented as:
  > `action in [write, delete] => true`

4. Effect

- Defines the outcome when all conditions are satisfied
  Allowed effects:
- `ALLOW`
- `DENY`
  There are **no** implicit defaults
  If no policy applies, the decision is `NOT_APPLICABLE`

---

## Evaluation Guarantees

When a policy is evaluated:

- All inputs must be explicitly provided
- Missing fields cause a validation failure
- Unsupported operators are rejected
- The engine produces:
  - a decision
  - the policy that produced it
  - an evaluation trace

---

## Non-Goals / Explicitly Out of Scope

This system does **not**:

- Resolve identity
- Authenticate users
- Enforce permissions directly
- Replace external IAM systems

It is a **decision engine**, not and enforcement mechanism.

---

## Why This Contract Exists

This contract ensures that:

- policies can be authored safely
- policies can be reviewed by non-engineers
- behavior is predictable across enviornments
- future developers can extend the system without breaking invariants
