# F-007 — Tasks

Format: `- [ ] T-NN [US?] <description>`. Mode: **mvp/fast** — large tasks, no task
packets. Commit per `commit-convention.yaml`: `type(F-007/T-NN[..T-MM]): title`.

## P0 — Plan
- [ ] T-00 Scaffold + SPEC/PLAN/TASKS + `active_feature.json` → F-007

## P1 — The commit tool
- [ ] T-01 [US1,US2,US3] `scripts/git/compose.py` (compose + self-validate reusing
  `commitmsg.validate`); `commands/commit.py` (`aspis commit`: stage explicit paths →
  compose → `git commit`, never `-A`, never push); register the verb in
  `commands/__init__.py`
  (`src/aspis/data/catalog/scripts/git/compose.py`, `src/aspis/commands/commit.py`,
  `src/aspis/commands/__init__.py`)

## P2 — The agent surface
- [ ] T-02 [US1,US4] Enrich `agents/committer.md` to commit via `aspis commit`; add the
  three skills (`commit-message`, `commit-splitting`, `clean-tree-precondition`) and ship
  them in the base profile
  (`src/aspis/data/catalog/agents/committer.md`,
  `src/aspis/data/catalog/skills/{commit-message,commit-splitting,clean-tree-precondition}/SKILL.md`,
  `src/aspis/data/profiles/base.yaml`)

## P3 — Tests
- [ ] T-03 Tests: compose validity (task / span / scopeless), `Tasks:` trailer,
  attribution rejection, explicit-path commit in a temp repo, no-paths refusal
  (`tests/test_commit.py`)

## P4 — The why + docs
- [ ] T-04 D-011 + ARCHITECTURE git section + ROADMAP Phase 3.6 done
  (`.aspis/context/DECISIONS.md`, `.aspis/context/ARCHITECTURE.md`, `.aspis/context/ROADMAP.md`)

## P5 — Dogfood + merge
- [ ] T-05 Regenerate runtime (live committer/skills carry F-007); gate green; merge to
  main (`--no-ff`)
  (`.aspis/**`, `.claude/**`, `.opencode/**`)
