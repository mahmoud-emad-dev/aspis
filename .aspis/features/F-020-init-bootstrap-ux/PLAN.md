# F-020 — Implementation Plan

> Mode: **production** — full depth. Big-task granularity (the planner also applies).

## Summary
Add the guided first-run experience without breaking the FIXED contracts. The shape is the
two-layer model: keep each **operation** independent (Before→Core→After) and add a thin
**setup-workflow** that sequences them. Insert a read-only **pre-bootstrap resolution** stage that
writes a resumable `.aspis/current/bootstrap_state.json`; make **onboarding** clear (meaning +
example + default per question); make the **bootstrap agent ask/confirm** (never self-decide) and
do a **file-by-file enrichment review**; guarantee the floor with a **deterministic post-bootstrap
self-heal**; make **stack** confidence-driven and correctable; and ensure **init exports the
complete, current asset set**. No model-file changes (F-021 owns the model decision engine; models
frozen). Git two-commit staging is touched lightly; full git re-arch is F-022.

## Technical context
- **Language / version**: Python 3.11+ (engine). Markdown for agent/skill/template assets.
- **Key dependencies**: existing `detect`, `runtime_inventory`, `settings`, `profiles`, `export`,
  `lifecycle` (Engine/Context), `promotion`, `manifest`, `health`, the context scripts.
- **Storage / interfaces**: new `.aspis/current/bootstrap_state.json` (resumable decision state);
  CLI surface on `aspis init` (guided) + small helper verbs (e.g. `aspis stack`); plan files read
  from repo root + `docs/`.
- **Decisions locked (2026-06-29)**: plan-file detection = common name patterns
  (`plan|arch|architecture|spec|prd|roadmap`) in root + `docs/`, formats `.md/.html/.pdf/.txt/.docx`;
  user-rules = a human-editable `.md` at a default-but-configurable path (structured yaml/json is
  the rules subsystem's later job); F-020 mode = production.
- **Constraints**: catalog-first (live dirs regenerated, never hand-edited); **do NOT** run
  `aspis export`/`models --apply` (models frozen); reuse detection modules (no duplication); honor
  every FIXED invariant in `initialization.md` + `bootstrapping.md`; never block automation (`--yes`).

## Gate check
- [x] **R-001 Scope** — within init/bootstrap/pre-bootstrap/onboarding/state + their tests + agent bodies.
- [x] **R-002 Gates** — ruff + pytest + validate-runtime 33/33 stay green each task.
- [x] **R-005 Tests-as-spec** — each big task lands with tests pinning its behavior.
- [x] **R-008 Human gate** — architecture change; the SPEC + `ARCHITECTURE_IMPACT.md` are owner-confirmed (2026-06-29).

## Components
1. **Pre-bootstrap resolution** (new, read-only): project-state machine + runtime/subscription/
   availability inventory + stack-confidence + rule-layer load + plan-file detection → `bootstrap_state.json`.
2. **setup-workflow** (new, thin orchestrator): post-init decision screen, stage sequencing,
   skip/resume, runtime continuation + multi-runtime guidance.
3. **Onboarding UX**: per-question meaning/example/default; mode explanations; colors/progress; non-blocking.
4. **Bootstrap agent + project-onboarding skill**: ask/confirm (never self-decide), read rules, use
   research-lead for stack, read plan file, file-by-file enrichment review.
5. **Stack handling**: confidence model + robust formats + manual fallback + later-correction verb +
   write stack→context+manifest.
6. **Post-bootstrap self-heal** (deterministic): fill/refresh context, FILE_REGISTRY, build history,
   `.gitignore`, stack — expected files only, never invented.
7. **State machine + recovery + resume**: detect 6 states; safe re-init/upgrade; resume interrupted runs.
8. **Init export completeness**: assert the full, current asset set ships; no missing/outdated asset.

## Steps (big tasks — see TASKS.md for the ordered list)
| Step | Files (indicative) | Gate |
|------|--------------------|------|
| Pre-bootstrap layer | `operations/pre_bootstrap.py`, reuse `detect`/`runtime_inventory`/`settings`, `tests/` | state file written read-only; states classified |
| setup-workflow | `operations/` + CLI on `init`, `tests/` | one guided command; skip + resume work |
| Onboarding UX | `operations/bootstrap.py` (prompts), `tests/` | each prompt has meaning+example+default; non-blocking |
| Bootstrap agent | catalog `agents/bootstrap.md`, `skills/project-onboarding/` | asks/confirms; reads rules/plan; research-lead path |
| Stack handling | `detect.py` + a stack verb + `tests/` | confidence; manual fallback; later correction |
| Post-heal | `operations/` post-stage + context scripts, `tests/` | weak-agent run still ends non-skeleton |
| State machine | `detect.py`/`project.py` + guards, `tests/` | existing `.aspis`/code never destroyed; resume |
| Export completeness | `export`/`init` check + `tests/` | no missing/outdated asset shipped |
| Gates + E2E | `tests/` | full acceptance green; no model files changed |

## Verification
```bash
uv run ruff format --check src tests && uv run ruff check src tests
uv run pytest -q
uv run aspis validate-runtime --runtime all      # 33/33
git diff --name-only main -- 'src/aspis/data/catalog/config/*model*' 'src/aspis/data/catalog/config/models.yaml'  # MUST be empty (models frozen)
```

## Risks & rollback
- **Risk**: scope sprawl into models/git → mitigated by hard out-of-scope (F-021/F-022) + the
  models-frozen check in Verification.
- **Risk**: breaking a FIXED invariant → mitigated by re-reading the subsystem FIXED blocks before
  each task + the E2E acceptance.
- **Risk**: guided flow blocks automation → mitigated by non-blocking defaults + `--yes` test.
- **Rollback**: isolated branch `feature/F-020-init-bootstrap-ux`; revert per task; no export/live
  deploy, so deployed projects are untouched until re-init.

## Decisions needing approval (R-008)
- Confirmed via the Architecture Impact (2026-06-29): pre-bootstrap stage + `bootstrap_state.json`;
  bootstrap-asks-not-decides; post-heal = deterministic-restore-only; setup-workflow as a new
  subsystem; model engine = F-021, git = F-022.
