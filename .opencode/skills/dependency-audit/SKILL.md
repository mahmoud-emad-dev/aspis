---
name: dependency-audit
description: Audit a plan's task dependency graph for structural integrity — circular dependencies, missing prerequisites, orphan tasks, and dependency classification (hard/soft/warning). Produces a pass/warn/fail audit report per dependency so planners catch graph errors before build starts.
---

# Dependency Audit

## Purpose

Validate that a feature's task dependency graph is structurally sound before any
task is assigned. Catch circular chains (T-A depends on T-B depends on T-A),
missing prerequisites (a task references a dependency not listed in TASKS.md),
orphan tasks (no predecessor and not a deliverable), and misclassified
dependencies (hard vs. soft) — the graph-level errors that make a plan
unbuildable regardless of individual task quality.

## When to use

- During plan review (P7), after task decomposition completes and before the plan
  is handed to build.
- When a feature has ≥3 tasks with inter-task dependencies.
- When a build stalls because a task's prerequisite never ran — retroactively
  audit the graph to find the gap.
- When merging two feature plans and cross-feature dependencies need validation.

## Procedure

### Phase 1 — Build the dependency graph

1. Parse every task in `TASKS.md` — capture each task ID, its `Depends on:`
   list, and its `Blocks:` list. Use `.aspis/scripts/planning/dependency_graph.py`
   if available (R-003: deterministic-first); fall back to manual extraction.
2. Separate dependency annotations by class:
   - **Hard** (`[hard]`) — the task **cannot start** until its dependency completes.
   - **Soft** (`[soft]`) — recommended ordering but the task **can start** without
     it (higher rework risk).
   - **Warning** (unannotated) — presumed hard per the default rule, but the
     lack of explicit annotation is itself a warning.

### Phase 2 — Structural checks

3. **Circular-dependency check.** Walk the hard-dependency graph. For every task
   T, traverse its transitive hard dependencies. If T appears in its own
   transitive closure, flag a circular chain and report the full cycle path
   (e.g. `T-003 → T-004 → T-005 → T-003`). Every cycle blocks the plan.

4. **Missing-prerequisite check.** For every dependency reference in a task's
   `Depends on:` list, confirm the referenced task ID actually appears as a task
   in `TASKS.md`. Flag any reference to an unlisted task. A dependency on a task
   from another feature is valid only if the cross-feature dependency is
   documented; otherwise, flag it as missing.

5. **Orphan check.** Find every task that has **no** task depending on it (not
   in any other task's `Depends on:` or `Blocks:` list) AND is not a final
   deliverable (not the last task in the plan, not referenced in acceptance
   criteria). Flag as a potential orphan — the task either needs a consumer or
   is wasted work.

6. **Unreachable check.** Starting from tasks with zero hard dependencies (entry
   points), walk forward through `Blocks:` edges. Any task not reachable from an
   entry point is flagged as unreachable — it sits outside the execution DAG.

### Phase 3 — Dependency classification audit

7. For every dependency, verify the annotation matches reality:
   - If `Depends on: T-XXX [soft]` but T-XXX produces an artifact needed at
     build time (not just review/validate), escalate to `[hard]`.
   - If `Depends on: T-XXX [hard]` but the dependency is only a review or
     quality gate that could run in parallel, recommend `[soft]`.
   - Flag any unannotated dependency and recommend making the class explicit.

### Phase 4 — Cross-feature dependency audit (multi-feature plans only)

8. If the audit covers multiple features, build the cross-feature adjacency list
   and repeat phases 2-3 at the inter-feature level. Flag any undocumented
   cross-feature hard dependency as a structural risk.

### Phase 5 — Produce the audit report

9. Assemble findings into a structured audit report (see Outputs). Every finding
   gets a severity: **BLOCKER** (circular, missing hard dep), **WARN** (orphan,
   unreachable, soft-where-hard), **INFO** (unannotated dep, cross-feature
   reference).

10. Annotate the dependency graph with the audit result per edge — `PASS`,
    `WARN (orphan)`, `FAIL (circular: cycle T-003→T-004→T-003)` — so the planner
    can see exactly which dependencies need attention.

## Outputs

An audit report in one of two formats:

**Inline (attached to plan review):**

```
## Dependency Audit Report
- Feature: <F-NNN>
- Tasks audited: N
- Hard dependencies: N
- Circular: 0 (PASS)
- Missing prerequisites: 0 (PASS)
- Orphans: 2 (WARN — T-007, T-012)
- Unreachable: 0 (PASS)
- Unannotated: 3 (INFO — add [hard] or [soft] to T-003→T-004, T-005→T-006, T-008→T-009)
- Cross-feature refs: 1 (INFO — T-015 depends on F-019/T-002; document cross-feature contract)
- Verdict: PASS with 2 warnings (no blockers)
```

**Full report (standalone file):**

A per-dependency table with columns: Task | Depends on | Class | Audit result |
Evidence, followed by the summary above, followed by recommendations.

## Anti-patterns

- **Skipping the audit for small plans.** Even a 3-task sequence can have a
  circular dependency if the planner misannotated. The cost of a missed cycle
  is a blocked build; the cost of the audit is a script run.
- **Treating orphans as always wrong.** Some tasks are final deliverables with
  no downstream consumer — verify they appear in the acceptance criteria before
  flagging. Don't flag the last task in the plan as orphan.
- **Assuming cross-feature deps are safe.** A `[hard]` dependency on a
  different feature's task that hasn't been built yet is a schedule risk, not
  just a graph edge. Flag these and recommend a cross-feature contract.
- **Auditing without the actual TASKS.md.** Parsing a mental model of the graph
  instead of the source file produces reports that don't match reality. Always
  parse the source.
- **Relying on the audit to fix graph errors.** The audit detects; it does not
  fix. The planner owns the correction — the audit report is evidence for the
  reviewer, not an auto-fix tool.
