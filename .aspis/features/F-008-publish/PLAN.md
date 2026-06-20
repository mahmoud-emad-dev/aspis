# F-008 — v0 publish-readiness · Plan

Mode: **mvp**. Branched from `main` (… → F-007). Built directly, committed per unit with
`aspis commit`, gate green at each step.

## Build order
1. **T-01 — fix the two findings first** (so the rest of F-008 commits stay clean):
   - *Attribution*: replace bare model tokens in `commit-convention.yaml`'s
     `forbid_attribution` with attribution **phrases** (`co-authored-by`, `generated with`,
     `ai-generated`, `🤖`) plus model-name-in-attribution patterns; update
     `commitmsg.py` to apply them so `.claude`/`.opencode` dir mentions pass. Test it.
   - *Brain churn*: `git rm --cached` the generated indexes (CURRENT_STATE, RECENT_CHANGES,
     CODE_MAP, FILE_REGISTRY) and add them to `.gitignore`; they keep regenerating locally.
2. **T-02 — CI**: `.github/workflows/gate.yml` — matrix `{windows-latest, ubuntu-latest}`,
   `astral-sh/setup-uv`, `uv sync`, then the three gate steps. Push + PR triggers.
3. **T-03 — docs**: fix README (`.aspis`, real CLI, link quickstart); add
   `docs/QUICKSTART.md` (clone → uv sync → init → bootstrap → the loop).
4. **T-04 — worked example + merge**: a small `examples/<name>/` + `docs/FIRST-BUILD.md`
   showing the loop and the with/without-ASPIS difference; gate; merge to main (`--no-ff`).

## Reuse / principles
- The attribution fix keeps rules as **data** (Config-over-Code); the brain-churn fix is
  the constitution's **Generated Artifacts** rule applied to ourselves.
- CI mirrors the exact local gate; no new tooling.
- Everything stays cross-platform (rule 12 / C-PORTABLE).

## The why + docs
- `DECISIONS.md`: **D-012** — generated brain indexes are not tracked (Generated Artifacts);
  attribution is matched by phrase, not bare runtime name.
- `ROADMAP.md`: note v0 publish-readiness (F-008) and the deferred backlog.

## Risks
- *Untracking brain files* could surprise agents that read them on a fresh clone → they
  regenerate on `init`/post-commit; document it in the quickstart.
- *CI on Windows* must use the same UTF-8-safe paths the scripts now guarantee (rule 12).
