# Architecture Memory — Subsystems Index

Living per-subsystem intent (why it exists, what it owns, what it guarantees, how it
evolved). One file per subsystem. This index is advisory and rebuilt from each file's
header by `aspis subsystem index`.

> Only **architectural** change updates a subsystem file (intent/responsibility/boundary/contract/integration, or add/remove) — never bug fixes, refactors, renames.
> No file changes without explicit user confirmation. Trigger is the planning phase.

| Subsystem | Status | One-liner | Last reviewed |
|---|---|---|---|
| [architecture-memory](architecture-memory.md) | proposed | The permanent, file-first memory of architectural intent — one living file per subsystem — that prevents design drift as the project scales. | 2026-06-29 |
| [bootstrapping](bootstrapping.md) | active | The one-time, self-erasing setup that turns an initialized skeleton into a live, self-explaining project — run once, remembered forever, then it removes itself. | 2026-06-29 |
| [initialization](initialization.md) | active | `aspis init` — the deterministic, offline operation that turns a folder into a structurally complete (but not yet live) ASPIS project. | 2026-06-29 |
| [installation](installation.md) | active | How the global `aspis` CLI gets onto a machine — one cross-platform command that verifies prerequisites, installs the tool, and confirms it works, so the user can then `aspis init` any project. | 2026-06-29 |
