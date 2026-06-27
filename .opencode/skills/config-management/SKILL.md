---
name: config-management
description: How the System Lead safely changes project configuration — model routing, build mode, policy config, and stack — only through the aspis commands and the config data files, never by hand-editing a rendered runtime agent. Reachable user → project-lead → system-lead, or user → system-lead directly.
---

# Config management

The System Lead owns every change to how the project is configured. Change configuration only
through the `aspis` commands and the data files below — **never hand-edit a rendered runtime agent**
(`.opencode/` / `.claude/`); the adapters regenerate those from the catalog + config. Model routing
and permission changes are human-gated (R-008): confirm with the user before applying.

## Model routing (which model each agent uses)

1. See what's available: `aspis models --available` — the valid `provider/model` ids for this machine.
2. Edit the **data**, not the agents:
   - one tier for everyone → `.aspis/config/models.yaml` (the tier → model map);
   - one agent → `.aspis/config/agent-models.yaml` (per-agent pin; `aspis models --sync` (re)generates it).
3. Make it live: `aspis models --sync --apply` — refresh the editable file, then re-render the agents.

## Build mode (rigor: vibe / mvp / production)

`aspis mode <vibe|mvp|production>` sets the project's default mode (`aspis mode` shows the current one).

## Policy config (hooks, secrets, conventions)

Edit the data file under `.aspis/config/policy/` — e.g. add a secret pattern to `hooks.yaml`
(`secrets:`), change `enforcement:`, or adjust `commit-convention.yaml`. These are data: adding a
rule is editing the file, not code.

## Stack / project facts

Stack and goal live in `.aspis/config/project.yaml` and `AGENTS.md` (set at bootstrap). Change them
deliberately, then refresh the brain with `aspis context`.

## How a change reaches you

A config request can arrive **user → project-lead → system-lead** (the lead routes it) or **user →
system-lead directly** — both are first-class. Understand the request, make the smallest correct
change via the commands above, validate with `aspis doctor`, and hand any commit to the `committer`.
