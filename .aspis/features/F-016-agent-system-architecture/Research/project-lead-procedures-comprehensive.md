# Project-Lead — Comprehensive Procedural Reference (Industry-Synthesized)

> **Status:** design doc — the spec the project-lead agent body should be
> checked against. Companion to `project-lead-procedures.md` (the long
> reference); this doc emphasizes **industry pattern synthesis** — the
> four surveyed systems (Claude Code, Cursor, GitHub Copilot, Devin) and
> how each pattern manifests in ASPIS's 12 request flows.
>
> **Sources synthesized:**
> 1. `local/AGENT-SYSTEM-ARCHITECTURE.md` (the ASPIS spine)
> 2. `local/agents/project-lead.md` (ASPIS design intent)
> 3. `.opencode/agents/project-lead.md` (ASPIS live runtime)
> 4. `.aspis/features/F-016-agent-system-architecture/Research/core-loops-2026.md`
> 5. `.aspis/features/F-016-agent-system-architecture/Research/old-asps-system-design-3.md`
> 6. `.aspis/features/F-016-agent-system-architecture/Research/project-lead-procedures.md`
> 7. `core-loops-2026.md` source table (Anthropic, Cursor, GitHub, Cognition, METR)
>
> **Audience:** anyone who edits the project-lead body, the project-lead
> itself when reasoning about which flow to take, and reviewers verifying
> the design.

---

## 0. Why this document exists

`project-lead-procedures.md` enumerates the 12 flows in detail. This
document answers the *prior* question: **which proven industry patterns
underwrite each flow, and where does ASPIS adopt, adapt, or reject them?**

The four surveyed systems share a common shape but diverge in the
mechanics. Knowing the lineage makes the ASPIS-specific choices
defensible.

| System | Entry shape | Routing authority | Mode dial | Deterministic gate | Reviewer isolation |
|---|---|---|---|---|---|
| **Claude Code** (Anthropic, 2026) | CLI REPL with `/plan`, `/code-review` | The user picks; no L1 router | Implicit (plan-mode on/off) | Tests / build / screenshot | `/code-review` subagent in fresh context |
| **Cursor** (Composer + Bugbot) | IDE chat; `@agent` mention; Composer | Cursor's orchestrator; no user-facing L1 | Tab · Composer · Cloud Agent (3 dials) | Build + tests | Bugbot is a separate agent in different context |
| **GitHub Copilot** (cloud agent) | GitHub issue → cloud env | The cloud agent picks | Agent Mode (IDE) · Cloud Agent (autonomous) | Build + tests + lint | PR review (Copilot PR Reviews bot) |
| **Devin** (Cognition) | Web chat → sandboxed VM | Devin itself | Single mode (autonomous) | Tests + screenshot | Internal planner/executor/evaluator triad |
| **ASPIS project-lead** | Single chat with the human | **Project Lead (L1)** classifies, routes, recontextualizes | **3 modes** (vibe/mvp/production) from `modes.yaml` | **Five universal gates** (ruff-format, ruff-check, mypy, pytest, byte-parity) | **Reviewer** lead (read-only, separate context) **+** per-task sub-agent reviewer |

The fundamental choice ASPIS makes that the others do not: **there is
exactly one L1 entry point — project-lead.** Claude Code, Cursor, and
Copilot all let the user address any agent directly; Devin is a single
agent. ASPIS's narrow L1 with classified L2 delegation is the
"narrow-role-per-agent" lesson (Cursor's "self-driving codebases" §4)
applied to the L1 layer.

---

## 1. The master frame: 5 phases, 12 flows, 1 packet shape

Every request — every one of the 12 flows — runs inside the same
five-phase frame (`project-lead-procedures.md` §1):

```
ENTRY → CLASSIFY → CONTEXT → ACT → RECONTEXTUALIZE → EXIT
```

The 12 flows are the *atoms*. The packet shape is the *handoff* that
makes them composable. The recontextualization protocol is the *output*
that makes the system more than the sum of its parts.

### 1.1 Industry pattern map (which pattern underwrites which phase)

| Phase | ASPIS mechanism | Industry source | What we adopt / adapt / reject |
|---|---|---|---|
| **ENTRY** | `aspis bootstrap --check` (transient gate) + `aspis context` (L1 in one call) | Claude Code's "explore before plan" (best-practices) | **Adopt** — the explore-then-classify discipline. **Adapt** — we make it a single deterministic call, not a multi-step REPL. |
| **CLASSIFY** | `request-classification` skill → type + complexity + path | Cursor's "size the work to the ceremony" (multi-agent blog) | **Adopt** the discipline. **Adapt** — we pre-route to a single L2 lead; Cursor fanned out to subplanners. |
| **CONTEXT** | `context-ladder` skill (L1→L4, stop early) | Claude Code's "load minimum context" (best-practices) | **Adopt** the ladder discipline. **Adapt** — we generate a deterministic brain (FILE_REGISTRY, CODE_MAP) instead of letting the LLM scan. |
| **ACT** | `lead-routing` + `context-packaging` → one `task` call to a single L2 lead | Cursor's "planner delegates, workers context-isolate" (self-driving codebases) | **Adopt** the recursive planner-workers pattern. **Adapt** — we cap at 2 levels (D-028); Cursor's 3-level recursion failed on OpenCode. |
| **RECONTEXTUALIZE** | The 4-step protocol: verify artifact, translate, surface deltas, state next step | All four (Claude Code paraphrases; Cursor summarizes; Copilot bot comments; Devin reports) | **Adopt** the discipline. **Adapt** — we make the recontextualization the *only* place project-lead applies judgment to a specialist's output; never second-guess the verdict. |
| **EXIT** | `aspis doctor` + trace event + state update | Cursor's "Auto-review" classifier (4% block rate); METR's evaluator | **Adopt** the deterministic-substrate idea. **Adapt** — we use a 5-gate universal set, not a per-action classifier. |

### 1.2 The pre-flight sequence (run during ENTRY)

```
1. aspis bootstrap --check          # one-time; transient
2. aspis context                    # refresh brain + print L1 hot
3. git status                       # clean tree?
4. git log --oneline -10            # what's the recent history?
5. cat .aspis/current/active_feature.json
6. cat .aspis/context/CURRENT_STATE.md
7. cat .aspis/context/RECENT_CHANGES.md
```

**Source mapping:**
- `aspis context` ← Claude Code's "explore before plan" made deterministic
- `git status` + `aspis preflight` ← Copilot's "clean-tree-precondition"
  + Claude Code's "if the work is starting from an unknown state, stop"
- `active_feature.json` ← ASPIS-specific (D-013 / D-014); no industry
  equivalent — Devin tracks session state, but not as a file

**Direct handle vs delegate:** all of these are *read-only*; project-lead
runs them itself. They are the project's deterministic substrate, not a
task to delegate.

**Validation gate:** if any of steps 1, 2, or 3 fails, the flow branches
into Flow 12 (Health Detection) or stops for the user.

---

## 2. The 12 request flows — industry-synthesized

For each flow, this document adds **Industry patterns** (which surveyed
systems do this, and how), on top of the per-flow procedure from
`project-lead-procedures.md`. The fields per flow are:

- **Trigger** (user words that activate the flow)
- **Industry patterns** (which of the 4 systems do this; what we adopt)
- **Files read at each step** (the project-lead's reads, in order)
- **Scripts / commands run** (deterministic substrate)
- **Validation gates** (what must pass before the next step)
- **Direct handle vs delegate** (and the reason)
- **Error handling** (what if a pre-check fails)
- **Escalation** (when to stop and ask the user)
- **Context packet shape** (the 5-field shape, contents)
- **Recontextualization protocol** (the 4-step output)

### Flow 1 — Session Start / Bootstrap

> **Trigger:** the user opens a new session. Often no request — just "hi"
> or "what's going on?".

**Industry patterns:**
- Claude Code: the REPL's "first turn = explore + clarify intent"
  (best-practices §Explore).
- Cursor: the IDE loads project context (open files, git status)
  automatically.
- Copilot: the cloud agent starts in a fresh worktree.
- Devin: each session is a new VM with a snapshot.
- **ASPIS:** the bootstrap gate (transient) + `aspis context` + a
  3–4-file read of L1 hot context. We adopt Claude Code's "explore
  first"; we reject Copilot's "fresh worktree" (too heavy for chat);
  we adapt Devin's "VM per session" into "one call that loads L1".

**Files read (in order):**
1. `aspis bootstrap --check` output (transient — first message only)
2. `.aspis/context/CURRENT_STATE.md` (from `aspis context`)
3. `.aspis/context/RECENT_CHANGES.md` (from `aspis context`)
4. `.aspis/current/active_feature.json` (from `aspis context` or `cat`)
5. `git status` output

**Scripts / commands:**
```
aspis bootstrap --check
aspis context
git status
git log --oneline -10
```

**Validation gates:**
- `bootstrap --check` returns `Bootstrapped` (or the bootstrap agent
  runs; project-lead does not bootstrap itself)
- `aspis context` exits 0 (brain is readable)
- `git status` is clean or expected

**Direct handle vs delegate:** **Direct** — Flow 1 is read-only. The
output is a 3–5 line status report to the user. No delegation.

**Error handling:**
- `bootstrap --check` returns `Not bootstrapped` → delegate to
  `bootstrap` (transient) with the user's intent; stop reading.
- `aspis context` fails → the brain is broken → **Flow 12** (route to
  system-lead).
- `git status` shows conflict markers → **stop, do not touch**, show
  the user, ask.
- `.aspis/` missing → not a project, or wrong directory; show working
  dir, ask.

**Escalation:** if the project is broken and the user has not asked
for anything, ask once, concisely, and offer to route to system-lead
if they want.

**Context packet shape:** none — Flow 1 is direct. (The "packet" for
bootstrap is a one-liner: "bootstrap this empty project".)

**Recontextualization protocol:**

```
1. Verify the project is live (bootstrap --check, doctor).
2. Translate state into a 3–5 line report: name, mode, active, health, recent.
3. Surface deltas: anything new (new findings, a feature closing, a
   phase change).
4. State the next step: "ready to start a feature", "F-XXX is in
   build; want to look at it?", "doctor is red; route to system-lead?".
```

**Recontextualization example (good answer):**
```
ASPIS — python project. Mode: production. Active: F-015 (closed
2026-06-25). F-016 (agent system architecture) is in plan.
Health: 0 FAIL, 0 WARN. Last change: 57afbda docs(F-016): fix synthesis
doc blockers, 2h ago.
Ready to start a feature. Tell me what to build.
```

---

### Flow 2 — Feature Request ("build X", "start feature Y")

> **Trigger:** the user wants new behavior. "Build user auth", "start a
> new feature for export to PDF", "add a settings page".

**Industry patterns:**
- **Claude Code:** the canonical 4-phase loop is
  *explore → plan → implement → commit* (best-practices). Adopted
  verbatim as Flow 2's spine, with the planning kit (P0–P9) as the
  "plan" phase.
- **Cursor:** the "describe the diff in one sentence → skip the plan"
  rule (best-practices). Adopted as the "is it trivial? route straight
  to build-lead" branch in Step 2.
- **GitHub Copilot:** "research → plan → implement → iterate → PR"
  (cloud-agent doc). Adopted as the planning lead's procedure.
- **Devin:** "long-term reasoning + planning before any code"
  (Introducing Devin). Adopted as the planning lead's
  `requirement-clarification` discipline.
- **ASPIS-specific:** the `mode` dial (vibe/mvp/production) is the
  unique addition — none of the four systems have a 3-mode rigor dial;
  they have at most an on/off "plan mode" or two agent modes.

**Files read (in order):**
1. L1 hot: `.aspis/context/CURRENT_STATE.md`, `RECENT_CHANGES.md`
2. Mode resolution: `.aspis/config/modes.yaml` (the planning lead reads,
   but project-lead confirms the chosen mode)
3. `.aspis/config/project.yaml` (project default mode)
4. `.aspis/features/<active>/SPEC.md` (if a related feature exists)

**Scripts / commands:**
```
aspis context                   # refresh if RECENT_CHANGES is stale
aspis mode                      # confirm current
aspis preflight                 # clean tree? right branch?
cat .aspis/config/project.yaml  # project default mode
```

**Validation gates:**
- `aspis preflight` exits 0 (clean tree, right branch, no open findings)
- A mode is set (or project-lead sets one)
- The request passes the "feature, not trivial" classifier

**Direct handle vs delegate:** **Delegate** to `planning-lead` (default
feature path) or `build-lead` (trivial one-sentence diff). Project-lead
**never** plans or builds itself.

**Error handling:**
- `preflight` shows uncommitted changes → **stop and ask**: "you have
  uncommitted changes; stash, commit, or route to system-lead to
  investigate?"
- `preflight` shows wrong branch → ask, do not switch
- `preflight` shows open findings → surface them, ask whether to
  address now or proceed
- Planning lead returns without artifacts → ask the user or re-delegate
  with a clarified packet
- Plan-critic verdict = `rejected` → surface to user; do not auto-retry
- Mode was wrong → ask the user; project-lead can change mode with
  `aspis mode`, then re-delegate

**Escalation:**
- Mode = `production` and the change touches `rules/**`, `.opencode/`,
  permissions, or model-routing → **stop; ask the user** (R-009)
- User wants architecture-level changes that aren't a "feature" →
  **Flow 7** (System Change) instead

**Context packet shape:**
```yaml
intent: |
  Build <one-sentence outcome the user wants>.
context: |
  L1 brain state: mode, active feature, open findings.
  Project standard: stack, profile, current mode.
  Active feature: <F-XXX if any> (for awareness, not blocking).
constraints: |
  R-001: scope = <feature's allowed files; new feature, will be set by planning>.
  R-002: gates must pass.
  R-003: do not edit rules, AGENTS.md, or agent bodies.
  R-004: only committer commits.
  R-005: tests are part of the spec.
  Mode: <vibe|mvp|production> with knobs from modes.yaml.
  User-stated: "don't change X", "must use Y", etc.
references: |
  .aspis/context/CURRENT_STATE.md
  .aspis/context/IDENTITY.md (project = one-source for stack)
  .aspis/config/modes.yaml (knobs for the mode)
  Any existing related SPEC.md
expected_outcome: |
  planning-lead returns: SPEC.md, PLAN.md, TASKS.md (mode-scaled),
  task packets in tasks/T-NN.md, a plan-critic verdict.
  Routing: project-lead hands off to build-lead when plan is approved.
```

**Recontextualization protocol:**

```
1. Verify artifacts exist (SPEC.md, PLAN.md, TASKS.md, plan-critic verdict).
2. Translate, don't paste: the user wants to know what the plan means,
   not the SPEC verbatim.
3. Surface deltas: what changed (mode, scope, removed stories, plan-critic findings).
4. State the next step:
   - "Plan approved; handing to build-lead."
   - "Plan-critic flagged N items; here's the top one. Proceed?"
   - "Plan rejected; here's why. Want to revise or drop?"
```

---

### Flow 3 — Status Query ("what's the state?", "where are we?")

> **Trigger:** the user asks about project state.

**Industry patterns:**
- **Claude Code:** "ask Claude to explain the code or summarize state"
  (best-practices). Adopted.
- **Cursor:** the chat panel always shows the active file + branch
  context. We reject the ambient UI; we make it an explicit answer.
- **Copilot:** the cloud agent emits a session report. We adapt —
  the report is recontextualized, not raw.
- **Devin:** session-end summary. Adopted as the "what's next" line.
- **ASPIS-specific:** the `aspis status` + `aspis findings` + active
  feature pointer is the deterministic substrate; the recontextualized
  answer is the LLM output.

**Files read (in order):**
1. `.aspis/context/CURRENT_STATE.md`
2. `.aspis/context/RECENT_CHANGES.md` (last 5–10)
3. `.aspis/current/active_feature.json` (if exists)
4. `.aspis/features/<F-XXX>/SPEC.md` (if user named a feature)
5. `.aspis/features/<F-XXX>/tasks/` (if user named a feature, for
   per-task state)

**Scripts / commands:**
```
aspis context                  # only if RECENT_CHANGES is stale
aspis status                   # if asked "is it healthy"
aspis doctor                   # if asked "is it healthy"
aspis findings                 # if asked "what's open?"
```

**Validation gates:** none (read-only flow). If the brain is empty
(no `CURRENT_STATE.md`), run `aspis context`; if it still fails, route
to system-lead.

**Direct handle vs delegate:** **Direct** — Flow 3 is read-only and the
answer is in the brain. **Exception:** "where is X in the code?" is a
code-locator question, not a status question → delegate to
`project-explorer` (L3 helper).

**Error handling:**
- Brain is empty → run `aspis context`; if it fails, route to
  system-lead
- User asks "where is X in the code?" → delegate to `project-explorer`
- User asks "why did T-004 take so long?" → this needs trace analysis →
  delegate to `research-lead` (the trace spine is its domain)

**Escalation:** none. Status is read-only. The *answer* may suggest
an action, but the answer itself is always answerable.

**Context packet shape:** none — direct answer.

**Recontextualization protocol:**

```
1. Verify the brain is current (RECENT_CHANGES not stale).
2. Translate state into the canonical 3-line answer:
   - WHAT: the active feature (or "no active feature").
   - WHERE: phase + tasks done/total.
   - WHAT'S NEXT: the next concrete step the user can take.
3. Surface deltas: any new findings, any mode change, any uncommitted work.
4. State the next step: a question that gives the user the choice.
```

**Recontextualization example:**
```
F-016 (agent system architecture) is in plan, 0 of 5 tasks done.
Last change: 57afbda docs(F-016): fix synthesis doc blockers, 2h ago.
Health: 0 FAIL, 0 WARN, 0 open findings.
Next: planning-lead is producing the SPEC; you'll see it when ready.
Want to look at the draft, or wait?
```

---

### Flow 4 — Defect / Fix ("X is broken", "test failed")

> **Trigger:** the user reports a defect or a test fails.

**Industry patterns:**
- **Claude Code:** "if a check fails, Claude iterates in the same
  message; if Stop-hook blocks, the agent keeps working until it
  passes" (best-practices). Adopted in spirit; we adapt by routing
  to fix-lead (subagent) instead of looping in the main thread.
- **Cursor:** Bugbot finds bugs in PR review. Adopted as the **reviewer**
  escalation, not the fix path.
- **Copilot:** "fix bugs" + "address technical debt" are cloud agent
  capabilities. Adopted; routing to fix-lead.
- **Devin:** "SWE-bench" framing (localize → repair → validate, per
  Agentless) — **rejected** as a sub-loop; ASPIS's fix-lead is a
  separate subagent, not an in-line loop.
- **ASPIS-specific:** the `root-cause-analysis` skill is the unique
  addition; no surveyed system has a dedicated RCA skill.

**Files read (in order):**
1. The failing test / gate output (user-supplied or via `git log`)
2. `.aspis/context/CURRENT_STATE.md` (active feature, mode)
3. `.aspis/features/<F-XXX>/SPEC.md` (FR-### this work satisfies)
4. `.aspis/features/<F-XXX>/PLAN.md` (if exists)
5. The most recent commit(s) around the failure (`git log -5`)

**Scripts / commands:**
```
git status
git log --oneline -5
# If user mentioned a specific test:
python -m pytest <path>::<test_name> -x
# If a gate failed:
aspis doctor
aspis preflight                # re-confirm clean state
```

**Validation gates:**
- The failure is reproducible (fix-lead's first job, not project-lead's)
- The fix's scope is in the active feature's `scope.allowed` (R-001)
- The fix will not delete or weaken a test (R-005)

**Direct handle vs delegate:** **Delegate** to `fix-lead` (default).
The fix-lead has `root-cause-analysis`, `corrective-fix`,
`scope-control`, and `selective-testing` skills.

**Symptom → first-owner routing table:**

| Symptom | First owner |
|---|---|
| "test is failing" / "gate is red" / "regression" | `fix-lead` |
| "I think the design is wrong" / "this approach won't work" | `planning-lead` (revisit plan) |
| "we need a new test" / "coverage is low" | `test-lead` |
| "the build itself is broken" / "runtime won't load" | `system-lead` |
| "I want to add a feature to address this" | re-classify as feature (Flow 2) |

**Error handling:**
- Fix-lead reports "needs plan" → escalate to user; do not auto-loop
  into planning-lead (bypasses the user's awareness)
- Fix-lead reports 3 failed attempts → `REVIEW_NEEDED` → escalate to
  user (fix-lead's hard cap, not project-lead's)
- Failing test was user-written, not a project test → still fix-lead,
  but flag that R-005 (no weakening) does not apply
- Symptom is a *design* problem → re-route to `planning-lead` with
  fix-lead's report as a reference; user must confirm

**Escalation:**
- Fix touches a file outside the active feature's `scope.allowed` →
  stop, ask the user
- Fix changes public API, schema, or config format → stop, ask the
  user (R-009-adjacent)
- The defect is a security vulnerability → still fix-lead, but
  mention security to the user; consider follow-up reviewer pass

**Context packet shape:**
```yaml
intent: |
  Reproduce <symptom>, find root cause, apply minimal diff,
  verify with the gate that was red, return a fix report.
context: |
  <test output, gate output, error trace, recent commits>
  <the SPEC/ACCEPTANCE this work is supposed to satisfy>
  <the current mode (production = stricter)>
constraints: |
  R-001: only edit files in <feature's allowed list>.
  R-002: the gate must be green.
  R-005: do NOT delete or weaken the failing test; add a regression
         test if one is missing.
  Mode-derived: production = no scope creep; mvp/vibe = OK to address
                a small adjacent bug.
  Hard cap: 3 attempts; if still failing, return REVIEW_NEEDED.
references: |
  <the failing test path>
  <the SPEC FR-### the work is supposed to satisfy>
  <the active feature's PLAN.md>
expected_outcome: |
  fix-lead returns: FIX_REPORT with root cause, minimal diff,
  gate evidence (test/lint/type), and the commit message.
  Project-lead will then hand to committer.
```

**Recontextualization protocol:**

```
1. Verify the artifact exists (the fix commit, the passing test).
2. Translate: the user wants the one-line cause + the one-line fix,
   not the report.
3. Surface deltas: which file, which test, before/after evidence.
4. State the next step:
   - "Fixed; root cause: <line>. Committing via committer."
   - "Couldn't reproduce; please share the exact command/output."
   - "3 attempts failed; here's fix-lead's diagnosis. Want to revisit
      the plan, or hand to a human?"
```

---

### Flow 5 — Review Request ("review this diff", "is this safe?")

> **Trigger:** the user wants a verdict on a diff.

**Industry patterns:**
- **Claude Code:** the canonical pattern is "adversarial review in
  fresh context — a subagent reviews the diff and reports gaps"
  (best-practices). Adopted verbatim as the per-task sub-agent
  reviewer routing.
- **Cursor Bugbot:** "a separate agent reviewing PRs in a different
  context from the writing agent; finds 10% more bugs" (Bugbot
  updates). Adopted as the **reviewer** lead's design.
- **Copilot:** the cloud agent emits a PR; Copilot PR Reviews is a
  separate bot. Adopted.
- **Devin:** the evaluator subagent is internal; rejected as a
  sub-loop — ASPIS's reviewer is a separate subagent with its own
  context.
- **ASPIS-specific:** the `quality-review` skill's 9 dimensions
  (correctness, scope, architecture, maintainability, reliability,
  security, performance, standards, docs) — the unique addition;
  the others have at most 3-4 lenses.

**Files read (in order):**
1. `git diff main..HEAD` (or the user-specified range)
2. `.aspis/features/<F-XXX>/SPEC.md` (the FR-###/SC-### to check against)
3. `.aspis/features/<F-XXX>/feature.yaml` (scope.allowed / forbidden)
4. `.aspis/context/ARCHITECTURE.md` (as-built; reviewer checks fit)
5. `.aspis/config/constitution-checks.yaml` (the reviewer's owned checks)

**Scripts / commands:**
```
git status                     # confirm clean tree
git diff <range>                # the diff
git show <commit>              # if user pointed at a commit
```

**Validation gates (project-lead's pre-check):**
- The diff matches the active feature's `scope.allowed` (R-001 quick
  check). If not → **flag to user immediately**, do not waste the
  reviewer's context.
- The diff is not empty.
- The reviewer has a `SPEC.md` to check against.

**Direct handle vs delegate:** **Delegate** to `reviewer` (L2 lead) for
the full multi-lens review. **For per-task reviews during a build**, the
build-lead routes them itself — project-lead does **not** intercept.

**Review routing decision:**
- "review F-XXX" (meta-review of the whole feature) → `reviewer` lead
- "is this commit safe to ship?" (single-commit review) → `reviewer`
- "look at this PR" → `reviewer`
- "did build-lead do T-NN right?" (per-task during build) → build-lead's
  own routing; do not intercept

**Error handling:**
- Reviewer returns no verdict (drifted) → re-delegate once with a
  clarified packet; if it still drifts, route to system-lead (the
  reviewer itself is broken)
- Diff is empty → tell the user
- Diff is huge and reviewer timed out → ask the user: review in pieces,
  or raise the budget

**Escalation:**
- Reviewer flags a security issue → tell the user; do not auto-route
  to fix-lead (security is a user call)
- Reviewer flags an architecture issue → that's a planning-level
  change; route to `planning-lead`, not `build-lead`
- Reviewer verdict = `rejected` → stop. Do not override.

**Context packet shape:**
```yaml
intent: |
  Adversarial review of <diff>. Render one of:
  approved / approved with notes / changes required / rejected.
context: |
  <the diff>
  <the SPEC FR-### / SC-### this work is supposed to satisfy>
  <the mode (production = multi-lens; mvp = standard; vibe = light)>
  <the feature's scope.allowed / scope.forbidden>
constraints: |
  Read-only. No edits. No "while you're at it" changes.
  Findings: located (file:line), specific, actionable.
  Use quality-review + acceptance-decision skills.
  Reviewer checks the constitution-checks it owns.
references: |
  the SPEC, the PLAN, the active feature's feature.yaml
  .aspis/config/constitution-checks.yaml
  .aspis/context/ARCHITECTURE.md
expected_outcome: |
  REVIEW_REPORT with verdict and findings.
  Project-lead will route changes-required back to build/fix lead
  and approved to committer.
```

**Recontextualization protocol:**

```
1. Verify the artifact exists (REVIEW_REPORT).
2. Translate the verdict into the next concrete action.
3. Surface deltas: which findings are blockers vs notes; which are
   scope/security/architecture.
4. State the next step:
   - "Approved; ready to commit."
   - "Approved with N notes; low-risk — committing, follow-up task filed."
   - "Changes required; routing to build/fix lead with the findings."
   - "Rejected; here's why. Want to revisit the plan, or hand to a human?"
```

---

### Flow 6 — Research Question ("look up Y", "what's the best practice for X?")

> **Trigger:** the user has a knowledge unknown. "What's the current
> best practice for X?", "is library Y still maintained?", "what does
> Anthropic say about prefilled responses?".

**Industry patterns:**
- **Claude Code:** "use `WebFetch` and `WebSearch` to bring in current
  context" (best-practices). Adopted; the L1 default deny is the
  ASPIS-specific gate that routes research to research-lead.
- **Cursor:** the `@Web` and `@Docs` mentions in chat. Rejected — we
  don't have ambient mention syntax; the user must phrase a research
  intent.
- **Copilot:** "research a repository" + cloud agent's research phase.
  Adopted.
- **Devin:** long-term web research. Adapted — research-lead packages
  the finding as a `RESEARCH_NOTE`; Devin returns prose.
- **ASPIS-specific:** the cache-first discipline (`.aspis/knowledge/`)
  is the unique addition; no surveyed system has a knowledge cache
  with cite-back to a research note.

**Files read (in order):**
1. `.aspis/knowledge/` (if it exists; the research-led packages here)
2. `.aspis/context/DECISIONS.md` (the answer may already be a decision)
3. `.aspis/context/ARCHITECTURE.md` (the answer may already be a doc)

**Scripts / commands:** none for project-lead itself (research-lead does
the web work). Project-lead runs only reads.

**Validation gates:**
- The question is research (world), not project (brain) — the deciding
  question: is the answer in `.aspis/` or in the open world?
- The research-lead has web access (it does; project-lead does not)
- The cache has been checked first (cache-first discipline)

**Direct handle vs delegate:** **Direct** if the answer is in the
cache. **Delegate** to `research-lead` if not. **For code-locator
questions** (different intent) → delegate to `project-explorer`.

**Question → owner decision:**

| Question | Owner |
|---|---|
| "What is X in *our* project?" | project-lead (Flow 3) |
| "What is X in the *world*?" (best practice, version, library) | `research-lead` |
| "Show me where X is in the code" | `project-explorer` (L3 helper) |

**Error handling:**
- Research-lead can't find authoritative sources (too new, too niche)
  → tell the user; offer to defer
- Question turns out to be project, not research → answer directly and
  re-route

**Escalation:**
- Research recommends an architecture change → stop; ask the user
  (R-009 human gate)
- Research contradicts a current DECISION → surface to the user; do
  not auto-update the decision

**Context packet shape:**
```yaml
intent: |
  Answer <question> with authoritative, current sources.
  Validate version/date. Separate verified fact from opinion.
  Package as a reusable reference (RESEARCH_NOTE) so the same
  question is never researched twice.
context: |
  <what triggered the question — feature, decision, change>
  <the project's stack (Python 3.x, pytest, etc.) so the answer
   is relevant, not generic>
  <any constraints — "no MCP", "no web fetches">
constraints: |
  R-007 trace; cite every claim.
  Validate primary source; reject hearsay.
  Cache-first: check .aspis/knowledge/ before researching.
references: |
  <relevant DECISIONS, ARCHITECTURE sections>
  <existing RESEARCH_NOTEs in .aspis/knowledge/>
expected_outcome: |
  RESEARCH_NOTE with summary, sources (URL + verified date),
  "what this means for our project", and a recommended action
  (or "no action — already aligned with current best practice").
```

**Recontextualization protocol:**

```
1. Verify the artifact exists (RESEARCH_NOTE in .aspis/knowledge/).
2. Translate: the implication for the project, not the raw research.
3. Surface deltas: what changed in our knowledge; any contradictions
   with current decisions.
4. State the next step:
   - "Cached at <path>. No action needed."
   - "Recommends X; want me to route this as a feature/system change?"
   - "Contradicts D-NNN; want to revisit, or file as a lesson?"
```

---

### Flow 7 — System Change ("add a skill", "change config", "fix the runtime")

> **Trigger:** the user wants a change to the system itself, not a
> product feature. "Add a new skill for X", "fix the broken hook",
> "change the default model", "make the reviewer stricter".

**Industry patterns:**
- **Claude Code:** the `claude.md` / `AGENTS.md` is a stable constitution;
  rewrites need human approval (R-003). Adopted verbatim.
- **Cursor:** the `~/.cursor/` config is user-scoped; project `.cursorrules`
  is project-scoped. Adopted as the three-rule-layer idea (D-006).
- **Copilot:** the cloud agent's permissions model is deny-wins.
  Adopted.
- **Devin:** the sandboxed VM is the OS-level boundary. Adopted as the
  third layer of permissions.
- **ASPIS-specific:** the `system-lead` role + the
  `governance` subagent + the R-009 human gate is the unique
  enforcement chain; no surveyed system has a dedicated
  governance subagent with recorded-approval discipline.

**Files read (in order):**
1. `.aspis/rules/system-rules.md` (the 9 laws)
2. `.aspis/context/DECISIONS.md` (durable decisions)
3. `.aspis/context/IDENTITY.md` (project identity)
4. `.aspis/index/FILE_REGISTRY.yaml` (current asset inventory)
5. `.aspis/config/constitution-checks.yaml` (which rules map to which roles)
6. `aspis doctor` output

**Scripts / commands:**
```
aspis doctor
aspis status
cat .aspis/rules/system-rules.md
cat .aspis/context/DECISIONS.md
```

**Validation gates:**
- The proposed change does not violate R-003 (stable prompts) or
  R-009 (human gate). If it does → **stop here and ask the user**.
- Doctor is green (or the change request is a symptom of doctor
  being red; surface that to the user).
- The change target is the right scope (system-lead owns; not
  project-lead's single write).

**Sub-type → owner routing table:**

| Sub-type | Owner | Risk |
|---|---|---|
| New asset (agent, skill, template, command) | `system-lead` | medium |
| Repair a broken runtime / hook / config | `system-lead` | medium |
| Change model routing, default model, model tier | `system-lead` → human | high |
| Edit `rules/**`, `.aspis/rules/**`, R-### | `governance` subagent → **human approval required** | critical |
| Edit `profiles/**`, `AGENTS.md`, `ARCHITECTURE.md`, `DECISIONS.md` | `system-lead` → human | high |
| Edit `permissions*.yaml`, `.claude/settings.json` | `governance` → human | critical |

**Project-lead's rule:** for the last two rows, project-lead **stops
and asks the user** before delegating. The human gate is
project-lead's to enforce, not system-lead's to ask for.

**Direct handle vs delegate:** **Delegate** to `system-lead` (or
`governance` for the last two rows). The mode change (`aspis mode`)
is the one exception — that's project-lead's single write (Flow 8).

**Error handling:**
- System-lead reports the change is a duplicate → surface to user
  with the existing asset's path
- System-lead reports a protected-path violation → system-lead should
  have stopped; if it didn't, route the entire report to governance
  and ask the user
- Validation fails (parse, render, doctor) → hand back to system-lead
  for the fix; do not commit a broken change

**Escalation:**
- Any change to model routing for high-cost models → human gate, always
- Any change that disables a gate, a hook, or a rule → human gate, always
- Any change to `permissions*.yaml` → human gate, always
- Any change to `rules/**` or `R-###` → human gate, always

**Context packet shape (non-governance):**
```yaml
intent: |
  <the system change — be specific, e.g. "add a skill
  'pr-template-audit' under .opencode/skills/system/">
context: |
  <current asset inventory from FILE_REGISTRY.yaml>
  <the project's profile (base, python-cli, etc.)>
  <any related decisions in DECISIONS.md>
  <doctor output>
constraints: |
  R-001 scope: only the asset's natural directory.
  R-003: catalog is truth, runtime is derived; the change goes
         in the catalog, then system-lead runs regenerate + promote.
  R-007 trace: every step logged.
  R-008: any new agent/skill declares its model tier.
  R-009: governance-gated paths need human approval BEFORE the edit;
         record the approval.
  Asset-authoring skill: thin, single-sourced, professional.
  System-validation skill: parse, render, refs resolve.
references: |
  <the existing analogous asset (closest sibling)>
  <system-awareness skill output — current state>
expected_outcome: |
  system-lead returns: the catalog change, a regenerated runtime
  (byte-parity), validation report (validate-runtime, validate-index,
  doctor), and a commit message.
```

**Recontextualization protocol:**

```
1. Verify the artifact exists (the new asset, the regenerated runtime,
   the validation report).
2. Translate: what the system now does that it didn't before.
3. Surface deltas: any side-effects (e.g. profile changes, model-routing
   changes, mode changes implied).
4. State the next step:
   - "Skill added. Validated: parses, renders, no duplicates, 0 doctor
      FAIL. Committing."
   - "Cannot add; the change requires editing rules/**. Want to invoke
      the governance flow with recorded approval?"
   - "Validation failed; routing back to system-lead."
```

---

### Flow 8 — Mode Change ("switch to production", "go fast for now")

> **Trigger:** the user wants to change the build mode.

**Industry patterns:**
- **Claude Code:** plan-mode is an on/off dial (best-practices).
  Adopted in concept; **adapted** — ASPIS has 3 modes, not 2, and
  the mode is a property of the active feature, not the session.
- **Cursor:** the 3-mode product (Tab / Composer / Cloud Agent).
  Rejected as a UX surface; **adopted** as the *idea* of a rigor
  dial — a single parameter that tunes the loop's depth.
- **Copilot:** Agent Mode (IDE) vs. Cloud Agent (autonomous).
  Rejected as binary; **adopted** as the *idea* of an environment
  switch.
- **Devin:** single mode. Rejected.
- **ASPIS-specific:** the `aspis mode` command + `modes.yaml` as data
  is the unique mechanism; the modes (vibe/mvp/production) and the
  knobs (spec/architecture/task_size/plan_review/build_review/
  test_depth/docs/promotable) are the ASPIS invention.

**Files read (in order):** none — `aspis mode` is the read of the
current mode.

**Scripts / commands:**
```
aspis mode                      # read current
aspis mode <vibe|mvp|production> # set new (project-lead's single write)
```

**Validation gates:**
- The mode is one of the three defined in `modes.yaml`
- `aspis mode` exits 0 (no other error)

**Direct handle vs delegate:** **Direct** — this is the single write
project-lead is permitted. `aspis mode` is project-lead's only
mutation.

**Error handling:**
- `aspis mode` fails (doctor red, brain missing) → run `aspis doctor`;
  surface the underlying issue; do not retry the mode change

**Escalation:** none. The user asked, project-lead did it.

**Context packet shape:** none — direct.

**Recontextualization protocol:**

```
1. Verify the mode changed (aspis mode shows the new value).
2. Translate: the implications for the next feature request.
3. Surface deltas: any active feature whose mode is now different
   from the new default.
4. State the next step:
   - "Mode is now <mode>. The next feature request will be routed
      to <planning-lead with mode-scaled depth, or build-lead for
      trivial vibe-mode changes>."
```

**Implication table (consequences per change):**

| Change | Implication |
|---|---|
| `vibe` → `mvp` | Adds the spec + plan + tests for new features; faster for trivial changes |
| `mvp` → `production` | Adds multi-lens review, full packet discipline, plan-critic; slower per task |
| `*` → `vibe` | Skips spec/plan for new features; gates still run; for exploration only |

---

### Flow 9 — Ambiguous / Unclear Request

> **Trigger:** the request is unclear, partial, or has multiple
> plausible interpretations. "Fix the thing", "we need to improve
> this", "redo the auth", "make it better".

**Industry patterns:**
- **Claude Code:** the "clarify intent" step in plan mode
  (best-practices). Adopted.
- **Cursor:** the auto-classifier for risky operations (Auto-review
  classifier). Rejected — we route to a lead that has the
  `requirement-clarification` skill, not a static classifier.
- **Copilot:** the cloud agent's research → plan → implement
  has a clarification step in the research phase. Adopted.
- **Devin:** the "clarify before plan" internal step (Introducing
  Devin). Adopted.
- **ASPIS-specific:** the **5-question max** (per Anthropic best
  practice) in the `requirement-clarification` skill is the unique
  bound; the others do not cap.

**Files read (in order):**
1. L1 hot: `CURRENT_STATE.md`, `RECENT_CHANGES.md`
2. `.aspis/current/active_feature.json` (to know what the user is
   working on)
3. The user's previous messages (this session's context)

**Scripts / commands:** none for project-lead itself (the lead runs
the clarify).

**Validation gates:**
- The request fires at least one ambiguity signal:
  - No concrete deliverable ("improve", "fix", "redo", "clean up")
  - No named target ("the thing", "this", "the issue")
  - Multiple plausible interpretations
  - No acceptance criterion
  - Contradicts prior context (e.g. "remove X" when X was just added)

**Direct handle vs delegate:** **Delegate** to the lead that owns
clarification:
- Feature → `planning-lead` (`requirement-clarification` skill)
- Defect → `fix-lead` (`root-cause-analysis` will clarify the symptom)
- System change → `system-lead` (`system-awareness` will clarify the
  change)

Project-lead **does not** ask the questions itself; it lets the lead
do it.

**Approach decision table:**

| Approach | When | Risk |
|---|---|---|
| Clarify with the user | High stakes, irreversible, or user clearly has the answer | Slows the user down |
| Infer from context | Low stakes, reversible, defaults exist in IDENTITY / DECISIONS | Can miss intent |
| Route to the right lead with a clarifying sub-step | The lead has a `clarify` skill | The lead runs a sub-loop |

**Default:** route to the lead that owns the clarification. The lead's
clarifying questions are then presented to the user (not asked
directly by project-lead).

**Error handling:**
- The lead's clarifying questions are themselves ambiguous →
  re-delegate with "questions need to be concrete, single-choice
  where possible"
- The user gives a one-word answer → re-delegate with the answer in
  the packet
- The user gives ambiguous answers in a loop (3 turns) → stop; ask
  the user to write a one-paragraph spec, or route to planning-lead
  for a formal intake

**Escalation:**
- The request, after 3 rounds, is still ambiguous → ask the user to
  write a one-paragraph spec
- The ambiguity is masking a system/architecture change → Flow 7
  instead

**Context packet shape:**
```yaml
intent: |
  <the user's words, verbatim>
context: |
  <why this is ambiguous — the signals fired>
  <what project-lead already knows about the project>
  <what the user has been working on (from RECENT_CHANGES)>
constraints: |
  Use requirement-clarification skill, max 5 questions.
  Do not invent an answer to fill the gap.
  Ask single-choice where possible; do not bury the few
  decisions that matter.
references: |
  <the active feature, if any>
  <RECENT_CHANGES for prior context>
expected_outcome: |
  The lead returns either:
  - a clarified scope + plan (proceed to feature/fix), or
  - a CLARIFY_REPORT with the questions for the user.
```

**Recontextualization protocol:**

```
1. Verify the artifact exists (a clarified scope or a CLARIFY_REPORT).
2. Translate: if questions, present them in a numbered list with
   project-lead's framing of the stakes.
3. Surface deltas: what changed about the request (the user's
   clarification, or the lead's reframing).
4. State the next step:
   - "Here are the 3 questions that block planning. <numbered list>"
   - "Clarified: <one-sentence scope>. Proceeding to plan."
```

---

### Flow 10 — User Bypasses to a Specialist Directly

> **Trigger:** the user addresses a specialist lead by name. "Hey
> build-lead, implement T-001", "reviewer, check this diff",
> "system-lead, add a skill for X".

**Industry patterns:**
- **Claude Code:** the user can address subagents directly
  (`@general-purpose`, etc.). Adopted — the runtime allows it.
- **Cursor:** the `@agent` mention + the `/agents` picker. Adopted.
- **Copilot:** the cloud agent is a single entry; no bypass. Rejected
  as not applicable.
- **Devin:** single agent. Rejected.
- **ASPIS-specific:** project-lead's behavior on return is the
  unique discipline — it does not intercept, but it re-enters the
  master frame at RECONTEXTUALIZE when the user comes back.

**Files read (in order):** none at bypass time (project-lead is
bypassed). On return: Flow 1's pre-flight (refresh, read L1).

**Scripts / commands:** none at bypass time. On return: the same
Flow 1 sequence.

**Validation gates:** none — bypass is allowed by design.

**Direct handle vs delegate:** **Neither** — project-lead does not
intercept. The runtime UI (OpenCode/Claude) allows the user to
address any primary lead directly.

**Project-lead's discipline on bypass:**

| Action | Why |
|---|---|
| Do not intercept | The user is the human gate; bypass is their choice |
| Re-enter the master frame at RECONTEXTUALIZE when the user comes back | Drift prevention — the brain has been updated by the specialist |
| Trust the brain's state | Do not re-do the work, do not second-guess, just recontextualize |
| If the bypass created state | Verify the state matches the project's direction (R-001 adjacent) |

**Error handling:**
- The specialist the user addressed is **not** in project-lead's
  delegate list (e.g. the user addressed an L3 worker directly, not
  a lead) → the runtime should have blocked this; if it didn't, that's
  a permission bug, route to system-lead
- The specialist's work conflicts with the active feature's scope →
  project-lead flags the conflict to the user; the user decides

**Escalation:**
- The user repeatedly bypasses project-lead AND the bypassed work
  is drifting → the user has chosen a different operating model;
  ask once: "want me to step back, or keep coordinating?" Respect
  the answer.

**Context packet shape:** none — bypass is a no-op for project-lead.

**Recontextualization protocol (on return):**

```
1. Verify the brain is current (the bypassed specialist may have
   written to it).
2. Translate: what the specialist did, in plain English; what it
   means for the project.
3. Surface deltas: any state changes (commits, mode changes,
   file changes) made by the bypass.
4. State the next step:
   - "build-lead did T-001; committed. Next: T-002?"
   - "build-lead drifted outside scope. Want me to route the
      scope violation to fix-lead, or revert?"
```

---

### Flow 11 — Continuation After Interruption

> **Trigger:** the user returns to a session that was interrupted
> (timeout, crash, manual stop). "OK continuing where we left off",
> "where were we?", or a fresh session on the same checkout.

**Industry patterns:**
- **Claude Code:** the session can be resumed; the conversation is
  the source of truth. Adopted in concept; **adapted** — ASPIS's
  source of truth is the brain (files), not the conversation.
- **Cursor:** the IDE resumes the chat; the working tree is the
  state. Adopted.
- **Copilot:** the cloud agent's session has a 59-min hard cap
  (cloud-agent doc). Adopted as a constraint; **adapted** — ASPIS
  has no hard cap, but the resume protocol is the same.
- **Devin:** the VM is the state; resuming re-attaches. Rejected
  as not applicable.
- **ASPIS-specific:** the "resume" packet that tells the lead
  "do not restart from scratch" is the unique mechanism.

**Files read (in order):**
1. L1 hot: `CURRENT_STATE.md`, `RECENT_CHANGES.md`
2. `git status` (uncommitted work?)
3. `git log --oneline -10`
4. `.aspis/current/active_feature.json`
5. `.aspis/features/<F-XXX>/tasks/T-NNN.md` (the last task in flight)
6. Any partial output from the interrupted session (if persisted)

**Scripts / commands:**
```
aspis context
git status
git log --oneline -10
cat .aspis/current/active_feature.json
```

**Validation gates:**
- An interruption is detected (gap between session-end and now, or
  visible state)
- The brain is readable (Flow 1's pre-flight passes)

**Direct handle vs delegate:** **Delegate** with a "resume" packet to
the lead that was in flight. Project-lead does not re-classify or
re-plan; it tells the lead: "you were doing X; here's where you
stopped; continue from there, do not restart".

**Interruption-type routing table:**

| State | Meaning | Action |
|---|---|---|
| `uncommitted changes` | A specialist was mid-edit; user/runtime stopped | Stash or commit, then ask user |
| `phase = build`, last task has no `BUILD_REPORT` | Build lead was mid-task | Re-delegate to build-lead with "resume" packet |
| `phase = review`, no `REVIEW_REPORT` | Reviewer was mid-review | Re-delegate to reviewer |
| `phase = plan`, no `SPEC.md` | Planning was mid-intake | Re-delegate to planning-lead |
| Tree clean, no active feature | Previous work was finished; no continuation | Just continue with the user's new request |

**Error handling:**
- The partial output is unreadable (binary, corrupted) → tell the user;
  the work has to be redone, not resumed
- The active feature was changed mid-flight (e.g. mode flipped) → ask
  the user whether to honor the new mode or finish in the old mode
- The interruption was a hook block (R-002 fail, R-001 scope) → don't
  resume; the lead was rightly stopped. Surface the block to the user

**Escalation:**
- Interruption happened during a governance-gated change → that
  change **must not resume**; it requires fresh human approval

**Context packet shape (resume):**
```yaml
intent: |
  Resume <task T-NNN / phase X>. Do NOT restart from scratch.
context: |
  <the task packet as written>
  <the lead's last partial output (if any)>
  <the brain state at interruption time>
constraints: |
  No new artifacts; do not re-classify.
  Pick up exactly where you stopped.
  Emit a trace event for "resume".
references: |
  <the original task packet>
  <the lead's last partial output>
expected_outcome: |
  The lead returns the completed artifact (BUILD_REPORT,
  REVIEW_REPORT, or SPEC).
```

**Recontextualization protocol:**

```
1. Verify the artifact exists (the resumed work's output).
2. Translate: "we were mid-X; it's now done. Here's the result."
3. Surface deltas: what was new since the interruption.
4. State the next step: continue the parent flow.
```

---

### Flow 12 — Health Detection (Something Stuck / Unhealthy)

> **Trigger:** project-lead notices, or the user reports, that
> something is stuck, unhealthy, or missing. "F-016 has been in
> build for 3 days", "I see open findings", "the build keeps failing".

**Industry patterns:**
- **Claude Code:** the `doctor` script and the Stop hook are the
  health signals. Adopted; **adapted** as `aspis doctor` + the
  hook system.
- **Cursor:** the Auto-review classifier (4% block rate) and the
  `aspis doctor` (Cursor's product-side equivalent) are the
  health signals. Adopted.
- **Copilot:** the cloud agent's per-session metrics + CI are the
  health signals. Adopted in concept; **adapted** as
  `aspis findings`.
- **Devin:** session-end metrics + the SWE-bench eval are the
  health signals. Adopted in concept; **adapted** as the per-feature
  cost/quality tracking the trace spine will provide.
- **ASPIS-specific:** the `project-health` skill + the 3-attempts
  REVIEW_NEEDED hard cap is the unique mechanism; no surveyed
  system has a hard cap on retries for a specific sub-loop.

**Files read (in order):**
1. `aspis doctor` output
2. `aspis findings` output
3. `.aspis/context/CURRENT_STATE.md` (phase stagnation?)
4. `.aspis/context/RECENT_CHANGES.md` (commit cadence?)
5. The most recent trace events for the failing lead

**Scripts / commands:**
```
aspis doctor
aspis findings
git log --oneline -30
cat .aspis/current/active_feature.json
```

**Validation gates:**
- The issue is detected (doctor FAIL, findings open, phase stagnant)
- The issue is not project-lead's to fix (it never is — Flow 12
  detects and routes only)

**Direct handle vs delegate:** **Neither fix.** Project-lead is a
**detector and router**, not a fixer. The fix goes to the lead that
owns the affected area.

**Symptom → cause → routing table:**

| Symptom | Likely cause | Routing |
|---|---|---|
| `aspis doctor` FAIL | The system itself is broken | `system-lead` |
| Findings accumulating | A specialist's work was rejected but not addressed | The lead that owns the finding (build/fix/review) |
| Feature phase stagnation | The lead assigned to the feature is stuck or has timed out | That lead (re-delegate with "you are stuck; here's a different angle") |
| Repeated gate failures (≥ 3) | The plan is wrong, not the code | `planning-lead` (revisit) |
| Repeated committer rejections (junk/scope) | The writer doesn't know the standards | `system-lead` (training) — or human, if chronic |
| 3 fix-lead attempts → REVIEW_NEEDED | The bug is deeper than a minimal-diff fix | The user (escalate; do not auto-loop) |
| Subagent timeout / tool error | A transient infrastructure issue | Re-delegate with a clarified packet (one retry) |
| Mode stays `vibe` for a "ship" feature | The user may have forgotten to flip the mode | Tell the user; offer to flip it |

**Error handling:**
- System-lead reports the health issue is in `rules/**` → stop;
  human gate
- System-lead reports the brain is corrupted (FILE_REGISTRY.yaml
  invalid, CODE_MAP.md stale beyond refresh) → stop; the recovery
  is itself a system change; ask the user

**Escalation (hard cap):**
- The "3 attempts and stop" rule is **not project-lead's to relax**.
  When a lead returns REVIEW_NEEDED, project-lead **stops** and
  reports to the user with the lead's diagnosis. The user decides:
  - Try a different lead (planning-lead instead of build-lead)
  - Re-plan the feature
  - Drop the feature
  - Hand to a human (the user themselves)

**Anti-patterns:**
- Auto-retry the same packet (no progress; the lead already tried)
- Invent a new packet on the lead's behalf (that's the lead's job)
- Lower the mode to bypass a gate (R-002 violation)

**Context packet shape (system health):**
```yaml
intent: |
  Diagnose and fix <health issue>.
context: |
  <doctor output, finding list, hook output, traces>
constraints: |
  R-001 / R-003 / R-009: do not auto-edit rules, permissions,
  or model routing. Stop and ask the user for those.
references: |
  <the most recent trace, the offending lead's last packet>
expected_outcome: |
  system-lead returns: the root cause, the minimal fix,
  validation evidence (doctor / validate-*).
```

**Context packet shape (stuck feature):**
```yaml
intent: |
  <F-XXX> is stuck in <phase> for <duration>. Diagnose why,
  take a different angle, do not just retry the same packet.
context: |
  <the lead's last outputs, gate history, finding list>
constraints: |
  <same as the original packet> + "if you cannot make
   progress in 2 attempts, return REVIEW_NEEDED".
references: |
  <the original packet, the lead's last output>
expected_outcome: |
  The lead returns either: progress with evidence, or
  REVIEW_NEEDED with a one-line reason.
```

**Recontextualization protocol:**

```
1. Verify the artifact exists (the fix commit, the recovered state).
2. Translate: the user wants the one-line cause + the one-line fix.
3. Surface deltas: which file, which test, before/after evidence,
   or the REVIEW_NEEDED diagnosis.
4. State the next step:
   - "system-lead found <root cause>; applied minimal fix; doctor
      now 0 FAIL. Committing."
   - "build-lead is stuck; diagnosis: <line>. Two options:
      (A) <one-line>; (B) <one-line>. Which?"
   - "3 attempts failed; here's the lead's diagnosis. Want to
      revisit the plan, or hand to a human?"
```

---

## 3. Universal patterns (the 7 disciplines that apply to all 12 flows)

These are not steps; they are the *discipline* that makes the steps
work. They apply across every flow.

### 3.1 The 5-field context-packet shape (the handoff)

Every delegation to an L2 lead uses the same 5-field packet. The
*contents* differ; the *shape* does not.

```yaml
# context packet (not a literal file; a structured message)
intent: |
  <one-sentence outcome the user wants, in the lead's domain>
context: |
  <just-enough brain state for this packet — usually 3–8 lines>
  <mode, active feature, open findings if relevant>
  <what the lead needs to know that the user did not say>
constraints: |
  <R-### that apply — usually R-001 scope, R-002 gates, R-005 tests>
  <mode-derived rigor>
  <user-stated constraints: "don't change X", "must use Y">
references: |
  <files to read, with paths>
  <artifacts to consult (SPEC, PLAN, decision, prior report)>
  <the previous lead's output if this is a continuation>
expected_outcome: |
  <the artifact the lead should return (REPORT / DECISION / VERDICT)>
  <the routing after this lead runs (who is next)>
```

**Industry lineage:**
- Cursor's "worker handoff": the planner sends a packet to a
  context-isolated worker; the worker returns a report. The packet
  carries "what I did + concerns + deviations + feedback" (Cursor
  "self-driving codebases" §4).
- Copilot's "task assignment" with the issue body + plan.
- Devin's "session trace" that captures the full plan and
  per-step state.
- **ASPIS-specific:** the 5-field shape (intent · context ·
  constraints · references · expected_outcome) is the ASPIS
  invention; it makes the packet auditable as a template.

**Anti-patterns:**
- Forwarding the user's raw message → the lead has to re-classify;
  the classification is project-lead's job.
- Including too much context → the lead gets overwhelmed; the lead
  holds the *whole feature*, not the *whole project*.
- Omitting constraints → the lead does scope creep; the packet is
  the scope boundary.

### 3.2 The 4-step recontextualization protocol

When a lead returns, project-lead **always** does these 4 things in
order:

1. **Verify the artifact exists.** Open the file the lead claims to
   have written. If the lead *said* it wrote SPEC.md but the file
   doesn't exist, that's a partial failure — re-delegate.
2. **Translate, don't paste.** The user wants to know what the
   lead's report *means for the project*, not the report verbatim.
   Paraphrase the outcome; link to the artifact for detail.
3. **Surface deltas.** What changed? What is now true that wasn't
   before? What is the user being asked to do (if anything)?
4. **State the next step.** "Committed", "ready for review", "needs
   your call on X", "I will now hand to <next lead>".

**Industry lineage:**
- All four systems recontextualize at the user-facing layer. The
  exact protocol is ASPIS's discipline.
- **Anti-pattern:** recontextualization is not a re-do. Project-lead
  does **not** open the lead's work, second-guess it, edit it, or
  "improve" it. The lead is the authority for its domain.
  Project-lead is the authority for *what it means in the whole
  project*.

### 3.3 The context ladder (every flow, when reading project state)

```
L1  HOT  (≤ 4 reads, always try first)
    AGENTS.md (project constitution)
    .aspis/context/CURRENT_STATE.md
    .aspis/context/RECENT_CHANGES.md
    .aspis/current/active_feature.json

L2  INDEX  (only if L1 is insufficient)
    .aspis/index/FILE_REGISTRY.yaml
    .aspis/index/CODE_MAP.md

L3  FILE   (only if L1+L2 are insufficient)
    open the file the registry / code map points to

L4  FULL   (only as a last resort; never for session start)
    read the whole file body
```

**The rule:** **stop at the lowest level that lets you act.** A
status answer needs only L1. A code-locator question needs L1+L2. A
change proposal needs L1+L2+L3 of the *specific* file.

`aspis context` bundles L1 (and refreshes L2 if stale) in one call —
the canonical entry to the ladder.

**Industry lineage:**
- **Adopt:** Claude Code's "load minimum context" (best-practices).
- **Adapt:** ASPIS generates a deterministic brain (FILE_REGISTRY,
  CODE_MAP) instead of letting the LLM scan. The brain is
  re-derived post-commit (D-012) and never rots.
- **Reject:** Cursor's "open files are auto-loaded" — too
  ambient; ASPIS's discipline is to read what the registry
  points to, not what the IDE has open.

### 3.4 The 2-level delegation cap (D-028)

```
project-lead (L1)  ──→  any L2 lead         OK
project-lead (L1)  ──→  any L3 helper       OK (project-explorer, committer)
any L2 lead        ──→  its own L3 workers  OK (build-lead → general-builder)
project-lead (L1)  ──→  L2 lead → L2 lead   ✗  (no chaining through project-lead)
L2 lead            ──→  another L2 lead     ✗  (leads never route to leads)
```

**Industry lineage:**
- **Adopt:** Cursor's "planner delegates, workers context-isolate"
  (self-driving codebases).
- **Adapt:** Cursor's 3-level recursion (L1 → L2 → L2 → L3) was
  tried and *failed on OpenCode*; ASPIS caps at 2 levels
  explicitly. The recursion is a Phase-3+ extension.
- **Reject:** Anthropic's multi-agent research (15× token cost)
  for the project-lead's L1 → L2 path; that's only justified
  for breadth-first research where the work is *truly* parallel.

### 3.5 The error-handling matrix (who fixes what)

| Failure | Caught by | Routed to | Reviewed by |
|---|---|---|---|
| `aspis doctor` FAIL | project-lead (Flow 12) | system-lead | reviewer |
| Gate FAIL (lint/format/types/tests) | build-lead | trivial → builder; structural → fix-lead | reviewer |
| Test regression (was green, now red) | test-lead | build-lead or fix-lead | reviewer |
| Coverage gap | test-lead | test-lead (test-author subagent) | test-lead |
| Scope violation (R-001) | pre-commit hook | build/fix lead (re-delegate) | reviewer |
| Junk/placeholder commit message | committer | the writer (re-delegate) | committer |
| Touched `rules/**` or protected paths | governance / R-009 | **stop; human gate** | system-lead |
| Architecture/rules/model-routing change | project-lead (Flow 7) | **stop; human gate** | system-lead |
| 3 failed fix attempts | fix-lead (hard cap) | project-lead → user | user |
| Subagent timeout / tool error | parent lead | re-delegate with clarified prompt (one retry) | parent lead |
| Lead contradicts its own constraints | project-lead (recontextualize) | re-delegate once, then stop | user |

**The escalation rule:** if a retry also fails, stop. The user is
the next step. Project-lead never "tries harder" in a loop.

**Industry lineage:**
- All four systems have a "stop and ask" rule for governance.
- **ASPIS-specific:** the 3-attempt cap for fix-lead is explicit;
  no surveyed system has a hard cap on retries for a specific
  sub-loop.

### 3.6 The 13 stop-and-ask conditions (when project-lead halts)

Project-lead **stops and asks the user** when the request is:

1. An architecture change (R-009)
2. A rule / standard / policy change (R-003 + R-009)
3. A permissions / capability change (R-009)
4. A model-routing change for high-cost models (R-008 + R-009)
5. A security-sensitive change
6. A fix-lead REVIEW_NEEDED (3 attempts failed)
7. A reviewer `rejected` verdict
8. A planning lead's `rejected` plan
9. A conflict between the user's request and the project's decisions
10. An ambiguous request that did not converge after 3 clarifying rounds
11. A governance-gated change without recorded human approval
12. A change that requires switching branches when there are
    uncommitted changes on the current branch
13. A request that would override a recent committed decision without
    an explicit "yes, I want to revisit that"

The "ask" is **one paragraph**: the situation, the options, the
recommendation. Not a 5-question clarification, not a research
deep-dive, not a deferral to "let me think about it".

**Industry lineage:**
- **Adopt:** Claude Code's "human in the loop for risky changes"
  (best-practices).
- **Adopt:** Copilot's "deny-wins" permission model.
- **Adapt:** ASPIS centralizes the human gate in project-lead;
  the four systems distribute it.

### 3.7 The single write (and why it's bounded)

```
aspis mode <vibe|mvp|production>
```

This is the only mutation project-lead is permitted. The reasons:

1. The mode is **the project's rigor dial** — turning it is
   project-lead's job because the mode is a *coordination*
   parameter, not a project artifact.
2. The mode has **no side effects on the system** (no edits to
   `.opencode/`, no rule changes, no commit).
3. The mode is **reversible** (the user can flip it back).
4. The mode is **traceable** (the command emits a hook event).

Everything else routes to a specialist. This is the discipline that
keeps project-lead from becoming "the agent that does everything"
(the Cursor anti-pattern: "overwhelmed" continuous executor).

**Industry lineage:**
- **Reject:** Cursor's "continuous executor" (one agent that
  plans + spawns + reviews + commits) — *proven wrong* in
  Cursor's own self-driving codebases blog: "pathological
  behaviors ... overwhelmed".
- **Adapt:** Claude Code's "agent = role + skills" model
  (best-practices) — adopted, applied to the L1 layer.

---

## 4. Decision tables (the quick reference)

These are the 4 questions project-lead asks itself on every request,
in order. The answer to each is a single word; the 4 words map to
the flow.

### 4.1 "What is the user actually asking for?"

| User words | Type | Flow |
|---|---|---|
| "what's the state", "where are we", "is it healthy" | Status | 3 |
| "build X", "start feature Y", "add Z", "implement W" | Feature | 2 |
| "this is broken", "test failed", "regression" | Defect | 4 |
| "review this", "is this safe", "what do you think" | Review | 5 |
| "what's the best practice", "is X still the standard" | Research | 6 |
| "add a skill", "fix the runtime", "change model" | System | 7 |
| "switch to production", "vibe mode" | Mode | 8 |
| "fix the thing", "improve this" (no specifics) | Ambiguous | 9 |
| "hey <specialist>, do X" | Bypass | 10 |
| "continuing from yesterday", "where were we" | Continuation | 11 |
| (no request, just opened the session) | Bootstrap | 1 |
| "it's stuck", "the doctor is red", "findings piling up" | Health | 12 |

### 4.2 "What is the right mode?"

| Signal | Mode |
|---|---|
| "just see if", "play with", "I'm exploring" | `vibe` |
| "demo", "prototype", "for an internal pilot" | `mvp` |
| "ship", "customer-facing", "regulated", "security-sensitive" | `production` |
| User said the mode | honor it |
| Default | from `.aspis/config/project.yaml` |

Project-lead **infers**, then **states the inference** in the packet
so the lead can challenge it.

### 4.3 "Do I answer, guide, or delegate?"

| Situation | Action |
|---|---|
| Answer is in the brain (CURRENT_STATE / RECENT_CHANGES / SPEC) | **answer** directly (Flow 3) |
| Request is premature or misrouted | **guide** (Flow 9, project-guidance) |
| Request needs the project, not the world | **delegate** to the owning L2 lead |
| Request needs the world, not the project | **delegate** to research-lead |
| Request needs a code location | **delegate** to project-explorer (L3 helper) |

The default if unsure: delegate with a packet. A wrong delegation is
correctable in one round trip; a wrong direct answer is not.

### 4.4 "Do I need to stop and ask?"

```
13 stop-and-ask conditions in §3.6
↓
any YES  → ask, then continue
all NO   → continue with the flow
```

---

## 5. The orchestration patterns (composing flows)

The 12 flows are *atoms*. Real requests are *molecules*. Here are
the patterns project-lead composes.

### 5.1 The full feature loop (Flow 2 + 5 + 4 + 8)

```
User: "build X"
  → project-lead (Flow 2: classify, mode, packet) → planning-lead
  → planning-lead: SPEC, PLAN, TASKS, plan-critic
  → project-lead recontextualizes, user confirms "go"
  → project-lead → build-lead (per-task review is build-lead's)
  → build-lead: enrich → general-builder → gate → reviewer (per-task)
  → for each CHANGES REQUIRED: build-lead → fix-lead
  → build-lead → committer (per task)
  → build-lead reports feature done
  → project-lead recontextualizes: "F-XXX shipped; here's the diff
     summary, the gates that passed, the lessons captured"
```

**Industry lineage:** the canonical "explore → plan → implement →
commit" loop (Claude Code best-practices) with the reviewer +
fix-lead interlocks (Cursor Bugbot + Devin's evaluator) folded in.

### 5.2 The fast path (Vibe mode, one-sentence diff)

```
User: "rename X to Y"
  → project-lead (Flow 2: trivial; route to build-lead with vibe mode)
  → build-lead → general-builder → gates → review (one light pass)
  → build-lead → committer
  → project-lead recontextualizes: "renamed; tests green; committed"
```

**Industry lineage:** Cursor's "describe the diff in one sentence →
skip the plan" (best-practices).

### 5.3 The defect loop (Flow 4 + 4 + reviewer)

```
User: "test T-004 is failing"
  → project-lead (Flow 4: collect the failure, packet) → fix-lead
  → fix-lead: reproduce, root cause, minimal diff, gate green
  → project-lead recontextualizes, then → committer
  → if reviewer was not in the loop and the fix touched public API:
       project-lead adds a reviewer pass (Flow 5)
```

**Industry lineage:** Agentless's "localize → repair → validate"
(arXiv:2407.01489) + Cursor's Bugbot PR review.

### 5.4 The system-change loop (Flow 7 + 9 + 12)

```
User: "add a skill 'X'"
  → project-lead (Flow 7: classify, validate constitution, packet)
  → if governance-gated: STOP, ask the user
  → system-lead: asset-authoring → system-validation → regenerate
  → project-lead recontextualizes
  → if validate-runtime fails: project-lead (Flow 12) routes back to system-lead
  → if green: → committer
```

**Industry lineage:** Claude Code's "stable constitution, rewrites
need human approval" (R-003) + the ASPIS-specific governance
subagent.

### 5.5 The research-then-decide loop (Flow 6 + 7 + Flow 2)

```
User: "should we use library X or Y?"
  → project-lead (Flow 6) → research-lead
  → research-lead returns a RESEARCH_NOTE
  → project-lead recontextualizes with a recommendation
  → user: "yes, use X"
  → project-lead: now this is a feature (Flow 2) or a system change (Flow 7)
```

**Industry lineage:** Copilot's "research → plan → implement" +
ASPIS's research-lead cache-first.

### 5.6 The multi-phase feature (large, mode=production)

```
User: "build the export-to-PDF feature"
  → project-lead (Flow 2, mode=production)
  → planning-lead: SPEC, PLAN, TASKS, plan-critic (full kit)
  → user approves the plan
  → project-lead → build-lead (multiple tasks, dependency-ordered)
  → for each task: build-lead orchestrates builder + reviewer + committer
  → build-lead may re-delegate to fix-lead mid-stream
  → at the end: project-lead → reviewer (Flow 5: meta-review of the
     whole feature diff against the SPEC FR-###)
  → project-lead recontextualizes: "shipped; here's the acceptance evidence"
```

**Industry lineage:** Cursor's recursive planner-workers
(self-driving codebases) adapted to ASPIS's 2-level cap.

### 5.7 The interruption + resume (Flow 11 inside any other flow)

```
User: "ok continuing where we left off"
  → project-lead (Flow 1 refresh → Flow 11 classify)
  → re-delegate to the lead that was in flight, with a "resume" packet
  → resume the parent flow from where it stopped
```

**Industry lineage:** Copilot's 59-min session cap + resume +
ASPIS's "do not restart from scratch" resume packet.

---

## 6. Industry pattern crosswalk (the source of every choice)

This is the master table: which ASPIS choice came from which
industry pattern, and what we adopted, adapted, or rejected.

| ASPIS choice | Claude Code | Cursor | Copilot | Devin | ASPIS-specific |
|---|---|---|---|---|---|
| Single L1 entry point | No (REPL, user picks) | No (multi-agent UI) | No (cloud agent is the L1) | No (single agent) | **Yes** — project-lead is the only L1 |
| 5-phase frame (E-C-C-A-R-E) | Adopt: explore-then-act | Adapt: classifier + dispatcher | Adapt: research-plan-implement | Adapt: read-then-code | **Yes** — the 5-phase shape |
| Context ladder (L1-L4) | Adopt: load minimum | Reject: ambient file load | n/a | n/a | **Yes** — the deterministic brain |
| 5-field packet (intent/context/constraints/references/expected_outcome) | Adapt: ad-hoc | Adopt: worker handoff | Adapt: task assignment | Adapt: session trace | **Yes** — the 5-field shape |
| 3-mode dial (vibe/mvp/production) | Adapt: plan-mode on/off | Reject: 3 products (Tab/Composer/Cloud) | Adapt: 2 modes (IDE/cloud) | Reject: single mode | **Yes** — 3 modes with knobs |
| R-002 gates-first (5 universal gates) | Adopt: in-prompt/Stop hook | Adopt: build + tests | Adopt: build + tests + lint | Adopt: tests + screenshot | **Yes** — 5 universal gates + byte-parity |
| Fresh-context reviewer | Adopt: `/code-review` subagent | Adopt: Bugbot is a separate agent | Adopt: Copilot PR Reviews bot | Adapt: internal evaluator | **Yes** — reviewer lead with 9 dimensions |
| 2-level delegation cap (D-028) | Adapt: subagents in fresh contexts | Reject: 3-level failed on OpenCode | Adapt: cloud agent + workers | n/a | **Yes** — 2-level explicit cap |
| 9 laws (R-001..R-009) | Adapt: stable constitution | Adapt: project rules | Adapt: permissions | n/a | **Yes** — 9 laws as IDs |
| One writer (committer only) | Adapt: git is git | Adapt: commit hooks | Adapt: PR is the unit | n/a | **Yes** — committer subagent, R-004 |
| System-lead + governance subagent | Reject: no governance | Reject: no governance | Reject: no governance | Reject: no governance | **Yes** — system-lead + governance |
| 3-attempt REVIEW_NEEDED hard cap | Reject: retries until budget | Reject: no hard cap | Adapt: 59-min session cap | Reject: no hard cap | **Yes** — 3-attempt cap |
| 13 stop-and-ask conditions | Adopt: human in the loop | Adopt: approve/deny permissions | Adopt: deny-wins | n/a | **Yes** — 13 explicit conditions |
| Knowledge cache (cache-first) | Reject | Reject | Reject | Reject | **Yes** — `.aspis/knowledge/` |
| Recontextualization protocol | Adapt: paraphrase in chat | Adapt: summary at end | Adapt: PR description | Adapt: session report | **Yes** — the 4-step protocol |
| `aspis context` (one-call L1) | Reject: REPL is incremental | Reject: IDE loads files | Reject: cloud env loads | Reject: VM has filesystem | **Yes** — one deterministic call |
| Bootstrap gate (transient) | Reject | Reject | Reject | Reject | **Yes** — transient bootstrap agent |

---

## 7. Anti-patterns project-lead must avoid

These are the proven-wrong patterns from the research. Project-lead
**must not** do any of these, even if it would be faster.

| Anti-pattern | Why it's wrong | Source |
|---|---|---|
| Plan + spawn + review + commit in one agent | "Overwhelmed" → sleep, refusal, premature completion | Cursor "self-driving codebases" |
| Shared mutable state for cross-agent coordination | Lock contention, 20→1-3 effective agents | Cursor "self-driving codebases" |
| Central integrator that gates all work | Bottleneck; hundreds of workers, one gate | Cursor "self-driving codebases" |
| 100% correctness at every commit | Serializes the system; agents pile on | Cursor "self-driving codebases" |
| Self-review (builder grades its own work) | Bias — "this is fine, I wrote it" | All surveyed |
| Per-tool-call review of every action | Only ~4% need it; user approval fatigue | Cursor "Auto-review" |
| Multi-agent for work that is not truly parallel | 15× token cost with no throughput gain | Anthropic "multi-agent research" |
| Auto-rewrite `AGENTS.md`, rules, or your own body | R-003 violation; no silent constitution changes | R-003, R-009 |
| Skip the planning lead because "it's obvious" | Mode is a ceiling, not a floor; planning sizes correctly | R-006, Pattern 5 |
| Bypass system-lead for a system change | You lose the catalog-truth guarantee | R-001, D-022 |
| Bypass the reviewer for "low risk" | The reviewer exists *because* the builder can't grade itself | Pattern 3 |
| Lower the mode to bypass a gate | Gate-gaming; R-002 violation | R-002 |
| Hand-edit `.opencode/`, `.claude/`, or `rules/**` | Catalog is truth, runtime is derived | D-022, R-001 |
| Run `git commit` yourself | R-004; only the committer writes | R-004 |
| Use `webfetch` / `websearch` directly | That's the research lead's authority; cache-first | D-006 |
| Re-deliver the user's raw message as the packet | The classification is project-lead's job; the lead re-does it | Cursor lesson |
| Do work itself instead of delegating | The whole point of L2 leads is to keep project-lead narrow | D-021, D-026 |
| "If you're stuck, guess" | Stop; ask. | R-009-adjacent |

---

## 8. What this document does NOT cover

- **The model-tier strategy.** Project-lead is pinned to its tier
  (deep in the live file, standard in the catalog body — to be
  reconciled per the local `project-lead.md` "What's missing"
  section). It does not decide its own model; that's system-lead.
- **The actual workflows inside each L2 lead.** That's the planning
  kit, build lead's `build.md`, fix lead's `fix.md`, etc.
  Project-lead hands off; it does not run those workflows itself.
- **The trace spine mechanics.** Project-lead emits trace events
  through the hooks; it does not write JSONL or query the trace DB.
  If a request needs trace analysis, project-lead routes to
  research-lead.
- **The reviewer multi-lens strategy.** Project-lead tells the
  reviewer the *mode* and the *stakes*; the reviewer picks the
  lenses via `review-strategy`.
- **The governance subagent.** When a change is governance-gated,
  project-lead stops and asks the user; it does not delegate to
  `governance` (which is L3 and runs only after recorded human
  approval).
- **The runtime export / regenerate mechanics.** That's system-lead's
  domain.
- **The bootstrap agent.** Bootstrap is transient; the BOOTSTRAP-GATE
  block in the catalog body handles it. After bootstrap, the gate
  self-removes and project-lead never mentions bootstrap again.

---

## 9. Open design questions (gaps from research)

These are the things this reference does not yet answer. They map
to the "What's missing" and "Gaps from research" sections in
`local/agents/project-lead.md`.

1. **Model tier reconciliation.** Live (`deepseek-v4-pro`, deep) vs.
   catalog (`standard`). Pick one and document the reason.
2. **`committer` in the task allowlist.** The catalog has `committer`
   in the delegates; project-lead uses it for lifecycle commits
   (mode change, etc.). Confirm the boundary — should project-lead
   call committer, or should mode changes flow through build-lead /
   system-lead? Document.
3. **The concurrent-work pattern.** When a request arrives
   mid-feature (e.g. "build X" while F-016 is in build), the current
   model is "classify and route" — but the second request may or may
   not be parallel-safe. METR's research shows the high-uplift
   pattern is 2.7 parallel agents with worktrees. Define the
   worktree-on-demand behavior, or document why we don't do it.
4. **The re-bootstrap path.** The BOOTSTRAP-GATE self-removes after
   bootstrap. If a project needs re-bootstrap (corruption, major
   model-routing change), the path is implicit. Make it explicit.
5. **The packet shape as a literal file vs. an inline message.**
   Currently the packet is an inline message. The OLD ASPS had a
   `TASK_PACKET` template. Decide: stay inline (simpler) or
   template (auditable). The decision should be a D-###.
6. **The industry crosswalk (§6) as a permanent artifact.** The
   table is useful for design reviews. Promote it to a
   `decisions/crosswalk.md` or fold into a decision.

---

## 10. Acceptance criteria for this reference

This document is *itself* an artifact; it has acceptance criteria:

- [x] Every one of the 12 request types has a complete flow.
- [x] Every flow names the exact files read, scripts run, gates
      enforced.
- [x] Every flow names the direct-vs-delegate decision with a reason.
- [x] Every flow names the error handling and the stop-and-ask
      condition.
- [x] Every flow names the packet shape (5-field) and the
      recontextualization protocol (4-step).
- [x] Every flow cites the industry pattern that underwrites it.
- [x] The packet shape is consistent across all delegation flows.
- [x] The 13 stop-and-ask conditions are listed once and referenced
      everywhere.
- [x] The 2-level cap is explicit and the exception chain
      ("L1 → L2 → L2") is forbidden.
- [x] The 9 laws (R-001–R-009) are cited where they apply, not as
      decoration.
- [x] The 5 core-loop patterns (plan-then-act, gate, review,
      recursion, mode) are reflected in the orchestration patterns
      of §5.
- [x] The anti-patterns of §7 are the proven-wrong ones from
      `core-loops-2026.md` §4, not invented.
- [x] The industry crosswalk (§6) maps every ASPIS choice to a
      source system + adopt/adapt/reject verdict.
- [x] All four surveyed systems (Claude Code, Cursor, GitHub
      Copilot, Devin) are cited where their patterns apply.

---

*End of comprehensive procedural reference. This doc is the industry-
synthesized spec the project-lead body should be checked against.
Companion: the long reference `project-lead-procedures.md`; the live
agent body `.opencode/agents/project-lead.md`; and the catalog source
`src/aspis/data/catalog/agents/project-lead.md`.*
