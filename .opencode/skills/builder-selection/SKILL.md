---
name: builder-selection
description: Pick the right builder tier (cheap/standard/deep) per packet version (V0–V4) and risk profile.
---

# builder-selection

## Purpose
Match each task packet to the right builder tier — the cheapest model that can
execute it at the required quality — so the build-lead routes work efficiently
without burning deep-model budget on trivial tasks or sending critical work to
cheap models.

## When to use
- After packet validation, before delegating a task to a builder.
- When a builder fails and the build-lead re-assigns the task.
- When the mode or risk profile of a task changes mid-build.

## Selection matrix

| Packet version | Risk | Default tier | Rationale |
|---|---|---|---|
| V0 (vibe) | Low | `cheap` | The model just needs to follow simple instructions |
| V1 (mvp) | Low–Medium | `cheap` | Standard task; cheap model with full scaffolding handles it |
| V2 (production, small) | Medium | `standard` | Production quality needs a model with more consistency |
| V3 (production, cross-cutting) | Medium–High | `standard` | Cross-cutting work needs awareness; still standard-tier |
| V4 (production, critical/security) | High | `deep` | Security or critical path — pay for the best model |

## Override rules

The base tier from the matrix can be overridden by:

### Escalate one tier when:
- The task touches a **protected path** (`.opencode/`, `.claude/`, `rules/**`)
- The task has a **security dimension** (auth, secrets, input validation, data
  handling)
- The task is **cross-cutting** (touches 5+ files or multiple components)
- The task is the **first of its kind** (new patterns the model hasn't seen)

### Downgrade one tier when:
- The task is a **pure refactor** (no behaviour change, tests already exist)
- The task is a **known pattern** the project has executed successfully before
  on a cheaper model
- The packet is **exceptionally well-specified** (full skeleton, exact steps,
  no ambiguity)

### Hard floor:
- Never downgrade below `cheap`
- Never downgrade a V4 packet below `standard`
- Never downgrade a task with a `HIGH` criticality rating

## Tier cascade on failure

If the assigned builder fails (exceeds turn cap, produces incorrect output, or
can't complete the task):

1. **Same tier, focused**: give the same tier a narrower, more explicit packet.
2. **Escalate one tier**: if the focused attempt fails, escalate to the next tier
   with a broader packet.
3. **STOP at 3 attempts**: after 3 total attempts (assigned + focused + escalated),
   write REVIEW_NEEDED and escalate to the project-lead. Do not keep trying.

## Procedure
1. **Read the packet** — extract version (V0–V4), criticality, and risk signals.
2. **Check the matrix** — get the base tier.
3. **Apply overrides** — escalate or downgrade based on task characteristics.
4. **Set the tier** in the enriched packet's Identity section (`Mode / model tier`
   field).
5. **Record the rationale** — why this tier for this task (e.g. "V2 matrix default,
   escalated to deep for security dimension").

## Outputs
- The selected builder tier (`cheap` / `standard` / `deep`).
- The rationale for the selection.
- Updated packet with tier recorded.

## Anti-patterns
- Always using `deep` "just to be safe" — burns budget, violates R-007 (pinned
  models), and drags a deep model through cheap-model ceremony.
- Always using `cheap` to save money — V4 security tasks on cheap models produce
  dangerous output.
- Re-assigning to the same tier without changing the packet — if the builder
  failed, the packet or the tier is wrong; fix one before retrying.
- Selecting tier before validating the packet — a bad packet wastes any tier.
