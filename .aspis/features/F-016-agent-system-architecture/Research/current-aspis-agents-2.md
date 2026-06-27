# F-016 Research — Current ASPIS agent roles: live vs. catalog

> **Feature:** F-016 — agent system architecture
> **Mode:** production · **Phase:** plan
> **Compiled:** 2026-06-25
> **Scope:** per-agent analysis of the 10 agents deployed under `.opencode/agents/`
> (the live runtime), compared to the 12 catalog assets at
> `src/aspis/data/catalog/agents/`. The catalog is the source of truth — the live
> file is what an LLM actually executes today.

---

## 0. Inventory & high-level drift

| Agent | Live (`.opencode/agents/`) | Catalog (`src/aspis/data/catalog/agents/`) | Mode in live | Mode in catalog |
|---|---|---|---|---|
| project-lead | ✅ | ✅ | primary | primary |
| planning-lead | ✅ | ✅ | **primary** | subagent |
| build-lead | ✅ | ✅ | **primary** | subagent |
| reviewer | ✅ | ✅ | **primary** | subagent |
| system-lead | ✅ | ✅ | **primary** | subagent |
| fix-lead | ✅ | ✅ | subagent | subagent |
| research-lead | ✅ | ✅ | subagent | subagent |
| general-builder | ✅ | ✅ | subagent | subagent |
| committer | ✅ | ✅ | subagent | subagent |
| project-explorer | ✅ | ✅ | subagent | subagent |
| test-lead | ❌ **MISSING** | ✅ | — | subagent |
| bootstrap | ❌ (export-only) | ✅ | — | primary (export-only) |

> Live has 10 agents. Catalog has 12. **The 5 live primaries are
> project-lead + planning-lead + build-lead + reviewer + system-lead** — that
> matches the bootstrap post-condition ("promotes the leads → 5 primaries").
> **test-lead is the one catalog agent with no live counterpart** — and it is
> referenced as a delegable from 3 of the 5 primaries (project-lead, build-lead,
> fix-lead) plus indirectly by the reviewer's `aspis artifact test` step. That
> is a **runtime gap**: the live system can attempt to delegate to an agent
> that does not exist.

Other live-vs-catalog drift worth noting up front (full per-agent table
later):

- **Bootstrap gate removed from project-lead live** — the
  `<!-- ASPIS:BOOTSTRAP-GATE -->` block in the catalog has been stripped
  from the live file. This is the correct post-bootstrap state, but it is
  worth knowing the file is no longer self-describing about that.
- **Model field is materialized in live** — catalog uses tiers
  (`cheap`/`standard`/`deep`); live uses concrete models
  (`opencode-go/deepseek-v4-pro`, `opencode-go/minimax-m3`,
  `opencode-go/deepseek-v4-flash`). The current assignment map is in
  `.aspis/config/agent-models.yaml` (per-runtime `by_capability` + per-agent
  overrides).
- **Task allow-list drift in two agents** (planning-lead has `committer`
  added; reviewer has `research-lead` added) — see per-agent sections.
- **system-lead websearch** is `allow` in live, `deny` in catalog.
- **committer has no `temperature`** in live; every other live agent has
  `temperature: 0.1`.

---

## 1. project-lead

**Live file:** `.opencode/agents/project-lead.md` (133 lines)
**Catalog file:** `src/aspis/data/catalog/agents/project-lead.md` (152 lines)
**Mode:** primary · **Model:** `opencode-go/deepseek-v4-pro` (catalog: `standard`)

### 1.1 Identity (per the file)

> "the **project's intelligence layer** and the primary entry point for the user. You
> understand the project as a whole better than any other agent … You are not a
> router and not a planner; you are the authoritative representation of the
> project. You do not implement, plan, review, or change the system yourself — you
> coordinate the specialist leads who own those, and you keep their work aligned
> with the project's goals."

The identity is explicit about what the agent is *not* — and the boundary is
repeated in Core rules ("read broadly and change almost nothing"). An LLM
reading this should not reach for `edit`/`write`/`git commit`.

### 1.2 Core role

- Project Intelligence — retrieve from `.aspis/context/`, `.aspis/index/`,
  `git status/diff/log`; delegate deeper exploration to `project-explorer`.
- Coordinate the leads via dynamic orchestration: "a feature might run
  planning → build → review; a defect might run fix → test → review; 'can we
  build this?' might run research → test → research → answer with no
  implementation at all."
- Protect project direction; keep work aligned with goals.
- The "one simple setting" it owns is **build mode** (`aspis mode`).

### 1.3 What it does NOT do

- Edits, commits, modifies runtime/skill/agent.
- Bypasses System Lead for system changes, Planning Lead for planning, or
  Reviewer for acceptance.
- Fixes detected problems itself — routes to System Lead or specialist.

### 1.4 Skills (8, all allow-listed)

`project-awareness`, `context-ladder`, `request-classification`,
`lead-routing`, `context-packaging`, `project-question-answering`,
`project-guidance`, `project-health`. The Responsibility → Skill table maps
1:1.

### 1.5 Delegation (task allow-list)

Live allows: `planning-lead`, `build-lead`, `reviewer`, `research-lead`,
`test-lead`, `fix-lead`, `system-lead`, `project-explorer`, `committer`.
Catalog allows the same minus `committer` and `bootstrap`, plus
`bootstrap`. Differences:

- Live **includes `committer`** in its task allow-list, even though the
  agent's own role description says it "read[s] broadly and change[s] almost
  nothing — no edits, no commits." The committer should be invoked by
  build/fix, not by project-lead. This is a **likely permission drift**.
- Live **does not include `bootstrap`** (correct — bootstrap is removed
  after first run, and its task delegate would be a no-op).

### 1.6 Permissions

- `read`, `grep`, `glob`: allow
- `bash`: allow for `git status*`, `git diff*`, `git log*`,
  `aspis bootstrap --check*`, `aspis status*`, `aspis doctor*`,
  `aspis mode*`, `aspis context*`, `aspis preflight*`, `aspis findings*`,
  context scripts. Deny for everything else.
- `webfetch`: deny · `websearch`: deny

Tight read-only surface, with the **one** write through `aspis mode`. The
catalog's `tools` list adds `bash` only (no edit/write/web). The role is
internally consistent.

### 1.7 Tools

Implicit (frontmatter lists permissions, not tools). Effective tools:
`read`, `grep`, `glob`, `bash` (allow-listed subset). No `edit`, no `write`.

### 1.8 Workflow

References `.aspis/workflows/` (plan, build, review, fix, small-task) and
the `/plan`, `/build`, `/review`, `/system`, `/status` commands. The live
file is short on the bootstrap gate (catalog has the
`ASPIS:BOOTSTRAP-GATE` block; live does not — correct after bootstrap).
It does **not** have its own dedicated workflow doc — appropriate for an
orchestrator that composes a path from the request.

### 1.9 Escalation

- "When you detect something stuck, unhealthy, or missing, route it to
  the System Lead or the right specialist … — never fix it yourself."
- "If you're stuck, stop — don't guess." — appears in the other leads'
  files but **not** in project-lead. Implicit: ask the user, since the
  project-lead is the user's first point of contact.

### 1.10 Read-first files

`.aspis/context/CURRENT_STATE.md`, `.aspis/context/RECENT_CHANGES.md`,
`.aspis/index/FILE_REGISTRY.yaml`, `.aspis/index/CODE_MAP.md`.

### 1.11 Core rules (paraphrased)

1. Classify the request before acting.
2. Gather only the context the request needs.
3. Protect project direction.
4. Prefer the specialist lead.
5. Don't bypass System/Planning/Reviewer.
6. Change almost nothing (build mode is the one exception).
7. Keep the project healthy — detect and route, don't fix.

### 1.12 Model

`opencode-go/deepseek-v4-pro` — orchestration tier.

### 1.13 Clarity · Completeness · Consistency assessment

- **Clarity: high.** The identity paragraph + "what you do NOT do" +
  responsibility table make the role legible at a glance. The "How you
  handle a request" paragraph (live) is explicit about the **dynamic**
  nature of orchestration, not a fixed routing table.
- **Completeness: very high for the project-lead role itself, but a gap
  in the system**: the `task: test-lead: allow` line is dangling because
  test-lead is not deployed in live (see §11). The project-lead's
  intent ("route to the right lead") is sound; the runtime cannot honor
  it for test-lead today.
- **Consistency: high.** Doesn't conflict with other agents. The
  committer-in-task-list is the only soft inconsistency — it doesn't
  contradict a rule (it just *allows* a delegation that the role says
  shouldn't happen).

### 1.14 Gaps & questions

- The committer in the task list — should be removed.
- The test-lead delegate is dangling.
- No explicit "if you're stuck" rule (other leads have it).
- No mention of *which* `.aspis/context/` files are the minimal hot set
  for a given request — the catalog's responsibility table lists
  project-awareness but the live file tells the agent to use it, not what
  it returns. A new agent would have to read the skill to find out.

---

## 2. planning-lead

**Live file:** `.opencode/agents/planning-lead.md` (121 lines)
**Catalog file:** `src/aspis/data/catalog/agents/planning-lead.md` (121 lines)
**Mode:** primary (live) / subagent (catalog) — promoted at bootstrap · **Model:**
`opencode-go/deepseek-v4-pro` (catalog: `deep`)

### 2.1 Identity

> "the owner of the planning lifecycle. You transform an idea, request, or
> problem into an execution-ready plan … You do not build, review, test, or
> research — you prepare the work for the leads that do."

The "you do not …" list is the planner's key constraint. The role is
**persistent, not a single artifact**: planning is "a lifecycle, not a
single document."

### 2.2 Core role (6-step lifecycle)

1. Intake (planning-intake)
2. Context (prestart-checks + context-ladder)
3. Clarify (requirement-clarification)
4. Spec (feature-planning)
5. Architecture (architecture-planning)
6. Tasks (task-decomposition)

Plus a mode overlay (production / mvp / vibe) from `.aspis/config/modes.yaml`.
Plus a self-review hand-off (planning is not the reviewer of its own plan).

### 2.3 What it does NOT do

- "Plan only; never write product code, approve quality, or change the
  runtime."
- Research — request it from the Research Lead.
- Self-review — plans are reviewed by the Reviewer before any build.
- Invent scope when ambiguous — ask the Project Lead (or the user).

### 2.4 Skills (7)

`prestart-checks`, `context-ladder`, `planning-intake`,
`requirement-clarification`, `feature-planning`, `architecture-planning`,
`task-decomposition`. 1:1 with the lifecycle steps.

### 2.5 Delegation (task allow-list)

Live: `research-lead`, `reviewer`, `project-explorer`, **`committer`**.
Catalog: `research-lead`, `reviewer`, `project-explorer` (no committer).

**The live task list adds `committer`**. There is no scenario in which the
Planning Lead should commit — it doesn't produce code, it produces
templates. This is the same kind of drift as the project-lead's
committer. **Two agents, one bug shape: a stray committer delegate that
should not be there.**

### 2.6 Permissions

- `read`, `grep`, `glob`, `edit`, `write`: allow (for templates and
  artifacts in `.aspis/features/…`).
- `bash`: allow `git status*`, `git diff*`, `git log*`, `aspis preflight*`,
  `aspis findings*`, `aspis context*`, context scripts, **planning
  scripts** (`python .aspis/scripts/planning/*`).
- **Deny: `git commit*`, `git push*`.** Good — plans shouldn't commit.
- `webfetch`: deny · `websearch`: deny

The planning-scripts allowance matches the workflow's use of
`feature_scaffold.py`, `task_compile.py`, `prereq_validate.py`.

### 2.7 Tools

`read`, `grep`, `glob`, `edit`, `write`, `bash` (allow-listed subset).

### 2.8 Workflow

References `.aspis/workflows/plan.md` ("the procedure, step by step").
That doc lays out 8 steps (intake & classify, scaffold, clarify, spec,
architecture, tasks, plan review, gate) with mode overlays. The agent
file and the workflow file are well aligned.

### 2.9 Escalation

> "**If you're stuck, stop — don't guess.** When the request is too
> ambiguous to plan safely, or needs a decision above your role, ask the
> Project Lead (or the user) rather than inventing scope."

Clear and specific. Explicit "ask the Project Lead" routing is good.

### 2.10 Read-first files

> "read the project state and relevant code/plans before deciding"
> (`context-ladder` L1 hot state first, deeper only as needed). Also
> `docs/ARCHITECTURE.md` (intended) and `.aspis/context/ARCHITECTURE.md`
> (as-built).

### 2.11 Core rules (paraphrased)

1. Classify before planning; context before deciding.
2. Design to the architecture constitution.
3. Evidence over assumption; ask only what you must.
4. Every plan defines measurable acceptance, a review strategy, and a
   testing strategy.
5. Plan only — no product code, no quality approval, no runtime changes.
6. Hand off for independent review.
7. If stuck, stop.

### 2.12 Model

`opencode-go/deepseek-v4-pro` — planning tier.

### 2.13 Clarity · Completeness · Consistency assessment

- **Clarity: high.** The 6-step lifecycle is the spine, the
  Responsibility → Skill table makes ownership clear, the mode overlay
  paragraph makes the rigor dial explicit.
- **Completeness: high.** The 6 steps cover intake → delivery. The
  "produce structured outputs from the templates — don't reinvent the
  format" rule prevents the agent from re-inventing a plan format.
- **Consistency: high** (modulo the committer-in-task-list drift, which
  is a *permission* issue, not a *role* contradiction).

### 2.14 Gaps & questions

- The task allow-list contains `committer` — should be removed.
- "Plan only" plus "delegate to committer if you need a commit-related
  step" — no, that doesn't fit. Remove.
- "Design to the architecture constitution" — the file references the
  constitution, but the live file doesn't summarize the *tests* the
  agent should run (Cost-of-Change, special-cases, …) the way the
  reviewer does. A new agent would have to read the constitution file.
- No `task: test-lead: allow` — good (planner doesn't run tests).
- No mention of how to handle a request that turns out to be a *defect*
  (the "A defect that escaped is evidence the bar was too low" line is
  in fix.md; planning might need to *recognize* a defect-shaped request
  and route to fix-lead).

---

## 3. build-lead

**Live file:** `.opencode/agents/build-lead.md` (123 lines)
**Catalog file:** `src/aspis/data/catalog/agents/build-lead.md` (121 lines)
**Mode:** primary (live) / subagent (catalog) — promoted at bootstrap · **Model:**
`opencode-go/deepseek-v4-pro` (catalog: `deep`)

### 3.1 Identity

> "the owner of feature implementation. Once a plan is approved, you own
> it until the feature is complete: you coordinate builders, reviews,
> tests, and commits … You are an orchestrator — you do not write most of
> the code yourself; you make the builders that do succeed."

The orchestrator framing is explicit. The build-lead is the system's
**execution spine** for features.

### 3.2 Core role (7-step execution flow)

1. Verify readiness (prestart-checks + build-readiness)
2. Sync feature context (context-ladder)
3. Validate the packet
4. Enrich and delegate (task-orchestration)
5. Test by impact (selective-testing)
6. Coordinate review and commit
7. Track and verify

Plus workflow doc: `.aspis/workflows/build.md`. Plus tool:
`aspis artifact build --task <T-NN>`, mode-gated.

### 3.3 What it does NOT do

- "Write only orchestration artifacts (progress, reports); delegate all
  product code."
- Commit or push (routes through `committer`).
- Start from an unverified state.
- Expand scope or accumulate a whole feature into one long turn.
- Push past a blocker (escalate).

### 3.4 Skills (6)

`prestart-checks`, `context-ladder`, `build-readiness`,
`task-orchestration`, `scope-control`, `selective-testing`.

### 3.5 Delegation (task allow-list)

Live: `general-builder`, `reviewer`, `test-lead`, `fix-lead`,
`committer`, `project-explorer`, `research-lead`. Catalog: same minus
`research-lead`.

- **`test-lead: allow`** but test-lead is missing from live → dangling
  delegate (see §11).
- **`research-lead: allow`** is an addition in live vs. catalog — but it
  matches the build workflow's "research is a service every lead may
  pull from," so this is a likely *fix in catalog* rather than *drift in
  live*.

### 3.6 Permissions

- `read`, `grep`, `glob`, `edit`, `write`: allow.
- `bash`: `git status*`, `git diff*`, `git log*`, `aspis preflight*`,
  `aspis findings*`, `aspis context*`, **`aspis artifact*`**, context
  scripts, planning scripts, **`uv run pytest*`, `pytest*`**.
- **Deny: `git commit*`, `git push*`.**
- `webfetch`: deny · `websearch`: deny

`aspis artifact*` is the right permission for stamping task/feature
reports. `pytest*` is the right permission for "test by impact."

### 3.7 Tools

`read`, `grep`, `glob`, `edit`, `write`, `bash` (allow-listed subset).

### 3.8 Workflow

`.aspis/workflows/build.md` — Readiness → order work → per-task
(delegate/scope/test/review/commit) → track & verify → handoff. The
agent and workflow agree on the per-task review routing: a context-isolated
sub-agent by default, the Reviewer for high-criticality or cross-cutting.

### 3.9 Escalation

> "**If you're stuck, stop — don't guess.** A blocker you can't resolve
> in scope (an ambiguous plan, a gate you can't green, a decision above
> your role) → report it to the Project Lead and wait; never push past it
> or expand scope to work around it."

Clear. Includes the "wait, don't expand" guidance.

### 3.10 Read-first files

L1 hot state, SPEC, as-built architecture
(`.aspis/context/ARCHITECTURE.md`), task list, packets.

### 3.11 Core rules (paraphrased)

1. Never begin from an unverified state.
2. Build to the architecture constitution.
3. Hold the line on scope.
4. Write only orchestration artifacts.
5. Never commit/push (route through committer).
6. Work in small, checkpointed steps.
7. Verify against acceptance.
8. If stuck, stop.

### 3.12 Model

`opencode-go/deepseek-v4-pro` — orchestration tier.

### 3.13 Clarity · Completeness · Consistency assessment

- **Clarity: very high.** 7 numbered steps + per-step skill name + the
  "do not write most of the code yourself" line. A new LLM reading this
  alone would not get confused.
- **Completeness: high.** The "Track and verify" step is the most
  under-specified — it points at `aspis artifact` but doesn't say what
  evidence to record beyond "real changes, tests, and gate output." A
  new agent would have to know the template.
- **Consistency: high.** The review routing ("Reviewer for
  high-criticality … or security") aligns with review.md's
  "escalate to Reviewer for security / cross-cutting."

### 3.14 Gaps & questions

- `test-lead: allow` is a dangling reference (test-lead is not in live).
- Research-lead added vs. catalog — probably *should* be in catalog, not
  drift.
- Step 5 "test by impact" references `selective-testing` — the file
  says "test_depth" comes from the mode overlay. The agent file does
  not mention `.aspis/config/modes.yaml` directly, but the planning-lead
  does. The build-lead might want a sentence like "match test depth to
  the mode set in planning." Today the agent would have to discover
  this in the workflow.
- "Verify completion against acceptance" — the agent file points at
  `SC-###` via the workflow doc, but the live file itself doesn't show
  the template structure for the build artifact. A new agent has to
  read the artifact skill/template.

---

## 4. reviewer

**Live file:** `.opencode/agents/reviewer.md` (98 lines)
**Catalog file:** `src/aspis/data/catalog/agents/reviewer.md` (99 lines)
**Mode:** primary (live) / subagent (catalog) — promoted at bootstrap · **Model:**
`opencode-go/minimax-m3` (catalog: `deep`)

### 4.1 Identity

> "the independent quality authority. You answer one question: *should
> this be accepted?* … You do not build or plan; your independence is
> what makes your verdict worth trusting."

The role is **judge, not builder**. Independence is the defining trait.

### 4.2 Core role (4-step approach)

1. Set the strategy (review-strategy)
2. Verify, don't trust (quality-review + context-ladder)
3. Evaluate the dimensions
4. Decide (acceptance-decision)

Plus: review **plans** (pre-build, plan-critic) and **changes**
(during/after build). The dimensions enumerated are: correctness, scope
compliance, architecture, maintainability, reliability, security,
performance, standards, documentation. Tool: `aspis artifact review
--task <T-NN>` and `aspis artifact test`.

### 4.3 What it does NOT do

- "Review read-only — you evaluate and report; you never modify the work."
- Rubber-stamp a lead's claim.
- Approve on description alone.
- "Render a verdict if you lack the evidence to judge" — withhold and
  request.

### 4.4 Skills (5)

`context-ladder`, `review-strategy`, `quality-review`,
`acceptance-decision`, `plan-critic`.

### 4.5 Delegation (task allow-list)

Live: `project-explorer`, **`research-lead`**. Catalog: `project-explorer`
only.

The live adds research-lead — useful when a claim hinges on
current docs/APIs. The catalog is silent; this is a candidate to
*fix in catalog* (reviewer should be able to verify facts via the
research path).

### 4.6 Permissions

- `read`, `grep`, `glob`: allow (no `edit`, no `write`).
- `bash`: `git status*`, `git diff*`, `git log*`, `aspis artifact*`,
  `aspis context*`, context scripts, planning scripts.
- **Deny: `git commit*`, `git push*`.**
- `webfetch`: deny · `websearch`: deny

`aspis artifact*` is the stamp for review/test reports. The absence of
`edit`/`write` enforces the read-only review contract.

### 4.7 Tools

`read`, `grep`, `glob`, `bash` (allow-listed subset). No edit, no write.

### 4.8 Workflow

`.aspis/workflows/review.md` — Strategy → Evaluate → Decide → Route.
Mode overlays match the planning lead's. Good alignment.

### 4.9 Escalation

Implicit via the verdict routing: "rejected with a defect → Fix Lead
(`fix.md`)". "Changes required" routes back to a builder. There is no
explicit "if you're stuck" rule, but "withhold the verdict" + "request
the evidence" serves the same purpose.

### 4.10 Read-first files

> "Load only the context the change touches, in levels (`context-ladder`)."
> Also: as-built architecture (`.aspis/context/ARCHITECTURE.md`) for the
> architecture dimension.

### 4.11 Core rules (paraphrased)

1. Stay independent.
2. Run the constitution checks the reviewer owns.
3. Verify against evidence; don't approve on description.
4. Review is read-only.
5. Be specific (file:line).
6. Match depth to risk.

### 4.12 Model

`opencode-go/minimax-m3` (per agent-models.yaml, the `review` capability
is set to `deepseek-v4-pro`; the file bake shows `minimax-m3`).
**Note:** this conflicts with the per-runtime capability assignment in
`.aspis/config/agent-models.yaml` (review → `deepseek-v4-pro`). The
agent file's baked model is what runs. This is a **live-vs-config
drift** — not an agent-defect, but a system config note.

### 4.13 Clarity · Completeness · Consistency assessment

- **Clarity: high.** 4 numbered steps, the verdict taxonomy (approved /
  approved with notes / changes required / rejected) is named
  explicitly, and the dimensions are listed.
- **Completeness: high.** The "evaluate the dimensions" step is broad —
  the agent has to know what each dimension means. The
  `quality-review` skill presumably covers that. The file points at it
  but doesn't summarize.
- **Consistency: high.** The independence rule is repeated
  ("never review your own work or rubber-stamp"). Routing rejected
  defects to fix-lead matches the fix-lead's role.

### 4.14 Gaps & questions

- Model drift between agent file (`minimax-m3`) and
  `agent-models.yaml` (`deepseek-v4-pro`). Re-running
  `aspis models --apply` will overwrite.
- research-lead added vs. catalog — likely a catalog gap to close, not
  a live defect.
- The reviewer covers "security" as a dimension but has no security
  skill referenced; the only skills that touch security are in the
  system-lead's lane. A new reviewer would have to derive its own
  security lens.
- No explicit "no evidence = no verdict" — the catalog has it, live
  drops it. Re-add.

---

## 5. system-lead

**Live file:** `.opencode/agents/system-lead.md` (108 lines)
**Catalog file:** `src/aspis/data/catalog/agents/system-lead.md` (109 lines)
**Mode:** primary (live) / subagent (catalog) — promoted at bootstrap · **Model:**
`opencode-go/minimax-m3` (catalog: `deep`)

### 5.1 Identity

> "the executive owner of the ASPIS runtime and operating infrastructure.
> The Project Lead owns the project; you own the machine that makes
> ASPIS work inside it."

The "platform, not features" framing is the cleanest of the agents.

### 5.2 Core role

- **Deterministic-first** ladder for evolving the system (script →
  agent → skill → template → workflow).
- **Protected scope**: `.opencode/`, `.claude/`, protected `.aspis/`.
- **Workflow** (no `.aspis/workflows/*.md` reference — appropriate,
  this is the system that *produces* the workflows):
  Classify → inspect state (`system-awareness`) → decide mechanism
  (`deterministic-first`) → author (`asset-authoring`) → validate
  (`system-validation`) → record + hand commit to committer.

### 5.3 What it does NOT do

- "Never edit rules or permissions, or change model routing or security
  posture, without human approval."
- Never commit or push (hand to committer).
- Hand-write per-runtime files (let the adapters translate).
- Skip validation; ship a parse-failing asset.
- Own product features.

### 5.4 Skills (7)

`prestart-checks`, `system-awareness`, `deterministic-first`,
`asset-authoring`, `system-validation`, `system-repair`,
`config-management`.

### 5.5 Delegation (task allow-list)

Live: `project-explorer`, `reviewer`, `committer`. Catalog:
`project-explorer` only.

- Live adds `reviewer` and `committer`. Reviewer makes sense for
  "validate a system change" (independent quality). Committer makes
  sense because system-lead can't commit directly. Both are likely
  catalog gaps, not live defects.

### 5.6 Permissions

- `read`, `grep`, `glob`, `edit`, `write`: allow.
- `bash`: **allow all**, deny `git commit*` and `git push*`.
- **`webfetch`: allow · `websearch`: allow** (live) / `webfetch`: allow
  · `websearch`: **deny** (catalog).

**The websearch drift is a real permission widening.** The catalog
denies websearch; the live file allows it. A new agent reading the
catalog wouldn't reach for web search; the live one would. This
should be reconciled — either with the catalog (and a comment
explaining why system-lead may websearch) or by removing the
allow in the live file.

### 5.7 Tools

`read`, `grep`, `glob`, `edit`, `write`, `bash`, `webfetch`, `websearch`.

### 5.8 Workflow

No `.aspis/workflows/*.md` reference. The "How you work" section is the
workflow, in-line. This is appropriate — system-lead is the *source*
of workflows; its own procedure is in the agent file.

### 5.9 Escalation

> "Stop and request human approval for any change to rules, permissions,
> security posture, or model routing."

This is the most explicit escalation gate in the live set. Good.

### 5.10 Read-first files

> "inspect current state and dependencies (`system-awareness`)". The
> agent file doesn't enumerate files; that's what the skill does.

### 5.11 Core rules (paraphrased)

1. Understand the system before changing it.
2. Author runtime-neutral assets.
3. Validate every change.
4. Keep dependent files consistent.
5. Never edit rules/permissions/security/model-routing without human
   approval.
6. Never commit/push.

### 5.12 Model

`opencode-go/minimax-m3` (catalog: `deep`).

### 5.13 Clarity · Completeness · Consistency assessment

- **Clarity: very high.** The "deterministic-first ladder" is the
  crispest rule in the agent set. The protected-scope paragraph
  prevents drift into the project's own features.
- **Completeness: high.** The escalation rule is the only
  "stuck-on-decision" guidance, and it's specific (rules /
  permissions / security / model routing).
- **Consistency: high.** Doesn't conflict with other leads; the
  protected-scope rule is what the project-lead's "no edits, no
  commits" rule assumes.

### 5.14 Gaps & questions

- websearch drift (live allows, catalog denies) — reconcile.
- Reviewer/committer added to task list vs. catalog — likely catalog
  gaps, not live defects. But the catalog is the source of truth, so
  they should be added there.
- The system-lead has no frontmatter `task: *: deny` followed by an
  explicit allow-list for *its own* sub-workers. The current list is
  sufficient today, but the file is the place a future "system-validator
  worker" would be added.
- The system-lead's role description includes "system-validation" and
  "system-repair" as skills but the live role text doesn't say *how*
  it repairs. The skill presumably covers it, but a one-line "if the
  runtime is broken, the recovery path is …" would help a new agent
  on first contact.

---

## 6. fix-lead

**Live file:** `.opencode/agents/fix-lead.md` (81 lines)
**Catalog file:** `src/aspis/data/catalog/agents/fix-lead.md` (81 lines)
**Mode:** subagent · **Model:** `opencode-go/minimax-m3` (catalog: `deep`)

### 6.1 Identity

> "the recovery authority. When something is broken — a bug, a failure,
> a regression — you restore correct behavior by understanding and
> fixing the *cause*, not by silencing the symptom."

### 6.2 Core role (6 steps)

1. Verify readiness (prestart-checks)
2. Reproduce (root-cause-analysis)
3. Find the root cause (context-ladder)
4. Apply the smallest safe fix (corrective-fix + scope-control)
5. Verify (selective-testing)
6. Report and hand to committer

### 6.3 What it does NOT do

- "Fix the cause, not the symptom — avoid temporary patches that hide
  the problem."
- Weaken or delete tests.
- Plan features or build new ones.
- Commit or push.
- Patch blindly if the cause is unclear (escalate).

### 6.4 Skills (6)

`prestart-checks`, `context-ladder`, `root-cause-analysis`,
`corrective-fix`, `scope-control`, `selective-testing`. 1:1 with the
6-step process.

### 6.5 Delegation (task allow-list)

Live: `reviewer`, **`test-lead`**, `committer`, `project-explorer`.
Catalog: `reviewer`, `committer`, `project-explorer`.

**The live task list adds `test-lead` — and test-lead is missing from
live.** Same dangling-delegate pattern as project-lead and build-lead.
The catalog is correct (no test-lead delegate for fix-lead); live has
drifted.

### 6.6 Permissions

- `read`, `grep`, `glob`, `edit`, `write`: allow.
- `bash`: **allow all**, deny `git commit*` and `git push*`.
- `webfetch`: deny · `websearch`: deny

The broad `bash` allowance makes sense for a debugger (run any tool to
reproduce). The absence of web search is appropriate — fixing is about
*this* code, not external research.

### 6.7 Tools

`read`, `grep`, `glob`, `edit`, `write`, `bash` (allow-all except
commit/push).

### 6.8 Workflow

References `.aspis/workflows/fix.md`. The fix workflow (30 lines) is
the shortest, focused on reproduce → scope → correct → verify →
commit.

### 6.9 Escalation

> "**If you're stuck, stop — don't guess.** If you can't reproduce the
> failure or the cause is outside your scope/role, report to the Project
> Lead rather than patching blindly."

### 6.10 Read-first files

Logs, the diff, git history, "the relevant context" via
context-ladder. The fix workflow adds: "the failure signal: the error,
the failing test/gate output, or the rejection notes."

### 6.11 Core rules (paraphrased)

1. Fix the cause, not the symptom.
2. Never begin from an unverified state.
3. Keep the fix minimal and in-scope.
4. Every fix is proven (reproduce-then-pass).
5. Never commit/push.
6. If stuck, stop.

### 6.12 Model

`opencode-go/minimax-m3` (catalog: `deep`).

### 6.13 Clarity · Completeness · Consistency assessment

- **Clarity: high.** 6 numbered steps, each with a named skill. The
  "fix the cause, not the symptom" rule is repeated in the role and
  in the rules.
- **Completeness: high.** The "reproduce-then-pass" requirement is
  specific. "Fixes default to production rigor regardless of the
  feature's mode" sets the bar correctly.
- **Consistency: high.** Aligns with the build-lead's escalation
  language.

### 6.14 Gaps & questions

- `test-lead: allow` is a dangling reference.
- The "scope" skill (`scope-control`) is also in the build-lead's
  skill set — both leads need it. Good reuse.
- No mention of "if a fix touches a *system* asset, defer to
  system-lead" — for a protected-path fix, the system-lead probably
  owns the change. The role says "the cause is outside your
  scope/role → report to the Project Lead." Could be more specific:
  "if the failure is in `.opencode/`, `.claude/`, or protected
  `.aspis/`, hand to system-lead."
- No mention of when a fix should be promoted to a *feature* (a
  deeper change). The small-task workflow says "a defect with an
  unclear cause → fix.md," but the converse — a fix that grows —
  isn't addressed.

---

## 7. research-lead

**Live file:** `.opencode/agents/research-lead.md` (69 lines)
**Catalog file:** `src/aspis/data/catalog/agents/research-lead.md` (64 lines)
**Mode:** subagent · **Model:** `opencode-go/minimax-m3` (catalog: `deep`)

### 7.1 Identity

> "the knowledge layer of the system. When planning, building,
> reviewing, fixing, or system work hits an unknown, you find the answer
> from authoritative sources, verify it's current, and package it so
> it's never researched again. You serve every other lead; you do not
> build, plan, or review."

### 7.2 Core role (4 steps)

1. Scope the question (context-ladder)
2. Research from authority (knowledge-research)
3. Validate
4. Package for reuse (knowledge-packaging)

### 7.3 What it does NOT do

- Build, plan, or review.
- "Stay in your lane: you supply knowledge; planning and building
  decide what to do with it."
- Deliver a raw dump — package as a reference.

### 7.4 Skills (3)

`context-ladder`, `knowledge-research`, `knowledge-packaging`. The
smallest skill surface in the live set; well-scoped to the role.

### 7.5 Delegation (task allow-list)

`project-explorer` only. The most locked-down task list in the live
set — appropriate for a research-only agent.

### 7.6 Permissions

- `read`, `grep`, `glob`, `write`: allow. **No `edit`.**
- `bash`: deny all except `python .aspis/scripts/context/*`.
- `webfetch`: allow · `websearch`: allow

**The `write` without `edit` asymmetry is odd.** An agent that
researches typically doesn't author source files; the `write` is for
*knowledge assets* (packaging). The asymmetry is probably intentional
("I produce packaged references, not source edits") but the role text
doesn't say that explicitly.

The bash surface is *very* tight (context scripts only). The role can
fetch from the web, but it cannot `git status` or run any other shell
command. That matches the "no code changes" lane.

### 7.7 Tools

`read`, `grep`, `glob`, `write`, `webfetch`, `websearch`, `bash`
(allow-listed subset).

### 7.8 Workflow

**No `.aspis/workflows/*.md` reference.** Research has no formal
workflow doc. The "How you work" section in the agent file *is* the
procedure. A research.md workflow doc would be a reasonable addition,
but the role is small enough to be self-contained.

### 7.9 Escalation

None explicit. The "stay in your lane" rule is the closest thing — it
sends a discovery that requires planning to the planning lead via the
delegating lead.

### 7.10 Read-first files

L1 hot context first (context-ladder). No specific file list in the
agent.

### 7.11 Core rules (paraphrased)

1. Research once, reuse everywhere.
2. Prefer authoritative sources; record source + version.
3. Separate fact from assumption.
4. Deliver a packaged reference.
5. Stay in your lane.

### 7.12 Model

`opencode-go/minimax-m3` (catalog: `deep`).

### 7.13 Clarity · Completeness · Consistency assessment

- **Clarity: high.** The 4-step procedure is tight; the role is
  narrow by design.
- **Completeness: medium.** The file says "validate" and "package" but
  doesn't show what a packaged reference looks like. The skill
  presumably does. A first-time agent would have to read the skill.
- **Consistency: high.** Doesn't conflict with other agents.

### 7.14 Gaps & questions

- No explicit escalation rule ("if I'm stuck"). The closest is "stay
  in your lane."
- No workflow doc reference.
- `write` without `edit` — should be explained in the role text, or
  `edit` should be added (and the asymmetry removed).
- The agent has no `task: project-explorer: allow` as a *frequent*
  dependency; it's there but the role text doesn't say "delegate
  codebase lookup to project-explorer" the way the other leads do.
- No mention of *caching* strategy — the role says "package for
  reuse" but doesn't say where the cache lives or how to find an
  existing reference. A new agent would search the knowledge
  artifacts dir, but that's only documented in the
  `knowledge-packaging` skill.

---

## 8. general-builder

**Live file:** `.opencode/agents/general-builder.md` (52 lines)
**Catalog file:** `src/aspis/data/catalog/agents/general-builder.md` (51 lines)
**Mode:** subagent · **Model:** `opencode-go/minimax-m3` (catalog: `cheap`)

### 8.1 Identity

> "a disposable execution worker. You receive one task packet from the
> Build Lead, implement exactly that task, prove it works, and report
> back. You do not own the feature, plan the work, or persist beyond
> the task."

The most constrained role in the set: a single task, single packet,
single report, exit.

### 8.2 Core role (4-step lifecycle)

1. Read the packet
2. Implement (allowed files only)
3. Test
4. Report

### 8.3 What it does NOT do

- Touch forbidden paths or expand scope.
- Weaken/delete tests.
- Commit or push.
- Persist beyond the task.

### 8.4 Skills (2)

`prestart-checks`, `clean-tree-precondition`. The smallest skill
surface. The agent is supposed to *execute the packet*, not to apply
domain skills — the packet should contain whatever domain knowledge is
needed.

### 8.5 Delegation (task allow-list)

**None.** `task: *: deny` is implicit (no `task` block in the
frontmatter). The general-builder is a leaf worker — it does not
delegate. This is correct for a disposable executor.

### 8.6 Permissions

- `read`, `grep`, `glob`, `edit`, `write`: allow.
- `bash`: allow all except `git commit*` and `git push*`.
- `webfetch`: deny · `websearch`: deny

The broad bash allowance is appropriate for an executor (run any test
command, any build tool). The no-web is appropriate — workers don't
research; the research lead does.

### 8.7 Tools

`read`, `grep`, `glob`, `edit`, `write`, `bash` (allow-all except
commit/push).

### 8.8 Workflow

**No `.aspis/workflows/*.md` reference.** The general-builder is a
leaf — its procedure is the packet. The Lifecycle section is its
workflow.

### 8.9 Escalation

> "If blocked, or the change needs work outside the packet, STOP and
> report what's needed rather than guessing."

Clean stop-and-report. "STOP" is in caps — intentional emphasis.

### 8.10 Read-first files

"The packet is your whole context — read its references, not the wider
repo." Specific anti-pattern guidance (don't read the wider repo) is
excellent for an LLM.

### 8.11 Core rules (paraphrased)

1. Run preflight first; stop on a dirty tree.
2. Stay strictly inside allowed files.
3. Never weaken/delete tests.
4. Never commit/push.
5. If blocked, stop.

### 8.12 Model

`opencode-go/minimax-m3` (catalog: `cheap`).

### 8.13 Clarity · Completeness · Consistency assessment

- **Clarity: very high.** Short, scannable, every rule points at a
  concrete action.
- **Completeness: high for the role's scope.** The role is
  intentionally narrow. The Lifecycle + Rules cover every case.
- **Consistency: high.** Aligns with build-lead's "workers never
  commit."

### 8.14 Gaps & questions

- "The packet is your whole context" — but the agent has no
  `task:` to receive a packet. The packet arrives as part of the
  task invocation from the build-lead. This is implied; an LLM
  reading the file alone wouldn't know where the packet comes from.
  A one-line "you are invoked by the Build Lead with a packet"
  would help.
- No mention of how to handle a packet that is *thin* (missing
  references, vague acceptance). A first-time builder might patch
  over gaps. The build-lead's "Validate the packet" step is the
  counter, but the worker should also have a self-check.
- No mention of returning a **distilled summary** as the build-lead
  expects ("short distilled summary (files, result, risks), not raw
  output") — that lives in the build-lead's rules, not the worker's.
  The worker should mirror it.

---

## 9. committer

**Live file:** `.opencode/agents/committer.md` (71 lines)
**Catalog file:** `src/aspis/data/catalog/agents/committer.md` (70 lines)
**Mode:** subagent · **Model:** `opencode-go/deepseek-v4-flash` (catalog:
`cheap`)

### 9.1 Identity

> "the single point through which commits are made, so commit quality
> and scope are consistent. A lead hands you reviewed, gate-green work;
> you verify and commit it. You never write product code and never
> push."

The role is the **only writer to the git history**.

### 9.2 Core role (4 steps)

1. Confirm scope (git status / git diff)
2. Commit with the tool (`aspis commit <path> … --type … --task …`)
3. Fallback to raw git only if `aspis` is genuinely unavailable
4. Read the hook output, never force a commit

### 9.3 What it does NOT do

- Push.
- Edit files.
- Amend history without being asked.
- Stage `git add -A` / `.`.
- Add AI/model/tool attribution.
- Hand-format around the tool (except the documented fallback).

### 9.4 Skills (3)

`commit-message`, `commit-splitting`, `clean-tree-precondition`. Three
narrow, commit-specific skills.

### 9.5 Delegation (task allow-list)

**None.** No `task` block in frontmatter. The committer is invoked by
leads that need a commit; it doesn't delegate.

### 9.6 Permissions

- `read`, `grep`, `glob`: allow. **No `edit`, no `write`.**
- `bash`: deny all **except** `git status*`, `git diff*`, `git log*`,
  `aspis commit*`, `git add*`, `git commit*`; `git push*`: deny.

The `aspis commit*` allow + `git add*`/`git commit*` allow matches the
"primary tool + raw fallback" design. The deny on `git push*` is
critical and present.

### 9.7 Tools

`read`, `grep`, `glob`, `bash` (allow-listed subset). No edit, no
write.

### 9.8 Workflow

**No `.aspis/workflows/*.md` reference.** The Procedure section in
the agent file *is* the workflow.

### 9.9 Escalation

> "If the hook blocks (or warns about something real — scope, secret,
> protected path, message), stop and report rather than forcing the
> commit."

Clean stop. No "guess" path.

### 9.10 Read-first files

`commit-convention.yaml` (named), git status, git diff. The
`commit-message` skill presumably shows the convention format.

### 9.11 Core rules (paraphrased)

1. Commit only what was reviewed and intended.
2. One commit = one logical change.
3. Use `aspis commit`; hand-format only in the documented fallback.
4. Never push, never edit files, never amend without being asked.
5. Start from a clean tree.

### 9.12 Model

`opencode-go/deepseek-v4-flash` (catalog: `cheap`). No `temperature`
in frontmatter. Every other live agent has `temperature: 0.1`. The
committer's commits should be deterministic; the omission should be
fixed.

### 9.13 Clarity · Completeness · Consistency assessment

- **Clarity: very high.** The 4-step procedure is exact, and the
  fallback rules are explicit. The "Always use `aspis commit`" line
  is the right anchor.
- **Completeness: high.** The fallback path is documented. The
  report-back rule ("report that the fallback was used and why") is
  the right escape hatch.
- **Consistency: high.** "Workers never commit" (build-lead,
  general-builder) is enforced by giving the committer the only
  commit permission.

### 9.14 Gaps & questions

- **No `temperature: 0.1`** in the live file. Add for consistency.
- **No `name:` field** in frontmatter (other agents have it; the
  committer file uses an implicit name from the filename). Cosmetic.
- **No `mode:` field** either — present in catalog. Cosmetic.
- The `git add*` allow is broad — `git add*` matches `git add -A`
  too. The agent's rules forbid `git add -A`, but the *permission*
  allows it. A safer permission would be `git add <path>:*` (path
  arg required) — but that's hard to express in shell-glob form.
  The rules protect, the permission is broader. Acceptable.
- The fallback section says "If the `aspis` command is not found
  (not merely a convention warning), fall back to raw git." — the
  rules and the fallback path could conflict if a hook warning is
  misread as a missing-`aspis` signal. A new agent might use the
  fallback when it shouldn't. The role text should be even more
  specific ("missing-`aspis` means the executable isn't on PATH, not
  a hook warning").

---

## 10. project-explorer

**Live file:** `.opencode/agents/project-explorer.md` (50 lines)
**Catalog file:** `src/aspis/data/catalog/agents/project-explorer.md` (53 lines)
**Mode:** subagent · **Model:** `opencode-go/minimax-m3` (catalog: `cheap`)

### 10.1 Identity

> "a disposable, read-only exploration helper. A lead hands you a
> focused question about the codebase; you find the answer and return
> a compact summary, then exit. You hold no long-term state and you
> change no product code."

The "disposable" framing is the right contract — no memory, no edits.

### 10.2 Core role (5 steps)

1. Orient from the index
2. Run the code-map tool for a narrower skeleton
3. grep/glob for symbols/usages
4. Open only the few files needed
5. Return a compact result

### 10.3 What it does NOT do

- Edit or write product code.
- Run anything other than `.aspis/scripts/context/*` from bash.
- Expand into unrelated areas.
- Paste file dumps.
- Guess when "not found" is the honest answer.

### 10.4 Skills

**None listed in frontmatter.** The agent has no `skill` block (catalog
has none either). The role is procedural enough that skills aren't
needed — the procedure is the agent.

### 10.5 Delegation (task allow-list)

**None.** The explorer is a leaf helper. Correct — it doesn't fan
out.

### 10.6 Permissions

- `read`, `grep`, `glob`: allow. No `edit`, no `write`.
- `bash`: deny all **except** `python .aspis/scripts/context/*`.
- `webfetch`: deny · `websearch`: deny

The bash surface is the tightest in the set (just the context
scripts). The explorer cannot run any other command — the read-only
contract is fully enforced.

### 10.7 Tools

`read`, `grep`, `glob`, `bash` (context scripts only).

### 10.8 Workflow

**No `.aspis/workflows/*.md` reference.** The "How you work" section
*is* the workflow. The procedure is short and well-scoped.

### 10.9 Escalation

> "A clear 'not found' when nothing matches — never a guess."

This is the agent's "if stuck" rule. It escalates by **not making
something up**.

### 10.10 Read-first files

`.aspis/index/FILE_REGISTRY.yaml`, `.aspis/index/CODE_MAP.md`. These
are the agent's only required reads.

### 10.11 Core rules (paraphrased)

1. Read-only on product code.
2. Run only context scripts.
3. Stay scoped to the question.
4. Summarize, don't paste.

### 10.12 Model

`opencode-go/minimax-m3` (catalog: `cheap`).

### 10.13 Clarity · Completeness · Consistency assessment

- **Clarity: very high.** The role is small, the steps are
  numbered, the "what you return" section is specific.
- **Completeness: high for the role.** "A clear 'not found' when
  nothing matches" is exactly the right behavior.
- **Consistency: high.** No conflicts; no other agent tries to be
  read-only.

### 10.14 Gaps & questions

- No `temperature: 0.1` in live; other agents have it. Add for
  consistency.
- No `name:` field (cosmetic).
- The "How you work" step 2 mentions running
  `build_code_map.py --scope <path>`, but the agent has no
  instructions on what to do if the scope path is invalid. The
  bash permission allows the script regardless; the agent file
  should add "if the script fails, return 'not found' for that
  scope."
- The agent has no `task:` block. Fine, but the project-lead's
  text says "delegate exploration to `project-explorer`" — the
  build-lead's task list also includes `project-explorer: allow`.
  Consistent.

---

## 11. test-lead — the missing live agent

**Live file:** ❌ does not exist in `.opencode/agents/`
**Catalog file:** `src/aspis/data/catalog/agents/test-lead.md` (64 lines)
**Catalog mode:** subagent · **Catalog model:** `standard`

### 11.1 Why this is the most important finding

Three live agents reference `test-lead` as a delegable, and the
reviewer invokes the `aspis artifact test` command — but no live
agent file exists:

- **project-lead** task allow-list: `test-lead: allow`
- **build-lead** task allow-list: `test-lead: allow`
- **fix-lead** task allow-list: `test-lead: allow`
- **reviewer** core role step 4: "`aspis artifact test` for a test
  run"

If a runtime tries to honor any of those, the delegation has nothing
to land on. This is the single most concrete gap in the live system.

### 11.2 What the catalog says the role is

> "the validation authority. You determine whether software actually
> behaves as expected and turn that into objective evidence the rest of
> the system can rely on. You generate and run tests and report what
> they show. You do not approve the work — you give the Reviewer and
> the leads the evidence to decide."

The role is **evidence producer, not verdict renderer**. The
Reviewer remains the judge; the Test Lead feeds the judge. This is
the right separation of powers, but it's enforced by the live
agent's absence.

### 11.3 What the live system does *without* test-lead

The build workflow (`build.md`) has the build-lead run
`selective-testing` for each task; the test-lead is a *parallel*
validation path for deeper, more rigorous testing. With test-lead
absent, the system still works (the build-lead's `pytest*` bash
permission and the `selective-testing` skill cover the test
execution role), but:

- The "evidence layer" is just the build-lead's evidence, not an
  independent validator.
- The reviewer is more likely to be the *sole* independent quality
  voice, conflating "did the tests pass" with "is this acceptable."
- The fix-lead cannot delegate a focused test reproduction to a
  specialist — the fix-lead itself has to reproduce, which is
  fine, but loses parallelism.

### 11.4 Recommendation (out of scope here, but recorded)

The test-lead should be re-rendered to `.opencode/agents/`. The
catalog asset is complete; `aspis models --apply` plus a render
should bring it back. Until then, the live task allow-lists in
project-lead / build-lead / fix-lead should remove the dangling
`test-lead: allow` line — or the live should be considered
"test validation goes through the Reviewer, not a dedicated test
lead."

---

## 12. Cross-agent consistency matrix

| Concern | project-lead | planning-lead | build-lead | reviewer | system-lead | fix-lead | research-lead | general-builder | committer | project-explorer | test-lead (catalog) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Can edit product code? | ❌ | ❌ (templates only) | ❌ (orchestration only) | ❌ | ✅ (system) | ✅ | ❌ (write only) | ✅ | ❌ | ❌ | ✅ |
| Can commit? | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ (only) | ❌ | ❌ |
| Can push? | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Can web search? | ❌ | ❌ | ❌ | ❌ | ✅ (live drift) | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Has a workflow doc? | indirect | `.aspis/workflows/plan.md` | `.aspis/workflows/build.md` | `.aspis/workflows/review.md` | in-line | `.aspis/workflows/fix.md` | ❌ | ❌ | ❌ | ❌ | ❌ |
| "If stuck, stop" rule? | implicit | ✅ | ✅ | implicit (withhold verdict) | ✅ (specific gate) | ✅ | implicit | ✅ | implicit | implicit ("not found") | ✅ |
| References constitution? | ✅ (delegation) | ✅ (design) | ✅ (build) | ✅ (checks it owns) | ✅ (asset authoring) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Has mode `primary`? | ✅ | ✅ (post-bootstrap) | ✅ (post-bootstrap) | ✅ (post-bootstrap) | ✅ (post-bootstrap) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

**Findings from the matrix:**

- The "no commit" boundary is universally enforced at the bash
  permission level (`git commit*: deny`) for all agents except
  the committer. Good defense in depth.
- The "no push" boundary is universal. Good.
- The "can edit product code" surface is correctly bounded to
  the agents that need it: system-lead, fix-lead,
  general-builder, test-lead (catalog). project-lead,
  planning-lead (mostly templates), reviewer, research-lead,
  committer, project-explorer are read-only or write-only.
- Workflow docs exist for the 4 main leads
  (plan/build/review/fix) and are referenced from the matching
  agent files. The other 5 agents run from in-line procedure —
  appropriate for their smaller scope.
- The "if stuck, stop" rule is present in 5 of 10 live agents
  and implicit in the other 5 (reviewer, committer,
  project-explorer, project-lead, research-lead). Adding the
  rule explicitly to those 5 would make the system more
  consistent.

---

## 13. Findings — what the analysis says about the agent system

### 13.1 What's working well

1. **Clear role boundaries.** Each agent has an "Identity"
   paragraph that states what it is *not*. The "you do not …"
   lines are repeated in the rules. An LLM reading any single
   file would not mistake its role.
2. **Identity is one paragraph; behavior is numbered steps.** The
   10 live files all follow a consistent shape: Identity → How
   you X → Core rules → Responsibilities → skills table →
   Delegation. This is itself a system feature: the shape is
   legible.
3. **The 5-primary / 5-subagent split is honored.** project-lead,
   planning-lead, build-lead, reviewer, system-lead are
   `mode: primary`; the other 5 are `mode: subagent`. The
   primary/subagent split maps to "user can invoke directly" vs.
   "invoked by a primary," which matches the runtime model.
4. **No agent can push.** `git push*: deny` is universal. This is
   the single most important safety property and it's enforced
   in 10/10 agents.
5. **The "one simple change" the project-lead owns is well-scoped.**
   `aspis mode*` is the only write through the orchestrator.
6. **The deterministic-first ladder in system-lead is the right
   rule.** The 5-step ladder (script → agent → skill → template
   → workflow) is the most specific guidance in the live set.
7. **The architecture-constitution rule is referenced in 3
   places** (planning, build, reviewer), with each agent owning
   a distinct check. The cost-of-change test and the
   "extension-not-special-case" rule are the spine.
8. **Workflow docs are aligned with their owning agents.** The
   4 workflow files (plan/build/review/fix) match the 4
   corresponding agent files step-for-step.

### 13.2 Gaps, drift, and risks

#### 13.2.1 Critical — runtime gap

- **test-lead is not deployed in live.** Referenced by
  project-lead, build-lead, fix-lead, and reviewer. The catalog
  has the asset. Re-render to `.opencode/agents/test-lead.md`
  with `aspis models --apply`, or remove the dangling delegates
  and accept that the build-lead's `selective-testing` is the
  system's only validation path. (See §11.)

#### 13.2.2 Live-vs-catalog drift

| # | Drift | Live value | Catalog value | Risk | Suggested fix |
|---|---|---|---|---|---|
| 1 | committer in project-lead task list | `committer: allow` | absent | Project-lead could route commits it shouldn't own. | Remove from project-lead. |
| 2 | committer in planning-lead task list | `committer: allow` | absent | Planning-lead could commit a template change. | Remove from planning-lead. |
| 3 | test-lead in project-lead task list | `test-lead: allow` | present | Dangling (test-lead not deployed). | Re-render test-lead or remove delegate. |
| 4 | test-lead in build-lead task list | `test-lead: allow` | present | Dangling. | Same. |
| 5 | test-lead in fix-lead task list | `test-lead: allow` | absent | Dangling + drift. | Remove from fix-lead. |
| 6 | research-lead in reviewer task list | `research-lead: allow` | absent | Reviewer can pull research — useful but undocumented in catalog. | Add to catalog. |
| 7 | research-lead in build-lead task list | `research-lead: allow` | absent | Build-lead can pull research during a task — useful. | Add to catalog. |
| 8 | reviewer in system-lead task list | `reviewer: allow` | absent | System-lead can request independent validation. | Add to catalog. |
| 9 | committer in system-lead task list | `committer: allow` | absent | System-lead routes commits through committer. | Add to catalog. |
| 10 | system-lead `websearch` | `allow` | `deny` | System-lead can search the web (catalog says no). | Reconcile — either add a comment explaining why system-lead may search, or change live to `deny`. |
| 11 | committer `temperature` | absent | `0.1` (implicit by file shape) | Commits should be deterministic; no temperature is set. | Add `temperature: 0.1`. |
| 12 | Bootstrap gate in project-lead | absent | present (`<!-- ASPIS:BOOTSTRAP-GATE -->`) | Re-bootstrap path is no longer self-documented. | Acceptable post-bootstrap; the gate is removed by design. |
| 13 | Live model field | `opencode-go/deepseek-v4-pro` etc. | `standard`/`deep`/`cheap` | Catalog uses tiers, live uses concrete models. | Expected: `aspis models --apply` materializes the model name. |
| 14 | Mode for planning/build/reviewer/system | `primary` | `subagent` | Bootstrap promoted them. | Expected: bootstrap post-condition. |
| 15 | Model for reviewer | `minimax-m3` (file) | `deepseek-v4-pro` (config) | `agent-models.yaml` says review → `deepseek-v4-pro`; the agent file bake says `minimax-m3`. | Re-run `aspis models --apply` to reconcile. |

#### 13.2.3 Coverage gaps (use cases no agent explicitly owns)

- **Documentation / comment-only changes.** The small-task
  workflow covers trivial edits, but no agent is specialized for
  docs. The planning lead plans docs as features, the build
  lead executes them; no docs-specialist reviewer. Acceptable
  for a production system, but a `docs-builder` could be a
  future extraction per the deterministic-first rule.
- **Release / tag / changelog management.** The system-lead
  owns system releases (the catalog mentions "release" in the
  committer's `--no-scope` for repo-lifecycle commits), but no
  dedicated release agent. The system-lead + committer cover
  it, but a release workflow doc is missing
  (`.aspis/workflows/release.md` doesn't exist).
- **Onboarding / first-run.** `bootstrap.md` exists in the
  catalog but is `export-only` (removed after first run). The
  live project-lead file no longer has the bootstrap gate. A
  re-bootstrap or a new project would need a manual step.
- **Migration / upgrade of ASPIS itself.** The system-lead
  owns evolving the system, but a specific
  `aspis-migrate` workflow (taking a project from one ASPIS
  version to the next) is not present. The deterministic-first
  rule says "build what is needed, when it is needed" — so
  this is a future feature, not a current gap.
- **Reactive ops (alerts, scheduled tasks).** No agent
  owns "wake up and check" tasks. Acceptable — ASPIS is
  request-driven today.

#### 13.2.4 Workflow / skills coverage

Every responsibility in every agent maps to a skill that exists
in `.opencode/skills/`. The 38 skills listed match the agents'
responsibility tables 1:1. No agent references a missing skill.

The four `.aspis/workflows/*.md` files (plan, build, review, fix,
small-task) cover the four primary tracks. The
`small-task.md` workflow is referenced from project-lead but
has no dedicated agent — it routes through build-lead (which
makes sense for "small task = one packet" — it's a one-packet
build).

The `research-lead` has no workflow doc; this is acceptable for
its narrow role. Same for `general-builder`, `committer`,
`project-explorer`.

#### 13.2.5 Permission shape

- **`edit` vs `write` asymmetry.** research-lead has `write`
  but no `edit`. This is a deliberate "I author packaged
  references, not source code" signal, but the role text
  doesn't say that. Either document the asymmetry or
  unify.
- **`websearch` and `webfetch` are split correctly** in most
  agents (web research for system-lead and research-lead
  only). The system-lead `websearch: allow` (live) vs
  `deny` (catalog) is the only inconsistency.
- **`pytest*` is allowed in build-lead only.** The
  general-builder has `bash *: allow` and would inherit
  `pytest*` — so the test-execution permission lives in
  both places, by design (the build-lead orchestrates, the
  builder runs).
- **The `committer` has the only `git commit*: allow` and
  the only `git add*: allow`.** Correct enforcement of the
  "one writer" rule.

#### 13.2.6 Frontmatter consistency

Some agents have a sparse frontmatter (committer, project-explorer
lack `name:`, `temperature:`, `mode:` in different combinations).
The catalog versions are the canonical shape; live has drifted
on the per-agent materialization. Not a defect, but a uniformity
note: a linter or `aspis agents --validate` should enforce the
shape.

---

## 14. Summary — one paragraph

The current ASPIS agent system is **well-architected and largely
self-consistent** — every agent has a clear role, every role
references a real skill, and the safety boundaries (no push, no
untracked commit, protected paths only via system-lead) are
correctly enforced. The two material issues are (1) the **missing
test-lead in live**, referenced by 3 of the 5 primaries, and
(2) **task-allow-list drift** that adds `committer` to
project-lead and planning-lead (where it should not be) and
`test-lead` to three agents (where it points at nothing). A
secondary set of drifts — `system-lead` `websearch: allow` vs
catalog `deny`, the committer's missing `temperature`, the
reviewer's model file vs config — are easy fixes. The
`<!-- ASPIS:BOOTSTRAP-GATE -->` removal from the live
project-lead is the **correct** post-bootstrap state; the
catalog is the source of truth for re-bootstrap. The biggest
*coverage* gap is that no agent is specialized for docs-only
changes, but the deterministic-first rule says "build what is
needed when it is needed" — the absence is a feature, not a
defect. A new agent, given any single live file plus the four
workflow docs, has enough to act; given the live set as a whole,
it has enough to know its peers.
