# Subsystem: architecture-memory

- **Status:** proposed
- **Created:** 2026-06-29   **Last reviewed:** 2026-06-29
- **One-liner:** The permanent, file-first memory of architectural intent — one living file per subsystem — that prevents design drift as the project scales.

## Why it exists (problem)
As a project grows, no model or person can reliably reconstruct *design intent* from the
codebase alone. Implementation evolves, planning changes, git history grows, chats vanish,
and context windows reset — so each new session re-derives the same understanding and risks
silently breaking the original design. ASPIS already records the as-built technical shape
(`ARCHITECTURE.md`), dated decisions (`DECISIONS.md`), future work (planning), and live
status (`CURRENT_STATE.md`), but none of them hold the per-subsystem *why / responsibilities
/ boundaries / guarantees / evolution*. This subsystem fills that gap and exists to **prevent
architectural drift**.

## Responsibilities & boundaries
- **Owns:** the per-subsystem intent record (`.aspis/architecture/subsystems/<name>.md` + `INDEX.md`); the format of those files; the mode-gated planning loop that reads, proposes, confirms, applies, and verifies architectural change; the `architecture-memory` skill.
- **Does NOT own (out of scope):** the as-built technical architecture (that stays `ARCHITECTURE.md`), dated point-decisions (`DECISIONS.md`), implementation/planning artifacts, live status, or any model/runtime selection. It does not invent subsystem files from code or memory — the owner supplies each subsystem's real intent. It never edits a file automatically.

## Current behaviour (FIXED vs OPEN)
- **FIXED** — Each subsystem has exactly one markdown file; updates are append-only with a dated changelog line; **only architectural change** (intent/responsibility/boundary/contract/integration, or add/remove a subsystem) touches a file — never bug fixes, refactors, renames, formatting, or perf; **no file changes without explicit user confirmation** of a Current/Proposed/Reason draft; the trigger is the **planning phase**, never git/commits/file edits; ownership is **project-lead** via the `architecture-memory` skill (no new agent), with planning-lead as detector/consumer.
- **OPEN** — the exact section set of the file format; the precise mode-gating thresholds; the INDEX refresh mechanics; future deterministic staleness signals.
- Inputs: a planning request + the owner's stated intent. Outputs: conformant subsystem files, an `ARCHITECTURE_IMPACT.md` per change, and confirmed dated updates. Lifecycle: lives for the life of the project; grows one file per subsystem, by-need.
- Loop (mode-gated): Impact Analysis (pre-plan) → planning reads the file(s) → Impact Report on change → user-confirmed update → build → Architecture Verification (built vs approved intent). **Full in `production`, collapsed in `mvp`, skipped in `vibe`.**

## Integrations
- **Planning** is the trigger and primary consumer (planning-lead reads before designing, writes the Impact Report). **project-lead** owns the confirm + verification gates. **`aspis artifact`** scaffolds new files (D-013). **`modes.yaml`** gates the loop's depth. **`ARCHITECTURE.md` / `DECISIONS.md`** are siblings, not duplicates — a change here may also warrant a new `DECISIONS.md` entry. A change to the file format ripples into the template, the artifact kind, and the skill.

## System contracts (guarantees)
- Every subsystem the project formally tracks has exactly one intent file, discoverable via `INDEX.md`.
- A subsystem file reflects the **current** intent (not history) in its sections, with full history in its changelog.
- No subsystem file is ever changed without explicit user confirmation.
- Light-mode (`vibe`) work never incurs Architecture-Memory overhead and is never blocked by it.
- After Architecture Verification, no approved-vs-built divergence is left silently unaddressed.

## Future direction (optional)
Subsystem files for the existing engine parts (bootstrapping, initialization, models-intelligence,
catalog-to-runtime, hooks, git, agents-and-skills, …) are authored later from the owner's real
per-subsystem intent, one at a time. A lightweight deterministic staleness signal (Last-reviewed
vs. referenced-source changes) may be added — advisory only, never blocking.

## Changelog (append-only, newest last; ARCHITECTURE changes only)
- 2026-06-29 — Created as F-019's first subsystem file. Status proposed pending owner approval of the F-019 PLAN. Format: lean 7-section; loop mode-gated (production full / mvp collapsed / vibe skipped); owner = project-lead via `architecture-memory` skill; trigger = planning; no auto-update; folder = top-level `.aspis/architecture/subsystems/`.
