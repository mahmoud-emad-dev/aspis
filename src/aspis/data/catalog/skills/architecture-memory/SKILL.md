---
name: architecture-memory
description: Keep per-subsystem architectural intent current through the planning loop — read before designing, record an impact report on change, confirm with the user, apply a dated update, and verify the build against approved intent.
---

# architecture-memory

## Purpose
Preserve the *intent* of every subsystem across sessions so design never silently
drifts. Architecture Memory lives as one markdown file per subsystem under
`.aspis/architecture/subsystems/` (see `INDEX.md`). This skill is the discipline for
reading those files, proposing changes to them, and keeping them true — owned by the
**project-lead**, with the **planning-lead** as the detector/consumer during planning.

The loop is **mode-gated** by the `architecture` knob in `modes.yaml`:
`skip` (vibe) → files are read-only orientation, no loop, never blocks;
`note` (mvp) → collapsed (single yes/no; record + confirm only when intent changes);
`full` (production) → the whole loop below.

## When to use
- **Before planning a feature** (project-lead, pre-plan): Architecture Impact Analysis.
- **During planning** (planning-lead): read the affected subsystem file(s) before designing.
- **When planning detects an architectural change**: record an impact report.
- **When planning returns** (project-lead): confirm the change with the user, then apply.
- **After implementation + review** (project-lead): verify the build against approved intent.

## Procedure
1. **Impact Analysis (pre-plan).** Ask: does this work change a subsystem's
   responsibilities, boundaries, lifecycle, integrations, or contracts — or add/remove a
   subsystem? If every answer is *no*, plan normally and skip the rest. If any is *yes*,
   run the loop.
2. **Read (before designing).** Open the affected subsystem file(s). Honor what is marked
   **FIXED**; design *with* the current intent and existing System contracts, not against them.
3. **Record (impact report).** Run `aspis artifact architecture-impact` and fill it:
   affected subsystem(s) (existing / new / retire), reason, Current → Proposed, fixed-vs-changed,
   integration impact, and the questions the user must answer. This is recorded evidence, not a
   chat message. (Skipped automatically in vibe; the artifact is gated on the same knob.)
4. **Confirm (with the user) — NEVER automatic.** Present a short Current / Proposed / Reason
   draft and ask: *"Is this architectural summary correct?"* The model may have misread intent —
   the user's confirmation is the gate. Only on explicit *yes* do you edit a subsystem file.
5. **Apply.** Update the affected sections and append ONE dated changelog line. New subsystem →
   `aspis subsystem new <name>` then fill it. Retire → set `Status: cancelled` with a dated line
   saying why (keep the file for history). Set `Last reviewed` to today. Run `aspis subsystem index`.
6. **Verify (post-review).** Compare the approved intent to what was actually built. If they
   diverged, ask the user: correct the implementation, or update Architecture Memory? Never let
   the divergence stand silently.

## Outputs
- An `ARCHITECTURE_IMPACT.md` in the feature folder when intent changes (mvp/production).
- A user-confirmed, dated update to the affected subsystem file(s) + a refreshed `INDEX.md`.
- A verification note (or a raised question) reconciling built work with approved intent.

## Anti-patterns
- **Auto-editing intent.** Never change a subsystem file without explicit user confirmation.
- **Churn updates.** Bug fixes, refactors, renames, formatting, and perf MUST NOT touch these
  files — only a real change to intent/responsibility/boundary/contract/integration does.
- **Rewriting history.** Never edit a past changelog line; supersede it with a new dated one.
- **Running the loop in vibe.** Light modes read the files for orientation only — no report,
  no gate, no block.
- **Inventing subsystems.** Do not generate subsystem files from the codebase or from memory;
  capture the owner's real intent, one subsystem at a time.
- **Triggering on git.** The trigger is the planning phase, never a commit or a file edit.
