# F-006 — Tasks

Format: `- [ ] T-NN [US?] <description>`. Mode: **mvp/fast** — large tasks, no task
packets. Commit per `commit-convention.yaml`: `type(F-006/T-NN[..T-MM]): title`.

## P0 — Plan
- [x] T-00 Scaffold + SPEC/PLAN/TASKS + `active_feature.json`

## P1 — Shared deterministic core + git entry points (one build)
- [ ] T-01 [US1,US2] `config/hooks.yaml` (data) + `.aspis/scripts/hooks/` core:
  `_git.py`, `scope.py`, `secrets.py`, `commitmsg.py`, `cleanup.py` (junk + .gitkeep),
  `gitignore.py` (Toptal + offline cache) with bundled `ignore/{python,node}.gitignore`,
  `precommit.py`, `postcommit.py`, `install.py`
  (`src/aspis/data/catalog/{config/hooks.yaml,scripts/hooks/*}`)

## P2 — Runtime scope-guard (per-runtime, adapter-emitted)
- [ ] T-02 [US3] Wiring sources `runtime-hooks/claude/settings.json` +
  `runtime-hooks/opencode/scope-guard.ts`; `RuntimeAdapter.emit_runtime_hooks` +
  capability; Claude/OpenCode overrides; `write_export` calls it
  (`src/aspis/data/catalog/runtime-hooks/*`, `src/aspis/runtimes/{base,claude,opencode}.py`, `src/aspis/export.py`)

## P3 — CLI + wire + dogfood
- [ ] T-03 [US2,US4] `aspis gitignore [stack]` command; add hooks assets to base profile;
  post-init lifecycle hook runs `install.py`
  (`src/aspis/commands/gitignore.py`, `src/aspis/cli.py`, `src/aspis/data/profiles/base.yaml`, `.../catalog/hooks/post-init/*`)
- [ ] T-04 Regenerate runtime + install ASPIS's own git hooks (dogfood)
  (`.aspis/scripts/hooks/*`, `.claude/settings.json`, `.opencode/plugins/scope-guard.ts`, `.git/hooks/*`)

## P4 — Test + document
- [ ] T-05 Tests: scope, commitmsg, cleanup (+gitkeep), gitignore (offline), runtime-hook
  emission (`tests/test_hooks_*.py`, `tests/test_runtime_hooks.py`)
- [ ] T-06 Docs: D-010 + ARCHITECTURE hooks layer + ROADMAP Phase 3.5 done
  (`.aspis/context/DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`)
