---
name: deterministic-first
description: Use to decide what to build for a new need — choosing the cheapest mechanism that solves it (deterministic code before an agent, an agent before a skill, and so on) so the system stays fast, testable, and free of unnecessary agents.
---

# Deterministic-First

## Purpose

Pick the right mechanism for a need. Agent-first design becomes slow, expensive,
and unreliable; deterministic-first keeps the system cheap and testable. This is
the System Lead's core judgment.

## When to use

Whenever a new capability or fix is needed, before any authoring.

## Procedure

Walk the ladder and stop at the first rung that solves the need:

1. **Deterministic code?** Can a script, tool, or hook do it without an LLM?
   Build that — it is faster, cheaper, and testable.
2. **Agent?** Only if the need genuinely requires reasoning, add an agent with a
   thin instruction.
3. **Skill?** If the agent needs reusable procedure/knowledge, add a skill.
4. **Template?** If it needs structured output (especially for a cheap model),
   add a template.
5. **Workflow?** If a multi-step process repeats, capture it as a workflow.

Justify the rung you stop at. Prefer a hook + script over asking an agent to
remember repetitive steps.

## Outputs

- The chosen mechanism and one-line justification.
- What to build (and what *not* to build yet).

## Anti-patterns

- Reaching for an agent when a script would do.
- Building a skill/template/workflow before the agent that needs it exists.
- Pre-building mechanisms "for later" — build by facing the real need.
