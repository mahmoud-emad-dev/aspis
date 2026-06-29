# Architecture Memory — Subsystems Index

Living per-subsystem intent (why it exists, what it owns, what it guarantees, how it
evolved). One file per subsystem. This index is advisory and rebuilt from each file's
header by `aspis subsystem index`.

> Only **architectural** change updates a subsystem file (intent/responsibility/boundary/contract/integration, or add/remove) — never bug fixes, refactors, renames.
> No file changes without explicit user confirmation. Trigger is the planning phase.

| Subsystem | Status | One-liner | Last reviewed |
|---|---|---|---|
| [architecture-memory](architecture-memory.md) | proposed | The permanent, file-first memory of architectural intent — one living file per subsystem — that prevents design drift as the project scales. | 2026-06-29 |
