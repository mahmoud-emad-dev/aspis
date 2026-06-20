# F-008 — Tasks

Format: `- [ ] T-NN [US?] <description>`. Mode: **mvp/fast**. Commit per
`commit-convention.yaml` with `aspis commit`.

## P0 — Plan
- [ ] T-00 Scaffold + SPEC/PLAN/TASKS + `active_feature.json` → F-008

## P1 — Fix the two F-007 findings
- [ ] T-01 [US3] Attribution blocklist → phrase/context-aware (allow `.claude`/`.opencode`
  dir mentions); stop tracking generated brain indexes (`.gitignore` + `git rm --cached`)
  (`src/aspis/data/catalog/config/commit-convention.yaml`,
  `src/aspis/data/catalog/scripts/hooks/commitmsg.py`, `.gitignore`, `tests/test_commitmsg.py`)

## P2 — CI
- [ ] T-02 [US1] `.github/workflows/gate.yml` — ruff + pytest on Windows + Linux matrix
  (`.github/workflows/gate.yml`)

## P3 — Docs
- [ ] T-03 [US2] Fix README (`.aspis`, real CLI); add `docs/QUICKSTART.md`
  (`README.md`, `docs/QUICKSTART.md`)

## P4 — Worked example + merge
- [ ] T-04 [US4] A small worked example + `docs/FIRST-BUILD.md`; D-012; gate; merge to main
  (`examples/**`, `docs/FIRST-BUILD.md`, `.aspis/context/DECISIONS.md`)
