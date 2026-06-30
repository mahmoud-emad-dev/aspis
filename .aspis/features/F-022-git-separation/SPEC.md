# F-022 — Git separation: shadow brain repo + runtime integrity · Specification

> Mode: **production** — auto-escalated (introduces a new **`git`** subsystem; changes commit
> routing, hook install, and `.gitignore`; touches protected paths and many files). Honors the
> **FIXED** contracts in `initialization.md`, `bootstrapping.md`, and the export-safety guarantees
> (D-022 / F-021). **Storage-separation only** — workflow/branch discipline is deferred to F-023.

## Goal
Stop mixing three different histories in one git. A project carries three kinds of artifact with
three different lifecycles, and each should be versioned (or not) on its own terms:

1. **Product** (`src/`, `tests/`, docs) — the user's real software. Public, clean history.
2. **Brain** (`.aspis/` — architecture, decisions, rules, planning, features, index, context) — the
   AI workspace. Deserves full versioning (diff/blame/restore/branches) but on **its own rules**,
   without polluting the product's commit history.
3. **Runtime** (`.opencode/`, `.claude/`) — rendered from the catalog (catalog is truth). Does not
   need git; needs **integrity + change-detection** (only ASPIS changes it; every change is logged).

After F-022: the product git stays beautiful and private-safe; the brain lives in a **shadow git**
(`.aspis/.git`) it manages itself; the runtime dirs are tracked by **content hashes + an
append-only change-log**, never by git; and machine state / secrets never enter any git.

## Problem
Today everything lives in **one** product git:
- The scaffold `.gitignore` `aspis init` writes does **not** ignore `.aspis/` or the runtime dirs, so
  every user project commits its brain + runtimes into the product history — exposing planned
  features, context, machine state, subscriptions, and routing to anyone who clones the repo.
- System/brain changes (registry rebuilds, context refreshes, routing edits) would land as noise
  commits on the product's feature branches.
- There is **no `git` subsystem of record** — git logic is scattered across `gitops.py`,
  `gitcheck.py`, the 11 hook scripts, and `aspis gitignore`, with no single intent file.
- The runtime integrity record exists only implicitly (the F-021 `export-snapshot.json` +
  `export-log.jsonl`) and is not exposed or formalized as the runtime's change history.

## Scope
In scope (storage separation):
- **Product `.gitignore` + isolation shields.** `aspis init` ensures the product `.gitignore`
  ignores `.opencode/`, `.claude/` (every runtime dir, asked of the adapters), and the brain's
  non-shared parts. Optional shields the user can accept: `.dockerignore` entries, a `.vscode`
  hide/search-exclude, and **documented** CI `paths-ignore` advice (GitHub/GitLab) — ASPIS advises,
  never edits a user's pipeline silently.
- **Shadow brain repo (`.aspis/.git`) with its own rules.** `aspis init` initializes it; it versions
  the whole brain and commits on **brain events** (its own cadence, distinct from the product's
  feature-branch workflow). Its own `.gitignore` excludes machine-local + secret + regenerable state
  (`.aspis/current/`, runtime inventory, subscriptions, sessions, cache, keys) so secrets never enter
  *any* git. Managed entirely by `aspis` verbs — the user never runs git inside `.aspis/` by hand.
- **Runtime integrity record.** Formalize the F-021 snapshot+log as the runtime's change history:
  every ASPIS-made change is logged (already true), out-of-band edits are detected (UNKNOWN/CONFLICT),
  and a read verb (`aspis runtime status`, or an extension of `aspis drift`) reports it. No git.
- **Commit routing.** Brain commits → shadow repo (system-lead / committer); product commits →
  product repo. The committer/system-lead become repo-aware; `commit_owned` and the hooks split
  across the two `.git/hooks` trees.
- **Opt-in shared-slice surfacing.** A mechanism to copy/track *select* brain files into the product
  repo when the user wants collaborators to have them (manual, on demand) — designed minimally.

Out of scope (deferred):
- **F-023 — git workflow discipline** (product side): feature-branch-only commits, never commit on
  `main`, merge-to-main-only-when-done, one commit per completed feature.
- **Migrating THIS dogfood repo** out of product git (a separate, reviewed, history-shaping step).
- Any cloud/remote backup beyond a local `aspis workspace backup`/`restore` stub.

## Open decision (confirm before build)
**Default brain visibility in the product repo.** The owner picked "shared slice — practical" but
also wants a self-ruled `.aspis` shadow git and "share little files later." The proposed resolution:
**default = product git ignores the `.aspis/` brain (the shadow repo owns it); surfacing a chosen
slice into the product repo is opt-in.** If the owner instead wants a fixed shared slice
(architecture/decisions/rules/planning) tracked in the product repo by default, that flips the
`.gitignore` rules and the double-tracking model — so it is the one item to confirm in the
ARCHITECTURE_IMPACT before implementation.

## Success criteria
- SC-1: A freshly `init`ed project never tracks `.opencode/`, `.claude/`, or machine/secret brain
  state in its product git; `git status` after init is clean of them.
- SC-2: `.aspis/.git` exists, versions the brain, and an `aspis` verb commits brain changes there —
  with zero brain commits appearing in the product git.
- SC-3: Every runtime change made by ASPIS is recorded in the append-only log; an out-of-band edit
  to a runtime file is detectable and reported by a read verb.
- SC-4: Secrets / keys / subscriptions / runtime inventory are absent from **both** git histories.
- SC-5: A new `git` subsystem intent file exists; init/bootstrap/installation FIXED contracts and
  the F-021 export-safety guarantees still hold; gates green.
