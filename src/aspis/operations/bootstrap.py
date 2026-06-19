"""The ``bootstrap`` operation — make an initialized project live.

Collects project details (interactively or via flags/--yes), fills the
AGENTS.md / CLAUDE.md slots left by init, writes the manifest, and triggers the
first brain fill by running the project's own context scripts. Pre/post staging
(gating, commits, self-clean) is registered separately.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from aspis import detect, manifest, project, promotion
from aspis.constants import BRAIN_DIR
from aspis.health import run_checks
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
        "mode": _value(
            ctx,
            "mode",
            "Default build mode (vibe/mvp/production)",
            "production",
            interactive=interactive,
        ),
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


_PROJECT_CONFIG = """\
# Project settings — edit these freely (versioned, human-owned).
# The build mode this project defaults to when a request doesn't name one.
mode: {mode}

# Optional model overrides — uncomment to override the global tier->model map
# (.aspis/config/models.yaml) for this project, per runtime:
# models:
#   opencode:
#     deep: <model-id>
#   claude:
#     standard: <model-id>
# Optional per-agent pin — force one agent onto a tier or a concrete model id:
# agents:
#   reviewer: deep
"""


def _write_project_config(ctx: Context, state: dict, *, write: bool) -> None:
    """Write .aspis/config/project.yaml with the chosen default mode."""
    path = project.config_path(ctx.root)
    ctx.log(f"write {path.relative_to(ctx.root).as_posix()} (mode: {state['mode']})")
    if write:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_PROJECT_CONFIG.format(mode=state["mode"]), encoding="utf-8", newline="\n")


def _write_manifest(ctx: Context, state: dict, *, write: bool) -> None:
    """Write .aspis/manifest.json with project state and the bootstrapped flag."""
    data = manifest.load(ctx.root)
    data.update({**state, "bootstrapped": True})
    ctx.log("write .aspis/manifest.json")
    if write:
        manifest.save(ctx.root, data)


def _run_brain_fill(ctx: Context, *, write: bool) -> None:
    """Trigger the first brain fill by running the project's own update.py."""
    script = ctx.root / BRAIN_DIR / "scripts" / "context" / "update.py"
    if not script.is_file():
        ctx.log("brain fill skipped (context scripts not shipped)")
        return
    ctx.log("brain fill: .aspis/scripts/context/update.py")
    if write:
        subprocess.run(
            [sys.executable, str(script), str(ctx.root)], capture_output=True, check=False
        )


def _promote_leads(ctx: Context, *, write: bool) -> None:
    """Promote the post-bootstrap leads to primary; lands in the bootstrap commit."""
    result = promotion.promote_leads(ctx.root, write=write)
    ctx.results["promotion"] = result
    if result.promoted:
        ctx.log(f"promote leads to primary: {', '.join(result.promoted)}")
    elif result.already:
        ctx.log(f"leads already primary ({len(result.already)})")


def bootstrap_core(ctx: Context) -> None:
    """Collect details, fill slots, write the manifest, promote leads, fill the brain."""
    write = bool(ctx.options.get("write"))
    state = _collect(ctx)
    ctx.results["state"] = state
    _fill_slots(ctx, state, write=write)
    _write_project_config(ctx, state, write=write)
    _write_manifest(ctx, state, write=write)
    _promote_leads(ctx, write=write)
    _run_brain_fill(ctx, write=write)


# ---------------------------------------------------------------------------
# Pre/post staging
# ---------------------------------------------------------------------------


def _git(root: Path, *args: str) -> str:
    """Run a git command in *root*; return stripped stdout."""
    result = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=False
    )
    return result.stdout.strip()


def _has_git(ctx: Context) -> bool:
    return (ctx.root / ".git").is_dir()


def _commit_all(ctx: Context, message: str) -> None:
    """Stage everything and commit with *message* (best-effort)."""
    _git(ctx.root, "add", "-A")
    subprocess.run(
        ["git", "-C", str(ctx.root), "commit", "-q", "-m", message],
        capture_output=True,
        check=False,
    )


def _require_initialized(ctx: Context) -> None:
    """Bootstrap only runs on an initialized project (pre)."""
    if not project.is_project(ctx.root):
        raise RuntimeError("not an ASPIS project — run `aspis init` first")


def _note_if_bootstrapped(ctx: Context) -> None:
    """Note (don't block) when re-running on an already-bootstrapped project (pre)."""
    if manifest.is_bootstrapped(ctx.root):
        ctx.log("note: already bootstrapped (re-running is idempotent)")


def _autocommit_init(ctx: Context) -> None:
    """Commit the init scaffolding first, so bootstrap is a separate 2nd commit (pre)."""
    if not bool(ctx.options.get("write")) or not _has_git(ctx):
        return
    if not _git(ctx.root, "status", "--porcelain"):
        return  # already clean
    ctx.log("commit init scaffolding (1st commit)")
    _commit_all(ctx, "chore: initialize ASPIS project")


def _doctor_gate(ctx: Context) -> None:
    """Run the health checks after bootstrap (post, best-effort)."""
    failed = [check for check in run_checks(ctx.root) if check.status == "fail"]
    ctx.log(f"doctor: {len(failed)} failed" if failed else "doctor: ok")


def _self_clean(ctx: Context) -> None:
    """Remove the transient bootstrap assets listed in the manifest (post)."""
    write = bool(ctx.options.get("write"))
    for rel in manifest.load(ctx.root).get("transient_assets", []):
        path = ctx.root / rel
        if not path.exists():
            continue
        ctx.log(f"self-clean {rel}")
        if write:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()


def _record_done(ctx: Context) -> None:
    """Stamp the manifest with the bootstrap-done time (post)."""
    ctx.log("record bootstrap.done")
    if bool(ctx.options.get("write")):
        data = manifest.load(ctx.root)
        data["bootstrapped_at"] = datetime.now(UTC).isoformat(timespec="seconds")
        manifest.save(ctx.root, data)


def _commit_bootstrap(ctx: Context) -> None:
    """Commit the bootstrap fill as the 2nd commit (post)."""
    if not bool(ctx.options.get("write")) or not _has_git(ctx):
        return
    if not _git(ctx.root, "status", "--porcelain"):
        ctx.log("bootstrap commit: nothing to commit")
        return
    ctx.log("bootstrap commit (2nd commit)")
    _commit_all(ctx, "chore: bootstrap ASPIS project")


def register(engine: Engine) -> None:
    """Register the bootstrap operation with its pre/post staging."""
    engine.register(
        "bootstrap",
        bootstrap_core,
        pre=(_require_initialized, _note_if_bootstrapped, _autocommit_init),
        post=(_doctor_gate, _self_clean, _record_done, _commit_bootstrap),
    )
