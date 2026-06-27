---
type: template
category: planning
version: 1.0
---

# Plan of Plan — <feature-id>

> The meta-plan: how the planning phase itself will be executed. Produced as the
> first planning artifact (P0 output), before any spec or architecture work.
> Prevents planning from drifting into unbounded exploration.

---

## Scope boundary

<What the plan covers and what it deliberately excludes. One paragraph max.
Reference the intake request or feature trigger.>

## Stakeholders

- **Requester**: <Who asked for this feature / who owns the need.>
- **Planner**: <planning-lead (default) or delegated subagent.>
- **Reviewer**: <Who reviews the plan — reviewer, project-lead, or both.>
- **Approver**: <Who gives the final go/no-go on the plan.>

## Dependencies to resolve first

<List knowledge gaps, decisions, or external inputs that MUST be resolved before
planning can proceed. Each item names the dependency and who owns resolving it.>

1. <Dependency> — owner: <role or person>
2. ...

## Risk assessment

| Risk | Likelihood (L/M/H) | Impact (L/M/H) | Mitigation |
|------|--------------------|----------------|------------|
| <Risk description> | L | M | <How the plan handles it.> |
| ... | | | |

## Timebox

- **Planning start**: <YYYY-MM-DD>
- **Planning target**: <YYYY-MM-DD>
- **Hard deadline**: <YYYY-MM-DD or "none — next planning session">
- **Mode**: <vibe / mvp / production>
- **Effort budget**: <e.g. "1 planning session (~2 hours)" or "3 sessions max">

## Outputs expected

| Artifact | Path | Depth | Owner |
|----------|------|-------|-------|
| SPEC.md | `.aspis/features/<id>/SPEC.md` | <production/mvp/vibe> | planning-lead |
| PLAN.md | `.aspis/features/<id>/PLAN.md` | <depth> | planning-lead |
| TASKS.md | `.aspis/features/<id>/TASKS.md` | <depth> | task-decomposer |
| CLARIFICATION_LOG.md | `.aspis/features/<id>/Clarifications/` | <depth> | clarify |
| ... | | | |

## Checkpoints

<Hard stops during planning — gates that must pass before the next phase:>

1. **Intake classified** — track + mode selected; scope boundary set.
2. **Clarifications resolved** — all NEEDS CLARIFICATION items answered or
   deferred with owner.
3. **Architecture reviewed** — constitution check passes (or deviations
   documented + approved).
4. **Tasks compiled** — task_compile.py exits 0; prereq_validate.py exits 0.
5. **Plan review passed** — reviewer or project-lead signs off.
