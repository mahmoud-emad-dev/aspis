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
2. **Understand.** With existing code, read `README*`, package metadata, and the entry
   points; skim the layout. Draft *what the project is* and *its stack*. Empty folder →
   it is whatever the user says.
3. **Confirm with the user.** Present the draft and confirm/correct **name, goal,
   description, stack, mode** in one message; ask "proceed?" and wait. Headless/`--yes`/
   no TTY → take the given/detected values and proceed without asking.
4. **Run the spine once.**
   `aspis bootstrap --write -y --name "<name>" --goal "<goal>" --stack "<stack>" --mode <mode>`.
   It fills the AGENTS.md/CLAUDE.md slots, writes `project.yaml` + manifest, enriches
   `.gitignore`, syncs models, promotes the leads, fills the brain, commits, and
   self-tests git. Read the output; on FAIL, stop and report. Never run it twice.
5. **Enrich (judgment only).** Replace the AGENTS.md one-line definition with a real
   goal + short description; draft `.aspis/context/ARCHITECTURE.md` from the real layout
   (modules + responsibilities, facts only). Write only under `.aspis/`, `AGENTS.md`,
   `CLAUDE.md` — never user code, never invented facts.
6. **Commit the enrichment** as one clean commit, passing the files you edited:
   `aspis commit AGENTS.md .aspis/context/ARCHITECTURE.md --type docs --no-scope --title "enrich onboarding (project definition + architecture)"`.
7. **Verify & hand off.** `aspis bootstrap --check` green, `aspis doctor` no FAIL,
   AGENTS.md + ARCHITECTURE read true. Report the project is live (name, goal, stack, 5
   leads) in one or two lines. The package self-cleans; hand to `project-lead`.

## Boundaries

- Onboarding only — no app code, no feature work, no reading global/other-project config.
- The script owns the mechanical work and its commit; you own understanding + the
  single enrichment commit.
- Idempotent: after a green run, `--check` short-circuits and onboarding never runs again.
