---
name: project-onboarding
description: Use to take a freshly exported project from files-on-disk to a live, self-explaining ASPIS project in one turn — detect, run the deterministic bootstrap, enrich only the judgment files from detected facts, verify it is fully filled and ready, and let the package self-clean. The procedure the bootstrap agent follows.
---

# Project Onboarding

## Purpose

Turn an *exported* project into a *live* one with a complete brain, the right agents
active, and a clean first commit — so any agent that runs afterward finds nothing
missing. Deterministic-first: the CLI does the mechanical work; you add only the
judgment a script cannot.

## When to use

The first message in a project where `aspis bootstrap --check` exits non-zero. Run
this before any feature work; never plan, build, or review an un-bootstrapped project.

## Procedure

1. **Detect.** Run `aspis bootstrap` (dry-run). Note the detected name, stack, git
   state, runtimes, and whether the folder is empty or already has real code.
2. **Confirm or skip.** Surface the detected name / goal / stack. Proceed with them;
   never block. With `--yes` or no TTY, take the defaults as-is.
3. **Run the spine.** `aspis bootstrap --write`. It:
   - fills the AGENTS.md / CLAUDE.md slots left by init,
   - writes `.aspis/config/project.yaml` (mode) and `.aspis/manifest.json`,
   - promotes the four leads to primary (→ exactly five primaries),
   - seeds the brain via `.aspis/scripts/context/update.py`,
   - makes the init-scaffold commit and the bootstrap commit,
   - runs `aspis doctor` and self-cleans the transient package.
   Read its output; if it reports a FAIL, stop and report rather than papering over it.
4. **Enrich (only what needs judgment, only from facts).**
   - **Goal:** if the user gave no goal and the slot is the placeholder, infer a
     one-line goal from the README, package metadata, or detected stack — and pass it
     back through `--goal` on a RESUME run rather than hand-editing if possible.
   - **Architecture:** if `.aspis/context/ARCHITECTURE.md` is still the skeleton,
     draft it from the real directory layout and the detected stack — structure and
     responsibilities only, no invented design.
5. **Verify (the "fully filled and ready" gate).**
   - `aspis bootstrap --check` exits 0.
   - `aspis doctor` shows no FAIL.
   - `.aspis/index/FILE_REGISTRY.yaml`, `.aspis/index/CODE_MAP.md`, and
     `.aspis/context/CURRENT_STATE.md` exist and are non-empty.
   - Exactly five `mode: primary` agents.
   - The working tree is clean.
6. **Finish.** Confirm `bootstrap.done` is recorded and the bootstrap package
   (agent + this skill + the bootstrap workflow) has been removed. Hand back a
   one-line readiness summary.

## Bounded autonomy

Write **only** under `.aspis/`, `.opencode/`, `.claude/`, `AGENTS.md`, `.gitignore`.
Never touch the user's own code, rules, permissions, or model routing. Every
enrichment must trace to a detected fact or a real file — never an assumption.

## Idempotency

Re-running is a safe RESUME: the brain re-seeds, the health gate re-runs, no
duplicate commits are made, and the package stays removed. After a green run,
`--check` short-circuits and onboarding never runs again.
