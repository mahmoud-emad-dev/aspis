---
name: project-onboarding
description: The one-time procedure to take an exported project to live — understand it, confirm the name/goal/stack with the user, run the deterministic `aspis bootstrap`, enrich the judgment files (AGENTS.md, ARCHITECTURE, context), verify, and let the package self-clean. Followed by the bootstrap agent.
---

# Project Onboarding

## Purpose

Turn an *exported* project into a *live* one **once**: understood, named, its goal and
stack confirmed, brain filled, leads active, history clean. Deterministic-first — a
script does all the mechanical work; you add only the understanding and the user's
confirmation.

## When to use

The first interaction in a project where `aspis bootstrap --check` is not green. Never
run feature work before this; never run it twice.

## Procedure

1. **Check.** `aspis bootstrap --check`. If bootstrapped, stop — the project is live.
2. **Understand from evidence.** Read `.aspis/current/bootstrap_state.json` (project state,
   stack+confidence, detected runtimes, rule layers, plan files). With existing code read
   `README*`, package metadata, entry points, layout; read any **plan file** found (root or
   `docs/`) and the **rule layers** (project, system, and the user's rules file at the
   recorded path — the one machine file you may read). Draft *what the project is* + *its
   stack*. Empty folder → it is whatever the user says.
3. **Confirm with the user — never decide stack/mode yourself.** Present the draft and
   confirm/correct **name, goal, description, stack, mode** (explain the modes) in one message;
   even high-confidence detection must be confirmed. If the user wants "the latest/best stack",
   delegate to **research-lead**, then confirm its recommendation. Ask "proceed?" and wait.
   Headless/`--yes`/no TTY → take the given/detected values and proceed.
4. **Draft the architecture first (existing code only).** Before the spine — the project
   only goes live once `.aspis/context/ARCHITECTURE.md` is real (the package self-cleans
   on that gate). Draft it from the real layout (modules + responsibilities, facts only).
   A greenfield/empty folder has nothing to describe yet → leave the skeleton.
5. **Run the spine once.**
   `aspis bootstrap --write -y --name "<name>" --goal "<goal>" --stack "<stack>" --mode <mode>`.
   It fills the AGENTS.md/CLAUDE.md slots, writes `project.yaml` + manifest, enriches
   `.gitignore`, syncs models, promotes the leads, fills the brain, and — once the
   architecture is real and the brain is filled — removes the package, commits, and
   self-tests git. Read the output; on FAIL, fix the cause and run again.
6. **Finish enrichment (judgment only).** Replace the AGENTS.md one-line definition with a
   real goal + short description; and for an existing project, fill any missing file
   purposes — `python .aspis/scripts/context/build_registry.py --check` lists them, read
   each and add a one-line purpose under `files` in `.aspis/config/purposes.json`. Write
   only under `.aspis/`, `AGENTS.md`, `CLAUDE.md` — never user code, never invented facts.
7. **Commit the enrichment** as one clean commit, passing the files you edited:
   `aspis commit AGENTS.md .aspis/context/ARCHITECTURE.md --type docs --no-scope --title "enrich onboarding (project definition + architecture)"`.
8. **Verify & hand off.** `aspis bootstrap --check` green, `aspis doctor` no FAIL,
   AGENTS.md + ARCHITECTURE read true. Report the project is live (name, goal, stack, 5
   leads) in one or two lines. The package self-cleans; hand to `project-lead`.

## Boundaries

- Onboarding only — no app code, no feature work, no reading global/other-project config.
- The script owns the mechanical work and its commit; you own understanding + the
  single enrichment commit.
- Idempotent: after a green run, `--check` short-circuits and onboarding never runs again.
