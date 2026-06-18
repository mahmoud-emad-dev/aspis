"""The ``bootstrap`` operation — make an initialized project live.

Collects project details (interactively or via flags/--yes), fills the
AGENTS.md / CLAUDE.md slots left by init, writes the manifest, and triggers the
first brain fill by running the project's own context scripts. Pre/post staging
(gating, commits, self-clean) is registered separately.
"""

from __future__ import annotations

import subprocess
import sys

from aspis import detect, manifest
from aspis.lifecycle import Context, Engine

# Slots that init leaves in AGENTS.md / CLAUDE.md for bootstrap to fill.
_DEFN_SLOT = "<!-- one-line project definition — filled at bootstrap -->"
_STACK_SLOT = "<!-- Stack: <stack> — filled at bootstrap -->"


# ---------------------------------------------------------------------------
# Wizard (TTY-guarded, flag-overridable, non-blocking)
# ---------------------------------------------------------------------------


def _interactive(ctx: Context) -> bool:
    """True when we should prompt: a real TTY and not --yes."""
    return sys.stdin.isatty() and not bool(ctx.options.get("yes"))


def _ask(prompt: str, default: str) -> str:
    """Prompt with a default; return the default on Enter or EOF."""
    suffix = f" [{default}]" if default else ""
    try:
        answer = input(f"{prompt}{suffix}: ").strip()
    except EOFError:
        return default
    return answer or default


def _value(ctx: Context, key: str, prompt: str, default: str, *, interactive: bool) -> str:
    """Resolve a field from a flag, else a prompt, else the default."""
    if ctx.options.get(key):
        return str(ctx.options[key])
    return _ask(prompt, default) if interactive else default


def _collect(ctx: Context) -> dict:
    """Gather project details for the manifest + slot filling."""
    interactive = _interactive(ctx)
    detected_stack = detect.detect_stack(ctx.root)
    return {
        "name": _value(ctx, "name", "Project name", ctx.root.name, interactive=interactive),
        "goal": _value(ctx, "goal", "One-line goal", "", interactive=interactive),
        "stack": _value(ctx, "stack", "Main stack", detected_stack, interactive=interactive),
        "plan": _value(ctx, "plan", "Plan file (optional)", "", interactive=interactive),
    }


# ---------------------------------------------------------------------------
# Core steps
# ---------------------------------------------------------------------------


def _fill_slots(ctx: Context, state: dict, *, write: bool) -> None:
    """Fill the bootstrap slots in AGENTS.md / CLAUDE.md from collected details."""
    definition = state["goal"] or "(no description yet)"
    for name in ("AGENTS.md", "CLAUDE.md"):
        path = ctx.root / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        text = text.replace(_DEFN_SLOT, definition)
        text = text.replace(_STACK_SLOT, f"**Stack:** {state['stack']}")
        ctx.log(f"fill slots in {name}")
        if write:
            path.write_text(text, encoding="utf-8")


def _write_manifest(ctx: Context, state: dict, *, write: bool) -> None:
    """Write .asps/manifest.json with project state and the bootstrapped flag."""
    data = manifest.load(ctx.root)
    data.update({**state, "bootstrapped": True})
    ctx.log("write .asps/manifest.json")
    if write:
        manifest.save(ctx.root, data)


def _run_brain_fill(ctx: Context, *, write: bool) -> None:
    """Trigger the first brain fill by running the project's own update.py."""
    script = ctx.root / ".asps" / "scripts" / "context" / "update.py"
    if not script.is_file():
        ctx.log("brain fill skipped (context scripts not shipped)")
        return
    ctx.log("brain fill: .asps/scripts/context/update.py")
    if write:
        subprocess.run(
            [sys.executable, str(script), str(ctx.root)], capture_output=True, check=False
        )


def bootstrap_core(ctx: Context) -> None:
    """Collect details, fill slots, write the manifest, and fill the brain."""
    write = bool(ctx.options.get("write"))
    state = _collect(ctx)
    ctx.results["state"] = state
    _fill_slots(ctx, state, write=write)
    _write_manifest(ctx, state, write=write)
    _run_brain_fill(ctx, write=write)


def register(engine: Engine) -> None:
    """Register the bootstrap operation on *engine*."""
    engine.register("bootstrap", bootstrap_core)
