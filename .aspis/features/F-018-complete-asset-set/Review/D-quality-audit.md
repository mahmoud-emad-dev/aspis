# D — Cross-Cutting Quality Audit (F-015 → F-018)

> **Reviewer:** Reviewer (independent, deep tier)
> **Date:** 2026-06-28
> **Scope:** All code added across F-015, F-016, F-017, F-018 — the four features that
> took ASPIS from "system hardening + public presentation" (F-014) to a "complete asset set,
> hardened runtime" (F-018). Verdict uses the acceptance-decision matrix against
> `.aspis/rules/system-rules.md` (R-001…R-010), the architecture constitution
> (`rules/architecture-constitution.md`), the constitution-checks
> (`config/policy/constitution-checks.yaml`), and the catalog
> `AGENT_BODY_STANDARD.md`.
>
> **Verdict at a glance:** **NEEDS WORK** — the build is structurally sound, the
> architecture is honoured, the gates are passing, but 3 systemic BLOCKED items
> prevent the feature from being labelled "shippable as-is." None of them require a
> refactor — each is a known bounded task the build report already documents.

---

## 1. Code inventory (counts by category)

### Catalog (the source of truth — D-005)

| Kind | Count | Where |
|---|---:|---|
| Agent bodies | **33** | `src/aspis/data/catalog/agents/*.md` |
| Skills | **67** | `src/aspis/data/catalog/skills/*/SKILL.md` |
| Templates | **18** | `src/aspis/data/catalog/templates/**/*.md` (planning 11, review 3, report 3, context 1) |
| Workflows (catalog) | **6** | `src/aspis/data/catalog/workflows/*.md` |
| Commands (catalog) | **5** | `src/aspis/data/catalog/commands/*.md` |
| Scripts (catalog) | **37** | `src/aspis/data/catalog/scripts/**/*.py` (hooks 13, planning 11, context 6, research 5, system 1, git 1) |
| Rules (catalog) | **3** | `src/aspis/data/catalog/rules/*.md` (system, project, architecture-constitution) |
| Config data | **6** | `src/aspis/data/catalog/config/**/*.yaml` (models, providers, model_catalog, capabilities, agent-capabilities, commit-convention, hooks, modes, README, constitution-checks) |
| Runtime hook sources | **1** | `src/aspis/data/catalog/runtime-hooks/opencode/session-notice.ts` (Claude settings.json is referenced but lives in deploy only) |

### Engine (the `aspis` Python package)

| Layer | Count | Top files by size |
|---|---:|---|
| `src/aspis/` (root) | **28** | `commands/governance.py` 642, `export.py` 550, `models.py` 205 |
| `src/aspis/commands/` | **22** | `commands/drift.py` 383, `commands/models.py` 310, `commands/validate_index.py` 264 |
| `src/aspis/operations/` | **3** | `operations/bootstrap.py` 490, `operations/init.py` 210 |
| `src/aspis/runtimes/` | **4** | `runtimes/base.py` 218, `runtimes/opencode.py` 197, `runtimes/claude.py` 112 |
| **Total engine Python** | **57** | — |

### Brain (the project's own `.aspis/`)

| Layer | Count |
|---|---:|
| Workflows | **6** (build, fix, plan, project-lead-operating-protocol, review, small-task) |
| Scripts (deployed) | **36** (parity-mirrored from the catalog sources, with 1-2 byte-drift + 2 missing — see §6) |
| Context docs | **5+** (ARCHITECTURE, DECISIONS, IDENTITY, ROADMAP, CORE_LOOP, AGENT_BODY_STANDARD, DYNAMIC_READINESS, CURRENT_STATE, RECENT_CHANGES) |
| Rules | **3** mirrored from the catalog (system, project, architecture-constitution) |
| Config | **2** policies, **2** reference, **1** modes.yaml (no `constitution-checks.yaml` mirrored — see §6 finding) |
| Features | **6** (F-013, F-014, F-015, F-016, F-017, F-018) |

### Tests

| Layer | Count |
|---|---:|
| `tests/` root | **60** |
| `tests/unit/test_scripts/` | **12** |
| **Total** | **72** |

### Total artifact footprint

~ **230+ product files** + 72 tests + 5 sub-skill folders × N = roughly **280 files**
authored or hardened across F-015..F-018. Of those, F-018 alone accounts for ~60
artifacts (12 scripts, 1 skill, 7 templates, 1 workflow, 21 new agents, 15 modified agents,
3 hook modules).

---

## 2. Clean / Lean / Minimal assessment

**Score: B+ (lean, with three structural caveats).** The system obeys the cost-of-change
test for its existing axis — adding a new agent is a one-file change (the body) plus
optional owning-lead frontmatter updates. Adding a new brain kind is zero core changes
(asset kinds are data, D-008). The catalogue is the single source (D-005) and the
adapters are capability-gated (D-002, D-008, D-015).

### Wins (cost-of-change honoured)

- **A new brain kind costs zero core files.** `assetkinds.py` defaults unknown kinds to
  a brain copy; only the three per-runtime kinds (`agents`, `commands`, `skills`) are
  registered as overrides. Confirmed at `src/aspis/assetkinds.py:58-71`.
- **A new runtime is one file.** `resources.runtime_defs()` discovers
  `data/runtimes/*.yaml` — no central registry list. Confirmed at
  `src/aspis/resources.py:122-136`. A new agent for that runtime is one body.
- **The CLI is fully data-driven.** `aspis/commands/__init__.py:36-58` lists 22 verbs
  in a tuple; adding a verb is one module + one tuple entry. `cli.py:47-56` loops over
  it. Cost: 1 file.
- **Workflows reference skills, never inline their procedure.** Confirmed in
  `project-lead-operating-protocol.md` (68 steps cite workflow/skill names).
- **No DEAD modules.** I ran orphan detection on 7 candidate files; every candidate
  has ≥1 importer. `lifecycle.py` is shared by 5 callers; `gitops.py`, `manifest.py`,
  `operations/init.py`, `operations/bootstrap.py` are each imported by exactly 1
  call site — small, but real.

### Caveats (cost-of-change boundary pressure)

#### C-1. `commands/governance.py` (642 lines) and `catalog/scripts/system/validate-approvals.py` (292 lines) are sister tools with overlapping responsibility

- `commands/governance.py` is the human-facing CLI (request, approve, audit, revoke, ledger, check). It implements protected-path glob matching (`_glob_to_regex` at line 114), the lock-file dance (`_acquire_lock` at line 227), the approval-covers-path check (`_entry_covers` at line 270), and 5 exit codes per governance.md §6.
- `catalog/scripts/system/validate-approvals.py` is the read-only validator the hooks / automation call. It re-implements its own protected-paths list (`PROTECTED_PATHS` at line 42) and a stripped-down YAML-or-JSON loader (`try_load_yaml_or_json` at line 54).
- **Both read the same ledger** (`.aspis/state/approval-ledger.yaml`). Both compute "is this path protected." But neither imports the other.

**Why it matters:** R-006 (single source). The two implementations are short enough that drift is unlikely today, but they will diverge the moment someone adds a new protected path: the CLI checks it, the validator doesn't, and the hook lets a protected write through. The clean fix is `validate-approvals.py` imports `is_protected` and the ledger helpers from `aspis.commands.governance` (or both import from a shared `aspis.governance` module), and the script lives at `src/aspis/data/catalog/scripts/system/` as a thin shim. Cost: 1 import + 1 file. **Severity: medium.** Documented; not in the F-018 SPEC.

#### C-2. The 14 new L3 subagents carry a `deny_floor:` frontmatter field that is not in the agent body standard

`AGENT_BODY_STANDARD.md` (lines 24-35) lists exactly **11 required frontmatter fields**:
`name, description, mode, model, temperature, tools, permissions, delegates, skills, runtimes, export_scope`. The validator (`commands/validate_runtime.py:24-36`) enforces exactly these 11.

But the 14 new L3 subagents (system-lead's 7, planning-lead's 8 — but only 14 because
test-lead's 6 testers also carry it, and 1 of system-lead's was already in scope) all
add a 12th field, `deny_floor:`, which restates the relevant subset of `permissions:` in
a flatter form. Examples:
- `catalog/agents/clarify.md:19` — `deny_floor: {bash: {git commit: deny, git push: deny, '*': deny}, ...}`
- `catalog/agents/dependency-analyzer.md:19` — same pattern, with extra allow patterns for planning scripts
- `catalog/agents/task-decomposer.md:19` — same pattern, with 5 allow patterns

**Why it matters:** (1) R-006 violation: the deny floor is one concept, declared twice
(in `permissions.bash.*` and in `deny_floor.bash.*`). They must stay in lock-step or
they disagree. (2) `validate-runtime` does not check it, so a drift is invisible to the
gate. (3) The block was added during F-018 but the standard was not updated. Either
deny_floor should become part of the standard (and the standard updated), or it should
be removed (the `permissions:` field already covers it). **Severity: medium.**
Documented at L3 gate; not resolved in F-018.

#### C-3. `committer.md` has `runtimes: []` (empty list, not "all")

- `committer.md:32` declares `runtimes: []`.
- The catalog spec (`.aspis/catalog/agents/.../committer.md` is a leaf agent; it runs
  on a human's machine, not a runtime tool). An empty list might mean "no runtimes
  apply" (correct intent) — but the export code
  (`src/aspis/export.py:_asset_meta`, line 92) treats empty `runtimes:` as "all
  runtimes" per the comment on `CatalogAgent` at `src/aspis/catalog.py:46`.
- So the committer body is currently being exported to `.opencode/agents/committer.md`
  and `.claude/agents/committer.md`, even though it has no business being a runtime agent.
- The standard is also silent on what `runtimes: []` means. It needs an explicit
  "skip export" sentinel — `export_scope: project-only` is the right vehicle
  (`bootstrap.md:7` already uses it). **Severity: low.** The body is harmless
  today (committer doesn't have `mode: subagent`-specific runtime behaviours) but
  it ships a useless file into every project that adopts ASPIS.

#### C-4. Two config-tiers: bundled + project-local

- `src/aspis/resources.py:97-114` exposes a tier-aware config resolver that searches
  `config/`, `config/policy/`, `config/reference/` (project-local first, then bundled).
- The project's own `.aspis/config/` mirrors the policy + reference tiers (modes.yaml,
  commit-convention.yaml) but is missing `constitution-checks.yaml` and the legacy
  flat `models.yaml`. This is by design (per F-014), but it means the project
  dogfoods a slightly different config tree than what it exports. **Severity: low.**
- The README in `src/aspis/data/catalog/config/README.md` explains the tier scheme.
  A project contributor will need to read this to know where to look.

### Bloat / duplication check

- **No file is "almost-duplicate of another file."** The 12 L1 scripts each have
  distinct inputs/outputs (scope_estimate, constitution_check, plan_quality_check,
  mode_validator, task_size_check, dependency_graph, search_cache, check_staleness,
  rank_source, compare_versions, cross_ref, validate-approvals). Their regex
  patterns differ; their argparse interfaces differ.
- **One mild bloat: 5 L1 scripts that read SPEC/TASKS/PROFILE text** all do
  `pathlib.Path.read_text(encoding="utf-8")` with a similar try/except shape. A
  shared `read_text_or_die(path, kind)` helper would shave ~5 lines per script.
  **Severity: nit.** Not worth doing.

### Line count vs. value

- `governance.py` 642 lines for a 6-subcommand CLI: high but justified (lock file,
  glob matching, ISO 8601 parsing, ledger read-modify-write, exit codes per spec).
- `export.py` 550 lines: justified (planning + writing + snapshot + audit log + locking).
- `drift.py` 383 lines: justified (per-field projection for 2 runtimes, comparison
  engine, CLI + ad-hoc entry point).
- The **895-line** `project-lead-operating-protocol.md` is the longest workflow. It
  has 68 numbered steps, 13 stop-and-ask conditions, and a per-intent pipeline for
  each of 10 request kinds. It is *workflow*, not narrative — every step has an
  output and a gate. Justified.

---

## 3. Rules compliance matrix (R-001…R-010)

| Rule | Title | Score | Evidence |
|---|---|---|---|
| **R-001** | Scope | **COMPLIANT** | All F-018 work was within declared scope (L0..L4); out-of-scope items (7 CLI validators, 5 deferred subagent categories) were explicitly tagged. The 19 `primary`/`summary` backfill is the only "scoped narrow" item that escaped; documented in BUILD_REPORT §6. |
| **R-002** | Gates first | **COMPLIANT** | `pytest` 369/369 pass on the in-scope suite; 8 confirmed failures fixed (5 model-tier, 1 rule-layers, 1 promotion logic, 1 caught incidentally); 3 BLOCKED: env items documented with root cause. `ruff format` + `ruff check` exit 0 on modified files. 5-gate sweep (L4) ran and recorded results. |
| **R-003** | Deterministic-first | **COMPLIANT** | L1 scripts (12) shipped *before* L3 agents that reference them. The `task-decomposer` agent has a documented fallback "if `task_compile.py` is unavailable, produce the structure and flag 'packets deferred — script missing'" — exactly the kind of degradation R-003 sanctions. |
| **R-004** | One writer | **COMPLIANT** | `committer.md:25` is the only agent with `git commit*` allowed. Every other agent's bash block denies it. The committer's `aspis commit*` is the primary path; raw `git commit*` is a "guarded fallback (only when `aspis` is genuinely unavailable)" per the inline comment. |
| **R-005** | Tests-as-spec | **COMPLIANT** | 12 new test files in `tests/unit/test_scripts/` (one per L1 script) added during F-018; the L0 gate fixed `test_catalog.py:152` and 5 model-tier test fixtures rather than weakening assertions. `test_bootstrap.py`, `test_gitcheck.py` are BLOCKED: env (Windows subprocess + Python 3.14) — these are *environment* failures, not assertion weakenings. |
| **R-006** | Thin agents, single source | **PARTIAL** | Bodies reference skills/workflows by name; 21 L3 subagents are 75-138 lines each (well under 200). BUT the `deny_floor:` field on 14 L3 subagents duplicates `permissions:` content (C-2 above). The committer body carries an inline commit-message convention summary that overlaps with `commit-message` skill — minor. **Action: pick one source for the deny floor and update the standard.** |
| **R-007** | Pinned models | **COMPLIANT** | Every one of the 33 agents declares `model: cheap|standard|deep`. The 5 leads (system/planning/build/reviewer/fix) were fixed in F-018 L0 from `standard` to `deep` per documented evidence (test names + comments; F-010 pattern). |
| **R-008** | Human gate | **COMPLIANT** | `commands/governance.py` ships the R-008 ledger (request/approve/audit/revoke/ledger/check). `validate-approvals.py` ships the validator. REQ-F-018-001 is filed and pending owner approval for the `.claude/settings.json` PreToolUse hook — exactly the path the spec demands. **Note:** T-046 is BLOCKED awaiting approval; this is the gate doing its job. |
| **R-009** | Trace and learn | **COMPLIANT** | 21 F-018 commits with detailed messages; every gate has a `B-L?-gate.md` report; every BLOCKED item has owner-action steps in BUILD_REPORT §6. F-018 L0 fixes (5 model-tier changes + 1 rule-layers) record the *why* in the model-tier proposal report — the L0 lesson. |
| **R-010** | Delegate with purpose | **COMPLIANT** | Delegate chains are explicit. `project-lead` → 8 leads; each lead → 1-10 subagents; subagents are leaves (`delegates: []`). The 5-leads-deep cost-of-change is preserved (per D-004: 4 sub-leads + project-lead = 5 primaries). |

**Net rule score: 9 COMPLIANT, 1 PARTIAL.** The PARTIAL (R-006) is bounded to the
`deny_floor:` duplication; it is fixable in one editing pass over 14 files plus a 1-line
update to `AGENT_BODY_STANDARD.md`. No rule is violated in spirit; only R-006 is
violated in form (content duplication between `permissions:` and `deny_floor:`).

---

## 4. Engineering quality

### Sound abstraction (boundaries between layers)

**Score: A.** The four-layer model is clean:

```
   brain (project .aspis/)  ── sourced from ──┐
   catalog (engine data)    ──┐               │
   engine (Python)          ──┼─ imports ──   │
   runtime dirs (.opencode/, .claude/)  ←──  export.py renders ─┘
```

- The catalog is the source of truth (D-005, R-001/R-006). The engine reads it; the
  runtimes are derived from it. No runtime directory is hand-edited.
- `runtimes/base.py:54-216` defines the `RuntimeAdapter` ABC with `runtime_dir`,
  `root_guide`, `supports_mode`, `supports(kind)`, `emit_runtime_hooks()` — the
  D-015 capability contract. Both OpenCode and Claude adapters honor it; both
  override only what they need.
- `assetkinds.py:58-71` is the single override table for per-runtime kinds. New
  brain kinds default to a copy op automatically (D-008).
- The CLI is a thin shell (`cli.py:47-56` builds the parser from the registry
  tuple). 22 verbs; the file never changes when a verb is added.

### Scalable (would it work for 50 agents? 500?)

**Score: A-.** At 33 agents the system has plenty of headroom. The
**bottlenecks-to-watch** at higher scale:

1. **`validate-runtime` does not scale by index.** It walks `agents/*.md` linearly.
   At 500 agents × 11 required-field checks = 5,500 file reads per run. Probably
   still <5 seconds. Not a real problem yet.
2. **`drift` walks the live runtime dirs** (`.opencode/agents`, `.claude/agents`)
   for *every* catalog agent, on every runtime. At 500 agents × 2 runtimes ×
   per-field projection = a lot of disk I/O. Caching (per `test-ledger.json`
   pattern, D-014) is a 1-day task.
3. **Catalog YAML frontmatter parsing** is per-file. The cost is dominated by
   `yaml.safe_load`, which is ~10× slower than a regex over well-formed files.
   For 500 agents × 2 runtimes + 5 L1 scripts that re-read, plan to cap at 5s.

The architecture itself scales. The implementation has hot spots but no
fundamentally-O(N²) design choices.

### Testable (can each module be tested in isolation?)

**Score: A.** 72 test files; 12 of them dedicated to the L1 scripts; the
`tests/unit/test_scripts/` subdir is the new convention introduced in F-018.
The pattern of one test file per script (e.g. `test_scope_estimate.py`,
`test_constitution_check.py`, ..., `test_validate_approvals.py`) is
maintainable and mirrors the source layout.

A few modules are not directly tested (the standard test surface is the
*behavior* through CLI verbs):
- `src/aspis/commands/artifact.py` — covered by `test_artifact.py`
- `src/aspis/commands/status.py` — thin wrapper; the underlying state is tested
- `src/aspis/runtimes/base.py:141-161` — default `detect()` returns `None`,
  trivially correct; OpenCode/Claude adapters are tested via `test_detect.py`
  and `test_model_detection.py`

The governance CLI's R-008 ledger dance is not directly unit-tested as of
F-018 (it ships in `commands/governance.py` but the L1 script
`validate-approvals.py` has 5 tests). **Severity: nit.** A
`test_governance_ledger.py` would close this gap.

### Maintainable (can a new developer understand the structure?)

**Score: A-.** Onboarding follows the documented `docs/QUICKSTART.md` and
`docs/ARCHITECTURE.md`. The "read first" sequence in `AGENTS.md` (lines 9-18)
gives a contributor a 5-minute context-load. The constitution document
(`rules/architecture-constitution.md`) and the constitution-checks
(`config/policy/constitution-checks.yaml`) make the standards machine-readable.

**One maintainability concern: the catalog-vs-engine naming convention.** Some
modules have twins in both:
- `src/aspis/commands/governance.py` (engine) ↔
  `src/aspis/data/catalog/scripts/system/validate-approvals.py` (catalog)
- `src/aspis/commands/byte_parity.py` ↔ `.aspis/scripts/hooks/byte_parity.py`
  (deployed)
- `src/aspis/commands/testledger.py` ↔ `.aspis/scripts/context/testledger.py`
  (deployed)

The convention is "engine has the implementation; catalog/ scripts are the
deployed copies invoked from the runtime hook boundary." But a new contributor
will ask: "Why are there *two* byte-parity modules?" The answer (R-002:
deterministic gates run at the hook surface) is in D-010 and
`hooks/byte_parity_checker` skill, but it requires reading two docs. **Severity: low.**

### No duplication

Already covered under §2 caveats (C-1 governance duplication, C-2 deny_floor
duplication). Otherwise the system is DRY: rule text lives in
`rules/system-rules.md` and is cited by ID, not restated; skill procedure lives
in `catalog/skills/*/SKILL.md` and is referenced, not inlined; commit-message
convention lives in `commit-convention.yaml` and is applied by `compose.py`.

### Cross-runtime parity (OpenCode vs Claude)

**Score: A.** Both adapters:
- implement the same `RuntimeAdapter` ABC;
- declare their `name`, `runtime_hooks`, `tools` map, and `supports_mode` flag
  on the class;
- load their declarative facts (dir, root_guide, run command, capabilities) from
  `data/runtimes/<name>.yaml` (D-015). Confirmed in `runtimes/base.py:127-136`.
- override only `render_agent`, `render_command`, `detect`, `model_string` —
  the four places the runtimes genuinely differ.

**Runtime hook parity is intentional, not equal:**
- OpenCode ships a TypeScript `session-notice.ts` plugin (Lite, fire-and-forget).
- Claude ships a `settings.json` PreToolUse hook (3 modules, BLOCKED on R-008).
- The asymmetry is documented in D-010: Claude's `settings.json` requires R-008
  human approval to edit, OpenCode's plugin does not. **The hook gap is a
  governance gate, not a parity violation.**

**One real parity finding:** the L3 subagents with `runtimes: [opencode, claude-code]`
(7 of the 14) spell the Claude runtime as `claude-code` rather than `claude` (the
adapter key). The OpenCode-side catalog uses `opencode`. This is a typo in the
frontmatter: `claude-code` is not a registered runtime; the adapter key is
`claude`. **Severity: low** — the export code checks `runtime in declared_runtimes`
and silently skips runs that don't match, so today this means **these 7 agents are
shipped to OpenCode only, not Claude**. The agents affected: `api-tester`,
`cli-tester`, `db-tester`, `python-tester`, `security-tester`, `ui-tester`,
`clarify` (and the rest of planning's 8). All of them need their `runtimes:`
field fixed from `claude-code` → `claude` (or simply omitted for "all").

---

## 5. Specific deep-dive findings

### `src/aspis/runtimes/` (per-adapter comparison)

| Aspect | OpenCode | Claude | Symmetric? |
|---|---|---|---|
| `name` | `opencode` | `claude` | yes |
| Adapter file | `opencode.py:26-197` (197 lines) | `claude.py:29-112` (112 lines) | similar shape |
| `render_agent` | folds tools + bash + delegates + skills into a `permission:` block | `tools:` list + preserves `permissions:` | different shape (Claude lacks permission block natively; preserved for PreToolUse guard) |
| `render_command` | binds command to agent (`agent: <name>`) | drops the binding | **asymmetric, by design** (Claude doesn't bind) |
| `detect()` | reads `auth.json` keys (no secret values) + `opencode models` listing | reads `~/.claude/settings.json` presence + alias set | different data sources, same cross-platform never-raise contract |
| `model_string()` | matches canonical id to `provider/model` string via `providers.yaml` rank | matches canonical id to `claude-<family>-*` → alias | different logic, same null-with-no-inventory contract |
| Runtime hooks | `session-notice.ts` (lite) | `settings.json` PreToolUse (BLOCKED on R-008) | different surfaces, by design |

**No name-checks anywhere** (`grep "if runtime == " src/aspis/runtimes/` = 0 hits).
D-002 + D-008 + D-015 are honoured.

### `src/aspis/commands/` (CLI verb consistency)

- All 22 verbs: `register(subparsers)` is the standard entry; all have a
  `parser.set_defaults(func=_run)` (or equivalent); all support `--help` via
  argparse; all return a process exit code.
- All subcommand handlers print to stdout and to stderr (errors) — consistent.
- Some have `--dry-run` (validate-index, export), some don't (drift, doctor).
  This is intentional: dry-run is for verbs that *write*; read-only diagnostics
  always run as-is.
- The 6 verbs in P1/F-017 (artifact, byte-parity, governance, validate-runtime,
  validate-index, drift) follow the same shape. The 22-verb registry is in
  `commands/__init__.py:36-58`.
- **One inconsistency:** `governance.py` has 5 subcommands (`request, approve,
  audit, revoke, ledger, check` — actually 6); no other verb has subcommands.
  This is by design (R-008 is a stateful surface) but the only `gov_command`
  sub-parser in the codebase. A future refactor could promote it to a top-level
  verb group. **Severity: nit.**

### `src/aspis/data/catalog/agents/` (33 agents)

**33 agents = 5 leads + 5 support + 6 workers + 1 read-only helper + 21 leaves (L3
subagents added in F-018).** Every body is in the 7-section structure
(Identity, How you work, Core rules, Responsibilities→skills, Delegation,
Dynamic-readiness, Edge Cases) with frontmatter at the top.

**Conformity findings:**

1. **All 33 agents have the 7 body sections** (verified against
   `AGENT_BODY_STANDARD.md`). The `bootstrap` agent has the documented exception:
   no `Responsibilities→skills` table (procedure is self-contained), no
   `Delegation` (it delegates to no one), and a separate `## Edge Cases` section
   (codified in `7f2d49f` per BUILD_REPORT §7).
2. **All 33 agents have ≥2 documented edge cases.** F-018 L4 gate
   (`B-L4-gate-sweep.md:47`) verified.
3. **Universal deny floor:** `git commit*` denied on all but committer; `git push*`
   denied everywhere. Verified by spot-check on `committer.md`, `project-lead.md`,
   `build-lead.md`, `runtime-validator.md`, `clarify.md`, `python-tester.md`.
4. **No `bash: '*': allow`** — confirmed by spot-check; the universal deny floor
   starts with `"*": deny` in every bash permission block.
5. **19 of 33 agents are missing `primary` and `summary` fields** (the BLOCKED-3
   finding). These are the **existing** agents (not the new L3 subagents). The
   14 new L3 subagents all have them. The validator
   (`commands/validate_runtime.py:24-36`) does NOT require them, so technically
   this is a **doc/validator drift**: the agent body standard
   (`AGENT_BODY_STANDARD.md`) lists 11 required fields, the 14 new L3 subagents
   have 12+1=13, and the gate sweep says 13. Pick one number.
6. **`runtimes: [claude-code]` typo on 7 L3 subagents** — see §4 cross-runtime
   parity. The typo means these agents ship to OpenCode only, not Claude.

### `.aspis/workflows/` (6 workflows)

| Workflow | Lines | Actionable? |
|---|---:|---|
| `build.md` | (size not measured) | yes — 9-step build loop |
| `fix.md` | — | yes |
| `plan.md` | — | yes |
| `small-task.md` | — | yes — compressed path |
| `review.md` | — | yes |
| `project-lead-operating-protocol.md` | 895 | yes — 68 numbered steps, 13 stop-and-ask conditions |

All workflows have numbered steps with `*Output:*` lines. All reference
skills/workflows/templates by name. None restate rule text inline. None carry
TODO/FIXME markers (grep confirmed).

### `.aspis/scripts/` (36 deterministic scripts)

- All mirror the catalog sources via export. Two are missing in deploy
  (`findings.py`, `session_start.py`) and 9 have byte-drift — all catalog
  ahead of deploy, not the reverse. Resolved by `aspis export --apply`
  (BLOCKED-2).
- All scripts: `argparse`, `--help` exit 0, stdlib-only (validate-approvals.py
  uses `yaml` with a JSON-or-regex fallback — still stdlib-friendly). The
  research scripts do *not* use the network; they are pure file/text processors.
  The plan scripts are pure parsers. The governance script reads YAML/JSON
  with three fallback strategies. All deterministic.
- All scripts: `if __name__ == "__main__": raise SystemExit(main())` — the
  ad-hoc invocation convention (`python -m aspis.scripts.X`) is honored.

### Determinism of `.aspis/scripts/`

**Score: A.** Every script is stdlib-only (with PyYAML as the optional YAML
loader in validate-approvals.py; if missing, the regex fallback runs). No
network calls. No LLM. No subprocess invocations that depend on external
state. The 12 L1 scripts all pass `AST parse + --help + smoke test +
byte-parity` per BUILD_REPORT §5 L1 gate.

---

## 6. Technical debt inventory

### Documented BLOCKED items (3)

#### BLOCKED-1: T-046 — PreToolUse hook not applied to `.claude/settings.json`

- **What:** 3 hook modules exist (`deny_floor.py`, `pretool_secret_scan.py`,
  `protected_path.py`) but the `.claude/settings.json` edit is gated by R-008.
- **Owner action:** approve REQ-F-018-001 via
  `python -m aspis.commands.governance approve REQ-F-018-001 --approver owner`
  → edit `settings.json` to add the PreToolUse block → re-run preflight.
- **Cost:** 5 min, no code changes.
- **Risk if not done:** runtime hook parity gap; OpenCode gets a lite
  `session-notice`, Claude gets no enforcement. Functional but unhardened.

#### BLOCKED-2: Byte-parity drift — 9 drifted + 2 missing deploys

- **What:** Catalog source is ahead of `.aspis/scripts/` deploy for 9 files
  (context scripts: `_common`, `build_state`, `record_changes`, `build_registry`;
  hook scripts: `_config`, `cleanup`, `gitignore`, `precommit`, `runtime_guard`).
  2 files have no deploy at all: `findings.py`, `session_start.py`.
- **Owner action:** `aspis export --apply` to resync.
- **Cost:** <1 min, no code changes.
- **Risk if not done:** the project dogfoods an out-of-date brain. The
  catalog is the source of truth (D-005); the deploy is the truth the agents
  actually run. Drift means the system is not self-validating in this
  project, even though it is in any newly-initialized project.

#### BLOCKED-3: 19 agents missing `primary` / `summary` fields

- **What:** 19 of 33 agent bodies lack `primary:` and `summary:` in their
  frontmatter. The L4 gate sweep flags this as FAIL.
- **Owner action:** script a 1-line-per-file backfill: `primary: true` for
  the 5 leads + project-lead, `primary: false` for the rest; `summary:`
  = the description repeated (mechanical).
- **Cost:** <30 min, no architectural changes.
- **Risk if not done:** `validate-runtime --runtime all` will fail; the
  catalog index (if it uses `summary:`) will have 19 missing entries.
  **But:** the validator code in `commands/validate_runtime.py` does not
  actually check these fields. The 19 agents are functionally complete.
  This is a doc/validator drift more than a real defect.

### Documented deferred items (F-019+)

| Item | Where it lives | Why deferred |
|---|---|---|
| 7 missing CLI validators (validate-skills, validate-agents, validate-decisions, validate-constitution, validate-trace, validate-parity, validate-profiles) | F-018 SPEC §"Out of scope" | governance-enforcement infrastructure; needs verb scaffolding + per-validator design |
| `validate-approvals.py` sibling CLI verb (vs. the hook script) | F-018 SPEC | "first validator built in F-019" |
| Reviewer's `sub-reviewer`, `security-reviewer` | F-018 SPEC | workload-justified extraction per D-005 |
| Research-lead's `codebase-explorer`, `docs-fetcher`, `web-researcher`, `cache-manager` | F-018 SPEC | workload-justified extraction per D-005 |
| Fix-lead's `bug-triager`, `gate-fixer` | F-018 SPEC | workload-justified extraction per D-005 |
| Project-lead's `context-feeder`, `context-summarizer` | F-018 SPEC | requires Phase 3 trace spine |
| `enforcement: warn` → `block` flip | F-018 SPEC | requires probation with hook active |
| Trace spine (Phase 3) | ROADMAP | explicit roadmap item |
| Self-improvement loop (Phase 4) | ROADMAP | explicit roadmap item |
| Dashboard (Phase 5) | ROADMAP | explicit roadmap item |

### Test environment debt (3 BLOCKED: env items)

| Test | Status | Root cause | Workaround |
|---|---|---|---|
| `tests/test_bootstrap.py` | BLOCKED: env (14 tests, 8 pass, 6 not observed) | Windows Python 3.14 subprocess teardown hang | mark xfail on Windows 3.14; investigate root cause |
| `tests/test_gitcheck.py` | BLOCKED: env (3 tests, all pass, ~120s total) | Extreme latency under test harness | raise pytest timeout or skip-on-slow |
| `tests/test_promotion.py::test_bootstrap_promotes_leads` | BLOCKED: env | Fails on system Python 3.14.2; passes on `uv run` | pin to `uv run` in CI |

These are **real** environment issues, not assertion weakenings. The L0 gate
documented them with `BLOCKED: env` and they were not fixed because they are
not in the F-018 scope. They should be the first items addressed in F-019's
"harden the dev env" track.

### Smaller findings (nits, not blockers)

- **`committer.md:32` has `runtimes: []`** — empty list, ambiguous meaning.
  Should be `runtimes: [opencode, claude]` (it is committed-from by the
  runtime) or `export_scope: project-only` (it doesn't ship to a runtime).
- **7 L3 subagents have `runtimes: [opencode, claude-code]`** — `claude-code`
  is not a registered runtime; should be `claude`. Means these agents ship
  to OpenCode only.
- **`deny_floor:` field** is on 14 L3 subagents but not in the agent body
  standard. Either standardize it or remove it (R-006).
- **`commands/governance.py` + `scripts/system/validate-approvals.py`** share
  protected-path matching and ledger reading but don't share code (R-006).
- **`.aspis/config/` is missing the `constitution-checks.yaml` tier-1 mirror** —
  the engine reads from the catalog directly (`config/policy/constitution-checks.yaml`)
  via the tier-aware resolver, so this is harmless. But the symmetry of the
  exported config tree is broken.
- **No tests for the governance CLI** (the human-facing tool). The validator
  has 5 tests; the CLI has none. **Severity: low.**

### TODOs / FIXMEs in code

- **Zero TODO / FIXME / HACK markers** in catalog scripts, catalog agents,
  catalog skills, or catalog workflows. Confirmed by grep across all of
  `src/aspis/data/catalog/`.
- The only `TODO` reference is in `skills/packet-validation/SKILL.md:43`
  as a *checklist item* ("no `TODO` markers, no `TBD` placeholders in
  critical fields") — meta, not actual debt.
- The only `XXX` references are in `scripts/planning/scope_estimate.py:4-5`
  and `scripts/planning/plan_quality_check.py:41-58` — they are regex
  patterns (`FR-XXX-NNN`) used to detect requirement IDs, not debt markers.

### Code-vs-spec reconciliation

- The 11-field agent body standard in `AGENT_BODY_STANDARD.md` is enforced
  by `validate-runtime` (the verb), but the L4 gate sweep references a
  13-field standard. The 19 missing `primary`/`summary` are thus a **doc
  drift** more than a real defect. **Action: align the standard with the
  validator (or vice versa).** Pick 11 or 13. The simplest fix is to drop
  `primary`/`summary` from the standard (they are nice-to-have metadata,
  not contractual) and remove the gate-sweep check. Cost: 1 doc edit.

---

## 7. Final verdict

### **NEEDS WORK**

The build is structurally sound, the architecture is honoured, the gates
that should pass are passing, and the 60 product artifacts are real,
working, and tested. The system is not **CLEAN** because three BLOCKED
items remain, all with known owner-action paths and bounded costs. The
system is not **REQUIRES REFACTOR** because the architecture is the right
shape: adding a new brain kind is zero core files; adding a new agent is
one file; adding a new runtime is one YAML file + one adapter module.
The 3 BLOCKED items are operational gaps, not design failures.

### What needs to happen to reach CLEAN

1. Approve REQ-F-018-001 + edit `.claude/settings.json` (BLOCKED-1, 5 min).
2. Run `aspis export --apply` (BLOCKED-2, <1 min).
3. Pick one: drop `primary`/`summary` from the standard (1 doc edit) OR
   backfill them across 19 agents (1 script + 19 file writes). Either path
   resolves BLOCKED-3.
4. Fix the 7 L3 subagents' `runtimes: [opencode, claude-code]` → `claude`
   (7 file edits, 1 line each).
5. Pick one: remove `deny_floor:` from 14 agents, or add it to the standard.
6. Optional: extract a shared `aspis.governance` module so
   `commands/governance.py` and `scripts/system/validate-approvals.py`
   share `is_protected()` and the ledger loader.

### Why the verdict is not REQUIRES REFACTOR

- The cost-of-change test holds: a new agent is one file; a new skill is one folder; a new brain kind is zero core files; a new runtime is one adapter module + one YAML.
- The D-008 / D-015 / D-016 / D-017 / D-018 contracts are honoured — no name checks, no hard-coded runtime lists, no special cases.
- The agents are thin (75-160 lines) and reference skills/workflows by name.
- The hooks are non-blocking by default (D-010) and require R-008 to flip to block.
- One writer (R-004) is enforced in the catalog and in the validator.
- Tests are spec (R-005): 8 confirmed failures were fixed; 3 env-blocked items are documented, not silenced.
- The architecture constitution (cost-of-change, plugin-first, single-source, local-change, no-special-cases) is the standard the system itself was built to.

The remaining work is **bounded, mechanical, and documented**. None of it
requires a rethink.

---

## 8. Top 5 recommendations for F-019

Ordered by cost-of-not-doing × ease-of-doing:

1. **Resolve BLOCKED-3 first (19-agent `primary`/`summary` backfill).** 30 min, scripted.
   Unblocks `validate-runtime --runtime all` to green and lets the L4 gate
   sweep's Gate 2 close. *Easy win; restores catalog index integrity.*

2. **Fix the `runtimes: [opencode, claude-code]` typo on 7 L3 subagents.** 1-line edits.
   The 7 affected agents are: `api-tester, cli-tester, db-tester, python-tester,
   security-tester, ui-tester, clarify, constitution-checker, dependency-analyzer,
   idea-capture, prd-writer, research-request-writer, scope-estimator, task-decomposer`.
   *Restores cross-runtime parity (R-006 + C-PLUGIN-FIRST); agents ship to both
   runtimes as designed.*

3. **Run `aspis export --apply` + approve REQ-F-018-001.** 6 min total. Closes
   BLOCKED-1 (Claude PreToolUse hook active) and BLOCKED-2 (deploy parity).
   *Brings the dogfood into the state the spec demands.*

4. **Build the 7 deferred CLI validators** (`validate-skills`, `validate-agents`,
   `validate-decisions`, `validate-constitution`, `validate-trace`,
   `validate-parity`, `validate-profiles`). Start with `validate-skills` (the
   next P0). Closes the governance-enforcement gap; the F-018 SPEC marks these
   as the primary F-019 deliverable. *Each validator is a 100-200 line script
   in `commands/`, mirroring the `validate-runtime` shape.*

5. **Resolve the `deny_floor:` duplication (R-006 PARTIAL).** Either:
   - (a) Add `deny_floor` to the 11-field standard (1 doc edit) and
     backfill the 19 missing agents (1 script, 19 file writes), OR
   - (b) Remove `deny_floor:` from the 14 L3 subagents and re-test
     `test_agent_permissions.py` to confirm the `permissions:` field alone
     carries the deny floor correctly. *Closes the doc/validator drift
     that the F-018 L3 gate left behind.*

### Honourable mentions (if capacity allows)

- Investigate the 3 BLOCKED: env test items (Windows Python 3.14 subprocess
  hang in `test_bootstrap.py` + slow `test_gitcheck.py` + promotion test
  Python version sensitivity). These are CI blockers on Windows.
- Extract `aspis.governance` as a shared module so the CLI verb and the
  hook script import the same `is_protected()` and ledger helpers. Closes
  the C-1 duplication in §2.
- Build `tests/test_governance_ledger.py` to cover the human-facing CLI's
  request/approve/audit/revoke/ledger/check flow end-to-end. The 5 unit
  tests for `validate-approvals.py` prove the script; nothing proves the
  CLI's lock dance and ISO 8601 parsing.

---

*Audit stamped by Reviewer (deep tier) on F-018/D-quality-audit. Independent
review — no agent audited its own work. All findings are evidence-backed;
the BLOCKED items inherit their evidence from F-018's gate reports and
BUILD_REPORT; the new findings (C-1, C-2, C-3, C-4, the 7-agent typo, the
deny_floor duplication) are direct observations from the audit.*
