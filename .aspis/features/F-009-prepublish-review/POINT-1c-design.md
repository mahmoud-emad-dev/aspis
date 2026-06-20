# Point 1c — headless "CLI commander" purpose auto-fill (design)

Design only. The actual wiring is **deferred to F-010** because it needs the cheap-model
id and the runtime's headless invocation, which F-010 (models) establishes.

## Problem

When `--check` finds a registered file with no derivable purpose (Layer A docstring and
Layer B static map both miss), the gap is filled by hand. We want a cheap, non-interactive
way to propose that purpose — the seed of a general **headless-commander** tier: agents or
commands invoked *from scripts* with a cheap model, never opened in a runtime TUI.

## Design

- **Config-driven, no-op by default.** A new optional block in `.aspis/config/` names the
  headless command, e.g.

  ```yaml
  # headless.yaml (illustrative)
  commander:
    enabled: false               # off until F-010 configures a model
    command: ["opencode", "run", "-m", "{model}", "{prompt}"]   # or:
    #        ["claude", "-p", "{prompt}", "--model", "{model}"]
    model: ""                    # a cheap tier id, filled by F-010
  ```

- **A runtime-agnostic helper** (`scripts/context/commander.py`, say) that:
  1. reads the config; if `enabled` is false or unset → returns `None` (pure no-op, never
     blocks `--check`);
  2. otherwise renders `{model}`/`{prompt}` into the configured argv and runs it with
     `subprocess.run(..., text=True, encoding="utf-8", errors="replace")` (cross-platform,
     constitution rule 12);
  3. returns the model's one-line answer, or `None` on any failure (timeout, nonzero,
     empty) — failure is always a soft no-op.

- **Integration point.** The purpose-detection path calls the helper only as **Layer D**,
  after A (docstring) and B (static map) miss, and writes any returned line into
  `purposes.json` `files` as an agent-registered purpose (Layer C storage). Deterministic
  layers always win; the model only fills genuine gaps.

## Deferred to F-010

- The concrete cheap-model id and the runtime's exact headless command string (per the
  provider/subscription detection F-010 builds).
- Turning `enabled: true` on by default once a free/cheap tier is known.
- Generalizing the helper into a reusable headless-commander used by other scripts.

## Confirm with user

Approach above (config-gated, no-op-until-configured, Layer-D-only) is the proposal. The
user confirmed the models work — and thus this wiring — belongs to F-010.
