# F-007 — Git subsystem · Plan

Mode: **mvp**. Branched from `main` (F-004 → F-005 → F-006). Built directly by the
planning lead + builder (no task packets), committed per unit, gate green at each step.

## Shape

The enforcement wall exists (F-006). F-007 adds the authoring side over it:

```
.aspis/scripts/git/
  compose.py        # FR-001 compose type(scope): title + bullets + Tasks trailer;
                    #         self-validate by reusing scripts/hooks/commitmsg.validate
src/aspis/commands/
  commit.py         # FR-002 `aspis commit` — stage explicit paths → compose → git commit
  __init__.py       # register the verb (COMMAND_MODULES)
src/aspis/data/catalog/
  agents/committer.md                       # FR-004 enriched: aspis commit is its commit path
  skills/commit-message/SKILL.md            # FR-005 how to compose
  skills/commit-splitting/SKILL.md          # FR-005 one logical change per commit
  skills/clean-tree-precondition/SKILL.md   # FR-005 start clean
src/aspis/data/profiles/base.yaml           # ship the three skills
```

`scripts/git/` ships automatically (init's `_ship_scripts` copies every group under
`catalog/scripts/`). `compose.py` reaches its sibling validator by adding
`scripts/hooks/` to `sys.path` (the same self-contained pattern the hooks use), and
degrades gracefully if the hook module is absent (the commit-msg hook still validates).

## Reuse (DRY)
- `commit-convention.yaml` (F-005) — the only message-rule source.
- `scripts/hooks/commitmsg.validate()` (F-006) — the only validator; compose calls it.
- `scripts/hooks/_git.py` (F-006) — git state (root, staged, branch) where needed.
- The existing `committer` agent (F-004) — enriched, not replaced.

## Build order
1. **P1 — the tool.** `compose.py` (+ self-validate), `commands/commit.py`, register verb.
2. **P2 — the agent surface.** Enrich `committer.md`; the three skills; ship in base.
3. **P3 — tests.** `tests/test_commit.py` (compose validity, span/trailer, explicit-path commit).
4. **P4 — the why + docs.** D-011, ARCHITECTURE git section, ROADMAP Phase 3.6 done.
5. **P5 — dogfood + merge.** Regenerate runtime so the live committer/skills carry F-007;
   gate green; merge to main (`--no-ff`).

## Risks / mitigations
- *Cross-dir import fragility* → compose self-validate is best-effort; the commit-msg
  hook remains the hard validator at commit time, so a missing import never lets a bad
  message through.
- *Hooks fire during our own commits* (this repo is dogfooded, warn mode) → expected;
  they auto-fix and report without blocking. Keep commits convention-clean regardless.
- *post-commit churn* (context refresh / gitignore touch files after commit) → check the
  tree after each commit and fold any generated drift into the same logical unit.

## The why + docs
- `DECISIONS.md`: **D-011** — the committer is the single commit authority and commits
  through `aspis commit`, which composes per `commit-convention.yaml` and lets the F-006
  hooks enforce; agent composes, tool builds, hooks enforce. Push/worktrees deferred.
- `ARCHITECTURE.md`: a Git section (commit authority + the three-layer split).
- `ROADMAP.md`: Phase 3.6 (F-007) → Done on merge.
- `active_feature.json` → F-007 (at scaffold).
