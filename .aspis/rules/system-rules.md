# ASPIS System Rules

The non-negotiable rules for how the agentic system itself operates. They are
referenced by ID (R-001…) across agents and skills, and stated **once** here —
agents cite them, they do not restate them.

## What this file governs

**System rules govern how the agentic system — the agents — operate. They do NOT
dictate how a project's product is designed** (that is the Constitution, below).
They ship with every project and apply to every lead and worker; the ASPIS repo
may also keep repo-internal system rules that are not exported (marked
`internal`). Stable; changed only by human gate (R-008), and never overridden by
project or user rules — they are the safety floor.

## The rule layers

Rules live in four layers across two axes. An agent loads only the rules relevant
to its role and task, never all of them at once. The System Lead governs how they
fit together.

**Operating the agent machine (internal):**
- **System rules (this file).** How the agents operate: scope, gates, one-writer,
  tests, thin agents, pinned models, human gate, trace, delegate-with-purpose.

**Building the project's product (what most users care about):**
- **Global Constitution** (`architecture-constitution.md`). The global default
  design standard for *any* project and domain — software, data analysis/science,
  automation, web, research. The default until a project sets its own rules.
- **Project rules** (`project-rules.md`, per project). The one project's
  conventions — the **highest priority** for product work. Set by the active
  profile, by the user, or proposed by the system; changeable while the project
  runs (user directly, or project-lead → System Lead).
- **User rules** (the user's global file — *future feature*). What the user has
  learned across projects. The System Lead validates each and extracts the subset
  relevant to a project into that project's rules. Invalid or not-yet-applicable
  entries are carried but not enforced.

**Precedence.** For product work: **project rules first, then the Constitution.**
User rules feed into project rules. System rules sit on a separate axis and are
never overridden — they bound what the others may do.

**How an agent gets its rules.** An agent cites the system rules it must honour by
ID (briefly, in its instruction body — R-006). The product/project rules it needs
are loaded from `project-rules.md` by the **section/tag for its role**, through its
context step — so each agent reads only its own subset, never the whole file.

## Applying these rules — practice over theory

These rules exist to produce one outcome: a system that is **cheap to change and
safe to run**. They are the means, never the goal. Apply them with judgment, not
as a checklist:

- **Apply a rule where it improves the work; don't apply it where it would force
  an illogical, impractical, or lower-value result.** A rule that makes a
  specific case worse is a signal to question the application — raise it under
  R-008 — not to comply mechanically.
- **Only the rules a role actually owns apply to it.** An agent, spec, or file is
  not defective for "missing" a rule it does not own (see the three layers and
  `config/constitution-checks.yaml`). The absence of a box-ticking section is not,
  by itself, a defect.
- **A real defect is concrete:** it raises cost-of-change, breaks a gate, creates
  a wrong/unsafe behaviour, or makes the system harder to understand, change, or
  run. Judge every finding by that test. Conformance for its own sake is not a
  defect to fix.
- **When a rule and reality genuinely conflict, fix the rule or narrow its scope —
  don't bend reality to fit the rule.** These rules are a living working guide,
  not a fixed theory. When in doubt, optimise for the working system.

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
Important work leaves a traceable record (commits, reports). When a stronger
check catches a weaker one's miss, capture the lesson so the same mistake isn't
repeated.

### R-010 Delegate with purpose
A lead pushes mechanical and context-heavy work to a cheap, scoped subagent and
keeps its own (higher) model for judgment and critical review. Don't delegate
trivial work that costs more to hand off than to do; don't fill the lead's context
with raw tool output a subagent can digest into a summary.
