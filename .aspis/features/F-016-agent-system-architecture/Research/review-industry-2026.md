<!-- ASPIS:REFERENCE START -->
# F-016 — Industry Analysis: How the Best Agentic Coding Systems Review (June 2026)

**Author:** Research Lead
**Date:** 2026-06-25
**Status:** Primary-source research. Findings are validated against the cited
documents; opinion is marked `[R]`, multi-source verified findings `[VERIFIED]`,
single-source emerging practice `[EMERGING]`, vendor self-claim `[VENDOR]`.
**Scope:** How the best-in-class agentic coding systems (Cursor, Claude Code,
GitHub Copilot, Devin, Anthropic, OpenAI Codex, Cognition, Vercel) actually
**review** work — change review and plan review, the dimensions, the
procedures, the tools, the anti-patterns, and the role the reviewer plays.
**Audience:** the ASPIS **Reviewer** (lead), the Reviewer-adjacent skills
(`review-strategy`, `quality-review`, `acceptance-decision`, `plan-critic`),
the System Lead (when extending the review surface), and the Planning Lead
(when wiring the plan-review step into the planning pipeline).
**Bottom line up front:** in 2026, review is *not* a single LLM grade. It is a
**three-layer system**: (1) a deterministic gate (format, lint, types, tests,
scope), (2) a **fresh-context adversarial subagent reviewer** that sees the
diff + acceptance criteria, not the reasoning that produced the change, and
(3) a small **risk-tiered classifier** that decides how deep (2) needs to go.
The **safety classifier is a different role** from the **quality reviewer** —
confusing the two is the most common design mistake.

---

## §0. The seven things every ASPIS reviewer should know

1. **Fresh context is non-negotiable.** Every production system uses a reviewer
   in a fresh context (different model or subagent or session) that sees only
   the diff and the acceptance criteria, not the build trace. The reasoning
   that produced the change is *poison* for the grade. (Anthropic Claude Code
   `/code-review`, Cursor Bugbot, Anthropic *Building Effective Agents*
   evaluator-optimizer, Cognition Devin evaluator agent.) [VERIFIED]

2. **"Builder" must never grade "builder".** A reviewer is a *different* role
   with its own context, tools, and (often) model. The reviewer never sees the
   conversation that produced the change. (Cursor Bugbot, Claude Code
   `/code-review`, Cognition evaluator.) [VERIFIED]

3. **The verdict must be evidence-bound, not description-bound.** "Approve
   on description alone" is the #1 industry-wide anti-pattern. Every
   load-bearing system explicitly trains the reviewer to verify against the
   diff, the tests, the acceptance criteria — and to *withhold* the verdict
   if the evidence is missing. (Cursor Bugbot's learned rules post; Anthropic
   evaluator-optimizer "two signs of good fit".) [VERIFIED]

4. **Plan review and change review are different roles, sharing the same
   "second-opinion" pattern.** Plan-critic checks cross-artifact consistency
   and measurability (does the SPEC trace to PLAN to TASKS to acceptance?).
   Change review checks the diff against the SPEC. Anthropic, Cursor, GitHub
   Copilot, and OpenAI all converge on this two-phase model. [VERIFIED]

5. **A *safety* classifier is a different role from a *quality* reviewer.**
   Cursor's Auto-review classifier (4% block rate, 7% interrupt) is a small,
   fast, *agentic* model in the agent loop that decides "this tool call
   needs the user, this one doesn't" — informed by the *context* (file
   contents, intent, blast radius). It is *not* the bugbot / code-review
   agent. Confusing the two is the most common design mistake. [VERIFIED]

6. **The deterministic gate does most of the work.** In every surveyed
   system, the *majority* of "review" is the deterministic check (format,
   lint, type-check, test, screenshot, scope). The LLM reviewer's job is to
   catch the *judgment* failures the gate cannot catch: architectural drift,
   scope creep, missing acceptance criteria, broken user mental model, and
   "the change is correct but solves the wrong problem". The gate is the
   loop's *closer*; the reviewer is its *judge*. (Anthropic best practices;
   OpenAI harness; Cursor self-driving; Cognition evaluator.) [VERIFIED]

7. **Mode is a *depth* dial, not a *who's-the-reviewer* dial.** Every mode
   (vibe / MVP / production; Cursor Bugbot Low/Medium; GitHub Copilot
   Low/Medium; Claude Code's plan mode) tunes *how deep* the reviewer goes,
   not *whether* there is a reviewer. Vibe is still a fresh-context
   subagent reviewer — just with a narrower checklist. [VERIFIED]

---

## §1. How each system does review

### 1.1 Cursor Bugbot (separate agent in fresh context)

**What it is.** Bugbot is a *separate agent* — different model (Composer 2.5
as of June 2026), different context, different prompt — that reviews pull
requests for a Cursor-using team. It does not see the build session.

**What it checks (concrete).** From Cursor's public posts, the default
checks (Low effort — equivalent to "standard") are:

- **Correctness / bugs.** Logic errors, off-by-one, nil deref, race
  conditions. 78.13% resolution rate vs. ~47% for the next-best
  competitor (per the *Bugbot now self-improves* post, April 2026).
- **Style / consistency.** Naming, formatting, idiomatic patterns. Universal.
- **Security-sensitive patterns.** At Medium effort (and now also a
  separate Security Review agent, `/review-security`).

At Medium effort (≈ Claude Code's "more thinking" or GitHub Copilot Medium
— the "higher-reasoning model" tier), Bugbot additionally checks:

- **Cross-service / cross-file impact.** Things a single-file read misses.
- **Subtle logic in security-sensitive code.** Auth paths, input
  validation, sanitization.
- **"What's new in your PR"** (June 2026 update) — re-review is now
  incremental by default, so a small push does not re-trigger findings on
  code that was already approved.

**What it does NOT do (default).** It does not run the build. It does not
catch what a well-written test would catch. It does not check that the
change matches the SPEC (Bugbot has no SPEC by default — the PR description
and the diff are its only inputs).

**Output format.** Inline comments on the diff, organised by severity. Each
comment has file:line, the bug, and a suggested fix. Comments can be
reacted to (upvote = keep, downvote = "this was wrong"); downvotes feed
the *learned rules* loop.

**The Autofix loop (Feb 2026 → out of beta).** When Bugbot finds a bug, the
team can opt in to **Bugbot Autofix** — Bugbot spawns a *cloud agent* in
its own VM, runs the test, applies the fix, and proposes the change as a
follow-up commit on the same PR. **35% of Autofix changes are merged into
the base PR.** This is *Bugbot reading its own findings* and closing the
loop without human review of the fix — a strong signal that the reviewer
+ fix pair can run unattended when the change is local.

**The learned-rules loop (April 2026).** Bugbot ingests three signals from
every merged PR — (1) developer *reactions* to its comments, (2) developer
*replies*, (3) human-reviewer comments that Bugbot missed — and turns them
into *learned rules* that bias future reviews. 110,000 repos enabled
learning; 44,000+ rules generated. The key signal: the *false positive*
rate (downvote + reply) drives rule-tuning; the *false negative* rate
(human-reviewer-flagged issues Bugbot missed) drives new rules.

**Source.**
- https://cursor.com/blog/bugbot-updates-june-2026 (3× faster, 22%
  cheaper, 10% more bugs; incremental review; `/review` and
  `/review-bugbot`; Composer 2.5)
- https://cursor.com/blog/bugbot-learning (78.13% resolution; learned
  rules; reactions + replies + human-reviewer comments)
- https://cursor.com/blog/bugbot-autofix (35% Autofix merge rate; 52% →
  76% resolution; "agents running automatically based on an event like PR
  creation")

### 1.2 Cursor Auto-review (safety classifier — *not* a quality reviewer)

**What it is.** A small, fast, *agentic* model in the *same RPC stream* as
the parent agent that decides, *before* each tool call executes, whether
the action is "low-stakes (let it run)" or "high-stakes (interrupt the
user)". From Cursor's *Governing agent autonomy with Auto-review* post
(June 11, 2026).

**What it checks (concrete).**
- The **command** the parent agent is about to run.
- The **file contents** the command will touch (Bugbot can use Read,
  Grep, Glob, ListDir *before* deciding).
- The **declared intent** of the parent agent.
- The **blast radius** of the action (will it modify the filesystem
  outside the project? send a network request?).

**The numbers that matter.**
- 4% of actions blocked. 7% of chats lead to at least one user
  interruption. Compared to ~40% of actions blocked in enterprise
  configurations that use blanket permission gates. The Auto-review
  classifier is the *fix* for approval fatigue.
- 6,122 labelled evaluation rows (12 hours of internal sessions) +
  synthetic adversarial cases. Primary failure signal: "flapping" (a
  policy that allows 6, blocks 4 in a session is *underspecified*).
- Model: a small, fast, *agentic* classifier. Lower-reasoning models
  were not always faster; the right trade-off is a small model with
  enough reasoning to make the decision cleanly.

**Critical distinction from Bugbot.**
| Aspect | Auto-review classifier | Bugbot / quality reviewer |
|---|---|---|
| Scope | A single tool call in flight | A completed diff / PR |
| Trigger | Before *every* tool call | On PR open / push / `/review` |
| Verdict | Allow / block / interrupt | Inline comments, no verdict |
| Context | The command + file contents + intent | The diff + PR description |
| Cost | Real-time, must be fast | Minutes per PR |
| Role | Safety (the agent's blast radius) | Quality (the change's correctness) |
| Failure mode | "Flapping" (underspecified policy) | False positive / false negative |
| Fix | Re-label policy; tighten scope | Tune prompt / add learned rule |

**Conflating these is the #1 design mistake in agentic review systems.**
The ASPIS `runtime_guard` + `scope_guard` is the *deterministic* analogue
of Auto-review. The ASPIS Reviewer is the *quality-review* analogue of
Bugbot. They are not the same component. The runtime_guard is checked
on every tool call; the Reviewer is checked once per task packet.

**Source.**
- https://cursor.com/blog/agent-autonomy-auto-review (4% block; 7%
  interrupt; classifier model; same RPC stream; flapping signal)
- Anthropic — *Best practices for Claude Code* (2026): identical
  pattern under "auto mode" — "a classifier model reviews commands
  before they run, blocking scope escalation, unknown infrastructure,
  and hostile-content-driven actions"

### 1.3 Claude Code `/code-review` (subagent reviewer in fresh context)

**What it is.** A bundled skill (`/code-review`) that the user invokes or
the parent agent invokes. The skill launches a *subagent* — a separate
context with its own tools and (often) its own model — that reviews the
current diff. The subagent reports findings back to the parent.

**What it checks.** The skill is *general-purpose*; the dimensions it
checks are whatever the user (or the parent prompt) names. The standard
prompt template, from Anthropic's *Best practices*:

> *"Use a subagent to review the diff against PLAN.md. Check that every
> requirement is implemented, the listed edge cases have tests, and
> nothing outside the task's scope changed. Report gaps, not style
> preferences."*

The dimensions, named:

- **Correctness vs. acceptance criteria** — every SPEC requirement
  implemented? Every test for a stated edge case present?
- **Scope compliance** — anything outside the task's scope changed?
- **Edge case coverage** — the listed edge cases have tests?

**The Writer/Reviewer pattern.** Anthropic's canonical pattern is two
parallel sessions:

| Session A (Writer) | Session B (Reviewer) |
|---|---|
| `Implement a rate limiter for our API endpoints` | |
| | `Review the rate limiter implementation in @src/middleware/rateLimiter.ts. Look for edge cases, race conditions, and consistency with our existing middleware patterns.` |
| `Here's the review feedback: [Session B output]. Address these issues.` | |

The two sessions are *separate* — they do not share context. The
Writer's "I'm done" is not the Reviewer's "I'm done". The Reviewer can
also be used the other way (Writer writes tests, Reviewer writes the
code to pass them).

**A critical caveat from Anthropic's docs (often missed):**

> *"A reviewer prompted to find gaps will usually report some, even
> when the work is sound, because that is what it was asked to do.
> Chasing every finding leads to over-engineering: extra abstraction
> layers, defensive code, and tests for cases that can't happen. Tell
> the reviewer to flag only gaps that affect correctness or the stated
> requirements, and treat the rest as optional."*

This is the single most important caveat in the entire review
literature. **The reviewer is biased toward finding problems** (because
that's what it was asked to do). The prompt must *constrain* the
reviewer to *correctness* and *stated requirements* — not style, not
"this could be cleaner", not "I'd add a test for X". ASPIS's
"verdict = specific finding + why it matters + severity + file:line" is
exactly this constraint.

**Source.**
- https://code.claude.com/docs/en/best-practices (Writer/Reviewer
  pattern; subagent in fresh context; the "chase every finding" caveat)
- https://www.anthropic.com/research/building-effective-agents
  (evaluator-optimizer workflow; "two signs of good fit: LLM responses
  demonstrably improved by human feedback, and the LLM can provide
  such feedback")

### 1.4 GitHub Copilot code review (Low / Medium effort)

**What it is.** An automatic reviewer on every PR (when enabled), with
two effort levels. As of June 2026, GitHub has the most *graduated*
effort model in the industry.

**Low effort (default).** Per docs.github.com (verified 2026-06-25):

> *"Standard review. Provides fast, targeted feedback on common issues
> such as bugs, security vulnerabilities, and style inconsistencies."*

In practice, Low is:

- **Common bugs.** Null deref, off-by-one, typo'd variable, missed
  return value, missed error handling.
- **Common security patterns.** Hard-coded secrets, obvious SQL
  injection, XSS.
- **Style inconsistencies.** Diff-vs-baseline formatting, lint errors.

**Medium effort (preview).** Per docs.github.com:

> *"Routes pull requests to a higher-reasoning model for longer
> analysis of complex logic, security-sensitive code, and cross-service
> changes. Medium reviews use more AI credits and GitHub Actions
> minutes than Low reviews."*

In practice, Medium adds:

- **Cross-service / cross-file reasoning.** "This change to `auth.ts`
  breaks `auth-consumer.ts`'s assumption about error shape."
- **Deeper security review.** Auth flow, input validation, access
  control, cryptography use.
- **Logic in complex code.** Recursive functions, state machines,
  race conditions.

**Mode is a repo-level dial (not per-PR by default).** Repository
administrators set the default effort level. Per-PR override is
manual. The setting is governed by a Copilot policy in the org.

**Agentic capabilities (always on).**
- **Full project context gathering.** The reviewer reads the *entire*
  repo, not just the diff. Runs on GitHub Actions (standard runners
  by default; larger runners for Medium; self-hosted for free).
- **Pass suggestions to Copilot cloud agent.** A Medium finding can
  be turned into a follow-up PR by the cloud agent. (Public preview.)
- **MCP server access** (preview). The reviewer can read from
  third-party systems (issue trackers, documentation, service
  catalogs, incident tooling) when the PR description references
  them.

**Excluded files (always).** `package.json`, `Gemfile.lock`, log
files, SVG files. Dependency / asset files are not reviewed.

**Source.**
- https://docs.github.com/en/copilot/concepts/agents/code-review
  (Low / Medium effort; agentic capabilities; MCP; review
  exclusions; "model switching is not supported")
- The base number 46.69% resolution rate (vs Cursor Bugbot's 78.13%)
  comes from Cursor's *Bugbot now self-improves* post, April 2026.

### 1.5 Cognition Devin — evaluator agent (typed criteria)

**What it is.** A *separate model* with the *same tools* as the
implementing agent (shell, browser, code editing) that judges the
deliverable against **typed criteria** — natural-language specifications
that are concrete enough to verify (e.g., "does the dashboard have
more than 5 graphs?"), and that check the deliverable's behaviour
*directly*, not its code.

**How it evaluates (concrete — from the grafana-dashboard-metrics
example, September 2024).** The evaluator agent:

1. Logs into the *running* Grafana instance the building agent created.
2. Verifies the dashboard loads.
3. Checks specific properties:
   - "Does it contain more than 5 graphs?"
   - "Is there a line graph 'Average Queue Time by Pod (microseconds)'?"
   - "Is there a gauge titled 'GPU Power Total' showing a number
     within 10% of 170 kW?"
4. Reads the Prometheus config file and verifies it is consuming from
   the right URL.
5. Reads the Prometheus logs and verifies successful ingestion.
6. Accumulates a 0.0–1.0 score across criteria.

**Why typed criteria matter.** The criteria are not "is the code
clean?" — they are *observable, end-state properties* of the running
system. "The dashboard shows 5+ graphs" is verifiable in 3 tool calls
(browse, count, log). "The code is well-organized" is a judgment
that cannot be verified.

**The number that matters.** 74.2% on `cognition-golden` (the
internal benchmark), autonomous, without ever seeing the eval tasks
during training. The same process drives automated data generation
for further fine-tuning.

**The model of the evaluator matters.** The evaluator must be able
to:
- Run shell commands and read their output.
- Read files and grep them.
- Use the browser to navigate the running app.
- Reason about tool outputs in fresh context.
This is a *full agent* with its own context, not a single LLM
prompt.

**Source.**
- https://www.cognition.ai/blog/evaluating-coding-agents (the
  grafana-dashboard-metrics example; "evaluating the evaluators";
  74.2% on cognition-golden; precision/recall on ground truth)
- https://www.cognition.ai/blog/evaluating-coding-agents — also
  documents the "interactive self-reflection" property: a sufficiently
  capable agent can evaluate its own work using environment signals
  without human feedback.

### 1.6 OpenAI Codex (harness) — agent-to-agent review

**What it is.** Codex opens a PR and "iterates until all agent
reviewers are satisfied." Multiple agents (in the harness — typically
one or two specialised sub-agents, plus Codex itself) review the diff.

**What it checks (concrete).** The harness does not publish
dimension lists, but the *behaviour* is well-documented:
- **Linter / type-check / unit test** (deterministic gate; same as
  every other system).
- **Cross-file consistency** (sub-agent reads related files, flags
  inconsistencies the diff introduces).
- **Acceptance criteria from the issue body** (the spec lives in
  the GitHub issue; the reviewer checks the diff against it).
- **Self-review** is *allowed* (Codex reviews its own changes
  locally) but is *augmented* by independent sub-agent reviews
  (local + cloud). The harness explicitly calls out "all agent
  reviewers are satisfied" as the close condition, not "Codex said
  it's done".

**Output format.** PR comments; commits back to the same branch
when issues are found; the agent responds to comments autonomously.

**Source.**
- OpenAI, *Harness engineering* (Lopopolo, 2026-02-11) — the
  Codex loop, 3.5 PRs per engineer per day, 1,500 PRs in 5 months,
  0 manually-written lines.

### 1.7 Anthropic (multi-agent research) — evaluator-optimizer pattern

**What it is.** The "evaluator-optimizer" workflow (Anthropic,
*Building Effective Agents*, December 2024): one LLM call generates
a response while another provides evaluation and feedback in a loop.

**The two signs of good fit** (Anthropic, verbatim):

> *"This workflow is particularly effective when we have clear
> evaluation criteria, and when iterative refinement provides
> measurable value. The two signs of good fit are, first, that
> LLM responses can be demonstrably improved when a human articulates
> their feedback; and second, that the LLM can provide such feedback."*

The "second sign" is the load-bearing one for ASPIS: **the
reviewer must be capable of providing the same feedback a human
would.** If the reviewer's bar is lower than the human bar, the
loop produces worse output than a human-in-the-loop would. The
current ASPIS reviewer is on the `deep` model tier; this is the
right default.

**Critical caveat (often missed).** Anthropic's *Multi-agent
Research* post (June 2025) reports that multi-agent systems burn
~15× the tokens of single-agent chat. **Reviewers that are too
deep or too chatty** are the same anti-pattern. The reviewer's
verdict should be terse: a list of findings, each with file:line,
what's wrong, why it matters, severity, and a suggested fix. The
parent agent reads the verdict and fixes — the verdict is not
narrative prose.

**Source.**
- https://www.anthropic.com/research/building-effective-agents
  (evaluator-optimizer; the two signs of good fit)
- https://www.anthropic.com/engineering/multi-agent-research-system
  (15× token cost of multi-agent; token-usage explains 80% of
  variance)

### 1.8 Vercel v0 / Replit Agent 4 — preview-as-evaluator

**What it is.** Vercel v0 generates a real-time preview for every
code change; the preview *is* the evaluation surface. Replit Agent
4 does the same on a design canvas.

**How it differs from the others.** The reviewer is *not an LLM at
all* — it's a *visual + behavioural check* against the running app.
For UI work, the deterministic check is "does the rendered page
match the design at the specified breakpoints" — a screenshot diff.
For backend work, it's "does the deployed endpoint return the
expected response". The LLM reviewer is reserved for the cases
the visual check can't catch (architecture, naming, scope).

**ASPIS applicability.** ASPIS is a file-first, deterministic
factory. The "preview-as-evaluator" pattern is *not* directly
applicable to ASPIS's own development. But it is a *useful pattern
to recommend* to users of ASPIS for whom it makes sense
(front-end / full-stack features). The generalisation: *the
reviewer's evidence should be observable behaviour, not source
code*.

**Source.**
- https://vercel.com/docs (v0 — real-time preview as evaluation)
- https://replit.com/agent4 (Agent 4 — design canvas + concurrent
  forks)

---

## §2. What makes review effective (proven patterns)

The patterns below are observed in *all* surveyed systems. ASPIS
already has most of them.

### 2.1 Fresh context — non-negotiable

> *"A reviewer running in a fresh subagent context sees only the
> diff and the criteria you give it, not the reasoning that
> produced the change, so it evaluates the result on its own
> terms."* — Anthropic, *Best practices for Claude Code* (2026)

The reviewer must not see the build trace. The reasoning that
produced a change is full of "yes-but" arguments that bias the
reviewer toward approval. The *diff* is the only honest evidence.

**ASPIS today.** The reviewer is a separate subagent (`mode:
subagent`); it has its own context. The build-lead is documented
to hand the reviewer the diff + the SPEC + the acceptance criteria,
not the build session. **The build-lead → reviewer reachability
gap is a known issue** (D-build-lead-1); the existing review
template (`templates/review/review.md`) is filled by the reviewer
in its own context, which is the right shape.

**ASPIS should add.**
- A `reviewer-context` template that lists exactly what the
  reviewer sees: (diff, SPEC, PLAN, TASKS, acceptance criteria,
  constitution checks for `enforced_by: review`). The reviewer
  should never be handed a *narrative* of the build.

### 2.2 Adversarial stance — assume every change has issues

> *"Tell the reviewer to flag only gaps that affect correctness or
> the stated requirements, and treat the rest as optional."* —
> Anthropic

The reviewer is *primed* to find problems. That's the role. But
the *kind* of problem the reviewer looks for must be constrained:
*correctness + stated requirements*, not *style + opinions*.

**ASPIS today.** The reviewer's role (`agents/review/reviewer.md`,
verified) says:

> *"Stay independent — never review your own work or rubber-stamp
> a lead's claim."*

It does not say "find correctness gaps, not style nits." This is
the Anthropic caveat spelled out. **ASPIS should add the
constraint** to the reviewer body (or to `quality-review` skill
when it is written).

### 2.3 Specific findings — file:line, what's wrong, why it matters, severity

Every load-bearing system uses a finding table. ASPIS already has
this shape (`templates/review/review.md`):

```
| Severity | Where | Finding | Suggested fix |
|----------|-------|---------|---------------|
| <sev>    | <file:line> | <what's wrong> | <how to fix> |
```

**The fields are not optional.** "Severity" lets the parent agent
triage (high/medium/low — the build lead fixes high first, may
defer low). "Where" is the file:line (or the spec criterion
that is violated). "Finding" is the gap. "Suggested fix" is
optional (the parent agent may propose alternatives).

### 2.4 No self-review — the builder never grades its own work

Every system rejects the idea that the same session reviews its
own work. Cursor Bugbot is a *different agent in a different
context*. Claude Code's `/code-review` runs in a *fresh subagent*.
Cognition's evaluator is a *separate model with the same tools*.
Devin (production) uses *agent-to-agent* review.

**ASPIS today.** This is enforced by *role separation* and by the
reviewer's `mode: subagent` (so it cannot be invoked from inside
itself). The build-lead is the only agent that drives the build;
the reviewer is the only agent that delivers the verdict; the
committer is the only agent that commits. R-004 (one writer) +
R-006 (thin agents, single source) reinforce this.

**ASPIS should add.** A `reviewer-routing` rule: the reviewer
receives the diff and the SPEC and the acceptance criteria. The
reviewer *never* receives a "build report" or a narrative summary
of how the change was made. (The build report may *exist*; the
reviewer just doesn't read it.)

### 2.5 Evidence-based — approve on evidence, not description

> *"Have Claude show evidence rather than asserting success: the
> test output, the command it ran and what it returned, or a
> screenshot of the result."* — Anthropic

> *"Verifying against evidence (the diff, the tests, the
> acceptance criteria); don't approve on description alone. If
> you lack the evidence to judge, request it and withhold the
> verdict — never approve on a guess."* — ASPIS reviewer body
> (verified)

ASPIS already has this rule. It is the single most important rule
the reviewer owns.

**What "evidence" looks like in practice.**
- The diff itself (the file:line table).
- The test report (the gate output).
- The acceptance criteria checklist (each FR-### / SC-### ticked
  or not).
- For "the change matches the SPEC": the SPEC's text quoted
  alongside the diff's relevant line.
- For "the change is in scope": the task packet's `scope.allowed`
  vs. the diff's file list.

### 2.6 Depth matched to risk — not every change needs the same scrutiny

This is the **mode dial** pattern (§3 below). The reviewer
*scales* depth from the change's risk, complexity, and mode:

| Mode | Diff size | Risk class | Reviewer depth |
|---|---|---|---|
| vibe | 1-3 files, typo / rename | trivial | light pass — runs, in scope, no obvious breakage |
| mvp | 1-5 files, single concern | contained | standard — correctness, scope, basic security |
| production | multi-file, security-sensitive, cross-service | high | full — every acceptance criterion, multi-lens, learned rules |

**ASPIS today.** `modes.yaml` (verified) declares
`build_review: light | standard | full` per mode. The
`review-strategy` skill (referenced but not yet written) is the
mechanism that picks the depth.

**ASPIS should add.** A `reviewer-routing` table that maps
diff-size × mode × scope-flag to a review depth. The reviewer
reads the diff stats + the mode and picks the depth; the parent
agent does not need to ask.

### 2.7 Verdict is binding — reviewer's "reject" stops the feature

Every system makes the verdict *binding*: the build does not
proceed without an approve. ASPIS already has this — the
reviewer's verdict is the gate. R-004 (one writer) means the
committer does not commit without the verdict.

**The 4-outcome verdict** (ASPIS):
- **approved** — accept the change, commit.
- **approved-with-notes** — accept the change, but the parent
  agent must address the notes in a follow-up (do not block).
- **changes-required** — return to the builder; the parent
  agent re-delegates the task with the verdict as input.
- **rejected** — return to the builder; the change is so wrong
  it must be re-thought (rare; usually a sign the spec was
  wrong, not the build).

The 4-outcome shape is the same as Cursor Bugbot's upvote/downvote
+ human-comment flow (collapsed to 4 verdicts for the parent
agent's API).

### 2.8 Other proven patterns

- **Reviewer can read the *whole repo* (project context).** GitHub
  Copilot code review at any effort has full project context
  gathering (run on GitHub Actions). The reviewer is not limited
  to the diff; it can read the relevant files. (Verified at
  docs.github.com.) ASPIS reviewer is read-only; it can already
  grep + read across the project.
- **Reviewer can use MCP / tools.** GitHub Copilot's Medium-effort
  reviewer can use the GitHub MCP server and Playwright MCP
  server. ASPIS reviewer is denied `webfetch` / `websearch` by
  design (R-006 / least-privilege) — but the *general* principle
  (the reviewer is an agent, not a single prompt) holds.
- **The reviewer can propose the fix.** Cursor Bugbot's Autofix
  spawns a *cloud agent* that applies the fix. ASPIS does not
  do this today; the reviewer's verdict is read-only, and the
  parent agent (build-lead) routes the fix. This is a
  deliberate design choice — the reviewer never modifies the
  work, by R-004 + R-006. The trade-off is that *fix latency* is
  higher (build-lead has to delegate, not just apply); the
  benefit is *no review-bias* in the fix.

---

## §3. The 9 review dimensions — industry alignment

ASPIS's current reviewer body names 9 dimensions
(`src/aspis/data/catalog/agents/reviewer.md`, verified 2026-06-25):

> *"Evaluate the dimensions that matter for this change:
> correctness, scope compliance, architecture, maintainability,
> reliability, security, performance, standards, and documentation."*

The table below aligns each dimension with (a) the industry
consensus on who checks it, (b) whether the check is
deterministic (script, lint, test) or judgment (LLM), and (c)
the right depth per mode.

| # | Dimension | Industry check | Owner (industry) | Deterministic or judgment | Vibe | MVP | Production |
|---|---|---|---|---|---|---|---|
| 1 | **Correctness** | Bugbot (default), Claude Code `/code-review` (default), Copilot Low/Medium, Devin evaluator | Quality reviewer (fresh-context subagent) | Mostly judgment; tests are the deterministic sidecar | light (runs + obvious logic) | standard (acceptance criteria, edge cases) | full (every AC + edge case + concurrency) |
| 2 | **Scope compliance** | OpenAI harness (issue body), Copilot (auto on every PR), all subagent review | Quality reviewer; commit-reviewer subagent as second-line | Mostly deterministic (file list vs. `scope.allowed`) | skip (single-file implicit scope) | standard (file list + task packet scope) | full (also: spec-level scope; no architectural drift) |
| 3 | **Architecture** | Cursor self-driving, Cognition evaluator, Anthropic evaluator-optimizer | Quality reviewer (or dedicated architecture-reviewer at scale) | Mostly judgment | skip | note (does it fit the as-built architecture) | full (does it match `ARCHITECTURE.md`; would a fresh subagent recognise the patterns?) |
| 4 | **Maintainability** | Bugbot (style), Copilot Low (style) | Quality reviewer; linter for the sidecar | Mixed (lint is deterministic; "is this readable" is judgment) | skip | standard (lint passes; no obvious code-smell) | full (every file opens with purpose; no dead code; no speculative generality) |
| 5 | **Reliability** | Bugbot (race conditions at Medium), Claude Code (edge cases) | Quality reviewer; test report for the deterministic sidecar | Mostly judgment; tests are the sidecar | skip | standard (error paths; happy path tests) | full (failure modes; retries; timeouts; observability hooks) |
| 6 | **Security** | Bugbot / Security Review (separate agent), Copilot (security-sensitive at Medium), Amazon Q Developer scanning, CodeQL | Dedicated security-reviewer (subagent) at scale; quality reviewer covers the obvious cases | Mixed (CodeQL / Dependabot is deterministic; business-logic security is judgment) | skip (single-file / throwaway) | standard (OWASP top-10, secrets, input validation) | full (separate security-reviewer; CVE scan; threat model) |
| 7 | **Performance** | Cognition evaluator (load time, throughput), OpenAI harness (log/metric queries) | Quality reviewer; observability hook for the sidecar | Mostly judgment; benchmarks are the sidecar | skip | skip (unless the task is perf-critical) | standard (no N²; no obvious allocations in hot loops) |
| 8 | **Standards** | Linter (deterministic), Bugbot (style consistency) | Linter (deterministic); quality reviewer for the non-lintable cases | Mostly deterministic (lint, format, type-check) | gate only (lint + format pass) | standard (lint + format + type-check + project rules) | full (+ constitution checks C-COST, C-NO-SPECIAL-CASE, etc.) |
| 9 | **Documentation** | OpenAI harness (docs are first-class), Claude Code (AGENTS.md updates) | Quality reviewer; doc-gardening agent for the sidecar | Mixed (lint is deterministic; "is this useful" is judgment) | none (vibe is throwaway) | minimal (only the files that changed; a one-line note if anything surprising) | complete (every public API documented; README updated; AGENTS.md current) |

**Industry observations.**

- **Standards is the most deterministically-checkable dimension.**
  Every system runs lint/format/type-check first. The reviewer's
  job is *what the linter can't catch* (e.g., "the function is
  named correctly but does the wrong thing").
- **Security scales with risk.** Vibe-mode security review is
  effectively nil; production-mode security review has a
  *dedicated subagent* (Cursor's Security Review, ASPIS's
  `security-reviewer` leaf). The threshold is a `risk-class`
  flag, not the mode alone.
- **Architecture and documentation are the dimensions most
  likely to be skipped.** They are the dimensions most
  *expensive* to evaluate (require reading the SPEC, the PLAN,
  and the as-built architecture) and the dimensions most
  *likely to be missed* by a single-LLM reviewer. Production
  mode is the only mode where they are checked end-to-end.
- **Reliability and performance are correlated.** A change that
  breaks reliability usually breaks performance (or vice
  versa). The two should be checked together in production
  mode, not separately.
- **The 9 ASPIS dimensions are the industry consensus.** Every
  surveyed system has the same shape, with slight
  re-naming. ASPIS is well-aligned.

**Deterministic-vs-judgment split (the right shape).**

For each dimension, the deterministic check is the *floor* and
the LLM review is the *ceiling*:

```
[deterministic gate]  →  [LLM review]  →  [human spot-check]
   floor                    ceiling         optional, sampling
```

- The deterministic gate catches the *common* failure modes
  (lint, format, type, test).
- The LLM reviewer catches the *judgment* failure modes
  (architecture, scope creep, missing AC, "solves the wrong
  problem").
- The human spot-check is *optional* — used for security-
  sensitive or novel-domain work, not for every change.

ASPIS already has the deterministic floor (R-002 / gates).
ASPIS has the LLM ceiling (the Reviewer). The human spot-check
is R-008 (human gate) and is reserved for architecture /
rules / permissions / security posture.

---

## §4. Plan review vs change review

### 4.1 Plan review (plan-critic)

**What it is.** A review of the *plan artifacts* (SPEC, PLAN,
TASKS) before any code is written. The reviewer checks
*cross-artifact consistency* and *measurability* — does the
SPEC trace to the PLAN to the TASKS to the acceptance
criteria? Is every requirement testable? Is anything
orphaned, unverifiable, or vague?

**What it checks (industry).** The plan-critic is a *fresh-
context subagent* (same pattern as change review) that reads:

- SPEC.md → all FR-### / SC-### listed.
- PLAN.md → every architectural choice justified.
- TASKS.md → every task scoped, every dependency listed.
- ACCEPTANCE.md → every FR/SC traced to a test or demo.
- The cross-references — every SPEC item appears in the
  PLAN; every PLAN item appears in the TASKS; every TASK
  appears in ACCEPTANCE.

**The judgment dimensions.**
- *Measurability.* "Fast" is not measurable; "<100ms p95
  on the auth endpoint" is. "Easy to use" is not
  measurable; "user completes the task in <3 clicks" is.
- *Traceability.* Every requirement has a test, a
  scenario, or a clear owner. No orphans.
- *Scope.* The plan solves the stated problem; the
  TASKS are the smallest set that solves it; nothing
  speculative.
- *Risk.* The plan names the risks (technical, schedule,
  dependency) and either mitigates them or surfaces
  them.

**What it does NOT do.** Plan-critic does not *improve* the
plan — it does not write the spec. It reports gaps. The
planner takes the gaps and fixes them. (Same as change
review: the reviewer reports gaps; the builder fixes them.)

**Industry adoption.** Every system has plan review:
- **Anthropic Claude Code plan mode** is itself a kind
  of plan review — the user reviews the plan before the
  agent implements.
- **GitHub Copilot** uses the issue body as the spec;
  the agent's research→plan→implement pipeline produces
  a plan the user can review.
- **OpenAI Codex** uses the issue body + the harness's
  plan-output as the spec; the user can re-direct.
- **Devin** presents the plan at the start of the
  session; the user can re-direct.
- **Cognition's own** *How Cognition Uses Devin to Build
  Devin* (Feb 2026) — Devin plans; the human reviews;
  Devin implements.

**ASPIS today.** `plan-critic` is referenced in the
reviewer body (line 35, verified) and in the
`planning-lead` skill list. **It is not yet written.**
This is a real gap in the current catalog.

**ASPIS should add.** A `plan-critic` skill (referenced
in `agents/review/reviewer.md` line 90) that:
- Loads the SPEC, PLAN, TASKS, ACCEPTANCE for the
  active feature.
- Checks every FR/SC has a corresponding AC.
- Checks every AC is measurable.
- Checks every TASK has a defined scope, dependency,
  and acceptance.
- Returns findings as the standard finding table
  (severity, where, what's wrong, suggested fix).

The current ASPIS workflow has a `plan-critic` step
implicit in P8 (Analyzes/Review) of the planning
pipeline, but no skill implements it. This is the
highest-value single addition to the review surface.

### 4.2 Change review (quality-review)

**What it is.** A review of the *diff* (the file:line
changes) against the SPEC's acceptance criteria and the
project's rules. The reviewer is a fresh-context
subagent; the verdict is binding.

**What it checks (industry).** Already detailed in
§1 and §2. The dimensions are the 9 from §3, scaled
to the mode.

**ASPIS today.** `quality-review` is referenced in
the reviewer body (line 33, verified) and in the
review command. **It is not yet written.** The
reviewer is currently using inline judgement without
a structured checklist. This is a real gap.

**ASPIS should add.** A `quality-review` skill
(referenced in `agents/review/reviewer.md` line 92)
that:
- Loads the diff and the task packet.
- Loads the SPEC's FR-### / SC-### the task packet
  claims to satisfy.
- Walks the 9 dimensions (mode-scaled per §3).
- Returns findings as the standard finding table.
- Returns the verdict (approved / approved-with-
  notes / changes-required / rejected).

The two skills — `plan-critic` and `quality-review` —
are the *content* of the review surface. They are
referenced but not yet authored. Writing them is the
*most leveraged* change in the review surface.

### 4.3 The two together — when each fires

| When | Reviewer is | Verdict lands in |
|---|---|---|
| After P8 (Analyzes/Review), before P9 (Approve) | plan-critic | The plan is ready to ship to build, or returns to planner. |
| After a build-lead gate passes, before committer | quality-review (subagent) or Reviewer lead (high-risk) | The change is ready to ship to commit, or returns to builder. |
| At feature close (ACCEPTANCE check) | quality-review at the feature level | The feature is accepted, or returns to fix-lead. |
| At rule / architecture / security changes | R-008 human gate | A human decides. |

The plan-critic and the quality-review *share* the
finding table format and the verdict vocabulary. They
differ in *input* (artifacts vs. diff) and *depth*
(more at plan-time, scoped at change-time).

---

## §5. Review tools and skills

### 5.1 Review-specific tools in the market

- **Static analysis** — the universal floor. Linters
  (ruff, eslint, golangci-lint), formatters (black,
  prettier), type-checkers (mypy, tsc), and
  security linters (CodeQL, Bandit, Semgrep). The
  reviewer's job is to *trust* the linter and focus
  on the judgment dimensions.
- **Security scanning** — CodeQL (GitHub Advanced
  Security), Dependabot, Snyk, Amazon Q Developer
  security scanning. The reviewer delegates to
  these and reads their output.
- **Test coverage** — coverage.py, istanbul. The
  reviewer checks that new code has tests and the
  change does not drop overall coverage.
- **Diff-aware tools** — Cursor Bugbot, GitHub
  Copilot code review, Claude Code `/code-review`,
  CodeRabbit, Greptile, Sourcery, Codacy. All
  read the PR diff and produce inline comments.
- **Behavior / preview tools** — Vercel v0's
  preview, Replit's design canvas, the Chrome
  DevTools MCP for headless visual diffs. The
  reviewer can drive the running app and check
  the result.
- **Trace / log tools** — Cursor cloud agents
  query `LogQL` / `PromQL`; OpenAI Codex reads
  the same. The reviewer can query "what did
  the build do in production?" via the same
  tools.

### 5.2 Linter-as-reviewer — the deterministic floor

The linter is the *first* reviewer. It is the
*cheapest* reviewer. The LLM reviewer's job starts
where the linter's job ends.

**ASPIS today.** `.aspis/gates.yaml` is the
deterministic floor (`ruff check`, `ruff format
--check`, `mypy`, `pytest -n auto -m "not perf"`,
`pytest -q -m perf -p no:xdist` per the *old-
asps* deep analysis, §5). R-002 is "gates first".
This is the right shape.

### 5.3 The right split between deterministic and LLM review

| Layer | What it catches | Cost | When |
|---|---|---|---|
| **Linter** | Syntax, style, type errors, common bugs | Trivial | Every edit (pre-commit or in-CI) |
| **Tests** | Functional regressions, broken AC | Cheap (1-10s) | Every build |
| **Security scanner** | CVE, secrets, common injection | Cheap | Every build |
| **Coverage** | Missing tests for new code | Cheap | Every build |
| **Subagent reviewer (quality-review)** | Architecture, scope creep, missing AC, "solves the wrong problem" | ~30s–2min, deep model | Per task packet (post-build, pre-commit) |
| **Subagent reviewer (plan-critic)** | Measurability, traceability, scope, risk | ~1min, deep model | Once per feature (post-planning, pre-build) |
| **Dedicated security-reviewer** | Threat model, auth, cryptography, business-logic security | ~1min, deep model | Production-mode security-sensitive changes |
| **Human spot-check (R-008)** | Architecture, rules, model routing, security posture, novel domain | Minutes-hours | Rule changes; new architecture; novel domain |

**The split is intentional.** The deterministic
floor handles ~80% of the failures cheaply. The LLM
ceiling handles the remaining ~20% — the judgment
failures. The human spot-check is reserved for the
*constitutional* changes (R-008).

**Anti-pattern to avoid.** Adding more LLM review
layers does not help. Cursor's 4% Auto-review
block rate is the *evidence*: most actions do
not need a classifier; a deterministic scope
guard catches most of the rest. The LLM
reviewer's job is to be a *judge*, not a
*gatekeeper*.

### 5.4 Review-specific skills to add to ASPIS

The reviewer body references 5 skills (`agents/
review/reviewer.md` lines 30-35, verified):

| Skill | Status | Purpose |
|---|---|---|
| `context-ladder` | exists | Read only the context the change touches. |
| `review-strategy` | **not written** | Pick the depth and the dimensions from mode + risk. |
| `quality-review` | **not written** | Walk the 9 dimensions; produce findings. |
| `acceptance-decision` | **not written** | Render the verdict; route the follow-up. |
| `plan-critic` | **not written** | Cross-artifact consistency + measurability. |

**Plus, the catalog should consider (out of the
5 above):**

- A `reviewer-context` template — the exact
  list of what the reviewer sees (diff, SPEC,
  PLAN, TASKS, AC, constitution checks). What
  the reviewer *does not* see (the build
  trace) is as important as what it does.
- A `constitution-checks` skill (referenced in
  the reviewer body, line 77) that walks the
  11 constitution checks the reviewer owns
  (C-COST, C-LOCAL-CHANGE, C-SINGLE-SOURCE,
  C-CONFIG-OVER-CODE, C-NO-SPECIAL-CASE,
  C-DISCOVERY, C-FILE-SELF-EXPLAINS,
  C-TESTABLE, C-PORTABLE — 9 of the 11
  per `constitution-checks.yaml`).
- An `evidence` helper — a small script that
  produces the evidence bundle for the
  reviewer (diff, test report, scope report,
  acceptance checklist) so the reviewer does
  not have to gather it itself.

---

## §6. Review anti-patterns

These are the **proven** anti-patterns from the
industry. ASPIS already rejects most of them; the
remaining ones are listed for completeness and
self-check.

### 6.1 Self-review (builder grading own work)

> *"The longer Claude works unattended, the more an
> independent check matters before you count the
> work as done."* — Anthropic

**Failure mode.** The builder has a narrative
("I implemented it carefully; it should work")
that biases it toward approval. The reviewer in
the same context inherits that bias.

**Industry evidence.** Every surveyed system
rejects this. Cursor Bugbot is a different
agent. Claude Code's `/code-review` is a fresh
subagent. Cognition's evaluator is a different
model. Devin (production) uses agent-to-agent
review.

**ASPIS today.** Enforced by role separation
(reviewer is `mode: subagent`; build-lead is
`mode: subagent`; they are separate agents with
separate contexts). The reviewer's body
explicitly says "stay independent — never review
your own work." R-004 + R-006 reinforce.

### 6.2 Rubber-stamping (approving without reading)

**Failure mode.** The reviewer is on the same
context as the builder; the builder says "I'm
done"; the reviewer says "looks good". The
verdict is meaningless.

**Industry evidence.** Cursor's learned-rules
post (April 2026) treats *false positives*
(downvotes) and *false negatives* (human
reviewer comments Bugbot missed) as the two
signals that drive the reviewer. The metric is
*resolution rate* (% of Bugbot comments that
get acted on before merge) — 78.13% for
Bugbot, 46.69% for the next-best. The
*resolution rate* is the antidote to rubber-
stamping: a comment that nobody acts on is
either noise or unclear; either way, it is
feedback that the reviewer is wrong.

**ASPIS today.** The reviewer must produce
*specific findings* (file:line, what's wrong,
severity). A rubber-stamped verdict is one
with no findings — easy to detect in the
trace.

**ASPIS should add.** A `findings-count`
trace event; the post-commit trace analysis
flags verdicts with zero findings as a
"reviewer may have rubber-stamped" signal.

### 6.3 Reviewing everything at the same depth

**Failure mode.** Production-mode review on a
typo is over-engineering. Vibe-mode review on a
security-sensitive change is negligence. The
depth is wrong on both ends.

**Industry evidence.** Every system dials depth.
GitHub Copilot Low vs Medium. Cursor Bugbot
default vs. "more review". Anthropic /goal vs.
Stop hook vs. subagent review. ASPIS's mode
dial (vibe / MVP / production).

**ASPIS today.** `modes.yaml` has the
`build_review: light | standard | full` knob.
The `review-strategy` skill (referenced, not
written) is the mechanism.

**ASPIS should add.** A `review-strategy`
skill that *picks* the depth from the diff
size + the mode + the risk class (security-
sensitive, cross-service, novel-domain, etc.).

### 6.4 Reviewing without evidence

**Failure mode.** "The code looks right" is
not a verdict. The verdict must be bound to
the evidence — the diff, the tests, the
acceptance criteria.

**Industry evidence.** Anthropic's
"evaluator-optimizer" is explicit: "the
two signs of good fit are, first, that
LLM responses can be demonstrably improved
when a human articulates their feedback;
and second, that the LLM can provide such
feedback." A reviewer that can't explain
*what's wrong* is not a reviewer; it's a
generator.

**ASPIS today.** Enforced by the review
template (severity, where, finding, fix).
The reviewer's body says "verify against
evidence".

**ASPIS should add.** A "no evidence = no
verdict" rule (the reviewer body refers to
this; the reviewer body should state it
explicitly). A reviewer that has no diff,
no test report, and no acceptance
checklist is required to *request* them
and *withhold* the verdict.

### 6.5 Review bottleneck (one reviewer gating all work)

**Failure mode.** A single global integrator
or single human reviewer is a bottleneck.
The work piles up; the reviewer's quality
drops (rubber-stamping); the work moves
slowly.

**Industry evidence.** Cursor explicitly
*removed* the integrator from the
multi-agent path (per the *Towards self-
driving codebases* post): "It quickly became
an obvious bottleneck... we tried prompt
changes, but ultimately decided it was
unnecessary and could be removed to simplify
the system." The fix: *quality is
distributed*. Each task packet has its own
review; the review happens in parallel with
the build; the review is not a single
global gate.

**ASPIS today.** Per-task review (each task
packet has its own verdict) is the design.
The Reviewer is one agent, but the
*verdict* is per-task, not per-feature. The
Reviewer is the committer (per ASPIS
design, "the reviewer is the committer"
rule — the verdict and the commit share
one brain) — this is *fused* responsibility,
not bottleneck.

**Caveat.** "The reviewer is the committer"
is *not* an industry-standard pattern; most
systems keep the reviewer and the committer
separate. ASPIS's choice to fuse them is a
deliberate trade-off (faster cycle, single
owner) at the cost of the reviewer's
independence. **This is the single most
important design choice to revisit.** If
the user / the project lead has evidence
that the reviewer's verdicts are biased
toward approval (because the reviewer
*also* has to commit), the rule should
change. See §7.

### 6.6 Approval fatigue (the Auto-review failure mode)

**Failure mode.** The reviewer (or human) is
asked to approve too many things. They click
"approve" without reading. The review is
noise.

**Industry evidence.** Cursor's Auto-review
is explicitly the *fix*: "The first
technical decision was model choice. The
classifier runs before a tool call
executes... [to] make decisions around
agent autonomy behave more like a dial
than a switch." The block rate is 4% in
production; the interrupt rate is 7%. The
comparison: ~40% block rate with blanket
permission gates. The 4% is *the right
rate* — most things don't need a human;
the things that do are obvious.

**ASPIS today.** The R-001 scope guard is
the deterministic equivalent. The runtime
guard (deterministic, allowlist) is
analogous. The *LLM classifier* is the
as-yet-unbuilt piece.

**ASPIS should add.** A small classifier
in the runtime — *not* a quality reviewer
— that decides "this tool call needs the
user, this one doesn't." The Cursor
Auto-review model is the reference. (This
is a Phase-3+ feature per the *production-
loops-companies* doc §0 Pattern 5.)

### 6.7 Chasing every finding (over-engineering)

> *"A reviewer prompted to find gaps will
> usually report some, even when the work
> is sound, because that is what it was
> asked to do. Chasing every finding leads
> to over-engineering: extra abstraction
> layers, defensive code, and tests for
> cases that can't happen."* — Anthropic

**Failure mode.** The reviewer reports 12
findings; the builder "fixes" 12 things;
half are unnecessary; the diff bloats; the
reviewer reviews again; loop.

**Industry evidence.** Anthropic's caveat
(verbatim above) is the most-cited warning
in the review literature.

**ASPIS today.** The reviewer's "Core
rules" do not include the constraint.
This is the highest-value line to add to
the reviewer body — or, more correctly, to
the `quality-review` skill when written.

**ASPIS should add.** The "correctness +
stated requirements only" constraint, in
the reviewer body and in `quality-review`.

---

## §7. What ASPIS should adopt / adapt / reject

This is the answer to the F-016 question: "What
can ASPIS reviewer learn from each surveyed
system?" Per system, the recommendation is one
of: **adopt** (use the pattern as-is),
**adapt** (use a modified version), or
**reject** (deliberately not use).

### 7.1 From Cursor Bugbot

- **Adopt: the "findings → comments →
  reactions → learned rules" loop.** The
  *learned rules* concept is the right
  shape for ASPIS's improvement loop: the
  reviewer produces findings; the parent
  agent (or human) reacts; the reactions
  become rules that bias future reviews.
  This is a *Phase 3+* feature (the
  lessons loop is in
  `agent-system-design-patterns.md`).
  - **In the near term**: the review
    template's `Suggested fix` field is
    the right place for the parent agent
    to react ("applied", "won't fix",
    "needs more info") — and the
    reviewer's *next* review should
    weight prior "won't fix" reactions.
- **Adopt: incremental review (only
  review what's new).** When the
  builder pushes a small follow-up, the
  reviewer should not re-review the
  whole diff. The reviewer should
  default to "review the new lines
  only, but keep the prior verdict's
  findings in scope" (per Cursor's
  *Bugbot June 2026* post).
- **Adopt: the resolution-rate
  metric.** The "% of findings
  resolved before merge" is the
  reviewer's quality signal. ASPIS
  should track this in the trace.
- **Reject: Bugbot Autofix (reviewer
  applies the fix).** ASPIS's R-004
  (one writer) + R-006 (read-only
  reviewer) deliberately separate
  the review and the fix. The
  reviewer's verdict is read-only;
  the build-lead applies the fix.
  The trade-off (slower fix, no
  review-bias in the fix) is
  acceptable for ASPIS's smaller
  scale.

### 7.2 From Cursor Auto-review

- **Adopt: a small classifier in the
  runtime for *safety* decisions.**
  This is the *deterministic-first
  ladder* taken to the next level: a
  classifier in the agent loop that
  decides "this tool call needs the
  user, this one doesn't." ASPIS has
  the deterministic allowlist
  (R-001); the classifier is the
  contextual sidecar. The 4% block
  rate is the *target* — most things
  don't need a human; the things
  that do are obvious.
- **Adopt: the same-RPC-stream
  architecture.** The classifier
  reads the parent agent's intent
  and the file contents *before* the
  tool call executes. ASPIS's
  runtime_guard is the *shell-hook*
  equivalent; the classifier would
  be the *LLM-hook* equivalent.
- **Reject: the conflation of
  classifier and reviewer.** The
  classifier is *safety* (does this
  tool call do harm?). The reviewer
  is *quality* (is this change
  correct?). They are different
  roles with different verdicts.
  ASPIS already has the
  classification (deterministic
  scope guard); the reviewer is
  separate. Do not collapse them.

### 7.3 From Claude Code `/code-review`

- **Adopt: the Writer/Reviewer
  pattern as the canonical review
  shape.** Two parallel sessions;
  the reviewer is a subagent in
  fresh context; the reviewer's
  verdict is delivered to the
  parent; the parent fixes. ASPIS
  already does this in design; the
  implementation gap is the
  build-lead → reviewer reachability
  (D-build-lead-1).
- **Adopt: the "correctness +
  stated requirements only"
  constraint.** Add to the
  reviewer body and to the
  `quality-review` skill. The
  constraint is the single most
  effective anti-over-engineering
  rule in the review literature.
- **Adopt: the "subagent for
  verification" pattern.** After
  the build, a subagent in fresh
  context verifies the diff
  against the SPEC. Same
  pattern; ASPIS should make it
  the default.
- **Adapt: the `/code-review`
  skill as a *skill* (not a
  role).** Claude Code's
  `/code-review` is a skill that
  *uses* a subagent; the
  subagent is the *role*. ASPIS
  has the role (Reviewer lead);
  the skill (`quality-review`)
  is the *content* of what the
  role does. The split is the
  same.

### 7.4 From GitHub Copilot code review

- **Adopt: the Low / Medium effort
  dial as the *only* knob the
  reviewer needs.** The reviewer
  picks the depth from the diff
  size + the mode + the risk class.
  Vibe = Low. Production = Medium
  (always). Production +
  security-sensitive = Medium +
  security-reviewer subagent.
  This is the simplest viable
  dial; the industry is converging
  on it.
- **Adopt: full project context
  gathering.** The reviewer
  reads the *whole* repo, not
  just the diff. ASPIS reviewer
  is read-only across the project
  (verified) — it can grep and
  read freely. The *practice* is
  already supported; the
  *guidance* in the reviewer
  body should make it explicit
  ("read the relevant files; do
  not limit yourself to the diff").
- **Adopt: the "validate
  carefully" caveat.** GitHub is
  explicit: "Copilot is not
  guaranteed to spot all problems
  or issues in a pull request.
  Sometimes it will make
  mistakes. Always validate
  Copilot's feedback carefully.
  Supplement Copilot's feedback
  with a human review." The
  reviewer is *one* input to
  the verdict; the verdict is
  binding when supported by
  evidence. The reviewer body
  should make this explicit.

### 7.5 From Cognition Devin evaluator

- **Adopt: typed criteria as the
  shape of the reviewer's
  evidence.** The Devin
  evaluator's criteria are
  *observable, end-state
  properties* of the running
  system — "the dashboard shows
  5+ graphs", "the auth endpoint
  returns 401 on bad token". The
  ASPIS reviewer's *findings*
  should be the same shape: a
  specific behavior or property
  that is verifiable, not "the
  code is well-organized". The
  reviewer's evidence is *what
  the change does*, not *what
  the change looks like*.
- **Adopt: the "evaluating the
  evaluators" discipline.** The
  Devin team measures precision
  and recall of the evaluator
  against ground truth. ASPIS
  should do the same — track
  the reviewer's findings
  against the eventual
  post-merge state ("did this
  finding actually matter?").
  The metric is the
  resolution-rate analogue.
- **Adapt: the evaluator as a
  *general agent* (not a
  single LLM).** Cognition's
  evaluator has the *same
  tools* as the builder
  (shell, browser, code edit).
  ASPIS reviewer is read-only
  (R-004) and does not have
  code-edit tools. The
  *judgement* is the same; the
  *tools* are deliberately
  constrained. This is the
  right trade-off for ASPIS's
  scale.

### 7.6 From OpenAI Codex

- **Adopt: "iterate until all
  agent reviewers are
  satisfied" as the loop's
  close condition.** ASPIS
  already does this in design
  (the verdict is the gate);
  the *behaviour* is the same.
- **Adopt: the spec-in-the-
  issue-body shape.** The
  GitHub issue body (or the
  SPEC.md in ASPIS) is the
  reviewer's *first input*.
  Without a spec, the
  reviewer has no criteria.
  This reinforces the
  importance of the SPEC in
  ASPIS's mode dial (vibe =
  bullets, mvp = stories,
  production = full).
- **Adapt: the multi-reviewer
  shape.** Codex has multiple
  reviewers (sub-agent local,
  cloud, Codex itself). ASPIS
  has one Reviewer role with
  sub-agents (security,
  architecture) for
  high-risk changes. The
  *shape* is the same; the
  *number* is smaller. This
  is the right size for
  ASPIS's scale.

### 7.7 From Anthropic (general)

- **Adopt: the evaluator-
  optimizer pattern (one LLM
  generates, another
  evaluates, loop until
  satisfied).** ASPIS already
  has this shape (builder +
  reviewer + fix loop); the
  *evidence* is in the
  reviewer's verdict.
- **Adopt: the two signs of
  good fit (LLM can be
  improved by human
  feedback; LLM can provide
  such feedback).** ASPIS
  reviewer is on the `deep`
  model tier; this is the
  right default.
- **Adopt: the
  *chase-every-finding* warning
  as a hard rule in the
  reviewer body and the
  `quality-review` skill.**
- **Adopt: the Stop hook +
  /goal + subagent review
  *gradient*.** The four
  levels of "give Claude a
  check it can run" (in-
  prompt / /goal / Stop hook
  / subagent) are the same
  gradient ASPIS's mode dial
  exposes. The mode dial
  picks *which level* the
  build is at; the reviewer
  is always the *subagent
  review* level (the strictest
  that doesn't require a
  human). This is the right
  default.

### 7.8 From Vercel / Replit

- **Adopt (where applicable):
  *behaviour-as-evidence*.**
  For UI / full-stack work,
  the deterministic check is
  *what the running app does*,
  not *what the source code
  says*. ASPIS is a file-first
  factory, so the *built*
  app is not always available
  in the reviewer's context.
  But for any project that
  has a built artifact, the
  reviewer should prefer the
  built artifact over the
  source code.
- **Reject: the preview-UI
  shape** for ASPIS's own
  development. The
  *pattern* (the reviewer
  drives the running system)
  is right; the *specific
  mechanism* (a Vercel
  preview URL) is not
  applicable to ASPIS's own
  factory (file-first,
  no UI). For ASPIS-built
  products, the pattern
  is the right one to
  recommend.

### 7.9 The single most important recommendation

**Write the three missing review skills.**

The current catalog references 5 review skills.
3 of them are *referenced but not authored*:
`review-strategy`, `quality-review`,
`acceptance-decision`. `plan-critic` is the 4th.

| Skill | Purpose | Source pattern |
|---|---|---|
| `review-strategy` | Pick the depth and the dimensions from mode + risk | Cursor Bugbot's "default vs. Medium"; Copilot Low/Medium |
| `quality-review` | Walk the 9 dimensions; produce findings; verify against evidence | Anthropic /code-review; Cognition evaluator's typed criteria |
| `acceptance-decision` | Render the verdict; route the follow-up (approve / approve-with-notes / changes-required / rejected → committer / builder / fix-lead) | ASPIS's own 4-outcome shape; Cursor Bugbot's upvote/downvote |
| `plan-critic` | Cross-artifact consistency (SPEC ↔ PLAN ↔ TASKS ↔ ACCEPTANCE) + measurability | Anthropic plan mode; OpenAI Codex's plan review |

**The four together are the content of the
Reviewer role.** Without them, the Reviewer is a
prompt, not a process. With them, the Reviewer
is the load-bearing quality gate in the ASPIS
core loop.

The `review-strategy` + `quality-review` +
`acceptance-decision` triad is *the minimum
viable review skill set*. The `plan-critic` is
*the most leveraged single addition* — it
catches the most expensive failures
("the plan was wrong") before any code is
written.

---

## §8. The Reviewer's next 5 actions

If the Reviewer role were to read this doc and
make 5 concrete changes, in priority order:

1. **Write `plan-critic` skill.** The plan
   review is the *highest-leverage* review
   point — a wrong plan produces a wrong
   build. The skill checks SPEC ↔ PLAN ↔
   TASKS ↔ ACCEPTANCE for measurability,
   traceability, scope, and risk.

2. **Write `quality-review` skill.** The
   change review is the *most frequent*
   review point. The skill walks the 9
   dimensions (mode-scaled per §3) and
   produces specific findings. The
   "correctness + stated requirements only"
   constraint (per Anthropic) goes here.

3. **Write `review-strategy` skill.** The
   depth-picker. Maps diff size + mode +
   risk class to a review depth. Without
   this, the review is the same depth
   for a typo and a security change —
   the §6.3 anti-pattern.

4. **Add "correctness + stated requirements
   only" constraint to the reviewer body.**
   This is a one-paragraph add to the
   "Core rules" section of the
   `agents/review/reviewer.md`. It is the
   single most effective anti-over-
   engineering rule in the review
   literature.

5. **Track the resolution rate.** The "% of
   findings resolved before merge" is
   Cursor's load-bearing reviewer-quality
   metric. ASPIS should add a
   `findings → resolved?` trace event
   pair. The metric is the antidote to
   rubber-stamping and to noise.

**Plus, two structural decisions to revisit
in the medium term:**

- **The "reviewer is the committer" rule.**
  This is *not* an industry-standard
  pattern. The trade-off (single owner,
  fast cycle) is real; the risk (reviewer
  bias toward approval because the
  reviewer also has to commit) is also
  real. The rule should be revisited
  when ASPIS's quality metric (resolution
  rate) shows bias. Until then, the
  rule stands.
- **The "no evidence = no verdict" rule.**
  The reviewer body refers to this; the
  body should *state* it explicitly. The
  rule is the single most important
  reviewer discipline; it should be
  unmistakable.

---

## §9. Source provenance

All sources verified 2026-06-25. Refresh
cadence: quarterly for benchmark numbers;
on major model release for production-loop
findings.

| Source | URL | Verified | What it gave us |
|---|---|---|---|
| Cursor — *Bugbot is now over 3x faster* | https://cursor.com/blog/bugbot-updates-june-2026 | 2026-06-25 | Incremental review, `/review`, Composer 2.5, 3× faster, 22% cheaper, 10% more bugs |
| Cursor — *Bugbot now self-improves* | https://cursor.com/blog/bugbot-learning | 2026-06-25 | 78.13% resolution; learned rules; 110k repos; 44k rules |
| Cursor — *Bugbot Autofix* | https://cursor.com/blog/bugbot-autofix | 2026-06-25 | 35% Autofix merge rate; resolution rate 52% → 76%; "agents running automatically based on an event" |
| Cursor — *Governing agent autonomy with Auto-review* | https://cursor.com/blog/agent-autonomy-auto-review | 2026-06-25 | 4% block, 7% interrupt; classifier model; same-RPC-stream; flapping signal; ~40% blanket-gate comparison |
| Anthropic — *Best practices for Claude Code* | https://code.claude.com/docs/en/best-practices | 2026-06-25 | Fresh-context subagent review; Writer/Reviewer pattern; "chase every finding" warning; 4-level verification gradient |
| Anthropic — *Building Effective Agents* | https://www.anthropic.com/research/building-effective-agents | 2026-06-25 | Evaluator-optimizer workflow; "two signs of good fit"; 4 workflow patterns |
| Anthropic — *Multi-agent Research* | https://www.anthropic.com/engineering/multi-agent-research-system | 2026-06-25 | 15× token cost of multi-agent; 80% variance from token usage |
| GitHub — *About Copilot code review* | https://docs.github.com/en/copilot/concepts/agents/code-review | 2026-06-25 | Low / Medium effort; agentic capabilities; MCP; review exclusions; "model switching is not supported"; "validate carefully" caveat |
| Cognition — *Evaluating coding agents* | https://www.cognition.ai/blog/evaluating-coding-agents | 2026-06-25 | Evaluator agent with same tools; typed criteria; 74.2% on cognition-golden; interactive self-reflection; precision/recall of evaluators |
| OpenAI — *Harness engineering* | https://openai.com/index/harness-engineering/ | (already in `production-loops-companies.md`) | 3.5 PRs/engineer/day; "all agent reviewers satisfied"; Codex review loop |
| Vercel v0 | https://vercel.com/docs | (already in `production-loops-companies.md`) | Preview-as-evaluator pattern |
| Replit Agent 4 | https://replit.com/agent4 | (already in `production-loops-companies.md`) | Design canvas + concurrent forks |

**Cross-references in the ASPIS catalog (verified
2026-06-25):**

- `src/aspis/data/catalog/agents/reviewer.md`
  (the canonical reviewer body, lines 1-99)
- `src/aspis/data/catalog/workflows/review.md`
  (the 4-step review workflow)
- `src/aspis/data/catalog/commands/review.md`
  (the `/review` command shape)
- `src/aspis/data/catalog/templates/review/review.md`
  (the finding table template)
- `src/aspis/data/catalog/config/policy/modes.yaml`
  (the `build_review: light | standard | full` knob)
- `src/aspis/data/catalog/config/policy/constitution-checks.yaml`
  (the 11 checks the reviewer owns)
- `.aspis/rules/system-rules.md` (R-001 through R-009)
- `.aspis/workflows/review.md`, `templates/review/review.md`
  (the active copies in the live workflow)
- `local/AGENT-SYSTEM-ARCHITECTURE.md` (the synthesis doc)
- `local/agents/reviewer.md` (the local-doc reviewer's role)
- `local/ASPS/.asps/agents/review/asps-reviewer.md` (old ASPS Reviewer)
- `local/ASPS/.asps/agents/review/security-reviewer.md`, `commit-reviewer.md` (sub-reviewers in old ASPS)
- `local/ASPS/.asps/skills/review-checklist.md`, `scope-audit.md`, `architecture-review.md`, `security-review.md` (old ASPS review skills)

**Existing ASPIS research on review (verified
2026-06-25):**

- `local/ASPS/.asps/features/F-016-agent-system-architecture/Research/review-local-docs-rules.md` (rules-compliance review of the 11-agent synthesis)
- `local/ASPS/.asps/features/F-016-agent-system-architecture/Research/review-local-docs-accuracy.md` (accuracy review of the 11-agent synthesis)
- `local/ASPS/.asps/features/F-016-agent-system-architecture/Research/production-loops-companies.md` (industry patterns; §0 Pattern 3 = adversarial review in fresh context; §0 Pattern 5 = risk-tiered autonomy; §1.4 = Auto-review; §1.5 = Devin evaluator)
- `local/ASPS/.asps/features/F-016-agent-system-architecture/Research/core-loops-2026.md` (Pattern 3 = adversarial review in fresh context; §2 minimal effective loop)
- `.aspis/research/agent-system-design-patterns.md` (the broader agent-design patterns reference)

**What this doc adds** (the unique value):

1. **The conflation of safety-classifier and quality-reviewer is named and rejected** (the most common design mistake in agentic review systems).
2. **The 9 review dimensions are aligned with the industry consensus** (with concrete depth-per-mode for each).
3. **The 5 missing review skills are named and prioritised** (`plan-critic`, `quality-review`, `review-strategy`, `acceptance-decision`, plus the reviewer-context template).
4. **The 4-outcome verdict shape is justified against Cursor Bugbot's upvote/downvote + comment** (the same shape, collapsed to 4).
5. **The "reviewer is the committer" rule is flagged as a deliberate trade-off to revisit** (the risk is reviewer bias toward approval).
6. **The 5 concrete next actions for the Reviewer role** are ranked by leverage.
7. **The Cursor Bugbot learned-rules loop is the model for the Phase 3+ lessons loop** (the design pattern is `findings → reactions → rules → bias`).

---

*End of research. This doc is the load-bearing
review-surface reference for F-016 and the Reviewer
role. It is read in conjunction with
`production-loops-companies.md` (industry loop
patterns) and `core-loops-2026.md` (Pattern 3 =
adversarial review in fresh context).*

*Refresh schedule: quarterly for benchmark numbers;
on major model release for production-loop
findings; immediately on any change to the
Reviewer body, the review workflow, or the
`plan-critic` / `quality-review` / `review-strategy`
/ `acceptance-decision` skills (whichever lands
first).*
