---
name: test-generation
description: Use to design tests that genuinely exercise a behavior — happy path, edge cases, and failure modes — at the right level (unit, integration). Produces tests that would catch real defects, not tests that merely pass.
---

# Test Generation

## Purpose

Write tests that prove behavior and catch regressions. A test suite is only worth
its ability to fail when something is wrong — this skill targets the cases that
actually matter.

## When to use

When validating a new behavior, a feature, or a fix that needs regression coverage.

## Procedure

1. **Identify the contract.** What the code must do, its inputs/outputs, and the
   acceptance criteria it's measured against.
2. **Cover the cases.** Happy path, boundaries and edge cases, invalid input, and
   failure modes — not just the obvious success.
3. **Choose the level.** Unit tests for logic in isolation; integration tests where
   components meet. Prefer the cheapest level that proves the behavior.
4. **Add invariants** where they apply — properties that must hold for all inputs
   (round-trip, idempotence, ordering).
5. **Keep tests honest.** Each asserts real behavior and would fail if the behavior
   broke; no tautologies or assertions of the implementation's own output.

## Outputs

- Tests covering the behavior's success, edge, and failure cases at the right level.

## Anti-patterns

- Happy-path-only tests that miss edge and failure cases.
- Tests written to pass rather than to detect breakage.
- Over-mocking until the test no longer exercises real behavior.
