# Planning-Lead Quality and Rules Reference

> **Author:** Research Lead
> **Date:** 2026-06-26
> **Status:** Authoritative reference. The single document planning-lead consults
> to design, gate-check, and rank any plan. Synthesised from
> `architecture-constitution.md`, `system-rules.md`,
> `AGENT-SYSTEM-ARCHITECTURE.md`, `core-loops-2026.md`, and the planning-lead
> agent files (both opencode and local). Cite by section ID (`§1.2`,
> `§2.matrix-R03`, etc.) when a plan or review references it.
> **Rule of the doc:** the cheap model does production-grade work when the
> non-model factors — task clarity, test strength, review discipline, and
> deterministic gates — are in place. This reference is the leverage.

---

## 0. How to use this document

Planning-lead never starts blank. Before any planning work, walk this ladder:

1. **Read mode** (vibe / MVP / production) from `modes.yaml` via
   `planning-intake` — the mode is the single dial that tunes every other rule
   in this document.
2. **Apply §1 (Principles)** — design with these in mind; the plan-critic
   checks against them.
3. **Apply §2 (Rules matrix)** — the per-mode column tells you what is
   enforced, what is relaxed, and what is skipped.
4. **Hold §3 (Always-apply standards)** — these never relax; they are the
   cheap-model bet.
5. **Pin the model tier via §4** — wrong tier is a cost or quality bug.
6. **Read project + user rules via §5** — system rules bound; the rest are
   scoped.
7. **Refuse any plan that triggers §6 (Anti-patterns)** — these are provably
   wrong, not opinion.

If a planning decision is not addressed by this document, escalate — do not
invent. (R-001 scope; "if stuck, stop — don't guess.")

---

# 1. Quality Principles for Planning

Each principle has a **purpose**, an **application** to planning, and a
**check** the plan-critic runs. The principles compose; the cheapest design
satisfies all eight.

## 1.1 Abstraction — how to design extensible architectures

**Purpose.** Make the next feature of this shape a new file, not an edit to
the core. The Constitution calls this **Plugin First · Local Change** (rules
2, 1).

**Apply during planning.**
- For every new capability the plan introduces, ask: *is this a plugin, an
  asset, a config row, or an edit to the core?* The first three win.
- Identify the **extension seam** before naming the concrete instances. If
  the plan says "add Python support," ask first "what does the runtime
  contract look like for any language adapter?" and only then "and here is
  the Python adapter."
- If the plan modifies a file that other features also modify, that file is
  not the right home — find the seam.

**Check.** Run the Cost-of-Change test against the plan: *to add the *next*
feature of this shape, how many existing files must change?* Target 1–3.

## 1.2 Maintainability — how the plan produces maintainable code

**Purpose.** Low cost of change over the lifetime of the system. The
Constitution's north star: *things that change together live together; things
that change independently stay apart.*

**Apply during planning.**
- **Co-locate** logic that changes for the same reason. A function and its
  test, a rule and its checker, an agent and its skill — together.
- **Separate** logic that changes for different reasons. A formatter and a
  test runner live in different files even if both touch output text.
- Plans must call out **module boundaries** and name the file each
  responsibility will live in — not "the auth logic," but
  `auth/session.py` and `auth/policy.py`.
- Every file the plan creates must satisfy the file rules (purpose,
  responsibilities, does-not, used-by docstring).

**Check.** Cost-of-Change table (Constitution §"north star"). 1–3 healthy,
5–10 warning, 10+ architecture problem, 20+ critical.

## 1.3 Scalability — how to size plans for growth

**Purpose.** A plan that solves today's problem and survives tomorrow's
volume. ASPIS targets 70% cheap / 20% standard / 10% deep model usage, so
scaling is a *budget* problem as much as a capacity one.

**Apply during planning.**
- **Volume axes** — what grows? Files, tasks, agents, models, tokens,
  features? For each axis, name how the plan scales linearly.
- **Recursion budget** — multi-agent with recursion is 15× the tokens of
  single-agent (Anthropic 2025-06). Plans that fan out workers must
  justify the parallelizability or stay single-agent + subagent review
  (the ASPIS default for sub-1-hour tasks).
- **Context-isolation** — every worker / sub-builder the plan introduces
  gets a context-isolated packet; no shared mutable state for coordination
  (Cursor's failed experiment, `core-loops-2026.md` §1.4).
- **Mode scaling** — the plan declares its mode and the mode for *each
  task* if it varies; vibe for throwaway research, MVP for in-progress
  features, production for the customer-facing surface.

**Check.** For each task in TASKS.md, ask: *could this be done by a fresh
subagent with only the packet?* If no, the packet is too thin or the worker
is too coupled.

## 1.4 Simplicity — how to avoid over-engineering

**Purpose.** Boring, predictable, repeatable wins. (Constitution rule 10,
"Consistency over Cleverness.")

**Apply during planning.**
- **Boring by default.** New file with one purpose beats a clever shared
  abstraction.
- **The "describe the diff in one sentence" test** (Anthropic, June 2026):
  if you cannot, the work needs a plan; if you can in two words, no plan is
  needed — just commit. Vibe mode.
- **No speculative org charts.** "If we add three more agents we might
  need…" — R-003 forbids it. Build what is needed when it is needed.
- **Delete by default.** If the plan does not name a thing as created or
  used, do not create it.
- **Three-rule heuristic.** If a design needs more than three rules to
  explain, simplify the design until it needs fewer.

**Check.** Plan-critic looks for: unused parameters, "future-proof" flags,
dead code paths, abstractions with one user, plugin registries with one
member.

## 1.5 Constitution compliance — passing the 12 checks

**Purpose.** The architecture-constitution is the gate. A plan that violates
it produces a system that decays; the cost of that decay is not visible at
planning time, only at the next feature.

**Apply during planning.** The 12 rules are listed and per-moded in
`§2 matrix`. At a planning-level summary, the **three rules to enforce
above all** (per the Constitution: "if only three are enforced") are:

1. **Plugin First** — anything that will grow is a plugin; the core never
   names a concrete one.
2. **Single Source of Truth** — every fact has exactly one owner.
3. **Local Change** — new feature is mostly new files.

The other nine are real and enforced in production mode; the three are
the floor for MVP, and Vibe mode still respects the ones that are also
hard rules (R-001, R-008 — see `§2`).

**Check.** `aspis constitution-check` (planned) or a manual run of the
`constitution-checks.yaml` matrix. The plan-critic reviewer runs this
check as part of plan-critic.

## 1.6 Deterministic-first — scripts vs agents in the plan

**Purpose.** R-003 / Constitution "Automation before Intelligence":
`Script → Tool → Workflow → Agent`, in that order. The plan must respect the
ladder.

**Apply during planning.**
- For every step the plan introduces, classify it as
  **deterministic** (script / hook / template / config) or **judgmental**
  (agent / skill). Default to deterministic.
- A plan that introduces an agent to format text, validate a path, or run
  a build is wrong — those are scripts. A plan that introduces a script to
  decide architecture is also wrong — that is a plan-critic.
- Workflows (markdown procedures) and templates (markdown scaffolds) are
  higher on the ladder than agents because they are reproducible.
- The plan must list any **new scripts / hooks / templates** it introduces
  and the **new agents / skills** it introduces, separately.

**Check.** For each task in TASKS.md: *is the executor an LLM, or a script
the LLM invokes?* If LLM and the work is mechanical, refactor to a script
the LLM calls.

## 1.7 Single Source of Truth — catalog → brain → runtime

**Purpose.** One fact, one owner, generated everywhere else. (Constitution
rule 3.)

**Apply during planning.**
- The plan is the **source of truth** for its feature's scope, design, and
  acceptance. The brain (`.aspis/`) consumes the plan; the runtime
  (`.opencode/`, `.claude/`) regenerates from the catalog.
- The plan **never** hand-edits generated artifacts. If the plan needs a
  new file in `.opencode/`, that file is **generated** by the
  `promote` pipeline from a catalog entry — it is not authored in place.
- A plan that says "edit `.opencode/agents/X.md`" without saying "by
  adding Y to the catalog and running `promote`" is a Constitution
  violation.
- A plan must name the **owner** of every fact: where the canonical value
  lives, and which files are generated from it.

**Check.** Plan-critic runs `aspis validate-runtime` after the plan is
approved; if a planned change to a live file has no catalog source, the
plan is wrong.

## 1.8 Generated vs authored — the labeling rule

**Purpose.** (Constitution rule 8.) Humans edit source; machines generate
catalogs, indexes, and docs. Never hand-maintain generated output.

**Apply during planning.**
- Every file in a plan is tagged one of:
  - **Authored** — human/agent edits by hand, lives in source control.
  - **Generated** — produced by a script; checked in only if it must be
    reproducible offline; otherwise ignored.
  - **Runtime** — produced by the runtime pipeline; never edited by hand.
- ASPIS's policy today: generated artifacts are checked in to make the
  diff visible (D-012), with a clear generator path. The plan respects
  that and never edits a generated file to "fix" it — it fixes the
  generator and regenerates.
- Plans must mark **the generator** for any new generated file: which
  script produces it, on which event, with which inputs.

**Check.** Plan-critic walks the new-file list and asks for each:
"authored or generated? by whom, from what?" A missing answer is a
finding.

---

# 2. Rules Application per Mode

**Mode is a ceiling, not a floor.** (Pattern 5, `core-loops-2026.md` §1.5.)
The shape of the loop stays the same; the depth changes. The same artefact
exists in all modes — what changes is how many boxes must be checked.

**Reading the matrix:**

- **Enforce** — the rule is in effect; plan-critic fails the plan on violation.
- **Prefer** — the rule is the default; deviation needs a one-line reason in
  the plan and is still reviewable.
- **Skip** — the rule is not applied; no need to mention it.
- **Inherits** — the rule is enforced by the runtime / hooks (R-001, R-008,
  R-007, R-004) and does not depend on mode.

## 2.1 The 12 Constitution extension rules

| # | Rule | Production | MVP | Vibe | How plan-critic checks |
|---|---|---|---|---|---|
| C-01 | **Local Change** (new feature = new files) | **Enforce.** Cost-of-Change must be 1–3. | **Enforce.** Same target, but 1–5 acceptable. | **Prefer.** No minimum bar; do not edit the core. | Count files changed; flag if any feature touches ≥3 unrelated files. |
| C-02 | **Plugin First** (growing things are plugins) | **Enforce.** New agent / skill / profile / asset kind is a plugin, not a core edit. | **Enforce.** If the feature is one of a kind, OK to inline; flag a second instance and refactor. | **Skip.** Inline is fine; note the seam in `## Open`. | Search the plan for "new file" patterns vs. "edit core"; flag in-place growth. |
| C-03 | **Single Source of Truth** (one owner per fact) | **Enforce.** Catalog → brain → runtime chain respected. | **Enforce.** Same chain. | **Enforce.** This is the safety net that keeps vibe from rotting. | Trace every planned fact to its source; flag duplicates. |
| C-04 | **Configuration over Code** (data, not `if` chains) | **Enforce.** New behaviour is a config row, not an `if`. | **Prefer.** One `if` is OK; two is a config seam. | **Skip.** | Grep plan for `if mode ==` / `if runtime ==` / `if profile ==`; flag. |
| C-05 | **Core is Stable** (most work in plugins/assets) | **Enforce.** | **Prefer.** | **Skip.** | Diff core files; flag any non-fix edits. |
| C-06 | **Dependency Direction** (plugins → core, never reverse) | **Enforce.** | **Enforce.** | **Prefer.** | Static check: does the new module import from a leaf? Flag. |
| C-07 | **Discovery over Registration** (convention, no `REGISTRY`) | **Enforce.** | **Prefer.** | **Skip.** | Grep for `REGISTRY = `; flag. |
| C-08 | **Generated Artifacts** (machines generate, humans edit source) | **Enforce.** | **Enforce.** | **Enforce.** | Walk new files; mark authored/generated; flag hand-edits to generated. |
| C-09 | **No Special Cases** (capability checks, not runtime names) | **Enforce.** | **Prefer.** | **Skip.** | Grep plan for `if runtime ==` / `if profile ==` / hardcoded model ids. |
| C-10 | **Consistency over Cleverness** | **Enforce.** | **Enforce.** | **Enforce.** Boring is the bar. | Subjective; reviewer judgement; flag "clever" comments. |
| C-11 | **Architecture before Features** (build the seam, then the feature) | **Enforce** when ≥2 features of the same shape are planned. | **Prefer** when a 2nd is on the roadmap. | **Skip.** | Count features of the same shape on the roadmap; flag if seam is missing. |
| C-12 | **Portable by Default** (Windows + Linux, UTF-8, pathlib) | **Enforce.** | **Enforce.** | **Enforce.** OS difference is a bug. | Grep for `os.system`, `subprocess` without `encoding=`, `open(`, hardcoded `/` or `\`; flag. |

## 2.2 The 9 System rules (R-001 … R-009)

System rules **bound** what the others may do (per `system-rules.md` §
"Precedence"). They are *inherited* from the runtime where the hooks
enforce them; the plan-critic confirms the plan does not propose workarounds.

| # | Rule | Production | MVP | Vibe | How checked |
|---|---|---|---|---|---|
| **R-001** | **Scope** — change only allowed files; never touch forbidden / secrets | **Inherits + Enforce.** Plan's `scope.allowed` is the truth; hook enforces at commit. | **Inherits + Enforce.** | **Inherits + Enforce.** Always. | Pre-commit hook (`aspis preflight`); scope-control skill. |
| **R-002** | **Gates first** — format / lint / types / tests pass before "done" | **Inherits + Enforce.** Full gate per task packet. | **Inherits + Enforce.** May relax to format+lint+tests-only. | **Inherits + Enforce.** Minimum: format + the test that proves the change. | `.asps/gates.yaml` runs as one command; `aspis preflight` at commit. |
| **R-003** | **Deterministic-first** — script → tool → workflow → agent | **Enforce** in plan design. | **Enforce** in plan design. | **Prefer** in plan design. | Plan-critic checks each new "agent" against the ladder (§1.6). |
| **R-004** | **One writer** — only the committer commits; reviewers read-only | **Inherits + Enforce.** | **Inherits + Enforce.** | **Inherits + Enforce.** | Git permission block on every agent except `committer`; commit-reviewer subagent at the hook. |
| **R-005** | **Tests-as-spec** — behaviour change needs tests; never weaken a test | **Enforce** in TASKS.md; one test per FR. | **Enforce** for changed behaviour; gap tests added later. | **Enforce** for the one test that proves the change. Never delete. | Plan-critic checks: does the task packet include a failing test (red) before the implementation (green)? |
| **R-006** | **Thin agents, single source** — identity + rules + skills; no duplicated bodies | **Enforce.** Plan never duplicates a rule or procedure. | **Enforce.** | **Prefer.** | Plan-critic greps for rule text duplicated outside `system-rules.md`. |
| **R-007** | **Pinned models** — every agent declares an explicit tier | **Inherits + Enforce** in plan-critic; task may override per-tier. | **Inherits + Enforce.** | **Inherits + Enforce.** | `agent-models.yaml` resolves; `aspis models` reports. |
| **R-008** | **Human gate** — architecture / rules / permissions / security / model-routing | **Inherits + Enforce.** | **Inherits + Enforce.** | **Inherits + Enforce.** No mode relax. | `governance` subagent is the only path; approval-ledger enforces. |
| **R-009** | **Trace and learn** — durable record; capture lessons | **Enforce** in plan: every task emits the events in `TRACEHOOKS.md`. | **Enforce** for `delegation`, `gate_result`, `phase_end` minimum. | **Enforce** for `phase_end` and any `fail`. | `trace-pipe` post-commit; `asps doctor --post-run`. |

**Hard invariants (apply in every mode, no exception):**

- R-001, R-004, R-007, R-008, R-009 are **never** relaxed by mode.
- C-03 (Single Source of Truth), C-08 (Generated Artifacts), and C-12
  (Portable by Default) are **never** relaxed — they are the safety net
  that keeps a vibe-mode project from rotting.
- C-10 (Consistency over Cleverness) is **never** relaxed — boring is
  cheap; clever is a future cost.

## 2.3 Quick matrix (collapsed)

For when the planner needs a one-screen check:

| Concern | Production | MVP | Vibe |
|---|---|---|---|
| Cost-of-Change bar | 1–3 files | 1–5 files | no bar |
| Plugin / Local Change | enforce | enforce (relaxed) | prefer |
| Single Source of Truth | enforce | enforce | enforce |
| Generated Artifacts labelled | enforce | enforce | enforce |
| Portable (Windows+Linux) | enforce | enforce | enforce |
| New tests per FR | yes | yes (changed FRs) | one proves the change |
| Determinism before LLM | always | always | usually |
| Architecture seam first | if ≥2 features | if on roadmap | no |
| Trace events per task | full | minimal | `phase_end` + `fail` |
| Plan-critic review | required | required | optional |
| Human gate (R-008) | always | always | always |

---

# 3. Best Standards — Always Apply

The non-negotiable planning standards, regardless of mode. These are the
non-model factors that make the cheap model do production-grade work
(per the architecture's "prime directive"):

```
Quality = model capability × task clarity × test strength × review discipline
```

Every standard below moves one of the four factors; together they are
the leverage.

**S-01 · Measurable acceptance criteria.** Every SPEC has FR-### (functional
requirements) and SC-### (success criteria) — specific, testable, single
interpretation. *Vague is a planning bug.*

**S-02 · Testing strategy in every plan.** Every PLAN names: which test
types apply (unit, integration, e2e, contract), which gate proves
passing, who writes the failing test first (R-005), and how coverage
gap is closed.

**S-03 · Constitution compliance check.** Every PLAN has a `## Constitution
check` section that names the 12 rules and states pass/fail/N-A for each.
Not a hand-wave — a one-line per rule. (See `§2.1` for the per-mode
depth.)

**S-04 · Tasks sequenced with clear dependencies.** Every TASKS.md has
explicit `## Dependencies` and the DAG is acyclic. No "T-003 depends on
T-001 and T-002" without saying why and what the contract is.

**S-05 · SPEC has scope boundaries.** Every SPEC has `## In scope` and `##
Out of scope` — non-negotiable. Out-of-scope items are not "future work";
they are *explicitly excluded* so a builder cannot drift.

**S-06 · Each task packet is self-contained.** A general-builder with
only the packet can succeed. If the packet needs the SPEC to make sense,
the packet is too thin.

**S-07 · Architecture named in concrete files.** PLAN says `auth/session.py`
not "the auth logic." Modules, packages, and main symbols are named.

**S-08 · Mode declared and applied.** Plan frontmatter says `mode: production`
(or MVP / vibe), and the rest of the plan matches the matrix in `§2`.
Mismatch is a finding.

**S-09 · Hand-off to next lead is explicit.** The plan ends with a
`## Hand-off` that names build-lead, lists the artifacts, and states the
gate build-lead will run. No "and then implement" hand-wave.

**S-10 · One decision per ambiguity.** When the plan closes an open
question, it records the decision (e.g., "D-XXX — library X is pinned")
in the project's decision log. Open questions are listed, not
silently resolved.

**S-11 · The "describe the diff" check runs first.** Before writing
anything, run the heuristic: can the change be described in one
sentence? If yes, the plan is a paragraph, not a 30-page document
(Anthropic, June 2026).

**S-12 · Risk and uncertainty are explicit.** Any `[UNVERIFIED]` choice
is marked, with the risk and the path to verify later. The plan-critic
flags unmarked unverified choices.

---

# 4. Mode-Dependent Model Tier Strategy

ASPIS has three tiers: **cheap** / **standard** / **deep** (per
`profiles/defaults.yaml`, D-016 / D-017). Concrete model ids are in
`agent-models.yaml`; the tier *names* are stable.

**Target mix** (per `AGENT-SYSTEM-ARCHITECTURE.md` "How Cheap Models Are
Used"):

```
~70% cheap · ~20% standard · ~10% deep
```

The mix is a *target*, not a rule per task. The plan picks per sub-task.

## 4.1 Per-mode default

| Mode | Default for planning sub-tasks |
|---|---|
| **Production** | **Deep** for SPEC + Architecture, **standard** for task decomposition, **cheap** for clarification + small reads. |
| **MVP** | **Standard** for SPEC + Architecture, **standard** for task decomposition, **cheap** for everything else. |
| **Vibe** | **Cheap** throughout. Escalate to standard only if the model returns obvious nonsense. |

## 4.2 Per-phase selection (production reference)

| Phase | Tier | Why |
|---|---|---|
| **Intake / classification** | cheap | routing is mechanical once the heuristics are written |
| **Context gathering** (L1–L4) | cheap | most reads; orchestrator (standard) sees only summaries |
| **Clarification** (max-5 questions) | cheap | pattern is well-known; the skill does the work |
| **SPEC authoring** | **deep** | sets the bar for everything downstream |
| **Architecture design** | **deep** | constitutional impact; novel design space |
| **Task decomposition** | standard | mechanical given a good plan |
| **Plan-critic review** | **deep** | adversarial; needs strong judgement |
| **Acceptance criteria authoring** | standard | mechanical from FRs |
| **Hand-off doc** | cheap | the artefacts already exist |

## 4.3 Cascade on failure

If a tier fails to produce an acceptable artefact:

```
1. cheap (1st try) → cheap (2nd try, with feedback) → standard → deep → escalate
```

Three cheap attempts before escalating (the canonical cascade, per the
"Five quality-preserving patterns" of `AGENT-SYSTEM-ARCHITECTURE.md`).
This is a budget, not a rule — `mode: production` may allow fewer
cheap retries on critical phases.

## 4.4 Cost profile per mode (planning phase only)

Indicative relative cost (deep = 8× cheap, standard = 3× cheap):

| Mode | Cheapest plausible | Typical | Why it grows |
|---|---|---|---|
| Vibe | 1× (cheap only) | 1–2× | skips most phases |
| MVP | 2–3× | 4–6× | runs standard SPEC + standard tasks |
| Production | 6–10× | 10–20× | deep SPEC + deep plan-critic + acceptance |

The cost grows because **ceremony grows**, not because individual calls
are slower. The leverage is that the cost buys fewer build failures.

## 4.5 The reconcile gap (planning-lead frontmatter)

The current planning-lead live frontmatter pins
`model: opencode-go/deepseek-v4-pro` (deep tier), while the catalog
intent is standard (`local/agents/planning-lead.md` §"What's missing").
**Resolution:** the agent's default tier is **deep** for production mode
and **standard** for MVP; the `model:` pin is a *default*, and the
sub-task tier may override via `modes.yaml`. Until this is wired,
planning-lead uses the deep pin and accepts the cost — it is cheaper
than a bad SPEC.

---

# 5. Project / User Rules Integration

ASPIS has three rule layers (per `system-rules.md` §"The three rule
layers"). Planning-lead operates inside the project layer; the
**system-lead** owns the validation and promotion of rules between
layers.

## 5.1 The three layers

| Layer | Source | Scope | Mutability |
|---|---|---|---|
| **System** | `.aspis/rules/system-rules.md` + `architecture-constitution.md` | every project, every lead | human-gated (R-008) |
| **Project** | `.aspis/rules/project-rules.md` (authored per project) | this project only | planning-lead + build-lead apply; system-lead promotes |
| **User** | the user's own global file | every project the user owns | user writes; system-lead validates and projects relevant rules per project |

## 5.2 Precedence (when they conflict)

1. **System rules are never overridden** — they bound what the others may
   do. (Per `system-rules.md` §"Precedence".)
2. **Valid user rule > project default** — a user rule that has been
   validated by system-lead for this project overrides the project rule.
3. **Project rule > global default** — if no user rule covers it, the
   project rule applies.
4. **Invalid or not-yet-applicable user rule** — carried but not enforced
   (per `system-rules.md`); planning-lead notes them as
   `[INHERITED-NOT-ENFORCED]` and does not apply.

If a project rule *appears* to override a system rule, the project rule
is wrong. Escalate via system-lead, not silently override.

## 5.3 How planning-lead reads each layer

- **System rules** — load `system-rules.md` and
  `architecture-constitution.md` once at the start of every planning
  cycle; cite by ID (`R-002`, `C-07`).
- **Project rules** — load `.aspis/rules/project-rules.md` (if present)
  in the same step. If absent, the project uses the system rules alone
  + the project's `modes.yaml` + `gates.yaml` for project-specific
  defaults.
- **User rules** — system-lead projects the relevant subset into
  `.aspis/rules/user-rules.md` (planned). Planning-lead reads that file
  if present; otherwise none apply.

## 5.4 Rules that don't apply to the current stack

The system rules are stack-agnostic; they always apply. Project and
user rules may be stack-specific (e.g., "use ruff for Python
formatting"). When a project rule names a tool that does not exist in
the stack:

- **Carry, do not enforce.** Note the rule in
  `.aspis/rules/project-rules.md` with `[N/A this stack]`.
- **Substitute the equivalent** (e.g., `ruff` for Python → `gofmt`
  for Go) and add a project rule for the substitute.
- **Do not silently skip** — a missing tool is a finding the
  plan-critic reports.

## 5.5 Conflict-resolution procedure

When planning-lead encounters a conflict between layers:

1. Cite both rules by ID and file path in the SPEC's
   `## Open questions` section.
2. If one is a system rule and the other isn't, system wins — record
   the resolution and the rationale.
3. If both are project/user, prefer the user rule (if validated);
   record the resolution.
4. If the conflict is unresolvable in planning scope, **escalate** to
   project-lead (not silently pick a side).

---

# 6. Planning Anti-Patterns

These are **provably wrong** (sourced from the research + Constitution).
A plan that triggers one is a planning failure, not a style nit.

## 6.1 From the research (industry-validated)

| Anti-pattern | Why it fails | Source |
|---|---|---|
| **Self-coordinating agents via shared state file** | Agents hold locks wrong; 20 agents → throughput of 1–3. | Cursor, "Self-driving codebases" (Feb 2026) |
| **One agent with too many roles** (plan + spawn + review + commit) | "Overwhelmed" agent exhibits pathological behaviors: sleep, refusal, premature completion. | Cursor (Feb 2026) |
| **Central integrator gating all work** | Bottleneck; hundreds of workers, one gate. | Cursor (Feb 2026) |
| **100% correctness at every commit** | Serializes the system; agents trample each other fixing the same issue. | Cursor (Feb 2026) |
| **Self-review (builder grades own work)** | Bias — "this is fine, I wrote it." Every surveyed system rejects. | All surveyed (Anthropic, Cursor, METR) |
| **Per-tool-call review of every action** | ~4% need it; reviewing all 100% creates approval fatigue. | Cursor, "Auto-review" (June 2026) |
| **Multi-agent for non-parallel work** | 15× token cost for zero throughput gain. | Anthropic (June 2025); ASPIS sub-1-hour default is single-agent. |
| **Hand-tuned framework abstractions over direct API** | Layers obscure the prompts; harder to debug. | Anthropic, "Building Effective Agents" (Dec 2024) |
| **Prefilled responses for steering** | Deprecated in Claude 4.6; "model intelligence has advanced." | Anthropic, June 2026 |
| **Hand-maintained generated artifacts** | Drift; the byte-parity test fails. | ASPIS D-012, D-014 |

## 6.2 From the Constitution (engineering)

| Anti-pattern | Why it fails |
|---|---|
| **Editing the core to add a feature** | Violates C-05 (Core is Stable); every future feature needs to edit it. |
| **Special-casing a runtime / profile / framework by name** | Violates C-09 (No Special Cases); use capability checks. |
| **Hand-maintained `REGISTRY = [...]`** | Violates C-07 (Discovery over Registration); load by convention. |
| **Mixing generated and authored in the same file** | Violates C-08 (Generated Artifacts); one or the other, marked. |
| **Hardcoded paths, codecs, shell-isms** | Violates C-12 (Portable by Default); use `pathlib`, `encoding="utf-8"`, cross-platform shells. |

## 6.3 Planning-specific (this document)

These are how the above show up in a plan, with the planning-level
checks.

### A. Over-planning (analysis paralysis)

**Symptom:** a 30-page plan for a 2-file change; phases that produce no
artefact; speculative future-proofing.
**Test:** *Can the change be described in one sentence?* If yes, the
plan is too long.
**Fix:** Drop to vibe mode; the spec is the one-sentence change plus
its one test.

### B. Under-planning (build-ready gaps)

**Symptom:** a 1-page plan for a 20-file change; missing FR-###,
missing task dependencies, no acceptance criteria.
**Test:** *Can a fresh general-builder with only the packet succeed?*
If no, the packet is too thin.
**Fix:** Decompose; add FRs; add packets; route to plan-critic.

### C. Speculative architecture

**Symptom:** "in case we add X later, we will need Y" — R-003 forbidden.
**Test:** *Is Y used by the feature this plan delivers, or by a
plausible-but-not-planned future?*
**Fix:** Delete Y; the future plan adds it when needed.

### D. Gold-plating

**Symptom:** error handling for impossible cases; retries for
non-existent failures; abstractions with one user.
**Test:** *Is the surface area used in the current feature?* If not,
delete.
**Fix:** Delete until the next user complains; add when needed.

### E. Ignoring the Constitution

**Symptom:** a plan that adds a special case, hand-edits a generated
file, or edits the core to add a feature.
**Test:** Run the 12-rule check from `§2.1`.
**Fix:** Refactor the plan to honor the rule, or escalate to
project-lead if the rule blocks an explicit user requirement.

### F. Plan without acceptance

**Symptom:** no SC-###; "done" means "looks done."
**Test:** *What test, run by whom, on what command, proves the
feature works?* If unanswerable, no acceptance.
**Fix:** Add SC-### tied to FR-###, with a test per SC.

### G. Plan without scope boundary

**Symptom:** no `## Out of scope`; everything is in.
**Test:** *What does this plan explicitly NOT do?* If the answer is
vague, scope is open.
**Fix:** Add `## In` and `## Out` sections; out-of-scope items are
listed, not silent.

### H. Plan that names a concrete runtime in a special case

**Symptom:** `if runtime == "claude"` / `if profile == "x"` /
hardcoded model id in the plan body.
**Test:** Grep for these patterns.
**Fix:** Use a capability check or a config table; add to
`profiles/defaults.yaml`.

### I. Plan that touches the core for every feature

**Symptom:** core diff size grows with feature count.
**Test:** Count features planned vs. core files edited.
**Fix:** Find the seam; make the feature a plugin.

### J. Plan with 100% acceptance barrier per task

**Symptom:** every task must pass everything; "the only way to ship
is everything green."
**Test:** *Is this a per-task gate or a feature gate?*
**Fix:** Per-task = the task's own test + format/lint. Feature =
SPEC's SC-###. Don't conflate.

### K. Plan that hand-tunes prompts instead of using deterministic scripts

**Symptom:** "the agent will be told to always format dates as…"
**Test:** *Could a hook do this?* If yes, plan the hook.
**Fix:** Plan the hook, not the prompt.

### L. Plan that throws away context

**Symptom:** the plan exists only in chat; no SPEC.md / PLAN.md /
TASKS.md artefacts.
**Test:** *Is the plan persisted?* If no, the next agent cannot
recover.
**Fix:** Use templates; persist every artefact.

---

# Appendix A — Plan-critic checklist (the one-page version)

A reviewer running plan-critic walks this in order. A "no" is a
finding; three "no" answers = rejected plan.

### A.1 Mode and rigour

- [ ] Mode is declared in plan frontmatter and matches `modes.yaml`.
- [ ] Plan depth matches the mode's matrix column in `§2.3`.
- [ ] Hard invariants (R-001, R-004, R-007, R-008, R-009, C-03, C-08,
      C-10, C-12) hold.

### A.2 Standards (S-01 … S-12)

- [ ] Measurable acceptance criteria (S-01).
- [ ] Testing strategy (S-02).
- [ ] Constitution check section (S-03).
- [ ] Task dependencies explicit and acyclic (S-04).
- [ ] SPEC has `## In` / `## Out` (S-05).
- [ ] Each task packet is self-contained (S-06).
- [ ] Architecture named in concrete files (S-07).
- [ ] Mode declared and applied (S-08).
- [ ] Hand-off section names build-lead and the gate (S-09).
- [ ] Open questions listed, not silently resolved (S-10).
- [ ] "Describe the diff" check was run first (S-11).
- [ ] `[UNVERIFIED]` items are explicit (S-12).

### A.3 Constitution matrix (12 checks)

- [ ] C-01 Local Change — Cost-of-Change ≤ 3 (production) / ≤ 5 (MVP).
- [ ] C-02 Plugin First — no new instance hardcoded in core.
- [ ] C-03 Single Source of Truth — every fact has one owner.
- [ ] C-04 Configuration over Code — no `if` chains for behaviour.
- [ ] C-05 Core is Stable — core diff is empty (or fix-only).
- [ ] C-06 Dependency Direction — imports flow inward.
- [ ] C-07 Discovery over Registration — no hand-maintained `REGISTRY`.
- [ ] C-08 Generated Artifacts — every new file is labelled.
- [ ] C-09 No Special Cases — no `if runtime ==`, `if profile ==`.
- [ ] C-10 Consistency over Cleverness — boring by design.
- [ ] C-11 Architecture before Features — seam exists if ≥2 features.
- [ ] C-12 Portable by Default — no OS-specific code without
      cross-platform substitute.

### A.4 System rules (R-001 … R-009)

- [ ] R-001 scope.allowed matches the plan's file list.
- [ ] R-002 the gate that proves "done" is named.
- [ ] R-003 each new agent has a script-alternative considered.
- [ ] R-004 no agent except committer is asked to commit.
- [ ] R-005 each FR has a failing test in its task packet.
- [ ] R-006 no rule text is duplicated outside `system-rules.md`.
- [ ] R-007 every agent in the plan has an explicit model tier.
- [ ] R-008 architecture / rules / model changes routed to human.
- [ ] R-009 trace events per task are listed in the packet.

### A.5 Anti-patterns (§6)

- [ ] No item from §6.1 (research) appears in the plan.
- [ ] No item from §6.2 (Constitution) appears in the plan.
- [ ] No item from §6.3 (planning-specific) appears in the plan.

---

# Appendix B — One-screen "good plan" template

This is the shape every plan in production mode takes. MVP and vibe
abbreviate the sections; the labels stay.

```markdown
# F-NNN — [Feature Name]

> mode: production | model: deepseek-v4-pro | owner: planning-lead

## Problem & value
[1–3 sentences; the why.]

## In scope
[Bulleted; specific.]

## Out of scope
[Bulleted; explicit.]

## FR-### Functional requirements
- FR-1: …
- FR-2: …

## SC-### Success criteria
- SC-1: … (test: <command> passes)
- SC-2: …

## Constitution check
C-01 pass | C-02 pass | C-03 pass | … | C-12 pass

## Architecture
- New files: [list, with author/generated tag]
- Modified files: [list, with reason]
- Dependency direction: [one line]
- Cross-platform: [one line; pathlib + UTF-8 + encoding="utf-8"]

## Tasks
- T-001 [depends on: —] [model: standard]: scope, files, acceptance
- T-002 [depends on: T-001] [model: cheap]: scope, files, acceptance
- …

## Testing strategy
- Unit: <test files>
- Integration: <test files>
- Gate: `.asps/gates.yaml` runs in <workflow>

## Risks & [UNVERIFIED]
- R-1: <risk> → <mitigation>
- U-1: <choice> marked [UNVERIFIED] → <path to verify>

## Hand-off
- To: build-lead
- Artifacts: SPEC.md, PLAN.md, TASKS.md, packets/*.md
- Gate build-lead will run: `.asps/gates.yaml`
- Open questions: <list, if any>
```

---

# Appendix C — Source provenance

This document synthesises the following, verified on 2026-06-26:

| Source | Used for | Verified |
|---|---|---|
| `.aspis/rules/architecture-constitution.md` | 12 rules; Cost-of-Change test; automation-before-intelligence | 2026-06-26 |
| `.aspis/rules/system-rules.md` | R-001…R-009; precedence; three rule layers | 2026-06-26 |
| `local/AGENT-SYSTEM-ARCHITECTURE.md` | 3 modes; 3-layer hierarchy; 70/20/10 tier mix; deterministic-first ladder | 2026-06-26 |
| `.aspis/features/F-016-agent-system-architecture/Research/core-loops-2026.md` | 5 proven patterns; mode as ceiling not floor; 1,000-commits/hour + 15× token cost data; anti-patterns | 2026-06-26 |
| `.aspis/features/F-016-agent-system-architecture/Research/old-asps-deep-analysis-1.md` | P0–P9 pipeline; per-mode scaling; subsystems A–H; 8 orchestration patterns; profiles | 2026-06-26 |
| `.opencode/agents/planning-lead.md` | Live frontmatter (model = deepseek-v4-pro, deep tier); 6-step procedure; mode routing | 2026-06-26 |
| `local/agents/planning-lead.md` | Catalog intent (standard tier); skill list; "What's missing" notes | 2026-06-26 |
| Anthropic, "Best practices for Claude Code" (verified 2026-06-25 in `core-loops-2026.md` §1.5) | "Describe the diff in one sentence" heuristic | 2026-06-26 |
| Cursor, "Self-driving codebases" (Feb 2026) | Recursive planners; failed multi-agent experiments; 1,000-commits/hour | 2026-06-26 |
| Anthropic, "Multi-agent research" (June 2025) | 90.2% multi-agent win on research; 15× token cost; subagent context compression | 2026-06-26 |

External sources are cited where the rule depends on the industry
evidence (mode dial, 15× token cost, "describe the diff" heuristic).
System-internal sources are cited by file path for verifiability.

---

# Appendix D — Versioning and updates

- **Stable ID:** `planning-quality-reference-v1` (in the frontmatter of
  the planning-lead agent, planned).
- **Update trigger:** any change to `system-rules.md` (R-001…R-009),
  any change to the 12 constitution rules, any new mode added to
  `modes.yaml`, any change to the tier mix (70/20/10), or any new
  anti-pattern documented by research-lead.
- **Update path:** research-lead drafts the diff; system-lead promotes
  it; planning-lead and reviewer reload. The doc is **not** regenerated
  by the planning pipeline — it is human-curated because it sets the
  bar.
- **Citation convention:** a plan or review cites this doc as
  `planning-quality-reference-v1 §1.5` or
  `planning-quality-reference-v1 §2.1 C-09`. The version tag is
  required so old findings remain traceable.

---

*End of reference. Cite by section ID. The cheapest model does
production-grade work when this reference is in effect — that is the
bet.*
