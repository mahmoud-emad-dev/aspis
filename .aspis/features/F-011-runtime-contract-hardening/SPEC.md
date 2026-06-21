# F-011 — runtime-contract consolidation & pre-models hardening · Specification

Mode: **mvp** — focused rigor, built directly, committed per unit.

> Numbered F-011 but intended to run **before** F-010 (models). F-010 stays
> reserved for the models/routing work. Feature numbers are IDs, not execution order.

## Goal

Act on the pre-models full-repo audit. The audit confirmed ASPIS is modular, clean,
and degrades well; the gaps are specific, not structural. This feature closes them so
that the next runtime can be added or the project renamed with a **one-place change**,
the enforcement gates are actually tested, and the remaining correctness/portability/
drift misses are gone — leaving a clean base for the models work.

Findings, grouped:

1. **Abstraction / one-place runtime change.** Three core modules reinvent the
   `.<runtime>` dir convention instead of asking the adapter, and two more hardcode
   runtime identity (`if "claude" in ...`, `_MODE_RUNTIME = "opencode"`). `RUNTIMES`
   in `constants.py` / `settings.py` is a dead third source of "which runtimes exist"
   (the real sources are profiles + `available_runtimes()` auto-discovery).
2. **Correctness.** Two planning skills point at the old flat `.aspis/templates/SPEC.md`
   / `PLAN.md`; templates now live under `templates/planning/`.
3. **Portability (Constitution rule 12).** Two `subprocess.run(..., text=True)` reads
   omit `encoding="utf-8", errors="replace"` — the hazard the rest of the code fixes.
4. **Testability (R-005).** Three rule-enforcing gates ship untested: `secret_scan.py`,
   `precommit.py` (R-009 protected-paths), `runtime_guard.py` (tool-use veto). Plus
   `install.py`, `postcommit.py`'s never-fail guarantee, and the doctor FAIL branch.
5. **Doc/config drift.** `constitution-checks.yaml` is framed as machine-readable but
   nothing reads it; `commit-convention.yaml` has a stale header + unconsumed keys;
   `base.yaml` has vestigial empty `hooks:`/`scripts:` keys; the agent `model:` key
   holds a *tier* and reads like a vendor pin (rename is an R-008 change — confirm first).

## Scope

### Allowed
- `src/aspis/runtimes/**` — extend the `RuntimeAdapter` contract.
- `src/aspis/{detect,assetkinds,promotion,constants,settings}.py` — route through the contract; drop the dead source.
- `src/aspis/operations/{init,bootstrap}.py`, `src/aspis/hooks.py` — root-guide via capability; portability fixes.
- `src/aspis/data/catalog/skills/**` — fix the dangling template paths.
- `src/aspis/data/catalog/config/**` — doc/config drift.
- `.aspis/context/ARCHITECTURE.md`, `DECISIONS.md` — record the contract change (as-built + why).
- `tests/**` for every behaviour change; `.aspis/features/F-011-*/**` feature docs.
- Regenerated `.claude/`/`.opencode/` only via dogfood (`aspis` regenerate), never hand-edited.

### Forbidden
- `rules/**`, permission configs — R-009 human gate (raise, don't edit).
- The `model:` → `tier:` rename (T-12d) is an R-008 architecture change — **confirm with the user before doing it**; otherwise leave a flagged note only.
- Tracing spine, dashboard — out of scope.

## Acceptance
- Adding/renaming a runtime is a one-file change: no module reconstructs `f".{runtime}"`,
  names a runtime literal for root guides, or hardcodes the mode runtime.
- One source of truth for "which runtimes exist".
- The three enforcement gates have deterministic tests.
- Every change covered by tests; full gate (`ruff format --check`, `ruff check`, `pytest`)
  green on **Windows** (the gate of record). Atomic, human-authored commit per task.
