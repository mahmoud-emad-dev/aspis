# F-016 — Agent Permissions, Control & Reliability in Production Agentic Systems

> Research produced for the F-016 agent-system-architecture feature. Sources
> verified as of **2026-06-25**. Every claim is sourced; sources are listed at
> the end of each section. Where a system's design has moved on, the current
> successor is noted.

## How to read this

- §1 is the **executive summary** — the top 5 patterns to take into F-016.
- §2 is the **source landscape** — a compact map of who does what.
- §3 covers the eight topics the Planning Lead asked about, in order.
- §4 names the **implications for ASPIS** specifically — what the catalog
  already has, what is missing, what the feature should adopt or skip.
- §5 is the **source ledger** — every URL, with version stamps.

The research question, paraphrased: *how do production agentic systems
constrain, sequence, and recover — and what does that mean for ASPIS?*

---

## 1. Executive summary — the top 5 patterns

These five patterns recur across the surveyed systems and are the ones F-016
should treat as load-bearing. Each is named, sourced, and the "what this means
for ASPIS" point is one line.

### Pattern 1 — Tiered, rule-based tool permission with deny-wins precedence

Read-only tools run without prompts; mutating tools run with prompts. Rules are
expressed in a data file (`allow` / `ask` / `deny` lists, glob patterns),
evaluated in a fixed order (deny → ask → allow), with the first match winning.
A bare-name deny rule removes the tool from the agent's context entirely;
scoped denies block matching calls. Settings precedence is **managed → CLI →
local → shared → user**; a deny from any scope blocks an allow from any other.

- **Source of the most detailed implementation:** Claude Code permissions
  (code.claude.com/docs/en/permissions, current as of mid-2026).
- **Adopted in:** Claude Code, Cursor (rule-based LLM controls per its
  security page), OpenAI Agents SDK (tool filtering, swarm's
  `execute_tools=False` predecessor), and to a lesser extent AutoGen
  AgentChat (workbench/function registration).
- **What this means for ASPIS:** the F-006 hooks already implement a version
  of this for the *commit boundary*. F-016 should extend the same model to
  the *tool-use boundary* — a single, portable `permission.yaml` the adapter
  renders per runtime, with a fixed `deny → ask → allow` evaluator in
  `.aspis/scripts/hooks/` (the shared-core pattern from D-010). One source,
  one evaluator, two surfaces.

### Pattern 2 — Hooks at the tool boundary, not after

Every production system inspected exposes a hook seam **before** a tool runs
(`PreToolUse`) and **after** (`PostToolUse`), plus lifecycle events
(`SessionStart`, `SubagentStart`/`Stop`, `PreCompact`/`PostCompact`,
`Stop`, `Notification`, `ConfigChange`, `FileChanged`). Hooks are typically
shell commands (deterministic), with optional LLM-judge (`prompt`) and
multi-turn (`agent`) hook types. Exit-code 2 blocks with stderr as feedback
to the model. Multiple hooks on the same event are merged; the most
restrictive answer wins.

- **Source of the most detailed implementation:** Claude Code hooks
  (code.claude.com/docs/en/hooks-guide).
- **Adopted in:** Claude Code (25+ lifecycle events, 5 hook types), Cursor
  (its security page lists "Hooks" as a first-class feature), LangGraph
  (NodeInterrupt / dynamic interrupts, `langgraph` interrupts), CrewAI
  Flows (event-driven hooks via `@start` / `@listen` / `@router`).
- **What this means for ASPIS:** the hook model F-006 already ships is
  the **commit boundary** half. F-016 should add the **tool-use boundary**
  half with the same shared core and the same `enforcement: warn|block`
  switch. The seam is already there; F-016 fills the second surface.

### Pattern 3 — Subagent delegation with isolated context, allowed-list spawning

Lead agents delegate to subagents. The subagent runs in its **own context
window** (so the lead's window isn't flooded) with **its own tool
allowlist** (so it can't do what it wasn't hired to do). The lead
specifies which subagent types it is allowed to spawn — an explicit
allowlist, not a free-for-all. Subagents can spawn nested subagents
(depth-limited in practice). Each subagent declares its model tier, its
memory scope, and its own hooks.

- **Source of the most detailed implementation:** Claude Code subagents
  (code.claude.com/docs/en/sub-agents).
- **Adopted in:** Claude Code (built-in Explore/Plan/general-purpose +
  custom markdown), OpenAI Swarm/Agents SDK (handoffs as first-class
  primitive), CrewAI (hierarchical process with a manager agent),
  AutoGen AgentChat (AgentTool wrapping an agent as a tool).
- **What this means for ASPIS:** the **task packet** (CORE_LOOP §5) is
  already exactly this — context-isolated builder, declared scope,
  declared tools. F-016 should formalise the **subagent definition
  surface** (frontmatter: `name`, `description`, `tools`,
  `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `memory`,
  `isolation`, `hooks`, `skills`) as a catalog asset kind, and add the
  lead-side `Agent(agent_type)` allowlist. ASPIS already has
  `mode: subagent` (D-004); this adds the surface that consumes it.

### Pattern 4 — Deterministic-first: workflows, then agents

Every framework source explicitly recommends *not* reaching for an agent
when a workflow will do. Anthropic's framing: workflows (LLMs orchestrated
by code) and agents (LLMs directing their own tool use) are a spectrum;
start simple, add complexity only when measurements justify it. The
characteristic workflow patterns are: **prompt chaining** (with gates),
**routing** (classify → specialise), **parallelization** (sectioning +
voting), **orchestrator-workers** (dynamic delegation), and
**evaluator-optimizer** (one generates, one critiques). Agents (the
autonomous end) are for open-ended problems where the number of steps
can't be predicted — and the cost is latency, compounding error, and
the need for guardrails.

- **Source of the most-cited statement:** Anthropic, *Building Effective
  Agents* (Dec 2024, the patterns cookbook that goes with it).
- **Adopted in:** OpenAI Swarm (handoffs as a primitive but explicitly
  light-touch; not a framework), Anthropic's own SWE-agent (claims
  SOTA with a thin agent loop + good ACI), CrewAI (Crews for autonomy
  + Flows for control — the dual-track is the product), LangGraph
  (low-level, expects you to compose the workflow), Microsoft Agent
  Framework (replaces AutoGen, leans on the lessons above).
- **What this means for ASPIS:** D-005 ("deterministic-first, build-by-need")
  is the same idea. F-016 should bake the *five workflow patterns* into
  the catalog as named templates (so a feature can declare "I am a
  prompt-chain" or "I am an orchestrator-workers" and inherit the
  checklist), and the core loop should treat the workflow doc (§9 of
  CORE_LOOP) as a first-class asset.

### Pattern 5 — Trace, persist, and resume; the tool interface is the lever

Reliability comes from two complementary choices: **(a) durable execution
+ checkpoints** so a failed run resumes from the last known good state;
and **(b) a deliberately constrained tool interface** — the
"Agent-Computer Interface" (ACI) — that makes mistakes hard to make.
ACI design (SWE-agent's term) means: custom file viewers with scroll,
succinct search that lists files rather than matches, a linter on edit
that blocks unsyntactic changes, an empty-output handler that says
"ran successfully and produced no output", and poka-yoke tool args
(e.g., require absolute paths so the model can't get lost after a
`cd`). Trace + persist means a checkpointer per thread (LangGraph
term) that snapshots state, plus an event log that makes every
action attributable.

- **Source of the ACI framing:** SWE-agent (Princeton/Stanford, NeurIPS
  2024, the ACI background doc).
- **Source of the durable execution framing:** LangGraph
  (docs.langchain.com/oss/python/langgraph/durable-execution —
  checkpointers, time travel, fault tolerance).
- **Adopted in:** SWE-agent (the four ACI pillars above), LangGraph
  (durable execution + checkpointers + stores), CrewAI ("tracing and
  observability" as a first-class AMP feature), Cursor ("compliance
  logging" / audit logs in its security page), OpenAI Agents SDK
  (swarm's `Response` object as the serialisable handoff state).
- **What this means for ASPIS:** the **post-commit hook already
  refreshes the brain** — a kind of checkpoint. F-016 should add
  **(a) a per-run trace file** (one per task packet, written by the
  builder) and **(b) the ACI shape** as a catalog concern: the
  builder doesn't `cat` a 5,000-line file, it uses the brain's file
  viewer that returns 100 lines per turn with a scroll command. This
  is also the "evidence is the currency" principle from ARCHITECTURE
  §3 — the run artifact is consumed by the next actor.

---

## 2. Source landscape — who does what

A short scan of the systems the brief names, plus the two essential
extras (Anthropic's *Building Effective Agents* and SWE-agent's ACI).
Stars and last-release dates are at the time of writing (2026-06-25).

| System | Status (Jun 2026) | What it is | Why it matters here |
|---|---|---|---|
| **OpenAI Swarm** | Superseded by [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) | Educational, lightweight handoffs | The handoff primitive — *function returns an Agent, context transfers* — is the cleanest statement of "lead routes, subagent executes" in the field. |
| **Microsoft AutoGen** | In maintenance mode; succeeded by **Microsoft Agent Framework 1.0** | Multi-agent framework, Core/AgentChat/Extensions layers; Magentic-One built on top | Three-layer separation (message-passing core → opinionated chat API → extension packages) and the explicit warning that AutoGen Studio is *not* production-grade. |
| **CrewAI** | Active (54.3k stars); dual-track **Crews + Flows** | Role-based crews (autonomy) and event-driven flows (control); Pydantic state; hierarchical process; "AMP" enterprise tier with tracing | The most explicit "autonomy *or* control, choose your dial" model in the field; Pydantic-typed state is the cleanest way to keep flows safe. |
| **LangGraph** | Active (35.7k stars), v1.2.6 (2026-06-18) | Low-level orchestration for stateful, long-running agents; durable execution; checkpointers; "Deep Agents" higher-level package | The clearest source of durable execution / checkpointing / time-travel patterns, and the proof that *low-level with good docs* is a viable position. |
| **SWE-agent** | Superseded by [mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent) (~100 lines, 65% SWE-bench) | NeurIPS 2024; coined "Agent-Computer Interface" (ACI) | The ACI framing is the single most useful pattern in the survey; mini's lesson is *simplicity beats cleverness* — a single thin loop with a good ACI is enough. |
| **Cursor** | Active; SOC 2 Type II | AI IDE with Agents, Cloud Agents, BugBot, Marketplace, Hooks | Production-grade agent security story: principle of least privilege, hooks, MCP-security guidance, audit logs, privacy mode. The reference for "ship an agent product to enterprises". |
| **Anthropic Claude Code** | Active; v2.1.x; ships across CLI/IDE/Desktop/Web | Agentic coding tool with the most detailed permission/hook system in the field | The single best-documented permission and hook model — denylist precedence, process-wrapper stripping, subagent allowlists, lifecycle hooks, worktree isolation. Used as the reference implementation in §3. |
| **Anthropic *Building Effective Agents*** | Published Dec 2024; the cookbook ships reference notebooks for all five patterns | The field's most-cited taxonomy: workflows (chain/route/parallel/orchestrator-workers/evaluator-optimizer) vs agents | The five-pattern taxonomy is the vocabulary F-016 should adopt. |

A note on the **Microsoft Agent Framework** (the AutoGen successor): it
positions itself as "enterprise-ready" with stable APIs, multi-provider
model support, and A2A/MCP cross-runtime. We did not fetch its docs in
detail for this brief because the architectural lessons are already
covered by AutoGen + Claude Code; flag it as a follow-up if F-016
needs to compare against Microsoft's current reference implementation.

---

## 3. By topic — what the sources actually say

The eight topics the brief asks about, in order. Each topic names the
patterns, cites a primary source, and notes the consensus.

### 3.1 Permission models — principle of least privilege, sandboxing, tool access

**The consensus shape.** Every production system combines three layers:
**(1) a static, rule-based permission model** that decides whether a
specific tool call is allowed (read-only never prompts; mutating
prompts; dangerous never allowed), **(2) hooks that can override** the
permission model with custom logic (deny, ask, allow, defer), and **(3)
an OS-level sandbox** that enforces the boundary even if (1) and (2)
are bypassed. Cursor's security page states the principle of least
privilege explicitly; Claude Code's permission model is the most
detailed in the field.

**The detailed rule shape (Claude Code).** Rules are
`Tool(specifier)`, evaluated `deny → ask → allow`, with glob
patterns for `Bash` and `WebFetch` and gitignore-style patterns for
`Read` / `Edit` / `Write`. A bare-name deny rule (`Bash`, `WebFetch`,
`mcp__*`) removes the tool from the agent's context entirely — the
model never knows it exists. A scoped deny rule (`Bash(rm *)`) leaves
the tool in context but blocks matching calls. Settings precedence
is fixed (managed > CLI > local > shared > user) and a deny from any
scope blocks an allow from any other — "deny cannot be overridden,
even by an allow at a higher-priority level when both apply".
Compound commands (`&&`, `||`, `;`, `|`, `|&`, `&`, newline) are
parsed; each subcommand must match an allow rule independently.
Process wrappers (`timeout`, `time`, `nice`, `nohup`, `stdbuf`, bare
`xargs`) are stripped before matching, so `Bash(npm test *)` covers
`timeout 30 npm test`. A built-in set of read-only commands
(`ls`, `cat`, `echo`, `pwd`, `head`, `tail`, `grep`, `find`, `wc`,
`which`, `diff`, `stat`, `du`, `cd`, read-only `git`) runs without
a prompt in every mode.

**Sandboxing.** Cursor's security page points to its
[Cloud Agent network security](https://docs.cursor.com/docs/cloud-agent/security-network)
and [Sandboxing](https://docs.cursor.com/en/sandboxing) docs; Claude
Code's permission doc says permissions and sandboxing are
*complementary* — permissions decide whether Claude *attempts* a
call; the sandbox prevents the call from *reaching* a resource
outside the boundary even if a prompt injection bypasses the model.
When sandboxing is on, sandboxed `Bash` runs without prompting even
when a `Bash` ask rule exists — the sandbox boundary substitutes for
the whole-tool prompt.

**What this means for permission model design.** Build (1), (2), (3)
in that order: static rules, hooks, OS sandbox. The static rules go
in a data file the catalog owns; the evaluator is a single
deterministic module; the hooks reuse it. This is the F-006 pattern
(D-010) applied to the tool boundary.

### 3.2 Scope control — file access limits, command restrictions, role enforcement

**The mechanism stack.** Scope control is enforced by:
**(a) tool allowlists / denylists** at the agent definition
(Claude Code subagents' `tools` and `disallowedTools` frontmatter);
**(b) path patterns** for file tools (`//path` absolute, `~/path`
home, `/path` project-relative, `path` cwd-relative; `*` within a
segment, `**` across segments); **(c) symlink awareness** (Claude
Code checks both the symlink and the resolved target — allow rules
require both, deny rules require either); **(d) command-prefix
matching** for shell, with the process-wrapper stripping noted above;
and **(e) symlink scope**, so `Read(~/.ssh/**)` denied blocks a
symlink that points there even if the symlink itself is in an
allowed directory.

**Operating-directory isolation.** Claude Code subagents start in
the parent's `cwd` and `cd` does not persist back. To give a
subagent a fully isolated repo, set `isolation: worktree` (v2.1.178+)
and the subagent runs in a temporary git worktree branched from
default, cleaned up automatically if no changes are made. The
isolation is the kernel of the **context isolation** story: a
subagent can `cd`, make changes, run tests, all without disturbing
the parent.

**Resource limits.** Claude Code subagents have `maxTurns` (the
maximum number of agentic turns before the subagent stops) and the
parent's `max_turns` (in Swarm, `float("inf")` by default).
Together with `permissionMode` (default, acceptEdits, auto, dontAsk,
bypassPermissions, plan) these are the levers a lead uses to size a
subagent's authority.

**For ASPIS.** The F-016 scope-control story is *task-packet scope*
(the allowed/forbidden files in CORE_LOOP §5) + *subagent tool
allowlist* (the new frontmatter) + *a Claude-Code-style path-rule
evaluator* that the F-006 hooks core can re-use. The three layers
are not redundant — they defend different boundaries (intent,
authority, filesystem).

### 3.3 Delegation patterns — lead → subagent, multi-level, handoff

**Five recurring patterns.**

1. **Handoff (OpenAI Swarm / Agents SDK).** A function returns an
   Agent; control transfers; the chat history is preserved but the
   *system prompt* changes. The cleanest statement of "lead routes,
   subagent executes". A function can return a `Result(value=...,
   agent=..., context_variables={...})` to combine handoff with
   context mutation. Swarm itself is "now replaced by the OpenAI
   Agents SDK" — the SDK adds tracing, guardrails, and session
   state. The handoff primitive is identical.
2. **Subagent tool (Claude Code, AutoGen).** A subagent is a
   tool the lead calls. The lead's `description` says when; the
   subagent's `description` says what it does. Spawning is
   controlled by an `Agent(agent_type)` allowlist at the lead's
   `tools` frontmatter — a worker subagent cannot spawn a
   researcher subagent unless the worker's tools list names it.
   Built-in subagents (Explore/Plan/general-purpose) are always
   available in interactive sessions; custom subagents are
   markdown with YAML frontmatter, scoped managed > CLI > project
   (`/.claude/agents/`) > user (`~/.claude/agents/`) > plugin.
   Subagents receive only their own system prompt (plus basic
   environment details), not the full Claude Code system prompt —
   the explicit context-isolation design.
3. **Manager / hierarchical (CrewAI).** A Crew with
   `Process.hierarchical` "automatically assigns a manager to the
   defined crew to properly coordinate the planning and execution
   of tasks through delegation and validation of results". The
   manager agent decides what to delegate and to whom. This is
   the same role as the lead in subagent-tool, expressed in
   role-playing vocabulary.
4. **Tool-wrapping (AutoGen AgentTool).** `AgentTool(agent,
   return_value_as_last_message=True)` wraps an agent as a
   function the parent can call. The basic multi-agent pattern in
   the AutoGen README. Like Claude Code's subagent tool, but
   more explicit about the "this is a tool" framing.
5. **Orchestrator-workers (Anthropic).** "A central LLM
   dynamically breaks down tasks, delegates them to worker LLMs,
   and synthesizes their results." The key difference from
   parallelization is *flexibility* — subtasks aren't pre-defined
   but determined by the orchestrator. Recommended for "coding
   products that make complex changes to multiple files each
   time" and "search tasks that involve gathering and analyzing
   information from multiple sources".

**Multi-level.** Claude Code allows subagents to spawn their own
subagents since v2.1.172; the *outer* subagent's summary is what
returns to the parent, intermediate output is absorbed. AutoGen's
nested groups and CrewAI's hierarchical manager both support depth
but the depth is typically two — a lead, workers. ASPIS already
plans for *one* level of worker (the Build Lead's general-builder,
CORE_LOOP §5); a second level (a builder spawning a verifier per
finding) is a future-proofing note.

**For ASPIS.** The five patterns map onto the catalog as: handoff
→ routing workflow template; subagent-tool → the new subagent
asset kind; manager → the Project/Planning/Build/Reviewer leads;
orchestrator-workers → the Build Lead's main pattern. The
"subagent definition surface" (frontmatter fields, scopes,
allowlist spawning) is the F-016 deliverable.

### 3.4 Reliability patterns — deterministic behavior from non-deterministic LLMs

**The five tools the sources use, in order of impact:**

1. **Diverse-paths-then-vote (parallelization, voting).** Run the
   same task N times with different prompts / temperatures; keep
   the majority. Used in code review ("review for vulnerabilities,
   vote on whether to flag") and content safety. Cost is N× but
   reliability rises sharply for short, well-scoped tasks.
2. **Evaluator-optimizer loop.** One model generates, another
   evaluates against criteria, the generator iterates. Effective
   when "LLM responses can be demonstrably improved when a human
   articulates their feedback" and "the LLM can provide such
   feedback". Anthropic's example: literary translation.
3. **Gate-after-each-step (prompt chaining with gates).** A
   programmatic check between steps — "is the outline valid? if
   not, fail now." Trades latency for accuracy; eliminates a
   class of cascading errors.
4. **Durable execution + checkpointers (LangGraph).** Persist
   thread state as checkpoints; resume from the last known good
   state on failure; allow time travel for inspection. Two
   complementary stores: **checkpointers** (thread-scoped, short-
   term, conversation continuity / human-in-the-loop / fault
   tolerance) and **stores** (cross-thread, long-term, user
   preferences and shared knowledge). Most apps use both. The
   checkpointer pattern is the implementation of "evidence is
   the currency" — every phase emits a state the next phase
   consumes.
5. **The ACI itself (SWE-agent).** Poka-yoke the tools so the
   model *can't* make certain mistakes. Examples from the SWE-
   agent background doc:
   - a **linter** that runs on edit and blocks unsyntactic
     changes,
   - a **custom file viewer** that shows 100 lines per turn with
     scroll commands (not `cat` of a 5,000-line file),
   - a **succinct search** that lists files-with-matches rather
     than every match line,
   - an **empty-output handler** that returns "Your command ran
     successfully and did not produce any output."

**The cost-lever framing.** ASPIS's own ARCHITECTURE §4: "Deter-
minism is the cost lever. Shrink what the model must figure out —
tight task, rich context, conformant template — and the cheapest
model is correct." This is the same point SWE-agent makes with
ACI: the more *deterministic* the surface the model touches, the
less *non-deterministic* the model has to be. The packet, the
template, the deterministic scripts, and the gate are the four
deterministic surfaces an ASPIS builder touches.

**For ASPIS.** F-016 should formalise **(a) the trace file** (one
per task packet, written by the builder, read by the next actor)
and **(b) the ACI surface** (the catalog's file viewer, search,
linter, and command-output handlers). The post-commit brain
refresh is already a kind of checkpoint; F-016 makes the pattern
explicit and reusable.

### 3.5 Deterministic-first — scripts, tools, workflows before agents

**The unanimous advice.** Anthropic, OpenAI, the AutoGen-to-MAF
migration guide, and CrewAI all say the same thing in different
words: start simple, add complexity only when measurements justify
it. Anthropic: "for many applications, however, optimizing single
LLM calls with retrieval and in-context examples is usually
enough." OpenAI Swarm exists *because* Assistants was heavy; the
Agents SDK is "production-ready evolution". CrewAI: "Crews for
autonomy, Flows for control — use the dial that fits". AutoGen
Studio's own docs warn: "AutoGen Studio is meant to help you
rapidly prototype … **not meant to be a production-ready app**.
Developers are encouraged to use the AutoGen framework to build
their own applications, implementing authentication, security and
other features required for deployed applications."

**The workflow patterns that beat agents for well-defined tasks.**

- **Prompt chaining** — for tasks decomposable into fixed steps
  (generate copy → translate). Add programmatic gates to fail
  fast.
- **Routing** — for inputs that need different handling (customer
  service triage; easy → Haiku, hard → Sonnet).
- **Parallelization (sectioning)** — when subtasks are independent
  (guardrails: one model processes the query, another screens it).
- **Parallelization (voting)** — when diverse opinions improve
  confidence (code review for vulnerabilities).
- **Orchestrator-workers** — for dynamic decomposition (coding
  products that change N files in unknown ways).
- **Evaluator-optimizer** — when iteration adds value (literary
  translation; multi-round search).

**When to use a full agent.** Open-ended problems where the number
of steps is unpredictable, the path can't be hardcoded, and you
have some level of trust in the model's decision-making. "Higher
costs, and the potential for compounding errors. We recommend
extensive testing in sandboxed environments, along with the
appropriate guardrails."

**For ASPIS.** CORE_LOOP §1 already names this: "scale the
process to the work" and "delegate only when delegation adds
value". F-016 should make the *workflow doc* (CORE_LOOP §9) a
first-class asset kind with mode overlays, and the catalog should
ship the five workflow patterns as named templates a feature can
declare ("I am a prompt-chain" / "I am an orchestrator-workers")
that the lead reads.

### 3.6 Orchestration patterns — fan-out/fan-in, sequential, dynamic, consensus

**The taxonomy, from the sources:**

- **Sequential / prompt chain** — single LLM call per step;
  programmatic gates between steps. Latency-trades-accuracy.
- **Routing** — classify, then dispatch. Static or dynamic
  (LLM-routed).
- **Parallel (sectioning)** — N independent subtasks, aggregate.
  Map-reduce over LLM calls.
- **Parallel (voting / consensus)** — N runs of the same task,
  keep the majority. Used for safety and code review.
- **Orchestrator-workers** — a central LLM dynamically decomposes
  and synthesises. The orchestrator's tool is *another agent*.
- **Evaluator-optimizer** — a generate/evaluate loop. Often runs
  inside an orchestrator-worker.
- **Handoff (Swarm)** — the conversation control transfers; the
  history is preserved.
- **Event-driven (CrewAI Flows)** — `@start`, `@listen`,
  `@router` decorators; conditional branching; Pydantic-typed
  state that flows between steps.
- **Stateful graph (LangGraph)** — nodes + edges; checkpointer per
  thread; supports cycles, branches, sub-graphs, interrupts, time
  travel.
- **Message-passing core (AutoGen Core)** — agents publish and
  subscribe to typed messages on a runtime; local or distributed
  (gRPC). Lower-level than AgentChat; closer to LangGraph in
  spirit.

**The dimension that decides the pattern.** "How predictable is
the decomposition?" Static → chain / route / parallel sectioning.
Dynamic → orchestrator-workers / evaluator-optimizer / handoff.
Long-running + resumable → stateful graph with checkpointer.
Production with audit needs → event-driven flow with typed state.

**For ASPIS.** The current loop is sequential by design
(plan → build → review). F-016 doesn't need to add graph
orchestration to the core loop; it needs to **let a lead declare
which orchestration pattern a feature uses** (a data field in
PLAN.md or a separate `orchestration.yaml`) so the workflow
doc, the hooks, and the reviewers can adapt.

### 3.7 Error handling — when an agent fails, who recovers

**The patterns, by source:**

- **Append-error-to-chat (OpenAI Swarm).** "If an `Agent`
  function call has an error (missing function, wrong argument,
  error) an error response will be appended to the chat so the
  `Agent` can recover gracefully." Errors are data, fed back to
  the model.
- **`max_turns` + `execute_tools=False` (Swarm).** Two safety
  valves: a hard turn limit prevents infinite loops;
  `execute_tools=False` returns tool calls to the caller for
  inspection before running them.
- **Built-in retries + judge-based escalation (Claude Code).** A
  `PermissionDenied` event can be returned with `{retry: true}` to
  tell the model it may retry. A `PreToolUse` hook can `deny` and
  the model receives the reason as feedback. Background subagent
  permission prompts surface in the main session and name the
  asking subagent.
- **Permission modes as failure policy (Claude Code).** `auto`
  uses a background classifier that re-checks model decisions;
  `dontAsk` auto-denies unless pre-approved; `bypassPermissions`
  is opt-out via `permissions.disableBypassPermissionsMode` in
  managed settings. The mode *is* the failure policy.
- **Stops and stopping conditions (Anthropic agents).** "The task
  often terminates upon completion, but it's also common to
  include stopping conditions (such as a maximum number of
  iterations) to maintain control."
- **Durable execution / checkpointers (LangGraph).** A failure
  mid-run resumes from the last known good state. The checkpointer
  is the recovery record.
- **Stop hook + agent judge (Claude Code).** A `type: agent` hook
  on `Stop` runs a multi-turn verifier before allowing the agent
  to finish. Used to verify "all tests pass" before the agent
  claims done.

**Who recovers?** The default answer in all sources: the agent
itself, with the error fed back as a tool result. The lead recovers
when the agent exceeds `max_turns` or the task is misrouted. The
human recovers when the system exceeds its bounded authority (a
prompt, a circuit breaker). ASPIS adds one more ring: the **committer
recovers** when a hook fails (the build loop rejects the change;
the committer routes back to a builder or the Fix Lead).

**For ASPIS.** The error path is already in CORE_LOOP §6
("rejections route back to a builder or the Fix Lead") and
D-011 (committer is the single commit authority; hooks enforce).
F-016 should add: **(a) `max_turns`-equivalent** on the
subagent frontmatter (Claude Code has it; named there `maxTurns`);
**(b) error-as-data in the trace** (every tool failure written
to the trace file with the model's recovery action); **(c) the
Stop hook as the "did the agent claim done honestly" check**.

### 3.8 Traceability — who did what, when

**The four sources of truth, layered:**

1. **Transcript / conversation log.** Every Swarm `Response`
   carries `messages` (with a `sender` field showing which Agent
   produced each message), the last `Agent` that handled a turn,
   and the most up-to-date `context_variables`. The OpenAI Agents
   SDK formalises this as a session.
2. **Trace + observability (LangGraph → LangSmith; CrewAI AMP;
   Cursor audit logs).** LangGraph's value prop includes
   "debugging with LangSmith — gain deep visibility into complex
   agent behavior with visualization tools that trace execution
   paths, capture state transitions, and provide detailed runtime
   metrics". CrewAI AMP's first key feature is "Tracing &
   Observability: monitor and track your AI agents and workflows
   in real-time, including metrics, logs, and traces". Cursor's
   security page lists "Compliance logging" / "Audit logs" as
   first-class enterprise features.
3. **Subagent lifecycle events (Claude Code hooks).**
   `SubagentStart` and `SubagentStop` events include a `matcher`
   that filters by agent type. The hooks are the trace — log
   every tool use, every permission decision, every state change.
4. **ConfigChange event (Claude Code).** Fires when a settings
   file or skill file is modified *during* a session — closes the
   "who changed the rule" gap. Pair with `audit` hooks for
   compliance.

**Per-action attribution.** Claude Code's `PreToolUse` /
`PostToolUse` hooks receive the full tool input on stdin (JSON:
`session_id`, `cwd`, `hook_event_name`, `tool_name`,
`tool_input`). That JSON is the per-action record. A `PreCompact`
/ `PostCompact` pair gives the "what was lost when context
compacted" record. Together: every action is attributable to a
session, an agent, a tool, a turn, and (via the input) the
exact input/output.

**For ASPIS.** The **trace file** is the missing piece. CORE_LOOP
§6 names "build report / review report / test report" as the
artifacts, but the *per-turn* trace isn't. F-016 should define
the **trace schema** (per-task packet: feature id, task id,
session id, agent name, model, tool calls with inputs/outputs,
compaction events, errors) and emit it as a sibling of the build
report. The schema is small, the value is large — it makes the
reviewer's life tractable and is the seed of the Phase-4 tracing
spine flagged in D-016.

---

## 4. Implications for ASPIS

Tied back to the existing decisions (D-001 through D-018) and the
core loop (CORE_LOOP.md). The point is to name what the catalog
*already* has, what F-016 *should* add, and what F-016 *should
not* do.

### What ASPIS already has (don't re-invent)

- **The hooks shared core (D-010, F-006).** The
  scope/secret/junk/gitignore logic lives once under
  `.aspis/scripts/hooks/`; the commit boundary uses it today. The
  tool-use boundary should reuse the same code.
- **The brain/runtime split (D-003).** The System Lead owns the
  runtime; the other leads own the shared brain. The tool-use
  hooks live in the runtime half; the rule data (`permission.yaml`)
  lives in the brain half.
- **The committer as single commit authority (D-011).** The
  committer recovers when hooks fail; the Fix Lead handles
  cross-task fixes. This is the "who recovers" answer.
- **Subagent-by-default + promotion (D-004).** Every agent ships
  `mode: subagent`; only the Project Lead is primary. F-016
  formalises the surface.
- **Deterministic-first (D-005).** The same idea as the surveyed
  systems; F-016 makes the workflow patterns first-class.
- **Capture-now, derive-later (ARCHITECTURE §4).** The trace file
  is the "capture now" of agent runs; the "derive later" is the
  Phase-4 tracing spine. F-016 ships the capture, reserves the
  seam.
- **The task packet (CORE_LOOP §5).** Context-isolated builder
  with declared scope, declared tools, declared gates. Already
  exactly the "subagent tool" pattern.

### What F-016 should add

1. **A subagent definition surface** (catalog asset kind):
   markdown + YAML frontmatter with the Claude Code fields
   (`name`, `description`, `tools`, `disallowedTools`, `model`,
   `permissionMode`, `maxTurns`, `memory`, `isolation`, `hooks`,
   `skills`, `background`, `color`). The runtime adapter renders
   the format the target runtime accepts.
2. **A `permission.yaml` schema** for the tool boundary (the
   `allow / ask / deny` lists, glob/path syntax, precedence). One
   evaluator in `.aspis/scripts/hooks/permission.py`, used by
   both runtime boundaries via the adapter.
3. **A hooks config** for the tool boundary: which events the
   catalog subscribes to by default (`PreToolUse`, `PostToolUse`,
   `SubagentStart`, `SubagentStop`, `Stop`, `PreCompact`), and
   which are opt-in (`PermissionRequest`, `ConfigChange`,
   `Notification`).
4. **A workflow-pattern template per pattern**: prompt-chain,
   routing, parallel-sectioning, parallel-voting, orchestrator-
   workers, evaluator-optimizer. Each template is a markdown doc
   the lead reads, with mode overlays (CORE_LOOP §9) that say
   which steps to compress in vibe/MVP.
5. **A trace schema** for per-run attribution: feature id, task
   id, session id, agent name, model, tool calls with
   inputs/outputs, compaction events, errors. Emitted as a
   sibling of the build report; consumed by reviewers and (later)
   the Phase-4 tracing spine.
6. **An ACI library** under `.aspis/scripts/aci/`: file viewer
   (100 lines per turn + scroll), succinct search (files-with-
   matches), linter-on-edit, empty-output handler. Re-used by
   every builder. Implemented as plain Python — no LLM in the
   path.
7. **A `modes.yaml` extension** (already exists per D-013) that
   names the orchestration pattern a feature uses, so the hooks
   and the workflow doc can adapt.

### What F-016 should *not* do

- **Don't introduce a new orchestration engine.** LangGraph,
  CrewAI, AutoGen's Core, and the Microsoft Agent Framework
  already exist; ASPIS's value is the brain and the catalog, not
  a graph runtime. The catalog *names* the patterns; the
  runtimes *run* them.
- **Don't replace the F-006 hooks.** Reuse the shared core
  (D-010). The "deny-wins, one evaluator" pattern is the same on
  the commit boundary and the tool boundary.
- **Don't put the committer in the LLM loop.** The committer is
  a deterministic script (`aspis commit`, D-011) called by the
  Build Lead. F-016 doesn't change this.
- **Don't add a graph/checkpointer runtime of its own.** Capture
  the trace, persist the brain, defer the run-time to the
  adapter-emitted runtime. "Hard-`limits` enforcement … and
  `task_size` shaping are a run-time/dispatch concern" (D-017) —
  the same applies to checkpointers.
- **Don't tie the new surface to one runtime.** The catalog is
  the superset; the adapter renders. An OpenCode agent with
  `tools: [Bash, Edit]` and a Claude Code subagent with
  `tools: [Read, Grep, Glob, Bash]` should be expressible in the
  same source.

### A note on the open questions for the lead

- **Should ASPIS own the LLM judge for evaluator-optimizer, or
  delegate to the lead agent?** The survey suggests delegate —
  the judge is itself an agent, configured per workflow pattern.
  The lead picks the judge; the catalog ships the *pattern
  template* that names what the judge should check.
- **Should the trace schema be JSON Lines, JSON, or something
  else?** JSON Lines is the dominant shape (LangSmith, OpenLLMetry,
  OpenTelemetry); recommended unless there's a reason to diverge.
  The OpenTelemetry GenAI semantic conventions are the obvious
  reference; flag as a follow-up.
- **Do we want a single lead-promoted subagent pool (D-004's
  "five primaries") or a self-describing registry?** The
  current model is the right shape (primaries are promoted; the
  rest are subagents). F-016 adds the *definition* surface and
  the *allowlist* spawning; promotion stays in bootstrap.

---

## 5. Source ledger

Every URL, with the version stamp we verified. The "as of" date is
**2026-06-25** unless noted.

### Primary — patterns and case studies

| Source | URL | What we used | Version / as of |
|---|---|---|---|
| Anthropic, *Building effective agents* | https://www.anthropic.com/research/building-effective-agents | Five-pattern taxonomy, the workflows-vs-agents distinction, three core principles (simplicity, transparency, ACI) | Published 2024-12-19; current at read time |
| Anthropic, *Building Effective Agents* cookbook | https://github.com/anthropics/claude-cookbooks/tree/main/patterns/agents | Reference notebooks: `basic_workflows`, `orchestrator_workers`, `evaluator_optimizer`, `async_multi_agent_orchestration` | Current on `main`, retrieved 2026-06-25 |
| SWE-agent, *Agent Computer Interface (ACI)* | https://swe-agent.com/latest/background/aci/ | The four ACI pillars (linter, file viewer, succinct search, empty-output handler) | Last updated 2025; SWE-agent in maintenance, succeeded by mini-SWE-agent |
| SWE-agent paper | https://arxiv.org/abs/2405.15793 | The "ACI design leads to much better results" claim; NeurIPS 2024 | Published 2024 |

### Primary — production systems

| Source | URL | What we used | Version / as of |
|---|---|---|---|
| Claude Code, Permissions | https://code.claude.com/docs/en/permissions | The most detailed permission model in the field; denylist precedence, glob/path syntax, settings precedence, process-wrapper stripping, read-only commands | Current docs (Claude Code 2.1.x line, mid-2026) |
| Claude Code, Sub-agents | https://code.claude.com/docs/en/sub-agents | Built-in subagent types (Explore/Plan/general-purpose), frontmatter fields, scoping, `Agent(agent_type)` allowlist, worktree isolation, persistent memory | Current docs (Claude Code 2.1.x line, mid-2026) |
| Claude Code, Hooks | https://code.claude.com/docs/en/hooks-guide | 25+ lifecycle events, 5 hook types (command, http, mcp_tool, prompt, agent), exit-code semantics, matcher/if syntax | Current docs (Claude Code 2.1.x line, mid-2026) |
| Claude Code overview | https://code.claude.com/docs/en/overview | Skills, sub-agents, hooks, MCP, Agent SDK, auto memory, routines, agent teams | Current docs (Claude Code 2.1.x line, mid-2026) |
| OpenAI Swarm (readme) | https://github.com/openai/swarm | Handoff primitive; superseded by OpenAI Agents SDK; `Response` schema, function-as-handoff, error-as-data | Last commit 2024; replaced by https://github.com/openai/openai-agents-python |
| Microsoft AutoGen (readme) | https://github.com/microsoft/autogen | Three-layer architecture (Core/AgentChat/Extensions), MCP integration, Magentic-One, "AutoGen Studio is not production-ready" warning; in maintenance mode | v0.7.5 (2025-09-30), current; AutoGen in maintenance, succeeded by Microsoft Agent Framework |
| CrewAI (readme) | https://github.com/crewAIInc/crewAI | Crews (autonomy) + Flows (control) dual-track, `@start`/`@listen`/`@router`/`or_`/`and_` decorators, Pydantic state, hierarchical process, AMP enterprise tier with tracing | Current on `main`, retrieved 2026-06-25 (54.3k stars) |
| LangGraph (readme) | https://github.com/langchain-ai/langgraph | Low-level orchestration; durable execution; checkpointers; memory stores; inspired by Pregel/Apache Beam; "Deep Agents" higher-level package | v1.2.6 (2026-06-18), current |
| LangGraph Persistence | https://docs.langchain.com/oss/python/langgraph/durable-execution | Checkpointers vs stores; thread-scoped vs cross-thread memory; time travel, human-in-the-loop, fault tolerance | Current docs, retrieved 2026-06-25 |
| SWE-agent (readme) | https://github.com/SWE-agent/SWE-agent | "Free-flowing & generalizable", single yaml file governance, ACI framing, "configurable & fully documented"; superseded by mini-SWE-agent | v1.1.0 (2025-05-22), current; in maintenance |
| Cursor Security | https://cursor.com/security | Principle of least privilege; agent security; hooks; MCP security considerations; compliance / audit logs; privacy mode; SOC 2 Type II | Last updated 2026-04-24 |

### Secondary — context for ASPIS

| Source | URL | What we used |
|---|---|---|
| ASPIS ARCHITECTURE | `.aspis/context/ARCHITECTURE.md` | Constitution §4 (determinism is the cost lever), §4 (evidence is the currency) |
| ASPIS CORE_LOOP | `.aspis/context/CORE_LOOP.md` | §1 (scale the process), §5 (task packet = subagent), §6 (rejections route back), §9 (workflow docs as data) |
| ASPIS DECISIONS | `.aspis/context/DECISIONS.md` | D-004 (subagent-by-default + promotion), D-005 (deterministic-first), D-010 (hooks shared core, warn/block), D-011 (committer authority), D-016 (model catalog), D-017 (limits deferred to dispatch) |

### Follow-ups not in scope of this brief

- **Microsoft Agent Framework** (the AutoGen successor, v1.0). Not
  fetched in detail because the architectural lessons are already
  covered; flag if F-016 needs a direct comparison.
- **OpenAI Agents SDK** in detail. Swarm's handoff primitive is
  the one we needed; the SDK adds tracing, guardrails, sessions.
  Fetch https://github.com/openai/openai-agents-python before
  finalising the subagent frontmatter schema.
- **Anthropic *Building Effective Agents* — Appendix 2 ("Prompt
  engineering your tools")** in full. We quoted the ACI list; the
  full text is worth a dedicated read.
- **OpenTelemetry GenAI semantic conventions.** The trace schema
  in §4 should align with the emerging standard; pull
  https://opentelemetry.io/docs/specs/semconv/gen-ai/ before the
  schema is finalised.
- **LangGraph interrupts** (https://docs.langchain.com/oss/python/langgraph/interrupts).
  Human-in-the-loop as a first-class pattern; the brain's
  plan-critic could be expressed as an interrupt.
- **CrewAI Flows docs** (https://docs.crewai.com/concepts/flows).
  Pydantic-typed state with event-driven transitions is the
  cleanest "production workflow" model; worth a closer read.
- **mini-SWE-agent** (https://github.com/SWE-agent/mini-swe-agent).
  100 lines, 65% SWE-bench. The proof that the ACI matters more
  than the framework.
