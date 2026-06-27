---
name: hook-author
description: Author a new git or runtime hook with a parity test to prove it behaves identically across both runtime surfaces (OpenCode/Claude).
---

# hook-author

## Purpose

Author a new hook that works correctly on both the git surface AND the runtime
tool surface from a single shared implementation. The parity test proves the
hook catches the same violations, produces the same messages, and respects the
same enforcement mode regardless of which surface triggered it.

## When to use

- Adding a new hook (git or runtime).
- Modifying an existing hook's logic.
- Changing a hook's enforcement mode (warn <-> block).

## Procedure

1. Define the hook's purpose and which violations it detects.
2. Author the hook logic ONCE as a Python module under `.aspis/scripts/hooks/`
   — this is the shared core. Per R-006, never copy logic between surfaces.
3. Create the git-surface entry point (shell script in `.git/hooks/`) that
   imports the shared module.
4. Create the runtime-surface entry point (OpenCode plugin / Claude
   `PreToolUse` hook) that imports the SAME shared module. No second copy.
5. Write a parity test: run identical scenarios (clean commit, violation
   commit) through BOTH surfaces; assert identical exit codes, error messages,
   violation counts, and enforcement behavior.
6. Set the enforcement mode: `warn` for pre-commit (auto-fixes, non-blocking),
   `block` for runtime tools (hard wall). Read the mode from config, not from
   the hook body.
7. Register the hook in `hooks.yaml` so the system knows it exists.

## Outputs

- A new hook module in `.aspis/scripts/hooks/`.
- Both surface entry points (git + runtime).
- Parity test results proving identical behavior across surfaces.
- Updated `hooks.yaml` registration.

## Anti-patterns

- Copy-pasting hook logic between surfaces instead of sharing a module
  (R-006 violation — the rule is "two surfaces, one shared core").
- Testing only one surface and assuming the other works.
- Authoring a hook without a parity test — untrustworthy by construction.
- Hard-coding enforcement mode in the hook body instead of reading config.
- Blocking but ignoring the `ASPIS_ENFORCEMENT` env var override.
