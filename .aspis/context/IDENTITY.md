# ASPIS — Identity

## What ASPIS is

ASPIS is a **file-first agentic software-production factory**. It is a reusable
system — a CLI plus a runtime-neutral catalog of agents, skills, and templates —
that you install into any project to plan, build, review, and ship software with
orchestrated AI agents.

- **File-first.** A project's intelligence lives in plain files under `.aspis/`
  (the portable brain), not in a tool's memory. Any runtime can read it.
- **Runtime-neutral.** One catalog renders to each AI coding runtime
  (`.opencode/`, `.claude/`) through adapters. The catalog is the product; the
  runtime files are generated.
- **Deterministic-first.** Reach for the cheapest mechanism that works — a script
  before an agent, an agent before a fleet. Structure and context let cheap models
  succeed.
- **Git is the store.** Source of truth is plain files in Git — no database. The
  catalog (YAML + Markdown) is the product; runtimes are generated and disposable.
- **Two things at once.** ASPIS is Project #1 (it builds itself, proving the system)
  *and* a reusable factory others install into their own projects.

## What ASPIS is not

- **Not a web or data app.** Its product is the catalog and the `aspis` CLI.
- **Not a clone** of spec-kit or any single tool — it harvests good ideas and
  adapts them; it does not copy one wholesale.
- **Not frontier-model-dependent.** It is designed so inexpensive models produce
  good results through focused tasks, rich context, and deterministic gates.
- **Not the exported brain.** This factory repo *develops* the product; a target
  project *receives* it.

## The core loop

A user talks to the **Project Lead**, who routes to the specialist leads:
**Planning** (idea → spec → architecture → tasks), **Build** (orchestrates builders),
**Reviewer** (independent quality), with **Research / Test / Fix** support and the
**System Lead** owning the runtime. Work is sized by mode (vibe / MVP / production).
