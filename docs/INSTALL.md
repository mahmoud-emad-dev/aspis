# Install ASPIS

ASPIS is a single pure-Python CLI (`aspis`) with no runtime dependencies. It is
developed Windows-first; Linux and macOS use the same commands.

## Prerequisites

- **Python 3.11+** — [python.org/downloads](https://python.org/downloads)
- **Git** — [git-scm.com/downloads](https://git-scm.com/downloads)
- **uv** — [docs.astral.sh/uv](https://docs.astral.sh/uv/)

Install `uv` if you don't have it:

```powershell
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash
# Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Install the `aspis` command (global)

`uv tool install` puts an isolated `aspis` on your PATH that works from any
directory.

```bash
# Once published to GitHub:
uv tool install git+<repo-url>

# Or from a local clone (works today), run from the repo root:
uv tool install .

# Verify
aspis --version
aspis doctor
```

To refresh after pulling new changes:

```bash
uv tool install --reinstall .
```

## Verify your environment

`aspis doctor` checks Python, Git, and whether the current directory is an
ASPIS project:

```console
$ aspis doctor
  [ok  ] python   Python 3.12
  [ok  ] aspis    aspis 0.0.1
  [ok  ] git      /usr/bin/git
  [warn] project  not an ASPIS project (run `aspis init`)

All checks passed.
```

## Develop on ASPIS itself

From a clone, use the project's own environment instead of a global install:

```bash
uv sync                 # create .venv/ with dev tools (ruff, pytest)
uv run aspis --version  # run the CLI from the repo venv
uv run pytest           # run the tests
uv run ruff check .     # lint
```

`uv run aspis …` always resolves to the repo's `.venv`, so it reflects your
working tree exactly.

## Troubleshooting

**`aspis: command not found` after install.** `uv` puts the shim in
`~/.local/bin` (Linux/macOS) or `%USERPROFILE%\.local\bin` (Windows). Make sure
that directory is on your PATH and restart your terminal. Confirm with:

```bash
command -v aspis            # Linux / macOS
(Get-Command aspis).Source  # PowerShell
```
