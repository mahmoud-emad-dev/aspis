---
name: request-classification
description: Use to turn a raw user request into a single clear intent, its complexity, and a recommended path — the decision that drives whether to answer directly or which lead to route to.
---

# Request Classification

## Purpose

Understand what the user actually needs before acting, so routing and answering
are based on intent rather than surface wording.

## When to use

Immediately after reading the request, before deciding to answer or delegate.

## Procedure

1. Restate the request in one sentence — what outcome is wanted.
2. Pick exactly one primary type: `question`, `planning`, `build`, `review`,
   `fix`, `research`, `test`, `system`, or `mixed`.
3. Judge complexity (trivial / standard / involved) — enough to know whether it
   needs planning or research first.
4. Recommend a path: answer directly, or the lead and likely sequence to start.

## Outputs

- Intent (one sentence)
- Request type (one) and complexity
- Recommended path (answer, or starting lead + likely flow)

## Anti-patterns

- Classifying as two types at once — pick the primary one; mark genuinely blended
  work as `mixed` and name the parts.
- Reacting to wording instead of intent.
- Choosing a path before the intent is stated clearly.
