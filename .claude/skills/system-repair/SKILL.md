---
name: system-repair
description: Use to restore the system when the runtime is broken — a failed export or bootstrap, an agent or command that no longer renders, a broken hook or script, a dangling reference, or corrupted system state. Diagnose the root cause, apply the smallest safe fix, and prove the runtime works again.
---

# System Repair

## Purpose

Bring a broken runtime back to a working state without making the damage worse.
Repair is the System Lead's recovery responsibility — distinct from authoring a
new asset; here something that used to work no longer does.

## When to use

When the runtime is failing: bootstrap or export errored, an agent/command/skill
won't render or load, a hook or context script fails, a reference points at a
missing asset, or system state (manifest, registry) is inconsistent.

## Procedure

1. **Reproduce.** Trigger the failure and capture the exact error — which asset,
   which runtime, which step. Don't guess from the symptom.
2. **Diagnose the root cause.** Trace it to one source: a malformed catalog asset,
   an adapter mismatch, a stale reference, a missing file, or drifted state. Use
   `system-awareness` to see what the asset depends on and what depends on it.
3. **Smallest safe fix.** Repair the one root cause — never a broad rewrite. Fix
   the runtime-neutral source so the fix survives re-export; never patch only the
   rendered runtime file.
4. **Restore consistency.** If state drifted, rebuild it from its source of truth
   (re-run the generating script) rather than hand-editing.
5. **Prove it.** Re-run what failed; confirm it renders, references resolve, and
   the gate is green. Hand validation to `system-validation`.
6. Record what broke and why, so the same failure can be prevented.

## Outputs

- A working runtime, the root cause named, and the minimal change that fixed it.

## Anti-patterns

- Patching the rendered runtime file instead of the catalog source — the fix
  vanishes on the next export.
- A broad rewrite when one line was broken.
- Hand-editing generated state instead of regenerating it from source.
- Declaring it fixed without reproducing the original failure first.
