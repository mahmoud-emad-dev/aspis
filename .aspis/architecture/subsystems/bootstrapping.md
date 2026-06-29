# Subsystem: bootstrapping

- **Status:** active
- **Created:** 2026-06-29   **Last reviewed:** 2026-06-29
- **One-liner:** The one-time, self-erasing setup that turns an initialized skeleton into a live, self-explaining project — run once, remembered forever, then it removes itself.

## Why it exists (problem)
`aspis init` produces a structurally complete project, but it is not yet *live*: the brain has no
identity/architecture, the leads are not active, and no agent has project-specific context.
Without a one-time onboarding, every project would start generic and every session would re-ask
the basics. Bootstrapping is the polished first-run setup (like an app's first-login): it asks a
few questions, makes the project live, then **erases its own machinery** so no agent ever asks
about bootstrap again. This subsystem has repeatedly been the victim of drift — later features
(notably the F-016 agent-system rewrite) silently broke its detection/handoff — which is exactly
why its intent is recorded here as a fixed baseline.

## Responsibilities & boundaries
- **Owns:** collect project details (name, goal, stack, plan, mode) interactively or via
  flags/`--yes`; fill the `AGENTS.md`/`CLAUDE.md` slots init left; write `.aspis/manifest.json`
  (the live signal); trigger the first brain fill via the project's own context scripts; promote
  the leads to exactly **5 primaries**; **self-erase** the onboarding package (the `bootstrap`
  agent, the `project-onboarding` skill, the `workflows/bootstrap.md` doc) and strip the bootstrap
  gate prose once live; commit its fill as a separate commit; gate go-live on a health check.
- **Does NOT own:** planning or building features; model selection (models-intelligence);
  **editing catalog-managed agent bodies** (the parity moat forbids it — self-erasure works on the
  *deployed* copies via markers, never the catalog source); any autonomous file writing *after*
  bootstrap (post-bootstrap, files change only when the user asks).

## Current behaviour (FIXED vs OPEN)
The entry agent (`project-lead`) detects not-live on its first action (`aspis bootstrap --check`;
the signal is `.aspis/manifest.json`) and **delegates to the `bootstrap` agent** — it must
delegate, never self-run (`aspis bootstrap --write` is denied to project-lead by design). The
`bootstrap` agent ships `export_scope: export-only`, `mode: primary`. `operations/bootstrap.py`:
a TTY-guarded, flag-overridable, **non-blocking** wizard (`_collect`) gathers **name** (default =
dir), **goal**, **stack** (auto-detected + normalized), **plan** (optional), **mode** (default
`production`); fills `_DEFN_SLOT`/`_STACK_SLOT`; writes the manifest; runs the project's context
scripts to fill the brain; `_readiness` requires a non-skeleton `ARCHITECTURE.md` for
existing-code projects (greenfield exempt); promotes 5 primaries (`project-lead` + planning /
build / reviewer / system — D-004). **Self-erase:** `BOOTSTRAP-GATE` markers +
`_strip_bootstrap_prose` remove the gate block and bootstrap frontmatter from
`AGENTS.md`/`CLAUDE.md`/`project-lead.md` across every runtime dir once a green go-live run
completes; the rendered OpenCode `bootstrap: allow` task entry self-strips via the frontmatter
regex; the onboarding package files are deleted. Pre/post staging (gating, commits, self-clean) is
registered on the lifecycle engine separately from the core.
- **FIXED (must not break — this is the don't-break contract for F-020):**
  1. Runs **once**, remembered forever via the durable manifest; `--check` is the deterministic signal.
  2. **Non-blocking by default** (D-BW3 / T-INTERACTIVE): every prompt has a default that needs no
     human; `--yes`/flags drive it headless — never block CI/automation on a question.
  3. `project-lead` **delegates to the `bootstrap` agent; it never self-runs** the denied command.
  4. Self-erasure must **NOT** edit catalog-managed agent bodies (parity moat, BT-1): it strips the
     deployed copies via markers and removes an `export-only` package — the catalog stays pure.
  5. Enrich **only from detected facts + templates** — never invent (bounded autonomy, D-B6).
  6. **Post-bootstrap: no autonomous writes** — files change only on the user's request.
  7. Exactly **5 primaries** (D-004); the project ends with **zero bootstrap residue**.
- **OPEN (free to evolve):** the question set (today: name/goal/stack/plan/mode); ephemeral
  bootstrap *agent* vs command+skill; interactive depth (fast vs full Q&A); two-commit pre/post
  staging; rules-file seeding (must route through governance R-008 for any later change).

## Integrations
- **After initialization** (consumes its skeleton + slots). **catalog-to-runtime:** the gate
  prose and the `bootstrap` delegate live in the catalog and are stripped from the *deployed*
  files at go-live — so a change to the gate ripples into `project-lead`, `AGENTS.md`, `CLAUDE.md`.
  **models-intelligence:** the `mode` answer feeds downstream rigor/gating. **promotion:** the
  5-primary step. **The brain context scripts:** bootstrap triggers them for the first fill. A
  change to the agent roster or the strip markers can silently break detection (it has before).

## System contracts (guarantees)
After a green bootstrap: project **mode** and **stack** are confirmed; the brain is **non-skeleton**
(identity + `ARCHITECTURE.md` present); the `AGENTS.md`/`CLAUDE.md` slots are filled; the
onboarding package and bootstrap gate are **removed** (no residue, no agent re-checks); the
manifest records the project is live; there is a separate bootstrap commit; the health gate is
green; exactly 5 primaries are active; **the project is ready for planning**.

## Future direction (F-020 — re-arch; the new vision, not yet built)
Realize the full self-erasing model cleanly: bootstrap as an **Operation** (Before → Core → After)
orchestrated by the **Workflow** layer (so the user just runs `aspis init` and is guided into
onboarding → import → bootstrap → ready, with **resume** of an interrupted run). "Before" validates
init + commits it if uncommitted (two-commit staging); "After" does heavy validation (nothing
missing, git/test/trace hooks) before the real system starts. Keep the instruction **decoupled
from catalog agent bodies** (BT-2 option A: a removable overlay / the export-only agent) so erasure
never risks parity. Optionally a dedicated **ephemeral bootstrap agent**; richer enrichment;
**opt-in** interactive depth (fast defaults vs full Q&A) — fast path stays non-interactive.
Rules seeding stays a one-time, user-confirmed seed; all later changes go through governance.

## Changelog (append-only, newest last; ARCHITECTURE changes only)
- 2026-06-29 — Intent recorded (F-019) as the baseline before F-020. Sources: original ASPS
  vision (REFACTOR-ANALYSIS §BT / B1–B9, BOOTSTRAP-UX-PLAN, BOOTSTRAP_CONTRACT) + as-built
  `operations/bootstrap.py`. **History of breakage this file exists to prevent:** (a) the F-016
  agent-system rewrite DROPPED project-lead's bootstrap-detection instruction (it survived only as
  a silent permission) → project-lead skipped onboarding; **restored** as a marker-wrapped
  self-stripping first-action gate (commits 90777f4 / ce7fba0). (b) On OpenCode the project-lead
  could not delegate to the `bootstrap` agent (not in its task roster) and tried to self-run the
  deny-floored `aspis bootstrap --write` → **fixed** by adding `bootstrap` to project-lead's
  delegates + delegation-only gate prose (commit 32b0342).
