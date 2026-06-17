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

The name fits the job: an *aspis* (ἀσπίς) was the round shield a hoplite carried.
ASPIS is the shield around your build — against drift, insecure code, broken
commits, and the non-determinism of raw AI builds.

> ⚠️ **Status: early development.** ASPIS is being built in the open, one core
> part at a time. The public API and CLI are not yet stable.

## Install

ASPIS uses [`uv`](https://docs.astral.sh/uv/). From a clone:

```bash
uv sync
uv run aspis --version
```

Or install the CLI into an isolated environment:

```bash
uv tool install .
aspis --version
```

## Usage

```bash
aspis --help        # show available commands
aspis status        # report whether the current directory is an ASPIS project
```

More commands (`init`, `build`, `review`) arrive as their core parts land.

## How it's built

ASPIS separates four layers:

| Layer       | What it is                                         | Lifetime    |
|-------------|----------------------------------------------------|-------------|
| **Factory** | this repository — the catalog, rules, and engine   | source      |
| **Brain**   | `.asps/` — a project's durable, tool-neutral memory | permanent   |
| **Runtime** | `.claude/`, `.opencode/` — generated tool configs   | disposable  |
| **Product** | `src/`, `tests/`, `docs/` — the software being built | the deliverable |

## License

[MIT](LICENSE) © 2026 Mahmoud Emad
