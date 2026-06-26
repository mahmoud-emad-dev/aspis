# Project Lead — Complete Delegation Map

> **Feature:** F-016 — agent system architecture
> **Mode:** production · **Author:** research-lead
> **Compiled:** 2026-06-26
> **Scope:** every delegate project-lead can route to in the current ASPIS
> runtime — name, level, triggers, context packet shape, expected return,
> deployment status, known drift, and how project-lead recontextualizes the
> return. Also: the human gate, what project-lead handles directly, the
> "subordinate lead never routes to another lead" rule, and the orchestration
> patterns project-lead composes.
>
> **Sources read.**
> - `local/AGENT-SYSTEM-ARCHITECTURE.md` (the system shape)
> - `local/agents/project-lead.md` (the role + intent routing table)
> - `.opencode/agents/project-lead.md` (the live frontmatter — actual task
>   allow-list)
> - `.aspis/features/F-016-agent-system-architecture/Research/current-aspis-agents-2.md`
>   (per-agent live-vs-catalog drift, including the missing test-lead)
> - `.aspis/features/F-016-agent-system-architecture/Research/old-asps-deep-analysis-1.md`
>   (the old ASPS's R-009 routing table — the ancestor of the current R-008
>   human gate)
> - `.aspis/rules/system-rules.md` (R-001…R-009)

---

## 0. TL;DR

Project-lead is the **only L1 entry point**. It owns 9 delegation edges
in the live runtime: **7 L2 leads** (4 primaries + 3 subagents) and **2 L3
helpers**. Of the 9 edges, **2 are drifted / dangling** today:

1. **`committer` is in project-lead's task allow-list** — the role says
   project-lead "read[s] broadly and change[s] almost nothing — no edits,
   no commits." This edge allows a delegation that contradicts the role.
   **Recommended fix:** remove `committer` from the live task list.
2. **`test-lead` is in project-lead's task allow-list** but test-lead is
   **not deployed in live** (catalog has it; `.opencode/agents/` does
   not). The edge dangles. **Recommended fix:** either re-render
   test-lead from the catalog, or remove the edge and accept that
   test validation flows through the reviewer.

The remaining 7 edges are correct and load-bearing.

---

## 1. The delegation table (one row per edge)

| # | Delegate | Level | Mode | Deployed in live? | Live task list | Catalog task list | Drift |
|---|---|---|---|---|---|---|---|
| 1 | `planning-lead` | L2 | primary | ✅ | ✅ | ✅ | clean |
| 2 | `build-lead` | L2 | primary | ✅ | ✅ | ✅ | clean |
| 3 | `reviewer` | L2 | primary | ✅ | ✅ | ✅ | clean |
| 4 | `system-lead` | L2 | primary | ✅ | ✅ | ✅ | clean |
| 5 | `fix-lead` | L2 | subagent | ✅ | ✅ | ✅ | clean |
| 6 | `research-lead` | L2 | subagent | ✅ | ✅ | ✅ | clean |
| 7 | `test-lead` | L2 | subagent | **❌** | ✅ (dangling) | ✅ | **runtime gap** |
| 8 | `project-explorer` | L3 | subagent | ✅ | ✅ | ✅ | clean |
| 9 | `committer` | L3 | subagent | ✅ | ✅ (drift) | ❌ | **permission drift** |

Local-file `local/agents/project-lead.md` (line 61) describes "the 7 L2
leads" but the live frontmatter (line 24-34) actually allows 7 L2 + 2 L3 =
**9 delegates**. Treat the live frontmatter as truth for routing.

---

## 2. The per-delegate reference

For each delegate: **what it does** · **level** · **triggers** (user words
*and* system conditions) · **context packet shape** (the 5-field
`intent · context · constraints · references · expected outcome` shape
project-lead's `context-packaging` skill produces) · **expected return
format** · **deployed?** · **drift / bugs** · **recontextualization**
(what project-lead does with the return before it reaches the user).

---

### 2.1 `planning-lead` (L2, primary)

**What it does.** Owns the planning lifecycle: intake → clarify → spec →
architecture → tasks → acceptance. Produces execution-ready plans. Does
not build, review, test, or research (it routes research to
research-lead). The planner narrows scope and hands off to build-lead
at P9.

**Level.** L2, `mode: primary` (post-bootstrap).

**Triggers — user words.**
- "plan …", "spec out …", "design …"
- "scope this", "what should we build"
- "new feature: <name>"
- "how would we approach …", "decompose this"
- "write the requirements for …", "draft a PRD"
- "clarify what we mean by …", "ask me the questions"
- "this is too vague — make it buildable"

**Triggers — system conditions.**
- User request classified as `intent: feature` and `mode != vibe`
  (vibe mode: planning-lead produces a 1-paragraph plan, not full
  SPEC/PLAN/TASKS).
- A request that arrives *after* a feature is partially planned and
  the plan needs to be amended → planning-lead (not build-lead).
- A request that turns out to be defect-shaped *but* ambiguous →
  planning-lead for a "should this be a plan or a fix?" triage,
  then dynamic handoff to fix-lead.

**Context packet shape (what project-lead includes).**
- `intent`: classify the request — "plan" vs "spec" vs "clarify" vs
  "re-plan" vs "scope check"
- `context`: feature ID (or "new"), the user's one-sentence idea,
  mode (vibe / MVP / production), any prior planning artifacts
  (paths under `.aspis/features/F-XXX/`)
- `constraints`: deadline hints, budget hints, stack constraints,
  anything the user said that scopes the work
- `references`: links to similar prior features, the as-built
  architecture (`.aspis/context/ARCHITECTURE.md`), the modes
  overlay (`.aspis/config/modes.yaml`)
- `expected outcome`: the artifacts the planner should produce
  (e.g., SPEC + PLAN + TASKS + ACCEPTANCE for production; 1-paragraph
  plan for vibe)

**Expected return format.**
- A list of artifacts produced with paths:
  - `.aspis/features/F-XXX/SPEC.md`
  - `.aspis/features/F-XXX/PLAN.md`
  - `.aspis/features/F-XXX/TASKS.md`
  - `.aspis/features/F-XXX/ACCEPTANCE.md` (or acceptance in TASKS)
- A "ready for build?" verdict from the planner's own quality check.
- If `plan-critic` was run: the reviewer's verdict against the plan.

**Deployed in live?** ✅

**Drift / bugs.** None at the project-lead ↔ planning-lead edge. The
*planning-lead's own* task list has a stray `committer: allow` (drift
in planning-lead, not in this edge).

**Recontextualization.** Project-lead translates the planner's
"ready for build" + artifacts into a user-facing summary: "Here's
the plan. It has N tasks, M acceptance criteria, a research note
if any unknowns, and a [approved / changes-requested] verdict from
plan-critic. Want me to send it to build-lead?" Project-lead
also surfaces any open questions the planner raised that the user
must answer before build can start.

---

### 2.2 `build-lead` (L2, primary)

**What it does.** Owns feature implementation. Takes an approved plan,
decomposes it into task packets, delegates each packet to a
context-isolated `general-builder`, runs the product gate per task,
routes to reviewer, and hands off to committer. Does not write product
code itself; writes only orchestration artifacts.

**Level.** L2, `mode: primary` (post-bootstrap).

**Triggers — user words.**
- "build …", "implement …", "code …"
- "ship …", "make …", "develop …"
- "add the feature", "execute the plan"
- "we already planned F-XXX — go"

**Triggers — system conditions.**
- A plan that was just approved and the user said "go".
- A reviewer returned "approved" and the user wants the next batch
  (sequential, not parallel — the plan drives the order).
- A fix-lead returned "fixed" and a regression test is needed →
  build-lead for the regression test (or fix-lead for the minimal
  fix + test). Triage by which is the cheaper path.
- "Build F-XXX" is the canonical command, surfaced as `/build`.

**Context packet shape.**
- `intent`: "implement the approved plan for F-XXX" or "build
  task T-NN from F-XXX" (build-lead is also valid mid-feature for
  one task)
- `context`: feature ID, plan path, task IDs, mode, current
  branch / `active_feature.json`, the prior `BUILD_REPORT`s
  (so build-lead knows what's already done)
- `constraints`: scope guard (`scope.allowed` / `scope.forbidden`),
  gates to run (`.aspis/gates.yaml`), any human-set deadlines
- `references`: SPEC, PLAN, TASKS, the as-built architecture
- `expected outcome`: BUILD_REPORT per task, gate-green status,
  reviewer-approved status, commits landed (via committer)

**Expected return format.**
- A list of `BUILD_REPORT` paths (one per task).
- Gate results (PASS/FAIL) per task.
- Reviewer verdicts per task.
- Commit SHAs (the committer produced them; build-lead reports
  them — does not commit itself).
- A "feature complete" verdict when all tasks are `[x]` in
  `TASKS.md` and reviewed + committed.

**Deployed in live?** ✅

**Drift / bugs.** None at this edge. (Build-lead's own task list has
a dangling `test-lead: allow`; that's a build-lead defect, not a
project-lead-edge defect.)

**Recontextualization.** Project-lead translates "feature complete"
+ commit SHAs into a user-facing status: "F-XXX is built and
committed across N tasks. M tests added, all gates green, reviewer
approved all M tasks. Here's the branch and the commits. Want a
summary in the project log?" Project-lead also surfaces any
rejections or open follow-ups the build-lead escalated.

---

### 2.3 `reviewer` (L2, primary)

**What it does.** Independent quality authority. Read-only. Reviews
both **plans** (pre-build, via `plan-critic`) and **changes**
(during/after build, via `quality-review`). Renders one of four
verdicts: **approved · approved with notes · changes required ·
rejected**. Does not plan, build, or commit.

**Level.** L2, `mode: primary` (post-bootstrap).

**Triggers — user words.**
- "review this", "is this OK", "did we do this right"
- "audit the diff", "check the change"
- "look at F-XXX before we merge", "second opinion"
- "is this safe to ship"
- "plan review" (explicit `plan-critic` mode)

**Triggers — system conditions.**
- A plan was just produced by planning-lead and needs
  pre-build review (`plan-critic`) — the **default** for
  production mode.
- Build-lead reports a task is "gate-green and ready for review"
  (the build workflow's per-task review routing).
- A `REVIEW_NEEDED` event arrives from fix-lead after 3 failed
  fix attempts.
- A security-touching diff was produced (cross-cutting; the
  reviewer covers security as a review dimension).

**Context packet shape.**
- `intent`: "review a plan" vs "review a change" vs "review for
  security" vs "second opinion"
- `context`: what to review (paths or plan paths), the diff or
  the plan, the SPEC / acceptance criteria, the gates output
- `constraints`: which dimensions to prioritize (security
  high-crit? cross-cutting?), the mode (matches planning/build
  for consistency), any human-set bar
- `references`: as-built architecture
  (`.aspis/context/ARCHITECTURE.md`), the architecture
  constitution (so the reviewer runs the constitution checks
  it owns)
- `expected outcome`: REVIEW_REPORT with verdict + per-dimension
  evidence (file:line for any finding), explicit recommendation
  for what to do next

**Expected return format.**
- A REVIEW_REPORT (path + verdict).
- The verdict: `approved` / `approved with notes` / `changes required` / `rejected`.
- Findings: list of `file:line — finding — severity` triples.
- Routing recommendation: "send back to build-lead" / "send to
  fix-lead" / "send to committer" / "escalate to human" (R-008).

**Deployed in live?** ✅

**Drift / bugs.** Reviewer's *own* task list adds `research-lead`
(live has it, catalog doesn't) — that's a likely catalog gap, not
a defect at this edge. Reviewer's model file (`minimax-m3`) drifts
from `agent-models.yaml` (`deepseek-v4-pro`); `aspis models --apply`
resolves it.

**Recontextualization.** Project-lead translates the verdict + findings
into user-facing language: "Reviewer says [approved with N notes /
changes required on M items / rejected]. Here's what they found,
file by file. The recommended next step is [send to build-lead for
N trivial fixes / send to fix-lead for M structural fixes / escalate
to you for a human decision]." Project-lead also decides whether
to surface the verdict in a project log or just to the user.

---

### 2.4 `system-lead` (L2, primary)

**What it does.** Owns the ASPIS runtime and operating infrastructure
(`.opencode/`, `.claude/`, protected `.aspis/`). Governs the catalog
evolution. Routes authoring to runtime-specific authors. Hands
commits to committer. The system-lead is **not** a product-feature
lead.

**Level.** L2, `mode: primary` (post-bootstrap).

**Triggers — user words.**
- "add a skill", "add an agent", "add a workflow", "add a template"
- "fix a broken runtime", "the bootstrap is broken", "doctor is failing"
- "change the default model", "update model routing"
- "add a hook", "add a command", "change the config"
- "migrate the system", "upgrade ASPIS", "re-bootstrap"
- "add a protected-path", "change permissions"

**Triggers — system conditions.**
- `aspis doctor` returns FAIL — project-lead detects this via the
  read-only bash allow-list and routes here.
- A `REVIEW_NEEDED` event names a runtime/route/permission defect.
- A `system-validation` failure surfaces (post-change).
- `aspis models --check` or `validate-runtime` reports drift.
- A new project is being onboarded (re-bootstrap path; the bootstrap
  agent is one-shot, so the project-lead routes the *recovery* to
  system-lead).
- A new profile is being added (`profiles/*.yaml`) — system-lead owns
  the profile system.

**Context packet shape.**
- `intent`: classify the system change — "new agent" / "new skill" /
  "new config" / "repair" / "model change" / "permission change" /
  "bootstrap recovery"
- `context`: what runtime is affected (`.opencode/` vs `.claude/`),
  current catalog state, current live state, any prior failure
  reports
- `constraints`: governance rules (R-003 deterministic-first,
  R-006 thin agents, R-007 pinned models, R-008 human gate for
  rules/permissions/security/model-routing)
- `references`: the asset being changed, the matching catalog entry,
  the relevant policy file (`.aspis/config/policy/hooks.yaml`,
  `agent-models.yaml`, `models.yaml`, `modes.yaml`)
- `expected outcome`: the runtime change authored + validated via
  `aspis validate-runtime` / `validate-index` / `doctor`; the commit
  handed to committer

**Expected return format.**
- A list of changed assets (paths).
- Validation results: `aspis validate-runtime: PASS`, `aspis
  validate-index: PASS`, `aspis doctor: 0 FAIL`.
- A hand-off note: "change is at committer, awaiting commit" or
  "committed, here is the SHA."

**Deployed in live?** ✅

**Drift / bugs.**
- **system-lead's `websearch`** is `allow` in live, `deny` in
  catalog. Real permission widening. Reconcile: either add a
  comment to live explaining why system-lead may websearch (e.g.,
  "to fetch latest official docs for an authoring task"), or set
  live to `deny`.
- Live adds `reviewer` and `committer` to system-lead's task
  list (catalog silent). Likely catalog gaps — close in catalog.

**Recontextualization.** Project-lead translates system-lead's
"runtime change validated, committed" into a user-facing status:
"The [agent/skill/config/permission] was [added / changed / fixed].
Doctor is 0 FAIL. Here's the commit. Note: this touched [runtime
X], so it affects [Claude / OpenCode] side." Project-lead also
**stops the user-facing claim** if the change was R-008-gated
("this was a rules/permissions change — I asked you first, you
approved, here's the diff").

---

### 2.5 `fix-lead` (L2, subagent)

**What it does.** Recovery authority. Receives a gate-fail or test
regression, reproduces, finds root cause (not symptom), applies the
smallest safe fix, verifies, hands to committer. **Hard cap: 3
attempts**, then `REVIEW_NEEDED` to the human review queue. Never
plans features, never broadens scope.

**Level.** L2, `mode: subagent`.

**Triggers — user words.**
- "fix this", "it's broken", "failing", "regression"
- "this used to work", "tests are red", "gate failed"
- "the build is broken", "we shipped a bug"
- "this is a regression"

**Triggers — system conditions.**
- A `gate_result: FAIL` event from a build task.
- A test regression (was green, now red) detected by the test run.
- A reviewer returned "rejected" with a defect (not "changes
  required" — that goes back to the builder; "rejected with a
  defect" routes to fix-lead).
- A `REVIEW_NEEDED` from build-lead's 3-attempt cap.
- An end-to-end smoke failed post-deploy (post-commit hook can
  signal this).

**Context packet shape.**
- `intent`: "fix the gate-fail on task T-NN" / "fix the regression
  introduced by commit <sha>" / "fix the bug reported as <user words>"
- `context`: the failure signal (error message, failing test
  output, the gate-fail artifact), the diff that introduced the
  failure, the most recent green state, the active feature
- `constraints`: minimal-diff discipline (R-001 scope + R-005
  tests-as-spec), do not weaken or delete tests, do not change
  architecture to work around the bug
- `references`: the relevant code paths, the failing test, the
  recent commits, the SPEC's acceptance criteria for the task
- `expected outcome`: FIX_REPORT with root cause + minimal diff
  + gate-green verification; hand-off to committer

**Expected return format.**
- A FIX_REPORT (path) with: root cause, the diff (paths + summary),
  the regression test added (if any), the gate results
  (before/after).
- A hand-off: "ready for committer" or `REVIEW_NEEDED` with
  reason (3 attempts exhausted, or cause is outside fix-lead's
  scope/role).

**Deployed in live?** ✅

**Drift / bugs.** Fix-lead's *own* task list has a dangling
`test-lead: allow` (live adds it, catalog doesn't, and test-lead
isn't deployed). Drift is in fix-lead, not at this edge.

**Recontextualization.** Project-lead translates the FIX_REPORT
into: "Root cause was X. The fix touches Y file(s) in Z lines.
A regression test was added. Gates are green. Here's the commit.
[If REVIEW_NEEDED:] The fix-lead hit the 3-attempt cap. The cause
appears to be [structural / outside scope]. This needs your
decision — see the review queue." Project-lead surfaces the
REVIEW_NEEDED case as a user-facing prompt, not buried in a log.

---

### 2.6 `research-lead` (L2, subagent)

**What it does.** Knowledge authority. Receives a question that the
system can't answer from in-project intelligence; researches from
authoritative sources, validates currency, packages the finding as a
reusable reference so the same question isn't researched again.
Cache-first — check the knowledge cache before fetching.

**Level.** L2, `mode: subagent`.

**Triggers — user words.**
- "what's the current best practice for X", "is X still the right way"
- "look up …", "research …", "find out …"
- "current docs for …", "latest version of …"
- "package this knowledge so we don't re-research it"
- "investigate <external topic>"

**Triggers — system conditions.**
- A planning or build request names an **unknown** (unfamiliar
  library, uncertain API, version-sensitive behavior).
- A reviewer flags a "needs verification" finding about an external
  fact.
- A fix-lead's root cause analysis points at an external
  dependency ("the failing behavior is in upstream X, not our code").
- A system-lead is registering a new skill and needs the source
  docs (`knowledge-packaging` is the system-lead's intake of
  research-lead's output).
- A previous research note is past its freshness date.

**Context packet shape.**
- `intent`: classify — "verify a volatile fact" / "fetch official
  docs" / "package a reference" / "investigate a topic"
- `context`: the question (in one sentence), the use case (what
  decided on this research), any prior research artifacts
  (check the cache first), the cache paths (`.aspis/research/`,
  `*_OFFICIAL_REFERENCES.md`)
- `constraints`: prefer authoritative sources, record source
  URL + retrieval date + version, separate fact from opinion,
  flag unverified claims, package not raw-dump
- `references`: any in-project hints (file paths, prior
  references), the relevant cache locations
- `expected outcome`: a RESEARCH_NOTE (a packaged reference) with
  source + version + freshness; the note is reusable — the
  next ask for the same question finds it in cache

**Expected return format.**
- A RESEARCH_NOTE (path) with: the question, the answer, the
  sources (URL + retrieval date + version), the freshness
  date, the version constraints, any `[UNVERIFIED]` flags.
- A "cache hit / miss / new note" status.

**Deployed in live?** ✅

**Drift / bugs.** Research-lead's `write` without `edit` asymmetry
is intentional but undocumented in the role text. The role text
should explain "I author packaged references (new files) and
don't edit source." Otherwise, this edge is clean.

**Recontextualization.** Project-lead translates the RESEARCH_NOTE
into a user-facing answer: the user asked "what's the current
best practice for X?" and gets back a short summary that names
the source and the version. Project-lead also notes if the
answer is `[UNVERIFIED]` so the user doesn't take it as ground
truth. If the research uncovered something the user should
decide (e.g., "the current best practice has changed and our
code uses the old one"), project-lead surfaces that as an
action item, not buried in the note.

---

### 2.7 `test-lead` (L2, subagent) — **the dangling edge**

**What it does (per catalog).** Validation authority. Determines
whether software actually behaves as expected; turns the answer
into objective evidence the system can rely on. **Evidence
producer, not verdict renderer** — the Reviewer remains the
judge. Generates and runs tests; reports what they show.

**Level.** L2, `mode: subagent` (per catalog).

**Triggers — user words.**
- "test this", "write tests for …", "what's the coverage"
- "test strategy for F-XXX"
- "is this test flaky", "why is this test failing"
- "red→green this", "give me a regression test"

**Triggers — system conditions.**
- A new feature is planned and the test strategy needs
  generation (planning-lead's P-pipeline calls test-lead for
  evidence design).
- A coverage gap is detected post-build (the build-lead's
  `selective-testing` skill is the *inline* path; test-lead
  is the *parallel* deeper path).
- A gate-fail needs an independent reproduction (fix-lead can
  use test-lead to reproduce without losing parallelism).
- A reviewer wants a deeper, independent test pass before
  acceptance.

**Context packet shape.**
- `intent`: "design the test strategy for F-XXX" / "run the
  test suite and report" / "reproduce a failure independently"
  / "fill a coverage gap"
- `context`: the feature, the diff, the SPEC's acceptance
  criteria, the current test inventory, the prior
  `TEST_REPORT`s
- `constraints`: R-005 tests-as-spec (never weaken/delete a
  test), selective-testing (test the change surface, not always
  the whole suite), classify failures (flaky vs regression)
- `references`: the failing test (if any), the SPEC, the
  current code
- `expected outcome`: TEST_REPORT with pass/fail evidence,
  coverage numbers, failure classification, and routing
  recommendations (builder / fix-lead / reviewer)

**Expected return format.**
- A TEST_REPORT (path) with: per-test results, pass/fail
  counts, coverage numbers, failure classification (regression
  / pre-existing / flaky / scope-violation), routing
  recommendations.

**Deployed in live?** ❌ **NOT DEPLOYED.**

**Drift / bugs.**
- **The runtime gap.** The catalog has `test-lead.md`
  (`.aspis/data/catalog/agents/test-lead.md`); the live
  runtime (`.opencode/agents/`) does not. Three of the five
  primaries reference test-lead: project-lead (this edge),
  build-lead, fix-lead. The reviewer invokes the `aspis
  artifact test` command which routes through test-lead.
  Today, all four of those dangle.
- **What the live system does *without* test-lead.** The
  build workflow's `selective-testing` skill (run by
  build-lead with `pytest*` permission) covers the
  test-execution role. The reviewer is more likely to be the
  *sole* independent quality voice, conflating "did the tests
  pass" with "is this acceptable."

**Recontextualization (if test-lead were present).** Project-lead
would translate the TEST_REPORT into a user-facing summary: "Tests
are green at N% coverage. M tests added, K failures classified
as [regression / flaky / pre-existing]. Routing: [no action /
back to builder / to fix-lead]." Today, with test-lead absent,
project-lead's "recontextualization" for the test route is to
*re-route through build-lead* (selective-testing) or *flag the
gap* to the user ("the system would normally use test-lead here,
but it's not deployed; the reviewer is the only independent
quality voice for this change").

**Recommended fix.**
- **Option A (preferred).** Re-render test-lead from the catalog:
  `aspis models --apply` + the existing render path produces
  `.opencode/agents/test-lead.md`. The 3 dangling edges light up
  in the same commit. Aligns with "the system runs as designed."
- **Option B.** Remove `test-lead: allow` from project-lead /
  build-lead / fix-lead's live task lists. Accept that the
  build-lead's `selective-testing` is the system's only
  validation path. The reviewer's `aspis artifact test` step
  becomes a no-op or routes through build-lead.

---

### 2.8 `project-explorer` (L3, subagent)

**What it does.** Disposable, read-only exploration helper. The
project-lead's "go and look it up" agent. A focused question
about the codebase; a compact summary; exit. No memory, no edits,
no state.

**Level.** L3, `mode: subagent`.

**Triggers — user words.**
- "where is X", "which files import Y", "what's in this directory"
- "find the file that handles Z", "codebase map for …"
- "what's the layout of this part of the code"
- "show me the test file for module M"

**Triggers — system conditions.**
- A request from project-lead itself: "I need to know where X
  lives before I can route this." The project-lead's
  `project-awareness` skill says: "for anything deeper than a
  lookup, delegate exploration to project-explorer."
- Project-lead is building a context packet for a downstream
  lead and needs the file paths / skeletons before packaging.
- A planning, build, or fix lead (when routed by project-lead)
  needs a focused structural lookup that the project-lead
  absorbs and re-passes.

**Context packet shape (lean — explorer is context-isolated).**
- `intent`: one focused question — "where is X" or "which files
  import Y" or "what's the API of module M"
- `context`: the path scope (whole repo / subdirectory), any
  specific symbols / patterns to look for
- `constraints`: read-only, no edits, no shell beyond context
  scripts (`python .aspis/scripts/context/*`)
- `references`: the index files (`.aspis/index/FILE_REGISTRY.yaml`,
  `.aspis/index/CODE_MAP.md`) — start from the index, don't
  read the wider repo
- `expected outcome`: a compact summary — file paths, line
  numbers, the relevant skeleton, the answer to the question
  in 1-3 paragraphs. **No file dumps.**

**Expected return format.**
- A compact finding: paths, line numbers, the relevant
  skeleton (or the import graph), the answer.
- "Not found" is an acceptable return when nothing matches —
  the explorer is honest, not creative.

**Deployed in live?** ✅

**Drift / bugs.** None at this edge. (The explorer's *own* file
lacks `temperature: 0.1` and `name:`; cosmetic, not a routing
defect.)

**Recontextualization.** Project-lead absorbs the explorer's
compact finding and uses it to (a) answer the user's "where is
X?" directly, or (b) build a richer context packet for a
downstream lead. Project-lead does *not* forward the explorer's
raw output to the user; the explorer returns "summaries, not
dumps" and project-lead is the agent that *synthesizes* the
summary into a project-aware answer.

---

### 2.9 `committer` (L3, subagent) — **the drifted edge**

**What it does.** The **only** agent permitted to commit to git.
Receives reviewed, gate-green work from a lead; verifies scope,
composes the message via `aspis commit`, runs the hooks, commits.
Never edits files, never pushes, never amends without being asked,
never stages `git add -A`. Refuses junk messages and gate failures.

**Level.** L3, `mode: subagent`.

**Triggers — user words.** **None normally.** A user talking to
project-lead should not say "commit this" — the system routes
commits through the lead that owns the work (build-lead for
feature work, fix-lead for fixes, system-lead for system
changes), and the lead routes to committer. The user should
never have to know `committer` exists.

**Triggers — system conditions.**
- The above, transitively: a lead needs a commit; the lead
  delegates to committer. The project-lead should not be
  in that chain.

**Why this edge is a drift.** The project-lead's own role
description says "no edits, no commits" and "you read broadly
and change almost nothing." But the live task allow-list
includes `committer: allow`. The role does not describe a
scenario in which project-lead *should* invoke committer.
The OLD ASPS used project-lead only for "lifecycle commits
such as mode changes" per its doc, and the current `local`
file says "should be removed — project-lead shouldn't route
commits." Today the live config *allows* a delegation that
the role says shouldn't happen.

**Recommended fix.** Remove `committer: allow` from
project-lead's live task list. Re-render from the catalog
(which is clean — it does not have this edge). This aligns
project-lead with "no commits" and removes the *allow* of
a delegation that has no documented scenario.

**Recontextualization (if this edge ever fires).** Project-lead
would treat the committer's return as a confirmation of the
change, not as a feature in itself: "Mode is now production;
the change is committed; here's the SHA." The user only sees
the *effect* of the commit (the mode is now production), not
the commit event.

---

## 3. The human gate (R-008)

The system rules (R-008) say: *"Architecture, rules, permissions,
security posture, and model-routing changes require human approval
— never an automated rewrite."* The OLD ASPS had R-009 (a stronger
version: rules/permissions/security/model-routing/*self-improvement*).
The current R-008 is the simplified form.

Project-lead escalates to the user — and does **not** delegate —
when the request is, or touches, any of:

1. **Architecture changes.** "Change how X is built", "redesign
   the system", "we need a new layer", "change the agent
   roster". Route to system-lead, but project-lead **stops the
   automation** at the design step: the user approves the
   design before system-lead authors.
2. **Rules changes.** "Change R-XXX", "add a rule", "remove a
   rule", "change the constitution". System-lead owns the
   authoring, but R-008 gates the rule itself. Project-lead
   holds the gate.
3. **Permissions changes.** "Add a new protected path", "loosen
   the deny on tool Y", "change the hook policy", any edit to
   `rules/**`, `.aspis/rules/**`, `.claude/settings.json`,
   `**/permissions*.yaml`, `profiles/defaults.yaml`. The
   governance subagent (per the OLD ASPS, a system-lead
   subagent) is the only path to mutate these; project-lead
   *is* the human gate.
4. **Security posture changes.** "Add a new secret pattern",
   "change the secret-scanner rule", "allow web search on
   agent X", "change the protected-path list". R-008 gates.
5. **Model-routing changes.** "Change which model the planner
   uses", "change the tier mapping", "change the per-agent
   override in `agent-models.yaml`". R-008 gates.
6. **Self-improvement (the OLD ASPS added this; current R-008
   covers it under "rules" and "permissions").** "The agent
   should change how it works", "tune the temperature",
   "change the skill list", "modify the prompt". R-008 gates.
7. **3 failed fix attempts (the fix-lead's hard cap).** The
   fix-lead writes `REVIEW_NEEDED` to the review queue and
   stops. Project-lead surfaces this as a user-facing
   decision: "fix-lead hit the 3-attempt cap; the cause is
   [structural / outside scope / unclear]. This needs your
   decision."
8. **Bootstrap re-run / new project onboarding.** The bootstrap
   agent is one-shot and self-deletes. A re-bootstrap or a
   second project requires a manual step. Project-lead holds
   that gate.
9. **`aspis doctor` reports a runtime defect that the
   system-lead cannot auto-fix.** "The system is broken in a
   way that requires a design decision, not a script." R-008
   gates.

**What project-lead does *not* do at the gate.**
- Project-lead does **not** ask "is this OK?" and then proceed
  on a yes — the user must approve the *specific* change with
  enough context to decide.
- Project-lead does **not** invent a default ("I'll proceed
  with X unless you say no"). R-008 is explicit: never an
  automated rewrite.
- Project-lead does **not** delegate the gate to a lead
  ("I'll let system-lead decide"). The gate is held at L1;
  the leads execute the *approved* change.

**The shape of the gate.** Project-lead presents the user with:
- what is being changed,
- the scope of the change (which files, which agents, which
  config),
- the alternative (do nothing, do X differently),
- the irreversibility (commit, deploy, break protected paths).

Then waits. The leads resume after the user approves.

---

## 4. What project-lead handles directly (never delegates)

Project-lead's `edit` and `write` are denied. The only write is
`aspis mode*` (the "one simple setting" the role owns). The rest
of what project-lead does is **read, classify, route, package,
recontextualize**. Specifically, project-lead handles directly:

1. **Project status questions.** "What's the state of F-XXX?",
   "what's the current mode?", "is the project healthy?" —
   project-lead reads L1 hot context (`CURRENT_STATE.md`,
   `RECENT_CHANGES.md`, `FILE_REGISTRY.yaml`, `CODE_MAP.md`),
   runs `aspis status` / `aspis doctor` / `git status` /
   `git log`, and answers. **No delegate.**
2. **Project guidance.** "What should I do next?", "is this
   the right next step?", "where are we?" — the
   `project-guidance` skill produces an answer from the
   project's current state. **No delegate.**
3. **Mode changes.** `aspis mode <vibe|mvp|production>` — the
   one write project-lead owns. This is the only "lifecycle
   commit" that may originate at L1.
4. **Health detection and routing.** "The project is unhealthy
   in this specific way" — project-lead runs the health check
   via `aspis doctor` (read-only), detects the problem,
   **routes to system-lead or the relevant specialist**.
   Project-lead never fixes the health issue itself.
5. **Recontextualization.** Every delegate's return passes
   through project-lead before reaching the user. This is
   the load-bearing role: "only you can say what its result
   means for the whole project."
6. **The human gate (R-008).** Held at L1. Never delegated.
7. **Direction protection.** Catch drift, misalignment, and
   workflow bypass — refuse the request, or reframe it, or
   route to a different lead. Project-lead is the system's
   immune system against "the wrong work, in the wrong way,
   by the wrong lead."

**Why these are not delegated.**
- Status / guidance / mode are L1's defining intelligence; the
  L2 leads don't have the project-wide view.
- Health detection is a read, not a fix; delegating a read is
  an anti-pattern (a delegate is for *work*, not for *answers
  about the project*).
- Recontextualization is *what makes project-lead the
  intelligence layer*. Delegating it would make project-lead
  a router, which the role explicitly is not.
- The human gate is a single point of accountability; splitting
  it across leads would create "who actually approved this?"
  ambiguity.

---

## 5. The "subordinate lead never routes to another lead" rule

From the live project-lead file: *"A subordinate lead never
routes to another lead; each fans out to its own workers, and
all changes to ASPIS itself go through `system-lead`."*

This is a **fan-out tree, not a mesh**. The rule has three
parts:

1. **No lead-to-lead-to-lead.** From L1, project-lead
   delegates to a lead. That lead delegates to its own
   workers. The workers do not delegate to other leads' workers.
   The longest chain is L1 → L2 → L3.
2. **Each lead owns its fan-out.** A planning-lead delegates
   to `clarify` and `task-decomposer`; a build-lead delegates
   to `general-builder`; a fix-lead delegates to
   `gate-fixer` (or to its own triage). The fan-out stays
   inside the lead's own scope.
3. **All ASPIS-itself changes go through system-lead.** Not
   because no other lead *could* author an asset, but because
   the catalog's byte-parity invariant requires a single
   authorship channel. The system-lead is the only lead that
   may modify protected runtime/catalog assets.

**Why this rule exists.**
- **The lead-to-lead case is the bottleneck and "overwhelmed"
  agent failure mode.** Cursor's research calls this out: a
  lead that "needs to reach another lead" starts carrying
  context for both, becomes a serial bottleneck, and
  eventually degrades ("sleep, refusal, premature
  completion").
- **The lead-to-lead-to-lead case is the centralized
  integrator anti-pattern.** A lead that all others route
  through is a single point of failure.
- **System-lead as the single authoring channel preserves
  the byte-parity moat.** The catalog regenerates live;
  anyone but system-lead editing live is a violation.

**What this means for project-lead.**
- Project-lead's delegation is **one hop at a time** to a
  lead. Project-lead does not say "planning-lead, ask
  build-lead to …" — project-lead talks to build-lead
  itself if the question is build-shaped.
- Project-lead is the **only** agent that can route across
  leads. It is the L1 entry point for cross-domain requests.
- If a lead returns "this needs X from lead Y," project-lead
  absorbs that and re-routes. The lead does not name a peer
  lead; it names the *problem* ("the cause is in protected
  paths — defer to system-lead") and project-lead re-routes.

---

## 6. Orchestration patterns

Project-lead composes a path from the actual request and project
state, not from a fixed table. The patterns it composes from
(from `old-asps-deep-analysis-1.md` § 8, adapted to the current
roster):

### 6.1 Single-hop (most common)

**Shape.** project-lead → one lead → one worker → return.

**When.** A request that maps cleanly to one lead's lane and
does not need the others:
- "Build F-XXX" → build-lead → general-builder.
- "Review this diff" → reviewer (one reviewer, one verdict).
- "Fix the gate fail" → fix-lead → (gate-fixer).
- "Research X" → research-lead → (one packaged note).
- "Add a skill" → system-lead → (opencode-author or
  claude-author).
- "Where is X?" → project-explorer.

**Triggers.** A request with a single intent that fits one
lead's lane. Most user requests are this.

### 6.2 Sequential pipeline

**Shape.** project-lead → lead A → lead B → lead C → return.

**When.** A request that needs each phase's artifact as the
next phase's input:
- **Feature:** planning-lead → (plan-critic) → build-lead →
  (per-task) reviewer → committer. (Plan-critic is the
  reviewer's *plan* mode; the reviewer is invoked from the
  planner's lifecycle, not as a separate top-level call.)
- **Defect:** fix-lead → (gate-fixer) → reviewer →
  committer.
- **System change:** system-lead → reviewer (for validation)
  → committer.

**Triggers.** A request that names a *lifecycle* — "build
this end-to-end", "fix and verify", "change the system and
validate". Project-lead composes the sequence; each lead
hands off to the next; project-lead recontextualizes the
final return.

### 6.3 Dynamic handoff

**Shape.** project-lead → lead A → (return says "actually,
this needs lead B") → project-lead re-routes → lead B.

**When.** A request that *looks* like one lead's lane but
turns out to be another:
- "Build this" → build-lead → returns "this is a fix, not a
  build — the failing test was the bug" → project-lead
  re-routes to fix-lead.
- "Plan this" → planning-lead → returns "this is a system
  change, not a feature" → project-lead re-routes to
  system-lead.
- "Fix the broken run" → fix-lead → returns "this is a
  runtime defect, not a code defect" → project-lead
  re-routes to system-lead.
- "Review this" → reviewer → returns "this is a planning
  question, not a review" → project-lead re-routes to
  planning-lead.

**Triggers.** Any case where the lead's return names a
*problem* (not a peer lead), and project-lead's
re-routing is the dynamic. The lead does **not** name the
peer lead — it names the problem and the gap, and
project-lead decides the next hop.

### 6.4 Fan-out (project-explorer only)

**Shape.** project-lead → project-explorer(s) → return.

**When.** A request that needs a focused structural lookup
that the L1 context-ladder can't satisfy:
- "Where is the model resolver?" → one project-explorer,
  one answer.
- "Which files import `protect.py`?" → one project-explorer,
  one answer.

**Note.** This is **not** multi-agent parallel work in the
Cursor sense. project-explorer is a leaf, fast, cheap, and
disposable. The fan-out is for *reads*, not for *work*.
True multi-agent parallel work (multiple builders on a
multi-component feature) is **parked** in ASPIS — proven for
truly parallel work, unproven for the dependency-ordered
feature work ASPIS does. When that work is unblocked,
project-lead would compose a multi-builder fan-out via
build-lead (not directly).

### 6.5 Pattern selection — the project-lead's decision

Project-lead picks the pattern by:
1. **Classify the request** (`request-classification` skill).
2. **Read the L1 hot context** (`project-awareness` +
   `context-ladder` L1). If the project is mid-feature, the
   pattern must compose with the in-flight work, not around
   it.
3. **Pick the lead** (`lead-routing` skill). If the request
   maps to one lead cleanly: single-hop. If the request is a
   lifecycle: sequential pipeline. If the classification is
   uncertain: dynamic handoff with a re-route trigger in
   the packet.
4. **Package the context** (`context-packaging` skill) with
   `intent · context · constraints · references · expected
   outcome`.
5. **Recontextualize the return** before the user sees it.
   This is the L1-only step; it is what makes project-lead
   the intelligence layer, not a router.

---

## 7. The complete routing matrix (user words → delegate)

| User words (sample) | Delegate | Pattern |
|---|---|---|
| "plan …", "spec out …", "scope …", "decompose …" | planning-lead | single-hop |
| "build …", "implement …", "code …", "ship …" | build-lead | single-hop |
| "review …", "audit …", "is this OK", "second opinion" | reviewer | single-hop |
| "add a skill", "add an agent", "fix a broken runtime", "doctor is failing", "change the model", "bootstrap" | system-lead | single-hop |
| "fix …", "broken", "regression", "gate failed", "test fail" | fix-lead | single-hop |
| "research …", "look up …", "current best practice", "what's the latest docs for …" | research-lead | single-hop |
| "test …", "write tests for …", "coverage" | test-lead **(dangling — see §2.7)** | single-hop (currently no-op) |
| "where is X", "which files import Y", "codebase map" | project-explorer | single-hop |
| "commit this" | **route through the owning lead, not directly to committer** (see §2.9) | sequential pipeline |
| "build F-XXX end-to-end" | planning-lead → build-lead → reviewer → committer | sequential pipeline |
| "fix the broken run" | fix-lead → reviewer → committer | sequential pipeline |
| "this is broken — and also we need to plan the rewrite" | fix-lead → (re-route) planning-lead | dynamic handoff |
| "change to production mode" | project-lead handles directly (`aspis mode production`) | L1 direct |
| "what's the state of F-XXX?" | project-lead answers directly | L1 direct |
| "is the project healthy?" | project-lead runs `aspis doctor`, reports | L1 direct |
| "change the rules", "add a protected path", "change the model routing", "change the security posture", "tune the agent's prompt" | **R-008 human gate** (project-lead holds) | L1 gate |

---

## 8. Drift summary (what to fix)

| # | Drift | Where | Risk | Fix |
|---|---|---|---|---|
| 1 | `committer: allow` in project-lead's task list | live frontmatter | Allows a delegation the role says shouldn't happen | Remove; re-render from catalog |
| 2 | `test-lead: allow` in project-lead's task list, but test-lead is not in `.opencode/agents/` | live frontmatter + missing file | Dangling edge; the runtime can't honor the routing | Re-render test-lead from catalog (preferred), or remove the edge |
| 3 | Same `test-lead: allow` issue in build-lead and fix-lead | live frontmatter of those leads | Same | Same |
| 4 | system-lead `websearch: allow` (live) vs `deny` (catalog) | system-lead live frontmatter | Permission widening vs catalog | Reconcile: comment in live OR set to deny |
| 5 | Reviewer / committer / research-lead in others' task lists but not in catalog | multiple agents' frontmatter | Drift; catalog is source of truth | Add to catalog (likely catalog gaps, not live defects) |
| 6 | committer lacks `temperature: 0.1` | committer frontmatter | Determinism | Add `temperature: 0.1` |

Items 1, 2, 3 are the edges that affect project-lead directly.
Item 6 is the only committer-shape defect that matters for
project-lead's "should I delegate to committer?" question —
and the recommended fix is "remove the edge," not "fix the
committer."

---

## 9. One-paragraph summary

Project-lead is the L1 intelligence layer and the only agent the
user talks to. It owns **9 delegation edges** in the live runtime:
7 L2 leads (planning, build, reviewer, system, fix, research,
test) and 2 L3 helpers (project-explorer, committer). Of the 9,
**2 are drifted today** — `committer` is allowed but should not
be (it contradicts the role's "no commits" rule), and `test-lead`
is allowed but is not deployed in `.opencode/agents/`. The other
7 are correct and load-bearing. Project-lead holds the human
gate (R-008): architecture, rules, permissions, security
posture, and model-routing changes never auto-rewrite. The
subordinate-leads-never-route-to-each-other rule keeps the
system a fan-out tree, not a mesh, with project-lead as the
only cross-lead router. The orchestration patterns are
single-hop (most), sequential pipeline (lifecycles), and
dynamic handoff (re-route when a return says "actually, this
is a different lead's lane"). Project-lead handles project
status, guidance, mode changes, health detection, and
recontextualization directly; everything else is delegated with
a 5-field context packet (`intent · context · constraints ·
references · expected outcome`).

---

*See also: `current-aspis-agents-2.md` for the per-agent live vs.
catalog drift, `old-asps-deep-analysis-1.md` for the ancestor
R-009 routing table, and `.aspis/rules/system-rules.md` for
R-001…R-009 (R-008 is the human gate).*
