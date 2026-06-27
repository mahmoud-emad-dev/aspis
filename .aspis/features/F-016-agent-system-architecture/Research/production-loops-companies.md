<!-- ASPIS:REFERENCE START -->
# Production AI-Assisted Software Loops — Real-World Research (June 2026)

A sourced reference of how companies that ship code with AI assistance actually
structure their planning → building → reviewing → testing → shipping loop.
**Built once, consumed by ASPIS roles that need to design, review, or extend
the agent system.**

**Audience:** System Lead (extending the agent catalog), Planning Lead (shaping
the plan→build→review phase design), Build Lead (worker design), Reviewer
(quality gate design), Project Lead (workflow shape).

**Provenance (sources read, current as of 2026-06-25):**

Primary (official docs / engineering blogs / 2026):
- OpenAI — *Harness engineering: leveraging Codex in an agent-first world* (Lopopolo, 2026-02-11) — https://openai.com/index/harness-engineering/
- Anthropic — *Best practices for Claude Code* (2026) — https://code.claude.com/docs/en/best-practices
- GitHub Blog — *Introducing Agent HQ: Any agent, any way you work* (Daigle, Universe 2025-10-28) — https://github.blog/news-insights/company-news/welcome-home-agents/
- GitHub Docs — *About GitHub Copilot code review* (2026) — https://docs.github.com/en/copilot/concepts/agents/code-review
- Cursor — *Towards self-driving codebases* (Wilson Lin, 2026-02-05) — https://cursor.com/blog/self-driving-codebases
- Cursor — *What we've learned building cloud agents* (Josh Ma, 2026-06-02) — https://cursor.com/blog/cloud-agent-lessons
- Cursor — *Governing agent autonomy with Auto-review* (Gomes & McPeak, 2026-06-11) — https://cursor.com/blog/agent-autonomy-auto-review
- Cursor — Blog index (2026) — https://cursor.com/blog (cloud agents, self-driving, auto-review, Notion SDK, Composer 2.5)
- Cognition / Devin — *AI Software Engineer* (2026) — https://devin.ai/
- Cognition — *A review of OpenAI's o1 and how we evaluate coding agents* (2024-09-12) — https://cognition.com/blog/evaluating-coding-agents
- Amazon — *Amazon Q Developer* (2026) — https://aws.amazon.com/q/developer/
- Vercel — *What is v0?* (2026) — https://vercel.com/docs
- Replit — *Agent 4* (2026) — https://replit.com/agent4
- Google DeepMind — *AlphaEvolve: A Gemini-powered coding agent for designing advanced algorithms* (2025-05-14) — https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/
- Google Research / DeepMind — Research index & AI coding areas (2026) — https://research.google/research-areas/software-engineering/
- SWE-bench — Official leaderboards (2026) — https://www.swebench.com/
- Mini-SWE-agent — https://github.com/SWE-agent/mini-swe-agent

Supporting (cross-cutting patterns already analysed in the project):
- ASPIS — *Agent System Design Patterns* (2026-06-25) — `.aspis/research/agent-system-design-patterns.md`

**ASPIS context this applies to:** F-016 (agent system architecture), Phase 3
production loop. Patterns in §1 are the *validated* production loop primitives
that the agent catalog, harness, and review model should adopt. Patterns in §2
are the *current* state by company. §3 answers the eight research questions
directly. §4 lists the SWE-bench results the F-016 SPEC's success criteria
should reference.

**Status:** Findings are validated, with sources. Where a claim is a vendor's
own framing (opinion / marketing), it is marked **[VENDOR]**. Where it is a
peer-reviewed or multi-source observation, it is **[VERIFIED]**. Where the
evidence is one team's internal post and not yet broadly replicated, it is
**[EMERGING]**.

---

## §0. Top 5 proven production loop patterns

A clean answer first. Every pattern below is observed in production at one or
more of the companies researched, with concrete numbers, not vendor marketing.

### Pattern 1 — **Verification is the loop closer; the agent must have a check it can run**

> *"Give Claude a way to verify its work. It's the difference between a session
> you watch and one you walk away from."* — Anthropic, *Best Practices for
> Claude Code* (2026). [VERIFIED, multi-source]

- **What it looks like in production:** The agent loop closes on a *deterministic
  pass/fail* the agent itself runs. The "check" varies by task class: a test
  suite (Anthropic, OpenAI, GitHub), a build exit code (Anthropic, Cursor), a
  lint/type check (all), a browser-screenshot diff against a design
  (Anthropic, OpenAI, Vercel v0, Replit, Cursor), a log/metrics query
  (OpenAI, Cognition), a deployed endpoint that the agent then *drives*
  (OpenAI Chrome DevTools MCP, Cognition evaluator agent, Replit Agent).
- **Evidence it works:**
  - **OpenAI Codex** (Harness engineering, 2026-02-11): the team reports
    "single Codex runs work on a single task for upwards of six hours (often
    while the humans are sleeping)" because the agent closes the loop on
    build + test + UI screenshots. **3.5 PRs per engineer per day, 1,500
    PRs in 5 months, ~1M LOC, 0 manually-written lines.**
  - **Cognition / Devin** (Cognition, 2024-09-12): uses an *evaluator agent*
    with browser/shell/edit tools to grade the deliverable against typed
    criteria. Reaches 74.2% on their internal `cognition-golden` benchmark
    autonomously.
  - **Anthropic Claude Code** (Best Practices, 2026): makes the check
    itself a *Stop hook* — a script that blocks the turn from ending until
    it passes. Quote: "you become the verification loop: every mistake
    waits for you to notice it. Give Claude something that produces a
    pass or fail, and the loop closes on its own."
  - **SWE-bench Verified** (swebench.com, 2026): the public benchmark
    that *rewards* this pattern — every agent run scores pass/fail against
    upstream tests. The leaderboard is dominated by agents that
    instrument a feedback loop on test output, not agents that produce
    long "looks done" prose.
- **ASPIS implication:** the deterministic gate (R-002) is not just a
  quality-control measure; it is the *fuel* the agent needs to keep
  iterating. Without it, every agent is a one-shot. The system should
  distinguish **finding the check** (a planning step that names the
  verification) from **running the check** (a build step). The Reviewer
  verdict is a *finding against a deterministic criterion*; without the
  criterion there is no verdict.

### Pattern 2 — **Repository knowledge is the system of record; `AGENTS.md` is a map, not a manual**

> *"Give Codex a map, not a 1,000-page instruction manual."* — OpenAI,
> *Harness engineering* (2026-02-11). [VERIFIED, multi-source]

- **What it looks like in production:** Durable knowledge lives *in the
  repository* (markdown, schemas, executable plans), not in chat threads,
  Google Docs, or in the agent prompt. The agent's entry-point file
  (`AGENTS.md`, `CLAUDE.md`, `.cursor/`, etc.) is short (~100 lines) and
  *points* to the system of record. A periodic "doc-gardening" agent
  catches drift.
- **Evidence it works:**
  - **OpenAI Codex** (Harness engineering, 2026-02-11): a 100-line
    `AGENTS.md` is the table of contents. The system of record is a
    structured `docs/` tree (`design-docs/`, `exec-plans/`,
    `product-specs/`, `references/`, `QUALITY_SCORE.md`, `SECURITY.md`).
    Custom linters + a doc-gardening agent keep it fresh. They tried the
    "one big AGENTS.md" and report it failed in 4 predictable ways:
    crowds out task context; becomes non-guidance when everything is
    "important"; rots instantly; can't be mechanically verified.
  - **Anthropic Claude Code** (Best Practices, 2026): `CLAUDE.md` lives
    at project root (or subdirectories, loaded on demand). It explicitly
    recommends the same "include only what Claude can't figure out from
    code" + "for domain knowledge that's only relevant sometimes, use
    skills (loaded on demand) instead." Quote: *"Bloated CLAUDE.md
    files cause Claude to ignore your actual instructions."*
  - **Cursor** (Cloud agents, 2026-06-02): the "dev environment is the
    product" pattern is the same idea applied to runtime: the agent
    inherits the *full* dev environment (skills, repos, credentials,
    network) the same way a human would; you don't ship a manual,
    you ship an environment.
  - **GitHub Copilot** (Universe 2025-10-28, Agent HQ): "AGENTS.md
    files, source-controlled documents that let you set clear rules
    and guardrails" are part of the VS Code customisation story.
- **ASPIS implication:** ASPIS already has the `brain/` (`.aspis/`) as
  the system of record and the agents load knowledge progressively
  via `context-ladder`. This pattern is the same idea at the
  product-repo level. The ASPIS *agent* file stays thin; the durable
  knowledge lives in `.aspis/rules/`, `.aspis/context/`,
  `.aspis/research/`, and per-feature folders. A periodic doc-gardening
  agent (the one already proposed in pattern 10 of
  `agent-system-design-patterns.md`) is the cheapest defence against
  drift.

### Pattern 3 — **Recursive planners + context-isolated workers (orchestrator-workers, not one mega-prompt)**

> *"Interestingly, this does represent how some software teams operate
> today."* — Cursor, *Towards self-driving codebases* (2026-02-05).
> [VERIFIED, multi-source]

- **What it looks like in production:** A *root planner* owns the whole
  scope and breaks it into *subplanners* (recursively, when scope grows)
  that each own a narrow slice. *Workers* pick up tasks, are **solely
  responsible for driving them to completion, are unaware of the larger
  system, do not communicate with any other planners or workers, and
  work on their own copy of the repo.** When done, they write a single
  handoff the system submits to the requesting planner. The handoff
  contains "not just what was done, but important notes, concerns,
  deviations, findings, thoughts, and feedback" — so information
  propagates up the chain to owners with increasingly global views,
  *without* global synchronisation or cross-talk.
- **Evidence it works:**
  - **Cursor self-driving browser** (2026-02-05): Wilson Lin's team ran
    **~1,000 commits/hour, 10M tool calls, 0 humans in the loop, for
    one week**, building a web browser. The final design is recursive
    planners + isolated workers, *not* an integrator (removed as a
    bottleneck), *not* a shared coordination file (lock contention
    collapsed 20 agents to 1–3 effective). Errors are *accepted* in
    flight and reconciled by a final "green" pass before release.
  - **OpenAI Codex** (Harness engineering, 2026-02-11): the same shape
    inverted — *humans* are the planners, *Codex* is the worker. An
    engineer describes a task, Codex executes, opens a PR, responds to
    review, and merges. The "planner" is a thin human prompt.
  - **Anthropic Claude Code** (Best Practices, 2026): "Use subagents
    for investigation. Delegate research with 'use subagents to
    investigate X'. They explore in a separate context, keeping your
    main conversation clean." Subagents run in their *own context
    window*, with *their own tools*, and report summaries back. The
    documented *Writer/Reviewer* pattern is two parallel sessions
    (one writes, one reviews in fresh context) — the cheapest
    second-opinion unit.
  - **Cognition / Devin** (Devin product, 2026): "Devin can spin up a
    team of Devins for large tasks. Devin gets better over time by
    reading past session trajectories." The fleet-of-Devins
    architecture for the Nubank migration is a deployment of the same
    shape: many workers, one owner per migration sub-task, handoffs
    between them.
  - **Mini-SWE-agent** (2026, github.com/SWE-agent/mini-swe-agent): the
    *Reference Agent* on the SWE-bench Verified leaderboard is a 100-
    line Python ReAct loop. The leaderboard reward structure forces
    this shape: simple loop, context-isolated per task, deterministic
    test verification on each turn.
- **ASPIS implication:** ASPIS already uses orchestrator-workers (the
  Build Lead hands a TASK_PACKET to a `general-builder` whose whole
  context *is* the packet — see pattern 1 of
  `agent-system-design-patterns.md`). What this pattern adds: a
  **recursive** decomposition (subplanners), a **typed handoff
  packet** that propagates *concerns* not just *results* back up, and
  the explicit recognition that *integrators are a bottleneck* and
  should be removed in favour of *acceptance reconciliation* at the
  boundaries.

### Pattern 4 — **The development environment is the product (especially for cloud agents)**

> *"Over and over again we've traced it back to the same diagnosis: the
> cloud agent not having the environment it needs to execute or verify
> its work."* — Cursor, *What we've learned building cloud agents*
> (2026-06-02). [VERIFIED, multi-source]

- **What it looks like in production:** A cloud agent inherits the
  *full* development environment a human developer would have — repos,
  dependencies, network, secrets, build tools, runtime, browser, IDE,
  observability stack. The platform is responsible for the *full
  environment*, not just the prompt. "Build it and they will work" does
  not work; "give them the environment and they will work" does.
- **Evidence it works:**
  - **Cursor cloud agents** (2026-06-02): reliability went from "one
    9" (work-stealing) to "two 9s" after migrating to **Temporal** for
    durable execution. **50M Temporal actions/day, 7M unique
    workflows/day, 40%+ of their own PRs come from cloud agents.**
    Their insight: as models got smarter, environment setup became
    the *determining factor* in whether they executed at full
    potential. They now build "enterprise IT for agents" — secret
    redaction, network policies, credential management.
  - **OpenAI Codex** (Harness engineering, 2026-02-11): the team made
    the app "bootable per git worktree" so each Codex run has its
    own environment; wired the **Chrome DevTools Protocol** into the
    agent runtime for visual validation; exposed **logs, metrics,
    traces via LogQL / PromQL** as tools the agent queries. The
    environment *is* the verification surface.
  - **Cognition / Devin** (Devin product, 2026): runs each task in a
    real Linux VM with root access; user sets up its own dev
    environment. Replit Agent 4 does the same in the browser.
  - **Replit Agent 4** (replit.com/agent4, 2026): "agents run
    independent tasks simultaneously, with progress always visible"
    — the environment is a multi-task workspace.
  - **Vercel v0** (vercel.com/docs, 2026): "Real-time preview of your
    app, with visual progress indicators and rich UI feedback for
    all agent actions" — preview IS the verification surface.
  - **Anthropic Claude Code** (Best Practices, 2026): "Tell Claude
    Code to use CLI tools like `gh`, `aws`, `gcloud`, and `sentry-cli`
    when interacting with external services. CLI tools are the most
    context-efficient way to interact with external services."
  - **Amazon Q Developer** (aws.amazon.com/q/developer, 2026):
    available in IDE, CLI, AWS Console, GitHub.com, GitLab, Slack,
    Teams — the platform is the agent, not the surface.
- **ASPIS implication:** ASPIS's build environment *is* the
  determinism — `aspis context`, `aspis verify`, the brain, the
  task packets, the unit / build / test commands. The agent doesn't
  need to invent the harness; the harness is the product. The
  corollary: when the ASPIS *runtime* ships (Part 1, 2, 3), the
  runtime itself must be a *full environment* (file system,
  permissions, network, verification surface) — not a thin proxy.
  The current `runtime_guard` + `scope_guard` are the start; the
  work-stealing / durable-execution layer is the gap.

### Pattern 5 — **Risk-tiered autonomy, gated by a small classifier (not a global permission switch)**

> *"Auto-review makes decisions around agent autonomy behave more like
> a dial than a switch."* — Cursor, *Governing agent autonomy with
> Auto-review* (2026-06-11). [VERIFIED, multi-source]

- **What it looks like in production:** A small, fast, *specialised*
  classifier model sits in the agent's execution path and decides
  whether each tool call is low-stakes (let it run) or high-stakes
  (interrupt the user). The classifier inspects the *context* (file
  contents, the user's intent, the action's blast radius) — it is
  *agentic* and may read files, grep, list dirs before deciding. When
  it blocks, it returns an *explanation* to the parent agent, which
  can often narrow the action or choose a different tool *without*
  interrupting the user. Routine work is invisible; risky work is a
  prompt.
- **Evidence it works:**
  - **Cursor Auto-review** (2026-06-11): in production, blocks ~4% of
    actions; only ~7% of total chats lead to at least one user
    interruption. The reference comparison: some enterprise customers
    were previously seeing ~40% of actions blocked under blanket
    permission gating. Cursor explicitly designed against "approval
    fatigue" (the failure mode where the user clicks through 10 prompts
    without reading). 6,122 labelled eval rows + synthetic
    adversarial cases; "flapping" is the primary failure signal
    (allow-six, block-four → underspecified policy).
  - **Anthropic Claude Code** auto mode (Best Practices, 2026):
    identical pattern, identical framing. *"A classifier model reviews
    commands before they run, blocking scope escalation, unknown
    infrastructure, and hostile-content-driven actions while letting
    routine work proceed without prompts."*
  - **Amazon Q Developer** (aws.amazon.com/q/developer, 2026):
    security scanning that "outperforms leading publicly benchmarkable
    tools on detection across most popular programming languages" +
    agentic capabilities "achieved the highest scores on the SWE-
    Bench Leaderboard and Leaderboard Lite" — i.e. the agent itself
    is judged by an *automated classifier* (the SWE-bench tests).
  - **GitHub Copilot code review** (docs.github.com, 2026): the
    review effort level is now a *dial*: "Low" (fast, targeted) vs
    "Medium" (higher-reasoning model, more analysis, more credits).
    "Use Medium for security-sensitive code, multi-service pull
    requests, or repositories with strict quality standards."
    MCP servers can be enabled or disabled per repo. AI controls
    + control plane (Agent HQ, Universe 2025-10-28) are the
    enterprise form of the same idea.
  - **Anthropic / OpenAI / Devin / Cursor all converge on the same
    shape**: a *graded* autonomy, not a binary on/off. The classifier
    is the *only* piece of the loop that needs a real-time, low-
    latency decision; the agent itself is the *slow* part.
- **ASPIS implication:** ASPIS's permission model (R-001 scope, the
  runtime guard, the `test_agent_permissions.py` golden test) is the
  *deterministic* part of the gate. The graded-autonomy pattern
  extends it with a *contextual* classifier: a small model in the
  agent loop that says "this tool call needs the user, this one
  doesn't" — informed by the user's intent, the file's sensitivity,
  and the operation's blast radius. The current deterministic
  allowlist handles *known* risk; the classifier handles *unknown*
  risk. The "approval fatigue" failure mode is real and is what
  pattern 5 is designed to prevent.

---

## §1. Per-company production loops

What the actual planning → building → reviewing → shipping loop looks like
in each company surveyed. Numbers are pulled from the cited source.

### 1.1 OpenAI (Codex / Harness engineering) — "the agent-first product team"

- **Team shape:** 3 engineers driving Codex grew to 7 over 5 months; **0
  manually-written lines** in a ~1M-LOC repo. **1,500 PRs in 5 months =
  3.5 PRs per engineer per day, increasing** as the team grew.
- **Loop:**
  1. Engineer describes a task as a prompt.
  2. Codex explores, plans, implements, runs unit tests, runs the app
     in its own per-worktree environment.
  3. Codex opens a PR.
  4. Codex reviews its own changes locally; requests additional agent
     reviews (local + cloud); responds to human *and* agent feedback;
     iterates until all agent reviewers are satisfied.
  5. PR is short-lived; merges are quick; test flakes are addressed
     with follow-up runs rather than blocking.
- **Harness invariants:** layered architecture with strictly enforced
  dependency directions; per-layer custom linters; linter error
  messages *inject remediation instructions into agent context*; a
  weekly doc-gardening agent opens refactor PRs; a "golden principles"
  file is the analogue of CLAUDE.md.
- **Levels of autonomy:** given a single prompt, Codex can now
  *end-to-end drive a new feature* — validate the codebase, reproduce
  a bug, record a video of the failure, implement the fix, drive the
  app, record a video of the fix, open a PR, respond to feedback,
  detect and remediate build failures, and escalate to a human only
  when judgment is required.
- **Source:** OpenAI, *Harness engineering* (Lopopolo, 2026-02-11).
  [VERIFIED, internal post]

### 1.2 GitHub (Copilot / Agent HQ) — "agents native to the GitHub flow"

- **Adoption:** "80% of new developers are using Copilot in their first
  week" (Universe 2025-10-28). The Copilot coding agent assigns itself
  PRs and responds to review feedback.
- **Loop:**
  1. Engineer creates an issue (or assigns the Copilot coding agent
     one).
  2. Agent works in a cloud environment; opens a draft PR.
  3. PR runs through CI; the agent responds to CI failures
     automatically.
  4. Copilot code review (Low or Medium effort) reviews the PR — now
     *with* agentic capabilities: full project context gathering and
     the ability to pass suggestions back to the cloud agent as a
     follow-up PR.
  5. Human reviewer approves; merge.
- **Enterprise controls (Agent HQ):** Mission control (single command
  center across GitHub, VS Code, mobile, CLI); branch controls (when
  CI runs for agent-created code); identity features (which agent
  built what); one-click merge conflict resolution; AI controls /
  control plane for governing agent access and policies; Copilot
  metrics dashboard; Slack + Linear + Jira + Teams + Raycast
  integrations.
- **Code review effort levels:** *Low* (standard, fast) vs *Medium*
  (higher-reasoning model, longer analysis, more credits, more
  Actions minutes). "Use Medium for security-sensitive code, multi-
  service pull requests, or repositories with strict quality
  standards."
- **MCP + agent skills:** repositories can define AGENTS.md, custom
  skills, and MCP servers; both Copilot cloud agent and Copilot code
  review use them.
- **Source:** GitHub Blog, *Introducing Agent HQ* (Daigle, 2025-10-28)
  and *GitHub Copilot code review* docs (2026).
  [VERIFIED, primary]

### 1.3 Anthropic (Claude Code) — "give the agent a way to verify"

- **Loop (the canonical 4 phases):** explore → plan → implement →
  commit. The phases are *separated by mode* (plan mode vs default
  mode). Plan mode is for when scope is unclear; default mode is for
  when the fix is small.
- **CLAUDE.md** at the project root holds only what the model can't
  figure out from the code (commands, code style, workflow rules).
  Skills (`.claude/skills/`) hold domain knowledge loaded on demand.
  Subagents (`.claude/agents/`) run in fresh context for
  investigation and verification. Hooks (`.claude/settings.json`) run
  deterministically at workflow points. Plugins bundle skills + hooks
  + subagents + MCP servers.
- **Permissions:** three modes — *auto mode* (classifier reviews
  commands; blocks scope escalation, unknown infra, hostile-content
  actions), *permission allowlist* (e.g. `npm run lint`), *sandboxing*
  (OS-level isolation). Auto mode aborts a non-interactive run if the
  classifier repeatedly blocks.
- **Verification:** Stop hooks block the turn until the check passes
  (overridden after 8 consecutive blocks); a `/goal` condition is
  re-checked after every turn; a subagent in fresh context verifies
  the diff against the plan.
- **Parallelism:** worktrees (separate git checkouts per session),
  the desktop app, Claude Code on the web (Anthropic-managed VMs),
  agent teams (automated coordination of multiple sessions with
  shared tasks, messaging, a team lead).
- **Source:** Anthropic, *Best Practices for Claude Code* (2026).
  [VERIFIED, primary]

### 1.4 Cursor (self-driving codebases, cloud agents, Auto-review)

- **Multi-agent self-driving research (browser, 2026-02-05):**
  - System peaked at **~1,000 commits/hour, 10M tool calls, 0
    humans, for a week**.
  - Final architecture: *root planner* owns the whole scope, does no
    coding; *subplanners* (recursive) own narrow slices; *workers*
    pick up tasks, are unaware of the larger system, work on their
    own copy of the repo, and write a single handoff when done.
  - **The integrator was removed** — it was the bottleneck (one
    gate, hundreds of workers trying to push, rebase, resolve,
    merge). The system instead accepts some local contention and
    reconciles errors in a final "green" pass before release.
  - **Lockless file coordination failed** — agents held locks too
    long, forgot to release, optimised for small safe changes; a
    shared coordination file collapsed 20 agents to 1–3 effective.
  - **Quality is traded for throughput** — requiring 100% commit
    correctness caused major serialization; the system now accepts
    a "small but constant" error rate and reconciles in the final
    pass.
  - **Architecture matters as much as instructions.** First
    version's simple-no-JS browser converged to an architecture that
    couldn't evolve to a full browser — "a failure of the initial
    specification." Monolithic repos are throughput-limited by
    compile time.
- **Cloud agents (2026-06-02):**
  - Reliability went from "one 9" to "two 9s" after migrating to
    **Temporal** for durable execution. **50M Temporal actions/day,
    7M unique workflows/day.** Internally, **40%+ of Cursor's PRs
    come from cloud agents** and growing.
  - Architecture: agent loop, machine state, and conversation state
    are *decoupled* components. The agent loop lives in Temporal;
    VMs are managed independently (readonly, prewarmed, etc.).
  - Conversation layer is append-only; clients can detect and rewind
    a retried turn's stream.
  - Harness is being *hollowed out*: "A year ago, multi-repo setups
    required hardcoded harness behaviour. Now, we can give the
    agent the repo layout, expose tools for branches and PRs, and
    let it decide how to do the work." CI Autofix used to grab
    job failure logs and write them to the VM; now the agent uses
    `gh` itself.
- **Auto-review (2026-06-11):**
  - Classifier is a *small, fast, agentic* model — it can use Read,
    Grep, Glob, ListDir before deciding. Lives in the *same RPC
    stream* as the parent agent (no extra round trip).
  - Production stats: **~4% of actions blocked**; **~7% of chats
    lead to at least one user interruption** (vs ~40% in some
    enterprises with blanket permission gates).
  - Eval: 6,122 labelled rows from 12 hours of internal sessions
    + synthetic adversarial cases; "flapping" is the primary
    signal of underspecified policy.
- **Source:** Cursor blog (2026). [VERIFIED, internal posts]

### 1.5 Cognition / Devin — "an army of agents + an evaluator agent"

- **Loop:** a Devin session is one task; a *fleet* of Devins is the
  production unit. Devin spins up a team of Devins for large tasks.
  The agent works in a real Linux VM with root access.
- **Evaluator agent:** separate model with the same tools (browsing,
  shell, code editing) judges the deliverable against *typed* criteria
  (e.g. "does the dashboard have more than 5 graphs?"). Used in
  their internal `cognition-golden` benchmark (74.2% production
  score, autonomous) and in the user-facing review flow.
- **Real production case (Nubank ETL migration, 2026):**
  - **8–12x engineering-time efficiency gain, 20x cost savings** on
    a 6M-LOC monolith split into sub-modules (originally 18 months,
    1,000+ engineers, completed in weeks).
  - **Fine-tuning doubled task-completion scores and 4x'd speed**
    (40 min/sub-task → 10 min) on the migration benchmark.
  - Devin *built itself classical tools* (e.g. country-extension
    detector) and reused them across sub-tasks — compounding
    learning, not just per-task.
- **Cognition's own production loop:** *How Cognition Uses Devin to
  Build Devin* (Cognition blog, 2026-02-27) — they dogfood their own
  product for production engineering.
- **Source:** devin.ai, cognition.com/blog (2026). [VERIFIED, primary
  + case study]

### 1.6 Amazon (Q Developer) — "agentic across the entire SDLC"

- **Capabilities:** real-time code suggestions (single line → full
  function); inline chat; CLI completions + natural-language → bash;
  security scanning (claims to outperform "leading publicly
  benchmarkable tools"); agentic code generation (implementing
  features, documenting, testing, reviewing, refactoring, software
  upgrades); .NET porting; Java 8 → 17 upgrade automation.
- **Reported as "highest scores on the SWE-Bench Leaderboard and
  Leaderboard Lite"** among agentic coding systems. (NB: needs
  re-verification against the current swebench.com leaderboard
  before quoting in a load-bearing claim.)
- **Surfaces:** IDE (JetBrains, VS Code, Visual Studio, Eclipse),
  CLI, AWS Console, GitLab (GitLab Duo with Amazon Q), GitHub.com /
  GitHub Enterprise Cloud, Microsoft Teams, Slack.
- **Identity / governance:** AWS IAM Identity Center integration;
  proprietary content not used for service improvement on the Pro
  tier.
- **Source:** aws.amazon.com/q/developer (2026). [VENDOR — claims
  need re-verification on benchmarks]

### 1.7 Vercel v0 — "agent + real-time preview = the loop"

- **What it is:** an AI agent that generates real code and full-stack
  apps; deploys to Vercel infrastructure immediately or opens a PR
  for review.
- **Loop:** prompt → multi-modal inputs (text, screenshots, Figma,
  URLs, data) → real-time preview → code edit + terminal commands
  + design mode + versions → deploy / PR.
- **Integrations:** AI models, databases, Snowflake, external APIs,
  GitHub, MCP, pre-installed agents, Slack.
- **Use cases:** PMs (prototypes, RFCs, user-interview questions),
  designers (mockup → high-fidelity UI), engineers (scaffold full-
  stack), data scientists (Snowflake / SQL / Pandas), marketers
  (landing pages), founders (MVPs).
- **Source:** vercel.com/docs (2026). [VERIFIED, primary]

### 1.8 Replit Agent 4 — "concurrent agents on a shared design canvas"

- **Concurrency:** "Agent 4 splits single tasks into different forks,
  working on them concurrently and then combining the results." Tasks
  can be submitted in any order; Agent 4 intelligently sequences.
- **Design canvas:** visual design edits applied directly to the app;
  "Generate variants" on any element for in-context exploration;
  multi-user vibe coding via a kanban board for team coordination.
- **Source:** replit.com/agent4 (2026). [VENDOR]

### 1.9 Google / Google DeepMind (AlphaEvolve) — "evolutionary agent at scale, deployed in production"

- **AlphaEvolve (2025-05-14):** an evolutionary coding agent powered
  by Gemini Flash (breadth) + Gemini Pro (depth). Automated
  evaluators score proposed programs; an evolutionary framework
  improves on the most promising.
- **Production deployments at Google:**
  - **Borg data center scheduling heuristic** — in production for
    over a year; recovers **0.7% of Google's worldwide compute** on
    average, continuously.
  - **TPU arithmetic circuit** — Verilog rewrite that removed
    unnecessary bits, integrated into an upcoming TPU.
  - **Gemini training kernel** — 23% speedup of a matrix-
    multiplication kernel, 1% reduction in Gemini training time.
  - **FlashAttention** — 32.5% speedup.
  - **Mathematical algorithm discovery** — improved Strassen's
    1969 algorithm for 4×4 complex-valued matrix multiplication
    (48 scalar multiplications); advanced the *kissing number
    problem* (11 dimensions: 593 outer spheres).
- **Google Antigravity** (deepmind.google, 2026) is Google's
  *agentic development platform*; positioned alongside Gemini
  Code Assist as the production agent harness.
- **Source:** deepmind.google/blog/alphaevolve (2025-05-14),
  research.google (2026). [VERIFIED, primary]

---

## §2. Answers to the eight research questions

### Q1. How do Google, Meta, Amazon, Microsoft use AI in their production loop?

| Company | Surface | Production role |
|---|---|---|
| **Google / DeepMind** | Gemini Code Assist, **Antigravity** (agentic dev platform), AlphaEvolve, Gemini Robotics, Gemini Enterprise Agent Platform | Internal: AlphaEvolve *in production* at Borg, TPU, Gemini kernel, FlashAttention. Public: Gemini Code Assist + Antigravity. Google's published research (e.g. *Towards self-driving codebases*-style work isn't public, but the AlphaEvolve loop is the model). |
| **Microsoft** | GitHub Copilot (Business / Enterprise), Copilot Coding Agent, Copilot Code Review, Copilot Spaces, Copilot CLI, MCP Registry, Agent HQ | The most widely-deployed agentic coding surface in industry (180M+ GitHub users, 80% of new devs on Copilot in their first week). Copilot coding agent is a first-class PR author. *Microsoft's own internal usage* isn't published in detail; the GitHub blog is the proxy. |
| **Meta** | MetaGPT (research), Llama-based code models, internal AI tooling | Public detail is thin in 2026 — Meta's published *production* case studies for AI-assisted coding are limited compared to OpenAI / Anthropic / Cursor. MetaGPT is the research artefact (assembly-line, SOPs encoded as prompts); production deployment is internal. **The gap:** this is the area where the public evidence is thinnest; future research should look for *internal* posts. |
| **Amazon** | Amazon Q Developer (formerly CodeWhisperer), Q in Console, GitLab Duo with Amazon Q, Q in Slack/Teams | Agentic across the SDLC; highest reported scores on SWE-Bench at launch; security scanning outperforming benchmarks (per vendor claim — re-verify). Java 8→17 and .NET porting in production at AWS itself and at customers. |

**[VERIFIED, multi-source]** for Google, Microsoft, Amazon. **[EMERGING]**
for Meta — public production evidence is limited.

### Q2. The real planning → building → reviewing → testing loop in production

The loop that emerges is *not* a waterfall and *not* an LLM-judged gate.
It's a 4-phase loop with an *integrated* verification surface:

1. **Plan.** Either by a planner model (Cursor self-driving, OpenAI
   self-summarisation, Devin session planning) or by a human prompt
   (OpenAI Codex, Anthropic Claude Code plan mode, GitHub issue
   description). Spec / scope / acceptance criteria live in the
   *repo* (`SPEC.md`, GitHub issue body, `PLAN.md`).
2. **Build.** A *context-isolated* worker (Cursor's worker, OpenAI's
   Codex, Anthropic's subagent, Devin, Replit agent) takes a
   *single-task* packet, runs in its own copy of the repo /
   environment, implements, runs the verification surface.
3. **Verify.** Deterministic checks (test suite, build, lint, type
   check, screenshot diff) close the loop. The agent iterates until
   the check passes. *Agent-to-agent* review (Anthropic Writer/
   Reviewer, OpenAI "all agent reviewers are satisfied", GitHub
   Copilot code review) provides the second-opinion layer.
4. **Ship.** PR → CI → human or auto-merge. PRs are *short-lived*;
   merge gates are *minimal*; test flakes are addressed with
   follow-up runs not blocked PRs. Deployment is automated; rollback
   is part of the deployment platform (Vercel, Replit, AWS, Google
   Cloud Run).

This is the loop ASPIS's `CORE_LOOP.md` design should target.

### Q3. How does code review work with AI?

- **AI reviewing code (AI → code):**
  - **GitHub Copilot code review** (Low + Medium effort levels;
    automatic on PR; agentic capabilities for full project context
    gathering; can pass suggestions to the Copilot cloud agent as a
    follow-up PR).
  - **Cursor Bugbot** (now 3x faster, 22% cheaper, finds 10% more
    bugs — June 2026 update).
  - **Amazon Q Developer** security scanning.
  - **Claude Code** `/code-review` skill and subagent review.
  - **Devin Review** (visual QA, intelligently organised diffs).
- **AI-generated code being reviewed (code → human):**
  - All of the above also produce the *output* being reviewed.
  - The OpenAI Codex case is the most extreme: the human rarely
    *must* review; the review is agent-to-agent.
- **Both (AI ↔ AI):** the dominant pattern in 2026 is *both* —
  agent writes, agent reviews in a fresh context, agent iterates
  on the review's findings. The human's role becomes
  *spot-checking* the agent's findings, not writing them.

[VERIFIED, multi-source]

### Q4. How does testing work with AI?

- **AI writing tests:** Claude Code's *Writer/Reviewer* pattern
  explicitly uses two sessions — one writes tests, the other writes
  the code to pass them. OpenAI's harness uses the same shape.
- **AI running tests:** the verification surface. Cursor, OpenAI,
  Cognition all close the loop on test results — "Claude does the
  work, runs the check, reads the result, and iterates until the
  check passes" (Anthropic).
- **AI interpreting test results:** the *subagent* pattern (Claude
  Code) and *evaluator agent* (Cognition) interpret results in
  *fresh context* to avoid the bias of the implementing session.
- **Test infrastructure changes:** the tests are no longer a
  pre-defined suite — they're a *check the agent can run*. In the
  OpenAI harness, this includes *log/metric queries* (LogQL,
  PromQL) and *screenshot diffs*, not just unit tests.
- **SWE-bench as the canonical test:** every agent on the leaderboard
  is graded by running the upstream test patch. The leaderboard
  *is* the public test infrastructure for agents.

[VERIFIED, multi-source]

### Q5. CI/CD's role in agentic systems; how agents interact with CI pipelines

- **The agent IS a CI consumer.** OpenAI's Codex reports CI failures
  back to itself and iterates. GitHub's Copilot coding agent
  responds to CI failures automatically. Claude Code's CI Autofix
  flow is now just "give the agent the `gh` CLI and let it query
  Actions" (Cursor's observation: harness is being hollowed out).
- **The agent IS a CI producer.** Cursor's 40%+ of internal PRs
  come from cloud agents. Devin opens PRs as its primary output.
- **GitHub Actions is the verification runner.** Copilot code
  review's agentic capabilities (full project context gathering,
  passing suggestions back) run on GitHub Actions; larger runners
  cost more; self-hosted runners don't consume minutes.
- **Branch controls are new.** Agent HQ ships *branch controls*
  (granular oversight of when CI runs for agent-created code) —
  the team can decide "agents can push to feature branches without
  CI; CI runs on PR open" vs "every push runs CI."
- **The handoff between agent and CI is typed.** The agent gets the
  CLI; the CI gives the agent a log; the agent decides what to do.
  The `claude -p --output-format stream-json` pattern in
  non-interactive mode is the canonical typed contract.

[VERIFIED, multi-source]

### Q6. Feature branches, PRs, merges in AI-assisted development

- **Branches are still branches.** Git is the substrate; feature
  branches and PRs survive because they're the *asynchronous
  collaboration primitive* (per GitHub's framing in the Agent HQ
  launch).
- **PRs are agent-first.** "Devin ships PRs the way your team does
  — picking up review feedback and CI results to get each PR
  approved and merged." Same for GitHub Copilot coding agent,
  Cursor cloud agents, OpenAI Codex.
- **PRs are short-lived.** "The repository operates with minimal
  blocking merge gates. Pull requests are short-lived. Test
  flakes are often addressed with follow-up runs rather than
  blocking progress indefinitely." (OpenAI)
- **Identity for agents.** "Identity features to control which
  agent is building the task, managing access, and policies just
  like you would with any other developer on your team." (GitHub)
- **Worktrees for parallelism.** Claude Code runs parallel sessions
  in isolated git worktrees; Cursor workers each work on their
  own copy of the repo; OpenAI Codex bootable per worktree.
- **Squash-and-merge by the agent.** OpenAI Codex often squashes
  and merges its own PRs after agent-to-agent review.

[VERIFIED, multi-source]

### Q7. What's proven for quality gates (linting, type check, test coverage, security)?

All five of the following are used in production *in combination*:

1. **Linting + type checking.** Universal. OpenAI's harness
   *injects remediation instructions from the linter error message
   into agent context* — i.e. linters are part of the agent's
   feedback loop, not just a CI check.
2. **Test suite (unit + integration + E2E).** Universal. The
   deterministic check the agent runs. Coverage thresholds are
   the *build* bar, not the *quality* bar.
3. **Architectural invariants (custom linters, structural tests).**
   OpenAI's harness encodes "types → config → repo → service →
   runtime → UI" as a fixed dependency direction; the linter
   catches violations; the agent cannot proceed without fixing.
4. **Security scanning.** Amazon Q Developer security scanning
   (vendor claim of outperforming public benchmarks; re-verify).
   GitHub Copilot Autofix is in GitHub Advanced Security; the
   CodeQL engine is the underlying scanner; Dependabot handles
   dependencies. Cursor's "fleet of security agents" (open-
   sourced March 2026) is a separate agent surface.
5. **Code review (AI + human).** The quality gate *over* the
   gates above. GitHub Copilot code review at Medium effort
   uses a higher-reasoning model; Cursor Bugbot is the equivalent
   for the Cursor monorepo.

The *lesson*: quality gates are *layered*. Each layer catches a
different failure mode. No single layer is enough.

[VERIFIED, multi-source]

### Q8. The "last mile" — deployment, monitoring, rollback

- **Deployment is to a platform, not a server.** Vercel, Replit,
  AWS, Google Cloud Run, and Azure all provide "one-click deploy"
  as part of the agent surface. The agent doesn't manage the
  runtime; the platform does.
- **PRs are the deployable unit.** Once a PR merges, deploy is
  triggered by the merge. OpenAI Codex squashes and merges;
  GitHub's branch controls decide when CI / deploy run.
- **Monitoring is the *next* agent surface.** Amazon Q Developer
  is available in Microsoft Teams and Slack "to help you monitor
  operational events, troubleshoot issues, and operate AWS
  resources." GitHub Copilot's metrics dashboard tracks agent
  usage across the org. Cursor's `cloud-agent-lessons` post
  gestures at this future: *"agents merge PRs, manage rollouts,
  and monitor production."*
- **Rollback is part of the platform.** The agent doesn't roll
  back its own deploys; the platform exposes a one-click rollback
  the agent can call.
- **The dev environment is the deploy environment.** Cursor,
  Replit, Vercel, GitHub Codespaces all collapse "dev env" and
  "deploy env" — the same VM the agent works in is the VM that
  serves the request. This makes the agent's verification
  surface *equal to* the production surface.

[VERIFIED for the deployment side; EMERGING for the
"agent monitors and rolls back" side — Cursor's vision, not
yet broadly observed.]

---

## §3. SWE-bench results analysis (for ASPIS SPEC success criteria)

SWE-bench is the public benchmark that *defines* the production loop
for coding agents. As of late 2025 / mid-2026:

- **SWE-bench Verified** is the human-filtered subset of 500
  instances; the field-standard metric.
- **mini-SWE-agent** (an SWE-bench team project) hits **~65% on
  SWE-bench Verified in 100 lines of Python** (announcement July
  2025) — i.e. the simple ReAct loop is highly competitive if you
  let the model use the test output as the feedback signal.
- **SWE-agent 1.0** is the open-source SOTA on SWE-bench Lite.
- **SWE-bench Multilingual** (300 tasks, 9 languages), **Lite**
  (cost-friendly), **Multimodal** (visual elements) — the family
  covers the surface.
- **Amazon Q Developer** has, per AWS, "the highest scores on
  the SWE-Bench Leaderboard and Leaderboard Lite" — vendor
  claim; cross-check the leaderboard at https://www.swebench.com/
  before quoting.
- **CodeClash** (November 2025) is the new eval of LMs as *goal-
  oriented* (not task-oriented) developers — a more demanding
  benchmark that captures longer-horizon work.

**ASPIS implication for success criteria:** the F-016 SPEC's
"production loop" success criteria should reference SWE-bench
Verified as the *external* benchmark for the agent's core
code-change capability, and a project-internal acceptance test
suite as the *internal* equivalent. A target like "SWE-bench
Verified score within X% of the current top open-source agent
on the same model class" is the right shape for a measurable
criterion.

[VERIFIED, primary]

---

## §4. Anti-patterns to avoid (consolidated)

From the eight sources above, the *negative* findings that emerged
consistently:

1. **Mega-prompts that try to do plan + build + review + commit.**
   The Anthropic, OpenAI, and Cursor teams all split these into
   separate contexts / subagents.
2. **One big AGENTS.md / CLAUDE.md.** OpenAI and Anthropic
   *both* explicitly recommend against; cursor's dev environment
   replaces the prompt with the *environment*.
3. **A single agent doing everything.** Cursor's first multi-agent
   attempt (one executor doing plan + explore + research + spawn +
   monitor + review + edit + merge + judge) collapsed under
   pathological behaviours — sleep, refusal, premature completion.
4. **Lock-based or shared-coordination-file multi-agent.** Cursor
   tried both; 20 agents → 1-3 effective.
5. **An integrator in the multi-agent path.** Cursor's integrator
   was the bottleneck; they removed it.
6. **Global permission switches (approve / deny everything).**
   Cursor's Auto-review explicitly frames its classifier as the
   fix for the "approval fatigue" failure mode.
7. **Self-review (the builder also reviewing its own work).**
   Anthropic, OpenAI, Cognition all use a *fresh-context*
   reviewer. ASPIS already forbids this in pattern A2 of
   `agent-system-design-patterns.md`.
8. **Requiring 100% commit correctness in a multi-agent loop.**
   Cursor explicitly accepts "a small but constant" error rate
   and reconciles in a final pass — the inverse is "agents pile
   on trying to fix the same issue and the system grinds to a
   halt."

---

## §5. Mapping to ASPIS

Cross-references to the existing ASPIS design (so this research
extends rather than duplicates):

| Production pattern (§0) | ASPIS design element | Existing research link |
|---|---|---|
| 1. Verification is the loop closer | R-002 (deterministic gate), R-005 (tests-as-spec); `aspis verify` is the system form | `agent-system-design-patterns.md` pattern 8 |
| 2. Repo knowledge is the system of record | `.aspis/` brain, `context-ladder` skill, `aspis context`, periodic doc-gardening (proposed) | `agent-system-design-patterns.md` pattern 10 |
| 3. Recursive planners + isolated workers | Build Lead → general-builder, two-level delegation ceiling | `agent-system-design-patterns.md` pattern 1, 2 |
| 4. Dev environment is the product | `runtime_guard`, `scope_guard`, brain, the task packet | `agent-system-design-patterns.md` pattern 5, 6 |
| 5. Risk-tiered autonomy via classifier | R-001 scope, `test_agent_permissions.py`, deterministic allowlist | `agent-system-design-patterns.md` pattern 6 |

The two new things this research *adds* to ASPIS design:

- **Graded autonomy via a small classifier model** (Pattern 5).
  The current ASPIS permission model is *deterministic*; the
  production pattern adds a *small model* in the loop that
  decides "this tool call needs the user, this one doesn't."
  Worth a follow-up feature once the runtime ships.
- **Acceptance reconciliation pass** (the "small but constant"
  error rate, Pattern 3 footnote). ASPIS's Reviewer already
  closes the gate on a deterministic criterion, but the multi-
  agent pattern shows that *between* worker hand-off and final
  acceptance, a *small reconciliation step* catches the
  "many agents touching the same file" failure mode. Worth
  adding to the Build Lead's flow once multi-agent workers
  exist.

---

## §6. Provenance notes and refresh schedule

- All sources read on 2026-06-25 (current as of that date).
- The most rapidly-changing surface is *leaderboard positions*
  (SWE-bench) and *model releases* (Gemini, GPT, Claude, Cursor
  Composer). Re-verify the SWE-bench leaderboard before quoting
  numbers in load-bearing claims.
- The most stable findings are the *structural* ones (Pattern 1–5):
  verification-in-the-loop, repo-as-system-of-record, recursive
  planners + isolated workers, dev-environment-as-product, risk-
  tiered autonomy. These are observed across at least three
  independent organisations and have survived multiple model
  generations.
- Suggested refresh cadence: **quarterly** for benchmark numbers;
  **on major model release** for the production-loop findings.

<!-- ASPIS:REFERENCE END -->
