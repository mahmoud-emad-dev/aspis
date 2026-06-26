<!-- ASPIS:REFERENCE START -->
# Build Execution — Industry Analysis for ASPIS build-lead Design

> **Author:** Research Lead
> **Date:** 2026-06-26
> **Status:** Primary-source synthesis. Built for the ASPIS build-lead
> agent. One question: what does industry prove about how to execute a
> build well, and what should ASPIS do about it?
>
> **Sources read (current as of 2026-06-25 / 26):**
> 1. `production-loops-companies.md` — Cursor, OpenAI Codex, Claude Code,
>    Devin, Copilot, Q Developer, Vercel v0, Replit Agent 4, AlphaEvolve.
> 2. `core-loops-2026.md` — five proven core-loop patterns (the spine).
> 3. `old-asps-deep-analysis-1.md` — the OLD ASPS build-lead failure modes
>    (F-026 reachability, 13 zero-byte junk files, no-stray-file gap).
> 4. `cheap-models-quality.md` — cost control + cheap-model patterns
>    (Bugbot 22% cheaper / +10% bugs, Wayfair 90%+, Sonnet 4.5 77.2%).
> 5. `local/AGENT-SYSTEM-ARCHITECTURE.md` — current ASPIS architecture
>    the build-lead lives in.
>
> **Audience:** Build Lead, Project Lead, Reviewer, anyone extending the
> build half of the core loop. Read as input to a SPEC/PLAN revision.
>
> **Provenance tags.** **[VERIFIED]** = multi-source primary. **[EMERGING]**
> = one team's internal post, not yet broadly replicated. **[VENDOR]**
> = vendor self-report, treat as opinion. **[ASPIS]** = current ASPIS
> design state.

---

## 0. Bottom line up front

The five build-execution patterns that survive 2024 → mid-2026 industry
churn — and that ASPIS's build-lead should treat as the contract — are:

1. **One packet per worker, context-isolated.** The planner holds whole-
   feature context; the worker sees only its packet. The handoff carries
   *concerns*, not just results. *(Cursor self-driving, Anthropic subagents,
   Devin, all converge.)*
2. **The product gate is the loop closer, and it runs after every worker
   handoff — not per-commit.** Per-commit 100% correctness serializes the
   system; per-task gate + final green pass is the proven cadence. *(Cursor
   explicitly documents this; OpenAI Codex does the same.)*
3. **The reviewer is a different agent with a different context.** The
   builder never grades its own work. Adversarial review is a subagent
   (or specialised lead), not a re-prompt of the same agent. *(Cursor
   Bugbot, Claude Code `/code-review`, METR, Cognition evaluator-agent
   all converge.)*
4. **A small, fast classifier sits in the agent loop and decides
   "is this risky?" — not a global permission switch.** ~4% of tool calls
   actually need a prompt; the other 96% should be invisible. *(Cursor
   Auto-review: 4% block / 7% interrupt / 0% approval fatigue.)*
5. **Cheap models do the work, frontier models judge the work.** Review
   and classify on a *different, often cheaper, often specialised* model
   than the one that built. *(Cursor Bugbot on Composer 2.5: 22% cheaper,
   +10% bugs found. Wayfair: 90%+ cost cut.)*

The five anti-patterns ASPIS must NOT replicate — all from real production
post-mortems — are:

1. **Builder cannot reach reviewer.** Permission block stops the handoff.
   *(OLD ASPS F-026, the most expensive single bug in the system.)*
2. **Self-coordinating agents via shared state file.** Lock contention
   collapses throughput. *(Cursor: 20 agents → 1-3 effective.)*
3. **One agent with too many roles** (plans + spawns + reviews + commits).
   *Pathological behaviours: sleep, refusal, premature completion.*
   *(Cursor's "continuous executor" attempt.)*
4. **Central integrator that gates all work.** A bottleneck. Quality must
   be distributed. *(Cursor removed the integrator.)*
5. **100% correctness at every commit.** Causes serialization; workers
   pile on the same issue. *(Cursor explicitly accepts a "small but
   constant" error rate, reconciles in a final pass.)*

The OLD ASPS F-026 build-lead failure was the union of (1) + (3) — the
build-lead *claimed* in prose to hand off to tester/reviewer, but its
`task:` permission only allowed builders, AND the same context kept
doing plan + spawn + delegate + review-ish work. The lesson for ASPIS:
**make the handoff reachable (allowlist) AND make the role narrow
(no review) AND make the loop deterministic (gate, then route, then
hand).**

---

## 1. Cursor — root planner → subplanners → workers (the 1,000-commits/hour architecture)

### 1.1 What the loop looks like

Cursor's `Towards self-driving codebases` (Wilson Lin, 2026-02-05) is the
most detailed public account of multi-agent execution. The system they
*kept* — after killing four earlier attempts — has three roles:

| Role | Owns | Does | Does NOT |
|---|---|---|---|
| **Root planner** | Whole project scope | Decomposes into subplanners; tracks progress via handoffs | Code; spawn workers directly; integrate results |
| **Subplanner** (recursive) | A narrow slice | Decomposes further when scope is too big; spawns workers | Code; talk to other subplanners |
| **Worker** | One task packet | Implements in its own copy of repo, runs verification, writes handoff | Know about the larger system; talk to other workers; take on work outside its packet |

### 1.2 How workers are invoked

Workers are **not** invoked by a shared coordination file (tried, failed,
collapsed 20 agents to 1-3 effective on contention). Workers are invoked
**by handoff** — the planner pushes a task packet, the worker picks it up.
The packet contains scope, files, acceptance, constraints. The worker
runs on its own copy of the repo.

### 1.3 The handoff format

> *"The handoff contains not just what was done, but important notes,
> concerns, deviations, findings, thoughts, and feedback. The planner
> receives this as a follow-up message."*

Three properties:

1. **Concerns, not just results.** A worker that noticed "the test
   fixture is brittle" or "I had to bend the spec at X" escalates *up*,
   not silently. This is the propagation mechanism.
2. **No global synchronisation.** Each handoff is a message; the planner
   composes the picture from handoffs. No shared mutable state.
3. **Asymmetric ownership.** The planner owns the global view, the
   worker owns the local. Information flows up, not sideways.

### 1.4 Worker failure handling

Cursor accepts that **workers will sometimes fail** — wrong file, bad
assumption, scope creep, premature completion. The handling is *not* a
try/catch; it's a structural decision:

> *"When we required 100% correctness before every single commit, it
> caused major serialization and slowdowns of effective throughput.
> ... Workers would go outside their scope and start fixing irrelevant
> things. Many agents would pile on and trample each other trying to fix
> the same issue. ... This may indicate that the ideal efficient system
> accepts some error rate, but a final 'green' branch is needed where an
> agent regularly takes snapshots and does a quick fixup pass before
> release."*

So: workers *may* fail; **the system reconciles at the integration
pass**, not at each commit. The per-task gate is the building block; the
per-feature gate is the contract.

### 1.5 Throughput

**~1,000 commits/hour, 10M tool calls, 0 humans in the loop, for one
week** — building a web browser from scratch. Not a marketing number;
this is the measured output of a real run.

The throughput lever is **no central integrator**. With one integrator,
hundreds of workers serialise on the gate. Without it, workers run in
parallel, errors are accepted in flight, reconciliation happens at the
boundary.

### 1.6 Cloud-agent durability (companion post, 2026-06-02)

Cursor's cloud agents run on **Temporal** for durable execution:
50M Temporal actions/day, 7M unique workflows/day, 40%+ of Cursor's own
PRs come from cloud agents. The architecture:

- **Agent loop lives in Temporal** (durable, retryable, recoverable).
- **VMs are managed independently** (readonly, prewarmed, replaced as needed).
- **Conversation state is append-only** (clients can rewind a retried turn).
- **Decoupled** — agent loop, machine state, conversation state are three
  components, not one.

> *"As models got smarter, we started moving logic out of the harness
> and into tools the agent controls."*

The harness is being hollowed out. The agent gets `gh` and lint and
tests as tools; it decides what to do with them.

### 1.7 Auto-review — the risk classifier in the loop (2026-06-11)

The same Cursor team ships a small classifier model that sits in the
*same RPC stream* as the parent agent and decides whether each tool call
is low-stakes (run it) or high-stakes (interrupt the user). It is
*agentic* — it can read files, grep, glob, listdir before deciding.

Production numbers:
- **~4% of actions blocked.**
- **~7% of chats lead to at least one user interruption.**
- *Compare:* some enterprise customers previously saw **~40% of actions
  blocked** under blanket permission gating (the "approval fatigue"
  failure mode).
- Eval: 6,122 labelled rows from ~12 hours of internal sessions +
  synthetic adversarial cases. Primary signal of underspecified policy:
  *flapping* (allow-six, block-four).

### 1.8 What ASPIS should take from Cursor

| Pattern | ADOPT / ADAPT / REJECT | ASPIS mapping |
|---|---|---|
| Root planner + subplanners + workers | **ADAPT** — current ASPIS is one-level deep (build-lead → general-builder). The recursion is a Phase 3+ extension. |
| Handoff carries concerns, not just results | **ADOPT** — the ASPIS task packet should include a `## Concerns / Deviations / Findings` block; the BUILD_REPORT must capture it. |
| No shared coordination file | **REINFORCE** — ASPIS already has the brain-as-files but only humans and single agents read it. Don't extend to multi-agent coordination. |
| 100% per-commit gate is anti-pattern | **REJECT** — ASPIS's per-task gate is correct. The reconciliation pass is implicit in the per-feature `feature.yaml` accept. |
| No central integrator | **ADAPT** — ASPIS's "single committer" is *not* a central integrator (it doesn't gate all work — it commits *one* approved handoff at a time). The Reviewer-as-committer is the *quality + write* fusion, not a global gate. |
| 1,000 commits/hour scale | **DEFER** — proven at browser-from-scratch scale; not ASPIS's shape. |
| Temporal-style durable execution | **DEFER** — Phase 3+ for the runtime. ASPIS today runs short tasks. |
| Auto-review classifier (4% block) | **ADAPT** — ASPIS's deterministic allowlist handles *known* risk. A small classifier for *unknown* risk is a follow-up feature. |
| Bugbot (cheap, fast, dedicated model) | **ADOPT** — ASPIS's reviewer should be able to be the cheap model; the build is the standard model. Today, the reviewer is `standard`; should be tier-aware. |
| `gh` as a tool the agent controls | **ALREADY TRUE** — ASPIS committer uses `aspis commit`; the agent gets the CLI, not the harness's opinion. |

---

## 2. Claude Code — implement → test → review → commit (the canonical 4-phase loop)

### 2.1 The four phases

From Anthropic's *Best practices for Claude Code* (2026):

> *"The recommended workflow has four phases:*
> 1. **Explore.** Enter plan mode. Claude reads files and answers
>    questions without making changes.*
> 2. **Plan.** Ask Claude to create a detailed implementation plan.*
> 3. **Implement.** Switch out of plan mode and let Claude code,
>    verifying against its plan.*
> 4. **Commit.** Ask Claude to commit with a descriptive message and
>    create a PR."*

The phases are *separated by mode* (plan mode vs default). Plan mode
is for unclear scope; default mode is for small fixes.

> *"If you could describe the diff in one sentence, skip the plan."*

This is the **mode-dial anchor** in the industry — the explicit
"trivial → don't plan" rule that the whole field converged on.

### 2.2 The verification gradient — four strengths

> *"Each step trades setup for attention:*
> - *In one prompt: ask Claude to run the check and iterate in the same
>   message.*
> - *Across a session: set the check as a `/goal` condition. A separate
>   evaluator re-checks it after every turn and Claude keeps working
>   until it holds.*
> - *As a deterministic gate: a [Stop hook](/en/hooks#stop) runs your
>   check as a script and blocks the turn from ending until it passes.
>   Claude Code overrides the hook and ends the turn after 8 consecutive
>   blocks.*
> - *By a second opinion: a verification subagent or a dynamic workflow
>   that checks its own findings has a fresh model try to refute the
>   result, so the agent doing the work isn't the one grading it."*

Four strengths, in order of cost: in-prompt → /goal → Stop hook →
subagent review. ASPIS's gate (.asps/gates.yaml, R-002) is closest to
the **Stop hook** strength. The build-lead should know the gradient
exists so it can *escalate* verification depth by mode.

### 2.3 The /goal re-check

> *"Across a session: set the check as a `/goal` condition. A separate
> evaluator re-checks it after every turn and Claude keeps working
> until it holds."*

This is the pattern ASPIS's *Build Lead + per-task gate* approximates:
the goal is the acceptance + tests; the re-check is the gate command;
the loop continues until green or until 3 attempts (ASPIS's hard cap).

### 2.4 The fresh-context reviewer (subagent)

> *"Add an adversarial review step. Tip: Before treating a task as
> done, have a subagent review the diff in a fresh context and report
> gaps."*
>
> *"The longer Claude works unattended, the more an independent check
> matters before you count the work as done. A reviewer running in a
> fresh subagent context sees only the diff and the criteria you give
> it, not the reasoning that produced the change, so it evaluates the
> result on its own terms."*

This is **Pattern 3 in the five-pattern spine**. The motivation is
*bias-break*, not "different model is better." A fresh context doesn't
have the writer's confirmation bias.

The *Writer/Reviewer* pattern is two parallel sessions — one writes,
one reviews in fresh context. The cheapest second-opinion unit.

### 2.5 Permissions — three modes, deny-wins

> *"A classifier model reviews commands before they run, blocking scope
> escalation, unknown infrastructure, and hostile-content-driven
> actions while letting routine work proceed without prompts."*

Three modes:
1. **Auto mode** (classifier reviews, blocks the bad ~4%, lets the rest
   run).
2. **Permission allowlist** (e.g. `npm run lint`).
3. **Sandboxing** (OS-level isolation).

ASPIS has (2) + (3) today (deny-wins allowlist + scope_guard). (1) is
the follow-up feature. Auto mode *aborts a non-interactive run* if the
classifier repeatedly blocks — i.e. it doesn't loop forever.

### 2.6 Subagents — context-isolated, own tools, own model

> *"Use subagents for investigation. Delegate research with 'use
> subagents to investigate X'. They explore in a separate context,
> keeping your main conversation clean."*

Subagents run in their own context window, with their own tools, and
return summaries back. ASPIS's `general-builder` is exactly this
shape — fresh context, sees only the packet, returns a 1-2k-token
distilled summary.

### 2.7 What ASPIS should take from Claude Code

| Pattern | ADOPT / ADAPT / REJECT | ASPIS mapping |
|---|---|---|
| Four phases (explore → plan → implement → commit) | **ALREADY TRUE** — ASPIS's plan → build → review → commit maps 1:1. Build-lead owns implement + commit-handoff. |
| "Skip plan if you can describe the diff in one sentence" | **ADOPT** — the Build Lead's workflow should include this as the trivial-task fast path (no SPEC, no PLAN, no TASKS — direct implement). |
| Four-strength verification gradient | **ADAPT** — document the gradient in build.md; default to Stop-hook (R-002), escalate to subagent-review for production mode. |
| `/goal` re-check after every turn | **ADAPT** — ASPIS's per-task gate is the re-check; the acceptance is the /goal. |
| Fresh-context subagent review | **ALREADY TRUE** — `quality-review` skill, reviewer is read-only. The gap: build.md step 3d names a "sub-reviewer" agent that doesn't exist yet. **Add the agent.** |
| Writer/Reviewer parallel sessions | **ADOPT** — when the packet is high-criticality, run a fresh-context reviewer in parallel to the next task. Don't block the queue. |
| Auto mode (classifier) | **DEFER** — Phase 3+. Current ASPIS deterministic allowlist is sufficient for F-016's scope. |
| Prefilled responses | **REJECT** — deprecated in Claude 4.6; not used by industry. ASPIS should not invent it. |
| One big CLAUDE.md | **REJECT** — explicitly warned against. ASPIS's thin agent files are the right call. |

---

## 3. Devin / Cognition — fleet of Devins + evaluator agent

### 3.1 Fleet pattern

> *"Devin can spin up a team of Devins for large tasks. Devin gets
> better over time by reading past session trajectories."*

A Devin session is one task; a *fleet* of Devins is the production unit.
Each Devin runs in a **real Linux VM with root access** — the
environment *is* the product. The user sets up the dev environment;
Devin inherits it.

### 3.2 Task distribution

Tasks are *assigned*, not "any Devin picks up any task." The fleet is
shaped by:

1. A *task graph* (dependencies, ordering).
2. A *team-of-Devins* instance per large scope.
3. Each Devin owns a narrow slice — same shape as Cursor's subplanners.

### 3.3 The evaluator agent (the standout pattern)

> *"An evaluator agent ... judges the deliverable against typed
> criteria (e.g. 'does the dashboard have more than 5 graphs?')."*

The evaluator has the *same tools* as the building agent (browsing,
shell, code editing). It is a **separate model** running in a **separate
context**. This is the *adversarial reviewer in fresh context* pattern,
applied with **typed criteria** — not "is this code good" but "does it
meet this specific list of assertions."

Cognition reports **74.2% on their internal `cognition-golden`
benchmark autonomously** with this pattern.

### 3.4 Compounding learning (the long-run story)

From the Nubank case study:
- **8-12x engineering-time efficiency gain, 20x cost savings** on a
  6M-LOC monolith split into sub-modules (originally 18 months, 1,000+
  engineers, completed in weeks).
- **Fine-tuning doubled task-completion scores and 4x'd speed** (40
  min/sub-task → 10 min) on the migration benchmark.
- Devin *built itself classical tools* (e.g. country-extension detector)
  and reused them across sub-tasks — **compounding learning, not just
  per-task.**

The takeaway: the per-task loop is fine, but the system that *wins*
over months is one that *learns which tools work* and *reuses* them.

### 3.5 What ASPIS should take from Devin

| Pattern | ADOPT / ADAPT / REJECT | ASPIS mapping |
|---|---|---|
| Fleet of agents for large scope | **DEFER** — same as Cursor's recursive subplanners. ASPIS's dependency-ordered features don't need it. |
| Each agent in a real VM with full env | **ADAPT** — when ASPIS's runtime ships, the build environment must be *the whole env*, not a thin proxy. The `runtime_guard` + `scope_guard` is the start. |
| **Evaluator agent with typed criteria** | **ADOPT — STRONG.** ASPIS's Reviewer should be evaluator-shaped. The packet's `acceptance` block *is* the typed criteria. The reviewer verifies each criterion explicitly. This is the cheap upgrade. |
| Compounding learning (built-its-own-tools) | **DEFER** — Phase 3+ self-improvement. ASPIS has the *shape* (skill registration, lessons loop) but not the *measurement*. |
| Fine-tuning for cost | **DEFER** — ASPIS uses third-party models. Fine-tuning is out of scope. |
| Each agent in a real VM | **ADAPT** — see runtime guard note above. |

---

## 4. GitHub Copilot — cloud agent in sandbox + AI code review

### 4.1 The cloud agent loop

From GitHub's *Agent HQ* launch (2025-10-28) and Copilot code review
docs (2026):

1. Engineer creates an issue (or assigns the Copilot coding agent one).
2. Agent works in a **cloud environment** (GitHub Actions-powered); opens
   a draft PR.
3. PR runs through CI; the **agent responds to CI failures
   automatically**.
4. **Copilot code review** (Low or Medium effort) reviews the PR — now
   *with* agentic capabilities: full project context gathering and the
   ability to pass suggestions back to the cloud agent as a follow-up PR.
5. Human reviewer approves; merge.

### 4.2 The hard session cap

> *"Each Copilot cloud agent session has a maximum execution time of
> 59 minutes. This is a hard limit that cannot be extended or bypassed."*

The stop condition is **time**, not "the agent thinks it's done." This
is the *deterministic cap* applied to long-running tasks.

### 4.3 Code review — Low/Medium effort

> *"**Low** (standard, fast) vs **Medium** (higher-reasoning model,
> longer analysis, more credits, more Actions minutes). Use Medium for
> security-sensitive code, multi-service pull requests, or repositories
> with strict quality standards."*

This is the **mode dial** applied to the *review* step, not the build.
The same PR can be reviewed at Low or Medium depending on criticality.
A *small* but real cost lever: 22% cheaper on Cursor's equivalent
(Bugbot on Composer 2.5).

### 4.4 Branch controls (the policy plane)

> *"Granular oversight of when CI runs for agent-created code ... the
> team can decide 'agents can push to feature branches without CI; CI
> runs on PR open' vs 'every push runs CI.'"*

ASPIS doesn't have a "feature branch without CI" mode today — every
build runs the gate. The equivalent policy decision is *which gate
runs*: fast (format + lint) vs. full (format + lint + type + test).
Mode-dial the gate, not just the review.

### 4.5 What ASPIS should take from Copilot

| Pattern | ADOPT / ADAPT / REJECT | ASPIS mapping |
|---|---|---|
| Cloud agent in CI environment | **DEFER** — ASPIS builds local today. Cloud is Phase 3+. |
| Agent responds to CI failures automatically | **ADAPT** — ASPIS's per-task gate already does this. The "responds automatically" part is the build-lead's per-task loop. The next step: have the gate's output feed a *fix decision* (trivial → builder, structural → fix-lead) without human routing. |
| **59-min hard session cap** | **ADOPT** — ASPIS should cap per-task attempts (already does: 3) and consider a wall-clock cap. A 30-min default with a 3-attempt loop is the right shape. |
| **Low/Medium review effort** | **ADOPT — STRONG.** Map to ASPIS's mode dial: vibe → Low (cheap + fast), production → Medium (deep + slow). The reviewer is the cost lever. |
| Branch controls | **ADAPT** — when ASPIS supports multiple worktrees, gate-mode per worktree. Today: per-feature fast vs full gate. |
| Agent identity (which agent built what) | **ALREADY TRUE** — R-007 trace records `agent_id + run_id + commit`. |
| AI review → AI build handoff (suggestions back) | **ADOPT — STRONG.** Reviewer can produce *follow-up tasks* the build-lead routes to a builder. Today the reviewer hands back to the human; a "follow-up PR" pattern is the cheap upgrade. |

---

## 5. OLD ASPS build-lead — the post-mortem that should drive ASPIS design

This section reads from `old-asps-deep-analysis-1.md` and the F-026 run
notes. The OLD ASPS build-lead is the most-instrumented agent in the
system, and the failure modes are *the* load-bearing lessons for the
new design.

### 5.1 What the build-lead did well

These are the patterns ASPIS should keep verbatim:

1. **Hold the whole-feature context.** Build Lead reads PLAN + TASKS;
   the worker reads the packet. The Lead is the only one who knows the
   whole picture. ✅ Keep.
2. **Gates-first (R-002).** The product gate (`.asps/gates.yaml`) is run
   as ONE command before "done" — never trust the builder's report.
   ✅ Keep, with the per-task vs per-feature cadence from Cursor.
3. **Scope discipline (R-001).** Builder only touches files in
   `scope.allowed`; scope is enforced at three boundaries (packet,
   frontmatter, pre-commit hook). ✅ Keep.
4. **3-attempt hard cap.** Two re-delegates with the failing gate output,
   then `REVIEW_NEEDED` to the human. ✅ Keep.
5. **Trace every step (R-007).** `delegation`, `edit`, `gate_result`,
   `fail`, `phase_end` events. ✅ Keep.
6. **Trivial-fix routing.** If the gate fail is trivial (format, typo),
   send back to the builder; if structural (logic, scope, regression),
   hand to `asps-fix-lead`. ✅ Keep.

### 5.2 What failed (the lessons)

#### 5.2.1 F-026 — Build Lead cannot reach any reviewer

> *"Lead builder cannot reach any reviewer. Its prose says 'on gate
> pass, hand off to the tester→reviewer loop,' but its `task:`
> permission only allows `python-builder` and `api-builder`. So review
> **cannot happen inside the loop** — the claimed handoff is blocked
> by the permission block."*
> — `local/agent-notes/asps-build-lead.md`

This is the **biggest open gap** in the OLD ASPS. The build-lead was
*told* to hand off; the permission block made the handoff impossible;
the system silently fell back to writing `REVIEW_NEEDED` to the review
queue, parked for human attention.

**The fix for ASPIS:** the build-lead's `task:` permission *must* allow
`reviewer`, `test-lead`, `fix-lead`, and `committer` — not just
`general-builder`. The handoff is reachable in the *permission layer*,
not just in prose. The current ASPIS design fixes this in the
delegation table (`local/agents/build-lead.md`), but **this lesson
should be codified in a permission-audit check** that fires on any
agent's frontmatter change.

#### 5.2.2 The 13 zero-byte junk files

> *"Builders wrote ~13 zero-byte junk files (shell-redirect misfires)
> — needs a no-stray-file guard and a `ruff format` step in the gate."*

The failure: the builder used a shell-redirect pattern (`> file.py`)
that misfired and left 13 zero-byte files in the repo. The gate didn't
catch them; the next agent tried to import them and crashed.

**The fix for ASPIS:** add a **pre-edit guard** to the build workflow:
before any edit, the worker reports the *intended* file set in the
BUILD_REPORT, and the committer / scope-checker verifies that the
actual filesystem matches. A 0-byte file is a *fingerprint* of a failed
edit and should be caught before commit. Concrete:

- A `pre-commit` hook (or scope-guard script) that flags 0-byte files
  in the diff and refuses.
- A `ruff format --check` step in `.asps/gates.yaml` (a 0-byte file
  fails format).
- A **stray-file guard** that compares the packet's `allowed` set to
  the actual files touched — files not in the packet's set are a
  scope violation.

#### 5.2.3 No-stray-file guard (the missing primitive)

> *"`asps preflight` should be enhanced with a **no-stray-file check**:
> any file in the diff that is not in the task packet's `allowed`
> set, and not a generated artifact, is a stray and blocks commit."*

The current ASPIS has scope-control (R-001) and the pre-commit hook
that reads `feature.yaml` for scope. The gap: the **per-task packet**
doesn't currently declare its `allowed` set in a machine-checkable
form. **Add a `files.allowed` block to the task packet template** —
a YAML list of globs the builder is allowed to touch. The hook
verifies the diff ⊆ packet.allowed ∪ packet.generated.

#### 5.2.4 Gate over-trust

The OLD ASPS build-lead ran the gate *after* the builder's report
arrived. The risk: the builder reports "done," the lead runs the gate,
the gate fails, the lead re-delegates. The cycle is correct, but the
builder's *initial* report is over-trusted — the lead doesn't sanity-
check the diff before running the gate.

**The fix for ASPIS:** the build-lead should run **two cheap checks
before the full gate**:
1. `git status` — is the diff actually in the expected files? (catches
   the stray-file failure).
2. `ruff check --diff` (incremental) — does the diff itself lint?
   Catches 80% of trivial failures in <1s.

Only then run the full gate. This is a **"first-fail-fast"** pattern
the industry uses widely but ASPIS doesn't currently encode.

#### 5.2.5 Skip ruff format

> *"`python-builder` ... skipped `ruff format` once and wrote ~13
> zero-byte junk files (shell-redirect misfires) — needs a no-stray-
> file guard and a `ruff format` step in the gate."*

The 13 zero-byte files were *partly* caught by the missing `ruff
format` step in the gate. If the gate had `ruff format --check`, the
empty files would have failed. The lesson: **the gate must include
format, not just lint and type.** Empty files fail format. Empty files
are real.

### 5.3 What ASPIS must learn from F-026 (consolidated)

| Failure | ASPIS fix |
|---|---|
| Build-lead cannot reach reviewer | Codify handoff edges in `task:` allowlist; add a permission-audit check on frontmatter change. |
| 13 zero-byte junk files | Add `ruff format --check` to gate; add no-stray-file guard (diff ⊆ packet.allowed ∪ packet.generated). |
| No `files.allowed` in packet | Add a YAML `files.allowed` block to TASK_PACKET template; enforce in scope-guard. |
| Gate over-trust | Add first-fail-fast pre-checks (`git status`, `ruff check --diff`) before full gate. |
| Builder skips format | Already in OLD ASPS's two-pass gate. Verify it's wired in ASPIS's `.aspis/gates.yaml`. |
| 3-attempt cap silently exceeded | Add a `attempts_used` field to the build report; refuse on 4th attempt. |

---

## 6. Builder context isolation — the proven pattern

The strongest cross-source signal in the research is **context isolation**
— every production system in 2026 uses it; the mechanism is consistent.

### 6.1 The pattern (one description, multiple implementations)

| System | How isolation works | What the worker sees |
|---|---|---|
| **Cursor (self-driving)** | Worker on own copy of repo | Only the task packet; not aware of other workers or planners |
| **Cursor (cloud agents)** | Conversation state in Temporal; agent loop decoupled from VM | The packet + its own conversation; no global view |
| **Anthropic (subagents)** | Fresh context window; own tools; own model choice | Only the subagent's task; returns a 1-2k-token summary |
| **Anthropic (Writer/Reviewer)** | Two parallel sessions, fresh context each | Writer sees plan; Reviewer sees diff + criteria |
| **Claude Code (Stop hook)** | Hook runs in the same context; but the *check* is deterministic, not context-driven | The check is a script, not a re-prompt of the agent |
| **OpenAI Codex** | Per-worktree environment; "bootable per git worktree" | Only its worktree + task |
| **Devin** | Real Linux VM per task; root access | Only its VM + the fleet's task assignment |
| **Copilot cloud agent** | Per-session GitHub Actions environment | Only the assigned issue + repo context it gathers |
| **Cognition evaluator agent** | Same tools as the builder, different model, different context | Only the deliverable + the typed criteria |

### 6.2 The three properties that hold across all systems

1. **No shared mutable state for coordination.** Handoffs are messages.
   Locks fail (Cursor's lesson). Coordination files fail (same lesson).
2. **The worker's context is *smaller* than the planner's, by design.**
   The planner holds the whole-feature context; the worker holds the
   packet. The orchestrator (cheap model) sees only distilled summaries.
3. **A fresh context is unbiased.** A subagent that didn't write the
   code can spot what the writer can't (Anthropic, Cursor Bugbot, METR).

### 6.3 What ASPIS already has (and what's missing)

ASPIS's current design ([ASPIS]):
- ✅ Build Lead holds the whole-feature context.
- ✅ `general-builder` is context-isolated (fresh subagent, sees only
  the packet).
- ✅ `quality-review` skill + Reviewer lead are read-only, separate
  context.
- ❌ **No `sub-reviewer` agent.** Build.md step 3d says "per-task
  reviewer in subagent context" but the agent doesn't exist; every
  review escalates to the Reviewer lead. **The biggest gap.** Fix:
  add a `sub-reviewer` agent to the catalog (L3 leaf, read-only, fresh
  context, sees only diff + criteria).
- ❌ **No `stray-file guard`.** The committer's scope check is
  per-feature (`feature.yaml`); not per-task. **Add a per-task
  `files.allowed` block to the packet template.**
- ❌ **No `attempts_used` cap enforcement.** The 3-attempt cap is in
  the lead's prose; the system doesn't refuse on 4th attempt
  structurally. **Add an `attempts_used` field to the build state
  file; the script refuses to re-delegate when ≥ 3.**

### 6.4 The minimal builder context-isolation contract

For ASPIS, every worker that takes a task packet should be contractually
bound by these rules (enforced in frontmatter, not prose):

```yaml
# Per the worker's frontmatter
mode: subagent
isolation: fresh_context    # the runtime opens a new context for this agent
sees:
  - the task packet
  - the read-only project context (per context-ladder level 1-2)
does_not_see:
  - the planner's whole-feature context
  - the conversation of other workers
  - the run history of previous tasks (except as summarized in packet)
returns:
  - a 1-2k-token distilled summary (the BUILD_REPORT shape)
  - the actual diff (committed via the committer, not the worker)
```

---

## 7. Gate execution patterns — frequency and granularity

### 7.1 The three proven cadences

| Cadence | Used by | What runs | Cost | When |
|---|---|---|---|---|
| **Per-tool-call** (in the agent loop) | Cursor Auto-review (the *classifier*); ASPIS's deterministic allowlist | A small classifier or a static rule check | Sub-second | Every tool call — the "is this risky?" check |
| **Per-task** (after a worker handoff) | ASPIS R-002; OpenAI Codex harness; Claude Code Stop hook | The full product gate (`.asps/gates.yaml`) | Seconds to minutes | After every worker handoff — the "is this handoff acceptable?" check |
| **Per-feature / per-merge** (the integration pass) | Cursor self-driving (the "final green" pass); GitHub Copilot (the merge gate) | The full test suite + multi-lens review + acceptance | Minutes | Before promotion to main / before feature close — the "is the whole thing shippable?" check |

### 7.2 The decision matrix — when to use which

| Need | Cadence | Mechanism |
|---|---|---|
| "Should I run this `rm -rf`?" | Per-tool-call | Classifier (Auto-review style) OR deterministic allowlist (ASPIS today) |
| "Did this builder handoff land green?" | Per-task | `.asps/gates.yaml` (R-002) |
| "Is this feature ready to merge?" | Per-feature | Acceptance check (FR-###, SC-###) + full test suite + multi-lens review |
| "Did the agent do something dangerous 5 minutes ago?" | Continuous | Trace (R-007) + `asps doctor --post-run` |
| "Are we shipping a broken release?" | Per-release | The platform (Vercel, Replit, AWS) deploys + monitors + rolls back |

### 7.3 The right frequency (the load-bearing answer)

**Per-task gate is the right default.** It's the unit of work, the unit
of the packet, and the unit the committer commits. It catches the
*most* failures for the *least* cost.

**Per-commit 100% correctness is the anti-pattern** (Cursor's explicit
finding). It serializes the system; workers pile on the same issue.

**Per-feature acceptance is the contract** — the build-lead is not done
until all FR-### / SC-### are checked. But the *gates* that *enforce*
the contract run per-task. The per-feature pass is the reconciliation,
not a re-run of every per-task gate.

### 7.4 What ASPIS has and what's missing

| Mechanism | Status | Action |
|---|---|---|
| `.asps/gates.yaml` as ONE command | ✅ Have | Verify it includes `ruff format --check` (catches 0-byte files) |
| Per-task gate after each worker handoff | ✅ Have | — |
| 3-attempt hard cap | ✅ Have in prose | Add `attempts_used` field; refuse on 4th |
| First-fail-fast pre-checks (status, lint --diff) | ❌ Missing | Add to build.md step 5 |
| Per-feature acceptance check (FR-###, SC-###) | ✅ Have (ACCEPTANCE.md) | Verify it runs *after* all tasks, not per-task |
| Per-tool-call risk classifier (Auto-review style) | ❌ Deferred to Phase 3+ | Note as a follow-up feature |
| Continuous trace (R-007) | ✅ Have | — |
| Pre-commit hook refuses junk messages | ✅ Have | — |
| Pre-commit hook refuses scope violations | ✅ Have (scope_guard) | Extend to **per-task `files.allowed`** check |
| Pre-commit hook refuses 0-byte files | ❌ Missing | Add to scope_guard |
| **Acceptance reconciliation pass** (Cursor's "final green") | ⚠️ Implicit (per-feature report) | Make it explicit: a `feature close` step that runs the *whole* acceptance suite + multi-lens review, owned by the build-lead |

### 7.5 The "final green" pass — Cursor's contribution to ASPIS design

Cursor's most underrated lesson:

> *"This may indicate that the ideal efficient system accepts some
> error rate, but a final 'green' branch is needed where an agent
> regularly takes snapshots and does a quick fixup pass before release."*

This is a *named* pattern. It is **not** "run all tests again." It is
*"an agent (or a script) takes the current state, identifies the
remaining issues, fixes them, and ships."* The agent is doing
*reconciliation*, not re-execution.

ASPIS has the *shape* of this in the per-feature acceptance check, but
not the *agent*. The current ASPIS workflow is:

```
build all tasks → reviewer reviews each → committer commits each →
per-feature acceptance check → hand to human for close
```

A "final green" pass would add:

```
build all tasks → reviewer reviews each → committer commits each →
[final green] → run all tests + acceptance + multi-lens review →
fix the small remaining issues → ship
```

The [final green] is owned by the build-lead; the fixes are routed
through the normal fix path (trivial → builder, structural → fix-lead).
This is the *one structural change* the research suggests for the
ASPIS build workflow. Cost: 1 extra script. Benefit: the
*reconciliation failure mode* (small accumulated drift across many
tasks) is caught automatically.

---

## 8. Cost control in builds — cheap models without lowering quality

From `cheap-models-quality.md`, the operational data and the patterns.

### 8.1 The proven cost numbers

| Source | What they did | Result |
|---|---|---|
| **Wayfair** (Jun 2026) | 5 researchers, 4-day sprint, 110 model variants tested by 20+ parallel Cursor agents | **94% cost reduction** + another **90%** (cumulative ~99%) on production tag-validation model |
| **Cursor Bugbot** (Jun 2026) | Switched PR-review from frontier to Composer 2.5 (Cursor's trained model) | **22% cheaper**, 3× faster, **+10% more bugs**. 90% of runs < 3 min |
| **Anthropic SWE-bench** (Sep 2025) | Sonnet 4.5, bash+edit scaffold, 200K thinking budget, 10 trials | **77.2%** single-model. With parallel sampling + rejection + scoring: **82.0%** at ~5-8× cost (still ~5× cheaper than Opus) |
| **Anthropic Cybersecurity / Hai** (Sep 2025) | Migrated Hai security stack to Sonnet 4.5 | **44% faster** vulnerability intake, **+25% accuracy** |
| **Replit** (Sep 2025) | Internal code-editing benchmark | **9% error rate → 0%** |

### 8.2 The "model that builds is rarely the model that judges" rule

> *"Cursor Bugbot is now Composer 2.5 (Cursor's own cheap model,
> $0.50/$2.50) and ships 10% more bugs at 22% lower cost vs. the
> previous frontier model."*

The single biggest cost lever in build-execution:

- **Build:** standard-tier model. Does the implementation, runs the
  tests, returns the diff.
- **Review:** cheap-tier specialised model. Reads the diff + criteria,
  returns findings. *Faster, cheaper, often better* because it's
  *trained on the task* (Composer 2.5 is fine-tuned for review).
- **Classify / route:** cheap-tier (Haiku 4.5, Flash-Lite). The
  Auto-review classifier is small and fast.
- **Decide / judge:** mid or frontier. Architecture, root cause,
  security verdict.

ASPIS's current model tier strategy (70/20/10 cheap/standard/deep) is
*aligned* with this. The gap: **the Reviewer is currently `standard`
tier in the catalog intent but `deep` in the live deployment**. The
*correct* mapping is `cheap` for routine review, `standard` for
multi-lens, `deep` only for security / architecture / root-cause.

### 8.3 The five quality-preserving patterns (re-stated for build)

From `cheap-models-quality.md` §3, applied to the build-lead's world:

1. **Tiered routing.** A cheap classifier routes tasks to the right
   tier. Cheap-by-default; escalate on explicit signals (multi-file,
   security, "investigate"). **The build-lead's `task-orchestration`
   skill is the closest ASPIS analog** — it decides which builder
   model to use.
2. **Sub-agent isolation.** Each subagent runs in its own context
   window with the right model for that sub-task. The orchestrator
   (cheap) sees only distilled summaries. **Already true** for
   `general-builder`.
3. **Cascade on failure.** Cheap-first, escalates on measurable
   failure (test fail, lint error, schema invalid). Cap: 3 cheap → 1
   mid → 1 deep. **ASPIS's per-task loop is 3 attempts deep; should
   add a tier escalation within the 3.**
4. **Verifier in the loop.** A deterministic check (test, lint,
   type-check) is always more reliable than an LLM judge. Cheap model
   writes → deterministic verifier grades → if fail, escalate. **R-002
   is this exact pattern.**
5. **Frontier for judgment, cheap for context.** Mechanise the 80%
   (parsing, exploration, summarisation) with cheap models. Reserve
   the 20% (architecture, root cause, security) for frontier. **The
   build-lead is the orchestrator; should be mid or deep. The
   general-builder should be standard. The sub-reviewer should be
   cheap. The triage (bug-triager, scope-check) should be cheap.**

### 8.4 The build-lead's per-tier mapping (proposed)

| Agent | Current tier | Proposed tier | Why |
|---|---|---|---|
| `build-lead` (orchestrator) | deep | **standard or deep** | Holds whole-feature context; needs general intelligence; cheap loses coherence. *Deep is overkill; standard should suffice.* |
| `general-builder` (per task) | standard | **standard** (unchanged) | Implementation is mid-tier work; cheap loses quality on multi-file edits. |
| `sub-reviewer` (per task, fresh context) | doesn't exist | **cheap** | Review is the *judge* role; cheap specialised model is the proven pattern. |
| `reviewer` (multi-lens lead) | standard live / deep catalog | **standard** | Multi-lens aggregation is mid-tier; deep is reserved for security/architecture. |
| `commit-reviewer` (per commit) | standard | **cheap** | The check is mechanical (scope, status, branch); LLM-as-judge is the wrong shape. |
| `security-reviewer` | standard | **deep** | Security is the *judgment* role; deep is correct. |
| `bug-triager` | standard | **cheap** | Triage is classification; cheap is the proven pattern (Cursor Auto-review). |

### 8.5 The "cascade within 3 attempts" pattern (the missing primitive)

ASPIS's 3-attempt cap is *flat*: 3 attempts of the same model. The
Cursor / Sonnet 4.5 lesson is that **attempts can escalate in tier**:

```
Attempt 1: cheap (Haiku / Flash-Lite) — most tasks land here.
Attempt 2: standard (Sonnet 4.6 / DeepSeek v4-pro) — if attempt 1 fails.
Attempt 3: deep (Opus 4.8 / DeepSeek v4-pro deep) — if attempt 2 fails.
→ If attempt 3 fails, REVIEW_NEEDED.
```

This compresses the cost curve. The cheap model handles the 70% of
tasks it can; the deep model handles the 5% that need it; the rest
escalates. ASPIS should add a `tier` field to the task packet
(`cheap | standard | deep | auto`) and let the cascade default to
`auto` (cheap → standard → deep, capped at 3).

---

## 9. ADOPT / ADAPT / REJECT — the matrix

A consolidated decision matrix per system, scoped to build-lead design.

### 9.1 Cursor

| Pattern | Decision | Build-lead impact |
|---|---|---|
| Root planner + subplanners + workers | **ADAPT (Phase 3+)** | Today: build-lead is the planner, general-builder is the worker. Recursion is a Phase 3+ extension when features are large enough to warrant. |
| Worker handoff carries concerns | **ADOPT** | Add `## Concerns / Deviations / Findings` block to BUILD_REPORT template. Build-lead reads and propagates to reviewer / fix-lead / next task. |
| No shared coordination file | **REINFORCE** | ASPIS brain is for humans + single agents, not multi-agent coordination. Don't extend. |
| 100% per-commit correctness is anti-pattern | **REJECT** (already correct in ASPIS) | Per-task gate is the right cadence. Don't move to per-commit. |
| No central integrator | **ADAPT** | ASPIS's "single committer" is not an integrator (it doesn't gate all work). Reviewer-as-committer is *quality + write fusion*, not a global gate. Keep. |
| 1,000 commits/hour scale | **DEFER** | Not ASPIS's shape. |
| Temporal durable execution | **DEFER** (Phase 3+) | ASPIS tasks are short. |
| Auto-review classifier (4% block) | **DEFER** (Phase 3+) | Today's deterministic allowlist is sufficient. |
| Bugbot on cheap model | **ADOPT — STRONG** | Reviewer should default to cheap; deep only for security / architecture. |
| `gh` as agent tool (not harness) | **ALREADY TRUE** | `aspis commit`, `git`, `pytest` are all available. Don't hide them. |
| **Final-green reconciliation pass** | **ADOPT** | Add a `feature close` step that runs the full acceptance suite + multi-lens review + fixes the small remaining issues. |

### 9.2 Claude Code

| Pattern | Decision | Build-lead impact |
|---|---|---|
| 4-phase loop (explore → plan → implement → commit) | **ALREADY TRUE** | Build-lead owns implement + commit-handoff. |
| "Skip plan if you can describe the diff in one sentence" | **ADOPT** | Trivial-task fast path in build.md (no SPEC/PLAN/TASKS, direct implement). |
| 4-strength verification gradient | **ADAPT** | Document in build.md. Default Stop-hook (R-002); escalate to sub-reviewer for production mode. |
| /goal re-check after every turn | **ADAPT** | Per-task gate is the re-check. Acceptance is the /goal. |
| **Fresh-context subagent review** | **ALREADY TRUE (partial)** | Add the `sub-reviewer` agent. The biggest gap. |
| Writer/Reviewer parallel sessions | **ADOPT** | When the packet is high-criticality, run a fresh-context reviewer in parallel to the next task. |
| Auto mode (classifier) | **DEFER** | Phase 3+. |
| Prefilled responses | **REJECT** | Deprecated. |
| One big CLAUDE.md | **REJECT** | Thin agent files are the right call. |
| Plan mode (explore without changes) | **ADOPT** | The build-lead should default to "read-only mode" when reading the plan + packet + codebase; only switch to edit mode when the actual builder runs. |

### 9.3 Devin / Cognition

| Pattern | Decision | Build-lead impact |
|---|---|---|
| Fleet of agents for large scope | **DEFER** | Not ASPIS's shape. |
| Real VM with full env | **ADAPT** | When ASPIS runtime ships, the build env must be the whole env, not a thin proxy. |
| **Evaluator agent with typed criteria** | **ADOPT — STRONG** | Reviewer should be evaluator-shaped. The packet's `acceptance` block is the typed criteria. The reviewer verifies each criterion explicitly. Cheap upgrade, big quality win. |
| Compounding learning | **DEFER** | Phase 3+ self-improvement. |
| Fine-tuning for cost | **DEFER** | Out of scope. |

### 9.4 GitHub Copilot

| Pattern | Decision | Build-lead impact |
|---|---|---|
| Cloud agent in CI environment | **DEFER** | Phase 3+. |
| Agent responds to CI failures | **ALREADY TRUE** | Per-task gate. |
| 59-min hard session cap | **ADOPT** | Add a wall-clock cap. 30-min default + 3-attempt loop. |
| **Low/Medium review effort** | **ADOPT — STRONG** | Mode-dial the reviewer. Vibe → cheap. Production → standard or deep. |
| Branch controls (when CI runs) | **ADAPT** | Per-feature fast vs full gate. |
| Agent identity (which agent built what) | **ALREADY TRUE** | R-007 trace. |
| **AI review → AI build handoff (follow-up PR)** | **ADOPT — STRONG** | Reviewer can produce *follow-up tasks* the build-lead routes to a builder. Today the reviewer hands back to the human. |

### 9.5 OpenAI Codex (additional)

| Pattern | Decision | Build-lead impact |
|---|---|---|
| Per-worktree environment | **ADAPT (Phase 3+)** | When ASPIS supports multiple worktrees, isolate builders per worktree. |
| Chrome DevTools for visual validation | **DEFER** | Out of scope for F-016 (file-first, not browser-first). |
| Logs/metrics/traces as agent tools (LogQL/PromQL) | **DEFER** | Out of scope. |
| Linter error message *injects remediation* into agent context | **ADAPT** | The build-lead's gate output should be *reformulated* for the builder's next attempt. Don't just paste the gate log; translate to "fix this file, this line, this test." |
| 3.5 PRs/engineer/day, 1,500 PRs in 5 months | **REFERENCE** | The throughput target for ASPIS's fully-built production loop. Not the build-lead's local target. |

### 9.6 OLD ASPS lessons (consolidated)

| Pattern | Decision | Build-lead impact |
|---|---|---|
| F-026: build-lead can't reach reviewer | **FIX** | `task:` permission must allow `reviewer`, `test-lead`, `fix-lead`, `committer`. Codify in a permission-audit check. |
| 13 zero-byte junk files | **FIX** | Add `ruff format --check` to gate; add no-stray-file guard (diff ⊆ packet.allowed ∪ packet.generated). |
| No `files.allowed` in packet | **FIX** | Add YAML `files.allowed` to TASK_PACKET template. Enforce in scope-guard. |
| Gate over-trust | **FIX** | Add first-fail-fast pre-checks (status, lint --diff) before full gate. |
| Skip ruff format | **VERIFY** | Confirm `ruff format --check` is in `.aspis/gates.yaml`. |
| 3-attempt cap silently exceeded | **FIX** | Add `attempts_used` field to build state. Refuse on 4th. |
| Trivial-vs-structural fix routing | **KEEP** | Build-lead → trivial back to builder; structural → fix-lead. |

### 9.7 Cheap-model patterns (consolidated)

| Pattern | Decision | Build-lead impact |
|---|---|---|
| Tiered routing | **ALREADY TRUE** | Task packet's `model_tier` field (when added). |
| Sub-agent isolation | **ALREADY TRUE** | General-builder. |
| **Cascade within 3 attempts (cheap → mid → deep)** | **ADOPT** | Add `tier: cheap|standard|deep|auto` to packet. Default `auto`. |
| Verifier in the loop | **ALREADY TRUE** | R-002. |
| **Model that builds ≠ model that judges** | **ADOPT — STRONG** | Build = standard. Sub-reviewer = cheap. Reviewer lead = standard. Security = deep. Commit-reviewer = cheap. |
| Per-tier metrics (cost, pass rate, escalation) | **ADAPT (Phase 3+)** | Trace should record model + tokens + outcome per task. |
| Wayfair 90%+ cost cut | **REFERENCE** | The cost target for a fully-tuned ASPIS production loop. |

---

## 10. The build-lead design implications (synthesis)

Putting §1-§9 together, here are the concrete changes for the
ASPIS build-lead (in priority order).

### 10.1 P0 — must fix (correctness blockers)

1. **Add `sub-reviewer` agent to the catalog.** L3 leaf, read-only,
   fresh context, sees only the diff + the packet's acceptance
   criteria. The Reviewer lead is *not* the per-task reviewer. *(§6.3,
   §9.2, §9.9)*
2. **Add `files.allowed` to TASK_PACKET template.** YAML list of
   globs. Enforced in scope-guard (pre-commit). The committer
   refuses any file outside the set. *(§5.2.3, §5.3, §9.6)*
3. **Add `attempts_used` field to the build state.** The build script
   refuses to re-delegate when ≥ 3. The 3-attempt cap is
   *structural*, not *prose*. *(§5.3, §9.6)*
4. **Verify `.aspis/gates.yaml` includes `ruff format --check`.** This
   is the 0-byte-file guard. *(§5.2.2, §5.2.5, §9.6)*
5. **Verify `task:` permission on the build-lead includes reviewer,
   test-lead, fix-lead, committer.** F-026 was a permission bug, not
   a workflow bug. *(§5.2.1, §9.6)*

### 10.2 P1 — should fix (quality and cost wins)

6. **Add a "final-green" pass to the build workflow.** A `feature
   close` step that runs the full acceptance suite + multi-lens
   review, owned by the build-lead, fixes the small remaining
   issues. *(§7.5, §9.1)*
7. **Add tier escalation within the 3-attempt loop.** Cheap →
   standard → deep, capped. Default `auto`. *(§8.5, §9.7)*
8. **Mode-dial the reviewer.** Vibe = cheap sub-reviewer. Production
   = standard sub-reviewer + deep security review. *(§4.3, §9.4)*
9. **Add `## Concerns / Deviations / Findings` block to BUILD_REPORT.**
   Build-lead reads and propagates. Reviewer reads. *(§1.3, §9.1)*
10. **Add first-fail-fast pre-checks (`git status`, `ruff check
    --diff`) before the full gate.** Catches 80% of trivial
    failures in <1s. *(§5.2.4, §9.6)*

### 10.3 P2 — defer (Phase 3+ or out-of-scope)

11. **Recursive subplanners** (build-lead can spawn a sub-build-lead
    for a sub-feature). *(§1.1, §9.1)*
12. **Per-tool-call risk classifier** (Auto-review style). *(§1.7,
    §9.1, §9.2)*
13. **Temporal-style durable execution** for the runtime. *(§1.6,
    §9.1)*
14. **Cloud agent in CI environment.** *(§4.1, §9.4)*
15. **Compounding learning (built-its-own-tools).** *(§3.4, §9.3)*

### 10.4 P3 — reference (not actionable today)

16. **Wayfair 90%+ cost cut** — the cost target for a fully-tuned
    production loop, not the build-lead's local target.
17. **3.5 PRs/engineer/day** (OpenAI Codex) — the throughput target.
18. **1,000 commits/hour** (Cursor self-driving) — the upper bound
    on multi-agent; not ASPIS's shape.

---

## 11. The build-lead's contract (post-research, restated)

After applying this research, the build-lead's contract is:

1. **Read the plan, not just the packet.** Whole-feature context.
2. **Enrich the packet** with `files.allowed`, `files.generated`,
   `model_tier`, `acceptance`, `attempts_used`, `concerns_block`.
3. **Delegate to a context-isolated worker** (`general-builder`),
   fresh subagent, sees only the packet. The worker does *not* see
   the planner's whole context.
4. **Run the per-task gate** (R-002: `ruff format --check`, `ruff
   check`, `mypy`, `pytest` per the project's gate spec). First-fail
   fast checks (`git status`, `ruff check --diff`) before the full
   gate.
5. **On gate fail:** re-delegate with the *reformulated* gate output
   (translated to "fix this file, this line, this test"). Cascade
   model tier (cheap → standard → deep) if `model_tier=auto`. After
   3 attempts, write `REVIEW_NEEDED` and stop.
6. **On gate pass: route to the per-task sub-reviewer** (L3 leaf,
   fresh context, sees only diff + acceptance). For high-criticality
   or cross-cutting, route to the Reviewer lead.
7. **On review approve: hand to the committer.** The build-lead
   never commits directly (R-004).
8. **On review fail:** re-delegate (trivial) or hand to fix-lead
   (structural). Same 3-attempt cap.
9. **At the per-feature close: run the "final-green" pass.** Full
   acceptance suite + multi-lens review. Fix the small remaining
   issues. The build-lead is the *owner* of the close.
10. **Trace every step** (R-007): delegation, edit, gate_result,
    fail, phase_end, model_tier_used, attempts_used.

---

## 12. What this research is and isn't

**Is:** an industry survey of build-execution patterns, validated
against primary sources, with concrete ASPIS changes prioritized.

**Isn't:** a redesign of the build-lead from scratch. The current
ASPIS build-lead is *already on the right track* — recursive
planner-workers is the proven pattern, context isolation is the
proven primitive, deterministic gate is the proven closer. The
research adds:

- The **fresh-context sub-reviewer** (the biggest gap).
- The **no-stray-file guard** (the F-026 lesson).
- The **mode-dialed reviewer cost** (the cheap-model win).
- The **final-green reconciliation pass** (the per-feature contract).
- The **tier-cascade within 3 attempts** (the cost-quality curve).

These five changes, together, bring ASPIS's build-lead from "matches
the proven 2024 patterns" to "matches the proven 2026 patterns."

**What's deliberately out of scope:** the runtime infrastructure
(durable execution, Temporal-style, worktree isolation), the model
selection (which Anthropic / OpenAI / Cursor model for which tier),
the agent catalog (which leaf workers exist), the trace spine
(implementation details of R-007), and the R-009 human gate
(unchanged from current design).

---

## 13. Provenance and refresh

**Sources read on 2026-06-25 / 26:**
- `production-loops-companies.md` (Research Lead, 2026-06-25, 880 lines)
- `core-loops-2026.md` (Research Lead, 2026-06-25, 895 lines)
- `old-asps-deep-analysis-1.md` (Research Lead, 2026-06-25, 632 lines)
- `cheap-models-quality.md` (Research Lead, 2026-06-25, 539 lines)
- `local/AGENT-SYSTEM-ARCHITECTURE.md` (current ASPIS architecture, 380 lines)
- `local/agents/build-lead.md` (current build-lead agent, 133 lines)
- `old-asps-deep-analysis-1.md` §12 (what's proven vs. experimental)

**Underlying primary sources** (cited in `production-loops-companies.md`):
- OpenAI, *Harness engineering* (Lopopolo, 2026-02-11)
- Anthropic, *Best practices for Claude Code* (2026)
- GitHub Blog, *Agent HQ* (Daigle, 2025-10-28)
- Cursor, *Towards self-driving codebases* (Lin, 2026-02-05)
- Cursor, *Cloud agents* (Ma, 2026-06-02)
- Cursor, *Auto-review* (Gomes & McPeak, 2026-06-11)
- Cursor, *Bugbot* (2026-06-10)
- Cognition / Devin, blog and product (2024-2026)
- METR, transcript analysis (2026-02-17)

**Refresh cadence.** Quarterly for benchmark numbers and cost data.
On major model release for tier recommendations. On any new build-
execution post-mortem at one of the surveyed companies.

**Most-stable findings** (won't change):
- Plan-then-act (Pattern 1)
- Deterministic gate (Pattern 2)
- Fresh-context reviewer (Pattern 3)
- Recursive planner-workers (Pattern 4)
- Rigor dial / mode (Pattern 5)
- No shared coordination file (anti-pattern)
- No central integrator (anti-pattern)
- 100% per-commit correctness is anti-pattern
- Model that builds ≠ model that judges
- F-026 permission bug (permanently, it's a system design lesson)

**Most-likely-to-change findings:**
- The exact tier mix (cheap/standard/deep) — model pricing moves
  quarterly.
- The exact throughput numbers (1,000 commits/hour, 3.5 PRs/day) —
  new releases shift the bar.
- The specific cheap-model cost numbers (22% Bugbot, 90% Wayfair) —
  one product launch can reset them.

---

*End of analysis.* This doc is the *external evidence* the build-lead
SPEC/PLAN/TASKS should be checked against. The internal architecture
is in `local/AGENT-SYSTEM-ARCHITECTURE.md` and `local/agents/build-lead.md`;
this research adds the 5 P0 + 5 P1 changes that bring the build-lead
from "matches the proven 2024 patterns" to "matches the proven 2026
patterns."

<!-- ASPIS:REFERENCE END -->
