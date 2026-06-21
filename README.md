# ASPIS

> **the shield for autonomous software production**

ASPIS is a **file-first, deterministic software-production system** for building
software with AI agents. Every piece of project state — plans, rules, traces,
agent definitions — lives as plain files in Git, so any AI runtime reads and
writes the same source of truth.

**The bet:**

```text
Quality = model capability × task clarity × test strength × review discipline
```

Instead of hoping a frontier model gets it right, ASPIS engineers **clarity,
determinism, tests, and review** so the *cheapest sufficient* model produces
*production-grade* software — repeatably, not once.

> ⚠️ **Status: early beta.** ASPIS is being built in the open. The public API and
> CLI are not yet stable.

## Install

One command — it checks prerequisites, installs `uv` if missing, installs the
global `aspis`, and verifies:

```bash
# Linux / macOS
curl -fsSL https://raw.githubusercontent.com/mahmoud-emad-dev/aspis/main/install.sh | bash
```
```powershell
# Windows (PowerShell)
irm https://raw.githubusercontent.com/mahmoud-emad-dev/aspis/main/install.ps1 | iex
```

Other methods (clone, contributor, troubleshooting, uninstall, where files live):
**[docs/INSTALL.md](docs/INSTALL.md)**.

## Verify

```bash
aspis doctor             # Python, Git, project health
aspis doctor --verbose   # + where ASPIS lives and which runtimes are detected
```

## Your first project

```bash
mkdir my-project && cd my-project
aspis init --write        # scaffold the brain + runtime assets
aspis bootstrap --write   # make the project live (sets goal, promotes leads)
aspis models --sync       # assign a model to each agent for this machine
```

Each command prints the next step. Then open **`AGENTS.md`** and start your
runtime (OpenCode by default; `aspis init --runtime claude` for Claude Code).
New here? The **[Quickstart](docs/QUICKSTART.md)** walks the first
`plan → build → review` loop; **[Your first ASPIS build](docs/FIRST-BUILD.md)**
shows a real feature end-to-end.

## Commands

```bash
aspis init <dir>        # scaffold an ASPIS project (dry-run; --write to apply)
aspis bootstrap         # onboarding: make an initialized project live
aspis status            # report project state
aspis models            # the model each agent resolves to, per runtime (see below)
aspis commit <paths…>   # compose a conventional message and commit (single writer)
aspis commits           # audit commit-message history (--fix repairs the auto-fixable)
aspis gitignore         # write/refresh .gitignore for the detected stack
aspis doctor            # check environment + project health (-v for paths + runtimes)
aspis uninstall         # remove machine-wide state (keeps project brains)
```

## Model intelligence

ASPIS routes each agent to the *cheapest sufficient* model — **per runtime**,
because the same agent can run on a different model under Claude than OpenCode.

```bash
aspis models            # resolved model per agent, per runtime
aspis models --sync     # generate the editable .aspis/config/agent-models.yaml
```

Agents declare a *tier* (`cheap`/`standard`/`deep`), never a hard-coded model; a
resolver translates that to the exact model your connected providers expose, with
per-agent and per-capability overrides — all data, no code change. Detection is
presence-only (no session or content access). Full detail in the project docs.

## How it's built

ASPIS separates four layers:

| Layer       | What it is                                         | Lifetime    |
|-------------|----------------------------------------------------|-------------|
| **Factory** | this repository — the catalog, rules, and engine   | source      |
| **Brain**   | `.aspis/` — a project's durable, tool-neutral memory | permanent   |
| **Runtime** | `.claude/`, `.opencode/` — generated tool configs   | disposable  |
| **Product** | `src/`, `tests/`, `docs/` — the software being built | the deliverable |

## License

[MIT](LICENSE) © 2026 Mahmoud Emad
