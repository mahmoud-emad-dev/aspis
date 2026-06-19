# F-006 — Tasks

Format: `- [ ] T-NN [US?] <description>`. Mode: **mvp/fast** — large tasks, no task
packets. Commit per `commit-convention.yaml`: `type(F-006/T-NN[..T-MM]): title`.

## P0 — Plan
- [x] T-00 Scaffold + SPEC/PLAN/TASKS + `active_feature.json`

## P1 — Shared deterministic core + git entry points (one build)
- [x] T-01 [US1,US2] `config/hooks.yaml` (data) + `.aspis/scripts/hooks/` core:
  `_git.py`, `scope.py`, `secrets.py`, `commitmsg.py`, `cleanup.py` (junk + .gitkeep),
  `gitignore.py` (Toptal + offline cache) with bundled `ignore/{python,node}.gitignore`,
  `precommit.py`, `postcommit.py`, `install.py`
  (`src/aspis/data/catalog/{config/hooks.yaml,scripts/hooks/*}`)

## P2 — Runtime scope-guard (per-runtime, adapter-emitted)
- [x] T-02 [US3] Wiring sources `runtime-hooks/claude/settings.json` +
  `runtime-hooks/opencode/scope-guard.ts`; `RuntimeAdapter.emit_runtime_hooks` +
  capability; Claude/OpenCode overrides; `write_export` calls it
  (`src/aspis/data/catalog/runtime-hooks/*`, `src/aspis/runtimes/{base,claude,opencode}.py`, `src/aspis/export.py`)

## P3 — CLI + wire + dogfood
- [x] T-03 [US2,US4] Non-blocking enforcement (`enforcement: warn`, auto-fix + report) +
  `aspis gitignore [stack]` command; `config/hooks.yaml` in the base profile; `init` runs
  `install.py` to arm `.git/hooks`
  (`src/aspis/commands/gitignore.py`, `src/aspis/operations/init.py`, `src/aspis/data/profiles/base.yaml`)
- [ ] T-04 Regenerate runtime + install ASPIS's own git hooks (dogfood) — see HANDOFF.md
  (`.aspis/scripts/hooks/*`, `.claude/settings.json`, `.opencode/plugins/scope-guard.ts`, `.git/hooks/*`)

## P4 — Test + document
- [x] T-05 Tests: scope, commitmsg, cleanup (+gitkeep), gitignore (offline), enforcement,
  runtime-hook emission (`tests/test_f006_hooks.py`)
- [x] T-06 Docs: D-010 + ARCHITECTURE hooks layer + ROADMAP Phase 3.5 done
  (`.aspis/context/DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`)
