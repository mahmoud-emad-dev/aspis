# Subsystem: installation

- **Status:** active
- **Created:** 2026-06-29   **Last reviewed:** 2026-06-29
- **One-liner:** How the global `aspis` CLI gets onto a machine — one cross-platform command that verifies prerequisites, installs the tool, and confirms it works, so the user can then `aspis init` any project.

## Why it exists (problem)
Before any project work, a user needs the `aspis` engine installed globally, with its
prerequisites resolved, on Windows or Linux/macOS, without remembering a sequence of steps.
Installation is the **one-command front door**: it must verify/repair prerequisites (Python,
`uv`), install the CLI, put it on PATH, and prove it runs — degrading gracefully (warn, don't
fail) when run outside a project. It is distinct from per-project setup: installation provisions
the *tool on the machine*; `initialization` provisions a *project*.

## Responsibilities & boundaries
- **Owns:** the one-command installers (`install.sh` for Linux/macOS, `install.ps1` for Windows
  PS5+); prerequisite verification (Python ≥3.11 required; git optional) and **auto-installing
  `uv`** if missing; installing the global CLI via **`uv tool install`** (from a local clone or
  `git+` the repo); PATH guidance for the shim; post-install verification (`aspis --version` +
  `aspis doctor --verbose`); the machine-wide state directories (OS-aware config / data / cache +
  the runtime inventory) and their removal via `aspis uninstall`.
- **Does NOT own:** per-project scaffolding (`initialization`), making a project live
  (`bootstrapping`), model assignment (`models-intelligence`), or editing any project. Installing
  the CLI never touches a project; uninstalling never touches a project's `.aspis` brain.

## Current behaviour (FIXED vs OPEN)
The package (`pyproject.toml`) is a hatchling build exposing the console script
`aspis = aspis.cli:main`, `requires-python >=3.11`, runtime deps `pydantic` / `pydantic-settings`
/ `pyyaml`, version dynamic from `src/aspis/__init__.py`. Both installers run **two ways** — remote
(`curl -fsSL …/install.sh | bash` · `irm …/install.ps1 | iex`) or from a clone — and do: (1) check
Python ≥3.11 (hard fail if absent/old); (2) note git (optional); (3) install `uv` if missing
(`astral.sh/uv`); (4) `uv tool install --reinstall .` from the clone when `pyproject.toml` is
`name = "aspis"`, else `uv tool install --reinstall git+<repo>`; (5) ensure the shim dir is on PATH
(`~/.local/bin`, or `%USERPROFILE%\.local\bin` on Windows); (6) verify with `aspis --version` then
`aspis doctor --verbose` (doctor **warns, never fails** outside a project) and print the next steps
(`aspis init --write` → `aspis bootstrap --write` → `aspis models --sync`). Machine-wide state lives
in OS-standard dirs resolved by `paths.all_locations()` (config / data / cache + `runtime_inventory`);
`aspis uninstall` removes that state (dry-run by default; `--write` to delete; `--keep-config` to
keep config), **never** a project brain — and prints `uv tool uninstall aspis` for the binary itself
(a tool cannot delete its own running executable). `scripts/smoke-test.{sh,ps1}` sanity-check a build.
- **FIXED (must not break):** cross-platform (Windows + Linux/macOS) with a parallel installer
  each; **one command** to install; **`uv tool install` is the vector**; **Python 3.11+** is the
  floor; `uv` is auto-installed when missing; post-install verify **warns, never hard-fails**
  outside a project; `aspis uninstall` **never** removes a project's `.aspis` brain; dry-run is the
  default for destructive actions.
- **OPEN (free to evolve):** component/profile install options; on-demand remote catalog;
  install-time runtime detection + selection menu; lean-by-default profile selection at install;
  a global cross-project brain/DB; PyPI/pipx packaging; asset signing/verification.

## Integrations
- **Produces the global `aspis` CLI that `initialization` then runs.** `doctor` is the shared
  verify/health gate (also used by project health). `paths` defines the OS-aware global store
  (foundation for any future global tier). The **runtime inventory** (detection / models-
  intelligence) is part of the machine state installation manages. `aspis uninstall` is the
  inverse operation. A change to deps, the entry point, or the path layout ripples into both
  installers and uninstall.

## System contracts (guarantees)
After a successful install: `aspis` is on PATH and runs; prerequisites are satisfied (Python
3.11+, `uv` present); `aspis doctor --verbose` reports the environment, install paths, and
detected runtimes; the user can `aspis init` any project; **no project is modified by installing**;
machine state lives only in OS-standard config/data/cache dirs and is fully removable via
`aspis uninstall` (which leaves every project brain intact).

## Future direction (the Part-1B platform tier — mostly net-new, not F-020)
The recorded global-tier vision (REFACTOR-ANALYSIS Part 1B, V1–V12): a **global install store +
cross-project brain/DB**; an **on-demand remote catalog** behind a `CatalogSource` interface
(local | remote) with verify/cache and **offline fallback = the shipped `base` profile**;
**install-time runtime detection + a selection menu** (Claude Code / OpenCode / Cursor / Codex);
**component/profile install options** (the profile is the unit of what you install — lean by
default); an **onboarding wizard** (fast defaults vs full setup, always opt-in so the
non-interactive path survives); and curated packaging (`uv tool` / pipx + a thin bootstrap).
Reserve cheap seams now (the OS-aware `paths` abstraction already exists; profile-as-unit exists;
add a `CatalogSource` interface) and keep the offline fallback = shipped base. The remote/registry,
the global brain, and big cross-project ingest are the **platform phase**, not now.

## Changelog (append-only, newest last; ARCHITECTURE changes only)
- 2026-06-29 — Intent recorded (F-019). Sources: `install.sh`, `install.ps1`, `pyproject.toml`,
  `commands/uninstall.py`, `paths`, `scripts/smoke-test.*`, and the old global-tier vision
  (REFACTOR-ANALYSIS Part 1B / V1–V12). The installers + `uninstall` + OS-aware paths were built
  in F-013 (install-ux). FIXED invariants above are the don't-break contract.
