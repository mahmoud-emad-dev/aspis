# F-017 — Implementation Plan

> Mode: **production** — full plan.

## Summary
F-017 turns F-016's agent system *designs* into *working assets*. The approach is **layered by depth, agent-by-agent within each layer**: build shared infrastructure once at L0, then deepen through L1 (per-lead core), L2-P0 (CLI verbs + governance + leaf agents), and L2-P1 (remaining skills + edge cases). Every layer has a deterministic exit gate. The plan honors R-006 (single source — every fact in one place, referenced, never duplicated), R-003 (deterministic-first — script before agent), and the architecture constitution (new files over core edits, cost-of-change ≤ 3). The deliverable is 12 final agent bodies, 25 new skills, 6 CLI verbs, 1 governance subagent, 3 deployed scripts, and a verified core loop.

## Technical context
- **Language / version**: Python 3.11+ (scripts + CLI verbs). Markdown/YAML (agent bodies, skills, workflows, templates). No product code changes to `src/aspis/` Python modules unless a rendering bug is uncovered.
- **Key dependencies**: F-016 reference specs (12 agent refs, 5 systemic specs, skills inventory), existing catalog agents (11 thin bodies), existing skills (38), existing workflows (5), catalog script sources (4 files at `src/aspis/data/catalog/scripts/planning/`), `modes.yaml`, `models.yaml`, architecture constitution, system rules R-001–R-010.
- **Storage / interfaces**: Agent bodies at `src/aspis/data/catalog/agents/`. Skills at `src/aspis/data/catalog/skills/<name>/SKILL.md`. Scripts at `src/aspis/data/catalog/scripts/` (source) → `.aspis/scripts/` (deployed). Workflows at `.aspis/workflows/`. CLI verbs as new `src/aspis/commands/<verb>.py` modules (expose `register(subparsers)`, listed in `COMMAND_MODULES` in `commands/__init__.py`; dispatched from `src/aspis/cli.py`). Governance ledger at `.aspis/state/approval-ledger.yaml`.
- **Testing**: AST parse for scripts, `--help` for CLI verbs, structural validation for agent bodies (required sections, resolved references), end-to-end loop run for L1 exit gate, `aspis validate-runtime` / `aspis byte-parity` for systemic validation (skill→agent→delegate consistency folded into validate-runtime).
- **Project type / structure**: Asset-authoring feature. New files in `catalog/skills/`, `catalog/templates/`, `.aspis/scripts/planning/`, `.aspis/context/`, `src/aspis/commands/`. Edits to existing catalog agent bodies. No edits to `src/aspis/` core Python modules unless a rendering or path-resolution bug is discovered.
- **Constraints**: Must preserve catalog as single source of truth. Must not break existing agent rendering. Must pass architecture constitution gate-check (cost-of-change ≤ 3 for any new agent/skill). Claude Code adapter fix must not regress existing Claude setups.

## Gate check
The plan must clear the project's rules before any build.

- [x] **R-001 Scope** — Changes stay within `src/aspis/data/catalog/` (agents + skills + templates + scripts), `.aspis/scripts/planning/` (deployment), `.aspis/workflows/` (verification), `.aspis/context/` (conventions), `src/aspis/commands/` (new verbs), and `.aspis/state/` (governance ledger). No edits to core Python modules unless a bug forces it. No edits to `.opencode/` or `.claude/` (owner runs export manually). PASS.
- [x] **R-002 Gates** — Deterministic gates at every layer: AST parse + `--help` for scripts/verbs, `aspis validate-runtime` for agent bodies, `aspis byte-parity` for cross-runtime parity, cross-reference script for skill→agent→delegate consistency, end-to-end loop run for L1 exit. PASS.
- [x] **R-005 Tests-as-spec** — Every skill has documented acceptance (Anti-patterns + Outputs sections). Every CLI verb has `--help` + dry-run + exit-code contract. Agent body standard is the testable contract. End-to-end loop run is the integration test. PASS.
- [x] **R-008 Human gate** — Governance subagent is the mechanism; its design is R-008-gated. Live runtime regeneration is explicitly out-of-scope. Architecture decisions flagged below. PASS.

## Architecture

### Layered design — L0 → L3

```
L3 (F-018): Subagents + nested
    system-lead subs, planning-lead subs, stack testers
    
L2-P1: Depth + remaining skills
    6 P1 skills, 3 P1 CLI verbs, edge cases
    
L2-P0: CLI verbs + governance + leaf agents
    3 P0 CLI verbs, governance subagent, 3 leaf agents full sets
    [OWNER REVIEW GATE — hard stop]
L1: Per-lead core (8 leads)
    Final bodies, own P0 skills, wired tools, verified permissions
    Exit: plan→build→review→commit runs end-to-end on cheap+standard
    
L0: Shared foundation
    7 shared P0 skills, 3 scripts deployed, workflows verified,
    agent-body standard, dynamic-readiness convention
```

**Dependency direction**: L0 → L1 → L2-P0 → L2-P1. Each layer unblocks the next. Within a layer, agents are independent (parallelizable). A shared asset is authored once at the layer where it's first needed by multiple agents.

**Cost-of-change**: Adding a hypothetical new leaf agent or skill after F-017 = 1 new catalog file + 1 entry in the owning agent's frontmatter + (optionally) 1 referencing agent's frontmatter = ≤ 3 files. Adding a new skill = 1 new catalog file + 1 entry in owning agent's frontmatter = 2 files.

### Component 1 — Agent body standard (L0)

A durable reference document at `.aspis/context/AGENT_BODY_STANDARD.md` defining:
- Required frontmatter fields (name, description, mode, model, temperature, tools, permissions, delegates, skills, runtimes, export_scope)
- Required body sections (Identity, How you work, Core rules, Responsibilities→skills table, Delegation, Dynamic-readiness)
- The thin-agent rule: content lives in skills/workflows; bodies reference by name/path, never inline
- The cite-don't-restate rule: system rules cited by ID only
- Checkable checklist for reviewer use

Every agent body written in L1/L2 checks against this standard. The standard itself is the source of truth; individual bodies do not restate it.

### Component 2 — Dynamic-readiness convention (L0)

A durable reference document at `.aspis/context/DYNAMIC_READINESS.md` defining:
- The three dials: mode (rigor ceiling), task kind/scope (inherent need), model capability (scaffolding need)
- The key distinction: optimize the path (fewer files/steps for strong models), never the bar (same quality regardless)
- The leanest-correct-path default: skip phases/workflows the work doesn't warrant, load smart/needed context only
- How agents read the dials from existing infrastructure (`modes.yaml`, frontmatter tier, `context-ladder`)
- Written so a future router engine can drive these dials without rewriting bodies

Each loop agent's dynamic-readiness block references this document and encodes its own application of the three dials.

### Component 3 — Planning scripts + templates deployment (L0)

Script source: `src/aspis/data/catalog/scripts/planning/` (5 files: `_console.py`, `feature_scaffold.py`, `task_compile.py`, `prereq_validate.py`, `active_feature.py`)

Deploy to: `.aspis/scripts/planning/` (byte-for-byte copy, never a move)

Template source: `src/aspis/data/catalog/templates/planning/` (5 files: `SPEC.md`, `PLAN.md`, `TASKS.md`, `ACCEPTANCE.md`, `TASK_PACKET.md`)

Deploy to: `.aspis/templates/planning/` (byte-for-byte copy, never a move)

Validation per script:
- File exists at destination
- `python <script> --help` returns usage (exit 0)
- AST parse: `python -c "import ast; ast.parse(open('<script>').read())"` exits 0
- `feature_scaffold.py` refuses to overwrite an active feature (raises `FeatureActiveError`)
- `prereq_validate.py --phase plan` exits 0 when SPEC.md present
- `task_compile.py --dry-run` parses a known TASKS.md and reports packet set

### Component 4 — Shared P0 skills (L0)

Seven P0 skills that are prerequisites for the core loop, authored to the catalog pattern:

| Skill | Owning agent(s) | Why L0 |
|---|---|---|
| `mode-decision` | planning-lead, project-lead | Truly cross-cutting — both leads use it |
| `recontextualization` | project-lead | Needed by the entry point to reload context |
| `constitution-checks` | planning-lead | PLAN audit gate — blocks planning quality |
| `constitution-check` | reviewer | Review gate — blocks review quality |
| `evidence-validation` | reviewer | "Verify, don't trust" — blocks review quality |
| `packet-validation` | build-lead | Task packet gate — blocks build quality |
| `builder-selection` | build-lead | Builder routing — blocks build delegation |

Each skill follows the catalog pattern: frontmatter (name, description) + Purpose / When to use / Procedure / Outputs / Anti-patterns.

### Component 5 — Workflow verification (L0)

Verify 5 existing workflows against owning agents' reference specs, filling gaps:

| Workflow | Owning agent | Current lines | Target check |
|---|---|---|---|
| `plan.md` | planning-lead | 52 lines | Verify against planning-lead ref § phases P0–P8 |
| `build.md` | build-lead | 43 lines | Verify against build-lead ref § 9-step loop |
| `review.md` | reviewer | ~30 lines | Verify against reviewer ref § 9 dimensions |
| `fix.md` | fix-lead | ~30 lines | Verify against fix-lead ref § 6-step spine |
| `small-task.md` | planning-lead (dispatch) | — | Verify tracks: Question/Trivial/Small-task |

Fill gaps: add missing steps, remove TODO markers, align step names with reference spec procedure sections. Do not restructure — extend in-place.

### Component 6 — Per-lead core bodies (L1)

For each of the 8 leads, finalize the catalog agent body to the standard shape:

1. **Read** the agent's F-016 reference spec (`Research/ref/<agent>.md`) for the authoritative design
2. **Read** the existing thin catalog body (`catalog/agents/<agent>.md`) for the current state
3. **Diff** against the agent body standard — add missing sections, fill thin content
4. **Author** any P0 skills the agent owns that were NOT built in L0 (e.g., `security-review` for reviewer, `cache-management` for research-lead, `catalog-validator` for system-lead, `governance-approval` for system-lead, `harvest-protocol` for research-lead)
5. **Wire** tools/hooks per the reference spec's permission surface — least-privilege, deny floor honored
6. **Verify** delegation edges — every delegate listed exists as a catalog agent
7. **Add** dynamic-readiness block referencing the convention

Agents in L1 (with their L0-gap P0 skills):

| Agent | P0 skills to author (not in L0) |
|---|---|
| project-lead | `session-continuation` (P1, but can stub P0) |
| planning-lead | (all P0 covered in L0) |
| build-lead | (all P0 covered in L0) |
| reviewer | `security-review` |
| system-lead | `catalog-validator`, `governance-approval`, `drift-detector` |
| fix-lead | (none — uses shared skills) |
| test-lead | (none — uses shared skills) |
| research-lead | `cache-management`, `harvest-protocol` |

**L1 exit gate**: A sample feature runs plan→build→review→commit end-to-end on cheap/standard models. This is a hard gate — owner reviews at this checkpoint before L2 begins.

### Component 7 — L2 P0: CLI verbs (L2)

Three P0 CLI verbs implemented as deterministic Python modules under `src/aspis/commands/` (each exposes `register(subparsers)`, listed in `COMMAND_MODULES` in `commands/__init__.py`, dispatched from `src/aspis/cli.py`):

| Verb | Script | Contract |
|---|---|---|
| `validate-runtime` | `src/aspis/commands/validate_runtime.py` | Reads all catalog agents; checks structural validity (frontmatter fields present, refs resolve, delegate refs resolve, no orphan delegates); exits 0 when all pass; reports per-file pass/fail with file:line evidence. Also folds in the cross-agent consistency check (0 broken refs, 0 orphan delegates). |
| `byte-parity` | `src/aspis/commands/byte_parity.py` | **Read-only reporter** over the existing rendering/protection pipeline (`plan_export`/`write_export`/`protect`). Renders each catalog agent in-memory; checks catalog self-consistency (render matches expected output shape, no broken refs, no missing fields); reports CLEAN/CONFLICT/PROTECT per the protection engine contract; exits 0 when all CLEAN. Does NOT reimplement rendering or protection. Live `.opencode`/`.claude` parity is verified only after the owner's manual post-F-017 `aspis export`. |
| `export` | `src/aspis/commands/export_cmd.py` | **Thin wrapper** over the existing `plan_export`/`write_export`/`protect` pipeline (reconciles with `aspis init` — same pipeline, single source). Renders all catalog agents for target runtime(s); applies protection engine (CONFLICT/PROTECT); `--dry-run` reports plan without writing; preserves `permission:` block in Claude Code adapter output (fix the stripping bug in `src/aspis/runtimes/claude.py`). Acceptance: no duplication of rendering/protection engine. |

Each verb:
- Exposes `register(subparsers)` and is listed in `COMMAND_MODULES` in `src/aspis/commands/__init__.py`
- Is dispatched from `src/aspis/cli.py` (do NOT create `src/aspis/cli/` directory)
- Has `--help` returning usage information
- Exits 0 on success, non-zero on failure
- Outputs per-file pass/fail with file:line evidence on failure
- Is stdlib-only except for `pyyaml` (the project-wide YAML dep, used by the
  governance ledger and other `aspis` commands) — no *new* third-party deps

### Component 8 — L2 P0: Governance subagent (L2)

A deterministic enforcement mechanism — not an LLM agent — for R-008 human gate:

| Artifact | Path | Purpose |
|---|---|---|
| Governance module | `src/aspis/commands/governance.py` | CLI entry point (`aspis governance <subcommand>`); exposes `register(subparsers)`, listed in `COMMAND_MODULES` |
| Boundary checker | `src/aspis/commands/governance.py` (shared) | Exact-match path check against protected paths set |
| Approval ledger | `.aspis/state/approval-ledger.yaml` | Append-only YAML log of approvals with fields: `id`, `paths`, `reason`, `approver`, `expiry`, `glob_approval`, `status`, `timestamp` |

**CLI subcommands — match governance.md §6 verbatim:**

1. `request --paths <path> [<path>...] --reason <text>` — declare intent to write protected path(s)
2. `approve <request-id> --approver <name> [--expiry <ISO-date>] [--glob-approval]` — human records R-008 approval (the gate). `--approver` is REQUIRED — dropping it is a forbidden R-008 redesign. `--glob-approval` is a dangerous extension: warns + confirms before granting pattern-level approval.
3. `audit [--since <date>] [--approver <name>]` — query ledger history
4. `revoke <request-id> --approver <name>` — append-only revoke (new entry, never edit)
5. `check <path>` — diagnostic: would this write be allowed right now?
6. `ledger` — operational health (entry count, stale approvals, last activity, stale lock detection >60s)

**Minimal boundary-check (don't gold-plate)**: The governance subagent's core check is: does the path being written match a protected path pattern? If yes, is there an active (non-revoked, non-expired) R-008 approval in the ledger? If no, block. No `--force`, no env-var override. Process-level file lock on ledger writes.

Protected paths (canonical set):
- `rules/**`, `.aspis/rules/**`
- `.aspis/config/hooks.yaml`, `modes.yaml`, `constitution-checks.yaml`, `capabilities.yaml`, `agent-capabilities.yaml`, `commit-convention.yaml`
- `profiles/defaults.yaml`
- `.opencode/agents/**`, `.claude/agents/**`, `.claude/settings.json`
- `**/permissions*.yaml`
- `.aspis/current/active_feature.json`

### Component 9 — L2 P0: Leaf agents (L2)

Three leaf agents get complete asset sets matching the standard shape:

| Agent | Skills to author/verify | Key constraint |
|---|---|---|
| committer | `clean-tree-precondition`, `commit-message`, `commit-splitting` (verify existing) | No `edit`/`write` tools. `git commit*` allowed (only agent). Leaf — no delegation. |
| general-builder | `prestart-checks`, `clean-tree-precondition` (verify existing) | Path-scoped edits. Max-turns cap. No delegation. No commit. |
| project-explorer | (procedural — no named skills needed) | No `edit`/`write` tools. Leaf — no delegation. Read-only. |

### Component 10 — L2 P1: Depth + remaining (L2)

After L2-P0 is verified, build the depth layer:

**P1 skills (6 in L2-P1; session-continuation authored in L1/T-16)**: byte-parity-checker, export-manager, finding-format, model-router, runtime-author, scope-compliance — each a `catalog/skills/<name>/SKILL.md` file.

**P2 skills (4)**: commit-readiness, hook-author, model-inventory, profile-manager — same pattern. (`dependency-audit` deferred to F-018.)

**P1 CLI verbs (3)**:
- `validate-index` — checks FILE_REGISTRY.yaml and CODE_MAP.md freshness
- `drift` — per-field per-agent catalog↔live drift detection
- `governance` verb (if not fully built in L2-P0 — add subcommands)

**Edge-case coverage**: Each lead agent's body adds error-handling for at least 2 edge cases from its reference spec (e.g., planning-lead: stuck-on-ambiguous-request, mode-mismatch; build-lead: builder-timeout, packet-impossible; reviewer: same-model-contamination, no-evidence-verdict).

## Steps

| Step | Layer | Files | Gate |
|---|---|---|---|
| 1. Deploy planning scripts + templates | L0 | `.aspis/scripts/planning/*` (5 files) + `.aspis/templates/planning/*` (5 files) | AST parse + `--help` exits 0 per script; templates valid markdown |
| 2. Verify workflows | L0 | `.aspis/workflows/*` (5 files) | No TODO/NYI markers; steps align with ref specs |
| 3. Author agent-body standard | L0 | `.aspis/context/AGENT_BODY_STANDARD.md` | Checklist matches every agent body section |
| 4. Author dynamic-readiness convention | L0 | `.aspis/context/DYNAMIC_READINESS.md` | Three dials documented; referenced by L1 agents |
| 5. Author shared P0 skills (7) | L0 | `catalog/skills/<name>/SKILL.md` (7 files) | Each has valid frontmatter + required sections |
| 6. **CHECKPOINT L0** | — | — | All scripts pass; all skills valid; conventions documented |
| 7. Finalize project-lead body + own skills | L1 | `catalog/agents/project-lead.md` + skills | Body passes standard check; skills resolve |
| 8. Finalize planning-lead body | L1 | `catalog/agents/planning-lead.md` | Body passes standard check; skills resolve |
| 9. Finalize build-lead body | L1 | `catalog/agents/build-lead.md` | Body passes standard check; skills resolve |
| 10. Finalize reviewer body + own skills | L1 | `catalog/agents/reviewer.md` + skills | Body passes standard check; skills resolve |
| 11. Finalize system-lead body + own skills | L1 | `catalog/agents/system-lead.md` + skills | Body passes standard check; skills resolve |
| 12. Finalize fix-lead body | L1 | `catalog/agents/fix-lead.md` | Body passes standard check; skills resolve |
| 13. Finalize test-lead body | L1 | `catalog/agents/test-lead.md` | Body passes standard check; skills resolve |
| 14. Finalize research-lead body + own skills | L1 | `catalog/agents/research-lead.md` + skills | Body passes standard check; skills resolve |
| 15. Cross-agent consistency check | L1 | All 8 lead bodies | 0 broken refs, 0 orphan delegates (folded into validate-runtime at T-33) |
| 16. **OWNER REVIEW GATE — L1 EXIT** | — | — | plan→build→review→commit runs end-to-end on cheap+standard |
| 17. Build `validate-runtime` verb | L2-P0 | `src/aspis/commands/validate_runtime.py` | `--help` + dry-run exits 0 on valid catalog |
| 18. Build `byte-parity` verb | L2-P0 | `src/aspis/commands/byte_parity.py` | `--help` + dry-run reports per-agent parity |
| 19. Build `export` verb + Claude adapter fix | L2-P0 | `src/aspis/commands/export_cmd.py` + adapter | `--help` + `--dry-run` exits 0; permission block preserved |
| 20. Build governance subagent (minimal) | L2-P0 | `src/aspis/commands/governance.py` + `.aspis/state/approval-ledger.yaml` | `check <protected-path>` blocks; ledger append-only |
| 21. Finalize committer body | L2-P0 | `catalog/agents/committer.md` | Body passes standard check; skills resolve |
| 22. Finalize general-builder body | L2-P0 | `catalog/agents/general-builder.md` | Body passes standard check; skills resolve |
| 23. Finalize project-explorer body | L2-P0 | `catalog/agents/project-explorer.md` | Body passes standard check; skills resolve |
| 24. **CHECKPOINT L2-P0** | — | — | All 3 CLI verbs functional; governance blocks protected writes; 3 leaf agents complete |
| 25. Author P1 skills (6) | L2-P1 | `catalog/skills/<name>/SKILL.md` (6 files) | Each has valid frontmatter + required sections |
| 26. Author P2 skills (4) | L2-P1 | `catalog/skills/<name>/SKILL.md` (4 files) | Each has valid frontmatter + required sections |
| 27. Build P1 CLI verbs (3) | L2-P1 | `src/aspis/commands/validate_index.py`, `drift.py`, governance additions | `--help` + dry-run exits 0 |
| 28. Edge-case coverage for leads | L2-P1 | `catalog/agents/*.md` (8 bodies) | ≥ 2 edge cases per lead body, per ref spec |
| 29. Final acceptance sweep | L2 | All files | `validate-runtime` exits 0; `byte-parity --dry-run` reports catalog self-consistency; 0 broken refs |

## Verification
Run before declaring any layer done:

```bash
# Per script/verb: AST parse + --help
python -c "import ast; ast.parse(open('.aspis/scripts/planning/feature_scaffold.py').read())"
python .aspis/scripts/planning/feature_scaffold.py --help

# Per agent body: standard shape check
# (cross-reference script validates sections, refs, delegates)

# L1 exit gate: end-to-end loop
# Run plan→build→review→commit on a sample feature using cheap+standard models

# L2 exit gate: systemic validation
aspis validate-runtime --runtime all
aspis byte-parity --dry-run
aspis export --dry-run
aspis governance check rules/system-rules.md  # must block
```

## Risks & rollback

- **Risk**: A P0 skill's design in F-016 inventory is too thin to author directly.
  → **Mitigation**: Each skill task reads the owning agent's reference spec for the use case before writing. If genuinely underspecified, flag and proceed with best interpretation — don't block.
- **Risk**: The Claude Code adapter fix reveals deeper rendering issues.
  → **Mitigation**: Scope the fix to the `permission:` block only. Log any other rendering gaps as findings for a future feature. The `byte-parity` verb documents CONFLICT/PROTECT states, not forces them.
- **Risk**: L1 exit gate (end-to-end loop) fails because of a missing integration not covered by the plan.
  → **Mitigation**: The gate IS the test — if it fails, surface the specific gap, fix it as part of L1, and re-run. Don't proceed to L2 with a failing gate.
- **Risk**: A lead agent's reference spec has an open question or contradiction with the live codebase.
  → **Mitigation**: Resolve in favor of the reference spec (it's the authoritative design). If the resolution is load-bearing, flag for owner under R-008.
- **Rollback**: Every layer is checkpointed. If L1 fails the exit gate, fix L1 — L0 is already validated. If L2-P0 breaks something, revert L2 changes only; L1 is stable. Catalog assets are versioned in git — `git revert` the layer's commits.

## Complexity tracking
No gate-check violations. The plan passes all 4 gates (R-001, R-002, R-005, R-008). No complexity justification needed.

## Decisions needing approval
- **Dynamic-readiness convention**: The three-dial model and "leanest correct path" default are architectural choices that affect every agent's behavior. **Owner approves `DYNAMIC_READINESS.md` at T-08a before L1 agents bake it in** (R-008 gate).
- **Governance subagent design**: The approval ledger path (`.aspis/state/approval-ledger.yaml`) and the protected paths set are load-bearing architecture decisions. The governance signatures MUST match governance.md §6 verbatim — `approve` requires `--approver`, ledger tracks `approver`/`expiry`/`glob_approval`. Owner approves or adjusts the protected paths set.
- **Claude Code adapter fix**: The `permission:` block preservation may require a change to the rendering path (`src/aspis/runtimes/claude.py`). This is the only planned edit to core runtime modules. Owner approves or suggests alternative.
- **L1 exit gate results**: Owner approves the end-to-end loop run at T-32a before any L2 work begins. Hard gate — do not proceed to T-33 without this approval.
