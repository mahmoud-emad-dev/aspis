# OLD ASPS — Deep Analysis: Agent System Architecture

> **Sources read.** All files in `local/ASPS/.asps/context/` (16 files), `local/ASPS/local/guide/` (6 files), `local/ASPS/local/phases/` (9 files), `local/ASPS/local/agent-notes/` (4 files), `local/ASPS/agents/**` (all 28 agent .md files), `local/ASPS/.asps/workflows/` (5 files), `local/ASPS/profiles/**` (7 files), `local/ASPS/rules/SYSTEM_RULES.md`, `local/ASPS/local/launch/LINKEDIN-DRAFT.md`, and the start of `local/ASPS/ARCHITECTURE.md` and `DECISIONS.md`.
>
> **What is ASPS?** A **file-first, multi-runtime agentic software production factory**. It is *both* the system being built (Project #1) *and* the reusable factory for any future project (D-001). Its core bet:
>
> ```text
> Quality = model capability × task clarity × test strength × review discipline
> ```
>
> Spend effort on **determinism, clarity, tests, gates, review, tracing** so the **cheapest** model can do production-grade work, repeatably. Three layers — `L1 Catalog` (markdown, truth) → `export/transform` (profile-gated) → `L2 Live runtimes` (`.opencode/`, `.claude/`) — with a **byte-parity moat** proving `catalog == live`.

---

## 1 · The Roster at a Glance (D-026, D-028, ROSTER_SPEC)

The exported roster is a **lean 3-layer hierarchy** (1 + 7 + ~20 = 28), each with a clear job and the *narrow-role principle* (no overlap, easy to pin a model for, easy to improve).

```
L1  project-lead                      primary — the ONLY agent the human talks to
L2  asps-system-lead                  primary — runtime/catalog author + committer governance
    asps-planning-lead                primary — spec → plan → tasks → acceptance (P0–P9)
    asps-build-lead                    primary — implementation orchestrator
    asps-reviewer                     primary — independent quality authority (read-only)
    asps-fix-lead                     subagent — recovery authority (minimal-diff)
    asps-tester                       subagent — testing strategy + gate enforcement
    lead-researcher                   subagent — knowledge authority + harvest path
L3  governance, committer                                  system leaf workers
    asps-opencode-author, asps-claude-author              runtime-specific authors
    asps-bootstrap                                          one-time onboarding (self-deletes)
    python-builder, api-builder                            build workers (leaf)
    bug-triager, gate-fixer                                fix workers (leaf)
    security-reviewer, commit-reviewer                     review workers (leaf)
    test-author                                            test worker (leaf)
    clarify, idea-capture, task-decomposer                 planning workers (leaf)
    codebase-explorer, docs-fetcher, web-researcher        research workers (leaf)
    project-explorer, context-feeder, context-summarizer   shared read-only helpers
```

**`D-028 — Two delegation levels for now`:** L1 = all 7 leads (incl. project-lead), L2 = subagents. The 3rd level is **parked** because OpenCode L3 has a freeze bug. Claude Code supports arbitrary depth but the Claude exporter currently lacks the `Agent` tool, so even Claude's chain is dead until the R-009 fix lands (A1, see `local/agent-notes/NESTING-3-LEVELS.md`).

---

## 2 · Per-Agent Deep Dives

For each lead I extracted: exact role, problems solved, who it interacts with, skills used, permissions, tools, workflows, escalation rules, subagents, and known findings.

### 2.1 `project-lead` (L1, primary) — `agents/system/project-lead.md`

**Exact role.** *"The main agent the user talks to (L1) and the project's intelligence layer. It understands the project as a whole, answers project questions directly when it can, and coordinates the specialized leads when work is needed. It is **not merely a router**: it owns project awareness, translates intent into project-aware delegation, and recontextualizes results. It does not implement, author, or commit — it coordinates and holds scope + the human gate."*

**Problems it solves.**
- *One agent the user talks to* — the entire system is reachable through one L1; the human never deals with internal hierarchy.
- *Intent translation* — turns a vague "build me X" into a single classified route + scoped context.
- *Recontextualization* — translates a specialist's output back into what it means for the whole project.
- *Holds the human gate (R-009)* — escalates architecture/rules/security/model-routing/self-improvement to the human, no automated rewrites.

**Interactions.** Delegates (one at a time) to the **7 L2 leads** per this routing table:

| Intent | Delegate to |
|---|---|
| feature / plan / spec / clarify | `asps-planning-lead` |
| build / implement | `asps-build-lead` |
| bug / gate-fail / regression | `asps-fix-lead` |
| tests / coverage | `asps-tester` |
| review / security / diff | `asps-reviewer` |
| runtime / custom-asset / governance | `asps-system-lead` |
| research / docs / codebase-map | `lead-researcher` |
| architecture / rules / security / model-routing / self-improvement | **human gate (R-009)** |

It may also call the shared read-only helpers (`project-explorer`, `context-feeder`, `context-summarizer`). It must **never** delegate to an L3 worker directly, and **never** lead→lead→lead (the 3-level model cap).

**Skills.** `asps-lead-operating-protocol`, `asps-context-navigation`, `request-routing`, `scope-control`, `done-reporting`, `fallback-recovery`.

**Permissions / tools.** `mode: primary`; `model: standard`; `read/list/search allow`; `edit allow` (trace events only); `bash allow` (read-only `asps status|validate-*|status-report`, `git status|diff`; deny `git commit|push`); `webfetch/websearch deny`; `Delegation intent: allow`. The base profile's `defaults.yaml` further pins this: `bash: git diff*|git status*|asps status*|asps validate-*: allow`, `edit: allow`, `task: asps-{system,planning,build,fix,review,test}-lead + lead-researcher: allow`, `asps-opencode-author: ~` (suppressed — never delegates directly to an author).

**Workflows.** Reads `AGENTS.md` once (Level 1 entry), then `asps-context-navigation` (level ladder) and `asps-lead-operating-protocol` (opening sequence). For deep files: `.asps/index/CONTEXT_GUIDE.md`.

**Escalation.** R-009 for architecture/rules/security/model-routing/self-improvement. Stops on branch/pointer mismatch or dirty tree.

**Subagents.** Zero by design — the file is explicit: *"Workers: zero (locked — PL coordinates, it does not execute)."*

**Known findings (F-026 run, 2026-06-16).** None at the L1 level; it consistently routed correctly. (Build-lead's failure to reach reviewers — see 2.4 — was *not* project-lead's fault.)

---

### 2.2 `asps-system-lead` (L2, primary) — `agents/system/asps-system-lead.md`

**Exact role.** *"The owner of ASPS runtime infrastructure and system assets — agents, skills, templates, configs, commands, hooks. It governs how the platform evolves and stays consistent; it does not own product features. It is the only lead that may modify protected runtime/catalog assets (never `rules/**`), and it routes authoring to a runtime-specific author rather than writing assets itself."*

**Problems it solves.**
- *Governs the catalog* — every agent/skill/command/template addition goes through it.
- *Routes by runtime* — Claude asset vs OpenCode asset is a hard contract; system-lead picks the right author.
- *Preserves the byte-parity moat* — edits the catalog, never the live `.opencode/**`/`.claude/**`.
- *Routes commits* — work ends with `committer`, never with system-lead committing.

**Interactions.** Delegates to:
- `governance` — for any `rules/**` or permission-config change (R-009 gated).
- `committer` — for any commit (the ONLY agent that commits).
- `asps-opencode-author` — for `.opencode/agents/*` / skills / commands / config.
- `asps-claude-author` — for `.claude/agents/*` / skills / commands / settings.

Does **not** implement product features, **does not** edit `rules/**` directly, **does not** commit/push.

**Skills.** `asps-lead-operating-protocol`, `asps-context-navigation`, `asps-feature-workflow`, `commit-discipline`, `asps-trace-discipline`, `security-review`, `event-emission`, `stable-base`, `fallback-recovery`.

**Permissions / tools.** `mode: primary`; `model: standard`; read/list/search allow; edit ask; bash ask (read-only `asps validate-*|status`, `git status|diff`; deny `git commit|push`); webfetch/websearch ask. `defaults.yaml` further pins: `bash "*": allow` (full), `task: asps-opencode-author: allow`, `committer/governance: ~` (folded back via system-lead itself), webfetch allow.

**Workflows.** (a) Classify the system change → (b) Inspect state + deps + duplication → (c) Route authoring to the runtime-specific author, one asset at a time, to the current contract → (d) Verify with `asps validate-runtime|validate-index|doctor` → (e) Hand the commit to `committer`.

**Escalation.** Stops on R-009: rules / permission / model-routing / security change. Splits a task that spans two asset types or two runtimes.

**Subagents.** `governance`, `committer`, `asps-opencode-author`, `asps-claude-author`. Also `asps-bootstrap` (transient onboarding) for new projects.

**Critical subagent — `governance` (`agents/system/governance.md`).** *"The ONLY agent permitted to edit `rules/**` and permission configs; every change is gated behind the R-009 human gate."* It's a **leaf** (delegates to none). It only writes `rules/**` and `profiles/defaults.yaml` permission blocks, and only after explicit R-009 clearance. The change is handed to `committer` for the final gate + commit. This is the **only path** to mutate the constitution.

**Critical subagent — `committer` (`agents/system/committer.md`).** *"The only agent permitted to commit to Git."* Receives reviewed, gate-green work from any lead/subagent. Runs the **product gate** (`.asps/gates.yaml`): `ruff check`, `ruff format --check`, `mypy`, `pytest` (split: `pytest -n auto -m "not perf"` then `pytest -q -m perf -p no:xdist` because perf tests false-fail under xdist). Verifies the commit message is **real** (rejects empty, "WIP", "placeholder", "fix", "tmp"). **Stages explicit paths only** — never `git add -A`. Refuses on any gate failure or junk message. Never pushes, amends, rebases, force-pushes, or skips hooks. After commit, the `post-commit` hook records it via `trace-pipe`; no foreground trace call needed.

**Critical subagent — `asps-opencode-author` and `asps-claude-author`.** Write **one** runtime asset at a time (agent, skill, command, config, plugin, template) to the current official contract. Read `.asps/context/OPENCODE_OFFICIAL_REFERENCES.md` (or the Claude equivalent) and the `asps-{opencode,claude}-runtime-authoring` skill first; `webfetch` only as a fallback. For agents: explicit `mode`/`model`/`permission`, least-privilege allowlists, thin body. For skills: folder name = frontmatter `name`, `## Purpose` present. Hand finished work to `committer` — never commit themselves. Stop and hand back to `asps-system-lead` for any approval-gated or cross-asset task.

**Critical subagent — `asps-bootstrap` (`agents/system/asps-bootstrap.md`).** **Transient onboarding agent**. *"It is the ONLY agent that knows about bootstrap; once `bootstrap.done` is recorded it is gone and `project-lead` takes over."* One-time SEED/RESUME: detect → confirm → `asps bootstrap --write` → promote 5 primaries → **self-clean** (remove the bootstrap agent/skill/workflow/templates/shell scripts from the product runtime) → record `bootstrap.done` in the manifest. Default to `project-lead`; user may override to `asps-lead` or any `[a-z][a-z0-9-]*` name.

**Known findings.** (1) `asps-system-lead` was carrying a `mode: primary` pin but its model was `opencode/minimax-m3-free` (unavailable) — silent dead runs. **Fixed:** pinned to `opencode-go/deepseek-v4-pro` (commit `7ed6a69`). (2) R-009 enforcement needed generalization — Phase 0.7 (D-12) generalized the approval-ledger to a deterministic gate.

---

### 2.3 `asps-planning-lead` (L2, primary) — `agents/planning/asps-planning-lead.md`

**Exact role.** *"The owner of the planning lifecycle. It turns an idea/request/problem into an execution-ready plan (spec → clarify → architecture → tasks → acceptance → review/test strategy) so that building succeeds on the first pass. It does not build, does not review for acceptance, and does not approve quality — it maximises the probability of successful execution before implementation begins."*

**Problems it solves.**
- *Turns intent into a build-ready plan* — the planning phase is the highest-leverage part: most of the build rides on it.
- *P0–P9 pipeline orchestration* — sequential pipeline pattern; each phase has a named sub-agent, skill, template, validation, and trace event (see `PLANNING_WORKFLOW.md`).
- *Clarifies ambiguity* — 10-category ambiguity scan + max-5 prioritized questions (via `clarify`).
- *Decomposes into task packets* — sized for cheap builders, each with scope/dependencies/acceptance.
- *Critiques the plan* — `plan-critic` after PLAN + TASKS (multi-perspective: coverage, tests, risks, constitution alignment).
- *Asks for research, not doing it* — routes to `lead-researcher` rather than researching itself.

**Interactions.** Delegates to `clarify` (P1b ambiguity scan), `task-decomposer` (P7 PLAN → ordered TASKS), `idea-capture` (P0 raw idea → intake). Hands off to `asps-build-lead` at P9. R-009 gates P9 (architecture, rules, security, model-routing, self-improvement).

**Skills.** `asps-lead-operating-protocol`, `asps-context-navigation`, `spec-to-plan`, `spec-quality`, `plan-critic`, `clarify-routing`, `task-format`, `done-reporting`, `fallback-recovery`.

**Permissions / tools.** `mode: subagent`; `model: standard`; read/list/search allow; edit ask; bash ask (read-only); webfetch/websearch ask. `defaults.yaml` further suppresses folded delegates: `prd-writer, spec-writer, plan-architect, acceptance-designer, lead-researcher: ~`.

**Workflows.** `PLANNING_WORKFLOW.md` (P0–P9): P0 Intake (idea-capture) → P1 Project Spec (prd-writer) → P1b Clarify (clarify) → P2 Research (lead-researcher / docs-fetcher) → P3 Technical Plan → P4 Architecture Plan (R-009) → P5 Feature Map → P6 Feature Implementation Plan → P7 Task Packets (task-decomposer) → P8 Analyze/Review (plan-critic) → P9 Approve (R-009).

**Escalation.** Hands back to `project-lead` for cross-domain or out-of-scope requests. R-009 human gate at P9. If research cannot verify a volatile choice, marks `[UNVERIFIED]` and raises the risk.

**Subagents.** `clarify`, `task-decomposer`, `idea-capture`. Plus shared helpers.

**Known findings.** The `prd-writer` agent referenced in `PLANNING_WORKFLOW.md` P1 is **missing** — F-027 (designed, not built) noted as a real gap. `clarify.md` itself notes its taxonomy was *"harvested from Spec Kit clarify.md (MIT). D-008."* Mode scaling (vibe / MVP / production) is designed but not yet wired (REFACTOR-PLAN §1.5-D).

---

### 2.4 `asps-build-lead` (L2, primary) — `agents/build/asps-build-lead.md`

**Exact role.** *"The owner of implementation execution. It turns an approved plan + task packets into completed, gate-green work by orchestrating builder workers — it does not primarily write code itself, and it does not plan or give final acceptance. It protects scope and architecture, runs the product gate first, and tracks progress until the feature is genuinely done."*

**Problems it solves.**
- *Owns the build vertical* — pre-work, packet validation, builder selection, gate enforcement, progress tracking, evidence.
- *Gates-first (R-002)* — `.asps/gates.yaml` must pass before "done" — never just trusts the builder's report.
- *Scope discipline* — never touches files outside `scope.allowed` (R-001).
- *Routes commits* — through `committer`; never commits directly.

**Interactions.** Delegates implementation to `python-builder` / `api-builder`. Routes commits to `committer`. Uses shared helpers for context. Escalates gate failures to `asps-fix-lead` via `project-lead`.

**Skills.** `asps-lead-operating-protocol`, `asps-context-navigation`, `asps-feature-workflow`, `gates-first`, `gate-running`, `scope-control`, `done-reporting`, `fallback-recovery`.

**Permissions / tools.** `mode: subagent`; `model: standard`; read/list/search allow; edit ask; bash ask (gate + read-only); webfetch/websearch ask. `defaults.yaml` further pins: `bash "*": allow`, `edit: allow`, `task: python-builder, api-builder: allow`, `task: database-builder, frontend-builder, config-builder, refactor-builder, docs-builder: ~` (folded).

**Workflows.** `BUILD_WORKFLOW.md`. Per packet:
1. Read the packet; verify `scope.allowed` (R-001) and active-feature pointer.
2. Validate the packet — planning output is **not** trusted blindly; build-lead is the final execution gate.
3. Delegate to the matching builder with enriched context.
4. Run the **product gate** as ONE command (`.asps/gates.yaml` — never hardcoded `pytest`). On FAIL: produce a failure summary; trivial fix → builder directly; structural → hand to `asps-fix-lead`.
5. On PASS: hand to `tester → reviewer` per `REVIEW_TEST_LOOP.md`.
6. Trace every step (R-007): `delegation`, `edit`, `gate_result`, `fail`, `phase_end`.

**Escalation.** (a) Stop if `.asps/gates.yaml` is missing. (b) Stop if a task needs a cross-domain change. (c) On a failed gate it cannot scope minimally, hand the failure summary up. (d) **Hard cap: 3 attempts max** — re-delegate to the worker with only the failing gate output, then a second-opinion attempt, then **STOP** and write `REVIEW_NEEDED` to the review queue. (e) R-009 for architecture/rule/gate changes.

**Subagents.** `python-builder`, `api-builder`. Plus shared helpers. (Intended to reach `asps-tester` / `asps-reviewer` / `asps-fix-lead` per the documented review handoff, but **`task:` permission blocks it** — see Known Findings.)

**Known findings (F-026 run, the load-bearing one).** *"Lead builder cannot reach any reviewer. Its prose says 'on gate pass, hand off to the tester→reviewer loop,' but its `task:` permission only allows `python-builder` and `api-builder`. So review **cannot happen inside the loop** — the claimed handoff is blocked by the permission block."* (`local/agent-notes/asps-build-lead.md`) This is the **biggest open gap**. Decision `D-build-lead-1` is unapplied: either grant the permission OR rewrite the prose. Currently the reviewer is parked as `REVIEW_NEEDED` for the human to drive. Also: builders must run `.asps/gates.yaml` verbatim, never ad-hoc `pytest` (perf tests false-fail under xdist). And builders wrote ~13 zero-byte junk files (shell-redirect misfires) — needs a no-stray-file guard.

---

### 2.5 `asps-reviewer` (L2, primary) — `agents/review/asps-reviewer.md`

**Exact role.** *"The independent quality authority. It answers one question — 'should this be accepted?' — by evaluating a plan or diff against spec, scope, architecture, gates, and ASPS rules. It does not plan, does not build, and never reviews its own work. Read-only (R-004): testing tells us whether it works; review decides whether it should be accepted."*

**Problems it solves.**
- *Independent, evidence-based acceptance* — not a tool check, not a developer gut check.
- *The four-outcome verdict* — **approve · approve-with-notes · changes-requested · escalate** — with evidence.
- *Multi-perspective fan-out* — delegates to `security-reviewer` (OWASP/injection/auth/exposure) and `commit-reviewer` (scope/status/branch fit), aggregates their findings, owns the final verdict.
- *Traceability check* — R-001 scope, R-002 gates-first, R-005 tests-as-spec, FR/SC → task → acceptance.

**Interactions.** Receives evidence from `asps-build-lead` (post gate) and `asps-tester`. Delegates to `security-reviewer` and `commit-reviewer`. Hands back to `project-lead` on changes-requested; gates `REVIEW_NEEDED` to human on architecture/rules/security/model-routing (R-009).

**Skills.** `asps-lead-operating-protocol`, `asps-context-navigation`, `review-checklist`, `scope-audit`, `architecture-review`, `security-review`, `done-reporting`, `fallback-recovery`.

**Permissions / tools.** `mode: subagent`; `model: standard`; read/list/search allow; **edit deny**; bash allow (read-only `asps status|validate-*`, `git status|diff`; deny `git commit|push`); webfetch/websearch deny. `defaults.yaml` further suppresses folded reviewers: `architecture-reviewer, style-reviewer: ~`.

**Workflows.** `REVIEW_TEST_LOOP.md`. (1) Gate must pass before review starts. (2) Read-only checks: scope (R-001), gates (R-002), tests-as-spec (R-005), correctness vs task packet. (3) Decide verdict. (4) On approve: stage explicit paths and commit (R-004 one-writer; the reviewer is the committer). (5) Mark task `[x]`, update `CURRENT_STATE.md`, trace.

**Escalation.** Genuine disagreement or out-of-scope → `project-lead`. R-009 for architecture/rules/security/model-routing. Captures the lesson when a stronger model catches a miss (R-006 — *Teach*).

**Subagents.** `security-reviewer`, `commit-reviewer`. (Architecture-reviewer and style-reviewer folded into the lead via `review-checklist` + `architecture-review` skills, per D-026.)

**Known findings.** R-004 keeps it honest — read-only. The "reviewer is the committer" rule keeps responsibility fused: the verdict and the commit share one brain.

---

### 2.6 `asps-fix-lead` (L2, subagent) — `agents/fix/asps-fix-lead.md`

**Exact role.** *"The recovery authority. It receives a gate/test failure, finds the root cause (not the symptom), applies the minimal safe fix, and loops until the gate is green — without scope creep or architecture drift. It does not plan features or give acceptance; it restores intended behaviour."*

**Problems it solves.**
- *Cause over symptom* — RCA discipline, hybrid flow routing.
- *Minimal-diff discipline* — fix only what the failure identifies (R-001).
- *Red→green loop* — gate-fixer loops: fix → gate → pass until green.
- *Severity-aware fix* — classification first (regression vs pre-existing vs flaky vs scope-violation) via `bug-triager`.

**Interactions.** Receives failure summaries from `asps-build-lead` (gate fails) and `asps-tester` (test regressions). Delegates to `bug-triager` (read-only triage) and `gate-fixer` (smallest diff to green). Routes finished work to review (via project-lead).

**Skills.** `fallback-recovery`, `gates-first`, `scope-control`, `minimal-diff`. (Note: a `root-cause-analysis` skill is recommended in the design but not yet created — see SHIP-PLAN E-2 / `CORE-AGENTS-PLAN.md` §4.7.)

**Permissions / tools.** `mode: subagent`; `model: standard`; read/list/search allow; edit ask; bash ask (gate + read-only); webfetch/websearch ask. `defaults.yaml` further pins: `task: regression-guard, asps-reviewer: ~` (folded); webfetch/websearch deny.

**Workflows.** (1) Validate/reproduce the issue; gather logs + recent changes + the failure summary. (2) Find root cause (not symptom); choose minimal fix surface. (3) Apply within scope. (4) Re-run the product gate. (5) Lock the fix with a regression test. (6) Record the fix report. **Hard cap: 3 attempts max**, then write `REVIEW_NEEDED` to `.asps/dashboard/review-queue.jsonl`.

**Escalation.** If the fix needs an architecture/plan change → hand back up (don't redesign here). Never changes architecture/rules to work around a bug (R-009).

**Subagents.** `bug-triager` (read-only classification, regression/pre-existing/flaky/scope-violation), `gate-fixer` (the smallest red→green diff). (Regression-guard was folded into the fix-lead protocol — D-026.)

**Known findings.** The hybrid flow was a real design choice — fix-lead runs a structured triage + minimal-diff loop, not "try random fixes." This is one of the most disciplined agents in the roster.

---

### 2.7 `asps-tester` (L2, subagent) — `agents/test/asps-tester.md`

**Exact role.** *"The validation authority. It owns testing strategy, gate enforcement, and failure triage, producing objective evidence (pass/fail, coverage) through red→green discipline. It produces evidence, not acceptance — review decides acceptance."*

**Problems it solves.**
- *Evidence not approval* — the tester never approves features (that's reviewer's job).
- *Red→green discipline (R-005)* — failing test first, then green; never weaken a test to pass.
- *Selective/affected tests* — test the change surface, not always the whole suite.
- *Failure classification* — flaky / regression / pre-existing gap, with priority (P0/P1/P2).

**Interactions.** Called after build-lead's gate passes (per `REVIEW_TEST_LOOP.md`). Delegates to `test-author` for new test creation. Hands persistent failures to `asps-fix-lead` via `project-lead`.

**Skills.** `gates-first`, `gate-running`, `coverage-analysis`, `fallback-recovery`.

**Permissions / tools.** `mode: subagent`; `model: standard`; read/list/search allow; edit ask; bash ask (test runners + `asps validate-*`; deny `git commit|push`); webfetch/websearch deny. `defaults.yaml` further suppresses folded test helpers: `gate-runner, coverage-analyst: ~`.

**Workflows.** (1) Classify the testing need; pick test types per the plan. (2) Drive red→green. (3) Run the gate, analyse results, report evidence + coverage. (4) Triage failures (flaky vs regression). (5) If new failures found, produce a test-failure summary and route back to the builder. (6) Trace (R-007).

**Escalation.** Persistent failures → `asps-fix-lead` (Blocked) via `project-lead`. R-009 for gate/rule/model-routing changes.

**Subagents.** `test-author` (red→green test author — write failing test first, verify implementation makes it pass, never weaken an existing test, produce TEST_REPORT). (Coverage-analyst + gate-runner folded via D-026; `gates-first` + `coverage-analysis` skills cover the gap.)

**Known findings.** Coverage analysis was deliberately folded into tester rather than a separate subagent — D-026 lean roster. Recommendation: add `fallback-recovery` to the skill list (consistency with other leads; the uncommitted PART 3a runbook fix).

---

### 2.8 `lead-researcher` (L2, subagent) — `agents/research/lead-researcher.md`

**Exact role.** *"The knowledge authority. It keeps ASPS's runtime/reference knowledge current — fetches and validates official docs, packages reusable references, and harvests skill candidates. Research once, reuse everywhere. It does not build, plan, or register assets itself."*

**Problems it solves.**
- *Cache-first research* — check `.asps/research/` and `.asps/context/*_OFFICIAL_REFERENCES.md` first; don't repeat.
- *Harvest path (D-008)* — record → check source/license → adapt → prove → review → promote.
- *Version/freshness validation* — every volatile choice gets a dated proof link or `[UNVERIFIED]`.

**Interactions.** Receives research requests from `asps-planning-lead` (P2), `asps-system-lead` (cross-domain skill registration), and `project-lead`. Delegates to `codebase-explorer`, `docs-fetcher`, `web-researcher`. Hands validated knowledge + skill candidates to `asps-system-lead` for registration — **never** registers assets itself.

**Skills.** `codebase-mapping`, `docs-harvest`, `source-ranking`, `dependency-audit`, `fallback-recovery`.

**Permissions / tools.** `mode: subagent`; `model: standard`; read/list/search allow; edit ask; bash ask (read-only); **webfetch allow; websearch allow**. `defaults.yaml` further pins: `task: dependency-scout, asps-system-lead: ~` (folded/suppressed — research doesn't delegate back to system-lead via the task field; the cross-handoff is by protocol).

**Workflows.** (1) Classify the research need; check cache first. (2) Fetch from authoritative sources; validate version/freshness; record sources. (3) Package into a reusable reference / skill candidate. (4) Hand to `asps-system-lead` for registration (D-008).

**Escalation.** Routes validated knowledge to `asps-system-lead`. R-009 before adding a new external source of record or a large reference.

**Subagents.** `codebase-explorer` (read-only structural search — "where is X? which files import Y?"), `docs-fetcher` (fetch official docs, distill to `*_OFFICIAL_REFERENCES.md` shape, with source URL + retrieval date + license note), `web-researcher` (targeted web search/fetch, always cite sources, distinguish facts from opinions). Dependency-scout was folded into `docs-fetcher` — D-026.

**Known findings.** Body must state the **cache-first** rule and the **skill-candidate → System Lead** handoff — research never registers assets itself. Recommendation: add `fallback-recovery` to the skill list (consistency with other leads; the uncommitted PART 3a runbook fix).

---

## 3 · The L3 Worker Roster (per-agent one-liners)

Every worker is a **leaf** (Delegates to: none). They were audited, and the relevant ones below.

### 3.1 Build workers
- **`python-builder`** — *Implement one scoped feature's Python work (code + tests), staying inside allowed paths and proving every change with deterministic gates.* Skills: `gates-first`, `scope-control`, `asps-trace-discipline`, `minimal-diff`. Model: standard. **R-005 red→green enforced.** *Known issue:* skipped `ruff format` once and wrote ~13 zero-byte junk files (shell-redirect misfires) — needs a no-stray-file guard and a `ruff format` step in the gate.
- **`api-builder`** — *Implement one scoped API/endpoint build unit (REST/GraphQL/RPC).* Skills: `gates-first`, `scope-control`, `stable-base`, `asps-trace-discipline`. Model: standard.

### 3.2 Fix workers
- **`bug-triager`** — *Read-only triage: classify a failure (regression / pre-existing / flaky / scope-violation), produce a root-cause hypothesis + minimal reproduction, recommend a fix surface, with confidence level. Never edits.* Skills: `gates-first`, `asps-trace-discipline`. Model: standard.
- **`gate-fixer`** — *Receive a triage report, apply the smallest possible diff to turn red gate green, loop up to 3 times.* Skills: `scope-control`, `red-green`, `stable-base`, `asps-trace-discipline`. Model: standard. *Hard rules:* never weaken a test (R-005), never widen to a feature, never edit files not in the triage report.

### 3.3 Test worker
- **`test-author`** — *Write a failing test first (red), then verify the implementation makes it pass (green). Coverage for happy path / edge / error / boundary. Never weaken or remove an existing test.* Skills: `gates-first`. Model: standard. Hands off to `asps-fix-lead` if implementation doesn't make tests pass.

### 3.4 Review workers
- **`security-reviewer`** — *Audit one diff for OWASP top-10, injection, broken auth, exposure, XXE, broken access control, security misconfig, XSS, insecure deserialization, known-vuln components, insufficient logging. CVE check via websearch allowed. Verdict: CLEAN / FINDINGS / BLOCKED.* Skills: `review-checklist`, `security-review`. Model: standard. BLOCKED → R-009.
- **`commit-reviewer`** — *Pre-commit gate: verify all changed files are in `scope.allowed`, none in `scope.forbidden`, status files present and green, branch matches active feature pointer. Verdict: APPROVED / CHANGES_REQUESTED / BLOCKED → hands to `committer`.* Skills: `commit-discipline`, `scope-control`. Model: standard. *Never* commits, pushes, or runs `git add` (R-004).

### 3.5 Research workers
- **`codebase-explorer`** — *Read-only structural search — where is X? which files import Y? what's the directory layout? find tests for module Z. Read `.asps/context/` first for orientation. Use glob/grep + read-only bash (rg/fd/find/ls) — never build/test/install.* Skills: `asps-context-navigation`, `codebase-mapping`. Model: standard.
- **`docs-fetcher`** — *Fetch the latest official docs for one tool/topic, snapshot, distill into a `*_OFFICIAL_REFERENCES.md` draft. Record source URL + retrieval date + license. Hand draft to `lead-researcher`; never promote.* Skills: `docs-harvest`. Model: cheap. Webfetch/websearch allow.
- **`web-researcher`** — *Targeted web search/fetch with citations; prefer official docs; distinguish facts from opinions; flag unverified claims. No `bash` (web tools + file reading only).* Skills: `asps-context-navigation`, `source-ranking`. Model: standard. Webfetch/websearch allow.

### 3.6 Planning workers
- **`clarify`** — *Run a 10-category ambiguity scan on the SPEC, ask max-5 prioritized questions one-at-a-time with recommendations, integrate accepted answers into `## Clarifications`. Re-validate spec quality checklist.* Skills: `clarify`, `asps-trace-discipline`, `clarify-routing`. Model: standard. (Taxonomy harvested from Spec Kit's clarify.md, MIT, D-008.)
- **`task-decomposer`** — *Break an approved PLAN into a sequenced, dependency-ordered TASKS.md with build-unit task packets. Each task scoped to one build-unit (one agent session) with scope/deps/effort/acceptance/exact file targets. Tasks must be dependency-ordered.* Skills: `spec-to-plan`, `scope-control`. Model: standard.
- **`idea-capture`** — *Capture a raw idea and structure it into a P0 intake document — goal, problem, value, constraints, rough scope, initial risks.* Skills: `spec-to-plan`, `scope-control`. Model: cheap.

### 3.7 Shared read-only helpers
- **`project-explorer`** — *Shared helper: explore repo structure, find files matching a pattern, search for a symbol, return relevant context. Cheap, fast, never edits. Confirms repo root first.* Skills: `asps-context-navigation`. Model: cheap. **The most general-purpose helper.**
- **`context-feeder`** — *Shared helper: return compact, task-scoped context for any agent by reading the context pyramid (L1–L4) — so the caller loads only what it needs.* Skills: `asps-context-navigation`. Model: cheap. **Stops at the requested level; never interprets.**
- **`context-summarizer`** — *Shared helper: condense recent traces, changes, run summaries into short context-file updates — keeps the project brain current without manual effort. Writes `.asps/context/*.md`, `.asps/current/*.json`, `dashboard/STATUS.md`.* Skills: `asps-context-navigation`, `asps-trace-discipline`. Model: cheap. **Keep summaries under 5 bullet points each.**

### 3.8 Transient onboarding
- **`asps-bootstrap`** — Already covered under system-lead. *One-time, self-deleting.*

---

## 4 · The Core Loop (Plan → Build → Review → Test → Develop)

The **deterministic spine** — what makes the cheap-model bet work.

```text
                            project-lead (L1, primary)
                                       │
                       classify → route → delegate (one of 7)
                                       │
              ┌────────┬─────────┬──────┴──────┬─────────┬─────────┬─────────┐
              ▼        ▼         ▼             ▼         ▼         ▼         ▼
         planning   build    reviewer     system     fix       test     research
         (P0–P9)   (impl)   (verdict)   (catalog)  (RCA)    (evidence) (knowledge)
              │        │         │             │         │         │         │
              │        ▼         │             │         │         │         │
              │   gates-first    │             │         │         │         │
              │   (R-002)        │             │         │         │         │
              ▼        ▼         ▼             ▼         ▼         ▼         ▼
         PLAN+TASKS  build  REVIEW_REPORT   registered  red→green  TEST_  RESEARCH_NOTE
              │     REPORT    APPROVED?      asset?     green       REPORT
              │        │         │             │         │         │
              └────┬───┴────┬────┴────────┬────┘         │         │
                   │        │             │              │         │
                   ▼        ▼             ▼              ▼         ▼
                committer (the ONLY committer) ──►  post-commit hook ──► trace-pipe
                                                       │
                                                       ▼
                                            .asps/traces/ + dashboard
```

**Per-feature vertical** (from `BUILD_WORKFLOW.md` + `REVIEW_TEST_LOOP.md`):
1. **Start** — `git switch -c feature/F-XXX`, `active_feature.json` updated, `feature.yaml`+`SPEC.md`+`PLAN.md`+`TASKS.md`+`ACCEPTANCE.md` created. (`NEW_FEATURE_WORKFLOW.md` rules 1–6.)
2. **Plan** — `asps-planning-lead` runs P0–P9 (planning-lead → subagents: `idea-capture` → `prd-writer` (gap) → `clarify` → `lead-researcher` → `task-decomposer` → `plan-critic`). R-009 at P9.
3. **Build** — `asps-build-lead` reads packet → `TASKS.md` `[ ]` → `[~]` → delegates to `python-builder` / `api-builder` → builder implements → build-lead runs `.asps/gates.yaml` (R-002) → `[x]` and hands to `tester → reviewer` OR `[!]` and hands to `asps-fix-lead`.
4. **Fix** — `asps-fix-lead` (RCA via `bug-triager`) → `gate-fixer` (minimal red→green diff) → loop. Hard cap: 3 attempts. → `REVIEW_NEEDED` if blocked.
5. **Test** — `asps-tester` runs the gate as evidence, extends tests for coverage gaps, classifies failures, hands back to builder if needed.
6. **Review** — `asps-reviewer` (read-only) → fan-out to `security-reviewer` + `commit-reviewer` → verdict. On approve, reviewer stages explicit paths and commits.
7. **Commit** — `committer` runs the gate one last time, verifies the commit message is real, stages explicit paths only, commits. `post-commit` hook records via `trace-pipe`.
8. **Trace** — every step (delegation, edit, gate_result, fail, phase_end, git_commit) emitted as a curated event keyed by `run_id`. `asps trace-report` renders a timeline per run; `asps trace-rollup` aggregates by feature/agent/model. `dashboard/STATUS.md` is the human view.

**Three working modes (REFACTOR-PLAN §1.5-D, designed not yet wired):** one flow, three knobs — **vibe** (throwaway, fail-open, strong model, big chunks, not promotable), **MVP** (balanced, promotable via refactor-up), **production** (default, fail-closed, cheapest-sufficient). "Cheapest" is a *production* property earned by structure; vibe spends model power to skip structure. The matrix is *policy-as-data*, not `if mode == …`.

---

## 5 · Error Handling — Who Fixes What

| Failure | Who catches it | Who fixes it | Who reviews the fix |
|---|---|---|---|
| **Gate FAIL** (lint/format/types/tests) | `asps-build-lead` (run as ONE command) | Trivial → builder; structural → `asps-fix-lead` → `bug-triager` + `gate-fixer` | `asps-reviewer` (post-green) |
| **Test regression** (was green, now red) | `asps-tester` (P0 priority) | Hand back to builder | `asps-reviewer` |
| **Coverage gap** | `asps-tester` | `test-author` (red→green) | `asps-tester` |
| **Pre-existing test failure** | `asps-tester` (P2) | `asps-fix-lead` if in scope; else flag | `asps-reviewer` |
| **Flaky test** | `asps-tester` (mark `@pytest.mark.flaky`, follow-up task) | `asps-test-lead` / `test-author` | — |
| **Scope violation** (file outside `scope.allowed`) | `commit-reviewer` (BLOCKED) | Builder pulls it back, hand to author | `asps-reviewer` |
| **Junk / placeholder commit message** | `committer` (refuses) | Caller rewords | — |
| **Editor touched `rules/**` or `profiles/defaults.yaml` permissions** | `governance` (R-009 in code, Phase 0.7) | `governance` after R-009 approval | `asps-system-lead` |
| **Architecture / rules / model-routing change requested** | All leads (escalation rule) | Human via R-009 | Human |
| **Missing `.asps/gates.yaml`** | `asps-build-lead` (STOPS) | Owner creates it (R-009) | — |
| **OpenCode 3-level freeze** | Operational finding (NESTING-3-LEVELS.md) | Cap at 2 levels (D-028) | — |
| **3 failed fix attempts** | `asps-fix-lead` (hard cap) | `REVIEW_NEEDED` to review queue | Human + WSL Claude |
| **Subagent time-out / tool error** | Parent agent (re-delegates with clarified prompt) | Subagent or human | — |
| **Subagent in infinite loop** | `steps:` limit cuts it off (TRACEHOOKS.md) | Re-delegate | — |
| **Subagent can't reach a forbidden tool** | `task:` permission allowlist (prevented by design) | — | — |
| **Silent run** (edits without trace events) | `asps doctor --post-run` (4-hour window, `LD-7`) | The lead that should have traced | — |

**Hard invariant:** the committer refuses ANY commit on a gate failure or junk/placeholder message. **The build-lead** is the final execution gate — it does not trust the builder's report blindly. **The reviewer** is the final acceptance gate — it is the only committer of feature work, and it never reviews its own work.

---

## 6 · Profiles — How Specialization Works

A **profile** is a YAML file that selects which catalog assets a project receives (D-009). Files in `profiles/`:
- `base.yaml` — the shared base layer **every** project inherits (leads, core skills, templates, commands, hooks, scripts).
- `asps-self.yaml` — ASPS's own profile (selects the real seeded catalog).
- `python-cli.yaml` — example: a small Python CLI (adds `python-builder` on top of base).
- `full.yaml` — `include_all: true` (the entire catalog).
- `defaults.yaml` — export/model-routing defaults (NOT a profile; different schema).
- `_schema.md` — the profile field contract.
- `README.md` — how profiles work.

**Merge rule:** `resolve_export_profile` unions `base` with the named profile (deduped, base first); `include_all` expands to the full catalog. **Scope gate** (per-asset `Export scope`: `all` / `opencode-only` / `claude-only` / `export-only` / `factory-only`) decides per target. **Config filter** (`config.filter_assets`) drops anything disabled by user/project config.

**The 3-layer transform is the moat.** `L1 Catalog` (markdown, truth) → `export/transform` (profile-gated, per-runtime frontmatter) → `L2 Live runtimes` (`.opencode/`, `.claude/`, generated, disposable). **`promote` is the only sanctioned write** to live (hash-lock decision table: ADD / UPDATE / PROTECT / CONFLICT / UNTRACKED / UNCHANGED). The byte-parity test (`test_real_repo_regenerate_reproduces_every_live_file`) proves catalog regenerates live exactly — **the load-bearing invariant of the whole system**. (EA-9 honesty note: "byte-for-byte" is actually newline-normalized text identity; an LF policy is the real fix.)

**Model routing** lives in `profiles/defaults.yaml` as **data, not code** (D-9). Tiers: `cheap` / `standard` / `deep` / `ui` / `second_opinion`, mapped per runtime (`opencode` / `claude`):

```yaml
cheap:    opencode: opencode-go/deepseek-v4-flash | claude: haiku
standard: opencode: opencode-go/deepseek-v4-pro  | claude: sonnet
deep:     opencode: opencode-go/deepseek-v4-pro  | claude: opus
ui:       opencode: minimax/minimax-m3           | claude: sonnet
second_opinion: opencode: minimax/minimax-m2.7   | claude: haiku
```

Per-agent overrides (model/mode/permissions/tools) are keyed by agent name, runtime-mappable, and applied AFTER the catalog→runtime render. `null`/`~` suppresses a field entirely. The model is *policy data* (REFACTOR-ANALYSIS EA-4) — code carries only the resolution logic.

---

## 7 · Determinism & Reliability — The Whole System's Spine

The `ASPS_OPERATING_MODEL.md` puts the one idea plainly: **one small, deeply context-aware lead whose intelligence is a smart context pyramid + scoped skills, NOT a big prompt or big model, that never lets the system drift, duplicate, or over-build, on a machine where every step is deterministic** (skills / workflows / hooks / scripts / specialized agents) so **cheap models run almost all of it**.

**Seven patterns proven to work:**

1. **The 3-layer transform with byte-parity moat.** Edit the catalog, never the live. `promote` is the only sanctioned write. The test fails if anyone hand-edits a live body.
2. **One policy engine for hooks AND CLI.** Phase 0.1 (D-11, GE-1) collapsed scope/secret/junk/test-removal checks into a single module. The git hooks (pure shell, no Python dependency) and the Python CLI read the **same** rule data; a parity test proves they give the same verdict. (Proof it works: a Windows commit-guard that *looked* correct silently let bad commit messages through — the parity test caught it.)
3. **One trace writer, run_id-keyed.** Phase 0.2 (D-15b). Append-only JSONL, run_id joinable. Every event tagged with `kind + position + file registry + commit link`. `asps doctor` flags silent runs.
4. **One bootstrap path.** Phase 0.3 (D-15c). Python `asps bootstrap` is the engine; the shell/agent route *calls* it. No duplicate orchestration.
5. **Catalog content-conformance validator.** Phase 0.4 (D-14). Every "hand this to agent X" resolves to a real agent; no hardcoded model id; one agent shape; one skill frontmatter requirement. Catches the dangling-reference bug class.
6. **One law/config source-of-truth hierarchy.** Phase 0.5 (D-16). ARCHITECTURE / ROSTER_SPEC / BUILD_PLAN resolved into a stated hierarchy. Drift guards fail if `base.yaml ≠ ROSTER_SPEC` or the R-rule mirror diverges.
7. **Load-bearing warns → errors + R-009 code-enforced.** Phase 0.6–0.7. Generalized approval-ledger; an agent-path edit to `rules/**` is BLOCKED unless a human approval is on record. A recorded human approval passes.

**Plus the operational ones:**
- **Two-hook-class discipline** (`TRACEHOOKS.md`). Trace hooks (fire-and-forget, JSONL) vs enforcement hooks (synchronous, may block). Two paths, two classes.
- **`steps:` limits on all lead agents** (8–15). No infinite loops.
- **Explicit `task:` permission audit on all 49 agents**. Permission propagation bugs killed.
- **Continuation instructions on every lead**. "When a delegated sub-agent returns, process its result and continue — do NOT stop."
- **Two-pass gate standard** (`.asps/gates.yaml`): `pytest -n auto -m "not perf"` then `pytest -q -m perf -p no:xdist` (perf tests false-fail under xdist).
- **Windows CI = gate of record** (D-19). The shell hooks have a `.ps1` (Windows) version that a Linux machine never runs. Windows catches what Linux can't.
- **Pure functional core + thin I/O shell.** `transform`, `runtime_lock.decide`, `curate.derive` are all string-in/string-out. Easy to test, parallel-safe.
- **The promote hash-lock decision table.** Six outcomes (ADD/UPDATE/PROTECT/CONFLICT/UNTRACKED/UNCHANGED) derived from three inputs (regen/live/baseline hashes). Cleanly separates "safe to overwrite" from "human touched this."
- **Dry-run by default, everywhere.** `exporter` has no write path at all. `--write` is required to do anything. Safety is structural, not a flag you remember.
- **"Refuse to write into the ASPS repo."** `initializer.initialize_project` refuses if target is inside the source. `regenerate` refuses to write into the live runtime root. Footprint budget hard-fails an over-heavy export.
- **Local helper-prompt workflow** (`rules/SYSTEM_RULES.md` bottom). `local/`, `_local/`, `*.local.md`, `CLAUDE.local.md` are gitignored — helper context never leaks into Git history.
- **Bounded autonomy / D-1.** Self-heal = bounded restore from source-of-truth, never LLM-invent. Post-bootstrap ASPS writes only on user request.

**Two patterns still experimental / not landed:**
- **Working-modes mechanics** (REFACTOR-PLAN §1.5-D) — direction set, mechanics undefined (the 7 open questions: per-mode on/off matrix, storage, mode→model map, promotion mechanics, gate policy, subset scope, definition location).
- **3-level delegation on OpenCode** (D-028) — parked. OpenCode L3 freezes (Task tool has no timeout, no force-kill, hangs on forbidden tools). Cap at 2 levels; L1 coordinated by the human.

---

## 8 · Key Patterns (the 6 orchestration patterns from `PATTERNS.md`)

| Pattern | When to use | Used by | Pattern shape |
|---|---|---|---|
| **1. Orchestrator-Worker** | Most workflows (build, review, research, authoring) | `asps-build-lead`, `asps-system-lead`, `asps-planning-lead` | Lead decomposes work, assigns to specialists, integrates results |
| **2. Sequential Pipeline** | Planning (P0→P9), feature lifecycle | `asps-planning-lead` | Work passes through ordered stages, each producing a validated artifact before the next |
| **3. Fan-Out / Fan-In** | Multi-phase review, competing proposals, parallel research | `asps-reviewer` (→ security/architecture/style/commit), `lead-researcher` | Lead fans out to multiple independent sub-agents in parallel, then aggregates |
| **4. Multi-Agent Debate** | Architecture decisions, risk assessments, spec ambiguity resolution | `asps-planning-lead` (pending; template created) | Two or more agents with opposing perspectives debate; lead adjudicates |
| **5. Dynamic Handoff** | Cross-domain routing, gate failures, fix loops | `asps-lead` (routing table), `asps-fix-lead` (→ gate-fixer), `asps-build-lead` (→ builders) | Agent hands off with context about what was tried + why it failed |
| **6. Adaptive Planning** | Complex features with unknown design space | `asps-planning-lead` | Planning itself uses multiple agents; output of each informs the next; loop refines |

**Selection guide:**
- *Implement a feature* → Orchestrator-Worker → `asps-build-lead`
- *Plan a feature* → Sequential Pipeline → `asps-planning-lead`
- *Review a diff/plan* → Fan-Out/Fan-In → `asps-reviewer`
- *Decide architecture* → Multi-Agent Debate → `asps-planning-lead`
- *Bug appears mid-work* → Dynamic Handoff → `asps-fix-lead`
- *Unknown design space* → Adaptive Planning → `asps-planning-lead`
- *Research a topic* → Fan-Out/Fan-In → `lead-researcher`

---

## 9 · The 8 Subsystems (ASPS's 8 Areas)

Per `ASPS_OVERVIEW.md`, ASPS intends to be 8 subsystems (Core A/B/C/D/E ship first; F/G reserved seams):
- **A · Agents & skills (the catalog).** Core agents for plan/build/review/test, system agents, controlling agents. Core skills scoped per agent. Two-level delegation. Dynamic management. Profiles. Harvest path (D-008). Skill-quality-gate (later phase).
- **B · Planning.** Spec-driven flow upgraded for delegation. Research + latest-stack + doc-fetching. Multi-perspective plan review. Task decomposition into build-task packets sized for cheap models.
- **C · Build / lifecycle.** Lean roster driving plan → build → review → test. Deterministic `start` / `close-feature`. Rules, standards, security & database defaults — no wrong-direction or garbage builds.
- **D · Determinism & validation backbone.** One policy engine, git hooks (trace + enforcement), gates (lint/format/types/tests), step-by-step validation that blocks on any skipped/failed step. Workflows runnable deterministically.
- **E · Tracing & data substrate.** One trace writer keyed by `run_id`; append-only JSONL truth + normalized SQLite lens. Per-folder README + STATUS. Token-usage & cost-usage accounting per feature/agent/model/task.
- **F · Self-improvement.** Detect repeated work/patterns → propose templates/agents/skills. Agents learn from failures and never repeat. System upgrades itself (human-approved). Never weakens a gate.
- **G · Cockpit / dashboard.** Focused project overview + deep review/test/control + live monitor — a thin UI over a stable read-model so scoring/weights evolve without breaking the UI.
- **H · Install & onboarding.** One global install (Win/Linux); detects OS, runtimes, IDE tools. Two clean steps — `init` (export + scaffold) → `bootstrap` (validate, enrich, seed, cleanup). Engine pinned per project.

**Implementation status (2026-06-17):** Core A/B/C/D/E are **substantially built**. F-026 "Launch v0" shipped the thin end-to-end slice (install → init/bootstrap → plan/build/review/test → trace → dashboard) for the public v0. F (intelligence) and G (cockpit) are reserved seams.

---

## 10 · The 4 Theses (the decision lens)

From `REFACTOR-PLAN.md` §0, the four load-bearing theses:

1. **Determinism is the cost lever.** Shrink what the model must figure out. The cheapest model is correct when wrapped in a tight skill + script-tool + conformant template. (Phase 0 spine is the proof.)
2. **Evidence is the currency.** Each phase emits evidence — a report + a `gate_result` keyed to a git sha. Later actors *consume* it instead of redoing work. (Result-caching lifecycle in D-6.)
3. **Machine-checked invariants hold; prose-asserted ones rot.** Every "X must match Y" becomes a test or generated code. ("Prose rots; permissions hold." — `local/agent-notes/asps-build-lead.md`.)
4. **Capture-now, derive-later.** Record the full useful trace now (cheap, append-only). The intelligence that reads it comes later.

**Engineering principles (non-negotiable, apply to every unit):** Modular · DRY/single-source · testable (red→green, R-005) · clean & clear · scalable · maintainable. Concretely: one implementation per outcome; pure-core + thin-shell; structured data for machines, prose for humans; never edit catalog-managed live files in place; never weaken a gate/test/rule to pass; reserve seams, don't build the far layer.

---

## 11 · The Operating Model (the 12 principles from `ASPS_OPERATING_MODEL.md`)

1. **One small, deeply context-aware lead** whose intelligence is a smart context pyramid + scoped skills, NOT a big prompt or big model.
2. **Two layers** — foreground product agents + background "army" of hooks/workflows/cheap agents that trace, classify, update status, link commits→files, review, validate, self-improve.
3. **Agent file contract** — 10–50 lines of Markdown; one role, how to fetch context, the important skills. Detail in skills + the context pyramid.
4. **Skill scoping is the core mechanic** — each agent reads only the skills for its role. Specialization is the design and the token/quality control.
5. **Permissions = economy, not security** — each agent gets only its slice. Less context, sharper output.
6. **The context pyramid** — read only as deep as the task needs (L1 small always-on → L4+ drill-in). L1 = three files: identity (20 lines), current state, history (30 lines, one line per change with link).
7. **Tracing & per-folder status** — record every event (kind + position + file registry + commit). The trace store is *our* source of truth.
8. **Determinism over improvisation** — wrap every nondeterministic LLM step in a workflow/skill/hook/script. If a script can do it, a script does it.
9. **Capability → skill/subagent → reusable template** — when we need a capability, search first, build it as a skill or subagent, turn its output into a reusable template.
10. **Governance: no drift / no duplicates / no over-build** — preflight decides new vs done vs conflict vs improve before building.
11. **Model & cost split** — Opus = the brain (rare), cheap models = the hands (constant). Good instructions + full context → cheap models apply reliably.
12. **Sequencing in leverage order** — core working system → system-lead+governance → determinism layer → single source → then harvest/quality-gate/self-improvement/dashboard.
13. **Harmony** — every part works together; understand before building; grow without breaking alignment.

---

## 12 · What's PROVEN to Work vs What's Experimental

### PROVEN (gate-greens, in production):

- **The 3-layer transform with byte-parity moat.** 39 parity tests pass; byte-strict regeneration works.
- **One policy engine for hooks + CLI.** Caught a real Windows commit-guard bug that prose would never have caught.
- **One trace writer, run_id-keyed.** All trace tooling, dashboard, doctor, reports, lessons, improve work on the joined store.
- **Catalog content-conformance validator.** Catches dangling references, hardcoded model ids.
- **R-009 code-enforcement.** Approval-ledger blocks agent-initiated rules/permission/model-routing changes without human approval.
- **The lean 3-layer roster.** 1 + 7 + 20 = 28 agents, gate-greens, F-026 launched.
- **Bootstrap lifecycle (init-project → bootstrap → doctor).** Real on Windows + WSL2.
- **The 5-gate suite.** ruff check · ruff format --check · mypy · pytest (parallel non-perf) · pytest (serial perf) — two-pass standard adopted.
- **Profile-driven export + scope gates.** base + python-cli + asps-self + full profiles; runtime-conditional assets correctly excluded.
- **Hash-locked `promote` decision table.** 6 outcomes, every decision traceable, no clobber.
- **2-level delegation on OpenCode.** L2 lead → L3 worker proven by F-026 run; L1 coordinated by human.

### EXPERIMENTAL / designed-not-built / parked:

- **Working-modes mechanics** (REFACTOR-PLAN §1.5-D). Direction set (vibe/MVP/production), mechanics undefined. 7 open questions unresolved with the user.
- **3-level delegation on OpenCode** (D-028). Parked due to OpenCode freeze bug. Open issues #11865, #13841, #22167, #10802, #24342, #21176, #18378.
- **Claude Code delegation chain.** Designed to work; the exporter needs to emit `Agent(targets)` (R-009 fix, A1 from NESTING-3-LEVELS.md) — currently broken.
- **F-027 dynamic planning loop** (designed not built). Need: `asps plan` driver, mode×size matrix, missing `prd-writer`, plan-critic as a required gate, cost/usage control.
- **Self-improvement loop (Phase 5).** Skeleton in `improve.py` / `session_analyzer.py` / `lessons.py`; needs join + bounded-apply + measure-effect. *"Built, not proven on real data."*
- **Dashboard (Phase 6).** Static dashboard shipped; full cockpit (D-21…D-26) reserved.
- **`prd-writer` agent.** Referenced in `PLANNING_WORKFLOW.md` P1; missing from catalog.
- **Per-agent model routing on the cheaper side.** R-009, pending E-4.
- **Per-agent permission audit.** R-009, ongoing.
- **`root-cause-analysis` skill** for `asps-fix-lead`. Recommended; not yet created.
- **`system-doctor` skill** for `asps-system-lead`. Recommended; not yet created.
- **Script-tools ps1/sh pairs (~12 tools × 2 langs = largest duplication).** Open in REFACTOR-PLAN §3 (D-15a).
- **Per-agent `.claude.md` override vs canonical agent body.** Open / unverified (D-14(d)).
- **Brain-skeleton ×3 / brain-content-as-code-not-templates.** Open (IB-1).
- **The build-lead → reviewer reachability gap.** Open (`D-build-lead-1` from `local/agent-notes/asps-build-lead.md`).
- **Working modes (vibe/MVP/production) wired into gates + review/test rigor + model tier.** Designed; not wired.

---

## 13 · The "Single Idea" (one paragraph)

**One small, deeply-context-aware lead** (`project-lead`) whose intelligence is a **smart context pyramid + scoped skills**, NOT a big prompt or big model — that never lets the system **drift, duplicate, or over-build** — sitting on a machine where **every step is deterministic and controlled** (skills / workflows / hooks / scripts / specialized agents), so **cheap models run almost all of it**. The lead's intelligence comes from a smart context pyramid + scoped skills. Everything else exists to serve that agent and keep the project in harmony.

The 6 layer-2 specialized leads (planning, build, review, system, fix, test, research) each own one domain and fan out to 2–3 leaf workers. The 20+ leaf workers are disposable, single-purpose, and read-only or minimal-scope. The catalog is truth; the runtimes are disposable. The byte-parity moat proves it. The R-009 human gate protects the constitution. The trace store is the audit log. The result is a system that *proves itself into existence* — cheap models do production-grade work, repeatably, with full evidence.

---

## 14 · Agent Quick-Reference Table

| Agent | Layer | Mode | Model | Delegates to | Key skills | R/W | Web |
|---|---|---|---|---|---|---|---|
| `project-lead` | L1 | primary | standard | 7 L2 leads | lead-protocol, context-nav, request-routing, scope-control, done-reporting, fallback-recovery | R+edit-trace | no |
| `asps-system-lead` | L2 | primary | standard | governance, committer, opencode/author, claude-author | lead-protocol, context-nav, feature-workflow, commit-discipline, trace-discipline, security-review, event-emission, stable-base, fallback-recovery | R+edit-ask | ask |
| `asps-planning-lead` | L2 | subagent | standard | clarify, task-decomposer, idea-capture | spec-to-plan, spec-quality, plan-critic, clarify-routing, task-format, done-reporting, fallback-recovery | R+edit-ask | ask |
| `asps-build-lead` | L2 | subagent | standard | python-builder, api-builder | feature-workflow, gates-first, gate-running, scope-control, done-reporting, fallback-recovery | R+edit-ask | ask |
| `asps-reviewer` | L2 | subagent | standard | security-reviewer, commit-reviewer | review-checklist, scope-audit, architecture-review, security-review, done-reporting, fallback-recovery | **R only** | no |
| `asps-fix-lead` | L2 | subagent | standard | bug-triager, gate-fixer | fallback-recovery, gates-first, scope-control, minimal-diff | R+edit-ask | ask |
| `asps-tester` | L2 | subagent | standard | test-author | gates-first, gate-running, coverage-analysis, fallback-recovery | R+edit-ask | no |
| `lead-researcher` | L2 | subagent | standard | codebase-explorer, docs-fetcher, web-researcher | codebase-mapping, docs-harvest, source-ranking, dependency-audit, fallback-recovery | R+edit-ask | **yes** |
| `governance` | L3 | subagent | standard | none (leaf) | trace-discipline, scope-control | R+edit-**rules only** | no |
| `committer` | L3 | subagent | cheap | none (leaf) | commit-discipline, trace-discipline | R+bash-git | no |
| `asps-opencode-author` | L3 | subagent | cheap | none (leaf) | opencode-runtime-authoring, context-nav | R+edit | yes (fallback) |
| `asps-claude-author` | L3 | subagent | cheap | none (leaf) | claude-runtime-authoring, context-nav | R+edit-ask | yes (fallback) |
| `asps-bootstrap` | L3 | primary (transient) | standard | none (drives CLI) | asps-bootstrap, context-nav | R+edit-scope | no |
| `python-builder` | L3 | subagent | standard | none (leaf) | gates-first, scope-control, trace-discipline, minimal-diff | R+edit-impl | no |
| `api-builder` | L3 | subagent | standard | none (leaf) | gates-first, scope-control, stable-base, trace-discipline | R+edit-api | no |
| `bug-triager` | L3 | subagent | standard | none (leaf) | gates-first, trace-discipline | **R only** | no |
| `gate-fixer` | L3 | subagent | standard | none (leaf) | scope-control, red-green, stable-base, trace-discipline | R+edit-scope | no |
| `test-author` | L3 | subagent | standard | none (leaf) | gates-first | R+edit-test | no |
| `security-reviewer` | L3 | subagent | standard | none (leaf) | review-checklist, security-review | **R only** | ask (CVE) |
| `commit-reviewer` | L3 | subagent | standard | none (leaf) | commit-discipline, scope-control | **R only** | no |
| `codebase-explorer` | L3 | subagent | standard | none (leaf) | context-nav, codebase-mapping | **R only** | ask |
| `docs-fetcher` | L3 | subagent | cheap | none (leaf) | docs-harvest | R+edit-ask | **yes** |
| `web-researcher` | L3 | subagent | standard | none (leaf) | context-nav, source-ranking | R (no bash) | **yes** |
| `clarify` | L3 | subagent | standard | none (leaf) | clarify, trace-discipline, clarify-routing | R+edit-spec | ask |
| `idea-capture` | L3 | subagent | cheap | none (leaf) | spec-to-plan, scope-control | R+edit-ask | ask |
| `task-decomposer` | L3 | subagent | standard | none (leaf) | spec-to-plan, scope-control | R+edit-tasks | ask |
| `project-explorer` | helper | subagent | cheap | none (leaf) | context-nav | **R only** | no |
| `context-feeder` | helper | subagent | cheap | none (leaf) | context-nav | **R only** | no |
| `context-summarizer` | helper | subagent | cheap | none (leaf) | context-nav, trace-discipline | R+edit-context | no |

---

## 15 · Compact Synthesis

The OLD ASPS system is a **file-first, deterministic, two-layer agentic factory** where:

- **One L1 lead** (`project-lead`) talks to the human and routes to exactly one of 7 L2 leads.
- **7 L2 leads** (5 primary + 2 subagent-promoted; or 7 with planning/build/review/system as primary + fix/test/research as subagent in the D-028 lean model) own the seven domains — plan / build / review / system / fix / test / research — and fan out to 2–3 leaf workers each.
- **~20 L3 workers** are leaves: each owns one task, never delegates. Builders write code, fixers apply minimal diffs, reviewers check one thing only, researchers fetch and distill, authors author one asset at a time, the committer is the ONLY committer, governance is the ONLY rules editor (R-009 gated).
- **~7 shared helpers** (project-explorer, context-feeder, context-summarizer) are read-only context-assembly agents any lead can call.
- **The system-lead owns the catalog** — agents/skills/commands/templates/hooks. It routes authoring to `asps-opencode-author` or `asps-claude-author` based on the runtime contract.
- **The 3-layer transform with byte-parity moat** is the load-bearing invariant: catalog → profile-filtered export → live runtime; a single test proves catalog regenerates live exactly.
- **R-001 through R-009** are the constitution, frozen, only the `governance` agent can edit them, and only after a human approval record.
- **R-007 (Trace)** means no silent runs: every delegation, edit, gate, fail, commit emits a curated event keyed by `run_id` and persisted to append-only JSONL, with a rebuildable SQLite lens.
- **R-002 (Gates-first)** means `.asps/gates.yaml` runs as ONE command before "done" — `ruff check` · `ruff format --check` · `mypy` · `pytest -n auto -m "not perf"` · `pytest -q -m perf -p no:xdist`. Windows CI is the gate of record.
- **The 6 orchestration patterns** (Orchestrator-Worker, Sequential Pipeline, Fan-Out/Fan-In, Multi-Agent Debate, Dynamic Handoff, Adaptive Planning) match the situation to the right structure.
- **The 3 working modes** (vibe/MVP/production) dial rigor — vibe is throwaway, MVP is promotable, production is default and cheapest-sufficient.
- **Determinism is the cost lever** — every LLM step is wrapped in a workflow/skill/hook/script; cheap models run almost all of it.

**The whole system is one bet:** *Quality = model capability × task clarity × test strength × review discipline*. Spend effort on the last three, and the cheapest model does production-grade work, repeatably. The OLD ASPS proves that bet: 28 agents, 137 catalog assets, 60 Python modules, 1194+ tests, byte-strict moat, two-pass gate green, R-009 in code, F-026 Launch v0 shipped.

---

*End of analysis.*
