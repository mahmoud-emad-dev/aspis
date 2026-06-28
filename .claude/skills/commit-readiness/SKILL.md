---
name: commit-readiness
description: Verify hooks ran, no secrets, protected paths untouched, and commit message valid before committing. Owned by the reviewer.
---

# commit-readiness

## Purpose

Before any commit lands, confirm the git hooks fired correctly, no secrets
leaked into the diff, no protected path was touched without R-008 approval, and
the commit message follows the project convention. This is the last deterministic
gate before the committer writes — the reviewer owns it, the committer consults
it.

## When to use

- Before every commit — invoked by the committer or the reviewer in the
  pre-commit review path.
- When a hook reports a warning but the committer is unsure whether to proceed.
- After a scope-compliance check flags protected paths — re-verify here.

## Procedure

1. **Hooks ran** — confirm `pre-commit` and `commit-msg` hooks executed without
   block. A skipped hook (`.git/hooks/pre-commit` missing or non-executable) is
   a HIGH finding — refuse the commit.
2. **No secrets** — scan the staged diff (`git diff --cached`) for secret
   patterns (keys, tokens, passwords). Any hit is CRITICAL — refuse the commit.
3. **Protected paths** — cross-check every changed file against the protected
   path set (R-008, `.aspis/state/approval-ledger.yaml`). A protected path
   without an active `governance approve` entry is CRITICAL — refuse the commit.
4. **Valid message** — the commit message must match the convention
   (`type(scope): description` ≤72 chars). Non-conforming messages are MEDIUM
   — block unless the committer provides an explicit reason.
5. **All clear** — emit `COMMIT-READY` only when every gate passes. Any
   finding that blocks returns `COMMIT-BLOCKED` with file:line evidence per
   the `finding-format` skill.

## Outputs

- Verdict: `COMMIT-READY` or `COMMIT-BLOCKED`.
- Per-finding details with severity, location, and evidence (finding-format).
- Hook execution summary (pre-commit / commit-msg / post-commit status).

## Anti-patterns

- Skipping the hooks check because "they always pass" — a disabled hook is
  silent drift and the first sign of a broken gate.
- Allowing a commit with a protected-path touch because "it's just a doc fix."
  Protected means protected — R-008 approval is the only path.
- Accepting a non-conforming commit message with a vague promise to fix it
  later — the message is the permanent audit trail.
