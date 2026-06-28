---
name: model-router
description: Resolve the model tier for an agent via the 5-layer precedence chain (pin > per-agent > cap > project > global), then look up the canonical id in `model_catalog.yaml`.
---

# model-router

## Purpose

Resolve which model an agent actually uses when rendered to a runtime. The
5-layer precedence makes the most specific declaration always win, so a
per-agent pin overrides a project default. This prevents silent model drift
and enforces R-007 (pinned models — every agent declares an explicit tier).

## When to use

- When rendering an agent to a runtime (build / commit / sync).
- When changing model configuration (`models.yaml`, `agent-models.yaml`,
  `project.yaml`, capability maps).
- When diagnosing "why is this agent using model X?".
- During a model-routing audit or any R-008 territory review.

## Procedure

Walk the chain from least specific to most specific — the first hit wins:

1. **Layer 6 — Global tier default** from `.aspis/config/models.yaml`
   (cheap / standard / deep → canonical id).
2. **Layer 5 — Project tier** from `project.yaml` (overrides the global default).
3. **Layer 4 — Per-capability mapping** from
   `policy/capabilities.yaml` (e.g. "reasoning tasks → standard").
4. **Layer 3 — Per-(runtime, capability) mapping** — runtime-specific capability
   override (e.g. "on `opencode`, reasoning → deep").
5. **Layer 2 — Per-agent pin** from `agent-models.yaml` (overrides capability
   defaults for one named agent).
6. **Layer 1 — Per-(runtime, agent) pin** — the most specific layer; always
   wins over Layer 2.
7. **Resolve the canonical id** for the selected tier + runtime from
   `model_catalog.yaml` (D-016: models defined once, by provider-neutral id).
8. **R-008 gate check** — if the resolution crosses a tier boundary
   (cheap → frontier), modifies a security-sensitive lead's model, or changes
   a global tier default, halt and require human approval via
   `aspis governance request` before applying. See `governance-approval` skill.

The agent's own frontmatter `model:` tier is the **declared** tier (R-007) — the
resolver compares it to the resolved tier and flags any drift.

## Outputs

- The resolved model id (canonical) for the (agent, runtime) pair.
- The **layer that determined it** (1–6) — logged for audit and drift detection.
- Any R-008 gate findings (tier crossing, security-sensitive change, global
  default change) — these block the change until approved.

## Anti-patterns

- **Silent inheritance** — resolving without logging which layer won. The
  audit trail is the point; "it just works" is a bug.
- **Skipping the R-008 gate** on tier changes. Tier escalation, security-lead
  model changes, and global default changes are human-gated — always.
- **Hard-coding a single resolution path** (e.g. always reading the agent pin)
  instead of walking all 5 layers. Specificity is the whole contract.
- **Guessing the model id** — never resolve without consulting
  `model_catalog.yaml`. Stale or fabricated ids break adapters and audits.
- **Editing a rendered runtime agent** (`.opencode/`, `.claude/`) to change a
  model. Change the data (`agent-models.yaml`, `models.yaml`) and run
  `aspis models --sync --apply`. See `config-management` skill.
