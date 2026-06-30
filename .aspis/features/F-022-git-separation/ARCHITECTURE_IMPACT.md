# F-022 — Architecture Impact Report

> Recorded by planning when a feature changes a subsystem's intent (responsibilities,
> boundaries, lifecycle, integrations, or contracts — or adds/removes a subsystem).
> **NOT auto-applied:** project-lead confirms this with the user before any subsystem
> file under `.aspis/architecture/subsystems/` is updated.

## Affected subsystem(s)
- **`git`** — **NEW** (introduces the subsystem of record for version-control policy).
- `initialization` — EXISTING (init now writes the product `.gitignore` shields + stands up the
  shadow repo; today it does `git init` + one product commit).
- `bootstrapping` — EXISTING (bootstrap's commit + self-clean must route to the correct repo).
- `installation` — EXISTING (hook install splits across the product and shadow `.git/hooks` trees).

## Reason
ASPIS conflates three histories in one product git. The brain (architecture/planning/rules/decisions)
deserves real versioning but on its own cadence; the runtime dirs are catalog-rendered and only need
integrity + a change-log; and machine state / secrets must never reach a public repo. A single `git`
subsystem must own *which artifact is versioned where, by which rules, and what never gets committed*.

## Summary of the architectural change
- **Current:** No `git` subsystem. One product git tracks everything; the scaffold `.gitignore`
  ignores neither `.aspis/` nor the runtime dirs; system/brain changes would pollute product history;
  runtime integrity is an implicit side effect of the F-021 export snapshot/log.
- **Proposed:** A `git` subsystem with three lanes —
  1. **Product git** (`.git/`) — product source only; clean, public-safe; follows the F-023 workflow
     rules (branches/features, never `main` directly) once that lands.
  2. **Brain shadow git** (`.aspis/.git/`) — versions the brain, commits on **brain events** (its own
     rules, distinct from the product workflow), never auto-pushed, its own `.gitignore` for
     local/secret/regenerable state.
  3. **Runtime integrity** — `.opencode/`/`.claude/` are git-ignored and tracked by content hashes +
     an append-only change-log (formalized F-021 snapshot/log); a read verb reports drift. No git.
  Plus isolation shields (`.dockerignore`, `.vscode`, documented CI `paths-ignore`) and an opt-in
  mechanism to surface select brain files into the product repo.
- **Fixed vs changed:**
  - **FIXED (must not break):** init still produces a working project offline; bootstrap's
    self-erase + single first commit still happen (now in the right repo); catalog → runtime parity
    moat; F-021 export-safety (models frozen, bootstrap-aware) untouched; secrets never committed.
  - **Changed:** the scaffold `.gitignore` content; `commit_owned`/committer become repo-aware; hook
    install targets two `.git/hooks` trees; a second (shadow) git is created and managed by ASPIS.

## Integration impact
- **initialization:** `init_core` gains: write product `.gitignore` shields, `git init .aspis` shadow
  repo + its `.gitignore`, route init's first commit to the correct repo(s). Must stay offline/idempotent.
- **bootstrapping:** the separate bootstrap commit + `_self_clean`/`_strip_bootstrap_prose` must
  target the repo that owns each file (brain → shadow; runtime strips are filesystem, not commits).
- **installation:** `scripts/hooks/install.py` installs into both `.git/hooks` trees; the scope-guard
  / secret-scan / commitmsg hooks gain a repo context (product vs brain rules differ).
- **export / runtime integrity:** the F-021 `export-snapshot.json` + `export-log.jsonl` become the
  named runtime change record; a read verb surfaces it. Export behavior itself is unchanged.
- **`aspis gitignore`:** must coexist with the new ASPIS-managed ignore block (stack ignores vs the
  brain/runtime shields).

## Questions needing user confirmation
1. **Default brain visibility (the one real fork):** product git **ignores the whole `.aspis/` brain**
   (shadow owns it; surfacing a slice is opt-in) — *proposed* — **or** a fixed shared slice
   (architecture/decisions/rules/planning) is tracked in the product repo by default (double-tracked
   with the shadow). Which is the default?
2. **Shadow repo location:** `.aspis/.git` directly (proposed, simplest) vs `.aspis/workspace/.git`
   (separates exported project-assets from workspace-state, per the Gemini refinement)?
3. **Auto-commit cadence for the brain shadow repo:** which "brain events" trigger a shadow commit
   (e.g. after a planning artifact is written, after architecture-memory update, after a context
   rebuild), and is it automatic or only via an explicit `aspis` verb?
4. **Shields scope:** do we write `.dockerignore` + `.vscode` excludes by default, or only on
   opt-in? (CI `paths-ignore` stays documentation-only.)
