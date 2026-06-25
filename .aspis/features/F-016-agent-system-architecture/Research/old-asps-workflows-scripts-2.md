# OLD ASPS — Workflows, Scripts, Templates, Hooks & Determinism

> **Scope.** Deep read of the OLD ASPS factory repo at `local/ASPS/`. Focuses on the *mechanisms* that make the system reliable: workflows (procedures), scripts (deterministic CLIs), templates (output shapes), hooks (enforcement), config (declarative rules), and how they collaborate with agents.
>
> **Complements** `old-asps-deep-analysis-1.md` (which covers the roster, decisions, and architecture). This file is the **mechanical substrate** — the deterministic layer the agents sit on top of.
>
> **Sources read.** `local/ASPS/.asps/workflows/*` (5 files), `local/ASPS/.asps/context/*` (16 files: PATTERNS, DELEGATION_MAP, ASPS_OPERATING_MODEL, TRACEHOOKS, ENGINE_WORK_POLICY, BOOTSTRAP_CONTRACT, ASPS_FOUNDATIONS, ASPS_IDENTITY, ASPS_OVERVIEW, ROSTER_SPEC, REFACTOR-PLAN, etc.), `local/ASPS/.asps/traces/TRACE_SCHEMA.md`, `local/ASPS/.asps/gates.json`, `local/ASPS/.asps/gates.schema.md`, `local/ASPS/scripts/manifest.yaml` + every script in `local/ASPS/scripts/*` (read all the .ps1 and .sh), `local/ASPS/templates/**/*` (all 10 template categories, 25 templates), `local/ASPS/hooks/*` (commit-msg, pre-commit, post-commit, trace-pipe — both POSIX and pwsh), `local/ASPS/policy/*` (4 rule data files), `local/ASPS/agents/**/*.md` (28+ agents, with Operating Contracts), `local/ASPS/commands/*.md` (12 commands), `local/ASPS/planning-kit/phases/*` (P0–P9), `local/ASPS/src/asps/*.py` (61 Python modules), and `local/ASPS/.opencode/plugins/asps-trace.ts`.

---

## 0 · The one-paragraph mental model

The OLD ASPS turns soft agent decisions into **deterministic data + scripts + hooks**, layered so cheap models can do production work. The mechanism is:

1. **Workflows** (markdown) — the procedures agents follow.
2. **Templates** (markdown) — the shape of every output artifact (SPEC, PLAN, TASKS, REPORT, etc.).
3. **Scripts** (PowerShell + bash + Python) — the deterministic CLIs that replace agent decisions (detect, status, gates, trace, validate, bootstrap, clean, restore).
4. **Hooks** (commit-msg, pre-commit, post-commit, trace-pipe) — the **enforcement** that fires on every git event and every tool call.
5. **Policy data files** (`policy/*.txt`) — the **single source** of rules read by both shell hooks and Python engine (parity-tested).
6. **Config** (`gates.json`, `gates.yaml`, `gates.schema.md`, `feature.yaml`) — the project-defined gate list and the per-feature scope.

The cardinal rule from `ASPS_OPERATING_MODEL.md` §0: **wrap every nondeterministic LLM step in a workflow/skill/hook/script** so it is controlled and repeatable. The cardinal rule from `ASPS_FOUNDATIONS.md` Thesis 3: **machine-checked invariants hold; prose-asserted ones rot** — every "X must match Y" claim becomes a test, a hook, a script, or generated code.

---

## 1 · Workflows (`.asps/workflows/`)

Five workflow files. Each is a **procedure** the named agent executes, with rules + checkable steps + trace events.

| # | File | Owner agent | Purpose |
|---|------|-------------|---------|
| 1 | `PLANNING_WORKFLOW.md` | `asps-planning-lead` | P0→P9 pipeline (intake → spec → clarify → research → tech plan → arch → feature map → per-feature plan → tasks → plan-critic → human approval) |
| 2 | `BUILD_WORKFLOW.md` | `asps-build-lead` | Take one task packet `[ ]` → `[x]` (read packet → stack builder → implement → product gate → fix-lead handoff) |
| 3 | `REVIEW_TEST_LOOP.md` | `asps-tester` + `asps-reviewer` | After gate passes: tester runs pytest + classifies failures (flaky/regression/coverage gap) → reviewer checks R-001/R-002/R-005 → reviewer is the only committer |
| 4 | `NEW_FEATURE_WORKFLOW.md` | `project-lead` | Pre-flight before starting a new feature: clean tree, close current feature, create new branch FIRST, then planning files, then commit |
| 5 | `BOOTSTRAP_WORKFLOW.md` | `asps-system-lead` (via `asps-bootstrap` skill) | Two modes: SEED (create `.asps/`, install hooks, init git) / RESUME (re-validate existing). Calls `bootstrap.ps1`. |

### How the workflows enforce determinism

- **Strict output shapes** — every workflow names the exact file paths, trace event names, and report templates to emit. Example: `BUILD_WORKFLOW.md` Rule 1 specifies the exact task-line format `- [ ] T001 [P] [US1] Short description + file path(s)`.
- **Trace-event vocabulary is fixed.** `delegation`, `edit`, `gate_result`, `phase_start`, `phase_end`, `scope_decision`, `git_commit`, `fail`, `handoff` (12 types per `TRACE_SCHEMA.md`). Workflows say "emit `delegation`" not "log a delegation event."
- **No silent scope expansion** — `BUILD_WORKFLOW.md` Rule 9 forbids the builder from fixing adjacent problems it notices. The note goes in a trace event, not in the diff.
- **Status discipline is encoded in ASCII** — `[ ]` (not started), `[~]` (in-progress), `[x]` (build-pass), `[!]` (blocked/gate-fail). Workflows specify the exact transitions.
- **One writer (R-004)** — `REVIEW_TEST_LOOP.md` Rule 4 makes the **reviewer the only committer**; the builder never commits. Workflows spell this out rule by rule.

---

## 2 · Scripts (the deterministic CLI layer)

`scripts/manifest.yaml` is the canonical index. Every script has a PowerShell + bash mirror (`.ps1` and `.sh`) so the same behavior runs on Windows and Linux. They are organized in 9 sub-folders.

### 2.1 Full script inventory (from `scripts/manifest.yaml` + directory listing)

| Category | Scripts | What it does | Used by |
|----------|---------|--------------|---------|
| **common/** | `common.ps1`, `common.sh` | Shared library: `Get-AspsRoot`, `Write-TraceEvent`, `Get-ActiveFeature`, `Get-GitInfo`, `Test-PreReqs` (walks up dirs to find `.asps/`) | All other scripts + hooks (dot-sourced) |
| **bootstrap/** | `bootstrap.ps1`, `bootstrap.sh` | **Thin shim** — locates Python, calls `python -m asps bootstrap --no-shell`. For `--no-shell` to break the shim→shell→shim loop | `asps-bootstrap` skill, `asps-system-lead` |
| **gates/** | `gates.ps1`, `gates.sh` | Runs the gate suite from `.asps/gates.json` (or hardcoded fallback) → JSON pass/fail report + `gate_result` trace event | `gate-runner` agent, pre-commit hook |
| **tracing/** | `trace.ps1`, `trace.sh` | Append a JSONL event to `.asps/traces/raw/<run_id>.jsonl`. **Detached by default** (background process) so it never slows the caller | Agents, skills, hooks |
| **status/** | `status.ps1`, `status.sh`, `session-start.ps1`, `session-start.sh` | Read state files → JSON health report: active feature, phase, branch, commit, trace count, src/test file counts, prereqs | Dashboard, lead agents, CI |
| **validate/** | `validate.ps1`, `validate.sh` | Structural check of `.opencode/` (or `.claude/`) assets: frontmatter completeness, duplicate names, cross-refs. JSON report; exit 0/1 | Gates, export, CI |
| **cleanup/** | `clean-junk.ps1`, `clean-junk.sh` | Find zero-byte files at repo root (shell-redirect ghosts) → list or remove. Filter against `policy/junk-file-keep.txt` | Maintenance, CI, pre-commit |
| **detect/** | `detect.ps1`, `detect.sh` | Detect OS (Windows/Linux/macOS/WSL2), available shells, tools (git/python/node/cargo/docker), project kind (nextjs/python/rust/go), package manager, git status, **is_asps_project** flag | Bootstrapping, agents, CI |
| **files/** | `files.ps1`, `files.sh`, `restore-template.ps1`, `restore-template.sh`, `refresh-golden.py` | (a) Classify file states: `ok`/`changed`/`empty`/`missing`/`gitkeep`/`ignored`/`forbidden` per path; (b) extract paths from TASKS.md backticks; (c) write status markers `[ok]` back into TASKS; (d) restore a canonical template from `templates/`; (e) refresh the catalog golden manifest (`tests/golden/catalog_assets.txt`) | Agents pre-edit, scope guard, CI, L3 fallback recovery |
| **install-hooks/** | `install-hooks.ps1`, `install-hooks.sh` | Copy `hooks/{pre-commit,commit-msg,post-commit,pre-push}` into `.git/hooks/` **idempotently** (compares SHA-256, prints `skip`/`update`/`install` per hook) | Project setup, CI bootstrap |
| **run-feature/** | `run-feature.ps1`, `run-feature.sh` | Unattended runner: process a feature's `build/T-*.md` packets **serially** — for each: invoke opencode `asps-build` → run gates → invoke `asps-fix` up to N times → on persistent fail append `REVIEW_NEEDED` to `dashboard/review-queue.jsonl` | CI / batch execution |
| **export/** (root) | `export-asps-bs.ps1`, `export-asps-bs.sh` | Prove export to a fresh external project: dry-run → apply → validate → scorecard | Export workflow, CI |

### 2.2 How scripts make the system deterministic

This is the heart of the design. Every script replaces an LLM decision with a deterministic check.

| Script | What LLM decision it replaces | Why it's deterministic |
|--------|-------------------------------|------------------------|
| `detect` | "What stack is this project?" | File globs: `package.json` → node, `pyproject.toml`/`setup.py` → python, `Cargo.toml` → rust, `go.mod` → go. Examines `package.json.dependencies` to pick `nextjs` vs `react`. |
| `status` | "Is this project healthy?" | Reads 3 files (`active_feature.json`, `git` state, `traces/raw/`) and counts; outputs structured JSON. |
| `gates` | "Did the build pass?" | Runs each step from `.asps/gates.json` via subprocess; checks exit code; emits `gate_result` event with summary. |
| `validate` | "Are the runtime assets valid?" | Parses YAML frontmatter, checks required fields (`description`/`model`/`mode` for agents, `name`+`description` for skills), checks duplicate names. |
| `files` (classify) | "Is this path safe to edit / does it exist / is it ignored?" | Walks filesystem + `git check-ignore` + `git diff` to assign one of 7 statuses. |
| `files` (from-tasks) | "Do all paths in this task packet exist?" | Regex-extracts backtick-wrapped paths from TASKS.md, classifies each. |
| `clean-junk` | "Are there ghost files at the root?" | `Get-ChildItem -File` filtered to zero-byte, minus the keep-list from `policy/junk-file-keep.txt`. |
| `trace` | "Record an event happened" | Appends a JSONL line with run_id, ts, event name, runtime, data; detached process so it's a side-effect. |
| `install-hooks` | "Are the git hooks present and current?" | SHA-256 compare + idempotent copy with `skip`/`update`/`install` reporting. |
| `run-feature` | "Execute the whole feature unattended" | Iterates packets, runs build → gate → fix-ladder up to N attempts, writes `REVIEW_NEEDED` on failure. |
| `bootstrap` (shim) | "Run bootstrap" | Forces `--no-shell` to prevent shim→shell→shim loop. Locates Python via `python3`/`python`/`py` candidates. |
| `refresh-golden.py` | "Has the catalog drifted?" | Emits sorted `<kind>:<path>` identifiers; `--check` exits 1 on any add/remove. Replaces fragile count-snapshot asserts. |

### 2.3 Key design pattern: shell == python (parity-tested)

The most important determinism property in OLD ASPS. From `REFACTOR-PLAN.md` §0.1 (Phase 0) and `policy/*.txt` headers:

> Every rule pattern in `policy/secret-patterns.txt`, `policy/junk-message-patterns.txt`, `policy/junk-file-keep.txt` is read by BOTH the pure-shell git hooks AND the Python `asps.policy` engine. **Never hard-code a rule pattern anywhere else.** A parity test (`tests/test_policy_shell_parity.py`) proves the shell verdict equals the Python verdict.

Concretely:
- `hooks/pre-commit` is a **pure bash** script — no Python call for the policy checks. It walks `policy/secret-patterns.txt` and runs `grep -E -f`. It walks `policy/junk-file-keep.txt` and runs the keep-list loop. It parses `feature.yaml` for `scope.allowed`/`scope.forbidden` and bash-glob-checks each staged file.
- `hooks/commit-msg` is also pure bash, parses `policy/junk-message-patterns.txt` (which has `#:` metadata lines for `id | reason | flags | scope`) and refuses the commit if a pattern matches.
- The Python engine in `src/asps/policy.py` reads the **same files** through `asps.policy.load_patterns("secret")` / `load_patterns("junk-message")` / `load_keep_list`.
- The single `tests/test_policy_shell_parity.py` test (per the hooks file headers) proves `hook verdict == policy.py verdict` on a fixture corpus.

This is the **rules-as-data** pattern — the data files in `policy/` are the *one* source. Shell and Python are two views of the same data.

### 2.4 The fallback ladder (L0 → L3)

From `templates/context/FALLBACK_LADDER.md` — when something is broken, climb **down** this ladder:

| Level | Condition | Act |
|-------|-----------|-----|
| L0 | `asps` on PATH | `asps <verb>` |
| L1 | `asps` missing but Python + repo | `PYTHONPATH=src python -m asps <verb>` |
| L2 | no Python — only `scripts/` | `bash scripts/<area>/<name>.sh` |
| L3 | an asset/template missing | `bash scripts/files/restore-template.sh <relpath> <dest>` |

Each rung emits a `recovery` trace event. **Determinism is preserved by the ladder — a broken CLI does not break the workflow, it just degrades to the next rung.**

---

## 3 · Templates (the output-shape contract)

25 templates across 10 categories. **Every output in OLD ASPS has a template**, so the cheapest model is correct when the output is template-shaped + validated (from `REFACTOR-PLAN.md` §3.8: "Template-as-determinism + conformance").

### 3.1 Template inventory

| Category | Files | Purpose / when used |
|----------|-------|---------------------|
| **context/** | `FALLBACK_LADDER.md` | The L0→L3 ladder every agent climbs when a tool is missing |
| **feature/** | `feature.yaml.template` | Short pointer for a new feature: id, slug, status, phase, branch, risk, owner, commit_scope, summary, `scope.allowed`/`scope.forbidden` |
| | `SPEC.template.md` | The *what/why*: Goal · Problem · Scope · Out of scope · Behavior/acceptance scenarios (Given/When/Then per slice) · FR-###/SC-### · Assumptions · Clarifications · Open questions |
| | `PLAN.template.md` | The *how*: Approach · Constitution/Gate Check · Technical context · Steps with files+gate per step · Verification · Risks & Rollback · Commit |
| | `TASKS.template.md` | Strict task format: `- [ ] T-XXX [P] [US?] Description (exact file path)`. Phases: Setup · Foundational · User Story 1/2/... · Polish. Includes `When to split into a build unit` guidance. |
| | `ACCEPTANCE.template.md` | Checkable conditions derived from FR-###/SC-###. Sign-off section for reviewer. |
| | `CHECKLIST.template.md` | **Unit tests for English** — validates SPEC/PLAN quality *before* build (13 items, CHK001–CHK013, in 3 groups: Content Quality, Requirement Completeness, Feature Readiness). **Gate: Block build until all items pass.** |
| **task/** | `BUILD_UNIT.template.md` | Self-contained packet for a cheaper model: Context (gates file, feature, parent task, branch, background) · Objective · Allowed files (R-001) · Forbidden · Steps · Inputs/examples · Tests (red→green, R-005) · Invariants (property tests) · Done when · Verify (gates) · On failure · Report back (R-007 trace) |
| **planning/** | `constitution.template.md` | The project's governing principles. **Seeds with ASPS R-001…R-009 as binding core.** Adds X–XI project-specific principles. Requires version/ratification dates. |
| | `quality-checklist.template.md` | The 13-item CHK001–CHK013 checklist (alias of `feature/CHECKLIST.template.md`) |
| **trace/** | `TRACE.template.md` | Append-only event log: per-row table (ts, actor, action, target, gate, result, commit) **or** JSONL form. R-007 required events: agent steps, tool actions, gate results, reviews, decisions, failures, hand-offs |
| **lesson/** | `LESSON.template.md` | R-006 Teach: when a stronger model catches a weaker one. Fields: ID, Date, Origin, Caught by, Missed by, What happened, Root cause, Correct approach, Durable improvement (→ IMPROVEMENT_PROPOSAL if needed) |
| **improvement/** | `IMPROVEMENT_PROPOSAL.template.md` | R-009 Human gate. Fields: ID, Date, Proposed by, Source, Status, Problem, Proposed change, Affected files, Impact and risk, **Human decision required** |
| **report/** (11 templates) | `BUILD_DONE_STATUS.template.md` | Builder → lead → committer hand-off. Scope check, what changed, tests (R-005), gate result, trace events, hand-off |
| | `REVIEW_REPORT.template.md` | Reviewer → committer/fix-lead. Verdict (Approved / Changes Requested / Human gate), scope reviewed, gate results, findings table (CRITICAL/HIGH/MEDIUM/LOW), hand-off |
| | `COMMIT_REPORT.template.md` | Committer's only report. Branch fit, build status green, test status green, review clear, scope clean → commit. **Bounce-back if out-of-scope.** |
| | `COMMIT_REVIEW.template.md` | Pre-commit gate (commit-reviewer) — APPROVED/CHANGES_REQUESTED/BLOCKED. Validates task identity, branch fit, build/test/review status, scope. |
| | `FIX_REPORT.template.md` | asps-fix-lead minimal-diff loop. 3-attempt cap. Failure summary → root cause → fix → re-run gate table → scope check → escalate-or-hand-off |
| | `PLANNING_REPORT.template.md` | asps-planning-lead P0–P9 audit. Phases table (P0–P9) with status/sub-agent/artifact. Artifacts produced (SPEC, PLAN, TASKS, ACCEPTANCE, CLARIFY_REPORT). Plan-critic verdict. **P9 approval (R-009) block.** |
| | `CLARIFY_REPORT.template.md` | clarify sub-agent output. 10-category ambiguity scan. Max-5 prioritized questions one-at-a-time. Unresolved → Deferred |
| | `RESEARCH_NOTE.template.md` | lead-researcher output. Sources consulted, key findings, recommendations, **Harvest path status (D-008)**: Recorded → Source/license checked → Adapted → Proved → Reviewed → Promoted |
| | `TEST_REPORT.template.md` | tester / test-author / gate-runner output. Gates table (lint/types/tests/...). New/changed tests (R-005). Failures → routed to fix-lead. |
| | `AUTHOR_REPORT.template.md` | Runtime-asset author (opencode/claude/skill/command). Contract check, validation (`validate-runtime`), scope check (one asset per task). |
| | `SCOPE_CHECK.template.md` | The git stable-base + scope guard run BEFORE touching files. Stable base commit, working-tree clean at allowed paths. Verdict allow/deny. Emits `scope_decision` trace event. |
| **project/** | `github-gates.yml` | GitHub Actions workflow: install `asps`, run `asps trace-gate --ci` on every push/PR. |

### 3.2 How templates ensure consistent output

1. **Shape enforcement.** Every report template starts with `# <Report Type>: F-XXX [— Title]` and a copy-to instruction `.asps/features/F-XXX-slug/<dir>/<file>.md`. The cheapest model just fills the sections.
2. **Checkbox discipline.** Most templates end with a long `- [ ]` checklist that the agent must tick off. R-007 trace events, R-001 scope, R-005 tests-as-spec, R-002 gates — all explicit.
3. **Severity vocabularies are fixed.** Reviewer template: CRITICAL/HIGH/MEDIUM/LOW. Commit-reviewer: APPROVED/CHANGES_REQUESTED/BLOCKED. Fix: fixed/blocked/partial. **Standardized statuses mean the same words always mean the same things.**
4. **Trace event names are fixed.** Templates call out exact event names: `gate_result`, `phase_start`, `phase_end`, `delegation`, `edit`, `fail`, `scope_decision`, `git_commit`, `handoff`. The names match `TRACE_SCHEMA.md` exactly.
5. **Quality gate as a template.** `feature/CHECKLIST.template.md` is "unit tests for English" — a checklist that validates the **quality of the SPEC/PLAN prose** before any code is written. **The 13-item checklist is a pre-build gate.**
6. **Spec is the contract, plan is the recipe.** SPEC.md template uses Given/When/Then per slice and explicit FR-###/SC-### identifiers. PLAN.md template requires a "Steps with files and gates" table. TASK packets name exact file paths. **At each level, the artifact is self-contained enough for a cheaper model to execute.**

### 3.3 The harvest attribution

Every template footer records provenance (e.g. "Harvested from Spec Kit (MIT) — adapted for ASPS ..."). Templates are open-source where compatible; the harvest path (D-008) is record → license → adapt → prove → review → promote.

---

## 4 · Hooks (the enforcement layer)

5 hook files at the root, plus mirror in `hooks/` for the exportable project layout. README documents the contract.

### 4.1 Hook inventory

| File | What fires it | What it does | Modes of failure |
|------|---------------|--------------|------------------|
| **commit-msg** (bash) + **commit-msg.ps1** | Every `git commit` (after editor saves message) | 1. Refuse empty/whitespace messages. 2. Match `policy/junk-message-patterns.txt` (4 patterns: `plan(F-XXX)`, angle-bracket placeholders, "define <feature" prefix, single unhelpful words like "wip|fix|tmp"). 3. Refuse test-file deletions unless message contains `[test-removal-approved]` (R-005). Bypass: `ASPS_COMMIT_OK=1` env. | **Blocks** the commit (exit 1). Pure shell — works without Python. |
| **pre-commit** (bash) | Every `git commit` (before) | 1. **Scope guard** — reads `.asps/current/active_feature.json` + `feature.yaml scope.allowed/forbidden`; refuses if staged file matches forbidden or (if allowed list non-empty) doesn't match allowed. 2. **Secret guard** — `grep -E -f policy/secret-patterns.txt` against staged diff. 3. **Junk-file guard** — refuses files whose name starts with `=`, `*`, `-` or ends with `:`, `,`; refuses bare extensionless root words not in `policy/junk-file-keep.txt`. 4. **Gate runner** — `bash scripts/gates/gates.sh`; blocks commit on gate fail. 5. **Runtime validation** — `python -m asps validate-runtime --path .opencode` if `.opencode/` or `.claude/` files are staged. | **Blocks** the commit on any check fail. |
| **post-commit** (bash) + **post-commit.ps1** | Every successful commit | 1. Collects commit metadata: hash, branch, author, message, files_changed. 2. Appends `git.commit` event to `.asps/traces/raw/<date>.jsonl`. 3. Refreshes the `GENERATED-COMMITS START..END` block in `.asps/context/RECENT_CHANGES.md` with `git log --oneline -15`. | **Never blocks** — `set +e`, error → stderr only, `exit 0`. |
| **trace-pipe.sh** + **trace-pipe.ps1** | Every tool call (OpenCode `tool.execute.before`/`.after`, Claude `PreToolUse`/`PostToolUse`/`SessionStart`/`Stop`/`SubagentStop`) | Receives a JSON event (from `$1` for OpenCode, from stdin for Claude); enriches with timestamp, `asps_runtime`, `asps_hook`; **resolves run_id** from `ASPS_RUN_ID` env → event `run_id` → event `session_id` → `firehose` fallback; truncates write/edit `content` if >2KB; appends one JSONL line to `.asps/traces/raw/<run_id>.jsonl`. | **Never blocks** — `set +e`, all errors to stderr, `exit 0`. |
| **pre-push** (called by install-hooks but not yet implemented in the README list) | Every `git push` | Reserved; install-hooks copies it if present. | Per install-hooks behavior. |

### 4.2 How hooks make rules automatic

1. **No LLM in the loop.** Pre-commit is pure shell. It does not "ask" the agent — it reads policy files and exits 0/1. **A rule enforced by a hook cannot be skipped by an LLM.**
2. **Rules-as-data.** `policy/*.txt` files are the single source. Editing the file changes the rule for both shell hooks and Python engine. The parity test guarantees no drift.
3. **R-005 enforcement.** Both the pre-commit secret guard (via `policy/secret-patterns.txt`) and the commit-msg test-removal guard (with `[test-removal-approved]` escape hatch) are R-001/R-005 automatic.
4. **R-002 enforcement.** Pre-commit runs the gate suite. Commit cannot land on red.
5. **R-007 enforcement.** Post-commit and trace-pipe *fire automatically* on every commit and every tool call. **No silent runs** is enforced by the hook, not by asking the agent to remember.
6. **Two hook classes (D-3, REFACTOR-PLAN §3.10)**:
   - **Enforcement hooks** (commit-msg, pre-commit) — synchronous, may block.
   - **Trace hooks** (post-commit, trace-pipe) — fire-and-forget, never block, always exit 0.
7. **Self-dogfooding.** Per `REFACTOR-PLAN.md` §3.10 and `gates.json`: the engine enforces its own rules on itself.

### 4.3 Hook design notes from `hooks/README.md`

- **Shim vs Python** — the trace-pipe shims are **zero-dependency**; logic stays in Python (`python -m asps trace-hook` / `src/asps/trace_hook.py`). The shim only forwards.
- **Detached or TTY-safe** — the pwsh shim only reads stdin if `[Console]::IsInputRedirected` (else a TTY read would block forever).
- **Event filtering** — what we **intentionally don't hook**: OpenCode session lifecycle (runtime's job), Claude `UserPromptSubmit`/`Notification`/`PreCompact`/`PostCompact` (noise), per-tool matchers (the Layer A → B keep/drop table filters at derivation time).
- **Registration** — OpenCode plugin auto-loads from `.opencode/plugins/`. Claude hooks live in `.claude/settings.json` (project-shared).
- **Cross-platform** — bash for OpenCode path; pwsh for Windows; both kept in sync; runtime contract identical.

---

## 5 · Policy + Config (the data layer)

### 5.1 Policy data files (`policy/`)

Four files. Each is **POSIX-ERE plain text**, comment-stripped, read by both bash and Python:

| File | Lines (rules) | What it catches | Read by |
|------|---------------|-----------------|---------|
| `secret-patterns.txt` | 10 patterns (PEM, OpenAI, GitHub, Slack, AWS, DB conn, JWT, generic `key=value`, env-inline) | Possible secrets in staged diffs | pre-commit bash + `asps.policy` Python + `asps.secret_scan` |
| `junk-message-patterns.txt` | 4 patterns (placeholder, angle-bracket, `define <feature`, single unhelpful word) | Junk/placeholder commit messages | commit-msg bash + `asps.commit_guard` |
| `junk-file-keep.txt` | 7 names (LICENSE, Makefile, Dockerfile, Justfile, Procfile, Vagrantfile, Brewfile) | Extensionless root filenames that are legitimate (extends `asps.junk.DEFAULT_KEEP`) | pre-commit bash + `asps.policy.check_junk_files` |
| `r009-protected-paths.txt` | 5 globs (`rules/**`, `profiles/defaults.yaml`, `.claude/settings.json`, `opencode.json`, `.asps/improvements/**`) | R-009 protected surface — agent edits BLOCKED unless human approval in `IMPROVEMENTS.jsonl` | `asps.governance` Python |

**Pattern metadata format** (junk-message file):
```text
#: plan-placeholder | Commit message contains a placeholder pattern like "plan(F-001)". Write a meaningful commit message. | i | message
plan\(F-[0-9]+\)
```
- `id` | `reason` | `flags` (`i` = case-insensitive) | `scope` (`subject`/`message`)

**Secret pattern format:**
```text
#: pem-private-key | private key block | 0 |
-----BEGIN (RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----
```
- `id` | `label` | `redaction-group` | `flags`

### 5.2 Gate config (`.asps/gates.*`)

The project-defined product gate. **`.asps/gates.json`** is the JSON form (committed in OLD ASPS), **`.asps/gates.yaml`** is the YAML form (richer), **`.asps/gates.schema.md`** is the contract.

The committed `.asps/gates.json` for OLD ASPS has 8 gates:
1. `ruff-format` — `python -m ruff format --check` (required)
2. `ruff-check` — `python -m ruff check src tests` (required)
3. `mypy` — `python -m mypy src/asps` (required)
4. `pytest` — `python -m pytest -q` (required)
5. `validate` — `pwsh -NoProfile -File .asps/scripts/validate/validate.ps1` (required)
6. `property` — `pytest tests -k "property or invariant" -q` (optional)
7. `mutation` — `python -m mutmut run --paths-to-mutate src/asps` (optional)
8. `benchmark` — `pytest tests/test_benchmark*.py -v --durations=5` (optional)

**YAML schema** (per `gates.schema.md`):
```yaml
version: 1            # required; integer >= 1
stack: python         # optional, informational
gates:                # required; ordered list
  - id: lint
    cmd: [ruff, check, src, tests]
```
Validation rules are strict-on-present: missing file → fall back to canonical Python gate (no error). Invalid YAML → `ValueError`. Duplicate ids → `ValueError`. Etc.

**Key design**: the gate list is **data, not code**. `gates.ps1` reads JSON, falls back to hardcoded, runs each step as a subprocess, checks exit code, emits a single `gate_result` trace event. The agent never hardcodes `ruff`/`mypy`/`pytest`; it reads the gate file.

### 5.3 Runtime config

- **`.asps/runtime.lock.json` / `.runtime.lock.claude.json` / `.runtime.lock.opencode.json`** — the locked state of the runtime assets at a moment in time. The exporter regenerates this and the byte-parity guard proves catalog ↔ live parity.
- **`.opencode/` / `.claude/`** — the **generated** runtime assets; replaced by the export transform; never edited in place (from `ASPS_FOUNDATIONS.md` Engineering principles: "never edit catalog-managed live files in place").

### 5.4 Per-feature config (`feature.yaml`)

The template is **the contract for a feature**:
- `id`, `slug`, `title`, `status`, `phase`, `created`, `branch`, `risk`, `owner`, `commit_scope`, `summary`
- `scope.allowed: [path/or/glob/**]` — R-001 allow-list (the pre-commit hook reads this)
- `scope.forbidden: [paths]` — R-001 deny-list (forbidden wins, then must match allowed)

This is the **only file the pre-commit hook parses** to enforce scope. One feature = one feature.yaml. The active feature is tracked in `.asps/current/active_feature.json` as a short pointer (per D-012).

---

## 6 · Agents & skills — how they connect to workflows/scripts/hooks

### 6.1 The delegation chain (from `DELEGATION_MAP.md` + `agents/**/*.md`)

```
L1  project-lead (primary) — the only agent the human talks to
    ├─ L2 asps-system-lead (primary) ───┬─ governance, committer, asps-opencode-author, asps-claude-author
    │                                  └─ (owns the `asps-bootstrap` skill)
    ├─ L2 asps-planning-lead (primary) ── clarify, task-decomposer, idea-capture
    ├─ L2 asps-build-lead (primary) ───── python-builder, api-builder
    ├─ L2 asps-reviewer (primary) ──────── security-reviewer, commit-reviewer  (READ-ONLY, R-004)
    ├─ L2 asps-fix-lead ────────────────── bug-triager, gate-fixer, project-explorer
    ├─ L2 lead-researcher ─────────────── docs-fetcher, codebase-explorer, web-researcher
    └─ L2 asps-tester ──────────────────── test-author

shared helpers: project-explorer, context-feeder, context-summarizer
```

### 6.2 Per-agent contract (the operating contract pattern)

Every agent file follows the same skeleton (per `ASPS_OPERATING_MODEL.md` §2 and `ROSTER_SPEC.md` per-agent contract):

1. **Role** — one sentence.
2. **Operating Contract** (for some agents):
   - **Role** · **Write scope** · **Forbidden** · **Delegates to** · **Required skills** · **Escalation**
3. **Abstraction (runtime-agnostic)**:
   - **Mode intent**: `primary` (L1/L2 entrypoint) or `subagent`
   - **Model intent**: `standard` / `premium` / `cheap`
   - **Delegates to**: explicit list
   - **Skills**: explicit list
   - **Permission intent**: read/list/search `allow`/`ask`/`deny`; edit, bash, webfetch, etc.
4. **How it works** — 3–5 numbered steps.
5. **Responsibilities** — bullet list.
6. **Delegation Rules** — when to delegate vs when to do.
7. **Read-first files** — exactly which files the agent reads at the start of a task.
8. **Forbidden work** — explicit list.
9. **Escalation** — when to stop and route to human or another agent.

The **Read-first files** section is the bridge to the workflows/scripts/templates:
- `asps-build-lead.md`: read `.asps/workflows/BUILD_WORKFLOW.md`, `.asps/gates.yaml`, the active feature's `feature.yaml`/`PLAN.md`/`TASKS.md`/`pyproject.toml`.
- `asps-planning-lead.md`: read `.asps/workflows/PLANNING_WORKFLOW.md`, `planning-kit/`, `.asps/templates/feature/*` and `.asps/templates/task/*`.
- `asps-fix-lead.md`: read `REVIEW_TEST_LOOP.md`, gates.yaml, the failure summary.
- `asps-system-lead.md`: read the OpenCode/Claude official reference docs (`OPENCODE_OFFICIAL_REFERENCES.md`, `CLAUDE_CODE_OFFICIAL_REFERENCES.md`).
- `project-lead.md`: read `AGENTS.md` (already loaded), `asps-lead-operating-protocol`, `asps-context-navigation`.

### 6.3 Skills — the procedures agents load

Skills are in `skills/` (in the catalog) and `.opencode/skills/` and `.claude/skills/` (in the runtime). The `CATALOG_INVENTORY.md` lists 33 skills across: `build/`, `core/`, `planning/`, `research/`, `review/`, `system/`, `testing/`. Key skills:

| Skill | What it does |
|-------|--------------|
| `asps-lead-operating-protocol` | The opening sequence every lead runs |
| `asps-context-navigation` | How much context to load (Level 1 first, then stop) |
| `asps-feature-workflow` | The new-feature / build / review-test / close flow |
| `asps-trace-discipline` | R-007: every important step emits a trace event |
| `asps-trace` (plugin) | The OpenCode plugin that pipes every tool call to the trace store |
| `scope-control` | R-001 enforcement before any edit |
| `gates-first` | R-002: run gates before declaring done |
| `gate-running` | The procedure to run the gate suite |
| `spec-to-plan` | The P0–P9 procedure |
| `plan-critic` | The P8 review pass |
| `commit-discipline` | The reviewer-is-the-only-committer contract |
| `done-reporting` | The build-done-status hand-off |
| `fallback-recovery` | The L0→L3 ladder |
| `clarify` | 10-category ambiguity scan + max-5 questions |
| `coverage-analysis` | Test coverage report |
| `red-green` | R-005: red-first acceptance tests |
| `minimal-diff` | R-001 fix-lead's minimal-diff contract |
| `codebase-mapping`, `dependency-audit`, `source-ranking`, `docs-harvest` | Research sub-skills |
| `architecture-review`, `review-checklist`, `scope-audit`, `security-review` | Review sub-skills |

**Skills are the bridge between an agent and a deterministic script/template.** E.g. the `gates-first` skill says "run `pwsh scripts/gates/gates.ps1`" — the skill names the exact command.

### 6.4 The 6 orchestration patterns (from `PATTERNS.md`)

| # | Pattern | When | Lead |
|---|---------|------|------|
| 1 | **Orchestrator-Worker** | Most workflows — build, review, research, authoring | `project-lead`, `asps-build-lead`, `asps-system-lead` |
| 2 | **Sequential Pipeline** | P0→P9 planning, feature lifecycle | `asps-planning-lead` |
| 3 | **Fan-Out / Fan-In** | Multi-phase review, competing proposals, parallel research | `asps-reviewer`, `lead-researcher` |
| 4 | **Multi-Agent Debate** | Architecture decisions, risk assessments, spec ambiguity | `asps-planning-lead` (template created; pending use) |
| 5 | **Dynamic Handoff** | Cross-domain routing, gate failures, fix loops | `project-lead`, `asps-fix-lead`, `asps-build-lead` |
| 6 | **Adaptive Planning** | Complex features with unknown design space | `asps-planning-lead` |

### 6.5 The trace loop (R-007 enforcement)

`TRACEHOOKS.md` documents the OpenCode sub-agent stopping mitigations:

1. **Steps limits on all lead agents** (8 leads × 8–15 steps each).
2. **Explicit `permission.task` config** on all 49 agents — leaf workers have `task: "*": deny`.
3. **Continuation instructions** — every lead explicitly says "process sub-agent result and continue — do NOT stop."
4. **Trace plugin coverage** — `.opencode/plugins/asps-trace.ts` fires for `tool.execute.before` / `tool.execute.after` (every tool call) and pipes to the shim.

The trace is **two-layer** (per `TRACE_SCHEMA.md`):
- **Layer A (raw firehose)** — `.asps/traces/raw/<run_id>.jsonl`. One event per tool call (before + after). Captured by hooks/plugins. Append-only.
- **Layer B (curated story)** — `.asps/traces/runs/<run_id>.jsonl`. 12 event types: `session_start`, `phase_start`, `phase_end`, `delegation`, `tool_call`, `edit`, `gate_result`, `git_commit`, `scope_decision`, `fail`, `handoff`, `session_end`. Emitted by agents + scripts.

The **run_id join** is the keystone — every event is keyed by `run_id` (resolved from `ASPS_RUN_ID` env → event `run_id` → event `session_id` → `firehose`). **run_id-keyed** is the only path scheme. "Cost per feature/agent/model" is answerable from the joined store.

---

## 7 · How the pieces collaborate (the full picture)

A task flows like this (e.g. implementing F-XXX task T-001):

1. **User → project-lead**: classify intent → route to `asps-planning-lead` (P0–P9) → `asps-build-lead`.
2. **Planning lead** uses `PLANNING_WORKFLOW.md` (the P0→P9 procedure) + `templates/feature/SPEC.template.md` + `templates/feature/PLAN.template.md` + `templates/feature/TASKS.template.md` + `templates/feature/ACCEPTANCE.template.md` + `templates/feature/CHECKLIST.template.md` (the quality gate) + `templates/trace/TRACE.template.md` (the trace log) → produces build-ready task packets.
3. **Task-decomposer** compiles `TASKS.md` into `build/T-001.md` packets via `src/asps/task_compiler.py` + `templates/task/BUILD_UNIT.template.md`.
4. **Build-lead** uses `BUILD_WORKFLOW.md` (the per-task procedure):
   - reads packet from `TASKS.md` (status: `[ ]`)
   - delegates to `python-builder` / `api-builder` (orchestrator-worker pattern)
   - builder implements Allowed files only (R-001)
   - build-lead runs `pwsh scripts/gates/gates.ps1` → `gates.json` is read → each gate step runs → `gate_result` trace event emitted
   - on gate pass, status `[ ]` → `[x]`
   - on gate fail, hand off to `asps-fix-lead`
5. **Fix-lead** uses `FIX_REPORT.template.md` + `scope-control` skill: minimal diff to fix only the implicated files; re-run gate; up to 3 attempts; then escalate.
6. **Tester** uses `REVIEW_TEST_LOOP.md` + `TEST_REPORT.template.md`: run pytest, classify failures (flaky/regression/coverage gap), route back to builder on issues.
7. **Reviewer** uses `REVIEW_REPORT.template.md` + `review-checklist` skill: checks R-001 (scope), R-002 (gates), R-005 (tests-as-spec), correctness. **Reviewer is the only committer** — staging is `git add <explicit-paths>` (never `git add -A`).
8. **All along the way**:
   - **Pre-commit hook** enforces scope, secrets, junk names, and runs gates on every commit attempt.
   - **Commit-msg hook** enforces junk-message and test-removal rules.
   - **Post-commit hook** emits the `git.commit` trace event and refreshes the GENERATED-COMMITS block in `RECENT_CHANGES.md`.
   - **Trace-pipe hook** (via `.opencode/plugins/asps-trace.ts`) captures every tool call to the raw firehose.
   - **`scripts/status/status.ps1`** can be run at any time to report project health; `scripts/detect/detect.ps1` reports the environment.
9. **Lessons & improvements** — R-006: when a stronger model catches a weaker one, capture in `templates/lesson/LESSON.template.md`. If durable change needed, propose via `templates/improvement/IMPROVEMENT_PROPOSAL.template.md` (R-009: human gate required).

---

## 8 · The 9 Laws (R-001…R-009) — where each is enforced

| Rule | What it forbids | Where it is enforced (mechanism) |
|------|-----------------|----------------------------------|
| **R-001 Scope** | Touching files outside the task | `feature.yaml` → pre-commit hook (bash scope guard) + `scope-control` skill + build/fix/review `## Scope check` sections in every report template |
| **R-002 Gates first** | Declaring done before lint/format/types/tests/scope/secret checks | `gates.json` + `gates.ps1` script + pre-commit hook runs gates + `gates-first` skill + every PLAN template has a "Verification (gates — R-002)" section |
| **R-003 Stable prompts** | Casual mid-run rewrites of AGENTS.md / core skills / system rules | `policy/r009-protected-paths.txt` → governance agent blocks edits → `IMPROVEMENT_PROPOSAL.template.md` makes changes inspectable |
| **R-004 One writer** | Multiple active writers per branch; reviewers writing | `REVIEW_TEST_LOOP.md` Rule 4: "Reviewer is the only committer" + `committer` agent (leaf, no delegates) + the explicit `## Forbidden work: No direct commits/pushes` in builder agents |
| **R-005 Tests-as-spec** | Deleting/weakening a test to pass a gate | `commit-msg` hook refuses test-file deletions (unless `[test-removal-approved]`) + `BUILD_UNIT.template.md` "Tests (red→green, R-005)" section + `BUILD_DONE_STATUS.template.md` "Tests (R-005 — red → green)" section + reviewer check |
| **R-006 Teach** | Losing a lesson from a stronger-model-catches-weaker-model event | `LESSON.template.md` + `IMPROVEMENT_PROPOSAL.template.md` + `lessons.py` (Python) |
| **R-007 Trace** | Silent runs (no event for an important action) | `trace-pipe.sh/.ps1` + `asps-trace.ts` plugin (Layer A firehose) + `asps-trace-discipline` skill + every workflow names required events + `TRACE_SCHEMA.md` defines the 12 curated types |
| **R-008 Pin models** | Subagent inheriting an expensive primary model | Agent file's `Abstraction → Model intent` line; every agent declares its model |
| **R-009 Human gate** | Agent-initiated changes to architecture / rules / security / model-routing / self-improvement | `policy/r009-protected-paths.txt` → `asps.governance` Python + `governance.md` agent (the ONLY agent that can edit `rules/**` and `profiles/defaults.yaml` permission blocks, always R-009-gated) + `IMPROVEMENTS.jsonl` ledger |

---

## 9 · The deterministic-mechanism summary table

| Mechanism | Type | Replaces what agent decision? | How it stays correct |
|-----------|------|--------------------------------|----------------------|
| `gates.json` + `gates.ps1` | Data + script | "Did the build pass?" | JSON list, subprocess exit code, parity with YAML form |
| `policy/secret-patterns.txt` | Data | "Is this a secret?" | POSIX-ERE, read by bash + Python, parity test |
| `policy/junk-message-patterns.txt` | Data | "Is this a junk commit message?" | Same pattern as secrets |
| `policy/junk-file-keep.txt` | Data | "Is this extensionless root filename legitimate?" | Same pattern |
| `policy/r009-protected-paths.txt` | Data | "Is this an R-009 path?" | Globs, governance agent |
| `feature.yaml scope.allowed/forbidden` | Data | "Is this path in scope?" | Pre-commit bash scope guard |
| `feature.yaml TASKS.md` | Data | "What's the next task?" | Build workflow reads `[ ]` markers |
| `pre-commit` (pure bash) | Hook | "Does this commit violate any rule?" | Enforces R-001, R-002, secrets, junk names |
| `commit-msg` (pure bash) | Hook | "Is the commit message acceptable?" | Enforces R-005 + non-junk messages |
| `post-commit` (pure bash) | Hook | "Is the commit recorded?" | Always emits `git.commit` trace event + refreshes RECENT_CHANGES |
| `trace-pipe.{sh,ps1}` | Hook | "Is every tool call recorded?" | Always emits Layer A event; never blocks |
| `.opencode/plugins/asps-trace.ts` | Plugin | "Capture every OpenCode tool call" | Pipes to shim; detached |
| `scripts/detect/detect.ps1` | Script | "What kind of project is this?" | File globs + JSON parse |
| `scripts/status/status.ps1` | Script | "Is the project healthy?" | Reads 3 state files + counts |
| `scripts/validate/validate.ps1` | Script | "Are the runtime assets valid?" | YAML frontmatter parse + dup check |
| `scripts/files/files.ps1` (classify) | Script | "Is this path safe to edit?" | 7-status classification |
| `scripts/files/files.ps1` (from-tasks) | Script | "Do all paths in TASKS.md exist?" | Regex extract + classify each |
| `scripts/clean-junk/clean-junk.ps1` | Script | "Are there root ghost files?" | Zero-byte filter minus keep-list |
| `scripts/tracing/trace.ps1` | Script | "Record an event" | JSONL append; detached |
| `scripts/bootstrap/bootstrap.ps1` | Script | "Run bootstrap" | Forces `--no-shell` to break shim loop |
| `scripts/install-hooks/install-hooks.ps1` | Script | "Are hooks installed and current?" | SHA-256 compare + idempotent copy |
| `scripts/run-feature/run-feature.ps1` | Script | "Run the whole feature unattended" | Serial packet loop + gate + fix-ladder + REVIEW_NEEDED |
| `scripts/files/refresh-golden.py` | Script | "Has the catalog drifted?" | Sorted `<kind>:<path>` ids; exit 1 on diff |
| `scripts/files/restore-template.{sh,ps1}` | Script (L3 fallback) | "Restore a missing template" | Walks templates roots, copies to dest |
| Templates (25 files) | Output shape | "What does the deliverable look like?" | Strict headers, checkboxes, fixed severity/status vocabularies |
| Workflows (5 files) | Procedure | "What is the step-by-step?" | Numbered rules + exact file paths + exact trace event names |
| Skills (33 files) | Loaded procedure | "How do I do X?" | Skills name the exact script + template to use |
| `.asps/traces/TRACE_SCHEMA.md` | Schema | "What's a valid trace event?" | 12 types, common envelope, frozen contract |
| `.asps/gates.schema.md` | Schema | "What's a valid gates file?" | Strict-on-present rules; fall back on absent |
| `AGENTS.md` (12 lines) | Pointer | "Where do I start?" | Index, never re-statement |
| `governance` agent | Agent | "Who can edit R-009 paths?" | The ONLY writer of `rules/**` and `profiles/defaults.yaml` |
| `committer` agent | Agent | "Who can commit?" | The ONLY committer; everything else hands off |
| `project-lead` (L1) | Agent | "Who classifies my request?" | The ONLY agent the user talks to |

---

## 10 · What this means for the new ASPIS (key takeaways for F-016)

The OLD ASPS's reliability comes from **five mechanical pillars**:

1. **The script layer replaces LLM decisions with subprocesses.** Detect, status, gates, trace, validate, classify — all deterministic, all `pwsh` + `bash` + `python`. The cheapest model can use them correctly.
2. **Hooks make rules automatic.** Pre-commit enforces R-001, R-002, R-005, secrets, junk names. Commit-msg enforces non-junk. Post-commit + trace-pipe make R-007 (no silent runs) a property of the system, not a request to the agent. **A rule enforced by a hook cannot be skipped.**
3. **Policy is rules-as-data, parity-tested.** `policy/*.txt` are read by both shell and Python, with `tests/test_policy_shell_parity.py` proving identical verdicts. Editing the file edits the rule everywhere.
4. **Gates are data.** `.asps/gates.json` (or `.yaml`) is the project-defined product gate. Agents read it, never hardcode. New stack = new gates file = same agent procedure.
5. **Templates make output shape deterministic.** 25 templates for every output type (SPEC, PLAN, TASKS, REPORT, LESSON, IMPROVEMENT, TRACE). Strict headers, fixed status vocabularies (CRITICAL/HIGH/MEDIUM/LOW, APPROVED/CHANGES_REQUESTED/BLOCKED, ok/fail/blocked), required trace event names.

**The deterministic heart** is not the agent system — it's the combination of **policy data + hooks + scripts + templates + parity tests** that sits underneath. The agents are the **interface**, but the system is reliable because the substrate is mechanical.

**For the new ASPIS (F-016)**: every equivalent pillar should exist. The question is not "do we have workflows" but "are workflows backed by scripts and hooks that make the rules mechanical?"

---

## Appendix A · File-level index (the surface)

| Surface | Files | Location | Notes |
|---------|-------|----------|-------|
| Workflows | 5 | `local/ASPS/.asps/workflows/` | PLANNING, BUILD, REVIEW_TEST_LOOP, NEW_FEATURE, BOOTSTRAP |
| Context (durable) | 14 | `local/ASPS/.asps/context/` | ASPS_FOUNDATIONS, ASPS_IDENTITY, ASPS_OPERATING_MODEL, ROSTER_SPEC, PATTERNS, DELEGATION_MAP, REFACTOR-PLAN, BOOTSTRAP_CONTRACT, ENGINE_WORK_POLICY, TRACEHOOKS, ASPS_OVERVIEW, etc. |
| Trace schema | 3 | `local/ASPS/.asps/traces/` | TRACE_SCHEMA.md, OBSERVABILITY.md (449 lines), README.md |
| Gate config | 3 | `local/ASPS/.asps/` | gates.json, gates.yaml, gates.schema.md |
| Scripts | 23 (12 areas × 2 OSes) | `local/ASPS/scripts/` + `manifest.yaml` | common, bootstrap, gates, tracing, status, validate, cleanup, detect, files, install-hooks, run-feature, export |
| Hooks | 5 | `local/ASPS/hooks/` | pre-commit, commit-msg, post-commit, trace-pipe, README |
| Policy data | 4 | `local/ASPS/policy/` | secret-patterns, junk-message-patterns, junk-file-keep, r009-protected-paths |
| Templates | 25 | `local/ASPS/templates/` | 10 categories: context, feature (6), task, planning (2), trace, lesson, improvement, report (11), project, review |
| Agents (catalog) | 31 | `local/ASPS/agents/` | 9 subdirs: build (3), fix (3), general (3), planning (4), research (4), review (3), system (8), test (2) — plus AGENTS.template.md |
| Skills (catalog) | 33 | `local/ASPS/skills/` | 7 subdirs: build, core, planning, research, review, system, testing |
| Commands | 12 | `local/ASPS/commands/` | asps-analyze, asps-build, asps-checklist, asps-fix, asps-init, asps-map-repo, asps-plan, asps-pr-review, asps-proof, asps-review, asps-start, asps-status |
| Runtime (generated) | 1+ | `local/ASPS/.opencode/` | `plugins/asps-trace.ts` (the only plugin) |
| Planning kit | 12 | `local/ASPS/planning-kit/` | README + phases/ (P0–P9) + checklists/ |
| Rules | 1 | `local/ASPS/rules/SYSTEM_RULES.md` | The 9 laws |
| Python source | 61 | `local/ASPS/src/asps/*.py` | bootstrap, curate, doctor, exporter, governance, harvest, improve, initializer, junk, lead_activation, lessons, manifest, policy, profiles, promote, proof, regenerate, runtime_validator, scaffold, secret_scan, session_analyzer, status_report, task_compiler, trace, trace_events, trace_gate, trace_git, trace_hook, trace_ingest, trace_report, trace_store, transform, workflows, ... |

---

## Appendix B · The 4 theses (from `REFACTOR-PLAN.md` §0) — restated for the new ASPIS

1. **Determinism is the cost lever.** Shrink what the model must figure out; the cheapest model is correct when wrapped in a tight skill + script-tool + conformant template.
2. **Evidence is the currency.** Every phase emits evidence keyed to a git sha; later actors consume it instead of redoing work.
3. **Machine-checked invariants hold; prose-asserted ones rot.** Turn every "X must match Y" claim into generation or a test.
4. **Capture-now, derive-later.** Record the full useful trace fields now (append-only, cheap); the intelligence that reads them comes later.

**The OLD ASPS embodies all four.** The script layer + hooks are "determinism is the cost lever." The gate_result + git_commit trace events are "evidence is the currency." The parity test (`test_policy_shell_parity.py`) is "machine-checked invariants hold." The two-layer trace (raw firehose + curated story) is "capture-now, derive-later."

---

*End of file. Companion to `old-asps-deep-analysis-1.md` (the roster + architecture view).*
