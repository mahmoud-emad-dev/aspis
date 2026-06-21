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

**One command** — from a clone of this repo. The script checks prerequisites,
installs [`uv`](https://docs.astral.sh/uv/) if missing, installs the global
`aspis` CLI, and runs `aspis doctor` to confirm:

```bash
./install.sh          # Linux / macOS
```

```powershell
.\install.ps1         # Windows (PowerShell 5+)
```

**Manual** — if you prefer to drive `uv` yourself:

```bash
uv tool install .     # global CLI in an isolated environment
aspis --version

# …or work from the source tree without installing globally:
uv sync
uv run aspis --version
```

Either way, finish with `aspis doctor` to verify the environment. See
**[docs/INSTALL.md](docs/INSTALL.md)** for where files live (shim, global config,
per-project brain) and **[docs/TESTING.md](docs/TESTING.md)** for the manual
install/usage acceptance scenarios on Windows and Linux.

## Usage

```bash
aspis --help            # all commands
aspis init <dir>        # scaffold an ASPIS project (dry-run by default; --write to apply)
aspis bootstrap         # onboarding wizard — make an initialized project live
aspis status            # report project state
aspis models            # show the model each agent resolves to, per runtime (see below)
aspis commit <paths…>   # the committer's tool: compose a conventional message and commit
aspis commits           # audit commit-message history (--fix repairs the auto-fixable)
aspis gitignore         # write/refresh .gitignore for the detected stack
aspis doctor            # check the environment + project health
```

New here? Follow the **[Quickstart](docs/QUICKSTART.md)** — from a clone to your first
`plan → build → review` loop in a few minutes — then see a real feature built end-to-end
in **[Your first ASPIS build](docs/FIRST-BUILD.md)**.

## Model intelligence

ASPIS routes each agent to the *cheapest sufficient* model — the core of the bet
above — and it does so **per runtime**, because the same agent can run on a
different model under Claude than under OpenCode.

```bash
aspis models            # show the resolved model for each agent, per runtime
aspis models --available  # also list every model the connected providers expose
aspis models --sync     # (re)generate the editable per-agent model file
```

`aspis models` detects which providers your machine can actually reach and shows
how every agent resolves — canonical tier on the left, the exact runtime string
on the right:

```text
claude  (detected: anthropic)
  cheap     claude-haiku-4-5   ->  haiku
  standard  claude-sonnet-4-6  ->  sonnet
  deep      claude-opus-4-8    ->  opus
  pin general-builder  sonnet  ->  sonnet
opencode  (detected: opencode, github-copilot, openrouter, ...)
  cheap     deepseek-v4-flash  ->  opencode-go/deepseek-v4-flash
  standard  minimax-m3         ->  opencode-go/minimax-m3
  deep      deepseek-v4-pro    ->  opencode-go/deepseek-v4-pro
```

**How resolution works.** Agents declare a *tier* (`cheap` / `standard` /
`deep`), never a hard-coded model. The resolver applies, high to low:

```text
per-(runtime, agent) pin  >  per-agent pin  >  per-(runtime, capability)  >
per-capability  >  project / global tier override  >  tier map
```

— then translates the canonical id into the runtime's exact string against the
detected inventory. With nothing detected it returns the canonical id, so the
system works on any machine with no configuration. Override anything by editing
`.aspis/config/agent-models.yaml` (`aspis models --sync` seeds it) or the
project/global config; no code change is needed to add a model, provider, or
runtime. `aspis doctor` refreshes the detected inventory and flags when a
connected provider's models change.

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
