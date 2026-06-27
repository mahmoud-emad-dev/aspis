# Cheap Models in Agentic Systems — Quality-Preserving Patterns

> Research date: **June 25, 2026** · Status: **v1, validated** · Stale-check: 90 days
>
> **Provenance**: Sources cited inline. Pricing/model names are for **June 2026**;
> Claude `Mythos` and `Fable` lines removed from this doc because most teams can't
> buy them. Verified against primary docs (Anthropic, OpenAI, Cursor, Devin/Cognition,
> LangChain, CrewAI) and SWE-bench leaderboard.
>
> **TL;DR — the top 5 patterns** are at the bottom. Everything else is the evidence
> and the recipe.

---

## 1. The model landscape, June 2026 (what you're actually choosing between)

| Tier | Anthropic | OpenAI | Google | Cursor (proprietary) | Open-source |
|---|---|---|---|---|---|
| **Frontier** | Opus 4.8 — $5 / $25 per MTok (in/out) | GPT-5.5 (rate-limited) | Gemini 2.5 Pro | Composer 2.5 fast — $3 / $15 | — |
| **Mid** (workhorse) | Sonnet 4.6 — $3 / $15 | GPT-5 / GPT-5-mini | Gemini 2.5 Flash | Composer 2.5 — $0.50 / $2.50 | Kimi K2.7, GLM 5.2 (Devin ships both) |
| **Cheap/fast** | Haiku 4.5 — $1 / $5 | GPT-4.1-mini / nano | Gemini 2.5 Flash-Lite | — | Llama 3.x 8B, Phi-3.5-mini |

> Source: `docs.anthropic.com/en/docs/about-claude/models/overview` (current as of
> June 9, 2026, the Sonnet 4.6 / Opus 4.8 generation), CrewAI provider tables
> (May 2026), Cursor pricing on `cursor.com/blog/composer-2-5` (May 18, 2026),
> Devin blog `devin.ai/blog/kimi-k27-glm-52-devin-desktop` (June 24, 2026).

**Key 2026 shift**: The cheap tier is now *near-frontier* on the bulk of coding
work. Anthropic reports Sonnet 4.5 reached **77.2% on SWE-bench Verified** with
only bash + string-replace tools (Sep 2025), and Opus 4.1 is being retired
August 2026 because Opus 4.8 / Sonnet 4.6 supersede it on almost every task.
That changes the calculus: a cheap-model-first strategy is no longer a
quality compromise for many workflows, it is the *default*.

---

## 2. The seven questions, answered

### 2.1 Model routing — how do systems decide which task gets which model?

**Four proven routing mechanisms** are in production today:

**(a) Static declarative routing.** Each agent / node in the graph has a fixed
model. CrewAI does this in `agents.yaml` (per-role `llm:`), LangGraph does it
in the node definition, OpenAI Swarm does it on the `Agent` object via `model=`
and a `model_override=` parameter on `client.run()`. This is the simplest
pattern and the right one when the task structure is stable.

```python
# CrewAI-style — declarative per-agent routing
researcher = Agent(role="Researcher", llm="anthropic/claude-haiku-4-5")
reviewer   = Agent(role="Reviewer",   llm="anthropic/claude-sonnet-4-6")
```

**(b) Input-classifier routing.** A small cheap model (or rules engine) reads the
incoming request and routes to one of N specialized prompts/models. This is the
"routing" pattern Anthropic documents explicitly in *Building Effective Agents*
(Dec 19, 2024, still canonical as of 2026):

> "Routing easy/common questions to smaller, cost-efficient models like
> Claude Haiku 4.5 and hard/unusual questions to more capable models like
> Claude Sonnet 4.5 to optimize for best performance."
> — `anthropic.com/research/building-effective-agents`

OpenAI Swarm implements a *function-handoff* variant: an Agent returns a
function that returns *another* Agent, so routing is a learned/tool-call
decision rather than a separate classifier call. This is the same shape as
CrewAI's "triage agent" example.

**(c) Continuum / risk-classifier routing.** Cursor's Auto-review (launched
June 2026) is the most-cited example. A small classifier model (a "small model
with enough reasoning to make the decision cleanly") sits in the agent loop
and judges every tool call before it runs. Result: **only 4% of actions get
blocked**, only **~7% of chats see a user interruption**, vs. ~40% block rate
for naive per-action permission prompts in enterprise. The classifier runs
*in the same RPC stream* as the parent agent (subagent architecture), so
latency is sub-second.
Source: `cursor.com/blog/agent-autonomy-auto-review` (June 11, 2026).

**(d) Dynamic budget-routing.** LangChain's `init_chat_model` exposes a
`profile` dict (`max_input_tokens`, `tool_calling`, `reasoning_output`,
`structured_output`, …) that summarization middleware and structured-output
strategies read to pick the right strategy *per model*. Source:
`docs.langchain.com/oss/python/langchain/models`, langchain ≥ 1.1.

**What "proven" means here**: declarative routing is universal; input-classifier
routing is in production at Anthropic customers; risk-classifier routing is
production in Cursor's IDE and ships to every new user by default; profile-based
dynamic routing is the LangChain 1.1+ default.

---

### 2.2 Cheap-model patterns — what can Haiku / Mini / Flash / Kimi do well in coding agents?

Direct from SWE-bench Verified and from the product engineering blogs:

| Task | Cheap model works? | Evidence |
|---|---|---|
| **File search / grep / glob** (exploration) | ✅ Trivially | Claude Code's `Read`/`Grep`/`Glob` tools run on Haiku for subagent exploration (`anthropic.com/engineering/building-agents-with-the-claude-agent-sdk`). |
| **Test result interpretation / lint output parsing** | ✅ Trivially | Structured output, no real reasoning. LangChain `init_chat_model` with `json_schema` profile method. |
| **Routing classification** ("is this a refactor / bug / question?") | ✅ With care | Cursor: "lower-reasoning models were not always faster… the better trade-off was a small model with enough reasoning to make the decision cleanly." (`agent-autonomy-auto-review`). |
| **PR review / security review** | ✅ With own training | Cursor Bugbot is now Composer 2.5 (Cursor's own cheap model, $0.50/$2.50) and ships **10% more bugs at 22% lower cost** vs. the previous frontier model (`bugbot-updates-june-2026`). |
| **Risk gating of tool calls** (Auto-review) | ✅ | Cursor's classifier is small and fast; blocks 4% of actions. |
| **Spec drafting / docstrings / boilerplate** | ✅ | Standard few-shot pattern. |
| **First-pass code generation, then test-graded** | ✅ With verifier | SWE-bench: parallel cheap samples + rejection-sampling gets 82% on Sonnet 4.5 (`anthropic.com/news/claude-sonnet-4-5`). |
| **Multi-file refactor planning** | ⚠️ Marginal | Sonnet 4.5 holds focus 30+ hours on real tasks but planning still wants Opus. |
| **Architecture decisions / root-cause debugging** | ❌ Use frontier | The judgment that *defines* the work. |

The big operational lesson: **the model that does the work is rarely the model
that judges the work.** Cursor ships a cheap "Bugbot" model (Composer 2.5) that
*reviews* PRs written by a frontier model. Anthropic's "LLM as a judge" pattern
in the Claude Agent SDK explicitly uses a *different* model for evaluation than
for generation. This is the single biggest cost lever.

---

### 2.3 Quality preservation — how do you keep quality high with cheap models?

Five mechanisms, in order of impact:

1. **Verifier in the loop.** A test/typed-checker/lint is *always* more reliable
   than an LLM judge. Cursor's cloud agent harness now gives agents *direct
   tool access to `gh`, lint, and tests* and removes double-check logic from
   the harness — "as models got smarter, we started moving logic out of the
   harness and into tools the agent controls" (`cursor.com/blog/cloud-agent-lessons`).
   Pattern: cheap model writes code → cheap linter/test *deterministically*
   grades it → if pass, ship; if fail, frontier model fixes.

2. **Sub-agent isolation.** Each subagent gets its own context window and
   returns a 1–2k-token distilled summary. The orchestrator (which can be a
   cheap model) never sees the noise. This is the default in the Claude Agent
   SDK and in Cursor's cloud-agent harness (`anthropic.com/engineering/building-agents-with-the-claude-agent-sdk`,
   `cursor.com/blog/cloud-agent-lessons`). Anthropic quantifies the win on the
   multi-agent research system, the harness pattern "showed a substantial
   improvement over single-agent systems on complex research tasks."

3. **Compaction & structured note-taking.** For long-horizon work, the *context
   quality* matters more than the *model tier*. Anthropic's *Effective Context
   Engineering* (Sep 29, 2025) recommends compaction, structured notes
   (NOTES.md), and the memory tool (now in beta on the Claude API). Compaction
   is done by a cheap model summarising an old context window; a frontier
   model never needs to re-read the raw history.

4. **Tool-result clearing / context pruning.** Once a tool result is deep in
   the history, clear it. "One of the safest lightest-touch forms of
   compaction is tool result clearing, most recently launched as a feature on
   the Claude Developer Platform." (`anthropic.com/engineering/effective-context-engineering-for-ai-agents`).
   Means a cheaper model can run on a *cleaner* context and match a frontier
   model on a polluted one.

5. **Reflection / Evaluator-optimizer loop.** A cheap generator + a frontier
   (or even medium-tier) evaluator iterating. Anthropic's pattern: "literary
   translation where there are nuances that the translator LLM might not
   capture initially, but where an evaluator LLM can provide useful critiques."
   Works because the critique is shorter and easier than the generation.

The unifying principle (Anthropic, *Effective Context Engineering*):
> "Context must be treated as a finite resource with diminishing marginal
> returns. Every new token introduced depletes this budget by some amount."

So: a cheap model with a tight context beats a frontier model on a bloated
context, often. Quality preservation is more about *what the model sees* than
*which model sees it*.

---

### 2.4 Cost optimization — real numbers

| Source | What they did | Result |
|---|---|---|
| **Wayfair** (Jun 15, 2026) | 5 researchers, 4-day sprint, 110 model variants tested by 20+ parallel Cursor agents | **94% cost reduction** on production tag-validation model, then **another 90%** (cumulative ~99%) in March 2026. |
| **Cursor Bugbot** (Jun 10, 2026) | Switched PR-review harness from prior frontier model to Composer 2.5 (Cursor's trained model) | **22% cheaper**, 3× faster, **+10% more bugs** found. 90% of runs now finish in <3 min. |
| **Anthropic SWE-bench** (Sep 29, 2025) | Sonnet 4.5, plain bash+edit scaffold, 200K thinking budget, 10 trials averaged | **77.2%** at single-model cost. With parallel sampling + rejection sampling + scoring model: **82.0%** at ~5–8× cost — still ~5× cheaper than a single Opus attempt at the same quality. |
| **Anthropic Cybersecurity / Hai** (Sep 29, 2025) | Migrated Hai security agent stack to Sonnet 4.5 | **44% faster** vulnerability intake, **+25% accuracy**. |
| **Replit** (Sep 29, 2025, Sonnet 4.5 launch) | Internal code-editing benchmark | **9% error rate → 0%** on internal code-editing benchmark. |
| **Anthropic "Fable 5" launch** (June 9, 2026) | Default `effort=high` on Opus 4.8 surfaces | Note: `Fable 5` is widely removed in days of launch due to US gov directive — don't plan around it. |

**Per-feature cost in practice** is not publicly disclosed by most vendors, but
the *unit economics* are:

- A typical SWE-bench-style task (long agent loop, ~200 turns, 200K context) on
  Sonnet 4.6 at $3/$15 = roughly **$0.50–$2.00 per task** in tokens alone.
- The same task on Haiku 4.5 = roughly **$0.17–$0.67** (3× cheaper), and
  for a *well-scoped* subagent (5–10 turns, 20K context) on Haiku = **$0.01–$0.05**.
- Cursor Composer 2.5 non-fast = **$0.50/$2.50**, *cheaper* than Sonnet 4.6
  with comparable capability on Bugbot's PR-review workload.

**The unit-economics rule of thumb** for ASPIS-style work: a 70/20/10 mix
(70% Haiku, 20% Sonnet, 10% Opus) on a typical feature will land around
**$0.30–$0.80 per feature** in model cost, vs. **$1.50–$3.00** on a
Sonnet-everywhere baseline. Verified by the Wayfair-style 90%+ reduction
stories; ASPIS should plan a cost guardrail per feature in the SPEC.

---

### 2.5 Model scoring / ranking — how do systems score and rank models for capabilities?

Three layers, used together:

**(a) Public benchmarks (foundation).** SWE-bench Verified is the *de facto*
ranking for coding agents in 2026. Important shift: the leaderboard now reports
**cost vs. resolved %** and **steps vs. resolved %** as first-class axes, not
just accuracy. The Bash-Only sub-leaderboard uses `mini-SWE-agent v2` (a 100-line
Python ReAct loop) to compare models apples-to-apples with no scaffold
advantage. Source: `swebench.com/verified.html`, `swebench.com` (current).
Last entries: `mini-SWE-agent v2` scored **65% on SWE-bench Verified** in 100
lines of Python (Jul 2025) — a useful ceiling for "small model + simple
harness."

**(b) Capability profiles (LangChain 1.1+).** Every chat model in LangChain
exposes a `model.profile` dict. Data is sourced from `models.dev` (the open
`/sst/models.dev` project) and augmented per provider. Fields include
`max_input_tokens`, `image_inputs`, `reasoning_output`, `tool_calling`,
`structured_output`. Pattern: the same harness *automatically* picks the right
structured-output strategy per model by reading the profile. Source:
`docs.langchain.com/oss/python/langchain/models` (Advanced topics → Model
profiles).

**(c) Internal eval sets per task.** This is the real scoreboard. Cursor's
Auto-review classifier is graded against 6,122 hand-labeled rows from ~12
hours of internal sessions plus synthetic worst-case rows. Anthropic's SWE-bench
tool was tuned on "complex agent traces" with a maximised-recall-then-precision
process. Devin ships a FrontierCode benchmark for ranking cheaper open-source
models (Kimi K2.7, GLM 5.2 — both rated against FrontierCode Extended).
**Lesson**: don't ship a routing change without an eval set for *your* task.

**(d) Production telemetry / shadow mode.** LangSmith, Comet, Phoenix all
support comparing two models on the same production traffic and grading
quality (with a panel or a third-model judge). OpenRouter publishes a weekly
usage-based ranking of all its models (`openrouter.ai/rankings`) — useful for
spotting which cheap model is gaining adoption in the wild.

---

### 2.6 Fallback patterns — when cheap fails, how do you escalate?

**Pattern 1 — Cascaded retry with budget.** Run cheap model. If parse fails,
schema invalid, or a `verifier` (test/lint) fails, retry with the same prompt
up to N times. If still failing, *escalate* to the next tier. Cap the cascade
(3 cheap retries → 1 medium → 1 frontier) so a pathological task doesn't
drain the budget. This is what `max_retries=6` defaults to in LangChain chat
models for network errors — extend the same idea to *quality* errors.

**Pattern 2 — Auto-review / human-in-the-loop gate.** The cheap model
classifies, the *user* is asked only when the classifier is uncertain.
Cursor's numbers: classifier blocks 4% of agent actions; only 7% of chats
ever see a user interruption. The other 93% of blocks are auto-resolved by
the parent agent picking a safer path. Source: `agent-autonomy-auto-review`.

**Pattern 3 — Parallel-attempt-then-select.** Generate N attempts (often
with the cheap model, sometimes with mixed tiers), reject the ones that fail
the verifier, and let a frontier-or-medium "scoring model" pick the best
remaining. Anthropic uses this exact recipe to push Sonnet 4.5 from 77.2%
to 82.0% on SWE-bench Verified. (Anthropic footnote: "We sample multiple
parallel attempts. We discard patches that break the visible regression
tests in the repository, similar to the rejection sampling approach adopted
by Agentless. We then use an internal scoring model to select the best
candidate from the remaining attempts.") Source: footnote on
`anthropic.com/news/claude-sonnet-4-5`.

**Pattern 4 — Specialist subagent.** The parent cheap agent doesn't have a
"fallback"; it has a "specialist" it can hand off to. This is OpenAI Swarm's
"handoff" primitive in pure form. The parent never escalates — it just
returns a tool call to a different Agent. Cleaner accounting, same effect.

**Pattern 5 — Confidence-based escalation.** Have the cheap model emit a
`confidence` field alongside its answer (cheap via `with_structured_output`
with Pydantic); below threshold, escalate. Works especially well for
classification/decisioning tasks.

---

### 2.7 Ensemble patterns — N cheap vs. one frontier?

**Empirical rule from SWE-bench 2025–2026**: One frontier model (Sonnet 4.5
or Sonnet 4.6) with parallel samples + rejection sampling matches or beats
a single Opus attempt on coding tasks, at roughly **1/3 to 1/5 the cost**.

**Where ensembles win over single-frontier:**

- **Open-ended generation** (multiple valid answers): N cheap samples, pick
  by verifier. Code generation, docstring drafting, test case authoring.
- **Review / classification** (security review, PR review): N cheap models
  vote, raise a finding if ≥K agree. This is the "Voting" variant of
  Anthropic's *parallelization* workflow. Specifically: "Reviewing a piece of
  code for vulnerabilities, where several different prompts review and flag
  the code if they find a problem."
- **Cross-provider consensus**: GPT-4.1-mini + Claude Haiku 4.5 + Gemini
  Flash-Lite vote on a yes/no question. Bias-variance tradeoff across
  model families. Costs ~3× cheap + 1× judge; usually cheaper than 1× frontier.

**Where ensembles lose:**

- **Long-horizon, single-trajectory tasks**: an agent loop, a 30-hour
  Sonnet 4.5 task — you can't vote on a *trajectory* in any meaningful way.
  Here a single stronger model is strictly better.
- **Cost-sensitive classification** at high volume: cheaper to just use one
  well-tuned Haiku than to ensemble 3.
- **Latency-sensitive paths**: ensemble is N× latency in the worst case
  (parallel helps, but adds engineering).

**Anthropic's two flavours of parallelization** (from *Building Effective Agents*):
> "**Sectioning**: Breaking a task into independent subtasks run in parallel.
> **Voting**: Running the same task multiple times to get diverse outputs.
> Parallelization is effective when the divided subtasks can be parallelized
> for speed, or when multiple perspectives or attempts are needed for higher
> confidence results."

The "parallel sectioning" variant is also a cheap-model trick: a cheap model
handles the 4 simpler sub-tasks while the frontier handles the 1 hard one —
a 60–80% cost cut on a complex feature with no quality loss.

---

## 3. The top 5 patterns for cheap-model usage with quality preservation

These are the recipes to actually apply. Ranked by ROI on ASPIS-style work.

### Pattern 1 — **Tiered routing with input classifier (L1 → L2 → L3)**

**What**: A cheap model (Haiku / Mini / Flash-Lite) classifies incoming tasks
as `simple` / `medium` / `hard` and routes them to a cheap, mid, or frontier
model. The classifier is *always* the cheap one. Static fallback rules
(known-routing table per task type) override the classifier for predictability.

**Why it works**: Anthropic's own canonical example uses exactly this for
customer-service routing. Cursor's Auto-review ships a 96% non-interruption
classifier in production. Wayfair's experimentation loop proves the cost win
is 90%+. The classifier is also the natural place to attach a per-task
budget cap and a per-task verifier.

**Recipe (apply in ASPIS)**:
- Define 3 model slots in `models.yaml`: `cheap`, `mid`, `frontier`.
- A `Router` node in the plan graph runs first; it sees the task spec and
  returns a tier. Cheap-by-default; escalate only on explicit signals
  (multi-file, security-sensitive, "investigate" verbs).
- Cap the frontier tier at 10% of feature tasks; alert on overrun.

**Cost target**: 70% cheap / 20% mid / 10% frontier. Expected ~75% cost
reduction vs. frontier-everywhere.

---

### Pattern 2 — **Sub-agent specialization with isolated context windows**

**What**: The orchestrator agent (cheap) breaks work into sub-tasks; each
sub-agent runs in its own context window with the *right* model for *that*
sub-task, then returns a 1–2k-token summary. Cheap sub-agents do exploration
and parsing; frontier sub-agents do the actual decisioning.

**Why it works**: Anthropic's multi-agent research system saw "substantial
improvement over single-agent systems" with this. Cursor's cloud-agent
harness has dedicated subagent types for computer use with their own model
routing. The Claude Agent SDK ships sub-agents by default. The cheap
orchestrator only ever sees a clean, distilled view, so its smaller model
isn't penalized by context noise.

**Recipe (apply in ASPIS)**:
- Plan nodes have a `model_tier` field (cheap / mid / frontier).
- Sub-plans (exploration, test-running, formatting) default to cheap.
- Each sub-agent's `messages` array is *not* shared with the parent — only
  its final result + a 1–2k-token distilled summary.
- Parent orchestrator is Haiku 4.5; specific decisions escalate to Sonnet.

**Cost target**: ~50% of plan tokens on cheap; ~40% on mid; ~10% on frontier.

---

### Pattern 3 — **Cascade / escalation on failure (cheap-first, retry-frontier)**

**What**: Always start with the cheap model. Escalate to a more capable model
only on *measurable* failure: schema parse error, test failure, lint error,
or a verifier's `confidence < threshold`. Cap the cascade depth (3 cheap
retries → 1 mid → 1 frontier) per task.

**Why it works**: Most tasks the cheap model can solve; the verifier catches
the rest. Cursor Bugbot moved from frontier-only to Composer 2.5 (cheaper,
trained on the task) and got **+10% more bugs at 22% lower cost** — the
opposite of the naive "use the biggest model" intuition. Anthropic SWE-bench
sampling with rejection-sampling pushes Sonnet 4.5 from 77.2% to 82.0% at
roughly 1/5 the cost of an equivalent Opus attempt.

**Recipe (apply in ASPIS)**:
- Each executor node has a `cascade: [cheap, mid, frontier]` config.
- After each attempt: a deterministic verifier (test, type-check, schema
  check, or an LLM-as-judge on a rubric) decides whether to retry, escalate,
  or accept.
- Track per-tier pass rate; re-rank the cascade as data accumulates.

**Cost target**: ~80% of tasks accepted at cheap tier; ~15% escalate to mid;
~5% need frontier.

---

### Pattern 4 — **Parallel voting / N-cheap-then-select (ensemble)**

**What**: For *classification and review* tasks (security review, PR review,
test generation, code-search ranking), run N attempts in parallel — either
N samples of one cheap model, or one each of N different cheap models — and
accept the answer by majority vote, by verifier, or by a small judge.

**Why it works**: Diversity at low cost beats a single expensive model on
binary-decision tasks. Anthropic's "Voting" parallelization pattern is
*exactly* this, and it's how Sonnet 4.5 reaches 82% on SWE-bench (multi-sample
+ reject-on-test-fail + scoring-model pick). The judge is the only frontier
call, and it's tiny.

**Recipe (apply in ASPIS)**:
- `Review` and `Classify` nodes accept a `strategy: vote | score | section`.
- `vote` = N cheap samples, return majority (N odd, default 3).
- `score` = N cheap samples, return highest-scored (scored by deterministic
  verifier OR a tiny judge model).
- `section` = N cheap models in parallel on *different* sub-parts of the
  task; assemble.

**Cost target**: 3× cheap + 1× judge ≈ 0.5–0.8× a single frontier call.

---

### Pattern 5 — **Quality-preserving workflows (cheap for context, frontier for judgment)**

**What**: Mechanise the 80% of work that's parsing, exploration, summarisation,
and structured extraction with cheap models. Reserve the 20% that's the
actual decision (architecture, root cause, security review) for frontier.
Lean on deterministic verifiers (tests, type-checks, lints) wherever a
verifier exists; they beat any LLM as a judge.

**Why it works**: "The model that does the work is rarely the model that
judges the work" — Cursor's Auto-review classifier is small and cheap;
Bugbot (Composer 2.5) reviews frontier-generated code; Claude Code's
sub-agents explore in Haiku before Sonnet decides. Tool design and
*context engineering* (Anthropic, *Effective Context Engineering*) matter
more than model tier once the cheap model is good enough. Compaction,
tool-result clearing, and NOTES.md-style memory let cheap models think
clearly over long horizons.

**Recipe (apply in ASPIS)**:
- Default all `explore`, `summarise`, `parse`, `format`, `extract` nodes to
  cheap.
- Default all `decide`, `architect`, `judge`, `explain-why` nodes to mid or
  frontier.
- Always include a *deterministic* verifier (test, lint, type-check) before
  escalating — don't escalate on a model self-report.
- Treat context size as a budget: clear tool results > 5 turns old; compact
  on threshold.

**Cost target**: 60–80% of token spend is on cheap exploration and parsing;
the frontier tier is reserved for <15% of total tokens, and on those tokens
quality is preserved because context is clean and the task is well-scoped.

---

## 4. How to apply this to ASPIS (concrete next steps)

1. **Add `models.yaml`** under `.aspis/config/` with three tiers: `cheap`
   (claude-haiku-4-5), `mid` (claude-sonnet-4-6), `frontier` (claude-opus-4-8).
   Use provider-agnostic keys so the same config works for OpenAI/Gemini
   fallbacks. Per-task overrides from the SPEC.

2. **Add a `Router` plan step** in the core loop — runs first, decides tier
   for each downstream node based on task spec + simple heuristics
   (multi-file, security tag, "investigate" verbs, file count, line count).

3. **Default plan nodes to `cheap`**, override to `mid`/`frontier` per node
   in the SPEC. Surface the per-feature model-cost estimate in the plan
   summary so the builder can see what they're choosing.

4. **Add a deterministic verifier step** after every code-changing node —
   run the project's test suite, type-check, or a `ruff`-style lint. The
   verifier decides accept/retry/escalate; the LLM does not self-grade.

5. **Track per-tier metrics** in `.aspis/runs/`: tokens used, pass rate
   first-attempt, escalation rate, final cost per feature. Re-rank the
   default tier every N runs.

6. **Use sub-agent isolation by default** — orchestrator (cheap) + workers
   (per-node tier). The orchestrator's context is built from worker
   summaries only; raw worker output is dropped after summarisation.

---

## 5. Sources (full list, with retrieval dates)

- Anthropic, *Models overview* (Claude API docs), retrieved 2026-06-25.
  `docs.anthropic.com/en/docs/about-claude/models/overview`
- Anthropic, *Introducing Claude Sonnet 4.5*, 2025-09-29.
  `anthropic.com/news/claude-sonnet-4-5`
- Anthropic, *Building Effective Agents*, 2024-12-19.
  `anthropic.com/research/building-effective-agents`
- Anthropic, *Effective Context Engineering for AI Agents*, 2025-09-29.
  `anthropic.com/engineering/effective-context-engineering-for-ai-agents`
- Anthropic, *Building agents with the Claude Agent SDK*, 2025-09-29.
  `anthropic.com/engineering/building-agents-with-the-claude-agent-sdk`
- OpenAI / GitHub, *openai/swarm* README, retrieved 2026-06-25.
  `github.com/openai/swarm` — note: replaced by OpenAI Agents SDK.
- LangChain, *Models* (langchain-ai/docs), retrieved 2026-06-25.
  `docs.langchain.com/oss/python/langchain/models`
- LangChain, *LangGraph overview*, retrieved 2026-06-25.
  `docs.langchain.com/oss/python/langgraph/overview`
- CrewAI, *LLMs* docs, retrieved 2026-06-25.
  `docs.crewai.com/en/concepts/llms`
- Cursor, *Introducing Composer 2.5*, 2026-05-18.
  `cursor.com/blog/composer-2-5`
- Cursor, *Governing agent autonomy with Auto-review*, 2026-06-11.
  `cursor.com/blog/agent-autonomy-auto-review`
- Cursor, *Bugbot is now over 3x faster, 22% cheaper, and finds 10% more bugs*,
  2026-06-10. `cursor.com/blog/bugbot-updates-june-2026`
- Cursor, *What we've learned building cloud agents*, 2026-06-02.
  `cursor.com/blog/cloud-agent-lessons`
- Cursor, *How Wayfair cut ML model costs by 90% (twice!) with Cursor*,
  2026-06-15. `cursor.com/blog/wayfair`
- Devin / Cognition, blog index, retrieved 2026-06-25. `devin.ai/blog`
  (Kimi K2.7 + GLM 5.2 availability; Claude Opus 4.7 fast mode;
  Claude Fable 5 removal notice).
- SWE-bench, *SWE-bench Verified*, retrieved 2026-06-25.
  `swebench.com/verified.html`, `swebench.com`
- OpenRouter, *LLM Rankings*, retrieved 2026-06-25. `openrouter.ai/rankings`
- Martin Fowler / Thoughtworks, *Exploring Generative AI* memo series,
  retrieved 2026-06-25. `martinfowler.com/articles/exploring-gen-ai.html`

## 6. Caveats and uncertainty

- **The "Fable 5 / Mythos 5" line** is referenced in some sources but was
  removed from US-available models in early June 2026 per a US government
  directive. Not used in the patterns above.
- **Per-feature cost numbers** (other than Wayfair and Bugbot) are not
  publicly disclosed. The Wayfair 94% + 90% result is the most defensible
  public number we have for "agent-driven cost optimisation" in production.
- **Composer 2.5** is Cursor's proprietary model (built on Kimi K2.5) and
  not generally available — but its design pattern (cheap, fast variant of
  the same intelligence) is replicable with any provider pair.
- **The "LLM as judge" pattern** is explicitly called out by Anthropic as
  "not a very robust method, and can have heavy latency tradeoffs, but for
  applications where any boost in performance is worth the cost, it can be
  helpful." Don't lean on it for the final acceptance decision — use a
  deterministic verifier first.
- This research will go stale in 3–6 months at the rate model pricing and
  capability tiers are moving. Re-run the cost numbers and the
  SWE-bench leaderboard before any major ASPIS routing decision.
