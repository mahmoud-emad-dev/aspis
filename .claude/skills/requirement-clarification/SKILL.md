---
name: requirement-clarification
description: Use after intake to turn a vague request into a solid basis for planning — gather project context, resolve assumptions from existing conventions, and surface only the few clarifications that genuinely block or shape the work. Maximize information gain while minimizing interruption.
---

# Requirement Clarification

## Purpose

Replace guesswork with evidence before planning, while respecting the user's time.
Most gaps can be closed from the project itself; only the decisions that truly
need a human should reach one.

## When to use

After `planning-intake`, before writing the spec — whenever the request leaves
material questions open.

## Procedure

1. **Gather context.** Read project state, relevant code, existing plans, and prior
   decisions (delegate the search to `project-explorer` when broad).
2. **Resolve from convention.** Settle stack, patterns, and defaults from how the
   project already works — record these as explicit assumptions, not questions.
3. **Identify research needs.** If a real unknown needs external docs or facts,
   request it from the Research Lead; don't research it yourself.
4. **Prioritize what's left.** Rank open items: **critical** (blocks planning),
   **important** (shapes implementation), **optional** (quality only).
5. **Ask minimally.** Put the critical (and key important) questions to the user;
   carry the rest as assumptions. Don't ask what you can resolve.

## Outputs

- A list of resolved assumptions and a short, prioritized set of open questions.

## Anti-patterns

- Asking questions the project already answers.
- Long questionnaires that bury the few decisions that matter.
- Becoming the researcher instead of requesting research.
- Planning on unstated assumptions that were never written down.
