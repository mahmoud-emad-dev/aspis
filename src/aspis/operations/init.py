"""The ``init`` operation — scaffold a project and export its runtime assets.

Registered on the lifecycle engine, so it runs as
``pre-init hooks → init_core → post-init hooks``. The core itself is pure
orchestration over the export engine, the brain scaffold, and the root-file
templates — no runtime-specific logic lives here.
"""

from __future__ import annotations

import subprocess

from aspis import resources
from aspis.constants import BRAIN_DIRS
from aspis.export import plan_export, write_export
from aspis.lifecycle import Context, Engine
from aspis.profiles import Profile, load_profile, merge
from aspis.templating import render


def _load_profile(name: str) -> Profile:
    """Load *name* merged under the shared base profile."""
    profiles_dir = resources.data_dir() / "profiles"
    base = load_profile(profiles_dir / "base.yaml")
    if name == "base":
        return base
    return merge(base, load_profile(profiles_dir / f"{name}.yaml"))


def init_core(ctx: Context) -> None:
    """Export catalog assets, scaffold the brain, and write the root files."""
    write = bool(ctx.options.get("write"))
    force = bool(ctx.options.get("force"))

    profile = _load_profile(ctx.options.get("profile") or "base")
    if ctx.options.get("runtimes"):
        profile = profile.model_copy(update={"runtimes": list(ctx.options["runtimes"])})
    project_name = ctx.options.get("name") or ctx.root.name

    # 1) Export catalog assets (none until the catalog feature lands — harmless).
    plan = plan_export(resources.data_dir() / "catalog", profile)
    for line in write_export(plan, ctx.root, force=force, write=write):
        ctx.log(line)
    for missing in plan.missing:
        ctx.log(f"missing reference (skipped): {missing}")

    # 2) Scaffold the brain skeleton, 3) write root files, 4) init git.
    _scaffold_brain(ctx, write=write)
    _write_root_files(ctx, project_name, profile, write=write, force=force)
    if not ctx.options.get("no_git"):
        _git_init(ctx, write=write)


def _scaffold_brain(ctx: Context, *, write: bool) -> None:
    """Create the empty brain directories, each kept by a ``.gitkeep``."""
    for brain_dir in BRAIN_DIRS:
        keep = ctx.root / brain_dir / ".gitkeep"
        if keep.exists():
            continue
        ctx.log(f"scaffold {brain_dir}/.gitkeep")
        if write:
            keep.parent.mkdir(parents=True, exist_ok=True)
            keep.write_text("", encoding="utf-8", newline="\n")


def _write_root_files(
    ctx: Context, project_name: str, profile: Profile, *, write: bool, force: bool
) -> None:
    """Write AGENTS.md, .gitignore, and (when claude is a target) a full CLAUDE.md."""
    files = {
        "AGENTS.md": render(resources.template("AGENTS.md"), project_name=project_name),
        ".gitignore": resources.template("gitignore"),
    }
    if "claude" in profile.runtimes:
        files["CLAUDE.md"] = render(resources.template("CLAUDE.md"), project_name=project_name)

    for name, content in files.items():
        destination = ctx.root / name
        if destination.exists() and not force:
            ctx.log(f"skip (exists): {name}")
            continue
        ctx.log(f"write {name}")
        if write:
            destination.write_text(content, encoding="utf-8", newline="\n")


def _git_init(ctx: Context, *, write: bool) -> None:
    """Initialize a git repo when the target has none."""
    if (ctx.root / ".git").exists():
        return
    ctx.log("git init")
    if write:
        subprocess.run(["git", "init", "-q"], cwd=str(ctx.root), capture_output=True, check=False)


def register(engine: Engine) -> None:
    """Register the init operation on *engine*."""
    engine.register("init", init_core)
