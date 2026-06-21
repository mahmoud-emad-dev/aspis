# Install ASPIS

ASPIS is a single pure-Python CLI (`aspis`) with no runtime dependencies, run
through [`uv`](https://docs.astral.sh/uv/). It is tested on **Windows and Linux**
with the same commands.

## Method 1 — one command (recommended)

The installer checks prerequisites, installs `uv` if missing, installs the global
`aspis`, and runs `aspis doctor --verbose` to confirm and show where everything
lives.

```bash
# Linux / macOS
curl -fsSL https://raw.githubusercontent.com/mahmoud-emad-dev/aspis/main/install.sh | bash
```

```powershell
# Windows (PowerShell)
irm https://raw.githubusercontent.com/mahmoud-emad-dev/aspis/main/install.ps1 | iex
```

No clone, no `chmod`, no `uv` knowledge required.

## Method 2 — from a clone

```bash
git clone https://github.com/mahmoud-emad-dev/aspis.git
cd aspis
./install.sh          # Linux / macOS
```
```powershell
.\install.ps1         # Windows
```

The script detects the local working tree and installs from it.

## Method 3 — developer / contributor

```bash
uv tool install git+https://github.com/mahmoud-emad-dev/aspis.git   # global, from GitHub
uv tool install .            # global, from a clone
uv tool install --reinstall .   # refresh after pulling

# Or work from the repo without a global install:
uv sync && uv run aspis --version   # uses the repo .venv
uv run pytest && uv run ruff check .
```

## Verify

```console
$ aspis doctor
  [ok  ] python   Python 3.12
  [ok  ] aspis    aspis 0.1.0b1
  [ok  ] git      /usr/bin/git
  [warn] project  not an ASPIS project (run `aspis init`)

All checks passed.
```

`aspis doctor --verbose` additionally shows the CLI path, where config/data/cache
live, and which agent runtimes (Claude Code, OpenCode, Cursor, Gemini, Codex) are
on your PATH.

## Where ASPIS stores things

ASPIS uses your OS's standard per-user directories (an existing `~/.aspis` from an
older version is still honoured; `ASPIS_HOME` overrides everything):

| What | Linux / macOS | Windows |
|---|---|---|
| `aspis` CLI shim | `~/.local/bin/aspis` | `%USERPROFILE%\.local\bin\aspis.exe` |
| Global config | `~/.config/aspis/` | `%APPDATA%\ASPIS\` |
| Global data (runtime inventory) | `~/.local/share/aspis/` | `%LOCALAPPDATA%\ASPIS\` |
| Cache | `~/.cache/aspis/` | `%LOCALAPPDATA%\ASPIS\cache\` |
| **Per-project brain** (tracked) | `<project>/.aspis/` | `<project>\.aspis\` |

## Uninstall

```bash
aspis uninstall              # dry-run: show what would be removed
aspis uninstall --write      # remove machine-wide state (keeps project brains)
aspis uninstall --write --keep-config   # keep the global config
uv tool uninstall aspis      # remove the CLI binary itself
```

## Troubleshooting

**`aspis: command not found` after install.** `uv` puts the shim in
`~/.local/bin` (Linux/macOS) or `%USERPROFILE%\.local\bin` (Windows). Ensure that
directory is on your PATH and restart your terminal:

```bash
command -v aspis             # Linux / macOS
(Get-Command aspis).Source   # PowerShell
```

**`./install.sh: Permission denied`.** The repo ships the script with the
executable bit set, but if your filesystem dropped it: `bash install.sh` works, or
`chmod +x install.sh`.

**Python too old.** ASPIS needs Python 3.11+. Install from
[python.org/downloads](https://python.org/downloads) and re-run the installer.
