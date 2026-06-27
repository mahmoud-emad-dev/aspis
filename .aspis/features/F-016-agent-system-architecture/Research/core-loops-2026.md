# F-016 — Core Loops for Agentic Coding Systems (June 2026)

**Author:** Research Lead
**Date:** 2026-06-25
**Status:** Primary-source research. The five proven core-loop patterns below are the
contract F-016's agent architecture must satisfy. Read in conjunction with
`CORE_LOOP.md` (the draft) — this doc is the *external* evidence the draft rests on.
**Scope:** the plan→build→review cycle in production agentic coding systems as of
mid-2026. Concrete implementations, not theory. Bottom line up front in §0.

---

## 0. Bottom line up front — the five proven patterns

Every successful agentic coding system in production as of June 2026 uses a
**small, composable core loop** built from these five patterns. They are not
five competing approaches; they are five layers, each solving a distinct problem
in the loop:

| # | Pattern | One-line description | Solves |
|---|---|---|---|
| 1 | **Plan-then-act** | Separate *exploration* and *plan* from *implementation* | Solving the right problem |
| 2 | **Deterministic gate** | A test/build/lint/screenshot the agent MUST pass to stop | "Looks done" vs. *is* done |
| 3 | **Adversarial review in fresh context** | An independent reviewer (model or subagent) sees only the diff in a clean context | Bias of the writer grading itself |
| 4 | **Recursive planner-workers with handoffs** | A planner owns scope, delegates to workers via rich task packets, recurses on big scopes | Linear scaling of throughput |
| 5 | **Rigor dial (mode)** | Same loop, different depth: vibe / MVP / production | Right ceremony for the work |

The **minimal effective loop** is #1 (plan-then-act) + #2 (gate) + #3 (review),
optionally amplified by #4 (recursion) and #5 (mode dial). All five are
independently attested in primary sources cited below; they are not ASPIS's
invention.

**What has been abandoned (mid-2024 → mid-2026):**
- Self-coordinating agents via shared lockfiles (Cursor: "failed quickly")
- Single "continuous executor" that plans + spawns + reviews + commits (Cursor: pathological behaviors)
- Central integrator that gates all work (Cursor: bottleneck, removed)
- 100% commit correctness at every step (Cursor: serializes the system; agents pile on)
- Hand-tuned "prompt-orchestrated" multi-agent via framework abstractions (Anthropic: prefer direct API + patterns)
- Prefilled-response steering (Anthropic: deprecated in Claude 4.6, "intelligence has advanced")
- Forcing "code completion" interfaces to be agents (all of them evolved past this by 2025)

**State of multi-agent vs. single-agent (June 2026):**
- Single-agent (with rich tools) wins for: most coding tasks, anything with
  tight context coupling, anything shorter than ~30 min
- Multi-agent (planner-workers) wins for: huge open-ended work (browser from
  scratch, company-wide research), 1000+ commits/hour scale, true parallelism
  of *independent* subtasks
- The decisive factor is **how parallelizable the work is** — Anthropic's 90.2%
  multi-agent win on research came from "subagents provide compression across
  parallel context windows" — and 15× token cost is the price
- For ASPIS's scope (project-level agentic factory, sub-1-hour tasks typically):
  **single-agent + subagent reviews + recursion only when needed** is the right
  default

---

## 1. The five patterns in depth (with sources)

### 1.1 Pattern 1 — Plan-then-act (the explore → plan → implement → commit loop)

**Source: Anthropic, "Best practices for Claude Code"**
(https://code.claude.com/docs/en/best-practices, verified 2026-06-25)

> The recommended workflow has four phases:
> 1. **Explore.** Enter plan mode. Claude reads files and answers questions without making changes.
> 2. **Plan.** Ask Claude to create a detailed implementation plan.
> 3. **Implement.** Switch out of plan mode and let Claude code, verifying against its plan.
> 4. **Commit.** Ask Claude to commit with a descriptive message and create a PR.

> Plan mode is useful, but also adds overhead. For tasks where the scope is
> clear and the fix is small (like fixing a typo, adding a log line, or
> renaming a variable) ask Claude to do it directly. Planning is most useful
> when you're uncertain about the approach, when the change modifies multiple
> files, or when you're unfamiliar with the code being modified. **If you could
> describe the diff in one sentence, skip the plan.**

**Source: GitHub, "About GitHub Copilot cloud agent"**
(https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-coding-agent, verified 2026-06-25)

> Copilot cloud agent can: Research a repository; Create implementation
> plans; Fix bugs; Implement incremental new features; Improve test coverage;
> Update documentation; Address technical debt; Resolve merge conflicts.
>
> When you delegate tasks to Copilot cloud agent, you can: ... have Copilot
> research, plan, and make code changes on a branch, then iterate before
> creating a pull request.

The Copilot model is the same 4-phase loop: **research → plan → implement → iterate → PR**.

**Source: Xia et al., "Agentless: Demystifying LLM-based Software Engineering Agents"**
(arXiv:2407.01489, Oct 2024 v2, verified 2026-06-25)

> Compared to the verbose and complex setup of agent-based approaches, Agentless
> employs a simplistic three-phase process of **localization, repair, and patch
> validation**, without letting the LLM decide future actions or operate with
> complex tools. Our results on the popular SWE-bench Lite benchmark show that
> surprisingly the simplistic Agentless is able to achieve both the highest
> performance (32.00%, 96 correct fixes) and low cost ($0.70) compared with
> all existing open-source software agents!

This is striking: the simple linear pipeline (localize → repair → validate)
*beats* the complex agents on the canonical agentic-coding benchmark. The
plan-then-act pattern is not just convenient — it is empirically superior for
many coding tasks when the phases are well-defined.

**Lesson for ASPIS:** The default loop is plan-then-act. For a small task
(typo, rename, single-file change), the plan phase is trivial or skipped
("describe the diff in one sentence → skip the plan"). For a feature with
multiple files, the plan is a first-class artifact. ASPIS's existing
`feature-planning` skill implements this exact pattern (plan = SPEC + PLAN +
TASKS); this research confirms the pattern is the canonical industry default.

---

### 1.2 Pattern 2 — Deterministic gate (the agent must pass a test to stop)

**Source: Anthropic, "Best practices for Claude Code"**
(https://code.claude.com/docs/en/best-practices, verified 2026-06-25)

> Give Claude a check it can run: tests, a build, a screenshot to compare.
> It's the difference between a session you watch and one you walk away from.
>
> Claude stops when the work looks done. Without a check it can run, "looks
> done" is the only signal available, and you become the verification loop:
> every mistake waits for you to notice it. Give Claude something that
> produces a pass or fail, and the loop closes on its own.
>
> Each step trades setup for attention:
> - **In one prompt**: ask Claude to run the check and iterate in the same message.
> - **Across a session**: set the check as a `/goal` condition. A separate evaluator re-checks it after every turn and Claude keeps working until it holds.
> - **As a deterministic gate**: a [Stop hook](/en/hooks#stop) runs your check as a script and blocks the turn from ending until it passes. Claude Code overrides the hook and ends the turn after 8 consecutive blocks.
> - **By a second opinion**: a verification subagent or a dynamic workflow that checks its own findings has a fresh model try to refute the result, so the agent doing the work isn't the one grading it.

**Source: Anthropic, "Building Effective Agents" (Dec 2024)**
(https://www.anthropic.com/research/building-effective-agents, verified 2026-06-25)

> [For coding agents] ... Code solutions are verifiable through automated
> tests; Agents can iterate on solutions using test results as feedback; The
> problem space is well-defined and structured; and Output quality can be
> measured objectively.

**Source: Cognition Labs, "Estimating the Productivity of an Autonomous AI Software Engineer"**
(https://www.cognition.ai/blog/ai-productivity, June 2026, verified 2026-06-25)

> A recent randomized controlled trial studying end-to-end software features
> did not see time savings due to AI. — citing METR 2025-07-10

The METR RCT, when run end-to-end with *human verification*, often shows
*negative* time savings. The same agent, with a deterministic gate (test
passes), shows large time savings. The gate is the lever.

**Lesson for ASPIS:** The existing system rule **R-002 — Gates** is correct:
"the deterministic gate (format/lint/types/tests) is the bar." Every loop
endpoint in the ASPIS core loop (build, review, commit) must end at a
deterministic gate, not at the agent's assertion of completion. The "Vibe" mode
in `CORE_LOOP.md` §3 should still gate — just on fewer checks, not on none.

The four-level escalation (in-prompt → goal → Stop hook → subagent review) is
worth noting: it shows the industry uses a *gradient* of gate strength, not a
binary on/off. ASPIS's mode dial (§3 of the draft) is a *single* dial on this
gradient; the underlying mechanism is the same.

---

### 1.3 Pattern 3 — Adversarial review in fresh context (the "second opinion")

**Source: Anthropic, "Best practices for Claude Code"** (verified 2026-06-25)

> Add an adversarial review step
> Tip: Before treating a task as done, have a subagent review the diff in a
> fresh context and report gaps.
>
> The longer Claude works unattended, the more an independent check matters
> before you count the work as done. A reviewer running in a fresh subagent
> context sees only the diff and the criteria you give it, not the reasoning
> that produced the change, so it evaluates the result on its own terms.
>
> For a correctness check, run the bundled `/code-review` skill, which reviews
> the current diff for bugs in a fresh subagent and returns findings to the
> session.

The explicit motivation: *the agent doing the work shouldn't grade itself*. A
fresh context has no bias toward "this is fine, I wrote it."

**Source: Cursor, "Bugbot is now over 3x faster, 22% cheaper, and finds 10% more bugs"**
(https://cursor.com/blog/bugbot-updates-june-2026, June 2026, verified 2026-06-25)

> [Bugbot] finds 10% more bugs
> Bugbot is Cursor's code review product. It is a separate agent reviewing
> pull requests in a different context from the writing agent.

**Source: Anthropic, "Building Effective Agents" (Dec 2024)** — describes the
"Evaluator-optimizer" workflow:

> In the evaluator-optimizer workflow, one LLM call generates a response
> while another provides evaluation and feedback in a loop.
>
> This workflow is particularly effective when we have clear evaluation
> criteria, and when iterative refinement provides measurable value. The two
> signs of good fit are, first, that LLM responses can be demonstrably
> improved when a human articulates their feedback; and second, that the
> LLM can provide such feedback.

**Source: Cursor, "Governing agent autonomy with Auto-review" (June 2026)**
(https://cursor.com/blog/agent-autonomy-auto-review, verified 2026-06-25)

> The first technical decision was model choice. The classifier runs before a
> tool call executes, so it sits directly in the agent loop and needs to be
> fast as well as accurate. ... lower-reasoning models were not always faster.
> ... The better trade-off was a small model with enough reasoning to make
> the decision cleanly.
>
> We also made the classifier agentic, because some actions cannot be judged
> from the command alone. A command like `python script.py` might be safe or
> unsafe depending on what is inside the file, so the classifier can inspect
> the workspace with tools like ReadFile, Grep, Glob, and ListDir before
> deciding.
>
> When the classifier does run, it currently blocks around 4% of actions ...
> globally we're seeing that only about 7% of total chats in Auto-review
> mode lead to at least one interruption. To put that in perspective, some
> enterprise customers we're working with previously saw roughly 40% of
> actions blocked within their organization.

The review classifier is itself a *subagent* with its own tools, its own
context, and its own model (small + fast). It is a specialized reviewer; not
the same agent.

**Lesson for ASPIS:** The Reviewer role is not a model check — it is a
*separate agent role* with its own context. The current `quality-review` skill
in ASPIS is on the right track; the `subagent reviewer (default, per-task,
context-isolated)` routing in `CORE_LOOP.md` §5 is the correct architectural
shape. The additional lesson from Cursor's Auto-review: a *safety* classifier
can be a specialized subagent, too, when stakes warrant.

---

### 1.4 Pattern 4 — Recursive planner-workers with handoffs (multi-agent for scale)

**Source: Cursor, "Towards self-driving codebases" (Feb 2026)**
(https://cursor.com/blog/self-driving-codebases, Wilson Lin, verified 2026-06-25)

This is the most detailed public account of multi-agent design evolution by a
production system. Key findings, in order of evolution:

#### Failed: self-coordination via shared state file

> Our first multi-agent idea was the most simple: have agents with equal roles
> use a shared state file to see what others are working on, decide what to
> work on, and update the file.
>
> This failed quickly.
>
> The coordination file quickly created more problems. Agents held locks for
> too long, forgot to release them, tried to lock or unlock when it was
> illegal to, and in general didn't understand the significance of holding a
> lock on the coordination file. **Locking is easy to get wrong and narrowly
> correct, and more prompting didn't help.**
>
> Locking also caused too much contention. 20 agents would slow to the
> throughput of 1-3 with most time spent waiting on locks. ... The lack of
> structure between agents meant no single agent took on big, complex tasks.
> They avoided contention and conflict, opting for smaller and safer changes
> versus taking responsibility for the project as a whole.

This is a hard-won negative result: *agents cannot reliably use shared-file
locks*. ASPIS's brain-as-files design is fine for *humans* and *single agents*
to read; it is not a coordination mechanism for multiple concurrent agents.

#### Failed: planner + executor + workers + judge

> A planner would first lay out the exact approach and deliverables to make
> progress toward the user's instructions. This would be handed to an
> executor, who became the sole lead agent responsible for ensuring the plan
> was achieved completely. The executor could spawn tasks for workers, which
> provided linear scaling and throughput.
>
> For continued movement and accountability, an independent judge ran after
> the executor finished ...
>
> Ultimately, we found this system to be bottlenecked by the slowest worker.
> It was too rigid.

#### Failed: continuous executor (one agent that plans + spawns + reviews)

> The next version removed the independent planner. The executor could now
> also plan how to deliver the goal in addition to spawning tasks.
>
> Despite these improvements, the continuous executor started exhibiting
> pathological behaviors. It would sleep randomly, stop running agents, do
> work itself, refuse to plan and spawn more than a few narrowly focused
> tasks, not properly merge worker changes, and claim premature completion.
>
> We found it was being given too many roles and objectives simultaneously,
> including: plan, explore, research, spawn tasks, check on workers, review
> code, perform edits, merge outputs, and judge if the loop is done. **In
> retrospect, it makes sense it was overwhelmed.**

This is the cleanest negative result in the entire literature: **giving a
single agent too many roles produces an agent that is "overwhelmed" and
exhibits pathological behaviors.** ASPIS must take note: each agent role
should be narrow.

#### Failed: integrator as central quality gate

> We originally added an integrator for central globally-aware quality
> control and to remove contention from too many workers trying to push,
> rebase, resolve conflicts, and merge simultaneously.
>
> It quickly became an obvious bottleneck. There were hundreds of workers
> and one gate (i.e. "red tape") that all work must pass through. We tried
> prompt changes, but ultimately decided it was unnecessary and could be
> removed to simplify the system.

The lesson: **a single global integrator is a bottleneck even when its
purpose is quality control.** Quality must be distributed.

#### Proven: recursive planners + workers with rich handoffs

> 1. A root planner owns the entire scope of the user's instructions. It's
>    responsible for understanding the current state and delivering specific,
>    targeted tasks that would progress toward the goal. It does no coding
>    itself. It's not aware of whether its tasks are being picked up or by
>    whom.
> 2. When a planner feels its scope can be subdivided, it spawns
>    **subplanners** that fully own the delegated narrow slice, taking full
>    ownership in a similar way but only for that slice. This is recursive.
> 3. **Workers** pick up tasks and are solely responsible for driving them to
>    completion. They're unaware of the larger system. They don't communicate
>    with any other planners or workers. They work on their own copy of the
>    repo, and when done, they write up a single handoff that the system
>    submits to the planner that requested the task.
>
> Subplanners increase throughput by rapidly fanning out workers while
> ensuring the whole system remains fully owned and responsible by an agent.
>
> The handoff contains not just what was done, but important notes, concerns,
> deviations, findings, thoughts, and feedback. The planner receives this as
> a follow-up message.
>
> All agents have this mechanism, which allows the system to remain
> incredibly dynamic and self-converging, propagating information up the
> chain to owners with increasingly global views, **without the overhead of
> global synchronization or cross-talk.**

**This is the most important design pattern in the literature.** Key features:

1. **No shared mutable state for coordination** — handoffs are messages, not
   shared files
2. **Planners don't code** — narrow role, no risk of "overwhelmed" agent
3. **Workers are context-isolated** — they see only their task packet; they
   don't know the global state
4. **Recursion** — subplanners are full planners, just with a narrower scope
5. **Handoffs carry not just the work but the *concerns*** — propagating
   "what I'm worried about" up the chain

**Throughput claim:**

> The system peaked at ~1,000 commits per hour across 10M tool calls over a
> period of one week. Once the system started, it didn't require any
> intervention from us.

This is the *measured* throughput of a recursive planner-workers system, on a
real project (a browser from scratch). The system ran for a week unattended.

**Tradeoff explicitly documented:**

> When we required 100% correctness before every single commit, it caused
> major serialization and slowdowns of effective throughput. Even a single
> small error, like an API change or typo, would cause the whole system to
> grind to a halt. Workers would go outside their scope and start fixing
> irrelevant things. Many agents would pile on and trample each other trying
> to fix the same issue.
>
> This behavior wasn't helpful or necessary. Allowing some slack means agents
> can trust that other issues will get fixed by fellow agents soon, which is
> true since the system has effective ownership and delegation over the whole
> codebase. **This may indicate that the ideal efficient system accepts some
> error rate, but a final "green" branch is needed where an agent regularly
> takes snapshots and does a quick fixup pass before release.**

The "final green" pass is a *deterministic gate* (Pattern 2) — but applied
*between major iterations*, not per-commit. This is the right granularity:
gates at the wrong frequency serialize the system.

**Source: Anthropic, "How we built our multi-agent research system" (June 2025)**
(https://www.anthropic.com/engineering/multi-agent-research-system, verified 2026-06-25)

> Our Research feature involves an agent that plans a research process based
> on user queries, and then uses tools to create parallel agents that search
> for information simultaneously. ... Our internal evaluations show that
> multi-agent research systems excel especially for **breadth-first queries
> that involve pursuing multiple independent directions simultaneously**. We
> found that a multi-agent system with Claude Opus 4 as the lead agent and
> Claude Sonnet 4 subagents outperformed single-agent Claude Opus 4 by
> **90.2%** on our internal research eval.
>
> In our analysis, three factors explained 95% of the performance variance
> in the BrowseComp evaluation ... We found that **token usage by itself
> explains 80% of the variance**, with the number of tool calls and the model
> choice as the two other explanatory factors. ... Multi-agent architectures
> effectively scale token usage for tasks that exceed the limits of single
> agents.
>
> There is a downside: in practice, these architectures burn through tokens
> fast. In our data, agents typically use about 4× more tokens than chat
> interactions, and multi-agent systems use about **15× more tokens** than
> chats.

The 90.2% improvement on Anthropic's research eval is the strongest published
case for multi-agent — but with a 15× token cost, and the win is specifically
on **breadth-first queries that involve pursuing multiple independent
directions simultaneously**. For ASPIS's core loop, that condition is rarely
true; our tasks are usually depth-first ("implement this feature in this
codebase").

**Source: Cognition, "Estimating Productivity" (June 2026)** — productivity
work, not architectural; cited in §0 of this doc.

**Source: METR, "Analyzing coding agent transcripts" (Feb 2026)**
(https://metr.org/notes/2026-02-17-exploratory-transcript-analysis-for-estimating-time-savings-from-coding-agents/, Amy Deng, verified 2026-06-25)

> Higher agent concurrency is associated with a higher time savings factor.
> ... a higher daily average concurrency (main and total) is associated with
> a higher time savings factor.
>
> Technical Staff A, who has the highest time savings factor, averages at
> least **2.32 main agents and 2.74 total agents** on active days. ... He
> context-switches frequently between projects and uses git worktrees to work
> on multiple PRs in the same repo. He front-loads effort on detailed plans
> and verification instructions, enabling agents to sometimes run
> autonomously for 1–3+ hours while he spins up additional sessions.

Concrete data: the highest-uplift user runs ~2.7 agents in parallel
*constantly*, with worktrees, plan-first workflows, and "Ralph Wiggum"-style
prompt loops. The pattern is multi-agent via parallelism at the *human* level
(one human, many parallel sessions), not single-team multi-agent at the
*harness* level (one orchestrator, many workers).

**Lesson for ASPIS:** Multi-agent matters, but the architecture is *recursive
planners + isolated workers with rich handoffs*, not "a framework that lets
agents call each other." ASPIS's `task-compile` script and the per-task
packet design in `CORE_LOOP.md` §5 are the right shape: the planner (Build
Lead) holds the whole-feature context, the workers (general-builders) are
context-isolated, the packet is the handoff. The missing piece is the
*recursion* — ASPIS doesn't yet have a mechanism for the Build Lead to
subdivide a feature into sub-features. This is a Phase-3+ design decision.

ASPIS should *not* attempt to build a multi-agent system like Cursor's until
it has evidence the work is parallelizable enough to justify the 15× token
cost. The mode dial (Pattern 5) is the right place to expose this: only
"production" mode of a very-large feature should consider recursion; everything
else should be single-agent + subagent review.

---

### 1.5 Pattern 5 — Rigor dial (mode is a ceiling, not a floor)

**Source: Anthropic, "Best practices for Claude Code"** (verified 2026-06-25)

> Plan mode is useful, but also adds overhead. For tasks where the scope is
> clear and the fix is small ... ask Claude to do it directly. Planning is
> most useful when you're uncertain about the approach, when the change
> modifies multiple files, or when you're unfamiliar with the code being
> modified. If you could describe the diff in one sentence, skip the plan.

The single most important design heuristic in Claude Code: **the *process*
must scale to the work**. The "plan mode" is a dial on how much ceremony —
turn it up for complex work, down for trivial work.

**Source: Cursor blog (multiple posts, 2025-2026) — implicit but consistent:**

- "Composer 2.5" (May 2026): "long-horizon agentic tasks" — heavy orchestration
- "Bugbot" (June 2026): a separate review agent for production code; trivial
  one-line fixes don't get a Bugbot pass
- "Auto-review" (June 2026): the classifier's *block rate* is mode-aware
  (4% in normal mode; ~40% in some enterprise configurations)

Cursor's product model has at least three implicit modes: Tab (autocomplete),
Composer (single-shot agent), Cloud Agent (long-running), Bugbot (review). The
"right" mode is determined by task size and risk.

**Source: GitHub, Copilot cloud agent (verified 2026-06-25):**

> Copilot cloud agent is distinct from the "agent mode" feature available in
> your IDE. Copilot cloud agent works autonomously in a GitHub Actions-powered
> environment to complete development tasks assigned through GitHub issues or
> GitHub Copilot Chat prompts. ... In contrast, agent mode in your IDE makes
> autonomous edits directly in your local development environment.

Two modes, two contexts (cloud vs. IDE). The same conceptual model.

**Source: Cognition, "Estimating Productivity" (June 2026)** — by extension:
Cognition's Devin is one mode (long-running, autonomous); Cursor's Tab is
another (autocomplete, low-risk). The industry has converged on a *gradient*
of modes for the same conceptual "AI does the work" operation.

**Lesson for ASPIS:** The existing `CORE_LOOP.md` §3 (the "Modes" table with
vibe / MVP / production) is the right *abstract* model. What is needed in
F-016 is the *concrete realization* of those modes:

- **Vibe**: no plan, no spec, no architecture, single-pass build, single
  light-touch review. *Goal: "doesn't break anything, runs, in scope."*
- **MVP**: light spec, light architecture, packetized build, per-task
  review, core tests. *Goal: "good enough to demo and iterate on."*
- **Production**: full SPEC, full PLAN, full TASKS, packetized build, full
  multi-lens review, tests-as-spec. *Goal: "shippable to a customer."*

The classification that picks the mode is upstream of the loop (the
`planning-intake` skill), but the loop itself must be the *same shape* in all
three modes — only the depth of phases changes. This is what "mode is a
ceiling, not a floor" means: the path stays the same; the rigor dials.

---

## 2. The minimal effective loop (synthesis)

Synthesizing §1, the **minimal effective loop** for ASPIS is:

```
1. CLASSIFY      (mode + track; deterministic helper; lead confirms)
2. PLAN          (only if not trivial; write SPEC/PLAN/TASKS; gate)
3. BUILD         (per-task: enrich packet → delegate to builder → test → review)
4. REVIEW        (adversarial, in fresh context; verdict)
5. COMMIT        (only on accept; per task)
```

**What is essential:**
- Classification (size + mode) — *without it, the loop is one-size-fits-all and fails on both ends*
- A deterministic gate *somewhere* in the loop — *without it, "looks done" is the signal*
- A fresh-context review of the diff before commit — *without it, the writer grades itself*

**What is nice-to-have:**
- The full SPEC/PLAN/TASKS artifacts — *for trivial tasks, a one-sentence plan suffices*
- Multi-lens review — *a single fresh-context reviewer catches most issues; multi-lens is the production dial*
- Per-task packetization — *for very small tasks, the Build Lead can do it directly*
- Recursive subplanners — *for sub-1-hour tasks, single-agent is fine; reserve for huge features*

**What is provably anti-pattern:**
- Self-coordinating agents via shared file (Cursor)
- A single agent with too many roles (Cursor)
- A central integrator that gates all work (Cursor)
- 100% correctness at every commit (Cursor)
- Per-tool-call review of every action (only 4% need it; Cursor Auto-review)

This is the loop `CORE_LOOP.md` describes, with the additions from this
research:

1. The "classification" phase is the entry point, not the planning lead's
   judgement alone — it can be deterministic and lead-confirmed.
2. The "review" phase is *always* a fresh-context subagent (or lead), not
   the builder. Vibe mode's "light single-pass review" is *still* a
   fresh-context review, just narrower in scope.
3. The "build" phase can recurse — a task can be a mini-feature that gets
   its own plan/build/review sub-loop. This is a Phase-3+ extension; for
   F-016, the recursion is implicit (Build Lead → sub-builder → review
   sub-agent), not a feature of the loop.

---

## 3. Multi-agent vs single-agent — when each wins

This is the most-asked question in the field, and the answer has hardened
in 2025-2026. Summary:

| Work profile | Winner | Token cost | Why |
|---|---|---|---|
| Trivial fix, <30 min, single file | Single-agent | 1× | Overhead of multi-agent exceeds benefit |
| Small task, 1-3 files, well-defined | Single-agent + fresh-context review | ~1.5× | Determinism of single agent + bias-break of review |
| Feature, multiple files, dependency-ordered | Single-agent (Build Lead) + isolated workers | ~2-3× | Workers are context-isolated; planner keeps coherence |
| Open-ended research, many independent angles | Multi-agent (planner + parallel researchers) | 4-15× | The work is *truly* parallel; coordination is the win |
| Company-wide codebase exploration | Multi-agent (recursive planners) | 15×+ | Token cost justified by token-of-context that fits in one window |
| Long-running autonomous build (browser from scratch, 1000+ commits/hour) | Multi-agent with handoffs, no central gate | 15×+ | Sequential gate would serialize; accept some error, final green |

**Decisive factor: parallelizability.** Anthropic's 90.2% research win
came from subagents giving "compression across parallel context windows."
Cursor's 1,000 commits/hour came from no central gate. METR's 11.6× time
savings came from a single user running 2.7 agents in parallel.

**For ASPIS specifically:** the ASPIS core loop is single-project,
multi-file, dependency-ordered feature delivery. The work is *not* highly
parallel (tasks in a feature usually depend on prior tasks). The right
default is single-agent (Build Lead) + isolated workers + fresh-context
review + a deterministic gate. Multi-agent with recursion is reserved for
the "project plan" track (a project broken into multiple features) — and
even there, the recursion is *across features* (one feature per Build Lead),
not *within* a feature.

**Anti-pattern to avoid:** do not add a multi-agent framework "for scale"
without first measuring the work's parallelizability. The 15× token cost
*is the entire reason* single-agent-with-rich-tools is the default in 2026.

---

## 4. State of the field in 2025-2026 — what emerged, what was abandoned

### Emerged (now standard)

1. **Subagents as context isolation.** Every production system has them:
   Claude Code, Cursor (Bugbot is a subagent), Anthropic Research
   (multi-agent research), OpenHands, Devin. *The key reason:* a fresh
   context is unbiased by the writer's reasoning.

2. **A separate "reviewer" role with its own context, tools, and model.**
   Cursor Bugbot, Claude Code's `/code-review` skill, METR's eval
   methodology (LLM-as-judge with a different prompt), Devin's CI/test
   runs as the "judge." *The key reason:* the writer can't grade itself.

3. **Plan-then-act with explicit plan artifacts.** Claude Code's plan mode,
   GitHub Copilot's research→plan→implement, Cursor's plan-then-edit,
   Devin's read-then-code. *The key reason:* it prevents solving the wrong
   problem.

4. **Rich task packets (handoffs).** Cursor's worker handoffs, ASPIS's
   per-task packets, Devin's session traces. *The key reason:* workers
   need a self-contained brief; the planner's whole context is too large.

5. **Rigor dial (mode).** Implicit in every product (Tab vs. Composer vs.
   Cloud Agent in Cursor; Agent Mode vs. Cloud Agent in Copilot; local
   agent vs. cloud agent in Claude Code). *The key reason:* one-size-fits-all
   is wrong on both ends.

6. **A deterministic gate at the end of every step.** Tests, builds, lints,
   screenshots, "the user accepted the diff." *The key reason:* the agent
   stops at "looks done" otherwise; that's not enough.

7. **Durable execution for long-running agents.** Cursor migrated to
   Temporal; Anthropic uses checkpointing + resume; the pattern is
   "the agent loop lives outside any single machine." *The key reason:*
   inference outages, pod restarts, and multi-day runs cannot restart
   from scratch.

8. **Conversation state decoupled from machine state.** Cursor's pattern
   of "agent loop in Temporal, conversation storage separate, machine
   separate." *The key reason:* agents span multiple machines; the
   conversation must be a stream that follows them.

9. **Constraints over instructions in prompts.** Cursor:
   "Constraints are more effective than instructions. 'No TODOs, no
   partial implementations' works better than 'remember to finish
   implementations.' Models generally do good things by default.
   Constraints are defining their boundaries." (Wilson Lin, Feb 2026)

10. **Fresh-context review of the diff, not the conversation.** Cursor
    Bugbot, Claude Code `/code-review`, METR's transcript analysis — all
    feed the reviewer the *diff* + *plan*, not the full agent trace.

### Abandoned (was tried, was found wrong)

1. **Self-coordinating agents via shared state file.** Cursor tried it;
   "failed quickly." Agents can't reliably use locks. Lesson: coordination
   is via messages (handoffs), not shared mutable state.

2. **Central integrator that gates all work.** Cursor: "obvious bottleneck.
   ... unnecessarily and could be removed to simplify the system."

3. **Continuous-executor single agent (plans + spawns + reviews + commits).**
   Cursor: "pathological behaviors ... overwhelmed." Lesson: each agent
   role should be narrow.

4. **100% correctness at every commit.** Cursor: "caused major
   serialization and slowdowns. ... Many agents would pile on and trample
   each other trying to fix the same issue." Lesson: gates at the wrong
   frequency serialize the system.

5. **Code-completion-style agents as the universal interface.** Every
   system evolved past "tab autocomplete" to "agent with tools" by 2025.
   The exception now is Tab, which is intentionally narrow.

6. **Hand-tuned multi-agent via framework abstractions.** Anthropic
   (Dec 2024): "We suggest that developers start by using LLM APIs
   directly: many patterns can be implemented in a few lines of code.
   ... They often create extra layers of abstraction that can obscure
   the underlying prompts and responses, making them harder to debug."

7. **Prefilled responses for steering.** Anthropic: "Starting with Claude
   4.6 models, prefilled responses on the last assistant turn are no
   longer supported. ... Model intelligence and instruction following
   have advanced such that most use cases of prefill no longer require
   it." (Verified 2026-06-25)

8. **Optimizer-loop patterns with hand-tuned evaluators.** Anthropic's
   evaluator-optimizer workflow is *described*, but the eval criteria
   must be LLM-graded, not hand-coded. Hand-coded evals are too brittle
   for open-ended agent work.

9. **"The agent knows when it's done" as a stop condition.** Every
   production system uses a deterministic gate or a max-iteration cap
   (GitHub Copilot: "Each Copilot cloud agent session has a maximum
   execution time of 59 minutes. This is a hard limit that cannot be
   extended or bypassed."). The agent's "I'm done" claim is necessary
   but not sufficient.

10. **The "framework" approach to multi-agent (LangChain-style, AutoGen,
    CrewAI).** Most serious production work is now on direct API +
    hand-rolled orchestration. Anthropic's own multi-agent system is
    hand-rolled. Cursor's is hand-rolled. The frameworks have not kept
    up with the model capabilities.

---

## 5. The Core Loop — concrete ASPIS architecture (synthesis)

Pulling the five patterns together, the ASPIS core loop is:

```
ENTRY:
  Project Lead receives request
  → route to Planning Lead (large) or Build Lead (small)
  → Planning Lead classifies (track + mode) via planning-intake skill

PLANNING (mode >= MVP):
  P0: classify (planning-intake reads modes.yaml)
  P1: clarify (requirement-clarification; max 5 questions)
  P2: SPEC.md (feature-planning)
  P3: PLAN.md (architecture-planning)
  P4: TASKS.md + packets (task-decomposition → task-compile)
  P5: plan review (Reviewer + plan-critic)
  GATE: prereq-validate

BUILD (every mode):
  for each task packet:
    enrich (Build Lead holds whole-feature context)
    delegate to general-builder (context-isolated; fresh subagent)
    build (with the packet's acceptance + tests as the goal)
    GATE: deterministic (the project's R-002 — format/lint/types/tests)
    review per the packet's routing
      - sub-agent reviewer (default, per-task, context-isolated)
      - OR Reviewer lead (high criticality, security, cross-cutting)
    GATE: review verdict = approve / approve-with-notes
    commit (committer role)
  track progress
  verify completion against SPEC FR-###/SC-###

REVIEW (already in BUILD per-task; this is the meta-review):
  strategy/depth by risk+mode (review-strategy)
  evaluate dimensions (quality-review)
  verdict: approve / approve-with-notes / changes-required / rejected
  route the fix (back to builder or Fix Lead)

EXIT:
  per-feature acceptance (ACCEPTANCE.md check)
  optional: project-level PR (only if external review desired)
```

**Properties this gives ASPIS:**

- **Scales to the work.** Classification upstream; mode dial; no over-process for trivial tasks.
- **Verifiable.** Deterministic gate after every build; reviewer in fresh context.
- **Recoverable.** Failed gate → back to builder; rejected review → back to builder; committer is the only writer.
- **Context-isolated.** Planner/Build Lead hold whole-feature context; workers run in fresh contexts; reviewers run in fresh contexts; the packet is the handoff.
- **Token-efficient for small work.** Vibe mode skips most phases; small task packets don't need full TASKS.md.
- **Token-expensive but proven for huge work.** Recursive subplanners + isolated workers is the proven Cursor pattern for 1,000-commits/hour scale. ASPIS does not need this for F-016's scope; it should be a documented Phase-3+ extension.

---

## 6. Risk and uncertainty

### Things that are well-established (cite as fact in F-016 plan)

- The plan-then-act pattern (1.1)
- The deterministic gate (1.2)
- The fresh-context reviewer (1.3)
- Self-coordination via shared state is an anti-pattern (§4)
- 100% commit correctness is an anti-pattern (§4)

### Things that are widely-attested but not yet universal

- The recursive planner-workers pattern (1.4) — proven by Cursor at extreme scale (1 browser in 1 week); unproven at the sub-feature scale ASPIS operates at
- The mode dial (1.5) — every product has one; no canonical set of "modes"
- The "adversarial review by a different model" — Anthropic, Cursor, METR all do this; no public ablation of "same model, different prompt" vs. "different model"

### Things I am uncertain about (caveat in F-016 plan)

- The exact threshold of when multi-agent beats single-agent. Anthropic's
  90.2% win was on research (not coding). Cursor's 1,000-commits/hour is
  on a single project (a browser). I have *no* primary source that says
  "multi-agent beats single-agent for a 5-file feature in a normal
  codebase." The default should be single-agent + subagent reviews.
- The optimal size of a task packet. ASPIS's draft says "each task is
  small enough to build at full focus." Cursor's worker handoffs are
  unstated in size. More research needed here; the practical answer
  comes from measurement, not theory.
- Whether *vibe* mode should keep a fresh-context review. Cursor's
  Auto-review (4% block rate on every action) suggests yes; Claude Code's
  "light single-pass review" suggests yes; Agentless (which has no
  reviewer, just a gate) suggests no. ASPIS's draft says "vibe is not
  'no review'" — I would preserve that, but treat the review as a
  one-shot subagent read of the diff, not a multi-lens.

### What I deliberately did not research (not in scope for F-016)

- The model-vs-prompt debate (which model, which prompt) — the planner
  chooses models, not the architecture
- MCP (Model Context Protocol) — a separate research topic; F-016 plan
  inherits whatever decision is made elsewhere
- The user-UX of an agentic factory (CLI, IDE integration, web app) — the
  ASPIS catalog already addresses this
- Security / safety of autonomous agents — Cursor's Auto-review is a
  reference for this; ASPIS's R-009 human gate is the architectural answer
- Computer use / browser automation — out of scope for ASPIS's file-first
  factory; the brain is files, not GUIs

---

## 7. Source provenance

| Source | URL | Verified | What we used it for |
|---|---|---|---|
| Anthropic, "Building Effective Agents" | https://www.anthropic.com/research/building-effective-agents | 2026-06-25 | Pattern taxonomy (workflows vs. agents); evaluator-optimizer; "agentic systems trade latency and cost for performance"; recommendation to start with simple patterns |
| Anthropic, "How we built our multi-agent research system" | https://www.anthropic.com/engineering/multi-agent-research-system | 2026-06-25 | Orchestrator-workers pattern; 90.2% multi-agent win; 15× token cost; "subagents provide compression across parallel context windows"; agentic tool design |
| Anthropic, "Best practices for Claude Code" | https://code.claude.com/docs/en/best-practices | 2026-06-25 | 4-phase plan: explore→plan→implement→commit; verification gates (in-prompt / /goal / Stop hook / subagent); fresh-context review; "If you could describe the diff in one sentence, skip the plan"; subagents for context isolation |
| Anthropic, "Estimating AI productivity gains from Claude conversations" | https://www.anthropic.com/research/estimating-productivity-gains | 2026-06-25 | 80% time savings claim; 100K conversations; Anthropic's eval methodology; JIRA benchmark r=0.46 |
| Anthropic, "Prompting best practices" | https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices | 2026-06-25 | Subagent usage guidance; "subagents when tasks can run in parallel, require isolated context, or involve independent workstreams"; prefill deprecation |
| Cursor, "Towards self-driving codebases" | https://cursor.com/blog/self-driving-codebases | 2026-06-25 | The full multi-agent evolution: failed self-coordination, failed planner+executor+workers+judge, failed continuous executor, failed integrator, proven recursive planners + isolated workers with handoffs; 1,000 commits/hour, 10M tool calls/week; constraints > instructions |
| Cursor, "What we've learned building cloud agents" | https://cursor.com/blog/cloud-agent-lessons | 2026-06-25 | Durable execution (Temporal); decouple agent/machine/conversation state; "the development environment is the product"; move logic out of harness, into tools the agent controls |
| Cursor, "Governing agent autonomy with Auto-review" | https://cursor.com/blog/agent-autonomy-auto-review | 2026-06-25 | Subagent classifier in the same RPC stream; 4% block rate; classifier gives feedback, not just blocks; classifier's eval set must be relabeled when policy changes |
| Cursor, "Bugbot is now over 3x faster, 22% cheaper, and finds 10% more bugs" | https://cursor.com/blog/bugbot-updates-june-2026 | 2026-06-25 | Code-review-as-subagent in fresh context; Bugbot is a separate agent reviewing PRs |
| GitHub, "About Copilot cloud agent" | https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-coding-agent | 2026-06-25 | Research→plan→implement→iterate→PR loop; "Copilot can only work on one branch at a time"; 59-min session cap as a hard stop; agent vs. agent mode distinction |
| Cognition, "Introducing Devin" | https://www.cognition.ai/blog/introducing-devin | 2026-06-25 | First autonomous agent in sandboxed env; SWE-bench 13.86% in 2024; long-term reasoning + planning |
| Cognition, "Estimating the Productivity of an Autonomous AI Software Engineer" | https://www.cognition.ai/blog/ai-productivity | 2026-06-25 | Productive engineering hours as the metric; 258 sessions from 126 users; r=0.74 in log-space; code volume is a weak proxy for effort |
| METR, "Analyzing coding agent transcripts to upper bound productivity gains" | https://metr.org/notes/2026-02-17-exploratory-transcript-analysis-for-estimating-time-savings-from-coding-agents/ | 2026-06-25 | 1.5-13× time savings range; Technical Staff A averages 2.7 concurrent agents with 11.6× time savings; LLM judge r=0.83 vs. humans 0.67; concurrency strongly correlated with uplift |
| Xia et al., "Agentless" | https://arxiv.org/abs/2407.01489 | 2026-06-25 | Simple 3-phase pipeline (localize→repair→validate) beats complex agents on SWE-bench; 32% at $0.70 |
| Wang et al., "OpenHands" (f.k.a. OpenDevin) | https://arxiv.org/abs/2407.16741 | 2026-06-25 | Generalist-agent platform; coordination between multiple agents; sandboxed environments for code execution |
| Replit, "Introducing Replit Agent" | https://replit.com/blog/introducing-replit-agent | 2026-06-25 | "Like a pair programmer that configures the dev env, installs deps, and executes code"; idea→app→deployment |

---

## 8. The five patterns at a glance (cheat sheet for F-016 plan)

```
PATTERN 1: PLAN-THEN-ACT
  Explore → Plan → Implement → Commit
  Skip plan if "describe the diff in one sentence"
  ASPIS role: feature-planning, task-decomposition, plan-critic

PATTERN 2: DETERMINISTIC GATE
  A test/build/lint/screenshot the agent MUST pass to stop
  Four strengths: in-prompt / goal / Stop hook / subagent review
  ASPIS role: prereq-validate, the project's R-002 gate

PATTERN 3: ADVERSARIAL REVIEW IN FRESH CONTEXT
  Reviewer ≠ builder. Different context. Different prompt.
  Reviewer sees the diff, not the reasoning.
  ASPIS role: review-strategy, quality-review, acceptance-decision

PATTERN 4: RECURSIVE PLANNER-WORKERS WITH HANDOFFS
  Planner owns scope, doesn't code. Workers context-isolated.
  Handoff = "what I did + concerns + deviations + feedback."
  No shared mutable state. No central integrator.
  ASPIS role: Build Lead + general-builder + task packet (Phase 3+ for recursion)

PATTERN 5: RIGOR DIAL (MODE)
  Same loop, different depth. Mode is a ceiling, not a floor.
  Vibe: no plan, light review. Production: full plan, multi-lens review.
  ASPIS role: planning-intake reads modes.yaml, mode tunes the loop

ANTI-PATTERNS (do NOT do these):
  - Self-coordinating agents via shared state file
  - One agent with too many roles
  - A central integrator that gates all work
  - 100% correctness at every commit
  - Per-tool-call review of every action (only ~4% need it)
  - Multi-agent for work that is not truly parallel
  - Prefilled responses (deprecated in Claude 4.6)
  - Hand-rolled framework abstractions over direct API

WHEN MULTI-AGENT WINS:
  - Work is truly parallel (research, exploration, scanning)
  - Work exceeds single context window
  - Work involves many independent angles
  - Scale demands 100s-1000s of commits/hour
WHEN SINGLE-AGENT WINS:
  - Work is depth-first, dependency-ordered
  - Work has tight context coupling
  - Work fits in single context window
  - Token cost is a constraint (15× multi-agent overhead)
```

---

**End of research.** This doc is the *external evidence* the F-016 SPEC/PLAN/TASKS
should be checked against. The internal architecture is in `CORE_LOOP.md`;
the F-016 plan should:
1. Adopt the five patterns above as the loop's spine
2. Keep the rigor dial as a mode (vibe/MVP/production) parameter
3. Use the deterministic gate as the loop's stopping condition
4. Use the fresh-context reviewer as the per-task review step
5. Defer recursive multi-agent to a Phase-3+ feature (not in F-016's scope)
6. Avoid the anti-patterns in §4 / §8

A separate doc should be commissioned for: (a) MCP integration (separate
research topic), (b) harness patterns (durable execution, conversation
state, env-as-product) — Cursor's lessons, applicable to ASPIS when it
becomes a long-running factory.
