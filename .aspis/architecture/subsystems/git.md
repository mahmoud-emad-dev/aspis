# Subsystem: git

- **Status:** active
- **Created:** 2026-06-30   **Last reviewed:** 2026-06-30
- **One-liner:** The version-control policy of ASPIS — which artifact is versioned where, by which rules, and what must never be committed — keeping the product's git history clean while the AI workspace keeps a full history of its own.

## Why it exists (problem)
A project carries three kinds of artifact with three different lifecycles, and mixing them into
one git history is the core sin this subsystem prevents. Without a policy: the brain (plans,
context, decisions, routing) and the runtime dirs land in the product's public history — leaking
what is planned and what the machine runs — and every internal ASPIS update becomes commit noise
on the user's feature branches. The product's history should read as *its* story (features, fixes);
the AI workspace deserves real versioning (diff/blame/restore) but on its own terms; and the
runtime dirs, being catalog-rendered, need integrity not git. One subsystem owns that split.

## Responsibilities & boundaries
- **Owns:** the three-lane model and the routing between them — the **product** repo (`root/.git`),
  the **brain shadow** repo (`.aspis/.git`), and the **runtime-integrity** lane (no git); the
  product `.gitignore` shields that hide `.aspis/` and the runtime dirs; the brain shadow repo's
  lifecycle (create, commit on brain events, its own `.gitignore` for generated/local/secret); the
  commit-routing rule (`gitops.commit_owned` → brain to shadow, root guides to product, runtime to
  neither); and the legacy-safety guard (never auto-shadow a project whose product repo already
  tracks the brain).
- **Does NOT own (out of scope):** the product-side workflow discipline — feature-branch-only
  commits, never committing on `main`, one-commit-per-feature, merge gates (that is **F-023**); the
  runtime *content* decisions (export/parity own those — this subsystem only says runtime dirs are
  not git-tracked); secret *detection* (the secret-scan hook); stack-specific ignore bodies
  (`aspis gitignore`); the explicit migration of an existing single-repo project (a separate step).

## Current behaviour (FIXED vs OPEN)
`aspis init` writes the product `.gitignore` with a shields block (`.aspis/`, plus each target
runtime dir, e.g. `.opencode/`/`.claude/`), then — on a fresh project only — `git init`s the brain
shadow repo at `.aspis/` (`gitops.init_brain_repo`), whose own `.gitignore` (the seeded
`brain.gitignore`) excludes generated indexes, the export snapshot/log, inventory, traces, and
caches. Init's first commit is **routed**: the brain to the shadow repo, the root guides
(`AGENTS.md`/`CLAUDE.md`/`.gitignore`) to the product repo, and the runtime dirs to neither. Both
repos get their own independent `chore: initialize ASPIS project` commit. Bootstrap's fill commit
reuses the same `commit_owned` router, so it lands in the right lane for free. Two verbs expose the
lanes to the build loop: **`aspis brain`** (`status`/`commit`/`log` on the shadow repo — the commit
the loop calls on a brain event) and **`aspis runtime status`** (the runtime change-log + hash count,
read-only, no git).
- **FIXED (must not break):**
  1. **Product history never carries brain or runtime noise** — `.aspis/` and the runtime dirs are
     git-ignored by the product repo; only product source + the small root guides are tracked there.
  2. **The brain keeps full versioning** in `.aspis/.git` (diff/blame/restore/branches), on its own
     event-based cadence — never auto-pushed.
  3. **Runtime dirs are tracked by neither git** — they are catalog-rendered and covered by the
     export snapshot (hashes) + append-only change-log (the runtime-integrity lane).
  4. **Secrets / machine state never enter any git** — the brain shadow `.gitignore` excludes
     local/secret/generated state, so a backup/push of the brain repo cannot leak them.
  5. **Legacy safety** — a project whose product repo already tracks `.aspis` is never auto-converted
     to a shadow repo (would create a gitlink); it waits for the explicit, reviewed migration.
  6. **Offline + deterministic** — all of the above runs with local git, no network, idempotent.
- **OPEN (free to evolve):** whether `AGENTS.md`/`CLAUDE.md` stay product-owned or move to the brain;
  the exact brain-commit events and whether a CLI verb or an automatic hook triggers them; the
  opt-in mechanism for surfacing a chosen brain slice into the product repo; whether the brain shadow
  repo gets its own hooks (e.g. secret-scan); backup/restore + optional private remote for the brain.

## Integrations
- **initialization:** `init_core` writes the product shields and stands up the shadow repo before the
  routed first commit (`_init_brain_repo` + `_write_root_files`).
- **bootstrapping:** its single fill commit and self-clean route through `commit_owned`; runtime
  strips are filesystem edits (no commit), brain/root edits land in their lanes.
- **export / runtime-integrity:** the F-021 `export-snapshot.json` + `export-log.jsonl` are the
  runtime change record this subsystem points at instead of git.
- **installation (hooks):** product hooks live in `root/.git/hooks`; the brain shadow repo's hooks
  are a future addition. **`aspis gitignore`:** maintains stack blocks beside (never over) the
  shields block.
- A change to the owned-paths split or the shields ripples into both init and bootstrap commits.

## System contracts (guarantees)
After `aspis init` on a fresh project: the product `.gitignore` shields `.aspis/` and every target
runtime dir; a brain shadow repo exists at `.aspis/.git` with the brain committed to it; the product
repo tracks only source + root guides; the runtime dirs are tracked by no git; and no secret or
machine-local state is present in either history. On a legacy project, none of the shadow machinery
is forced — the project is left untouched pending migration.

## Future direction (optional)
F-023 adds the product-side workflow discipline (feature branches, no commits on `main`,
one-commit-per-feature, merge gates) on top of this storage split. Later: brain backup/restore and an
optional private remote; brain-repo hooks; and the opt-in shared-slice surfacing for collaboration.

## Changelog (append-only, newest last; ARCHITECTURE changes only)
- 2026-06-30 — Subsystem created (F-022, storage separation). Introduced the three-lane model
  (product repo / brain shadow repo / runtime-integrity), the product `.gitignore` shields, the
  `.aspis/.git` shadow-repo lifecycle, and commit routing in `gitops.commit_owned` (brain → shadow,
  root guides → product, runtime → neither) with a legacy-safety guard. Workflow discipline and the
  this-repo migration deferred (F-023 / separate step). See `.aspis/features/F-022-git-separation/`.
- 2026-06-30 — F-022 Stage B: added the build-loop verbs — `aspis brain` (status/commit/log on the
  shadow repo) and `aspis runtime status` (read the runtime change-log + hash count). These make the
  two non-product lanes usable during the loop without exposing the shadow git plumbing.
