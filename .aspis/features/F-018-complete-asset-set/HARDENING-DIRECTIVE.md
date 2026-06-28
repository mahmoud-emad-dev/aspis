# Codebase Hardening — OpenCode Directive (unit-by-unit)

> How to continue the unit-by-unit hardening pass the way Claude runs it, using
> OpenCode's agents. Written so a **less-capable model can execute it reliably**:
> deterministic scripts do the heavy lifting, each agent call is **one small
> scoped check**, and a single strong agent makes the final call per unit.
>
> **The prime directive — read this twice:** the goal is NOT to "apply every
> rule." The goal is *reliable, robust, scalable, simple* code. **Default to NO
> change.** Only change on a real defect or a clearly-lean improvement. NEVER add
> complexity, abstraction, strictness, or anything that slows/blocks normal use.
> **Simplicity beats rule-purity.** When unsure whether a change is an
> improvement, DO NOT make it — record it as a finding for Claude to review.

---

## How to run

`project-lead` orchestrates. Take **one unit at a time** from the scorecard
below, run Phases 1–6, commit, report, then stop and pick up the next unit.
Do not batch units. Do not skip the gates.

The unit list (files per unit) is in `Review/E-claude-acceptance-review.md`'s
sibling map and in Claude's scorecard at the bottom of this file.

---

## The method — 6 phases per unit

**Phase 1 — Inventory (cheap agent: `project-explorer`).**
List the unit's files + line counts. Read and quote each file's top docstring.
Output: a file table + the current docstrings. No judgment yet.

**Phase 2 — Deterministic checks (SCRIPTS, no model — R-003).**
Run these and record raw output. They are facts, not opinions:
- `ruff check <unit files>` — lint (line length, dead vars, unused imports, idioms).
- `pytest <unit's test files>` (use `uv run pytest`) — must be green.
- `grep -nE 'runtime ?== ?["'"'"']|profile ?== ?["'"'"']|== ?"(claude|opencode|base)"'` over the
  unit files — **No-Special-Cases** scan (constitution #9).
- `grep -nE '"(claude-|opencode/|deepseek|minimax|glm|gpt-|nemotron)'` — hardcoded
  model strings in logic (should be none outside `data/`).
- `grep -nE '^[A-Z_]+ ?= ?[\[{(]'` — constant collections; candidates that may
  duplicate a YAML/data source (#3 single-source).

**Phase 3 — Per-file judgment checks (cheap agent, ONE check per pass).**
For each check, the agent looks at the unit's files and answers a yes/no with
evidence. Keep each agent call to a SINGLE check so a weak model stays accurate:
- **C-DOC**: does every file have a top docstring that states its *Purpose* and
  is *accurate to what the file actually does* (not stale)? Flag missing/stale.
- **C-DUP**: is any block of logic/dict/shape built in 2+ places (copy-paste)?
- **C-DEADREF**: do comments/docstrings point to files/decisions that don't
  exist (e.g. a transient build-report)? Flag.
- **C-CLEVER**: is anything more complex/clever than the task needs? Flag, but
  remember cleverness that is *the mechanism* (documented) is allowed.
- **C-READ**: could a mid-level engineer read this file top-to-bottom and
  understand it without running it? If not, where does it lose them?

**Phase 4 — Triage (mid agent: `reviewer` at standard depth).**
For every flag from Phases 2–3, label it exactly one of:
- **DEFECT** — wrong/broken/will-break. → fix.
- **LEAN-FIX** — a smaller/clearer/standard-pattern version with no new
  complexity (e.g. extract one helper for a duplicated shape; wrap a long line;
  `raise … from`; modern stdlib idiom; bring a docstring to the 4-part standard).
  → fix.
- **KEEP** — a rule is technically bent but fixing it adds complexity or hurts
  clarity (e.g. an explicit ordered list vs auto-discovery; 3 readable near-twin
  functions vs one clever resolver). → do NOT change; record the reason.
- **DEFER** — real but bigger than a lean fix, or risks a working gate (engine
  refactor, shared-module extraction). → do NOT change; record for Claude/F-019/F-020.

**Phase 5 — Apply + re-gate (builder: `general-builder`/`fix-lead`).**
Make ONLY the DEFECT + LEAN-FIX changes. After each: `ruff check` clean and
`pytest` green on the unit. Tests: add only where there is a real coverage gap;
**clear + covering + FEW** — no bloat, no redundant or over-complex cases. If a
fix can't keep gates green, revert it and relabel it DEFER.

**Phase 6 — Final review (STRONG agent, used ONCE per unit — see costs).**
The strong agent reviews the unit AND the diff against the full criteria
checklist below and against this directive's prime directive. It answers:
1. Are all changes DEFECT/LEAN-FIX only (no new complexity/strictness)?
2. Is every KEEP/DEFER decision justified?
3. Gates green? Docstrings current + accurate? Senior-readable?
Verdict: **PASS** → committer commits (`fix(F-018)…`/`refactor(F-018)…`/`test(F-018)…`,
≤72-char subject, NO AI attribution). **NEEDS-WORK** → back to Phase 4 (max 2 loops,
then record remaining as DEFER and commit what passed). Write a short unit report
in this feature folder.

---

## The full criteria checklist (what the final review compares against)

**Architecture-constitution** (`.aspis/rules/architecture-constitution.md`):
1 Local Change · 2 Plugin First · 3 Single Source · 4 Config over Code ·
5 Core Stable · 6 Dependency Direction (inward) · 7 Discovery over Registration ·
8 Generated Artifacts · 9 No Special Cases (no `if runtime/profile ==`) ·
10 Consistency over Cleverness · 11 Architecture before Features · 12 Portable
(UTF-8 + pathlib + cross-platform). Plus the **Cost-of-Change** test (adding a
feature touches 1–3 files) and **Automation before Intelligence** (a deterministic
job is a script/hook, never an agent).

**File rules**: every file self-explains — a top docstring with **Purpose /
Responsibilities / Does-Not / Used-By** (proportionate: a 6-line dispatcher needs
only a clear Purpose + "Used by"), one concept per file, no hidden globals,
known dependency direction.

**Owner's criteria**: works/reliable/robust · scalable · clean · clear/readable ·
right abstraction · independent (works in any state, never crashes) · minimal
change to extend · dispatch/neutral/plugin/not-hardcoded · configurable later
without a big change · supports the next parts to build · NO over-engineering ·
tests clear+covering+few.

**Senior bar**: code reads like a 15+-year engineer wrote it — current, stable,
market-standard patterns; a junior, mid, or senior engineer (and an AI model)
can all read it and know how it works.

---

## Decomposition for weaker models (why this works)

- **Most checks are deterministic** (ruff, pytest, grep) → run as scripts, $0,
  no model judgment, no hallucination. This is the bulk of the signal.
- **Each judgment agent call is ONE check** over the unit, with a clear
  yes/no + evidence format → a weak model stays in scope and accurate.
- **Triage and final review are where capability matters** → those get the
  stronger model; everything else gets the cheap ones.
- **When uncertain, FLAG don't FIX** → a weak model can't make the code worse;
  Claude reviews the deferred items later.

## Model / agent + cost assignment

| Step | Agent | Model | Why |
|---|---|---|---|
| Deterministic checks | (scripts) | none | facts, no model |
| Inventory, Phase-3 checks | project-explorer / general-builder | **minimax-m3** | cheap, scoped, capable enough |
| Apply fixes | general-builder / fix-lead | **deepseek-v4-pro** | cheap, good at mechanical edits |
| Triage | reviewer (standard) | **deepseek-v4-pro** | labelling against clear rules |
| **Final per-unit review** | reviewer (deep) | **glm-5.2** | the decision gate — most capable; **ONE call per unit** (it's the expensive one, use sparingly) |
| Commit | committer | cheap | message only |

Keep glm-5.2 to the single Phase-6 review per unit. If a unit is tiny and clean
(like #1/#2 were), a weak model may run Phase 6 too and only escalate to glm-5.2
on NEEDS-WORK.

---

## Definition of done (per unit)

- ruff clean on the unit's files · `uv run pytest` green on the unit's tests.
- Every file has a current, accurate Purpose docstring.
- All changes are DEFECT/LEAN-FIX only; KEEP/DEFER items recorded with reasons.
- Final review PASS · committed · one short unit report written.

## Scorecard / where to resume

| Unit | Files | State |
|---|---|---|
| 1 CLI spine & lifecycle | cli, commands/__init__, engine, lifecycle, hooks, resources, paths, project, settings, constants | ✅ done (Claude) |
| 2 Catalog model & transform | catalog, assetkinds, profiles, transform, templating | ✅ done (Claude) |
| 3 Export & runtime adapters | export, export_cmd, manifest, runtimes/{base,opencode,claude} | ✅ done (Claude) |
| 4 Models & detection | models, commands/models, detect, inventory, runtime_inventory | ⏭️ **DEFER to F-019** (detection + tiers being reworked — don't harden now) |
| **5 Project setup** | operations/{init,bootstrap}, commands/{init,bootstrap}, promotion | ⬜ **RESUME HERE** |
| 6 Validation & drift gates | commands/{validate_runtime,validate_index,byte_parity,drift,doctor,preflight}, health | ⬜ |
| 7 Governance & protection | commands/governance, protect, findings, commands/findings, scripts/system/validate-approvals | ⬜ (heavy — expect findings) |
| 8 Git & commit discipline | gitcheck, gitops, commitaudit, commands/{commit,commits,gitignore}, scripts/git, scripts/hooks | ⬜ (F-020 territory) |
| 9 Misc verbs | commands/{artifact,mode,status,context,testledger,uninstall} | ⬜ |
| 10 Agent system (assets) | catalog/{agents,skills,workflows,commands,templates} | ⬜ (Claude swept twice already — low priority) |
| 11 Tier-B scripts | catalog/scripts/{context,planning,research,hooks} | ⬜ |
| 12 Rules & config/policy | catalog/{rules,config}, profiles/base.yaml | ⬜ |
| 13 Tests | tests/ | ⬜ (clarity/coverage pass) |
| 14 Docs / install / brand | docs, README/ROADMAP, install.{sh,ps1}, pyproject, assets | ⬜ |

Units 1–3 set the standard: each was already clean code → the work was mostly
*confirming* it, closing real test gaps, and senior-grade tidy-ups. The heavy
units (7 governance, 5 bootstrap) are where real findings are expected.
