# ASPIS System Rules

The non-negotiable rules for how the agentic system itself operates. They are
referenced by ID (R-001…) across agents and skills, and stated **once** here —
agents cite them, they do not restate them.

## The three rule layers

Rules live in three scopes; an agent loads only the layer relevant to its work,
never all of them at once. The System Lead governs how they fit together.

- **System rules (this file).** How the agentic system works. Ship with every
  project; apply to every lead and worker. Stable; changed only by human gate (R-008).
- **Project rules** (`.aspis/rules/project-rules.md`, authored per project). The
  source of truth for *one* project — its stack, conventions, and constraints.
  The planning and build leads follow them.
- **User rules** (the user's own global file). Everything the user has learned —
  style, stack preferences, testing, review, patterns — written once, across
  projects. The System Lead reads it, validates each rule, and extracts the subset
  relevant to a project into that project's rules. Invalid or not-yet-applicable
  entries are carried but not enforced; only valid rules take effect.

Precedence when they conflict: a valid user rule overrides a project default;
system rules are never overridden — they bound what the others may do.

## Rules

### R-001 Scope
Change only the files your task or role allows. Never touch forbidden paths or secrets.

### R-002 Gates first
Run the deterministic gates (format, lint, types, tests) before declaring work
done or asking for review. A failing gate is a finding, not a nuisance.

### R-003 Deterministic-first
Solve a need with the cheapest mechanism that works, in order: deterministic
code/script/hook → agent → skill → template → workflow. Build what is needed when
it is needed — never a speculative org chart of agents.

### R-004 One writer
One writer per branch. Reviewers are read-only. Only the committer creates commits;
no agent commits its own work.

### R-005 Tests-as-spec
Tests are part of the specification. Behaviour changes need tests; fixes need a
regression test. Never weaken or delete a test to make a gate pass.

### R-006 Thin agents, single source
An agent instruction holds identity, rules, and skill references; the intelligence
lives in skills. State each fact once and reference it — don't duplicate rules,
procedures, or assets.

### R-007 Pinned models
Every agent declares an explicit model tier (cheap / standard / deep). No agent
silently inherits an expensive model.

### R-008 Human gate
Architecture, rules, permissions, security posture, and model-routing changes
require human approval — never an automated rewrite.

### R-009 Trace and learn
Important work leaves a traceable record (commits, reports, events and more later). When a stronger
check catches a weaker one's miss, capture the lesson so the same mistake isn't
repeated.
