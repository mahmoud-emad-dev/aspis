---
name: context-packaging
description: Use to build the delegation packet that travels with a handed-off task — intent, scoped context, constraints, file references, and expected outcome — so a lead starts with everything it needs and nothing it doesn't.
---

# Context Packaging

## Purpose

Give a delegated lead exactly the context it needs to act, drawn from real project
state. This is the highest-leverage thing the Project Lead does: good packets make
delegation reliable; raw forwarding makes it fail.

## When to use

Whenever you delegate a request to a lead.

## Procedure

1. **Intent** — one sentence: the outcome wanted.
2. **Context** — the few facts from `project-awareness` the lead needs (active
   feature, current state, relevant history).
3. **Constraints** — scope boundaries, standards, rules in play, approval status.
4. **References** — the specific files, found via `.asps/index/FILE_REGISTRY.yaml`
   (paths, not pasted contents).
5. **Expected outcome** — what "done" looks like for this delegation.

Assemble these into one packet. Never forward the user's raw message.

## Outputs

A delegation packet: intent · context · constraints · references · expected outcome.

## Anti-patterns

- Forwarding the raw request instead of a packet.
- Dumping whole files instead of referencing paths.
- Over-packing context the lead will gather itself, or under-specifying the outcome.
