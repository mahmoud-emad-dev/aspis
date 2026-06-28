"""The ``bootstrap`` operation — make an initialized project live.

Collects project details (interactively or via flags/--yes), fills the
AGENTS.md / CLAUDE.md slots left by init, writes the manifest, and triggers the
first brain fill by running the project's own context scripts. Pre/post staging
(gating, commits, self-clean) is registered separately.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from aspis import (
    __version__,
    detect,
    gitcheck,
    gitops,
    manifest,
    project,
    promotion,
    runtime_inventory,
)
from aspis.constants import BRAIN_DIR, INIT_COMMIT_MESSAGE
from aspis.health import run_checks
from aspis.lifecycle import Context, Engine
from aspis.runtimes import runtime_dirs

# The transient onboarding package: shipped by init, removed once the project is
# live so no agent ever re-checks bootstrap. Per-runtime agent + skill, plus the
# shared workflow doc.
_PKG_AGENT = "bootstrap.md"
_PKG_SKILL = "project-onboarding"
_PKG_WORKFLOW = Path("workflows") / "bootstrap.md"

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
        "stack": detect.normalize_stack(
            _value(ctx, "stack", "Main stack", detected_stack, interactive=interactive)
        )
        or "unknown",
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


def _enrich_gitignore(ctx: Context, state: dict, *, write: bool) -> None:
    """Expand ``.gitignore`` for the detected stack via the project's shipped hook.

    Runs the project's own ``.aspis/scripts/hooks/gitignore.py`` (offline cache first,
    network only as a fallback) so the ignore rules match the real stack from the
    first commit. No-op when the script is not shipped or the stack is unknown.
    """
    script = ctx.root / BRAIN_DIR / "scripts" / "hooks" / "gitignore.py"
    stack = (state.get("stack") or "").strip()
    if not script.is_file() or not stack or stack == "unknown":
        ctx.log("gitignore enrich skipped (no script or unknown stack)")
        return
    ctx.log(f"enrich .gitignore for stack: {stack}")
    if write:
        subprocess.run(
            [sys.executable, str(script), stack],
            cwd=str(ctx.root),
            capture_output=True,
            check=False,
        )


def _detect_runtimes(ctx: Context, *, write: bool) -> None:
    """Detect installed runtimes and save the inventory so the project knows its options.

    Records which runtimes are on PATH (claude/opencode/…) into the data dir. Agents
    already render with a tier->model default, so the project is usable immediately;
    this surfaces availability without a manual ``aspis models --sync``.
    """
    detected = runtime_inventory.detect_runtimes()
    available = runtime_inventory.available(detected)
    ctx.results["runtimes"] = available
    ctx.log(f"detect runtimes: {', '.join(available) or 'none on PATH'}")
    if write:
        runtime_inventory.save_inventory(detected)


def _sync_models(ctx: Context, *, write: bool) -> None:
    """Write ``.aspis/config/agent-models.yaml`` by running the existing ``models --sync``.

    Bootstrap calls the real model tool (no reinvented logic, per Automation-before-
    Intelligence) so the project leaves bootstrap with a per-agent model config
    pre-filled from the connected runtimes — editable, not a manual follow-up step.
    """
    ctx.log("models --sync (write agent-models.yaml)")
    if write:
        subprocess.run(
            [sys.executable, "-m", "aspis.cli", "models", "--sync", "--path", str(ctx.root)],
            cwd=str(ctx.root),
            capture_output=True,
            check=False,
        )


def bootstrap_core(ctx: Context) -> None:
    """Collect, enrich, write config/manifest, detect+sync models, promote, fill brain."""
    write = bool(ctx.options.get("write"))
    state = _collect(ctx)
    ctx.results["state"] = state
    _fill_slots(ctx, state, write=write)
    _enrich_gitignore(ctx, state, write=write)
    _write_project_config(ctx, state, write=write)
    _write_manifest(ctx, state, write=write)
    _detect_runtimes(ctx, write=write)
    _sync_models(ctx, write=write)
    _promote_leads(ctx, write=write)
    _run_brain_fill(ctx, write=write)


# ---------------------------------------------------------------------------
# Pre/post staging
# ---------------------------------------------------------------------------


def _require_initialized(ctx: Context) -> None:
    """Bootstrap only runs on an initialized project (pre)."""
    if not project.is_project(ctx.root):
        raise RuntimeError("not an ASPIS project — run `aspis init` first")


def _note_if_bootstrapped(ctx: Context) -> None:
    """Note (don't block) when re-running on an already-bootstrapped project (pre)."""
    if manifest.is_bootstrapped(ctx.root):
        ctx.log("note: already bootstrapped (re-running is idempotent)")


def _autocommit_init(ctx: Context) -> None:
    """Safety net: commit the init scaffold if init did not already (pre).

    Init commits its own scaffold, so this is normally a no-op. It still fires when the
    scaffold is uncommitted (e.g. init ran with --no-git and git was added later, or an
    existing repo where init's commit was skipped), so bootstrap always starts on a
    clean, committed base — and never sweeps the user's own code (ours-only pathspec).
    """
    if not bool(ctx.options.get("write")) or not gitops.has_git(ctx.root):
        return
    if gitops.commit_owned(ctx.root, INIT_COMMIT_MESSAGE):
        ctx.log("commit init scaffolding (was uncommitted)")


#: Brain files that must exist AND be non-empty for the project to count as "ready".
_REQUIRED_BRAIN = (
    Path("index") / "FILE_REGISTRY.yaml",
    Path("index") / "CODE_MAP.md",
    Path("context") / "CURRENT_STATE.md",
)


def _readiness(root: Path) -> list[str]:
    """Required brain files that are missing or empty after the bootstrap fill."""
    missing = []
    for rel in _REQUIRED_BRAIN:
        path = root / BRAIN_DIR / rel
        if not path.is_file() or not path.read_text(encoding="utf-8").strip():
            missing.append(rel.as_posix())
    return missing


def _validate_exports(root: Path) -> list[str]:
    """Exported config YAMLs / agent frontmatter that fail to parse (syntax errors).

    The "are all our files correct and connected" check: every ``.aspis/config/*.yaml``
    must be valid YAML, and every rendered agent must carry a parseable frontmatter
    block — so a malformed export is caught here, not by an agent at runtime.
    """
    import yaml

    from aspis.catalog import split_frontmatter

    problems: list[str] = []
    cfg = root / BRAIN_DIR / "config"
    if cfg.is_dir():
        for f in sorted(cfg.rglob("*.yaml")):  # includes policy/ + reference/ tiers
            try:
                yaml.safe_load(f.read_text(encoding="utf-8"))
            except yaml.YAMLError:
                problems.append(f.relative_to(root).as_posix())
    for rdir in runtime_dirs():
        agents_dir = root / rdir / "agents"
        if not agents_dir.is_dir():
            continue
        for f in sorted(agents_dir.glob("*.md")):
            try:
                frontmatter, _ = split_frontmatter(f.read_text(encoding="utf-8"))
                if not isinstance(frontmatter, dict) or not frontmatter:
                    problems.append(f.relative_to(root).as_posix())
            except Exception:
                problems.append(f.relative_to(root).as_posix())
    return problems


def _structure_strays(root: Path) -> list[str]:
    """``.aspis/`` subfolders not in the canonical structure (invented or stray).

    Enforces one consistent brain layout — an agent or script may not invent a new
    top-level brain folder. ``traces/`` is allowed ahead of the tracing feature.
    """
    from aspis import resources

    brain = root / BRAIN_DIR
    if not brain.is_dir():
        return []
    allowed = resources.canonical_brain_subdirs() | {"traces"}
    return sorted(p.name for p in brain.iterdir() if p.is_dir() and p.name not in allowed)


def _doctor_gate(ctx: Context) -> None:
    """Health + readiness + validation + structure gate after bootstrap (post)."""
    failed = [check for check in run_checks(ctx.root) if check.status == "fail"]
    missing = _readiness(ctx.root)
    invalid = _validate_exports(ctx.root)
    strays = _structure_strays(ctx.root)
    ctx.results["doctor_failed"] = len(failed)
    ctx.results["readiness_missing"] = missing
    ctx.results["validation_errors"] = invalid
    ctx.results["structure_strays"] = strays
    ctx.log(f"doctor: {len(failed)} failed" if failed else "doctor: ok")
    if missing:
        ctx.log(f"readiness: {len(missing)} brain file(s) missing/empty: {', '.join(missing)}")
    ctx.log(
        f"validation: {len(invalid)} file(s) failed to parse: {', '.join(invalid)}"
        if invalid
        else "validation: all config + agent files parse"
    )
    ctx.log(
        f"structure: {len(strays)} non-canonical folder(s): {', '.join(strays)}"
        if strays
        else "structure: canonical (no stray folders)"
    )


def bootstrap_package(root: Path) -> list[Path]:
    """Return the transient onboarding package files that exist under *root*.

    The bootstrap agent + ``project-onboarding`` skill in each present runtime dir,
    plus the shared ``.aspis/workflows/bootstrap.md``. Used to self-clean the package
    once the project is live (and listed as the answer to "what is transient").
    """
    paths = [root / BRAIN_DIR / _PKG_WORKFLOW]
    for rdir in runtime_dirs():
        base = root / rdir
        paths.append(base / "agents" / _PKG_AGENT)
        paths.append(base / "skills" / _PKG_SKILL)
    return [p for p in paths if p.exists()]


def _self_clean(ctx: Context) -> None:
    """Remove the transient onboarding package once the project is live (post).

    Only fires on a green write run: if doctor failed, the package stays so the user
    can re-run bootstrap. Idempotent — on a RESUME the package is already gone, so
    this is a no-op. Also honours any extra ``transient_assets`` listed in the manifest.
    """
    write = bool(ctx.options.get("write"))
    if (
        ctx.results.get("doctor_failed")
        or ctx.results.get("readiness_missing")
        or ctx.results.get("validation_errors")
    ):
        ctx.log("self-clean skipped (project not fully ready — keeping bootstrap package)")
        return
    extra = [ctx.root / rel for rel in manifest.load(ctx.root).get("transient_assets", [])]
    for path in bootstrap_package(ctx.root) + [p for p in extra if p.exists()]:
        ctx.log(f"self-clean {path.relative_to(ctx.root).as_posix()}")
        if write:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
    _strip_bootstrap_prose(ctx, write=write)


_GATE_START = "<!-- ASPIS:BOOTSTRAP-GATE:START -->"
_GATE_END = "<!-- ASPIS:BOOTSTRAP-GATE:END -->"
_GATE_BLOCK = re.compile(re.escape(_GATE_START) + r".*?" + re.escape(_GATE_END) + r"\n?", re.DOTALL)
#: Frontmatter lines that reference bootstrap (delegate item, the aspis bootstrap
#: permission, a bootstrap task permission) — removed so no trace of bootstrap remains.
_BOOTSTRAP_FRONTMATTER = re.compile(
    r"^[ \t]*(?:-[ \t]*bootstrap"
    r'|["\']?aspis bootstrap[^\n]*'
    r"|[\"']?bootstrap[\"']?:[ \t]*\w+)[ \t]*\n",
    re.MULTILINE,
)


def _strip_bootstrap_prose(ctx: Context, *, write: bool) -> None:
    """Remove every standing reference to bootstrap once the project is live (post).

    The self-deleting package is more than files: the first-run gate prose (wrapped in
    BOOTSTRAP-GATE markers) and the ``bootstrap`` delegate are stripped from AGENTS.md,
    CLAUDE.md, and each runtime's rendered ``project-lead`` — so a live project reads as
    if bootstrap never existed, and no agent checks for or mentions it again.
    """
    targets = [ctx.root / "AGENTS.md", ctx.root / "CLAUDE.md"]
    for rdir in runtime_dirs():
        targets.append(ctx.root / rdir / "agents" / "project-lead.md")
    for path in targets:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        updated = _BOOTSTRAP_FRONTMATTER.sub("", _GATE_BLOCK.sub("", text))
        if updated != text:
            ctx.log(f"strip bootstrap prose from {path.relative_to(ctx.root).as_posix()}")
            if write:
                path.write_text(updated, encoding="utf-8")


def _record_done(ctx: Context) -> None:
    """Stamp the manifest with the bootstrap-done time + engine version (post).

    The version stamp lets ``doctor`` warn when the project was bootstrapped by an
    older engine than the installed one (the "stale snapshot" hazard).
    """
    ctx.log("record bootstrap.done")
    if bool(ctx.options.get("write")):
        data = manifest.load(ctx.root)
        data["bootstrapped_at"] = datetime.now(UTC).isoformat(timespec="seconds")
        data["bootstrap_engine_version"] = __version__
        manifest.save(ctx.root, data)


def _commit_bootstrap(ctx: Context) -> None:
    """Commit the bootstrap fill (ours-only) — bootstrap's single commit (post)."""
    if not bool(ctx.options.get("write")) or not gitops.has_git(ctx.root):
        return
    if gitops.commit_owned(ctx.root, "chore: bootstrap ASPIS project"):
        ctx.log("bootstrap commit")
    else:
        ctx.log("bootstrap commit: nothing to commit")


def _verify_subsystem(ctx: Context) -> None:
    """Prove the git subsystem works end-to-end via a throwaway probe commit (post).

    Bootstrap does not assume the hooks are wired — it exercises them (junk cleanup,
    stale-.gitkeep reap, attribution strip) on a probe and rolls it back, so the
    project leaves bootstrap with a *verified* git subsystem, not a hoped-for one.
    """
    if not bool(ctx.options.get("write")) or not gitops.has_git(ctx.root):
        return
    results = gitcheck.verify(ctx.root)
    ctx.results["subsystem"] = results
    failed = [c.name for c in results if not c.ok]
    if failed:
        ctx.log(f"git self-test: {len(failed)} issue(s): {', '.join(failed)}")
    else:
        ctx.log(f"git self-test: ok ({len(results)} checks passed)")


def register(engine: Engine) -> None:
    """Register the bootstrap operation with its pre/post staging."""
    engine.register(
        "bootstrap",
        bootstrap_core,
        pre=(_require_initialized, _note_if_bootstrapped, _autocommit_init),
        post=(_doctor_gate, _self_clean, _record_done, _commit_bootstrap, _verify_subsystem),
    )
